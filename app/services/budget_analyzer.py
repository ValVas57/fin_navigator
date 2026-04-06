from typing import List, Dict
from collections import defaultdict
from datetime import datetime

def analyze_expenses(transactions: List[Dict]) -> Dict:
    """Полный анализ расходов (без категории 'работа')"""
    if not transactions:
        return {
            "status": "ok",
            "total": 0,
            "table_data": [],
            "chart_data": [],
            "months": [],
            "totals_by_month": [],
            "monthly_avg": {},
            "months_table_data": [],
            "recommendations": ["Нет данных для анализа"]
        }
    
    # Группировка по месяцам
    monthly_data = defaultdict(lambda: defaultdict(float))
    category_total = defaultdict(float)
    
    for t in transactions:
        # Пропускаем категорию "работа" (на всякий случай)
        if t["category"] == "работа":
            continue
        
        date = t["date"]
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, "%Y-%m-%d")
            except:
                date = datetime.now()
        month_key = date.strftime("%Y-%m")
        category = t["category"]
        amount = t["amount"]
        
        monthly_data[month_key][category] += amount
        category_total[category] += amount
    
    total_expenses = sum(category_total.values())
    
    # Сортируем месяцы
    months = sorted(monthly_data.keys())
    
    # Данные для графика по месяцам
    totals_by_month = [sum(monthly_data[m].values()) for m in months]
    
    # Данные для таблицы (всего)
    table_data = [{"category": cat, "amount": amt, "percent": round(amt/total_expenses*100, 1)} 
                  for cat, amt in sorted(category_total.items(), key=lambda x: x[1], reverse=True)]
    
    # Данные для круговой диаграммы (топ-8)
    chart_data = table_data[:8]
    
    # Средние по категориям за месяц
    monthly_avg = {}
    months_count = len(months) if months else 1
    for cat in category_total:
        monthly_avg[cat] = round(category_total[cat] / months_count, 1)
    
    # Данные по месяцам для фильтрации
    months_table_data = []
    for month in months:
        month_total = sum(monthly_data[month].values())
        cat_list = [{"category": cat, "amount": amt, "percent": round(amt/month_total*100, 1) if month_total > 0 else 0} 
                    for cat, amt in sorted(monthly_data[month].items(), key=lambda x: x[1], reverse=True)]
        months_table_data.append({
            "month": month,
            "total": round(month_total),
            "categories": cat_list
        })
    
    # Рекомендации
    recommendations = []
    if table_data:
        top_cat = table_data[0]["category"]
        recommendations.append(f"📌 Самая затратная категория: {top_cat}. Попробуйте сократить на 10-15%")
    
    if len(months) >= 2 and totals_by_month[-1] > totals_by_month[-2] * 1.2:
        percent_increase = round((totals_by_month[-1]/totals_by_month[-2]-1)*100)
        recommendations.append(f"📈 Расходы выросли на {percent_increase}% за последний месяц")
    
    if not recommendations:
        recommendations.append("✅ Хорошая динамика! Продолжайте")
    
    return {
        "status": "ok",
        "total": round(total_expenses),
        "table_data": table_data,
        "chart_data": chart_data,
        "months": months,
        "totals_by_month": totals_by_month,
        "monthly_avg": monthly_avg,
        "months_table_data": months_table_data,
        "recommendations": recommendations
    }

