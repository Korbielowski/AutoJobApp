### Features:

- [ ] Make the app installable via pip/PyPi
- [ ] Add filter options for job postings on user dashboard
- [ ] Add CV and cover letter preview in HTML and small editor for that
- [ ] Add dashboard for run statistics, token usage, fails etc.
- [ ] Add support for locally run LLMs
- [ ] Add guardrails for agents' tasks
- [ ] Add system for handling automatic job applying
- [ ] Add prompt editor (default values would consist of prompts currently used)
- [/] Add model picker
- [/] Hide user's email and password used for logging into job posting websites
- [ ] Allow user to specify browser backend (LightPanda, Chrome, Chromium)

### Bugs:

- [x] Error when running pipeline for the first time without specifying user
  preferences regarding scraping (use default values when creating profile)
- [/] System fails for some specific CSS selectors (Add escape logic for some of the special symbols like '[]')
- [x] When editing websites on user account page, user needs to edit it twice to
  change the website url
- [x] Experience is not saved when registering/creating new user
- [x] Frontend error when adding new certificate on account page

### Minor issues:

- [x] Fix placeholder values for edit form fields on user account page
- [ ] Styling is off when adding new information about user or editing existing data (register page, account page)

### Internal:

- [ ] Write bash script for setting up environment (python, libraries,
  postgres/sqlite, environmental variables)
- [ ] Add make for automating different parts of application building, testing etc.
- [ ] Switch to using TypeScript (JS is horrible)
- [ ] Throw out Jinja2 from frontend
- [ ] Add dev scripts
- [ ] Switch to using puppeter(and find patchright counterpart for puppeter)
- [ ] Use LightPanda browser
- [ ] Add proper testing of features!!!
- [ ] Add github CI for testing, building and publishing
- [ ] Play around with screenshots and OCR
- [ ] Better async usage and add multithreading
- [/] Switch to PydanticAI, other framework like that or write own implementation of
  agents and agent loop
- [ ] Add system for tracking uniqueness of job offers in database
- [ ] Switch to Websockets (currently SSE)
- [ ] Look at Pico for CSS
- [ ] Better error/exception handling and messages for user
