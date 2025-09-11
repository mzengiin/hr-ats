"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

app = FastAPI(
    title="CVFlow API",
    description="CV Management and HR Process Automation System",
    version="1.0.0"
)

# CORS middleware - Düzeltilmiş ayarlar
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CVFlow API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is working correctly"}

# CORS middleware otomatik olarak OPTIONS request'leri hallediyor

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Import models to ensure they are registered
from app.models import *  # This will import all models

# Include API routers
from app.api.v1 import auth, users, files, roles, dashboard, candidates, interviews, case_studies

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["Candidates"])
app.include_router(interviews.router, prefix="/api/v1/interviews", tags=["Interviews"])
app.include_router(case_studies.router, prefix="/api/v1/case-studies", tags=["Case Studies"])

