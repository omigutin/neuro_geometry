# NeuroGeometry

2D-геометрия для пайплайнов компьютерного зрения: `Point`, `Line` (+ `LineDirection`), `Quadrangle`, `Rectangle`, `Triangle`.

**Лицензия:** [MIT](LICENSE). Фрагменты логики минимального описанного прямоугольника восходят к OpenCV — см. [NOTICE](NOTICE).

| | |
|--|--|
| **Репозиторий** | https://gitlab.com/matller/NeuroGeometry |
| **Имя на PyPI** | **`neurogeometry`** |
| **Страница PyPI** | https://pypi.org/project/neurogeometry/ *(после первой публикации)* |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) |

## Установка

С PyPI (после публикации пакета):

```bash
pip install neurogeometry
```

Конкретная версия:

```bash
pip install neurogeometry==0.1.1
```

Зависимости для разработки и сборки:

```bash
pip install -e ".[dev]"
```

## Миграция с `pc_geometric_shapes`

В монолите импорты вида `...pc_common.pc_geometric_shapes` или `...pc_geometric_shapes` заменяются на **`neurogeometry`**.

| Было (пример) | Стало |
|---------------|--------|
| `from ...pc_common.pc_geometric_shapes import Point` | `from neurogeometry import Point` |
| `from ..pc_geometric_shapes import Point` | `from neurogeometry import Point` |
| `from ...pc_common.pc_geometric_shapes import Line` | `from neurogeometry import Line` |
| `from ...pc_common.pc_geometric_shapes import Rectangle` | `from neurogeometry import Rectangle` |
| `from ...pc_common.pc_geometric_shapes import Quadrangle` | `from neurogeometry import Quadrangle` |
| `from ...pc_common.pc_geometric_shapes import Triangle` | `from neurogeometry import Triangle` |
| `from ...pc_geometric_shapes.gs_line import LineDirection` | `from neurogeometry import LineDirection` |
| `from ...pc_common.pc_geometric_shapes import Point, Line, Rectangle` | `from neurogeometry import Point, Line, Rectangle` |
| контур из координат (класс `Contour`) | `from neurogeometry.contour import Contour` |

Количество точек в пути импорта (`...`) зависит от глубины вашего модуля — важно только заменить хвост на `neurogeometry`.

## Пример

```python
from neurogeometry import Point, Rectangle, Line, LineDirection

p = Point(10, 20)
r = Rectangle([[0, 0, 100, 50]], rotated=False)
```

## Тесты

```bash
pytest
```

Настройка discovery: `[tool.pytest.ini_options]` в `pyproject.toml` (`testpaths`, `pythonpath = ["src"]`).

## Сборка дистрибутивов

В `[build-system]` зафиксирован **`hatchling<1.24`**, чтобы метаданные оставались в формате, который проходит **`twine check`** на текущих версиях Twine (поля PEP 639 в METADATA 2.4 пока часто ломают проверку).

```bash
pip install build
python -m build
```

Артефакты появятся в `dist/`: wheel (`.whl`) и sdist (`.tar.gz`). Проверка содержимого wheel:

```bash
python -m zipfile -l dist/neurogeometry-*.whl
tar -tzf dist/neurogeometry-*.tar.gz | head
```

Установка wheel в чистое окружение:

```bash
python -m venv .venv-build && source .venv-build/bin/activate  # Windows: .venv-build\Scripts\activate
pip install dist/neurogeometry-0.1.0-py3-none-any.whl
python -c "from neurogeometry import Point; print(Point(1,2))"
```

## Публикация на PyPI

**Токены и учётная запись PyPI нужны вам локально; из этого репозитория PyPI автоматически не вызывается.**

### Вариант A: Twine (локально)

1. Обновите версию в `pyproject.toml` (`[project].version`) и запись в [CHANGELOG.md](CHANGELOG.md).
2. Создайте git-тег `vX.Y.Z` и запушьте его (см. ниже).
3. Соберите дистрибутивы: `python -m build`.
4. Загрузка на **PyPI**:

   ```bash
   python -m twine check dist/*
   python -m twine upload dist/*
   ```

   Для **TestPyPI** (рекомендуется сначала):

   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

   Учётные данные: API token из настроек https://pypi.org/manage/account/ (или `~/.pypirc`).

### Вариант B: GitHub Actions + Trusted Publishing

1. В [PyPI](https://pypi.org/manage/account/publishing/) добавьте **Trusted Publisher** для репозитория проекта: укажите workflow `.github/workflows/publish-pypi.yml` и environment `pypi` (как в файле workflow).
2. В GitHub создайте environment **`pypi`** (Settings → Environments) при необходимости с правилами защиты веток.
3. Создайте **Release** на GitHub с тегом вида `v0.1.0` — workflow соберёт пакет и загрузит на PyPI через OIDC **без** хранения токена в секретах.

Шаблон workflow: [.github/workflows/publish-pypi.yml](.github/workflows/publish-pypi.yml). Ручной запуск `workflow_dispatch` собирает артефакты, но шаг загрузки на PyPI привязан к событию `release: published` — при необходимости измените условие `if:` в job `publish-to-pypi`.

## Структура

- `src/neurogeometry/` — код пакета (src-layout).
- `tests/` — pytest.
