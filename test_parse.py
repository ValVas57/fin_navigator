import xlrd
import sys

# Открываем ваш файл
file_path = "Затраты.xls"
print(f"Читаем файл: {file_path}")

try:
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)
    
    print(f"Имя листа: {sheet.name}")
    print(f"Количество строк: {sheet.nrows}")
    print(f"Количество колонок: {sheet.ncols}")
    
    print("\n=== Первые 5 строк файла ===")
    for row_idx in range(min(5, sheet.nrows)):
        row_values = []
        for col_idx in range(sheet.ncols):
            val = sheet.cell_value(row_idx, col_idx)
            row_values.append(str(val)[:30] if val else "None")
        print(f"Строка {row_idx}: {row_values}")
    
    print("\n=== Заголовки (строка 0) ===")
    headers = []
    for col_idx in range(sheet.ncols):
        val = sheet.cell_value(0, col_idx)
        if val:
            headers.append(str(val))
            print(f"Колонка {col_idx}: {val}")
    
    print(f"\nВсего найдено категорий: {len(headers)}")
    
    print("\n=== Данные по месяцам ===")
    for row_idx in range(1, sheet.nrows):
        month = sheet.cell_value(row_idx, 0)
        if month:
            print(f"\nСтрока {row_idx}: Месяц = {month}")
            for col_idx in range(1, min(5, sheet.ncols)):
                val = sheet.cell_value(row_idx, col_idx)
                if val and isinstance(val, (int, float)) and val != 0:
                    print(f"  {headers[col_idx] if col_idx < len(headers) else col_idx}: {val}")
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()