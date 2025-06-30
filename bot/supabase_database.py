
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Database Manager - إدارة قاعدة البيانات باستخدام Supabase
"""

import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models import User, UserGroup, Level, ShopItem, Badge, DailyQuest, Clan

class SupabaseManager:
    def __init__(self):
        """تهيئة Supabase client"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("متغيرات Supabase غير موجودة!")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    # المستخدمين
    async def add_user_if_not_exists(self, user):
        """إضافة مستخدم جديد إذا لم يكن موجوداً"""
        try:
            # البحث عن المستخدم أولاً
            existing = self.supabase.table('users').select('*').eq('id', user.id).execute()
            
            if not existing.data:
                # إضافة مستخدم جديد
                self.supabase.table('users').insert({
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'language_code': user.language_code,
                    'is_bot': user.is_bot
                }).execute()
            else:
                # تحديث البيانات الموجودة
                self.supabase.table('users').update({
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }).eq('id', user.id).execute()
        except Exception as e:
            print(f"خطأ في إضافة المستخدم: {e}")
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """الحصول على مستخدم بالمعرف"""
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            if result.data:
                return User.from_dict(result.data[0])
            return None
        except Exception as e:
            print(f"خطأ في جلب المستخدم: {e}")
            return None
    
    # الجروبات
    async def add_group_if_not_exists(self, group_id: int, name: str):
        """إضافة جروب جديد إذا لم يكن موجوداً"""
        try:
            existing = self.supabase.table('groups').select('*').eq('id', group_id).execute()
            
            if not existing.data:
                self.supabase.table('groups').insert({
                    'id': group_id,
                    'name': name
                }).execute()
            else:
                self.supabase.table('groups').update({
                    'name': name
                }).eq('id', group_id).execute()
        except Exception as e:
            print(f"خطأ في إضافة الجروب: {e}")
    
    # ربط المستخدمين بالجروبات
    async def add_user_to_group_if_not_exists(self, user_id: int, group_id: int):
        """ربط المستخدم بالجروب إذا لم يكن مربوطاً"""
        try:
            existing = self.supabase.table('user_groups').select('*').eq('user_id', user_id).eq('group_id', group_id).execute()
            
            if not existing.data:
                self.supabase.table('user_groups').insert({
                    'user_id': user_id,
                    'group_id': group_id
                }).execute()
        except Exception as e:
            print(f"خطأ في ربط المستخدم بالجروب: {e}")
    
    async def get_user_group(self, user_id: int, group_id: int) -> Optional[UserGroup]:
        """الحصول على بيانات المستخدم في الجروب"""
        try:
            result = self.supabase.table('user_groups').select('*').eq('user_id', user_id).eq('group_id', group_id).execute()
            if result.data:
                return UserGroup.from_dict(result.data[0])
            return None
        except Exception as e:
            print(f"خطأ في جلب بيانات المستخدم: {e}")
            return None
    
    async def update_user_stats(self, user_id: int, group_id: int, xp_gained: int, coins_gained: int):
        """تحديث إحصائيات المستخدم"""
        try:
            # جلب البيانات الحالية
            current = self.supabase.table('user_groups').select('xp, coins, total_messages').eq('user_id', user_id).eq('group_id', group_id).execute()
            
            if current.data:
                old_data = current.data[0]
                new_xp = old_data['xp'] + xp_gained
                new_coins = old_data['coins'] + coins_gained
                new_messages = old_data['total_messages'] + 1
                
                self.supabase.table('user_groups').update({
                    'xp': new_xp,
                    'coins': new_coins,
                    'total_messages': new_messages,
                    'last_message_at': datetime.now().isoformat(),
                    'last_xp_gain': datetime.now().isoformat()
                }).eq('user_id', user_id).eq('group_id', group_id).execute()
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {e}")
    
    async def update_user_level(self, user_id: int, group_id: int, new_level_id: int):
        """تحديث مستوى المستخدم"""
        try:
            self.supabase.table('user_groups').update({
                'level_id': new_level_id
            }).eq('user_id', user_id).eq('group_id', group_id).execute()
        except Exception as e:
            print(f"خطأ في تحديث المستوى: {e}")
    
    # المستويات
    async def get_level_by_id(self, level_id: int) -> Optional[Level]:
        """الحصول على مستوى بالمعرف"""
        try:
            result = self.supabase.table('levels').select('*').eq('id', level_id).execute()
            if result.data:
                return Level.from_dict(result.data[0])
            return None
        except Exception as e:
            print(f"خطأ في جلب المستوى: {e}")
            return None
    
    async def get_level_by_number(self, level_number: int) -> Optional[Level]:
        """الحصول على مستوى بالرقم"""
        try:
            result = self.supabase.table('levels').select('*').eq('level_number', level_number).execute()
            if result.data:
                return Level.from_dict(result.data[0])
            return None
        except Exception as e:
            print(f"خطأ في جلب المستوى: {e}")
            return None
    
    async def get_level_by_xp(self, xp: int) -> Optional[Level]:
        """الحصول على المستوى المناسب لكمية XP"""
        try:
            result = self.supabase.table('levels').select('*').lte('required_xp', xp).order('required_xp', desc=True).limit(1).execute()
            if result.data:
                return Level.from_dict(result.data[0])
            return None
        except Exception as e:
            print(f"خطأ في جلب المستوى بـ XP: {e}")
            return None
    
    # المتجر
    async def get_shop_items(self, limit: int = 50) -> List[ShopItem]:
        """الحصول على عناصر المتجر"""
        try:
            result = self.supabase.table('shop_items').select('*').eq('is_active', True).order('price').limit(limit).execute()
            return [ShopItem.from_dict(item) for item in result.data]
        except Exception as e:
            print(f"خطأ في جلب عناصر المتجر: {e}")
            return []
    
    async def get_shop_item_by_id(self, item_id: int) -> Optional[ShopItem]:
        """الحصول على عنصر من المتجر"""
        try:
            result = self.supabase.table('shop_items').select('*').eq('id', item_id).eq('is_active', True).execute()
            if result.data:
                return ShopItem.from_dict(result.data[0])
            return None
        except Exception as e:
            print(f"خطأ في جلب عنصر المتجر: {e}")
            return None
    
    # الشارات
    async def get_all_badges(self) -> List[Badge]:
        """الحصول على جميع الشارات"""
        try:
            result = self.supabase.table('badges').select('*').eq('is_active', True).execute()
            return [Badge.from_dict(badge) for badge in result.data]
        except Exception as e:
            print(f"خطأ في جلب الشارات: {e}")
            return []
    
    async def get_user_badges(self, user_id: int, group_id: int) -> List[Badge]:
        """الحصول على شارات المستخدم"""
        try:
            result = self.supabase.table('user_badges').select('badges(*)').eq('user_id', user_id).eq('group_id', group_id).execute()
            return [Badge.from_dict(item['badges']) for item in result.data if item['badges']]
        except Exception as e:
            print(f"خطأ في جلب شارات المستخدم: {e}")
            return []
    
    async def get_user_badges_count(self, user_id: int, group_id: int) -> int:
        """الحصول على عدد شارات المستخدم"""
        try:
            result = self.supabase.table('user_badges').select('id', count='exact').eq('user_id', user_id).eq('group_id', group_id).execute()
            return result.count or 0
        except Exception as e:
            print(f"خطأ في عد الشارات: {e}")
            return 0
    
    async def award_badge(self, user_id: int, group_id: int, badge_id: int):
        """منح شارة للمستخدم"""
        try:
            self.supabase.table('user_badges').insert({
                'user_id': user_id,
                'group_id': group_id,
                'badge_id': badge_id
            }).execute()
        except Exception as e:
            print(f"خطأ في منح الشارة: {e}")
    
    # المهام اليومية
    async def get_daily_quests(self, user_id: int, group_id: int, quest_date: date) -> List[DailyQuest]:
        """الحصول على المهام اليومية"""
        try:
            result = self.supabase.table('daily_quests').select('*').eq('user_id', user_id).eq('group_id', group_id).eq('quest_date', quest_date.isoformat()).execute()
            return [DailyQuest.from_dict(quest) for quest in result.data]
        except Exception as e:
            print(f"خطأ في جلب المهام اليومية: {e}")
            return []
    
    async def create_daily_quest(self, user_id: int, group_id: int, quest_type: str, 
                               target_value: int, reward_xp: int, reward_coins: int, quest_date: date):
        """إنشاء مهمة يومية جديدة"""
        try:
            self.supabase.table('daily_quests').insert({
                'user_id': user_id,
                'group_id': group_id,
                'quest_type': quest_type,
                'target_value': target_value,
                'reward_xp': reward_xp,
                'reward_coins': reward_coins,
                'quest_date': quest_date.isoformat()
            }).execute()
        except Exception as e:
            print(f"خطأ في إنشاء المهمة اليومية: {e}")
    
    async def update_daily_quest_progress(self, user_id: int, group_id: int, quest_type: str, 
                                        progress: int, quest_date: date):
        """تحديث تقدم المهمة اليومية"""
        try:
            # جلب المهمة الحالية
            current = self.supabase.table('daily_quests').select('current_progress, target_value').eq('user_id', user_id).eq('group_id', group_id).eq('quest_type', quest_type).eq('quest_date', quest_date.isoformat()).execute()
            
            if current.data:
                old_progress = current.data[0]['current_progress']
                target = current.data[0]['target_value']
                new_progress = old_progress + progress
                is_completed = new_progress >= target
                
                update_data = {
                    'current_progress': new_progress,
                    'is_completed': is_completed
                }
                
                if is_completed:
                    update_data['completed_at'] = datetime.now().isoformat()
                
                self.supabase.table('daily_quests').update(update_data).eq('user_id', user_id).eq('group_id', group_id).eq('quest_type', quest_type).eq('quest_date', quest_date.isoformat()).execute()
        except Exception as e:
            print(f"خطأ في تحديث تقدم المهمة: {e}")
    
    # الكلانات
    async def get_clan_by_id(self, clan_id: int) -> Optional[Clan]:
        """الحصول على كلان بالمعرف"""
        try:
            result = self.supabase.table('clans').select('*').eq('id', clan_id).execute()
            if result.data:
                return Clan.from_dict(result.data[0])
            return None
        except Exception as e:
            print(f"خطأ في جلب الكلان: {e}")
            return None
    
    async def get_clan_by_name(self, name: str, group_id: int) -> Optional[Clan]:
        """الحصول على كلان بالاسم"""
        try:
            result = self.supabase.table('clans').select('*').eq('name', name).eq('group_id', group_id).execute()
            if result.data:
                return Clan.from_dict(result.data[0])
            return None
        except Exception as e:
            print(f"خطأ في جلب الكلان بالاسم: {e}")
            return None
    
    # تسجيل الرسائل
    async def log_message(self, user_id: int, group_id: int, message_id: int, 
                         xp_gained: int, coins_gained: int, message_type: str = 'text'):
        """تسجيل رسالة"""
        try:
            self.supabase.table('message_logs').insert({
                'user_id': user_id,
                'group_id': group_id,
                'message_id': message_id,
                'xp_gained': xp_gained,
                'coins_gained': coins_gained,
                'message_type': message_type
            }).execute()
        except Exception as e:
            print(f"خطأ في تسجيل الرسالة: {e}")
    
    # المخزون
    async def add_to_inventory(self, user_id: int, group_id: int, item_id: int, 
                              quantity: int = 1, expires_at: datetime = None):
        """إضافة عنصر للمخزون"""
        try:
            insert_data = {
                'user_id': user_id,
                'group_id': group_id,
                'item_id': item_id,
                'quantity': quantity
            }
            
            if expires_at:
                insert_data['expires_at'] = expires_at.isoformat()
            
            self.supabase.table('user_inventory').insert(insert_data).execute()
        except Exception as e:
            print(f"خطأ في إضافة العنصر للمخزون: {e}")
    
    async def get_user_inventory(self, user_id: int, group_id: int) -> List[Dict]:
        """الحصول على مخزون المستخدم"""
        try:
            result = self.supabase.table('user_inventory').select('*, shop_items(name, description, item_type, effect_type, effect_value)').eq('user_id', user_id).eq('group_id', group_id).eq('is_active', True).execute()
            return [dict(item) for item in result.data]
        except Exception as e:
            print(f"خطأ في جلب المخزون: {e}")
            return []
