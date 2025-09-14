from fastapi import FastAPI, Depends
import os
from fastapi.middleware.cors import CORSMiddleware

# from core.database import init_db
from routes import user, group_session, selection_session, export, debug, dashboard, realtime, settings
from routes import join_resolver
from models.user import User
from core.dependencies import get_current_user
#, session, member, group
#app = FastAPI(title="GroupifyAssist API")

# Lifespan/init hooks can be added here if needed


app = FastAPI(title="GroupifyAssist API")
#app = FastAPI(title="GroupifyAssist API", lifespan=lifespan)

# CORS configuration: restrict to hosted frontend domain
# Allow-list of exact origins and an optional regex for Vercel previews
origins = [
    "https://groupifyassist.vercel.app",
    "http://localhost:5173",
    "http://localhost",
    "http://localhost:8080",
]

# Allow additional comma-separated origins via env (e.g., custom domains)
extra_origins = os.getenv("CORS_EXTRA_ORIGINS", "").strip()
if extra_origins:
    origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*\\.vercel\\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Example alternative CORS config can be added here if needed
# Register Routers
app.include_router(user.router, tags=["Authentication"])
app.include_router(group_session.router)
app.include_router(selection_session.router)
app.include_router(join_resolver.router)
app.include_router(export.router)
app.include_router(debug.router)
app.include_router(dashboard.router)
app.include_router(realtime.router)
app.include_router(settings.router)
# Example: register additional routers or startup hooks here


# Health check
@app.get("/")
async def root():
    return {"message": "Welcome to GroupifyAssist API"}
    
# Debug endpoint to check current user
@app.get("/api/debug/me")
async def debug_me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "email": current_user.email}
