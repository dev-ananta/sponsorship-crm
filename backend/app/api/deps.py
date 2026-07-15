from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.crm_service import CRMService
from app.services.import_export import ImportExportService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


def get_crm_service(session: AsyncSession = Depends(get_db)) -> CRMService:
    return CRMService(session)


def get_import_export_service(
    session: AsyncSession = Depends(get_db),
) -> ImportExportService:
    return ImportExportService(session)
