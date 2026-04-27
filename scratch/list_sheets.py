import openpyxl
wb = openpyxl.load_workbook(r'd:\03_Projects\LTW\Test2\01_TaiLieu\TC_ChinhSuaThongTinXe.xlsx')
with open(r'd:\03_Projects\LTW\Test2\scratch\sheets.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(wb.sheetnames))
