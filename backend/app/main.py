import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import jobs, cv_review, grammar_check, resources, auth, users, applications
from fastapi.middleware.cors import CORSMiddleware
import os

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Job Tracker API")

# Determine static files directory
static_dir = "/app/static" if os.path.exists("/app/static") else "../frontend"
index_file = "/app/index.html" if os.path.exists("/app/index.html") else "../../index.html"

# Mount static files for frontend assets
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(cv_review.router, prefix="/api/cv-review", tags=["cv-review"])
app.include_router(grammar_check.router, prefix="/api/grammar-check", tags=["grammar-check"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(applications.router, prefix="/api", tags=["applications"])

origins = [
    "http://localhost",  
    "http://localhost:3000",
    "http://localhost:8080",
    "*"  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

# Serve index.html on root
@app.get("/")
async def root():
    """Serve the main index.html page"""
    return FileResponse(index_file)

# Serve dashboard.html on /dashboard
@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard page"""
    dashboard_file = "/app/static/frontend/dashboard.html" if os.path.exists("/app/static") else "../frontend/dashboard.html"
    return FileResponse(dashboard_file)

# Serve login page
@app.get("/login")
async def login():
    """Serve the login page"""
    login_file = "/app/static/frontend/log-in.html" if os.path.exists("/app/static") else "../frontend/log-in.html"
    return FileResponse(login_file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
