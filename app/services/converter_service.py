import io
import mammoth
from fastapi import UploadFile, HTTPException
from typing import Dict, Any
from app.models.style_mapper import StyleMapper
from app.models.document_transformer import DocumentTransformer


class ConverterService:
    """
    Сервис для конвертации DOCX файлов в HTML
    """
    
    def __init__(self):
        self.style_mapper = StyleMapper()
        self.style_map = self.style_mapper.create_style_mapping()
        self.document_transformer = DocumentTransformer()
    
    async def convert_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Конвертирует DOCX файл в HTML
        
        Args:
            file: Загруженный DOCX файл
            
        Returns:
            Dict с результатом конвертации
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="Файл не выбран")
        
        if not file.filename.lower().endswith('.docx'):
            raise HTTPException(
                status_code=400, 
                detail="Поддерживаются только DOCX файлы"
            )
        
        try:
            content = await file.read()
            file_like = io.BytesIO(content)
            
            # Получаем опции трансформации
            transform_options = self.document_transformer.get_transform_options()
            
            # Конвертируем с использованием стилей и трансформации
            result = mammoth.convert_to_html(
                file_like, 
                style_map=self.style_map,
                **transform_options
            )
            html_content = result.value
            messages = result.messages
            
            warnings = [msg.message for msg in messages if msg.type == "warning"]
            errors = [msg.message for msg in messages if msg.type == "error"]
            
            # Анализ предупреждений о стилях
            style_analysis = self.style_mapper.analyze_style_warnings(warnings)
            warning_summary = self.style_mapper.get_warning_summary(style_analysis)
            
            complete_html = self._create_complete_html(html_content, file.filename)
            
            return {
                "original_filename": file.filename,
                "file_size": len(content),
                "html_content": html_content,
                "complete_html": complete_html,
                "conversion_warnings": warnings,
                "conversion_errors": errors,
                "style_analysis": style_analysis,
                "warning_summary": warning_summary,
                "warnings_count": len(warnings),
                "errors_count": len(errors),
                "status": "success" if not errors else "success_with_errors"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка при конвертации файла: {str(e)}"
            )
    
    def _create_complete_html(self, html_content: str, filename: str) -> str:
        """
        Создает полный HTML документ с необходимыми тегами
        
        Args:
            html_content: HTML контент от Mammoth
            filename: Имя исходного файла
            
        Returns:
            Полный HTML документ
        """
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #333;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        p {{
            margin-bottom: 1em;
        }}
        .table-caption {{
            font-style: italic;
            text-align: center;
            font-size: 0.9em;
            margin: 0.5em 0;
        }}
        .other {{
            background-color: #f9f9f9;
            padding: 10px;
            border-left: 3px solid #ccc;
            margin: 1em 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        table, th, td {{
            border: 1px solid #ccc;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""