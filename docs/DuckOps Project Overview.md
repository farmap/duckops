# **Project DuckOps: A DevOps & Data Exploration Blog Architecture**

Line spacing: 1.15

## **Overview**

DuckOps is a high-performance technical blog designed to showcase DevOps "tricks" and data exploration insights. The architecture follows a "Lakehouse" pattern on a single Linux server, utilizing PostgreSQL for transactional metadata and DuckDB for analytical processing of large datasets.

## **1\. API (The Engine)**

The backend is built with **FastAPI** using a **Design-First (Spec-Driven)** approach. This ensures a strict contract between the data processing logic and the frontend presentation layer.

* **Core Stack:** Python 3.11+, FastAPI, Pydantic V2, and SQLAlchemy.  
* **Analytical Layer:** DuckDB and Polars are used for zero-copy data aggregation. The API queries Parquet files directly, allowing for high-performance metrics analysis without the overhead of a traditional OLAP database.  
* **Database Strategy:** A hybrid model using PostgreSQL for blog content/user config and DuckDB for time-series metrics like process execution lag and network throughput.

| Component | Technology | Purpose |
| :---- | :---- | :---- |
| API Framework | FastAPI | Asynchronous, type-safe API endpoints. |
| Data Engine | DuckDB | High-speed analytical queries on Parquet files. |
| Migrations | Alembic | Version-controlled PostgreSQL schema evolution. |

## **2\. Frontend (The Presentation)**

The frontend utilizes **Astro** to deliver a content-first experience with minimal JavaScript bloat. It leverages the "Islands Architecture" to keep the blog fast while allowing for deep interactivity where needed.

* **Content Authoring:** Uses MDX (Markdown \+ JSX), allowing the author to embed interactive React chart components directly into long-form technical articles.  
* **Data Visualization:** Integrated with Apache ECharts to render complex datasets (e.g., Flame graphs, Gantt charts for process lag) fetched from the FastAPI backend.  
* **Styling:** Tailwind CSS for a clean, "DevOps-focused" dark-mode aesthetic.

## **3\. Deployment with GitHub Actions (The Pipeline)**

The deployment follows modern CI/CD practices, automating the build and delivery process to a self-hosted Linux server.

* **Continuous Integration:** GitHub Actions (GHA) triggers on every push to the main branch. It validates the OpenAPI spec, runs tests, and builds Docker images.  
* **Build Strategy:** Multi-stage Docker builds are employed to generate Pydantic models from the OpenAPI YAML spec at build time, ensuring the code never drifts from the documentation.  
* **Continuous Deployment:** GHA uses SSH to pull the latest images onto the Linux server and execute docker-compose up \-d.  
* **Reverse Proxy:** Caddy handles automatic SSL (HTTPS) termination with zero-touch configuration.

`# Deployment Flow`  
`1. Developer pushes MDX content or API code.`  
`2. GHA builds Docker images (API & Web).`  
`3. GHA pushes images to GitHub Container Registry (GHCR).`  
`4. GHA signals the Linux server to update.`  
`5. Caddy routes traffic to the new containers.`

This architecture represents a professional-grade personal project that demonstrates proficiency in backend engineering, data science, and infrastructure automation.