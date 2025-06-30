
-- قاعدة البيانات الأساسية لبوت تيليجرام
-- إنشاء قاعدة البيانات وتعيين الترميز
CREATE DATABASE telegram_bot;
USE telegram_bot;

-- جدول الجروبات
CREATE TABLE groups (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- جدول المستخدمين الأساسي
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'ar',
    is_bot BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- جدول المستويات
CREATE TABLE levels (
    id INT PRIMARY KEY AUTO_INCREMENT,
    level_number INT NOT NULL UNIQUE,
    level_name VARCHAR(100) NOT NULL,
    level_emoji VARCHAR(10) NOT NULL,
    required_xp BIGINT NOT NULL,
    category ENUM('Basic', 'Junior', 'Medium', 'Senior', 'Expert', 'Master', 'Grand Master', 'Legend', 'Mythic', 'Supreme', 'Owner') NOT NULL,
    tier INT NOT NULL CHECK (tier BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level_number (level_number),
    INDEX idx_required_xp (required_xp)
);

-- جدول ربط المستخدمين بالجروبات (البيانات الأساسية)
CREATE TABLE user_groups (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    xp BIGINT DEFAULT 0,
    level_id INT DEFAULT 1,
    coins BIGINT DEFAULT 0,
    total_messages BIGINT DEFAULT 0,
    last_message_at TIMESTAMP NULL,
    last_xp_gain TIMESTAMP NULL,
    clan_id BIGINT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (level_id) REFERENCES levels(id),
    UNIQUE KEY unique_user_group (user_id, group_id),
    INDEX idx_user_xp (user_id, xp),
    INDEX idx_group_level (group_id, level_id),
    INDEX idx_clan (clan_id)
);

-- جدول عناصر المتجر
CREATE TABLE shop_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price BIGINT NOT NULL,
    item_type ENUM('booster', 'upgrade', 'badge', 'vip', 'protection') NOT NULL,
    effect_type VARCHAR(100) NOT NULL,
    effect_value DECIMAL(10,2) NOT NULL,
    duration_hours INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type_price (item_type, price)
);

-- جدول مخزون المستخدمين
CREATE TABLE user_inventory (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    item_id INT NOT NULL,
    quantity INT DEFAULT 1,
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES shop_items(id),
    INDEX idx_user_group_item (user_id, group_id, item_id),
    INDEX idx_expires (expires_at)
);

-- جدول الشارات
CREATE TABLE badges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    emoji VARCHAR(10) NOT NULL,
    category VARCHAR(100) NOT NULL,
    requirement_type VARCHAR(100) NOT NULL,
    requirement_value BIGINT NOT NULL,
    rarity ENUM('common', 'rare', 'epic', 'legendary') DEFAULT 'common',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول شارات المستخدمين
CREATE TABLE user_badges (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    badge_id INT NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(id),
    UNIQUE KEY unique_user_group_badge (user_id, group_id, badge_id),
    INDEX idx_user_group (user_id, group_id)
);

-- جدول المهام اليومية
CREATE TABLE daily_quests (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    quest_type VARCHAR(100) NOT NULL,
    target_value BIGINT NOT NULL,
    current_progress BIGINT DEFAULT 0,
    reward_xp BIGINT NOT NULL,
    reward_coins BIGINT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    quest_date DATE NOT NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_group_quest_date (user_id, group_id, quest_type, quest_date),
    INDEX idx_user_group_date (user_id, group_id, quest_date)
);

-- جدول الكلانات
CREATE TABLE clans (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    leader_user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    total_xp BIGINT DEFAULT 0,
    member_count INT DEFAULT 1,
    max_members INT DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (leader_user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    UNIQUE KEY unique_clan_name_group (name, group_id),
    INDEX idx_group_xp (group_id, total_xp)
);

-- جدول أنشطة الكلان
CREATE TABLE clan_activities (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    clan_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    activity_type ENUM('join', 'leave', 'promotion', 'xp_gain', 'achievement') NOT NULL,
    description TEXT,
    xp_amount BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clan_id) REFERENCES clans(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_clan_date (clan_id, created_at)
);

-- جدول سجل الرسائل
CREATE TABLE message_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    xp_gained BIGINT DEFAULT 0,
    coins_gained BIGINT DEFAULT 0,
    message_type ENUM('text', 'photo', 'video', 'document', 'sticker', 'voice', 'other') DEFAULT 'text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    INDEX idx_user_group_date (user_id, group_id, created_at),
    INDEX idx_group_date (group_id, created_at)
);

-- جدول الإجراءات الإدارية
CREATE TABLE admin_actions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    admin_user_id BIGINT NOT NULL,
    target_user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    action_type ENUM('add_xp', 'remove_xp', 'add_coins', 'remove_coins', 'reset_user', 'ban', 'unban') NOT NULL,
    amount BIGINT DEFAULT 0,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_user_id) REFERENCES users(id),
    FOREIGN KEY (target_user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    INDEX idx_group_date (group_id, created_at),
    INDEX idx_admin_date (admin_user_id, created_at)
);

