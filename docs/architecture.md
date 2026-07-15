# Architecture

## Design Goals

- preserve the recovered 2022 database faithfully
- isolate modernization work from legacy artifacts
- allow analysis without requiring ArcGIS Pro
- expose a clear path from recovered dump to normalized analytical outputs

## Practical Legacy Strategy

The dump restores into `public.*` to preserve the original object names. The modernization layer adds `legacy.*` compatibility views rather than rewriting the recovered tables in place.

```mermaid
flowchart LR
    Dump["Recovered PostgreSQL custom dump"] --> Public["public.* restored legacy tables"]
    Public --> Legacy["legacy.* compatibility views"]
    Legacy --> Core["core.* normalized tables"]
    Legacy --> Analytics["analytics.* corrected queries"]
    Metadata["metadata.* aliases + provenance"] --> Core
    Core --> Outputs["outputs/query_results + outputs/figures"]
```

## Schemas

- `public`: faithful restore target for the legacy dump
- `legacy`: read-only compatibility views over `public`
- `metadata`: source datasets and alias tables
- `core`: normalized relational and spatial tables
- `analytics`: views and reusable analytical logic

## Separation of Responsibilities

- Legacy tables are treated as immutable reference artifacts.
- Modern constraints, foreign keys, and normalized names are applied only in `core`.
- Query corrections and new analyses live in `analytics`.
- Generated outputs live under `outputs/`.

