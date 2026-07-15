import io

import pandas as pd
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.crm import OrganizationCreate
from app.services.crm_service import CRMService
from app.services.import_export import ImportExportService


@pytest.mark.asyncio
async def test_import_export_csv_roundtrip(session: AsyncSession) -> None:
    service = ImportExportService(session)

    frame = pd.DataFrame(
        [
            {"name": "A", "website": "https://a.org"},
            {"name": "B", "website": "https://b.org"},
        ]
    )
    payload = frame.to_csv(index=False).encode("utf-8")

    summary = await service.import_organizations_csv(payload)
    assert summary.imported == 2

    exported = await service.export_organizations_csv()
    assert b"https://a.org" in exported


@pytest.mark.asyncio
async def test_import_export_excel_and_skip_invalid(session: AsyncSession) -> None:
    crm = CRMService(session)
    await crm.create_organization(
        OrganizationCreate(name="Existing", website="https://existing.org")
    )

    service = ImportExportService(session)
    frame = pd.DataFrame(
        [
            {"name": "Existing Dup", "website": "https://existing.org"},
            {"name": "No Website"},
            {"name": "Fresh", "website": "https://fresh.org"},
        ]
    )
    buffer = io.BytesIO()
    frame.to_excel(buffer, index=False)

    summary = await service.import_organizations_excel(buffer.getvalue())
    assert summary.imported == 1
    assert summary.skipped == 2

    xlsx = await service.export_organizations_excel()
    assert len(xlsx) > 0
