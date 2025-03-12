-- 创建数据库（如果不存在）
CREATE DATABASE
IF NOT EXISTS user_management CHARACTER
SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE user_management;

-- 创建用户表
CREATE TABLE
IF NOT EXISTS users
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR
(50) UNIQUE NOT NULL,
    email VARCHAR
(100) UNIQUE NOT NULL,
    hashed_password VARCHAR
(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    coins BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON
UPDATE CURRENT_TIMESTAMP
);

-- 创建任务表
CREATE TABLE
IF NOT EXISTS tasks
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR
(100) NOT NULL,
    description VARCHAR
(500),
    user_id INT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    repeat_type ENUM
('NONE', 'DAILY', 'WEEKLY', 'MONTHLY') DEFAULT 'NONE',
    coins_reward BIGINT NOT NULL DEFAULT 0,
    due_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON
UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY
(user_id) REFERENCES users
(id) ON
DELETE CASCADE
);

-- 创建任务完成记录表
CREATE TABLE
IF NOT EXISTS task_completions
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    user_id INT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY
(task_id) REFERENCES tasks
(id) ON
DELETE CASCADE,
    FOREIGN KEY (user_id)
REFERENCES users
(id) ON
DELETE CASCADE
);

-- 创建任务计划表
CREATE TABLE IF NOT EXISTS task_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    user_id INT NOT NULL,
    repeat_type ENUM('NONE', 'DAILY', 'WEEKLY', 'MONTHLY') DEFAULT 'NONE',
    coins_reward BIGINT NOT NULL DEFAULT 0,
    status ENUM('ACTIVE', 'PAUSED', 'COMPLETED') DEFAULT 'ACTIVE',
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NULL,
    last_generated TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 修改任务表，添加任务计划关联
ALTER TABLE tasks ADD COLUMN task_plan_id INT NULL;
ALTER TABLE tasks ADD CONSTRAINT fk_task_plan FOREIGN KEY (task_plan_id) REFERENCES task_plans(id) ON DELETE SET NULL;

-- 插入测试用户数据
-- 注意：这里的密码哈希值是示例，实际应用中应该使用正确的哈希算法生成
INSERT INTO users
    (username, email, hashed_password, is_active, coins)
