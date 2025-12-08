from fastapi import FastAPI, HTTPException
from .schemas import ValidacaoDocumentoSchema
from .services import validate_document_service

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Coordenadoria": "Extensão"}

@app.post("/validacao/")
async def validar_documento_estagio(doc: ValidacaoDocumentoSchema):
    return await validate_document_service(doc)
