from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parser import parse_excel
from app.services.budget_analyzer import analyze_expenses, calculate_forecast, calculate_503020
import traceback

router = APIRouter(prefix="/excel", tags=["excel"])

@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    print(f"=== ПОЛУЧЕН ФАЙЛ: {file.filename} ===")
    print(f"Content-Type: {file.content_type}")
    
    try:
        contents = await file.read()
        print(f"Размер файла: {len(contents)} байт")
        
        # Сохраняем файл для отладки
        with open("debug_uploaded.xlsx", "wb") as f:
            f.write(contents)
        print("Файл сохранён как debug_uploaded.xlsx")
        
        transactions = parse_excel(contents, file.filename)
        print(f"Получено транзакций: {len(transactions)}")
        
        if not transactions:
            raise Exception("Не удалось извлечь данные из файла")
        
        result = analyze_expenses(transactions)
        print("Анализ завершён успешно")
        return result
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")

@router.post("/forecast")
async def get_forecast(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        transactions = parse_excel(contents, file.filename)
        result = calculate_forecast(transactions)
        return result
    except Exception as e:
        print(f"ОШИБКА forecast: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")

@router.post("/budget_distribution")
async def get_budget_distribution(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        transactions = parse_excel(contents, file.filename)
        result = calculate_503020(transactions)
        return result
    except Exception as e:
        print(f"ОШИБКА budget: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")