VALUES
    ('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE, 100000),
    ('user1', 'user1@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE, 10000),
    ('user2', 'user2@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE, 5000),
    ('inactive_user', 'inactive@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', FALSE, 0),
    ('test_user', 'test@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE, 2500);
    ('test_user6', 'test@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE, 2500);

-- 插入测试任务数据
-- 使用当前日期和未来日期
SET @tomorrow = DATE_ADD(CURRENT_DATE
(), INTERVAL 1 DAY);
SET @next_week = DATE_ADD(CURRENT_DATE
(), INTERVAL 7 DAY);

INSERT INTO tasks
    (title, description, user_id, repeat_type, coins_reward, due_date)
VALUES
    ('一次性任务', '这是一个不重复的任务', 1, 'NONE', 1000, @tomorrow),
    ('每日任务', '这是一个每天重复的任务', 1, 'DAILY', 500, NULL),
    ('每周任务', '这是一个每周重复的任务', 1, 'WEEKLY', 2000, @next_week),
    ('每月任务', '这是一个每月重复的任务', 1, 'MONTHLY', 5000, NULL),
    ('用户2的任务', '这是用户2的任务', 2, 'NONE', 1500, @tomorrow);

-- 插入一些任务完成记录
INSERT INTO task_completions
    (task_id, user_id)
VALUES
    (2, 1),
    -- admin 完成了每日任务
    (2, 1),
    -- admin 再次完成了每日任务（不同日期）
    (3, 1),
    -- admin 完成了每周任务
    (5, 2);
-- user1 完成了他的任务

-- 更新用户的 coins 余额（基于已完成的任务）
UPDATE users SET coins = coins + 500 WHERE id = 1;
-- admin 完成每日任务获得 500 coins
UPDATE users SET coins = coins + 500 WHERE id = 1;
-- admin 再次完成每日任务获得 500 coins
UPDATE users SET coins = coins + 2000 WHERE id = 1;
-- admin 完成每周任务获得 2000 coins
UPDATE users SET coins = coins + 1500 WHERE id = 2;
-- user1 完成任务获得 1500 coins

-- 显示创建的数据
SELECT 'Users:' AS '';
SELECT *
FROM users;

SELECT 'Tasks:' AS '';
SELECT *
FROM tasks;

SELECT 'Task Completions:' AS '';
SELECT *
FROM task_completions;

-- 创建故事表
CREATE TABLE IF NOT EXISTS stories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    story_type ENUM('ADVENTURE', 'MYSTERY', 'ROMANCE', 'SCIFI', 'FANTASY', 'HORROR') DEFAULT 'ADVENTURE',
    unlock_cost BIGINT NOT NULL DEFAULT 5000,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
);

-- 创建故事章节表
CREATE TABLE IF NOT EXISTS story_chapters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    story_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    order_num INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE
);

-- 创建故事选择表
CREATE TABLE IF NOT EXISTS story_choices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT NOT NULL,
    text VARCHAR(500) NOT NULL,
    next_chapter_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES story_chapters(id) ON DELETE CASCADE,
    FOREIGN KEY (next_chapter_id) REFERENCES story_chapters(id) ON DELETE SET NULL
);

-- 创建用户故事表（记录用户解锁的故事）
CREATE TABLE IF NOT EXISTS user_stories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    story_id INT NOT NULL,
    current_chapter_id INT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
    FOREIGN KEY (current_chapter_id) REFERENCES story_chapters(id) ON DELETE SET NULL,
    UNIQUE KEY (user_id, story_id)
);

-- 创建用户故事响应表（记录用户在故事中的选择）
CREATE TABLE IF NOT EXISTS user_story_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_story_id INT NOT NULL,
    chapter_id INT NOT NULL,
    choice_id INT NULL,
    custom_response TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_story_id) REFERENCES user_stories(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES story_chapters(id) ON DELETE CASCADE,
    FOREIGN KEY (choice_id) REFERENCES story_choices(id) ON DELETE SET NULL
);

INSERT INTO user_management.stories (id, title, description, story_type, unlock_cost, is_active, created_at, updated_at) VALUES (1, '冒险之旅', '一个充满奇幻冒险的故事，你将扮演一位勇敢的探险家，探索未知的世界。', 'ADVENTURE', 50, 1, '2025-03-12 15:02:46', null);
INSERT INTO user_management.stories (id, title, description, story_type, unlock_cost, is_active, created_at, updated_at) VALUES (2, '神秘岛屿', '探索一个神秘的岛屿，揭开它的秘密。岛上有许多奇怪的现象和生物，等待你去发现。', 'MYSTERY', 100, 1, '2025-03-12 15:02:46', null);
INSERT INTO user_management.stories (id, title, description, story_type, unlock_cost, is_active, created_at, updated_at) VALUES (3, '城市传说', '都市中流传的神秘故事，真相往往比传说更加离奇。你将调查一系列超自然现象。', 'ROMANCE', 75, 1, '2025-03-12 15:02:46', null);
INSERT INTO user_management.stories (id, title, description, story_type, unlock_cost, is_active, created_at, updated_at) VALUES (4, '星际旅行', '在未来的宇宙中航行，探索外星文明和新的星球。你的选择将决定人类的命运。', 'SCIFI', 120, 1, '2025-03-12 15:02:46', null);
INSERT INTO user_management.stories (id, title, description, story_type, unlock_cost, is_active, created_at, updated_at) VALUES (5, '古代遗迹', '探索古代文明留下的遗迹，解开历史之谜。小心陷阱和诅咒！', 'ADVENTURE', 80, 1, '2025-03-12 15:02:46', null);


INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (1, 1, '出发', '你站在一个小村庄的边缘，准备开始你的冒险之旅。你的背包里有一些基本的补给和一把小刀。前方有两条路：一条通向茂密的森林，另一条通向开阔的草原。', 1, '2025-03-12 15:02:46', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (2, 1, '森林之路', '你选择了森林之路。树木高大，阳光几乎无法穿透茂密的树冠。你听到远处有水流的声音，同时也注意到一些奇怪的足迹。', 2, '2025-03-12 15:02:46', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (3, 1, '草原之路', '你选择了草原之路。开阔的视野让你能看到远处的山脉。草原上有一些野生动物，还有一个看起来像是营地的地方。', 3, '2025-03-12 15:02:46', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (4, 1, '神秘洞穴', '你跟随足迹来到一个神秘的洞穴入口。洞穴黑暗而潮湿，但似乎有微弱的光从深处传来。', 4, '2025-03-12 15:02:46', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (5, 1, '山顶', '经过艰难的攀爬，你到达了山顶。从这里可以俯瞰整个地区，你看到远处有一座古老的城堡。', 5, '2025-03-12 15:02:46', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (6, 2, '海难', '你在一场突如其来的风暴中幸存下来，被冲到一个神秘的岛屿上。你的船只已经损毁，只有少量物资幸存。岛上看起来郁郁葱葱，但异常安静。', 1, '2025-03-12 15:02:52', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (7, 2, '海滩', '你决定沿着海滩走，希望找到其他幸存者或者救援信号。你发现一些奇怪的足迹和一个半掩在沙中的箱子。', 2, '2025-03-12 15:02:52', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (8, 2, '丛林', '你进入岛屿的丛林。植被非常茂密，有些植物你从未见过。你听到远处有奇怪的声音。', 3, '2025-03-12 15:02:52', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (9, 2, '古老神庙', '你发现了一座古老的神庙，掩埋在丛林之中。神庙的墙壁上刻满了奇怪的符号和图案。', 4, '2025-03-12 15:02:52', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (10, 2, '地下通道', '神庙内有一个通往地下的通道。通道黑暗而潮湿，但你决定探索它。', 5, '2025-03-12 15:02:52', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (11, 3, '神秘电话', '你收到一个陌生号码的电话，对方声称知道关于城市中一系列怪异事件的真相。你决定调查这个电话的来源。', 1, '2025-03-12 15:02:52', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (12, 3, '废弃医院', '线索指向一家废弃的医院。据说这里曾经发生过一些不为人知的实验。', 2, '2025-03-12 15:02:52', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (13, 3, '地下室', '你在医院找到了通往地下室的入口。地下室黑暗而潮湿，墙上涂满了奇怪的符号。', 3, '2025-03-12 15:02:52', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (14, 3, '秘密档案', '你发现了一些秘密档案，记录了医院进行的实验。这些实验似乎与超自然现象有关。', 4, '2025-03-12 15:02:52', null);
INSERT INTO user_management.story_chapters (id, story_id, title, content, order_num, created_at, updated_at) VALUES (15, 3, '最终真相', '你终于了解到了城市传说背后的真相，但这个真相比传说本身更加可怕。', 5, '2025-03-12 15:02:52', null);

INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (1, 1, '选择森林之路', 2, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (2, 1, '选择草原之路', 3, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (3, 2, '跟随足迹', 4, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (4, 2, '寻找水源', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (5, 3, '前往营地', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (6, 3, '爬上山峰', 5, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (7, 6, '沿着海滩走', 7, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (8, 6, '进入丛林', 8, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (9, 7, '检查箱子', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (10, 7, '继续沿海滩走', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (11, 8, '调查声音来源', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (12, 8, '寻找神庙', 9, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (13, 9, '研究墙上的符号', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (14, 9, '探索地下通道', 10, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (15, 11, '追踪电话号码', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (16, 11, '前往废弃医院', 12, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (17, 12, '探索医院主楼', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (18, 12, '寻找地下室入口', 13, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (19, 13, '调查墙上的符号', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (20, 13, '寻找秘密档案', 14, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (21, 14, '销毁档案', null, '2025-03-12 15:02:59');
INSERT INTO user_management.story_choices (id, chapter_id, text, next_chapter_id, created_at) VALUES (22, 14, '继续调查真相', 15, '2025-03-12 15:02:59');


