#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot - نظام XP والمستويات والعملات مع Supabase
مطور بواسطة: Assistant
الإصدار: 2.0.0
"""

import asyncio
import logging
import os
import random
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)

from supabase_database import SupabaseManager
from models import User, UserGroup, Level, ShopItem, Badge, DailyQuest, Clan
from utils import (
    format_number, calculate_xp_gain, calculate_coin_gain,
    check_level_up, get_progress_bar, format_time_remaining
)

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        """تهيئة البوت"""
        self.token = token
        self.db = SupabaseManager()
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
        # إعدادات البوت
        self.XP_COOLDOWN = 60  # ثانية
        self.MAX_XP_PER_MESSAGE = 15
        self.MIN_XP_PER_MESSAGE = 5
        self.MAX_COINS_PER_MESSAGE = 10
        self.MIN_COINS_PER_MESSAGE = 1
        
    def setup_handlers(self):
        """إعداد معالجات الأوامر"""
        # الأوامر الأساسية
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # أوامر الإحصائيات
        self.application.add_handler(CommandHandler("xp", self.xp_command))
        self.application.add_handler(CommandHandler("level", self.level_command))
        self.application.add_handler(CommandHandler("progress", self.progress_command))
        self.application.add_handler(CommandHandler("profile", self.profile_command))
        self.application.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        
        # أوامر المتجر والمهام
        self.application.add_handler(CommandHandler("shop", self.shop_command))
        self.application.add_handler(CommandHandler("inventory", self.inventory_command))
        self.application.add_handler(CommandHandler("daily", self.daily_command))
        self.application.add_handler(CommandHandler("badges", self.badges_command))
        
        # أوامر الكلان
        self.application.add_handler(CommandHandler("clan", self.clan_command))
        self.application.add_handler(CommandHandler("createclan", self.create_clan_command))
        self.application.add_handler(CommandHandler("joinclan", self.join_clan_command))
        self.application.add_handler(CommandHandler("leaveclan", self.leave_clan_command))
        
        # أوامر الإدارة
        self.application.add_handler(CommandHandler("addxp", self.add_xp_command))
        self.application.add_handler(CommandHandler("addcoins", self.add_coins_command))
        self.application.add_handler(CommandHandler("resetuser", self.reset_user_command))
        
        # معالج الرسائل
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_message
        ))
        
        # معالج الأزرار
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        if update.effective_chat.type == 'private':
            welcome_text = """
🎉 مرحباً بك في بوت XP والمستويات!

🎯 الأوامر المتاحة:
📊 /xp - عرض نقاط الخبرة
📈 /level - عرض مستواك الحالي
🎪 /progress - عرض التقدم للمستوى التالي
👤 /profile - ملفك الشخصي الكامل
🏆 /leaderboard - قائمة المتصدرين

🛍️ /shop - المتجر
🎒 /inventory - مخزونك
🎯 /daily - المهام اليومية
🏅 /badges - شاراتك

🏰 /clan - معلومات الكلان
🆕 /createclan - إنشاء كلان جديد
🤝 /joinclan - الانضمام لكلان

💡 تفاعل في الجروبات لكسب XP والعملات!
            """
            await update.message.reply_text(welcome_text)
        else:
            # في الجروب
            await self.ensure_user_exists(update.effective_user, update.effective_chat.id)
            await update.message.reply_text(
                f"مرحباً {update.effective_user.first_name}! 🎉\n"
                "ابدأ بالتفاعل لكسب XP والعملات! 💰"
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        help_text = """
📖 دليل استخدام البوت:

📊 الإحصائيات:
• /xp - عرض نقاط الخبرة الحالية
• /level - المستوى الحالي والرتبة
• /progress - التقدم نحو المستوى التالي
• /profile - الملف الشخصي الكامل
• /leaderboard - قائمة أفضل 10 أعضاء

🛍️ المتجر والمهام:
• /shop - تصفح المتجر
• /inventory - عرض مخزونك
• /daily - المهام اليومية
• /badges - شاراتك المكتسبة

🏰 الكلانات:
• /clan - معلومات كلانك
• /createclan <اسم> - إنشاء كلان جديد
• /joinclan <اسم> - الانضمام لكلان
• /leaveclan - مغادرة الكلان

