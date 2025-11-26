from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, engine, Base
from app.routers import auth, tasks, companies, dashboard, employees, leaves, shifts, payroll, attendance, notifications, notification_preferences
from app.routers.profile_fixed import router as profile
from app.custom_json_response import CustomJSONResponse

# Only create tables when running the app directly, not when imported for testing
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workforce App", version="1.0", default_response_class=CustomJSONResponse)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin explicitly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(leaves.router, prefix="/api")
app.include_router(shifts.router, prefix="/api")
app.include_router(payroll.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(notification_preferences.router, prefix="/api")
app.include_router(profile, prefix="/api")

from app.seed_demo_user_final import seed_demo_user
from app.deps import get_db

@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    seed_demo_user(db)

app.include_router(dashboard.router, prefix="/api")
@app.get("/")
def root():
    return {"message": f"Welcome to the Workforce App! Environment: {settings.APP_ENV}"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/test")
def test_endpoint():
    return {"test": "value", "number": 123, "boolean": True}
