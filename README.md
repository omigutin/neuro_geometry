# neuro_geometry

2D-геометрия для пайплайнов компьютерного зрения: `Point`, `Line` (+ `LineDirection`), `Quadrangle`, `Rectangle`, `Triangle`, `Contour`.

Координаты — пиксели изображения: ось Y направлена вниз, точки хранятся как `int`.

| | |
|--|--|
| **Репозиторий** | https://github.com/omigutin/neuro_geometry |
| **Пакет** | `neuro-geometry` (импорт: `neuro_geometry`) |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) |
| **Лицензия** | [MIT](LICENSE) |

## Установка

```bash
pip install "neuro-geometry @ git+https://github.com/omigutin/neuro_geometry.git@main"
```

С OpenCV для повёрнутых прямоугольников:

```bash
pip install "neuro-geometry[cv] @ git+https://github.com/omigutin/neuro_geometry.git@main"
```

Обязательная зависимость — только `numpy`. OpenCV нужен лишь для `Rectangle(..., rotated=True)`.
Extra `[cv]` ставит `opencv-python-headless`. Если в проекте уже есть `opencv-python` или
`opencv-contrib-python`, extra не нужен: несколько дистрибутивов OpenCV в одном окружении конфликтуют.

## Пример

```python
import numpy as np
from neuro_geometry import Line, LineDirection, Point, Quadrangle, Rectangle

p = Point(10, 20)                      # или Point((10, 20))
line = Line([[0, 0], [100, 10]])
assert line.direction == LineDirection.HORIZONTAL
cross = line.get_intersection_point_with_line_segment((Point(50, -5), Point(50, 20)))

q = Quadrangle([[0, 0], [100, 0], [60, 50], [0, 50]])
q.area                                 # 4000.0

r = Rectangle([0, 0, 100, 50])         # по осям, как cv2.boundingRect
contour = np.array([[[10, 10]], [[110, 40]], [[100, 80]], [[0, 50]]], dtype=np.int32)
rr = Rectangle(contour, rotated=True)  # минимальной площади, как cv2.minAreaRect (нужен OpenCV)
smaller = rr.decrease(10, 10)
```

## Классы

- **`Point`** — точка с координатами `int`. Дробные значения округляются через `round()`
  (округление к чётному: `Point(2.5, 0).x == 2`). Поддерживает `+`, `-`, `==`, `hash`.
- **`Line`** — отрезок из двух точек. Направление `HORIZONTAL`, если `|dx| >= |dy|`, иначе `VERTICAL`.
  У горизонтального заполнены `lp`/`rp`, у вертикального — `tp`/`bp`; противоположная пара равна `None`.
  `get_x_on_line`/`get_y_on_line` работают для любого направления и считают по прямой, проходящей через отрезок.
- **`Quadrangle`** — четырёхугольник `lbp, ltp, rtp, rbp`. Из 2 точек строится прямоугольник по осям,
  из 3 и более — берутся крайние углы относительно центроида. Площадь — по формуле шнурования.
- **`Rectangle`** — прямоугольник вокруг контура.
  - `rotated=False` повторяет `cv2.boundingRect`: границы включительные, `width = xmax - xmin + 1`.
  - `rotated=True` повторяет `cv2.minAreaRect` + `cv2.boxPoints`. Углы `lbp/ltp/rtp/rbp` берутся в порядке
    `boxPoints`, поэтому у повёрнутого прямоугольника их имена условны.
  - `shift()` сдвигает прямоугольник на месте; `shift_given_angle()` и `decrease()` возвращают новый.
- **`Triangle`** — прямоугольный треугольник `bp, tp, lrp` с вертикальным катетом `tp–bp`.
- **`Contour.get_from_coords`** — `[[x, y], ...]` → массив OpenCV формы `(N, 1, 2)`, `int32`.

## Миграция с `pc_geometric_shapes` (production_counters) и `neurogeometry`

Хвост пути импорта заменяется на `neuro_geometry`:

| Было | Стало |
|------|-------|
| `from ...pc_common.pc_geometric_shapes import Point, Line, Rectangle` | `from neuro_geometry import Point, Line, Rectangle` |
| `from ...pc_geometric_shapes.gs_line import LineDirection` | `from neuro_geometry import LineDirection` |
| `from ...pc_common.types import Contour` | `from neuro_geometry import Contour` |
| `from neurogeometry import ...` | `from neuro_geometry import ...` |

Отличия в поведении от `pc_geometric_shapes` перечислены в [CHANGELOG.md](CHANGELOG.md) (версия 0.2.0).
Главные для миграции:

- `Quadrangle.area` считается точно по вершинам, а не по формуле Брахмагупты: для не вписанных
  четырёхугольников значения меняются. Проверьте пороги площади в конфигах.
- `Triangle.t_line_len()` и `b_line_len()` теперь возвращают длины своих сторон.
- `Line` не меняет переданный список координат.
- `Point` сравнивается по координатам (`==`) и хешируется.

## Разработка

```bash
pip install -e ".[dev]"
ruff check .
mypy
pytest
```

CI ([tests.yml](.github/workflows/tests.yml)) прогоняет ruff, mypy и pytest на Python 3.10–3.12,
плюс отдельный прогон без OpenCV.

## Сборка и публикация

```bash
python -m build
python -m twine check dist/*
```

В `[build-system]` зафиксирован `hatchling<1.24`: более новые версии пишут в METADATA поля PEP 639,
на которых `twine check` пока часто падает.

Публикация на PyPI — через GitHub Release и Trusted Publishing
([publish-pypi.yml](.github/workflows/publish-pypi.yml)): в настройках PyPI добавьте Trusted Publisher
для этого репозитория (workflow `publish-pypi.yml`, environment `pypi`), затем создайте Release с тегом `vX.Y.Z`.
Перед релизом обновите версию в `pyproject.toml`, `src/neuro_geometry/__init__.py` и запись в CHANGELOG.
