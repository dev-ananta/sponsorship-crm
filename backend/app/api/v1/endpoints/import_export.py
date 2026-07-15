from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response

from app.api.deps import get_import_export_service
from app.schemas.crm import ImportSummary
from app.services.import_export import ImportExportService

router = APIRouter(prefix="/import-export", tags=["import-export"])


@router.post("/import/csv", response_model=ImportSummary)
async def import_csv(
    file: UploadFile = File(...),
    service: ImportExportService = Depends(get_import_export_service),
) -> ImportSummary:
    content = await file.read()
    return await service.import_organizations_csv(content)


@router.post("/import/excel", response_model=ImportSummary)
async def import_excel(
    file: UploadFile = File(...),
    service: ImportExportService = Depends(get_import_export_service),
) -> ImportSummary:
    content = await file.read()
    return await service.import_organizations_excel(content)


@router.get("/export/csv")
async def export_csv(
    service: ImportExportService = Depends(get_import_export_service),
) -> Response:
    payload = await service.export_organizations_csv()
    return Response(
        content=payload,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="organizations.csv"'},
    )


@router.get("/export/excel")
async def export_excel(
    service: ImportExportService = Depends(get_import_export_service),
) -> Response:
    payload = await service.export_organizations_excel()
    return Response(
        content=payload,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": 'attachment; filename="organizations.xlsx"'},
    )
