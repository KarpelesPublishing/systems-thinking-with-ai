# Data

Derived records for the four real-data cases (Chapters 36 to 39). Each case directory holds a
small committed CSV, a `MANIFEST.json` with its SHA-256, and a README with seven required
sections: Source, Licence, Retrieval, Derivation, Column dictionary, Checksum, Known breaks.

Rules:

- Only derived files are committed, and only from sources whose licence permits redistribution
  (Open Government Licence v3.0, or United States federal works in the public domain). The
  original downloads go to `data/raw/`, which is ignored by git.
- Nothing is committed that `scripts/fetch_data.py` cannot reproduce from the source.
- The committed checksum fixes the vintage. A later release will differ; the chapter's numbers
  describe the vintage the checksum names, and `scripts/fetch_data.py --verify` confirms you
  have the same file.
- The test suite never touches the network. `tests/test_data_manifests.py` recomputes every
  checksum offline. Live fetches are marked `network` and excluded by default.

Re-fetch (needs internet):

```
uv run python scripts/fetch_data.py nhs-rtt
uv run python scripts/fetch_data.py bls-jolts
uv run python scripts/fetch_data.py fred-capacity
uv run python scripts/fetch_data.py bts-ontime
uv run python scripts/fetch_data.py --verify
```
