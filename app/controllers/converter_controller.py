from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from app.services.converter_service import ConverterService

router = APIRouter(tags=["converter"])


@router.post("/convert")
async def convert_file(
    file: UploadFile = File(...),
    format: str = Query("json", description="Формат ответа: json или html")
):
    """
    Конвертирует DOCX файл в HTML
    
    Parameters:
    - file: DOCX файл для конвертации
    - format: Формат ответа - 'json' (по умолчанию) или 'html'
    
    Returns:
    - При format=json: JSON с информацией о конвертации
    - При format=html: HTML страница с результатом конвертации
    """
    try:
        converter_service = ConverterService()
        result = await converter_service.convert_file(file)
        
        if format.lower() == "html":
            return HTMLResponse(
                content=result["complete_html"],
                status_code=200
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Файл успешно конвертирован",
                "original_filename": result["original_filename"],
                "file_size": result["file_size"],
                "html_content": result["html_content"],
                "complete_html": result["complete_html"],
                "conversion_warnings": result["conversion_warnings"],
                "conversion_errors": result["conversion_errors"],
                "style_analysis": result["style_analysis"],
                "warning_summary": result["warning_summary"],
                "warnings_count": result["warnings_count"],
                "errors_count": result["errors_count"],
                "status": result["status"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )