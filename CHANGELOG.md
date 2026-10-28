# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версии по [Semantic Versioning](https://semver.org/lang/ru/).

## [0.2.0] — 2026-10-28

Репозиторий перенесён на https://github.com/omigutin/neuro_geometry.

### Изменено (несовместимо)

- Пакет переименован: `neurogeometry` → `neuro_geometry`, дистрибутив — `neuro-geometry`.
- `Rectangle(rotated=True)` снова использует OpenCV (`cv2.minAreaRect` + `cv2.boxPoints`).
  OpenCV — необязательная зависимость: extra `[cv]`. Без него `rotated=True` бросает `ImportError`
  с подсказкой. Собственный numpy-порт `_rotcalipers` удалён: результаты расходились с OpenCV 4.5+
  (другой диапазон угла и порядок вершин), а вызов был примерно в 2400 раз медленнее.
- `Quadrangle.area` и `Rectangle.area` считаются по формуле шнурования. Раньше использовалась
  формула Брахмагупты, которая точна только для вписанных четырёхугольников.
- Ошибки валидации — `ValueError`/`TypeError` с сообщениями на английском вместо голого `Exception`.

### Исправлено

- `Line`: `len()`, `list_of_tuples()`, `get_x_on_line()` и `get_y_on_line()` падали с `AttributeError`
  для линий «не того» направления; `get_x_on_line()` делила на ноль для строго вертикальной линии.
- `Triangle`: `t_line_len()` и `b_line_len()` возвращали длину стороны `tp–bp`.
- `Quadrangle`: `IndexError` для фигуры шириной 1 пиксель (округлённый центроид оставлял левую группу пустой);
  для вырожденного набора точек теперь `ValueError`.
- `Rectangle.shift()` не пересчитывал `cp`, `contour`, `lcp`, `rcp`, `tcp`, `bcp`.
- `Rectangle.decrease()` дважды пересчитывал проценты и терял поворот; теперь уменьшает каждую сторону
  на заданный процент с сохранением центра и угла.
- `Rectangle.shift_given_angle()` возвращает точный параллельный перенос (без повторного `minAreaRect`).
- `Point`: `numpy.float32` округлялся отбрасыванием дробной части, а не через `round()`.

### Добавлено

- `Point`: `__eq__`, `__hash__`, `__repr__`.
- `Rectangle.rotated`; `Contour` в корне пакета; `__version__`.
- Полная типизация (mypy `--strict`), тесты на все классы и сверка с OpenCV, CI-workflow с тестами.
- `.gitattributes`: переводы строк в репозитории — LF.

## [0.1.1] — 2026-03-19

### Исправлено

- `Line`: исключить мутацию входного списка координат при определении ориентации линии.

## [0.1.0] — 2025-03-19

### Добавлено

- Пакет `neurogeometry`: `Point`, `Line`, `LineDirection`, `Quadrangle`, `Rectangle`, `Triangle`, `Contour`.
- `Rectangle` без обязательной зависимости от OpenCV (numpy-порт rotating calipers для `rotated=True`).

[0.2.0]: https://github.com/omigutin/neuro_geometry/releases/tag/v0.2.0