def calculate_forecast(transactions: List[Dict]) -> Dict:
    """Прогноз рисков (без категории 'работа')"""
    if not transactions:
        return {
            "status": "ok",
            "forecast": {
                "avg_monthly": 0,
                "recommended_reserve": 0,
                "risk_level": "low",
                "risks": ["Нет данных для анализа"]
            }
        }
    
    # Группировка по месяцам
    monthly_totals = defaultdict(float)
    for t in transactions:
        if t["category"] == "работа":
            continue
        date = t["date"]
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, "%Y-%m-%d")
            except:
                date = datetime.now()
        month_key = date.strftime("%Y-%m")
        monthly_totals[month_key] += t["amount"]
    
    totals = list(monthly_totals.values())
    avg_monthly = sum(totals) / len(totals) if totals else 0
    recommended_reserve = avg_monthly * 3
    
    # Оценка риска
    if len(totals) >= 2:
        max_val = max(totals)
        min_val = min(totals) if min(totals) > 0 else 1
        volatility = max_val / min_val
        if volatility > 1.5:
            risk_level = "high"
        elif volatility > 1.2:
            risk_level = "medium"
        else:
            risk_level = "low"
    else:
        risk_level = "low"
    
    risks = []
    if avg_monthly > 50000:
        risks.append(f"💰 Средние расходы {avg_monthly:,.0f} ₽. Резерв: {recommended_reserve:,.0f} ₽")
    if risk_level == "high":
        risks.append("⚠️ Высокая волатильность расходов")
    
    return {
        "status": "ok",
        "forecast": {
            "avg_monthly": round(avg_monthly),
            "recommended_reserve": round(recommended_reserve),
            "risk_level": risk_level,
            "risks": risks if risks else ["✅ Стабильные расходы"]
        }
    }

def calculate_503020(transactions: List[Dict], total_income: float = None) -> Dict:
    """Расчёт бюджета 50/30/20 (без категории 'работа')"""
    if not transactions:
        return {
            "status": "ok",
            "total": 0,
            "needs": {"actual": 0, "ideal": 0, "percent": 0},
            "wants": {"actual": 0, "ideal": 0, "percent": 0},
            "savings": {"actual": 0, "ideal": 0, "percent": 0},
            "recommendations": ["Нет данных"]
        }
    
    needs_categories = ["продукты", "жкх", "лекарства", "лечение", "квартира", "коммунальные", "транспорт", "связь", "интернет", "машина"]
    wants_categories = ["кафе", "рестораны", "развлечения", "хобби", "подарки", "путешествия", "косметика", "одежда", "алкоголь", "обувь", "бытовая химия", "косметические средства", "бытовая техника", "тлф, пк", "дача"]
    
    # Исключаем "работа" из транзакций
    filtered_transactions = [t for t in transactions if t["category"] != "работа"]
    
    total_expenses = sum(t["amount"] for t in filtered_transactions)
    
    needs_total = sum(t["amount"] for t in filtered_transactions if t["category"] in needs_categories)
    wants_total = sum(t["amount"] for t in filtered_transactions if t["category"] in wants_categories)
    savings_total = total_expenses - needs_total - wants_total
    
    if total_income and total_income > 0:
        ideal_needs = total_income * 0.5
        ideal_wants = total_income * 0.3
        ideal_savings = total_income * 0.2
    else:
        ideal_needs = total_expenses * 0.5
        ideal_wants = total_expenses * 0.3
        ideal_savings = total_expenses * 0.2
    
    recommendations = []
    if needs_total > ideal_needs:
        recommendations.append(f"📌 Обязательные расходы ({needs_total:,.0f} ₽) выше 50%")
    if wants_total > ideal_wants:
        recommendations.append(f"🎯 Расходы на желания ({wants_total:,.0f} ₽) выше нормы")
    if savings_total < ideal_savings:
        recommendations.append(f"💰 Накопления ({savings_total:,.0f} ₽) меньше 20%")
    
    return {
        "status": "ok",
        "total": round(total_expenses),
        "needs": {
            "actual": round(needs_total),
            "ideal": round(ideal_needs),
            "percent": round(needs_total / total_expenses * 100) if total_expenses > 0 else 0
        },
        "wants": {
            "actual": round(wants_total),
            "ideal": round(ideal_wants),
            "percent": round(wants_total / total_expenses * 100) if total_expenses > 0 else 0
        },
        "savings": {
            "actual": round(savings_total),
            "ideal": round(ideal_savings),
            "percent": round(savings_total / total_expenses * 100) if total_expenses > 0 else 0
        },
        "recommendations": recommendations if recommendations else ["✅ Идеальный баланс!"]
    }
