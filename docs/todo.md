### Features:

- [ ] Make the app installable via pip/PyPi
- [ ] Add filter options for job postings on user dashboard
- [ ] Add CV and cover letter preview in HTML and small editor for that
- [ ] Add dashboard for run statistics, token usage, fails etc.
- [ ] Add support for locally run LLMs
- [ ] Add guardrails for agents' tasks
- [ ] Add system for handling automatic job applying

### Bugs:

- [X] Error when running pipeline for the first time without specifying user
  preferences regarding scraping (use default values when creating profile)
- [ ] System fails for some specific CSS selectors

### Internal:

- [ ] Write bash script for setting up environment (python, libraries,
  postgres/sqlite,
  environmental variables)
- [ ] Switch to using TypeScript (JS is horrible)
- [ ] Throw out Jinja2 from frontend
- [ ] Add dev scripts
- [ ] Switch to using puppeter(and find patchright counterpart for puppeter)
- [ ] Switch to using LightPanda browser (Make two possible backends)
- [ ] Add proper testing of features!!!
- [ ] Play around with screenshots and OCR
- [ ] Better async usage and add multithreading
- [ ] Switch LangChain, other framework like that or write own implementation of agents and agent loop
- [ ] Add system for tracking uniqueness of job offers in database
