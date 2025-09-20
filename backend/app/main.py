from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from typing import Optional
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
    language: str = Form("en")  # Use standard language codes
):
    """
    Analyze either an uploaded legal document file or raw text.
    Returns simplified explanation, risks, and recommended actions.
    """
    try:
        if file:
            # Process uploaded file (PDF/Image/Text)
            content = await document_processor.process_uploaded_file(file)
        elif text and text.strip() != "":
            # Use provided text
            content = text.strip()
        else:
            raise HTTPException(
                status_code=400,
                detail="❌ Either file or non-empty text must be provided."
            )

        # Pass content to AI Service
        analysis = await ai_service.analyze_document(content, language)
        return analysis  # This is now a dict, no schema needed

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

    # Render sets PORT=10000 by default
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
