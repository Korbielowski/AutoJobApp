from fastapi import APIRouter

from backend.routes import pages, account
from backend.routes.crud import tools, user_preferences, users, projects, charities, languages, programming_languages, locations, educations, job_entries, experiences, social_platforms, websites

api_router = APIRouter()
api_router.include_router(pages.router)
api_router.include_router(account.router)
api_router.include_router(users.router)
api_router.include_router(user_preferences.router)
api_router.include_router(tools.router)
api_router.include_router(projects.router)
api_router.include_router(charities.router)
api_router.include_router(languages.router)
api_router.include_router(programming_languages.router)
api_router.include_router(locations.router)
api_router.include_router(educations.router)
# api_router.include_router(job_entries.router)
api_router.include_router(experiences.router)
api_router.include_router(social_platforms.router)
api_router.include_router(websites.router)
