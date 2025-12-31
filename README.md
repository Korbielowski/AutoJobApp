<h1 align="center">
<img src="https://raw.githubusercontent.com/Korbielowski/AutoApply/main/branding/main_logo_v2.jpeg" width="500">
</h1><br>

__*AI agents that look for adequate jobs and create tailored CVs and cover letters. Fully automated — no more manual effort*__
<br>
<br>

# About AutoJobApp

**AutoJobApp** is an application whose goal is to greatly simplify the process of seeking for job opportunities, especially for younger and less experienced developers(not limited to junior profiles), that would also be easy to use, free, and open-source.

# Installation and Configuration Guide

## Configuration (Optional)

The application environment can be edited via ```.env``` file. An example is provided in the repository as ```.env.example``` with all the possible configuration options.

The most important key in the config file is
```OPENAI_API_KEY="<your-openai-api-key>"```, as it's critical for the proper functioning of the application(website scraping and automatic document generation).```OPENAI_API_KEY``` is the only config variable you should set manually.

## Docker Installation (Recommended):

### Requirements:
- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)(Optional. Install only if using Postgres database backend)

```bash
git clone https://github.com/Korbielowski/AutoJobApp
cd AutoJobApp/
docker compose build
```

## Local Installation:

### Requirements:
- [Python 3.12+](https://www.python.org/downloads/) (Recommended [uv](https://docs.astral.sh/uv/getting-started/installation/))
- [PostgreSQL 14+](https://www.postgresql.org/download/)(Optional. Install only if using Postgres database backend)
- [Weasyprint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)

```bash
git clone https://github.com/Korbielowski/AutoJobApp
cd AutoJobApp/
sh setup.sh
```
# Usage/Quick Start

After the configuration and installation of the application, you can run it using the commands below. Then click the link that the FastAPI backend returns, e.g. ```http://127.0.0.1:8000```.

For more information on how to use the software, click [HERE](https://github.com/Korbielowski/AutoJobApp/blob/main/docs/guides/basic_guide.md).

### Docker (Recommended)
```bash
docker compose up
```

### Local
```bash
sh setup.sh --run
```
Or
```bash
fastapi run backend/app.py
```

# Features

- Centralized dashboard aggregating job listings from multiple sources
- Support for multiple candidate profiles with separate preferences
- Editable user preferences, experience and search criteria
- Automated CV and cover letter generation tailored to each job offer
- Configurable scraping runs with per-profile settings
- Structured storage of job data and generated documents

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
├── backend                 # Core project directory
│   ├── career_documents    # CV and cover letter generation
│   ├── database            # Database operations and models
│   ├── llm                 # Prompt loading and requests to LLMs
│   │   └── prompts         # Prompts in yaml files
│   ├── routes              # FastAPI application routes
│   ├── schemas             # Endpoint and LLM response models
│   ├── scrapers            # Scraper logic and utility functions
│   ├── static              # Icons and styling
│   └── templates           # HTML templates
├── docs                    # Project documentation
│   └── guides              # Guides on how to use software
├── branding                # AutoJobApp logos and images
├── README.md               # Document with general project information
├── LICENSE                 # Project's license
├── docker-compose.yaml     # Docker orchestration file(connecting backend and database)
├── Dockerfile              # Dockerfile for fastapi backend
├── pyproject.toml          # File containing project metadata, dependencies, configs
├── .env.example            # File containing example user's application configuration
└── setup.sh                # Setup file for local installation
```

# Contributing

Currently, the repository is not open for any contributions regarding code, tests, etc. But I'm open to feature suggestions, bug reports and improvement ideas. All of them can be posted via the ['Issues'](https://github.com/Korbielowski/AutoJobApp/issues) tab on GitHub.

# License

The AutoJobApp project is published under the MIT license. Here you can see the full [LICENSE](https://github.com/Korbielowski/AutoJobApp/blob/main/LICENSE).
