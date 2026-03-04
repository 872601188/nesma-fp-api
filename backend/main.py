from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from nesma.analyzer import RequirementAnalyzer
from nesma.calculator import FunctionPointCalculator
from nesma.excel_generator import ExcelGenerator

app = FastAPI(
    title="NESMA Function Point API",
    description="API for calculating NESMA function points from software requirements",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class RequirementInput(BaseModel):
    text: str
    project_name: Optional[str] = "Untitled Project"

class FunctionPoint(BaseModel):
    type: str  # ILF, EIF, EI, EO, EQ
    name: str
    complexity: str  # Low, Average, High
    count: int

class CalculationResult(BaseModel):
    project_name: str
    function_points: List[FunctionPoint]
    total_unadjusted_fp: float
    adjusted_fp: float
    vaf: float  # Value Adjustment Factor
    details: dict

# Initialize components
analyzer = RequirementAnalyzer()
calculator = FunctionPointCalculator()
excel_gen = ExcelGenerator()

@app.get("/")
def read_root():
    return {
        "message": "NESMA Function Point API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze", response_model=CalculationResult)
def analyze_requirements(input_data: RequirementInput):
    """Analyze requirements text and calculate function points"""
    try:
        # Analyze requirements
        components = analyzer.analyze(input_data.text)
        
        # Calculate function points
        result = calculator.calculate(components)
        
        return CalculationResult(
            project_name=input_data.project_name,
            function_points=result["function_points"],
            total_unadjusted_fp=result["total_unadjusted_fp"],
            adjusted_fp=result["adjusted_fp"],
            vaf=result["vaf"],
            details=result["details"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...), project_name: Optional[str] = "Untitled Project"):
    """Upload and analyze a requirements file"""
    try:
        content = await file.read()
        text = content.decode("utf-8")
        
        components = analyzer.analyze(text)
        result = calculator.calculate(components)
        
        return CalculationResult(
            project_name=project_name,
            function_points=result["function_points"],
            total_unadjusted_fp=result["total_unadjusted_fp"],
            adjusted_fp=result["adjusted_fp"],
            vaf=result["vaf"],
            details=result["details"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export-excel")
def export_excel(result: CalculationResult):
    """Export calculation result to Excel file"""
    try:
        file_path = excel_gen.generate(result.dict())
        return {
            "message": "Excel file generated successfully",
            "download_url": f"/download/{file_path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nesma/complexity-table")
def get_complexity_table():
    """Get NESMA complexity weight table"""
    return {
        "ILF": {"Low": 7, "Average": 10, "High": 15},
        "EIF": {"Low": 5, "Average": 7, "High": 10},
        "EI": {"Low": 3, "Average": 4, "High": 6},
        "EO": {"Low": 4, "Average": 5, "High": 7},
        "EQ": {"Low": 3, "Average": 4, "High": 6}
    }

@app.get("/nesma/gsc-factors")
def get_gsc_factors():
    """Get General System Characteristics factors"""
    return {
        "factors": [
            {"id": 1, "name": "Data Communications", "description": "How many communication facilities are there?"},
            {"id": 2, "name": "Distributed Data Processing", "description": "How are distributed data and processing functions handled?"},
            {"id": 3, "name": "Performance", "description": "Did the user require response time or throughput?"},
            {"id": 4, "name": "Heavily Used Configuration", "description": "How heavily used is the current hardware platform?"},
            {"id": 5, "name": "Transaction Rate", "description": "How frequently are transactions executed?"},
            {"id": 6, "name": "Online Data Entry", "description": "What percentage of the information is entered online?"},
            {"id": 7, "name": "End-User Efficiency", "description": "Was the application designed for end-user efficiency?"},
            {"id": 8, "name": "Online Update", "description": "How many ILFs are updated by online transactions?"},
            {"id": 9, "name": "Complex Processing", "description": "Does the application have complex processing?"},
            {"id": 10, "name": "Reusability", "description": "Was the application developed to meet one or many user needs?"},
            {"id": 11, "name": "Installation Ease", "description": "How difficult is conversion and installation?"},
            {"id": 12, "name": "Operational Ease", "description": "How effective is start-up, backup, and recovery?"},
            {"id": 13, "name": "Multiple Sites", "description": "Was the application designed for multiple sites?"},
            {"id": 14, "name": "Facilitate Change", "description": "Was the application designed to facilitate change?"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
