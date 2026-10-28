# neuro_geometry

2D-геометрия для пайплайнов компьютерного зрения: `Point`, `Line`, `Rectangle`, `Quadrangle`, `Triangle`
и векторные операции над массивами фигур (`neuro_geometry.batch`).

| | |
|--|--|
| **Репозиторий** | https://github.com/omigutin/neuro_geometry |
| **Пакет** | `neuro-geometry` (импорт: `neuro_geometry`) |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) |
| **Лицензия** | [MIT](LICENSE) |

## Установка

```bash
pip install "neuro-geometry @ git+https://github.com/omigutin/neuro_geometry.git@main"
# с OpenCV для повёрнутых прямоугольников:
pip install "neuro-geometry[cv] @ git+https://github.com/omigutin/neuro_geometry.git@main"
```

Обязательная зависимость — только `numpy`. OpenCV нужен лишь для `Rectangle.from_points(..., rotated=True)`.
Extra `[cv]` ставит `opencv-python-headless`; если в проекте уже есть `opencv-python` или
`opencv-contrib-python`, extra не нужен — несколько дистрибутивов OpenCV в одном окружении конфликтуют.

## Принципы

- **Координаты — float**, ось Y направлена вниз (координаты изображения). Промежуточного округления нет;
  в пиксели переводят явно: `Point.to_int_tuple()`, `Rectangle.to_int_box()`, свойство `contour` (int32 для OpenCV).
  Округление — половина вверх (`2.5 → 3`), без смещения к чётному, как у `round()`.
- **Изменить на месте или получить новый объект** — по паре имён, как `list.sort()` / `sorted()`:

  | На месте, возвращает `None` | Новый объект |
  |---|---|
  | `shift(dx, dy)` | `shifted(dx, dy)` |
  | `scale(kx, ky)` | `scaled(kx, ky)` |
  | `decrease(w%, h%)` | `decreased(w%, h%)` |
  | `increase(w%, h%)` | `increased(w%, h%)` |
  | `Rectangle.shift_along_axes(...)` | `Rectangle.shifted_along_axes(...)` |
  | `p += q`, `p -= q`, `set(...)` | `p + q`, `p - q`, `copy()` |

  Изменение на месте не создаёт новых объектов: `Rectangle` хранит только центр, размеры и угол,
  а `shift()` сдвигает уже посчитанные вершины в своём буфере. mypy подсветит ошибку вида
  `r2 = r.shift(...)`, потому что метод возвращает `None`.
- **Фигуры изменяемые, поэтому не хешируются** (`hash()` бросает `TypeError`); сравнение `==` — точное по float,
  для допуска есть `Point.isclose()`.
- **Производные величины ленивые**: вершины и контур `Rectangle` считаются при первом обращении и кэшируются.

## Пример

```python
import numpy as np
from neuro_geometry import Line, Point, Quadrangle, Rectangle, batch

p = Point(10, 20)
p += Point(1, 1)                       # на месте
q = p.shifted(5, 0)                    # новая точка

line = Line(0, 50, 100, 50)            # линия подсчёта
move = Line.from_points(Point(10, 40), Point(12, 60))
cross = line.intersection_with_segment(move)       # Point(11, 50)
side = line.side_of(Point(10, 60))                 # > 0: справа по направлению линии

r = Rectangle.from_box(0, 0, 100, 50)  # по осям; width = 100
r.shift(10, 0)                         # на месте
smaller = r.decreased(10, 10)          # новый: каждая сторона внутрь на 10 %
x1, y1, x2, y2 = r.to_int_box()        # для вырезки image[y1:y2, x1:x2]

contour = np.array([[[10, 10]], [[110, 40]], [[100, 80]], [[0, 50]]], dtype=np.int32)
rr = Rectangle.from_points(contour, rotated=True)  # как cv2.minAreaRect (нужен OpenCV)
rr.ltp, rr.tcp, rr.area                # вершины и середины сторон корректны и для повёрнутого

quad = Quadrangle([[100, 0], [0, 50], [60, 50], [0, 0]])  # вершины в любом порядке
quad.area                              # 4000.0

# Много объектов кадра одним вызовом
prev = np.array([[10, 40], [20, 45]])
cur = np.array([[10, 60], [25, 48]])
crossed = batch.crossed_line(prev, cur, [[0, 50], [100, 50]])  # array([ True, False])
```

## Классы

- **`Point(x, y)`** — `x`, `y` (float, можно присваивать), `distance_to()`, `isclose()`,
  `to_tuple()`, `to_int_tuple()`, `to_list()`, арифметика `+ - *`, распаковка `x, y = p`.
- **`Line(x1, y1, x2, y2)`**, `Line.from_points()`, `Line.from_coords()` — отрезок start → end (порядок сохраняется).
  `length`, `angle`, `center`, `direction` (`HORIZONTAL` при `|dx| >= |dy|`), концы по положению
  `tp`/`bp`/`lp`/`rp` (определены всегда), `x_at(y)`, `y_at(x)`, `side_of(point)`, `distance_to_point()`,
  `intersection_with_line()`, `intersection_with_segment()`.
