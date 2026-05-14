# DuckOps
Blog Project combining insights into devops, and data discovery using DuckDb. The goal is to flesh out this blog with snippets and charts that I may find useful, as well as info I may discover on the way.  Essentially, this is my ultimate take on dogfooding.
# Languages

 - python >= 3.11
 - node >= 24

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
├── build/              # for codegen from spec output
└── docker-compose.yml  # Orchestrates API, Web, and Postgres
```

# build fastapi code from openapi specification

```
fastapi-codegen --input ./api/spec/openapi.yml --output ./build
```
# init astro project from blog template

```
nvm use 24.12.0
cd ./web
npm create astro@latest
(create in empty ./web dir & select blog template)
run dev server: npm run dev
```

# add astro plugins
```
npx astro add mdx
npx astro add tailwind
```