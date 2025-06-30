
import os
import json
from telegram import Update
from telegram.ext import Application
from supabase_database import SupabaseManager
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعداد البوت
BOT_TOKEN = os.getenv('BOT_TOKEN')
application = Application.builder().token(BOT_TOKEN).build()
db = SupabaseManager()

async def handler(request):
    """معالج webhook لـ Vercel"""
    try:
        if request.method == 'POST':
            # تحويل البيانات إلى Update object
            update_data = await request.json()
            update = Update.de_json(update_data, application.bot)
            
            # معالجة التحديث
            await application.process_update(update)
            
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'success'})
            }
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }
    except Exception as e:
        print(f"خطأ في webhook: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