⚙️ أوامر الإدارة (للمشرفين فقط):
• /addxp @user <رقم> - إضافة XP
• /addcoins @user <رقم> - إضافة عملات
• /resetuser @user - إعادة تعيين المستخدم

💡 نصائح:
- تفاعل بانتظام لكسب XP والعملات
- اشتر عناصر من المتجر لتحسين تقدمك
- انضم لكلان للمنافسة الجماعية
        """
        await update.message.reply_text(help_text)
    
    async def xp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض نقاط الخبرة"""
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ هذا الأمر متاح في الجروبات فقط!")
            return
            
        user_group = await self.get_user_group(update.effective_user.id, update.effective_chat.id)
        if not user_group:
            await update.message.reply_text("❌ لم يتم العثور على بياناتك!")
            return
        
        level = await self.db.get_level_by_id(user_group.level_id)
        next_level = await self.db.get_level_by_number(level.level_number + 1)
        
        xp_text = f"📊 إحصائيات {update.effective_user.first_name}:\n\n"
        xp_text += f"⚡ XP: {format_number(user_group.xp)}\n"
        xp_text += f"🏆 المستوى: {level.level_number}\n"
        xp_text += f"{level.level_emoji} الرتبة: {level.level_name}\n"
        
        if next_level:
            needed_xp = next_level.required_xp - user_group.xp
            xp_text += f"📈 للمستوى التالي: {format_number(needed_xp)} XP\n"
        
        xp_text += f"💰 العملات: {format_number(user_group.coins)}\n"
        xp_text += f"📝 الرسائل: {format_number(user_group.total_messages)}"
        
        await update.message.reply_text(xp_text)
    
    async def level_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المستوى الحالي"""
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ هذا الأمر متاح في الجروبات فقط!")
            return
            
        user_group = await self.get_user_group(update.effective_user.id, update.effective_chat.id)
        if not user_group:
            await update.message.reply_text("❌ لم يتم العثور على بياناتك!")
            return
        
        level = await self.db.get_level_by_id(user_group.level_id)
        
        level_text = f"🏆 مستوى {update.effective_user.first_name}:\n\n"
        level_text += f"{level.level_emoji} {level.level_name}\n"
        level_text += f"🔢 المستوى: {level.level_number} من 55\n"
        level_text += f"🏷️ الفئة: {level.category}\n"
        level_text += f"⭐ الدرجة: {level.tier}\n"
        level_text += f"⚡ XP المطلوب: {format_number(level.required_xp)}\n"
        level_text += f"⚡ XP الحالي: {format_number(user_group.xp)}"
        
        await update.message.reply_text(level_text)
    
    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض التقدم للمستوى التالي"""
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ هذا الأمر متاح في الجروبات فقط!")
            return
            
        user_group = await self.get_user_group(update.effective_user.id, update.effective_chat.id)
        if not user_group:
            await update.message.reply_text("❌ لم يتم العثور على بياناتك!")
            return
        
        current_level = await self.db.get_level_by_id(user_group.level_id)
        next_level = await self.db.get_level_by_number(current_level.level_number + 1)
        
        if not next_level:
            await update.message.reply_text("🎉 تهانينا! لقد وصلت للمستوى الأقصى!")
            return
        
        current_xp = user_group.xp - current_level.required_xp
        needed_xp = next_level.required_xp - current_level.required_xp
        progress_percent = (current_xp / needed_xp) * 100
        
        progress_bar = get_progress_bar(progress_percent)
        remaining_xp = next_level.required_xp - user_group.xp
        
        progress_text = f"📈 تقدم {update.effective_user.first_name}:\n\n"
        progress_text += f"🔸 المستوى الحالي: {current_level.level_emoji} {current_level.level_name}\n"
        progress_text += f"🔹 المستوى التالي: {next_level.level_emoji} {next_level.level_name}\n\n"
        progress_text += f"{progress_bar}\n"
        progress_text += f"📊 التقدم: {progress_percent:.1f}%\n"
        progress_text += f"⚡ XP المطلوب: {format_number(remaining_xp)}\n"
        progress_text += f"📅 الرسائل المتبقية: ~{remaining_xp // 10}"
        
        await update.message.reply_text(progress_text)
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الملف الشخصي الكامل"""
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ هذا الأمر متاح في الجروبات فقط!")
            return
        
        user_group = await self.get_user_group(update.effective_user.id, update.effective_chat.id)
        if not user_group:
            await update.message.reply_text("❌ لم يتم العثور على بياناتك!")
            return
        
        level = await self.db.get_level_by_id(user_group.level_id)
        badges_count = await self.db.get_user_badges_count(
            update.effective_user.id, update.effective_chat.id
        )
        
        # معلومات الكلان
        clan_info = ""
        if user_group.clan_id:
            clan = await self.db.get_clan_by_id(user_group.clan_id)
            if clan:
                clan_info = f"🏰 الكلان: {clan.name}\n"
        
        # تاريخ الانضمام
        join_date = user_group.joined_at.strftime("%Y-%m-%d") if user_group.joined_at else "غير معروف"
        
        profile_text = f"👤 الملف الشخصي: {update.effective_user.first_name}\n"
        profile_text += f"{'='*30}\n\n"
        profile_text += f"{level.level_emoji} {level.level_name}\n"
        profile_text += f"🏆 المستوى: {level.level_number}/55\n"
        profile_text += f"⚡ XP: {format_number(user_group.xp)}\n"
        profile_text += f"💰 العملات: {format_number(user_group.coins)}\n"
        profile_text += f"📝 الرسائل: {format_number(user_group.total_messages)}\n"
        profile_text += f"🏅 الشارات: {badges_count}\n"
        profile_text += clan_info
        profile_text += f"📅 انضم في: {join_date}"
        
        # إضافة أزرار للتفاعل
        keyboard = [
            [InlineKeyboardButton("📊 التفاصيل", callback_data="profile_details")],
            [InlineKeyboardButton("🏅 الشارات", callback_data="view_badges")],
            [InlineKeyboardButton("🛍️ المتجر", callback_data="open_shop")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(profile_text, reply_markup=reply_markup)
    
    async def shop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المتجر"""
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ هذا الأمر متاح في الجروبات فقط!")
            return
        
        shop_items = await self.db.get_shop_items()
        if not shop_items:
            await update.message.reply_text("❌ المتجر فارغ حالياً!")
            return
        
        user_group = await self.get_user_group(update.effective_user.id, update.effective_chat.id)
        
        shop_text = f"🛍️ المتجر - عملاتك: {format_number(user_group.coins)}\n"
        shop_text += f"{'='*30}\n\n"
        
        keyboard = []
        for item in shop_items[:10]:  # أول 10 عناصر
            emoji_map = {
                'booster': '⚡',
                'upgrade': '🎯',
                'badge': '🏅',
                'vip': '👑',
                'protection': '🛡️'
            }
            
            emoji = emoji_map.get(item.item_type, '📦')
            shop_text += f"{emoji} {item.name}\n"
            shop_text += f"💰 السعر: {format_number(item.price)}\n"
            shop_text += f"📝 {item.description}\n\n"
            
            # إضافة زر للشراء
            keyboard.append([InlineKeyboardButton(
                f"{emoji} {item.name} - {format_number(item.price)} 💰",
                callback_data=f"buy_item_{item.id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(shop_text, reply_markup=reply_markup)
    
    async def daily_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المهام اليومية"""
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ هذا الأمر متاح في الجروبات فقط!")
            return
        
        # إنشاء المهام اليومية إذا لم تكن موجودة
        await self.create_daily_quests(update.effective_user.id, update.effective_chat.id)
        
        quests = await self.db.get_daily_quests(
            update.effective_user.id, update.effective_chat.id, date.today()
        )
        
        if not quests:
            await update.message.reply_text("❌ لا توجد مهام اليوم!")
            return
        
        daily_text = f"🎯 المهام اليومية - {date.today().strftime('%Y-%m-%d')}\n"
        daily_text += f"{'='*30}\n\n"
        
        for quest in quests:
            status_emoji = "✅" if quest.is_completed else "⏳"
            progress_percent = (quest.current_progress / quest.target_value) * 100 if quest.target_value > 0 else 0
            
            daily_text += f"{status_emoji} {self.get_quest_name(quest.quest_type)}\n"
            daily_text += f"📊 التقدم: {quest.current_progress}/{quest.target_value} ({progress_percent:.0f}%)\n"
            daily_text += f"🎁 المكافأة: {quest.reward_xp} XP + {quest.reward_coins} 💰\n\n"
        
        completed_quests = sum(1 for q in quests if q.is_completed)
        daily_text += f"📈 مكتمل: {completed_quests}/{len(quests)}"
        
        await update.message.reply_text(daily_text)
    
    async def clan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض معلومات الكلان"""
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ هذا الأمر متاح في الجروبات فقط!")
            return
        
        user_group = await self.get_user_group(update.effective_user.id, update.effective_chat.id)
        
        if not user_group or not user_group.clan_id:
            await update.message.reply_text(
                "🏰 لست عضواً في أي كلان!\n"
                "استخدم /createclan <اسم> لإنشاء كلان جديد\n"
                "أو /joinclan <اسم> للانضمام لكلان موجود"
            )
            return
        
        clan = await self.db.get_clan_by_id(user_group.clan_id)
        if not clan:
            await update.message.reply_text("❌ خطأ في العثور على الكلان!")
            return
        
        # معلومات قائد الكلان
        leader = await self.db.get_user_by_id(clan.leader_user_id)
        leader_name = leader.first_name if leader else "غير معروف"
        
        clan_text = f"🏰 كلان: {clan.name}\n"
        clan_text += f"{'='*30}\n\n"
        clan_text += f"👑 القائد: {leader_name}\n"
        clan_text += f"👥 الأعضاء: {clan.member_count}/{clan.max_members}\n"
        clan_text += f"⚡ XP الجماعي: {format_number(clan.total_xp)}\n"
        clan_text += f"📅 تأسس في: {clan.created_at.strftime('%Y-%m-%d') if clan.created_at else 'غير معروف'}\n"
        
        if clan.description:
            clan_text += f"📝 الوصف: {clan.description}\n"
        
        # أزرار الإدارة
        keyboard = []
        if clan.leader_user_id == update.effective_user.id:
            keyboard.append([InlineKeyboardButton("⚙️ إدارة الكلان", callback_data="manage_clan")])
        
        keyboard.append([InlineKeyboardButton("👥 عرض الأعضاء", callback_data="clan_members")])
        keyboard.append([InlineKeyboardButton("📊 إحصائيات الكلان", callback_data="clan_stats")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(clan_text, reply_markup=reply_markup)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل الأساسي"""
        if update.effective_chat.type == 'private':
            return  # تجاهل الرسائل الخاصة
        
        # التأكد من وجود المستخدم
        await self.ensure_user_exists(update.effective_user, update.effective_chat.id)
        
        # التحقق من cooldown
        user_group = await self.get_user_group(update.effective_user.id, update.effective_chat.id)
        if user_group and user_group.last_xp_gain:
            time_diff = datetime.now() - user_group.last_xp_gain
            if time_diff.total_seconds() < self.XP_COOLDOWN:
                return  # المستخدم ما زال في فترة الانتظار
        
        # حساب XP والعملات
        xp_gained = calculate_xp_gain(self.MIN_XP_PER_MESSAGE, self.MAX_XP_PER_MESSAGE)
        coins_gained = calculate_coin_gain(self.MIN_COINS_PER_MESSAGE, self.MAX_COINS_PER_MESSAGE)
        
        # تطبيق المضاعفات (إذا كانت موجودة)
        # TODO: تطبيق تأثيرات العناصر المشتراة
        
        # تحديث البيانات
        await self.db.update_user_stats(
            update.effective_user.id,
            update.effective_chat.id,
            xp_gained,
            coins_gained
        )
        
        # تسجيل الرسالة
        await self.db.log_message(
            update.effective_user.id,
            update.effective_chat.id,
            update.message.message_id,
            xp_gained,
            coins_gained,
            'text'
        )
        
        # التحقق من ترقية المستوى
        new_user_group = await self.get_user_group(update.effective_user.id, update.effective_chat.id)
        level_up_result = await check_level_up(self.db, new_user_group)
        
        if level_up_result:
            new_level = level_up_result
            await update.message.reply_text(
                f"🎉 تهانينا {update.effective_user.first_name}!\n"
                f"ارتقيت إلى المستوى {new_level.level_number}!\n"
                f"{new_level.level_emoji} {new_level.level_name}\n"
                f"⚡ XP المطلوب للمستوى التالي: {format_number(new_level.required_xp)}"
            )
        
        # التحقق من الشارات الجديدة
        await self.check_new_badges(update.effective_user.id, update.effective_chat.id)
        
        # تحديث المهام اليومية
        await self.update_daily_quests(update.effective_user.id, update.effective_chat.id, 'messages', 1)
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار التفاعلية"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("buy_item_"):
            item_id = int(data.split("_")[2])
            await self.process_purchase(query, item_id)
        elif data == "profile_details":
            await self.show_profile_details(query)
        elif data == "view_badges":
            await self.show_user_badges(query)
        elif data == "open_shop":
            await self.show_shop_inline(query)
        # يمكن إضافة المزيد من المعالجات هنا
    
    async def ensure_user_exists(self, user, group_id: int):
        """التأكد من وجود المستخدم في قاعدة البيانات"""
        # إضافة المستخدم إذا لم يكن موجوداً
        await self.db.add_user_if_not_exists(user)
        
        # إضافة الجروب إذا لم يكن موجوداً
        await self.db.add_group_if_not_exists(group_id, "Unknown Group")
        
        # ربط المستخدم بالجروب
        await self.db.add_user_to_group_if_not_exists(user.id, group_id)
    
    async def get_user_group(self, user_id: int, group_id: int) -> Optional[UserGroup]:
        """الحصول على بيانات المستخدم في الجروب"""
        return await self.db.get_user_group(user_id, group_id)
    
    async def create_daily_quests(self, user_id: int, group_id: int):
        """إنشاء المهام اليومية للمستخدم"""
        today = date.today()
        
        # التحقق من وجود مهام لليوم
        existing_quests = await self.db.get_daily_quests(user_id, group_id, today)
        if existing_quests:
            return  # المهام موجودة بالفعل
        
        # إنشاء مهام عشوائية
        quest_templates = [
            {"type": "messages", "target": 50, "xp": 100, "coins": 50},
            {"type": "xp_gain", "target": 100, "xp": 150, "coins": 75},
            {"type": "coins_gain", "target": 50, "xp": 75, "coins": 100},
        ]
        
        for template in quest_templates:
            await self.db.create_daily_quest(
                user_id, group_id, template["type"], 
                template["target"], template["xp"], template["coins"], today
            )
    
    async def update_daily_quests(self, user_id: int, group_id: int, quest_type: str, progress: int):
        """تحديث تقدم المهام اليومية"""
        await self.db.update_daily_quest_progress(user_id, group_id, quest_type, progress, date.today())
    
    async def check_new_badges(self, user_id: int, group_id: int):
        """التحقق من الشارات الجديدة"""
        user_group = await self.get_user_group(user_id, group_id)
        if not user_group:
            return
        
        # الحصول على جميع الشارات المتاحة
        all_badges = await self.db.get_all_badges()
        
        # الحصول على الشارات الحالية للمستخدم
        user_badges = await self.db.get_user_badges(user_id, group_id)
        user_badge_ids = [badge.id for badge in user_badges]
        
        # التحقق من كل شارة
        for badge in all_badges:
            if badge.id in user_badge_ids:
                continue  # المستخدم يملك هذه الشارة بالفعل
            
            # التحقق من الشروط
            if await self.check_badge_requirement(badge, user_group):
                await self.db.award_badge(user_id, group_id, badge.id)
                # إشعار المستخدم (يمكن إضافة هذا لاحقاً)
    
    async def check_badge_requirement(self, badge: Badge, user_group: UserGroup) -> bool:
        """التحقق من شروط الشارة"""
        if badge.requirement_type == "messages":
            return user_group.total_messages >= badge.requirement_value
        elif badge.requirement_type == "xp":
            return user_group.xp >= badge.requirement_value
        elif badge.requirement_type == "coins":
            return user_group.coins >= badge.requirement_value
        elif badge.requirement_type == "level":
            level = await self.db.get_level_by_id(user_group.level_id)
            return level.level_number >= badge.requirement_value
        
        return False
    
    def get_quest_name(self, quest_type: str) -> str:
        """الحصول على اسم المهمة"""
        quest_names = {
            "messages": "إرسال رسائل",
            "xp_gain": "كسب XP",
            "coins_gain": "جمع عملات",
            "shop_purchase": "شراء من المتجر"
        }
        return quest_names.get(quest_type, quest_type)
    
    async def process_purchase(self, query, item_id: int):
        """معالجة عملية الشراء"""
        # TODO: تطبيق منطق الشراء
        await query.edit_message_text("🛠️ ميزة الشراء قيد التطوير...")
    
    async def show_profile_details(self, query):
        """عرض تفاصيل الملف الشخصي"""
        # TODO: تطبيق عرض التفاصيل
        await query.edit_message_text("🛠️ ميزة التفاصيل قيد التطوير...")
    
    async def show_user_badges(self, query):
        """عرض شارات المستخدم"""
        # TODO: تطبيق عرض الشارات
        await query.edit_message_text("🛠️ ميزة الشارات قيد التطوير...")
    
    async def show_shop_inline(self, query):
        """عرض المتجر التفاعلي"""
        # TODO: تطبيق المتجر التفاعلي
        await query.edit_message_text("🛠️ المتجر التفاعلي قيد التطوير...")
    
    # أوامر الإدارة
    async def add_xp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة XP (للمشرفين فقط)"""
        if not await self.is_admin(update.effective_user.id, update.effective_chat.id):
            await update.message.reply_text("❌ هذا الأمر للمشرفين فقط!")
            return
        
        # TODO: تطبيق إضافة XP
        await update.message.reply_text("🛠️ أمر إضافة XP قيد التطوير...")
    
    async def add_coins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة عملات (للمشرفين فقط)"""
        if not await self.is_admin(update.effective_user.id, update.effective_chat.id):
            await update.message.reply_text("❌ هذا الأمر للمشرفين فقط!")
            return
        
        # TODO: تطبيق إضافة عملات
        await update.message.reply_text("🛠️ أمر إضافة العملات قيد التطوير...")
    
    async def reset_user_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إعادة تعيين مستخدم (للمشرفين فقط)"""
        if not await self.is_admin(update.effective_user.id, update.effective_chat.id):
            await update.message.reply_text("❌ هذا الأمر للمشرفين فقط!")
            return
        
        # TODO: تطبيق إعادة التعيين
        await update.message.reply_text("🛠️ أمر إعادة التعيين قيد التطوير...")
    
    async def is_admin(self, user_id: int, group_id: int) -> bool:
        """التحقق من صلاحيات المشرف"""
        try:
            chat_member = await self.application.bot.get_chat_member(group_id, user_id)
            return chat_member.status in ['administrator', 'creator']
        except:
            return False
    
    # أوامر الكلان
    async def create_clan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إنشاء كلان جديد"""
        # TODO: تطبيق إنشاء الكلان
        await update.message.reply_text("🛠️ إنشاء الكلان قيد التطوير...")
    
    async def join_clan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الانضمام لكلان"""
        # TODO: تطبيق الانضمام للكلان
        await update.message.reply_text("🛠️ الانضمام للكلان قيد التطوير...")
    
    async def leave_clan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مغادرة الكلان"""
        # TODO: تطبيق مغادرة الكلان
        await update.message.reply_text("🛠️ مغادرة الكلان قيد التطوير...")
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة المتصدرين"""
        # TODO: تطبيق قائمة المتصدرين
        await update.message.reply_text("🛠️ قائمة المتصدرين قيد التطوير...")
    
    async def inventory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المخزون"""
        # TODO: تطبيق عرض المخزون
        await update.message.reply_text("🛠️ المخزون قيد التطوير...")
    
    async def badges_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الشارات"""
        # TODO: تطبيق عرض الشارات
        await update.message.reply_text("🛠️ الشارات قيد التطوير...")
    
    def run(self):
        """تشغيل البوت"""
        print("🤖 بدء تشغيل البوت مع Supabase...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

# نقطة البداية
if __name__ == "__main__":
    # توكن البوت
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("❌ خطأ: لم يتم العثور على توكن البوت!")
        print("يرجى تعيين متغير البيئة BOT_TOKEN")
        exit(1)
    
    # إنشاء وتشغيل البوت
    bot = TelegramBot(BOT_TOKEN)
    bot.run()
