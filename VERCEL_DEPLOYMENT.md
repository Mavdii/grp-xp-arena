
# نشر البوت على Vercel مع Supabase

## الخطوات المطلوبة

### 1. رفع الكود إلى GitHub
```bash
git add .
git commit -m "إعداد البوت مع Supabase"
git push origin main
```

### 2. إنشاء قاعدة البيانات في Supabase
- اذهب إلى [Supabase Dashboard](https://app.supabase.com)
- أنشئ الجداول المطلوبة باستخدام SQL Editor:

```sql
-- إنشاء جدول المستخدمين
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'ar',
    is_bot BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- إنشاء جدول الجروبات
CREATE TABLE groups (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- إنشاء جدول ربط المستخدمين بالجروبات
CREATE TABLE user_groups (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    group_id BIGINT REFERENCES groups(id),
    xp INTEGER DEFAULT 0,
    level_id INTEGER DEFAULT 1,
    coins INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    last_message_at TIMESTAMP,
    last_xp_gain TIMESTAMP,
    clan_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, group_id)
);

-- إنشاء جدول المستويات
CREATE TABLE levels (
    id SERIAL PRIMARY KEY,
    level_number INTEGER UNIQUE NOT NULL,
    level_name VARCHAR(255) NOT NULL,
    level_emoji VARCHAR(10) NOT NULL,
    required_xp INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL,
    tier INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- إدراج بيانات المستويات الأساسية
INSERT INTO levels (level_number, level_name, level_emoji, required_xp, category, tier) VALUES
(1, 'مبتدئ', '🌱', 0, 'Basic', 1),
(2, 'متعلم', '📚', 100, 'Basic', 1),
(3, 'نشيط', '⚡', 250, 'Basic', 1),
(4, 'متفاعل', '🎯', 500, 'Basic', 1),
(5, 'خبير مبتدئ', '🏅', 1000, 'Basic', 1);

-- إنشاء باقي الجداول...
CREATE TABLE shop_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price INTEGER DEFAULT 0,
    item_type VARCHAR(50) DEFAULT 'booster',
    effect_type VARCHAR(50) DEFAULT 'xp_multiplier',
    effect_value DECIMAL(5,2) DEFAULT 1.0,
    duration_hours INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    emoji VARCHAR(10) DEFAULT '🏅',
    category VARCHAR(50) DEFAULT 'achievement',
    requirement_type VARCHAR(50) DEFAULT 'messages',
    requirement_value INTEGER DEFAULT 1,
    rarity VARCHAR(20) DEFAULT 'common',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_badges (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    group_id BIGINT REFERENCES groups(id),
    badge_id INTEGER REFERENCES badges(id),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, group_id, badge_id)
);

CREATE TABLE daily_quests (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    group_id BIGINT REFERENCES groups(id),
    quest_type VARCHAR(50) NOT NULL,
    target_value INTEGER NOT NULL,
    current_progress INTEGER DEFAULT 0,
    reward_xp INTEGER DEFAULT 0,
    reward_coins INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    quest_date DATE NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    leader_user_id BIGINT REFERENCES users(id),
    group_id BIGINT REFERENCES groups(id),
    total_xp INTEGER DEFAULT 0,
    member_count INTEGER DEFAULT 1,
    max_members INTEGER DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE message_logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    group_id BIGINT REFERENCES groups(id),
    message_id BIGINT NOT NULL,
    xp_gained INTEGER DEFAULT 0,
    coins_gained INTEGER DEFAULT 0,
    message_type VARCHAR(20) DEFAULT 'text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_inventory (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    group_id BIGINT REFERENCES groups(id),
    item_id INTEGER REFERENCES shop_items(id),
    quantity INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. نشر على Vercel
1. اذهب إلى [Vercel Dashboard](https://vercel.com)
2. اربط المستودع من GitHub
3. أضف متغيرات البيئة التالية:
   - `BOT_TOKEN`: 7788824693:AAHg8E72ySppXpxG2KScfnppibDFJ-ovGTU
   - `SUPABASE_URL`: https://bqvrcecayxaoqkfsukdo.supabase.co
   - `SUPABASE_ANON_KEY`: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   - `DEBUG`: False
   - `LOG_LEVEL`: INFO

### 4. إعداد Webhook
بعد النشر، استخدم رابط Vercel لإعداد webhook:
```bash
curl -X POST "https://api.telegram.org/bot7788824693:AAHg8E72ySppXpxG2KScfnppibDFJ-ovGTU/setWebhook" \
-H "Content-Type: application/json" \
-d '{"url": "https://your-project.vercel.app/api/webhook"}'
```

### 5. التحقق من الإعداد
```bash
curl "https://api.telegram.org/bot7788824693:AAHg8E72ySppXpxG2KScfnppibDFJ-ovGTU/getWebhookInfo"
```

## ملاحظات مهمة
- تأكد من إنشاء جميع الجداول في Supabase
- تأكد من صحة جميع متغيرات البيئة
- راقب logs في Vercel للتأكد من عدم وجود أخطاء
- البوت سيعمل في الجروبات فقط وليس في المحادثات الخاصة

## استكشاف الأخطاء
- تحقق من Vercel Functions logs
- تأكد من صحة Supabase credentials
- تأكد من إعداد webhook بشكل صحيح
- تحقق من أن البوت له صلاحيات في الجروب
