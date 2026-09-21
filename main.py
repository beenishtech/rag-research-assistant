from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from rag_engine import process_pdf_files, ask_rag_engine

app = FastAPI(title="Research Paper RAG Assistant", version="1.0")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files mount (if HTML frontend in static folder)
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def home():
    # if in static folder exists index.html then serve by this
    return FileResponse("static/index.html")

@app.post("/upload-pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """
    Multiple PDF files upload karne ke liye endpoint.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Koi file select nahi ki gayi.")
    
    uploaded_files = process_pdf_files(files)
    return {
        "message": "PDFs successfully upload and processed ",
        "files_processed": uploaded_files
    }

@app.post("/chat")
def chat_with_rag(request: QueryRequest):
    """
    endpoint to ask question from uploaded paper.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question can't be empty.")
    
    result = ask_rag_engine(question=request.question)
    return result