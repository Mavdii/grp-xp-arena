
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils - الوظائف المساعدة
"""

import random
from typing import Optional
from database import DatabaseManager
from models import UserGroup, Level

def format_number(num: int) -> str:
    """تنسيق الأرقام مع الفواصل"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

def calculate_xp_gain(min_xp: int, max_xp: int) -> int:
    """حساب XP عشوائي"""
    return random.randint(min_xp, max_xp)

def calculate_coin_gain(min_coins: int, max_coins: int) -> int:
    """حساب العملات عشوائية"""
    return random.randint(min_coins, max_coins)

def get_progress_bar(percentage: float, length: int = 10) -> str:
    """إنشاء شريط التقدم"""
    filled = int(length * (percentage / 100))
    empty = length - filled
    return "█" * filled + "░" * empty

def format_time_remaining(seconds: int) -> str:
    """تنسيق الوقت المتبقي"""
    if seconds < 60:
        return f"{seconds}ث"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}د"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}س {minutes}د"

async def check_level_up(db: DatabaseManager, user_group: UserGroup) -> Optional[Level]:
    """التحقق من ترقية المستوى"""
    current_level = await db.get_level_by_id(user_group.level_id)
    if not current_level:
        return None
    
    # التحقق من وجود مستوى أعلى
    next_level = await db.get_level_by_number(current_level.level_number + 1)
    if not next_level:
        return None  # وصل للمستوى الأقصى
    
    # التحقق من توفر XP للترقية
    if user_group.xp >= next_level.required_xp:
        # ترقية المستوى
        await db.update_user_level(user_group.user_id, user_group.group_id, next_level.id)
        return next_level
    
    return None

def get_rarity_color(rarity: str) -> str:
    """الحصول على لون الندرة"""
    colors = {
        'common': '⚪',
        'rare': '🔵',
        'epic': '🟣',
        'legendary': '🟡'
    }
    return colors.get(rarity, '⚪')

def get_item_type_emoji(item_type: str) -> str:
    """الحصول على رمز نوع العنصر"""
    emojis = {
        'booster': '⚡',
        'upgrade': '🎯',
        'badge': '🏅',
        'vip': '👑',
        'protection': '🛡️'
    }
    return emojis.get(item_type, '📦')

def calculate_clan_rank(total_xp: int) -> str:
    """حساب رتبة الكلان"""
    if total_xp >= 1_000_000:
        return "🏆 أسطوري"
    elif total_xp >= 500_000:
        return "💎 ماسي"
    elif total_xp >= 100_000:
        return "🥇 ذهبي"
    elif total_xp >= 50_000:
        return "🥈 فضي"
    elif total_xp >= 10_000:
        return "🥉 برونزي"
    else:
        return "🔰 مبتدئ"

def get_quest_progress_emoji(progress: int, target: int) -> str:
    """الحصول على رمز تقدم المهمة"""
    percentage = (progress / target) * 100
    if percentage >= 100:
        return "✅"
    elif percentage >= 75:
        return "🔶"
    elif percentage >= 50:
        return "🔸"
    elif percentage >= 25:
        return "🔹"
    else:
        return "⏳"

def validate_clan_name(name: str) -> bool:
    """التحقق من اسم الكلان"""
    if not name or len(name) < 3 or len(name) > 50:
        return False
    
    # التحقق من الأحرف المسموحة
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-أبتثجحخدذرزسشصضطظعغفقكلمنهويء")
    return all(c in allowed_chars for c in name)

def get_level_tier_emoji(tier: int) -> str:
    """الحصول على رمز درجة المستوى"""
    tier_emojis = {
        1: "I",
        2: "II", 
        3: "III",
        4: "IV",
        5: "V"
    }
    return tier_emojis.get(tier, "I")

def calculate_daily_quest_difficulty(user_level: int) -> dict:
    """حساب صعوبة المهام اليومية حسب المستوى"""
    base_difficulty = {
        'messages': 20,
        'xp_gain': 50,
        'coins_gain': 25
    }
    
    # زيادة الصعوبة مع المستوى
    multiplier = 1 + (user_level * 0.1)
    
    return {
        'messages': int(base_difficulty['messages'] * multiplier),
        'xp_gain': int(base_difficulty['xp_gain'] * multiplier),
        'coins_gain': int(base_difficulty['coins_gain'] * multiplier)
    }
