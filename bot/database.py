
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager - إدارة قاعدة البيانات
"""

import asyncio
import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models import User, UserGroup, Level, ShopItem, Badge, DailyQuest, Clan

class DatabaseManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pool = None
    
    async def connect(self):
        """الاتصال بقاعدة البيانات"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                min_size=5,
                max_size=20
            )
            print("✅ تم الاتصال بقاعدة البيانات بنجاح!")
        except Exception as e:
            print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            raise
    
    async def disconnect(self):
        """قطع الاتصال بقاعدة البيانات"""
        if self.pool:
            await self.pool.close()
    
    async def execute_query(self, query: str, *args):
        """تنفيذ استعلام"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch_one(self, query: str, *args):
        """جلب صف واحد"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetch_all(self, query: str, *args):
        """جلب جميع الصفوف"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    # المستخدمين
    async def add_user_if_not_exists(self, user):
        """إضافة مستخدم جديد إذا لم يكن موجوداً"""
        query = """
        INSERT INTO users (id, username, first_name, last_name, language_code, is_bot)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            updated_at = CURRENT_TIMESTAMP
        """
        await self.execute_query(
            query, user.id, user.username, user.first_name, 
            user.last_name, user.language_code, user.is_bot
        )
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """الحصول على مستخدم بالمعرف"""
        query = "SELECT * FROM users WHERE id = $1"
        row = await self.fetch_one(query, user_id)
        return User.from_dict(dict(row)) if row else None
    
    # الجروبات
    async def add_group_if_not_exists(self, group_id: int, name: str):
        """إضافة جروب جديد إذا لم يكن موجوداً"""
        query = """
        INSERT INTO groups (id, name)
        VALUES ($1, $2)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            updated_at = CURRENT_TIMESTAMP
        """
        await self.execute_query(query, group_id, name)
    
    # ربط المستخدمين بالجروبات
    async def add_user_to_group_if_not_exists(self, user_id: int, group_id: int):
        """ربط المستخدم بالجروب إذا لم يكن مربوطاً"""
        query = """
        INSERT INTO user_groups (user_id, group_id)
        VALUES ($1, $2)
        ON CONFLICT (user_id, group_id) DO NOTHING
        """
        await self.execute_query(query, user_id, group_id)
    
    async def get_user_group(self, user_id: int, group_id: int) -> Optional[UserGroup]:
        """الحصول على بيانات المستخدم في الجروب"""
        query = "SELECT * FROM user_groups WHERE user_id = $1 AND group_id = $2"
        row = await self.fetch_one(query, user_id, group_id)
        return UserGroup.from_dict(dict(row)) if row else None
    
    async def update_user_stats(self, user_id: int, group_id: int, xp_gained: int, coins_gained: int):
        """تحديث إحصائيات المستخدم"""
        query = """
        UPDATE user_groups 
        SET xp = xp + $3, 
            coins = coins + $4, 
            total_messages = total_messages + 1,
            last_message_at = CURRENT_TIMESTAMP,
            last_xp_gain = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $1 AND group_id = $2
        """
        await self.execute_query(query, user_id, group_id, xp_gained, coins_gained)
    
    async def update_user_level(self, user_id: int, group_id: int, new_level_id: int):
        """تحديث مستوى المستخدم"""
        query = """
        UPDATE user_groups 
        SET level_id = $3, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $1 AND group_id = $2
        """
        await self.execute_query(query, user_id, group_id, new_level_id)
    
    # المستويات
    async def get_level_by_id(self, level_id: int) -> Optional[Level]:
        """الحصول على مستوى بالمعرف"""
        query = "SELECT * FROM levels WHERE id = $1"
        row = await self.fetch_one(query, level_id)
        return Level.from_dict(dict(row)) if row else None
    
    async def get_level_by_number(self, level_number: int) -> Optional[Level]:
        """الحصول على مستوى بالرقم"""
        query = "SELECT * FROM levels WHERE level_number = $1"
        row = await self.fetch_one(query, level_number)
        return Level.from_dict(dict(row)) if row else None
    
    async def get_level_by_xp(self, xp: int) -> Optional[Level]:
        """الحصول على المستوى المناسب لكمية XP"""
        query = """
        SELECT * FROM levels 
        WHERE required_xp <= $1 
        ORDER BY required_xp DESC 
        LIMIT 1
        """
        row = await self.fetch_one(query, xp)
        return Level.from_dict(dict(row)) if row else None
    
    # المتجر
    async def get_shop_items(self, limit: int = 50) -> List[ShopItem]:
        """الحصول على عناصر المتجر"""
        query = "SELECT * FROM shop_items WHERE is_active = TRUE ORDER BY price ASC LIMIT $1"
        rows = await self.fetch_all(query, limit)
        return [ShopItem.from_dict(dict(row)) for row in rows]
    
    async def get_shop_item_by_id(self, item_id: int) -> Optional[ShopItem]:
        """الحصول على عنصر من المتجر"""
        query = "SELECT * FROM shop_items WHERE id = $1 AND is_active = TRUE"
        row = await self.fetch_one(query, item_id)
        return ShopItem.from_dict(dict(row)) if row else None
    
    # الشارات
    async def get_all_badges(self) -> List[Badge]:
        """الحصول على جميع الشارات"""
        query = "SELECT * FROM badges WHERE is_active = TRUE"
        rows = await self.fetch_all(query)
        return [Badge.from_dict(dict(row)) for row in rows]
    
    async def get_user_badges(self, user_id: int, group_id: int) -> List[Badge]:
        """الحصول على شارات المستخدم"""
        query = """
        SELECT b.* FROM badges b
        JOIN user_badges ub ON b.id = ub.badge_id
        WHERE ub.user_id = $1 AND ub.group_id = $2
        ORDER BY ub.earned_at DESC
        """
        rows = await self.fetch_all(query, user_id, group_id)
        return [Badge.from_dict(dict(row)) for row in rows]
    
    async def get_user_badges_count(self, user_id: int, group_id: int) -> int:
        """الحصول على عدد شارات المستخدم"""
        query = "SELECT COUNT(*) FROM user_badges WHERE user_id = $1 AND group_id = $2"
        row = await self.fetch_one(query, user_id, group_id)
        return row[0] if row else 0
    
    async def award_badge(self, user_id: int, group_id: int, badge_id: int):
        """منح شارة للمستخدم"""
        query = """
        INSERT INTO user_badges (user_id, group_id, badge_id)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id, group_id, badge_id) DO NOTHING
        """
        await self.execute_query(query, user_id, group_id, badge_id)
    
    # المهام اليومية
    async def get_daily_quests(self, user_id: int, group_id: int, quest_date: date) -> List[DailyQuest]:
        """الحصول على المهام اليومية"""
        query = """
        SELECT * FROM daily_quests 
        WHERE user_id = $1 AND group_id = $2 AND quest_date = $3
        ORDER BY id
        """
        rows = await self.fetch_all(query, user_id, group_id, quest_date)
        return [DailyQuest.from_dict(dict(row)) for row in rows]
    
    async def create_daily_quest(self, user_id: int, group_id: int, quest_type: str, 
                               target_value: int, reward_xp: int, reward_coins: int, quest_date: date):
        """إنشاء مهمة يومية جديدة"""
        query = """
        INSERT INTO daily_quests (user_id, group_id, quest_type, target_value, reward_xp, reward_coins, quest_date)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        await self.execute_query(query, user_id, group_id, quest_type, target_value, reward_xp, reward_coins, quest_date)
    
    async def update_daily_quest_progress(self, user_id: int, group_id: int, quest_type: str, 
                                        progress: int, quest_date: date):
        """تحديث تقدم المهمة اليومية"""
        query = """
        UPDATE daily_quests 
        SET current_progress = current_progress + $4,
            is_completed = CASE WHEN current_progress + $4 >= target_value THEN TRUE ELSE FALSE END,
            completed_at = CASE WHEN current_progress + $4 >= target_value THEN CURRENT_TIMESTAMP ELSE completed_at END
        WHERE user_id = $1 AND group_id = $2 AND quest_type = $3 AND quest_date = $5
        """
        await self.execute_query(query, user_id, group_id, quest_type, progress, quest_date)
    
    # الكلانات
    async def get_clan_by_id(self, clan_id: int) -> Optional[Clan]:
        """الحصول على كلان بالمعرف"""
        query = "SELECT * FROM clans WHERE id = $1"
        row = await self.fetch_one(query, clan_id)
        return Clan.from_dict(dict(row)) if row else None
    
    async def get_clan_by_name(self, name: str, group_id: int) -> Optional[Clan]:
        """الحصول على كلان بالاسم"""
        query = "SELECT * FROM clans WHERE name = $1 AND group_id = $2"
        row = await self.fetch_one(query, name, group_id)
        return Clan.from_dict(dict(row)) if row else None
    
    # تسجيل الرسائل
    async def log_message(self, user_id: int, group_id: int, message_id: int, 
                         xp_gained: int, coins_gained: int, message_type: str = 'text'):
        """تسجيل رسالة"""
        query = """
        INSERT INTO message_logs (user_id, group_id, message_id, xp_gained, coins_gained, message_type)
        VALUES ($1, $2, $3, $4, $5, $6)
        """
        await self.execute_query(query, user_id, group_id, message_id, xp_gained, coins_gained, message_type)
    
    # المخزون
    async def add_to_inventory(self, user_id: int, group_id: int, item_id: int, 
                              quantity: int = 1, expires_at: datetime = None):
        """إضافة عنصر للمخزون"""
        query = """
        INSERT INTO user_inventory (user_id, group_id, item_id, quantity, expires_at)
        VALUES ($1, $2, $3, $4, $5)
        """
        await self.execute_query(query, user_id, group_id, item_id, quantity, expires_at)
    
    async def get_user_inventory(self, user_id: int, group_id: int) -> List[Dict]:
        """الحصول على مخزون المستخدم"""
        query = """
        SELECT ui.*, si.name, si.description, si.item_type, si.effect_type, si.effect_value
        FROM user_inventory ui
        JOIN shop_items si ON ui.item_id = si.id
        WHERE ui.user_id = $1 AND ui.group_id = $2 AND ui.is_active = TRUE
        AND (ui.expires_at IS NULL OR ui.expires_at > CURRENT_TIMESTAMP)
        ORDER BY ui.purchased_at DESC
        """
        rows = await self.fetch_all(query, user_id, group_id)
        return [dict(row) for row in rows]
