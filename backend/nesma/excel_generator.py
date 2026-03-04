from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from datetime import datetime

def generate_excel_to_buffer(function_data, output_buffer, project_name="软件项目"):
    wb = Workbook()
    ws = wb.active
    ws.title = "功能点清单"
    
    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 40
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 10
    ws.column_dimensions['F'].width = 10
    
    ws.merge_cells('A1:F1')
    title_cell = ws['A1']
    title_cell.value = f"{project_name} - NESMA 功能点评估清单"
    title_cell.font = Font(size=16, bold=True)
    title_cell.alignment = Alignment(horizontal='center')
    title_cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    ws.row_dimensions[1].height = 30
    
    ws.merge_cells('A2:F2')
    ws['A2'].value = f"评估日期: {datetime.now().strftime('%Y-%m-%d')}"
    ws['A2'].alignment = Alignment(horizontal='right')
    
    headers = ['序号', '功能模块', '功能描述', '功能类型', '复杂度', '功能点']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.fill = PatternFill(start_color='B4C7E7', end_color='B4C7E7', fill_type='solid')
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    details = function_data.get('details', [])
    for idx, item in enumerate(details, 1):
        row = 4 + idx
        ws.cell(row=row, column=1, value=idx)
        ws.cell(row=row, column=2, value=item.get('module', ''))
        ws.cell(row=row, column=3, value=item.get('description', ''))
        ws.cell(row=row, column=4, value=item.get('type', ''))
        ws.cell(row=row, column=5, value=item.get('complexity', ''))
        ws.cell(row=row, column=6, value=item.get('fp', 0))
    
    total_row = 5 + len(details)
    ws.merge_cells(f'A{total_row}:E{total_row}')
    ws.cell(row=total_row, column=1, value="功能点总计").font = Font(bold=True)
    ws.cell(row=total_row, column=1).alignment = Alignment(horizontal='right')
    ws.cell(row=total_row, column=6, value=function_data.get('total', 0))
    ws.cell(row=total_row, column=6).font = Font(bold=True)
    ws.cell(row=total_row, column=6).fill = PatternFill(start_color='FFD966', end_color='FFD966', fill_type='solid')
    
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    for row_cells in ws[f'A4:F{total_row}']:
        for cell in row_cells:
            cell.border = thin_border
    
    wb.save(output_buffer)
