import json
from typing import List, Dict

def process_financial_question(question: str, user_data: Dict = None) -> str:
    """Умный AI-ассистент для финансовых вопросов"""
    question_lower = question.lower()
    
    # Сценарий 1: Накопить за год
    if "накопить" in question_lower and "за год" in question_lower:
        import re
        numbers = re.findall(r'\d+', question)
        if numbers:
            target = int(numbers[0])
            monthly = target / 12
            return f"""🎯 Для накопления {target:,} ₽ за год нужно откладывать по {monthly:,.0f} ₽ в месяц.
📊 Ежемесячный взнос: {monthly:,.0f} ₽
📅 Срок: 12 месяцев
💰 Общая сумма: {target:,} ₽
💡 Совет: Открыть накопительный счёт под 10% годовых"""
    
    # Сценарий 2: Купить ноутбук / дорогую вещь
    if "купить" in question_lower or "могу ли я" in question_lower:
        import re
        numbers = re.findall(r'\d+', question)
        if numbers:
            price = int(numbers[0])
            if price < 50000:
                return f"✅ Да, вы можете купить это за {price:,} ₽. Ваш бюджет позволяет эту покупку."
            elif price < 150000:
                return f"🤔 Покупка за {price:,} ₽. Потребуется копить 3-4 месяца по {price//4:,.0f} ₽ в месяц."
            else:
                return f"⚠️ Покупка за {price:,} ₽ требует планирования. Рекомендуемый срок накопления: 8-12 месяцев."
    
    # Сценарий 3: Перерасход
    if "перерасход" in question_lower or "много трачу" in question_lower:
        return """⚠️ Выявлен перерасход.
📊 Рекомендации:
1. Проанализируйте ежедневные траты
2. Установите лимит на месяц
3. Ищите альтернативы с меньшей стоимостью"""
    
    return f"""🤖 ФинНавигатор: {question}
Что я могу сделать:
• Рассчитать накопления за год
• Оценить возможность крупной покупки
• Проанализировать перерасход
Уточните вопрос для точного расчёта!"""

def get_education_recommendations(hobbies: List[str]) -> List[Dict]:
    """Рекомендации курсов на основе хобби"""
    recommendations = []
    
    for hobby in hobbies:
        hobby_lower = hobby.lower()
        if "программ" in hobby_lower or "it" in hobby_lower or "код" in hobby_lower:
            recommendations.append({
                "title": "Python-разработчик",
                "description": "Full-stack на Python с нуля",
                "duration": "6 месяцев",
                "cost": 89000,
                "potential_income": "150 000 - 300 000 ₽/мес"
            })
        elif "дизайн" in hobby_lower or "рис" in hobby_lower:
            recommendations.append({
                "title": "UI/UX дизайнер",
                "description": "Дизайн интерфейсов и приложений",
                "duration": "4 месяца",
                "cost": 75000,
                "potential_income": "120 000 - 250 000 ₽/мес"
            })
        elif "финанс" in hobby_lower or "экономи" in hobby_lower:
            recommendations.append({
                "title": "Финансовый аналитик",
                "description": "Управление личными и корпоративными финансами",
                "duration": "3 месяца",
                "cost": 45000,
                "potential_income": "80 000 - 150 000 ₽/мес"
            })
    
    if not recommendations:
        recommendations.append({
            "title": "Финансовая грамотность",
            "description": "Основы управления деньгами и инвестиций",
            "duration": "2 месяца",
            "cost": 25000,
            "potential_income": "Экономия до 50 000 ₽/год"
        })
    
    return recommendations[:5]