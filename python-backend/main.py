from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import json
import ast
import traceback  # <--- Added for debugging
import RAG as rag

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def parse_llm_response(ans):
    if isinstance(ans, dict):
        return ans

    if isinstance(ans, str):
        cleaned_ans = ans.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned_ans)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(cleaned_ans)
            except (SyntaxError, ValueError):
                pass
    return {}


@app.post("/generate")
def generate_flashcards(file: UploadFile = File(...)):

    temp_file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"File saved to: {temp_file_path}")  # Debug print

        print("Starting RAG processing...")  # Debug print
        docs = rag.load_and_chunk(temp_file_path)

        print("Querying LLM...")  # Debug print
        raw_ans = rag.pipeline(docs)
        print(f"Raw LLM Answer: {raw_ans}")  # Debug print

        flashcards_dict = parse_llm_response(raw_ans)

        flashcards_list = [
            {"id": i, "question": k, "answer": v}
            for i, (k, v) in enumerate(flashcards_dict.items())
        ]
        return {"flashcards": flashcards_list}

    except Exception as e:
        print("--------------- ERROR TRACEBACK ---------------")
        traceback.print_exc()
        print("-----------------------------------------------")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print("Cleanup: Temporary file removed.")
