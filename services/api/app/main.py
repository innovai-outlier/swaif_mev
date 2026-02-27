"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    programs,
    habits,
    check_ins,
    users,
    badges,
    enrollments,
    auth,
    admin_rewards,
    admin_badges,
    admin_programs,
    admin_analytics,
    protocol_templates,
    protocol_runs,
)

app = FastAPI(
    title="Motor Clínico - Gamification API",
    description="API para gamificação de medicina de estilo de vida",
    version="0.1.0",
)

# CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(admin_rewards.router)
app.include_router(admin_badges.router)
app.include_router(admin_programs.router)
app.include_router(admin_analytics.router)
app.include_router(programs.router)
app.include_router(habits.router)
app.include_router(check_ins.router)
app.include_router(users.router)
app.include_router(badges.router)
app.include_router(enrollments.router)
app.include_router(protocol_templates.router)
app.include_router(protocol_runs.router)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "Motor Clínico - Gamification API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