- **`Rectangle(cx, cy, width, height, angle=0)`**, `from_box()`, `from_xywh()`, `from_points(points, rotated=False)`.
  Угол нормализуется в `(-45, 45]`: `width` — сторона ближе к горизонтали. Вершины `lbp/ltp/rtp/rbp`, середины сторон
  `lcp/rcp/tcp/bcp`, центр `cp` — в системе самого прямоугольника. `area = width * height`, `corners` (4, 2),
  `coords`, `contour`, `bounding_box()`, `to_int_box()`, `contains()`. Сеттеры `width`, `height`, `angle`, `set_center()`.
  - `from_points(..., rotated=False)` — геометрическая ширина `xmax - xmin`.
    Результат `cv2.boundingRect` (пиксельная ширина, на 1 больше) передавайте через `from_xywh(*cv2.boundingRect(c))`.
- **`Quadrangle(vertices)`** — 4 вершины в любом порядке, упорядочиваются в `lbp, ltp, rtp, rbp` по углу вокруг центра
  (корректно и для повёрнутых фигур). `from_box()`, `from_points()` (крайние точки облака).
  Длины сторон, `min/max_width/height`, середины сторон, `area` (формула шнурования).
- **`Triangle(a, b, c)`**, `Triangle.from_coords()` — стороны `ab`, `bc`, `ca`, `perimeter`, `area`, `centroid`.
- **`batch`** — numpy над массивами: `boxes_centers`, `boxes_areas`, `shift_points(..., out=)` (`out=points` —
  на месте), `side_of_line`, `segments_intersections`, `crossed_line`.
- **`to_contour(points)`**, **`round_half_up(value)`** — перевод в пиксели.

## Производительность

Python 3.10, numpy 1.26, OpenCV 4.11; одна операция:

| Операция | Время |
|---|---|
| `Point(x, y)`, `p += q` | ~0.1 µs |
| `Line(...)` / пересечение отрезков | 0.17 / 0.5 µs |
| `Rectangle.from_box(...)` | 0.5 µs |
| `Rectangle.from_points(contour)` / `rotated=True` | 4 / 2.2 µs |
| `Rectangle.shift()` (на месте) / `shifted()` | 0.11 / 0.27 µs |
| `Quadrangle(4 вершины)` / `shift()` | 2.6 / 0.27 µs |
| 1000 траекторий × линия подсчёта: цикл `Line` / `batch.crossed_line` | 0.4 / 0.04 ms |

Для десятков и сотен объектов на кадр используйте `batch`.

## Миграция с `pc_geometric_shapes` (production_counters)

API несовместим: координаты стали float, имена методов изменились. Основные замены:

| Было | Стало |
|------|-------|
| `from ...pc_geometric_shapes import Point, Line, Rectangle` | `from neuro_geometry import Point, Line, Rectangle` |
| `Point(x, y).tuple()` для OpenCV | `Point(x, y).to_int_tuple()` |
| `Point((x, y))` | `Point.from_seq((x, y))` |
| `Line(coords)` | `Line.from_coords(coords)` |
| `line.get_intersection_point_with_line_segment((p1, p2))` | `line.intersection_with_segment(Line.from_points(p1, p2))` |
| `line.get_x_on_line(p)` / `get_y_on_line(p)` | `line.x_at(p.y)` / `line.y_at(p.x)` |
| `Rectangle(contour)` | `Rectangle.from_xywh(*cv2.boundingRect(contour))` — точно как раньше, или `Rectangle.from_points(contour)` |
| `Rectangle(contour, True)` | `Rectangle.from_points(contour, rotated=True)` |
| `rect.shift(Point(dx, dy))` | `rect.shift(dx, dy)` |
| `rect.shift_given_angle(d)` | `rect.shifted_along_axes(d)` |
| `Quadrangle([[x1, y1], [x2, y2]])` | `Quadrangle.from_box(x1, y1, x2, y2)` |
| `Triangle(bp, tp, lrp).t_line_len()` | `Triangle(bp, tp, lrp).bc` |
| `Contour.get_from_coords(coords)` | `to_contour(coords)` |

## Разработка

```bash
pip install -e ".[dev]"
ruff check .
mypy
pytest
```

CI ([tests.yml](.github/workflows/tests.yml)) прогоняет ruff, mypy и pytest на Python 3.10–3.12 и отдельно без OpenCV.

## Сборка и публикация

```bash
python -m build
python -m twine check dist/*
```

В `[build-system]` зафиксирован `hatchling<1.24`: более новые версии пишут в METADATA поля PEP 639,
на которых `twine check` пока часто падает.

Публикация на PyPI — через GitHub Release и Trusted Publishing ([publish-pypi.yml](.github/workflows/publish-pypi.yml)):
в настройках PyPI добавьте Trusted Publisher для этого репозитория (workflow `publish-pypi.yml`, environment `pypi`),
затем создайте Release с тегом `vX.Y.Z`. Перед релизом обновите версию в `pyproject.toml`,
`src/neuro_geometry/__init__.py` и запись в CHANGELOG.
