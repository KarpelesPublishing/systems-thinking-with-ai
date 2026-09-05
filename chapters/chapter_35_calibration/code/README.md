# Chapter 35 pack: calibration

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| An observed sequence with its provenance and checksum | `calibrate.py` | `Series` |
| A model output the fit must reproduce, with an error function and a tolerance | `calibrate.py` | `Target` |
| A parameter the fit may move, and the range somebody will defend | `calibrate.py` | `Knob` |
| Read one column of a committed CSV as a Series | `calibrate.py` | `read_series` |
| Score one document against every target | `calibrate.py` | `error_of` |
| Coarse grid, then re-grid around the winner. Capped at one knob per three points | `calibrate.py` | `grid_fit` |
| The document with fitted values marked `inferred` and their provenance in the note | `calibrate.py` | `with_fitted` |
| Error on a window the fit never saw | `calibrate.py` | `holdout` |
| The table a chapter prints | `calibrate.py` | `fit_report` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack imports the model document (Chapter 20) and the runtime (Chapter 22).
The four real-data case packs (Chapters 36 to 39) import it.

Example:

```python
from chapters.chapter_35_calibration.code.calibrate import Knob, Target, grid_fit, read_series
```