-- جدول إحصائيات البوت
CREATE TABLE bot_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    stat_date DATE NOT NULL UNIQUE,
    total_users BIGINT DEFAULT 0,
    total_groups BIGINT DEFAULT 0,
    total_messages BIGINT DEFAULT 0,
    total_xp_gained BIGINT DEFAULT 0,
    total_coins_gained BIGINT DEFAULT 0,
    active_users BIGINT DEFAULT 0,
    new_users BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (stat_date)
);

-- إدراج المستويات الأساسية (55 مستوى)
INSERT INTO levels (level_number, level_name, level_emoji, required_xp, category, tier) VALUES
-- Basic (1-5)
(1, 'Basic I', '🌱', 0, 'Basic', 1),
(2, 'Basic II', '🌿', 100, 'Basic', 2),
(3, 'Basic III', '🍃', 250, 'Basic', 3),
(4, 'Basic IV', '🌾', 500, 'Basic', 4),
(5, 'Basic V', '🌳', 1000, 'Basic', 5),

-- Junior (6-10)
(6, 'Junior I', '🔵', 1750, 'Junior', 1),
(7, 'Junior II', '🟦', 2750, 'Junior', 2),
(8, 'Junior III', '💙', 4000, 'Junior', 3),
(9, 'Junior IV', '🧿', 5500, 'Junior', 4),
(10, 'Junior V', '🔷', 7500, 'Junior', 5),

-- Medium (11-15)
(11, 'Medium I', '🟢', 10000, 'Medium', 1),
(12, 'Medium II', '🟩', 13000, 'Medium', 2),
(13, 'Medium III', '💚', 16500, 'Medium', 3),
(14, 'Medium IV', '🍀', 20500, 'Medium', 4),
(15, 'Medium V', '🔶', 25000, 'Medium', 5),

-- Senior (16-20)
(16, 'Senior I', '🟠', 30000, 'Senior', 1),
(17, 'Senior II', '🟧', 35500, 'Senior', 2),
(18, 'Senior III', '🧡', 41500, 'Senior', 3),
(19, 'Senior IV', '🔸', 48000, 'Senior', 4),
(20, 'Senior V', '🔥', 55000, 'Senior', 5),

-- Expert (21-25)
(21, 'Expert I', '🟣', 63000, 'Expert', 1),
(22, 'Expert II', '🟪', 72000, 'Expert', 2),
(23, 'Expert III', '💜', 82000, 'Expert', 3),
(24, 'Expert IV', '🔮', 93000, 'Expert', 4),
(25, 'Expert V', '⚡', 105000, 'Expert', 5),

-- Master (26-30)
(26, 'Master I', '🔴', 118000, 'Master', 1),
(27, 'Master II', '🟥', 132000, 'Master', 2),
(28, 'Master III', '❤️', 147000, 'Master', 3),
(29, 'Master IV', '💎', 163000, 'Master', 4),
(30, 'Master V', '👑', 180000, 'Master', 5),

-- Grand Master (31-35)
(31, 'Grand Master I', '🌟', 198000, 'Grand Master', 1),
(32, 'Grand Master II', '⭐', 217000, 'Grand Master', 2),
(33, 'Grand Master III', '✨', 237000, 'Grand Master', 3),
(34, 'Grand Master IV', '💫', 258000, 'Grand Master', 4),
(35, 'Grand Master V', '🌠', 280000, 'Grand Master', 5),

