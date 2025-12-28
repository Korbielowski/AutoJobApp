<h1 align="center">
<img src="https://raw.githubusercontent.com/Korbielowski/AutoApply/main/branding/main_logo_v2.jpeg" width="300">
</h1><br>

__*AI agents that look for adequate jobs and create tailored CVs and cover letters. Fully automated — no more manual effort*__
<br>

## About AutoJobApp

## Installation Guide

### Docker (Recommended):

#### Requirements:
- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

```bash
git clone https://github.com/Korbielowski/AutoJobApp
cd AutoJobApp/
docker compose up --build
```

### Local Installation:

#### Requirements:
- [Python 3.12+](https://www.python.org/downloads/) (Recommended [uv](https://docs.astral.sh/uv/getting-started/installation/))
- [PostgreSQL 14+](https://www.postgresql.org/download/)
- [Weasyprint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)

```bash
git clone https://github.com/Korbielowski/AutoJobApp
cd AutoJobApp/
sh setup.sh --run
```
