# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версии по [Semantic Versioning](https://semver.org/lang/ru/).

## [0.2.0] — 2026-10-28

Библиотека переписана. Репозиторий перенесён на https://github.com/omigutin/neuro_geometry.
API несовместим с 0.1.x и с `pc_geometric_shapes` — таблица замен в README.

### Изменено (несовместимо)

- Пакет переименован: `neurogeometry` → `neuro_geometry`, дистрибутив — `neuro-geometry`.
- Координаты хранятся во float без промежуточного округления. Перевод в пиксели явный:
  `to_int_tuple()`, `to_int_box()`, `contour`, `to_contour()`; округление половины вверх.
- Единое правило изменения: `shift()`/`scale()`/`decrease()`/`increase()` меняют объект на месте и возвращают `None`,
  `shifted()`/`scaled()`/`decreased()`/`increased()`/`copy()` возвращают новый.
- `Point(x, y)` — float; `Point.from_seq()` вместо `Point((x, y))`; `to_tuple()`/`to_list()` вместо `tuple()`/`list()`;
  `distance_to()` возвращает float. Точки сравниваются по координатам и не хешируются.
- `Line(x1, y1, x2, y2)`, `from_points()`, `from_coords()`; порядок концов сохраняется; `tp`/`bp`/`lp`/`rp`
  определены всегда; `length` — float; новые имена методов (`x_at`, `y_at`, `intersection_with_line`,
  `intersection_with_segment`); `len(line)` убран.
- `Rectangle` хранит центр, размеры и угол. Конструкторы `from_box()`, `from_xywh()`, `from_points(rotated=...)`.
  Ширина по точкам — геометрическая (`xmax - xmin`), а не пиксельная, как у `cv2.boundingRect`.
  Угол нормализуется в `(-45, 45]`; вершины и середины сторон корректны для повёрнутого прямоугольника;
  `area = width * height`.
- `Rectangle(rotated=True)` использует OpenCV (`cv2.minAreaRect`), OpenCV — необязательная зависимость (extra `[cv]`).
  Собственный numpy-порт `_rotcalipers` удалён: расходился с OpenCV 4.5+ и был примерно в 2400 раз медленнее.
- `Quadrangle(vertices)` принимает ровно 4 вершины в любом порядке; `from_box()` — вместо 2 точек,
  `from_points()` — крайние точки облака. Площадь — по формуле шнурования.
- `Triangle(a, b, c)` — произвольный треугольник (`ab`, `bc`, `ca`, `area`, `perimeter`, `centroid`) вместо NamedTuple.
- `Contour.get_from_coords()` заменён функцией `to_contour()`.

### Исправлено

- Ошибки 0.1.x: падения `Line` для линий «не того» направления, деление на ноль, неверные длины сторон `Triangle`,
  `IndexError` у `Quadrangle` в 1 пиксель, вырожденный ромб, неверная площадь не вписанных четырёхугольников,
  `Rectangle.shift()` без пересчёта производных точек, неработающий `Rectangle.decrease()`.

### Добавлено

- Изменение на месте без выделения памяти, `copy()` у всех фигур, сеттеры `Rectangle.width/height/angle`.
- `Line.side_of()`, `Line.distance_to_point()`, `Rectangle.contains()`, `bounding_box()`, `to_int_box()`.
- Модуль `batch`: векторные операции numpy над массивами точек, боксов и отрезков.
- Типизация mypy `--strict`, ruff, тесты со сверкой с OpenCV, CI-workflow с тестами, `.gitattributes` (LF).

## [0.1.1] — 2026-03-19

### Исправлено

- `Line`: исключить мутацию входного списка координат при определении ориентации линии.

## [0.1.0] — 2025-03-19

### Добавлено

- Пакет `neurogeometry`: `Point`, `Line`, `LineDirection`, `Quadrangle`, `Rectangle`, `Triangle`, `Contour`.

[0.2.0]: https://github.com/omigutin/neuro_geometry/releases/tag/v0.2.0
