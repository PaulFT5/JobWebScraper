from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import filterRoute, jobsCardRoute
from backend.utils.data_setup import data_folder_setup

data_folder_setup()
app = FastAPI(title="Job Scraper & Matcher API")

# Enable CORS so your Svelte dev server (usually localhost:5173) can talk to FastAPI (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filterRoute.router, prefix="/api")
app.include_router(jobsCardRoute.router, prefix="/api")