"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="CVFlow API",
    description="CV Management and HR Process Automation System",
    version="1.0.0"
)

# CORS middleware - Acil çözüm
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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

# Import models to ensure they are registered
from app.models.user import User
from app.models.user_role import UserRole
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.models.cv_file import CVFile

# Include API routers
from app.api.v1 import auth, users, files, roles

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])

