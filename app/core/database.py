import sys
import os
#import app.models

from pathlib import Path
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from dotenv import load_dotenv
from typing import Annotated, AsyncGenerator
from fastapi import Depends

# Add root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Load env
current_dir = Path(__file__).parent
config_path = current_dir / "config.env"
load_dotenv(dotenv_path=config_path)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        #await conn.run_sync(SQLModel.metadata.create_all)
        await conn.run_sync(lambda conn: SQLModel.metadata.create_all(conn, checkfirst=True))
        return True  

SessionDep = Annotated[AsyncSession, Depends(get_session)]
