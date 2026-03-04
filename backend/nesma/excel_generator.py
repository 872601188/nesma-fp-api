"""
NESMA Excel Report Generator
Generates Excel reports for function point calculations.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from typing import Dict, Any
import os
from datetime import datetime

class ExcelGenerator:
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, result: Dict[str, Any]) -> str:
        """Generate an Excel report for the function point calculation."""
        wb = Workbook()
        
        # Create Summary Sheet
        self._create_summary_sheet(wb.active, result)
        
        # Create Detailed Components Sheet
        self._create_components_sheet(wb, result)
        
        # Create Complexity Distribution Sheet
        self._create_complexity_sheet(wb, result)
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"FP_Report_{result.get('project_name', 'Project').replace(' ', '_')}_{timestamp}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        wb.save(filepath)
        return filepath
    
    def _create_summary_sheet(self, ws, result: Dict[str, Any]):
        """Create the summary worksheet."""
        ws.title = "Summary"
        
        # Title
        ws['A1'] = "NESMA Function Point Analysis Report"
        ws['A1'].font = Font(size=16, bold=True)
        ws.merge_cells('A1:D1')
        
        # Project Info
        ws['A3'] = "Project Name:"
        ws['B3'] = result.get('project_name', 'N/A')
        ws['A3'].font = Font(bold=True)
        
        ws['A4'] = "Report Date:"
        ws['B4'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws['A4'].font = Font(bold=True)
        
        # Summary Table
        headers = ["Metric", "Value"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=6, column=col, value=header)
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
        
        summary_data = [
            ["Total Unadjusted Function Points", result.get('total_unadjusted_fp', 0)],
            ["Value Adjustment Factor (VAF)", result.get('vaf', 0)],
            ["Adjusted Function Points", result.get('adjusted_fp', 0)],
            ["Total Components", len(result.get('function_points', []))]
        ]
        
        for row_idx, row_data in enumerate(summary_data, 7):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                if col_idx == 1:
                    cell.font = Font(bold=True)
        
        # Component Counts
        ws['A12'] = "Component Counts"
        ws['A12'].font = Font(size=14, bold=True)
        
        headers = ["Component Type", "Count", "Weight Range"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=13, column=col, value=header)
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
        
        details = result.get('details', {})
        counts = details.get('component_counts', {})
        
        weights = {
            "ILF": "7-15",
            "EIF": "5-10",
            "EI": "3-6",
            "EO": "4-7",
            "EQ": "3-6"
        }
        
        for row_idx, (comp_type, count) in enumerate(counts.items(), 14):
            ws.cell(row=row_idx, column=1, value=comp_type)
            ws.cell(row=row_idx, column=2, value=count)
            ws.cell(row=row_idx, column=3, value=weights.get(comp_type, "N/A"))
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 15
    
    def _create_components_sheet(self, wb, result: Dict[str, Any]):
        """Create the detailed components worksheet."""
        ws = wb.create_sheet("Components")
        
        # Title
        ws['A1'] = "Detailed Function Point Components"
        ws['A1'].font = Font(size=14, bold=True)
        ws.merge_cells('A1:E1')
        
        # Headers
        headers = ["Type", "Name", "Complexity", "Weight", "Description"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
        
        # Data
        function_points = result.get('function_points', [])
        for row_idx, fp in enumerate(function_points, 4):
            ws.cell(row=row_idx, column=1, value=fp.get('type', ''))
            ws.cell(row=row_idx, column=2, value=fp.get('name', ''))
            ws.cell(row=row_idx, column=3, value=fp.get('complexity', ''))
            ws.cell(row=row_idx, column=4, value=fp.get('count', 0))
            ws.cell(row=row_idx, column=5, value=str(fp.get('description', ''))[:100])
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 10
        ws.column_dimensions['E'].width = 50
    
    def _create_complexity_sheet(self, wb, result: Dict[str, Any]):
        """Create the complexity distribution worksheet."""
        ws = wb.create_sheet("Complexity Distribution")
        
        # Title
        ws['A1'] = "Complexity Distribution by Component Type"
        ws['A1'].font = Font(size=14, bold=True)
        ws.merge_cells('A1:E1')
        
        # Headers
        headers = ["Component Type", "Low", "Average", "High", "Total"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
        
        # Data
        details = result.get('details', {})
        distribution = details.get('complexity_distribution', {})
        
        row_idx = 4
        for comp_type, complexities in distribution.items():
            ws.cell(row=row_idx, column=1, value=comp_type)
            ws.cell(row=row_idx, column=2, value=complexities.get('Low', 0))
            ws.cell(row=row_idx, column=3, value=complexities.get('Average', 0))
            ws.cell(row=row_idx, column=4, value=complexities.get('High', 0))
            total = sum(complexities.values())
            ws.cell(row=row_idx, column=5, value=total)
            row_idx += 1
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 10
        ws.column_dimensions['C'].width = 10
        ws.column_dimensions['D'].width = 10
        ws.column_dimensions['E'].width = 10
