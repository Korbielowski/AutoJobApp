<h1 align="center">
<img src="https://raw.githubusercontent.com/Korbielowski/AutoJobApp/main/branding/main_logo_v2.jpeg" width="500">
</h1><br>

__*AI agents that look for adequate jobs and create tailored CVs and cover letters. Fully automated — no more manual effort*__
<br>
<br>

# About AutoJobApp

**AutoJobApp** is an application whose goal is to greatly simplify the process of seeking for job opportunities, especially for younger and less experienced developers(not limited to junior profiles), that would also be easy to use, free, and open-source.

# Installation and Configuration Guide


### Requirements:
- [Python 3.12+](https://www.python.org/downloads/) (Recommended [uv](https://docs.astral.sh/uv/getting-started/installation/))
- [Weasyprint](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)

### Installation:

```bash
uv install autojobapp
```
#### Or
```bash
pip install autojobapp
```

# Usage/Quick Start

```bash
autojobapp
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
