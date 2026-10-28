# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версии по [Semantic Versioning](https://semver.org/lang/ru/).

## [0.1.0] — 2025-03-19

### Добавлено

- Первый публичный релиз на PyPI (после публикации): пакет **`neurogeometry`**.
- Примитивы 2D-геометрии: `Point`, `Line`, `LineDirection`, `Quadrangle`, `Rectangle`, `Triangle`.
- `Rectangle` без обязательной зависимости от OpenCV в runtime (numpy + rotating calipers для `rotated=True`).
- Вспомогательный класс `Contour` в модуле `neurogeometry.contour`.
- Типизация (`py.typed`), layout `src/neurogeometry/`.
- Зависимость: `numpy>=1.23`; Python `>=3.10`.

[0.1.0]: https://github.com/kkropachev12/NeuroGeometry/releases/tag/v0.1.0

## [0.1.1] — 2026-03-19

### Исправлено

- `Line`: исключить мутацию входного списка координат при определении ориентации линии.

[0.1.1]: https://github.com/kkropachev12/NeuroGeometry/releases/tag/v0.1.1
