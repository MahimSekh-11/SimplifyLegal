from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Body
from typing import Optional
from .services.document_processor import DocumentProcessor
from .services.ai_service import AIService
import os

app = FastAPI(
    title="LegalSimplify API",
    version="1.0.0",
    description="API backend for simplifying legal documents into plain language with multilingual support"
)

document_processor = DocumentProcessor()
ai_service = AIService()


@app.get("/")
async def root():
    return {"message": "✅ LegalSimplify API is running"}


# Endpoint 1: Multipart/form-data (file or text)
@app.post("/analyze/form")
async def analyze_document_form(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language: str = Form("en")
):
    if file:
        content = await document_processor.process_uploaded_file(file)
    elif text and text.strip():
        content = text.strip()
    else:
        raise HTTPException(status_code=400, detail="Either file or text must be provided.")
    analysis = await ai_service.analyze_document(content, language)
    return analysis


# Endpoint 2: JSON-only (text input)
@app.post("/analyze/json")
async def analyze_document_json(payload: dict = Body(...)):
    text = payload.get("text", "").strip()
    language = payload.get("language", "en")
    if not text:
        raise HTTPException(status_code=400, detail="Text must be provided in JSON body.")
    analysis = await ai_service.analyze_document(text, language)
    return analysis


@app.get("/languages")
async def get_supported_languages():
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