-- Legend (36-40)
(36, 'Legend I', '🏆', 303000, 'Legend', 1),
(37, 'Legend II', '🥇', 327000, 'Legend', 2),
(38, 'Legend III', '🏅', 352000, 'Legend', 3),
(39, 'Legend IV', '🎖️', 378000, 'Legend', 4),
(40, 'Legend V', '🏵️', 405000, 'Legend', 5),

-- Mythic (41-45)
(41, 'Mythic I', '🌈', 433000, 'Mythic', 1),
(42, 'Mythic II', '🦄', 462000, 'Mythic', 2),
(43, 'Mythic III', '🐉', 492000, 'Mythic', 3),
(44, 'Mythic IV', '🔱', 523000, 'Mythic', 4),
(45, 'Mythic V', '⚜️', 555000, 'Mythic', 5),

-- Supreme (46-50)
(46, 'Supreme I', '🌌', 588000, 'Supreme', 1),
(47, 'Supreme II', '🌠', 622000, 'Supreme', 2),
(48, 'Supreme III', '✨', 657000, 'Supreme', 3),
(49, 'Supreme IV', '🌟', 693000, 'Supreme', 4),
(50, 'Supreme V', '💫', 730000, 'Supreme', 5),

-- Owner (51-55)
(51, 'Owner I', '👑', 768000, 'Owner', 1),
(52, 'Owner II', '💎', 807000, 'Owner', 2),
(53, 'Owner III', '🔥', 847000, 'Owner', 3),
(54, 'Owner IV', '⚡', 888000, 'Owner', 4),
(55, 'Owner V', '🎯', 930000, 'Owner', 5);

-- إدراج عناصر المتجر الأساسية
INSERT INTO shop_items (name, description, price, item_type, effect_type, effect_value, duration_hours) VALUES
('XP Booster', 'مضاعف XP لمدة ساعة واحدة', 50, 'booster', 'xp_multiplier', 2.0, 1),
('Coin Booster', 'مضاعف العملات لمدة ساعة واحدة', 75, 'booster', 'coin_multiplier', 2.0, 1),
('XP Shield', 'حماية من فقدان XP لمدة 24 ساعة', 100, 'protection', 'xp_protection', 1.0, 24),
('VIP Status', 'حالة VIP لمدة 7 أيام', 500, 'upgrade', 'vip_status', 1.0, 168),
('Mega Booster', 'مضاعف XP و Coins لمدة 30 دقيقة', 150, 'booster', 'mega_multiplier', 3.0, 0.5),
('Legend Badge', 'شارة الأسطورة', 1000, 'badge', 'special_badge', 1.0, 0);

-- إدراج الشارات الأساسية
INSERT INTO badges (name, description, emoji, category, requirement_type, requirement_value, rarity) VALUES
('First Steps', 'أول رسالة في الجروب', '👶', 'milestone', 'messages', 1, 'common'),
('Chatterbox', 'إرسال 100 رسالة', '💬', 'activity', 'messages', 100, 'common'),
('Veteran', 'إرسال 1000 رسالة', '🏅', 'activity', 'messages', 1000, 'rare'),
('Coin Collector', 'جمع 1000 عملة', '💰', 'achievement', 'coins', 1000, 'common'),
('Wealthy', 'جمع 10000 عملة', '💎', 'achievement', 'coins', 10000, 'rare'),
('Level Up', 'الوصول للمستوى 10', '📈', 'progression', 'level', 10, 'common'),
('High Roller', 'الوصول للمستوى 25', '🎯', 'progression', 'level', 25, 'epic'),
('Shopaholic', 'شراء 10 عناصر من المتجر', '🛍️', 'shopping', 'purchases', 10, 'rare'),
('Clan Leader', 'إنشاء كلان', '👑', 'social', 'clan_created', 1, 'epic'),
('Team Player', 'الانضمام لكلان', '🤝', 'social', 'clan_joined', 1, 'common');
