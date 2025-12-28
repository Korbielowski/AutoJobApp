<h1 align="center">
<img src="https://raw.githubusercontent.com/Korbielowski/AutoApply/main/branding/main_logo_v2.jpeg" width="300">
</h1><br>

__*AI agents that look for adequate jobs and create tailored CVs and cover letters. Fully automated — no more manual effort*__
<br>

## About AutoJobApp

**AutoJobApp** is an application which goal is to greatly simplify a process of seeking for job opportunities, especially for younger and less experienced devs(not only).

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
## Usage/Quick Start

After installation the app will automatically start and fastapi will share a url, that you can then open in your browser and start using AutoJobApp.
For more information on how to use software click [HERE]().

## Configuration

Application environment can be edited via ```.env``` file, example one is present in the repository and is named ```.env.example``` with all the possible configuration options.

## Features

## Roadmap

- [X] Account
    - [X] Sign up/Sign in
    - [X] Delete/Update
- [ ] Scraping
    - [X] Sign in to websites
    - [X] Navigation to job listings
    - [X] Job information scraping
    - [ ] Website elements caching
    - [ ] Guardrails
- [X] Document generation
    - [X] CV generation
    - [X] Cover letter generation
- [ ] Applying
- [ ] Tests

## Project Structure
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
├── branding
├── docs
├── README.md
├── LICENSE
├── docker-compose.yaml
├── Dockerfile
├── pyproject.toml
└── setup.sh
```

## Contributing

Currently repository is not open for any contirbutions regarding code, tests etc. But I'm very open for feature suggestions, bugs and errors reports and improvement ideas. All of them can be posted via 'Issues' tab.

## License

See the [LICENSE](https://github.com/Korbielowski/AutoJobApp/blob/main/LICENSE)
