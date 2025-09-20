from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .services.document_processor import DocumentProcessor
from .services.ai_service import AIService, DocumentAnalysis
from .middleware import add_security_headers
from .config import get_settings
from fastapi import Form

app = FastAPI(title="LegalSimplify API", version="1.0.0")

# Add middleware
app.middleware("http")(add_security_headers)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://simplifylegal-11.onrender.com",  # Your frontend URL
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            raise HTTPException(status_code=400, detail="Either file or text must be provided")
        
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
            {"code": "te", "name": "Telugu"}
        ]
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
