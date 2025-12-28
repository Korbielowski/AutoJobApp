<h1 align="center">
<img src="https://raw.githubusercontent.com/Korbielowski/AutoApply/main/branding/main_logo_v2.jpeg" width="500">
</h1><br>

__*AI agents that look for adequate jobs and create tailored CVs and cover letters. Fully automated — no more manual effort*__
<br>

# About AutoJobApp

**AutoJobApp** is an application which goal is to greatly simplify a process of seeking for job opportunities, especially for younger and less experienced devs(not only).

# Installation and Configuration Guide

## Configuration

Application environment can be edited via ```.env``` file, example one is present in the repository and is named ```.env.example``` with all the possible configuration options.

The most important key in the config file is
```OPENAI_API_KEY="<your-openai-api-key>"```, as it's critical for website scraping and automatic document generation.

## Docker Installation (Recommended):

### Requirements:
- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

```bash
git clone https://github.com/Korbielowski/AutoJobApp
cd AutoJobApp/
docker compose build
```

## Local Installation:

### Requirements:
- [Python 3.12+](https://www.python.org/downloads/) (Recommended [uv](https://docs.astral.sh/uv/getting-started/installation/))
- [PostgreSQL 14+](https://www.postgresql.org/download/)
- [Weasyprint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)

```bash
git clone https://github.com/Korbielowski/AutoJobApp
cd AutoJobApp/
sh setup.sh
```
# Usage/Quick Start

After configuration and installation of the application, you can simply run it using commands below and then click the link that fastapi returs e.g. ```http://127.0.0.1:8000```. Then You can click the link or copy it to your preferred browser and use the application.

For more information on how to use software click [HERE](https://github.com/Korbielowski/AutoJobApp/blob/main/docs/guides/basic_guide.md).

### Docker (Recommended)
```bash
docker compose up
```

### Local
```bash
sh setup.sh --run
```
```bash
fastapi run backend/app.py
```


# Features

# Roadmap

- [X] Account
    - [X] Sign up/Sign in
    - [X] Delete/Update
    - [X] Multiple profiles
- [ ] Scraping
    - [X] Sign in to websites
    - [X] Navigation to job listings
    - [X] Job information scraping
    - [ ] Website elements caching
    - [ ] Guardrails
- [X] Document generation
    - [X] CV generation
    - [X] Cover letter generation
- [ ] Automatic applying
- [ ] Tests

# Project Structure
```bash
.
├── backend
│   ├── career_documents
│   ├── database
│   ├── llm
│   │   └── prompts
│   ├── routes
│   ├── schemas
│   ├── scrapers
│   ├── static
│   └── templates
├── docs
│   └── guides
├── branding
├── README.md
├── LICENSE
├── docker-compose.yaml
├── Dockerfile
├── pyproject.toml
└── setup.sh
```

# Contributing

Currently repository is not open for any contirbutions regarding code, tests etc. But I'm very open for feature suggestions, bugs and errors reports and improvement ideas. All of them can be posted via 'Issues' tab on GitHub.

# License

See the [LICENSE](https://github.com/Korbielowski/AutoJobApp/blob/main/LICENSE)
