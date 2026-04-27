from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db, SessionLocal
from .api import auth, traffic, dashboard, admin, websocket


def create_default_admin():
    """Ensure at least one admin user exists on startup."""
    from .models.user import User, UserRole
    from .utils.security import get_password_hash
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_exists:
            admin_user = User(
                username="admin",
                email="admin@trafficiq.com",
                full_name="System Admin",
                hashed_password=get_password_hash("admin1234"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(admin_user)
            db.commit()
            print("✅ Default admin created — username: admin / password: admin1234")
        else:
            # Fix any admin accounts with invalid .local email domain
            bad_admins = db.query(User).filter(
                User.role == UserRole.ADMIN,
                User.email.like("%@%.local")
            ).all()
            for u in bad_admins:
                u.email = u.email.replace(".local", ".com")
                print(f"✅ Fixed email for {u.username}: {u.email}")
            if bad_admins:
                db.commit()
            # Promote existing user by username if needed
            target = db.query(User).filter(User.username == "hello123").first()
            if target and target.role != UserRole.ADMIN:
                target.role = UserRole.ADMIN
                db.commit()
                print(f"✅ Promoted hello123 to ADMIN")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application"""
    # Startup
    print("🚀 Starting Traffic Congestion Analysis API...")
    init_db()
    create_default_admin()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-Time Traffic Congestion Analysis Dashboard API",
    version="1.0.0",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": "1.0.0"
        }
    )


# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(traffic.router, prefix=f"{settings.API_V1_PREFIX}/traffic", tags=["Traffic"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_PREFIX}/dashboard", tags=["Dashboard"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
