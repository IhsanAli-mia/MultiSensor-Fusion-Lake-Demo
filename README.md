```text
fusion-lake/
├── data/                ← never committed; mounted by workflow
│   ├── [x] raw/             ← S3 prefix "raw/" (object store truth, chunked Zarr)
│   ├── [ ] posterior/       ← S3 prefix "posterior/" (μ, Σ, ELBO etc.)
│   └── [ ] scratch/         ← temp workspace, auto-GC'd by Make targets
├── [x] stac/                ← STAC Items & Collections (JSON)
├── src/
│   ├── fusion_lake/     ← importable Python package
│   │   ├── [x] ingest/      ← Stage-1/2 DAG nodes (warp → zarr)
│   │   ├── [ ] posterior/   ← Stage-3 notebooks / Papermill drivers
│   │   ├── [ ] ledger/      ← Stage-4 append-only Γ log helpers
│   │   └── [ ] utils/       ← checksum, logging, S3 helpers
│   └── __init__.py
├── workflows/
│   ├── [x] ingestion_dag.py   (Prefect)
│   └── [ ] posterior_dag.py   (Papermill → Zarr)
├── .github/workflows/
│   ├── [ ] ci.yml           ← lint + unit + stac-validator
│   └── [ ] nightly.yml      ← schedule: 'posterior_dag' on UTC 00:30
├── [x] pyproject.toml       ← poetry + isort + black; pins rasterio ≥1.3, zarr ≥2.17
├── [ ] Makefile             ← `make ingest file=...` / `make validate`
├── [x] README.md            ← usage, DAG diagram, bucket policy snips
└── [x] LICENSE              ← MIT
