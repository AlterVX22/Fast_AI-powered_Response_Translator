from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.llm_utils import translate_text_with_llm, generate_itmo_response
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    source_lang: str = "auto"

@app.post("/translate")
async def translate(req: TranslateRequest):
    try:
        result = translate_text_with_llm(
            text=req.text,
            target_lang=req.target_lang,
            source_lang=req.source_lang
        )
        if "Ошибка" in result or "Error" in result:
            raise HTTPException(status_code=400, detail=result)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/itmo-translate")
async def itmo_translate():
    try:
        responses = generate_itmo_response()
        return {"responses": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)