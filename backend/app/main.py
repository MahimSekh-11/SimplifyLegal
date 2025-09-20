from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Body
from typing import Optional, Union
from .services.document_processor import DocumentProcessor
from .services.ai_service import AIService
import os

# Initialize FastAPI app
app = FastAPI(
    title="LegalSimplify API",
    version="1.0.0",
    description="API backend for simplifying legal documents into plain language with multilingual support"
)

# Initialize services
document_processor = DocumentProcessor()
ai_service = AIService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "✅ LegalSimplify API is running - Making Legal Documents Simple"}


@app.post("/analyze")
async def analyze_document(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language: str = Form("en"),
    json_body: Optional[dict] = Body(None)
):
    """
    Analyze either an uploaded legal document file or raw text.
    Supports multipart form-data (file/text) or JSON body (text only).
    """
    try:
        content = None

        # If file or text in multipart/form-data
        if file:
            content = await document_processor.process_uploaded_file(file)
        elif text and text.strip():
            content = text.strip()
        # If JSON body provided
        elif json_body and "text" in json_body and json_body["text"].strip():
            content = json_body["text"].strip()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="❌ Either file or non-empty text must be provided."
            )

        # Pass content to AI Service
        analysis = await ai_service.analyze_document(content, language)
        return analysis  # dict output

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"⚠️ Analysis error: {str(e)}")


@app.get("/languages")
async def get_supported_languages():
    """List of supported languages for simplification"""
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi"},
            {"code": "bn", "name": "Bengali"},
            {"code": "ta", "name": "Tamil"},
            {"code": "te", "name": "Telugu"},
        ]
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
