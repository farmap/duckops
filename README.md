# DuckOps
Blog Project combining insights into devops, and data discovery using DuckDb. The goal is to flesh out this blog with snippets and charts that I may find useful, as well as info I may discover on the way.  Essentially, this is my ultimate take on dogfooding.

# initial project layout
```
duckops/
├── .github/workflows/  # CI/CD (GHA)
├── api/                # FastAPI + DuckDB logic
│   ├── spec/           # openapi.yaml (Source of Truth)
│   ├── src/            # Hand-written endpoints
│   └── Dockerfile      # Multi-stage build (Spec -> Pydantic)
├── web/                # Astro + MDX
│   ├── src/content/    # Your blog posts (.mdx)
│   └── src/components/ # ECharts islands
├── data/               # Python scripts for data aggregation
│   └── raw/            # .parquet files (git-ignored if large)
└── docker-compose.yml  # Orchestrates API, Web, and Postgres
```