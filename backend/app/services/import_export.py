from io import BytesIO

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.crm import ImportSummary, OrganizationCreate
from app.services.crm_service import CRMService


class ImportExportService:
    def __init__(self, session: AsyncSession) -> None:
        self.crm_service = CRMService(session)

    async def import_organizations_csv(self, file_bytes: bytes) -> ImportSummary:
        dataframe = pd.read_csv(BytesIO(file_bytes))
        return await self._import_dataframe(dataframe)

    async def import_organizations_excel(self, file_bytes: bytes) -> ImportSummary:
        dataframe = pd.read_excel(BytesIO(file_bytes))
        return await self._import_dataframe(dataframe)

    async def _import_dataframe(self, dataframe: pd.DataFrame) -> ImportSummary:
        imported = 0
        skipped = 0

        for row in dataframe.to_dict(orient="records"):
            website = row.get("website")
            name = row.get("name")
            if not website or not name:
                skipped += 1
                continue

            payload = OrganizationCreate(
                name=name,
                website=website,
                mission=row.get("mission"),
                description=row.get("description"),
                industry=row.get("industry"),
                location=row.get("location"),
                public_email=row.get("public_email"),
                public_contact=row.get("public_contact"),
                notes=row.get("notes"),
            )

            try:
                await self.crm_service.create_organization(payload)
                imported += 1
            except Exception:
                skipped += 1

        return ImportSummary(imported=imported, skipped=skipped)

    async def export_organizations_csv(self) -> bytes:
        organizations = await self.crm_service.list_organizations()
        rows = [
            {
                "id": org.id,
                "name": org.name,
                "website": org.website,
                "mission": org.mission,
                "description": org.description,
                "industry": org.industry,
                "location": org.location,
                "public_email": org.public_email,
                "public_contact": org.public_contact,
                "notes": org.notes,
                "created_at": org.created_at,
                "updated_at": org.updated_at,
            }
            for org in organizations
        ]
        dataframe = pd.DataFrame(rows)
        return dataframe.to_csv(index=False).encode("utf-8")

    async def export_organizations_excel(self) -> bytes:
        organizations = await self.crm_service.list_organizations()
        rows = [
            {
                "id": org.id,
                "name": org.name,
                "website": org.website,
                "mission": org.mission,
                "description": org.description,
                "industry": org.industry,
                "location": org.location,
                "public_email": org.public_email,
                "public_contact": org.public_contact,
                "notes": org.notes,
                "created_at": org.created_at,
                "updated_at": org.updated_at,
            }
            for org in organizations
        ]
        output = BytesIO()
        pd.DataFrame(rows).to_excel(output, index=False)
        return output.getvalue()
