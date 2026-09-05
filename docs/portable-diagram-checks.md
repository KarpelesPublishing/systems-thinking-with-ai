# Portable diagram checks

Verified on 2026-09-05 with Python 3.12, Matplotlib 3.11.1, and the Agg renderer.
The systematic-debugging and test-driven-development skills guided reproduction
with the existing collision tests before making layout changes.

Forcing `figstyle.STYLE['font.serif'] = ['DejaVu Serif']` in memory reproduced:

| Diagram | Labels | Initial overlap |
| --- | --- | --- |
| Archetypes | fundamental fix / B | 62% |
| Archetypes | capability / negative polarity | 42% |
| Portfolio | Workforce learning / GE employment swing | 19% |
| Portfolio | Beer game / Commodity cycle | 20% |
| Portfolio | several stocks / coupled through delay | 26% |
| Repository | model document / evidence, ledger | 14% |
| RTT | referrals / negative polarity | 16% |

DejaVu Serif has wider label extents than Times New Roman in these layouts.
The initial archetype run also reported undrawn tick labels. Main independently
fixed the test collector and added portable serif regression cases. No test or
shared style edits were made as part of this bounded diagram work.

Layout changes:

* Archetypes: shift the right B center from x=4.05 to 3.95, set only
  fundamental fix to 5.2 pt, and increase the quick fix to capability sign gap
  from 0.2 to 0.4.
* Portfolio: place GE employment swing at vertical offset -0.32 and Beer game
  at +0.31; right-align the several stocks tick label. Case coordinates,
  evidence bands, tick locations, and marker meanings are unchanged.
* Repository: reduce artifact header size from 6.4 to 5.0 pt so the two long
  headers fit their boxes. The helper's sublabels scale with the header size.
* RTT: move referrals from x=1.30 to 1.05, preserving its height and font size.

All label text, numerical data, links, polarities, delays, roles, grants, and
generator assertions are preserved. The shared default remains Times New Roman
first with DejaVu Serif fallback.

Final results: four existing collision cases pass with Times New Roman, four
pass with forced DejaVu Serif, and all four portable serif regression cases
pass. Both requested font files were resolved with fallback disabled. The
300 dpi DejaVu PNGs were visually inspected, including loop rings, delay marks,
portfolio label separation, repository header boxes, and the RTT polarity sign.
An intermediate layout passed the overlap threshold but crowded a delay mark
and adjacent portfolio labels; the final layout corrects those visual issues.

Final PNG and PDF evidence is in the temporary directory
`/var/folders/3r/_5vgh9zn51zcxvjxv3sswr940000gn/T/portable-diagrams-final-86yow01d`,
under `Times New Roman` and `DejaVu Serif`, each with `png` and `print` folders.
No full figure rebuild, commits, pushes, or tags were performed.

Run this from the publishing root to repeat only these four diagrams. Output
goes to a new temporary directory, bytecode and pytest cache writes are disabled,
and the font override lasts only for the Python process.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
import pathlib
import sys
import tempfile

sys.path.insert(0, 'build/figures')
import figstyle
import pytest
from matplotlib import font_manager

out = pathlib.Path(tempfile.mkdtemp(prefix='portable-diagrams-'))
print('Evidence:', out)
figstyle.ROOT = out
selected = ('archetype_templates or case_portfolio_map or '
            'repository_structure or rtt_structure')
results = []
for font in ['Times New Roman', 'DejaVu Serif']:
    print(font, font_manager.findfont(font, fallback_to_default=False))
    figstyle.STYLE['font.serif'] = [font]
    figstyle.PNG_DIR = out / font / 'png'
    figstyle.PRINT_DIR = out / font / 'print'
    results.append(pytest.main([
        '-p', 'no:cacheprovider', 'tests/figures/test_label_collisions.py',
        '-k', f'test_no_label_sits_on_another and ({selected})', '-q',
    ]))
results.append(pytest.main([
    '-p', 'no:cacheprovider',
    'tests/figures/test_label_collisions.py::test_diagram_labels_in_portable_serif',
    '-k', selected, '-q',
]))
raise SystemExit(max(results))
PY
```
