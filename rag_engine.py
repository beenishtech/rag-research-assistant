import os
import pdfplumber
from dotenv import load_dotenv
from groq import Groq

# environment variables load from .ev file
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found! Please .env file check.")

client = Groq(api_key=api_key)

# Global storage for document chunks (In-memory storage)
document_store = []

def process_pdf_files(file_objs):
    """
    Multiple PDF files's read then their text, filename, and page numbers will extract .
    """
    global document_store
    document_store = [] #for  old data clear
    
    extracted_data_summary = []

    for file_obj in file_objs:
        filename = file_obj.filename
        try:
            # PDF read from pdfplumber
            with pdfplumber.open(file_obj.file) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        document_store.append({
                            "filename": filename,
                            "page_number": page_num,
                            "content": text
                        })
            extracted_data_summary.append(filename)
        except Exception as e:
            print(f"Error reading {filename}: {str(e)}")
            
    return extracted_data_summary

def search_relevant_context(question: str):
    """
    It searches the document store for information related to the user's question.
    """
    if not document_store:
        return None, "No document uploaded."

     #Instead of doing a simple keyword search or returning just the first chunk.
     #we can send all the chunks or the best matches as context.
     #The best approach is to combine all the relevant text.
    context_text = ""
    sources = []
    
    #Right now, we are creating context from all the uploaded text so the model gets complete information
    for doc in document_store:
        context_text += f"\n[Source: {doc['filename']}, Page: {doc['page_number']}]\n{doc['content']}\n"
        sources.append({"filename": doc["filename"], "page_number": doc["page_number"]})
        
    return context_text, sources

def ask_rag_engine(question: str):
    """
    It uses the Groq LLM to generate answers based on the uploaded documents.
    """
    context, sources = search_relevant_context(question)
    
    if not context:
        return {
            "answer": "First upload research paper (PDF),I don't have any data to read.",
            "sources": []
        }

    prompt = f"""
   You are a Research Paper Assistant. You must answer questions based only on the context provided below. 
   If the answer is not in the context, clearly state that 'This information is not available in the uploaded documents.' 
   Always include the source document name and page number with every answer, as given in the context as [Source: filename, Page: X]

    Context:
    {context}

    Sawal: {question}
    """

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a strict and accurate AI research assistant who answers questions based only on the provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        answer = completion.choices[0].message.content
        return {
            "answer": answer,
        }
    except Exception as e:
        return {
            "answer": f"Error aagaya: {str(e)}",
        }