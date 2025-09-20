from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from typing import Optional
from .services.document_processor import DocumentProcessor
from .services.ai_service import AIService, DocumentAnalysis

app = FastAPI(title="LegalSimplify API", version="1.0.0")

# Initialize services
document_processor = DocumentProcessor()
ai_service = AIService()

@app.get("/")
async def root():
    return {"message": "LegalSimplify API - Making Legal Documents Simple"}

@app.post("/analyze", response_model=DocumentAnalysis)
async def analyze_document(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language: str = Form("english")
):
    try:
        if file:
            content = await document_processor.process_uploaded_file(file)
        elif text:
            content = text
        else:
            raise HTTPException(
                status_code=400,
                detail="Either file or text must be provided"
            )
        
        analysis = await ai_service.analyze_document(content, language)
        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

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
    import os

    port = int(os.environ.get("PORT", 10000))  # Render assigns PORT=10000
    uvicorn.run(app, host="0.0.0.0", port=port)

