from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.database import init_db
from routes import user, group_session, selection_session, export, debug, dashboard, realtime, settings
from routes import join_resolver
from models.user import User
from core.dependencies import get_current_user
#, session, member, group
#app = FastAPI(title="GroupifyAssist API")

"""@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    await init_db()
    yield
    # Clean up the ML models and release the resources
    await create_db.clear()"""


app = FastAPI(title="GroupifyAssist API")
#app = FastAPI(title="GroupifyAssist API", lifespan=lifespan)

# CORS configuration: restrict to hosted frontend domain
origins = [
    "https://groupifyassist.vercel.app",
     "http://localhost:5173",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://groupifyassist.vercel.app",
        "http://localhost:5173",
    ],
    # Also allow Vercel preview deployments if needed
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''
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
'''app.include_router(session.router, prefix="/sessions", tags=["Sessions"])
app.include_router(member.router, prefix="/members", tags=["Members"])
app.include_router(group.router, prefix="/groups", tags=["Groups"])

# Start DB connection and table creation
@app.on_event("startup")
async def on_startup():
    await init_db()'''


# Health check
@app.get("/")
async def root(current_user: User = Depends(get_current_user)):
    return {"message": "Welcome to GroupifyAssist API"}
    
# Debug endpoint to check current user
@app.get("/api/debug/me")
async def debug_me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "email": current_user.email}
