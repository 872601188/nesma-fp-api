from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
sys.path.append('/app/nesma')
from analyzer import NESMAAnalyzer
from calculator import calculate_fp
from excel_generator import generate_excel
import io
from fastapi.responses import StreamingResponse

app = FastAPI(title="NESMA FP API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = NESMAAnalyzer()

class AnalyzeRequest(BaseModel):
    requirement: str
    project_name: Optional[str] = "软件项目"

class CalculateRequest(BaseModel):
    functions: List[dict]
    method: str = "detailed"

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        result = analyzer.analyze(req.requirement)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calculate")
def calculate(req: CalculateRequest):
    try:
        result = calculate_fp(req.functions, req.method)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/excel")
def export_excel(req: AnalyzeRequest):
    try:
        analysis = analyzer.analyze(req.requirement)
        calc_result = calculate_fp(analysis['functions'], 'detailed')
        
        output = io.BytesIO()
        generate_excel_to_buffer(calc_result, output, req.project_name)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={req.project_name}_FP.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
