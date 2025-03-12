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
    story_type ENUM('adventure', 'mystery', 'romance', 'scifi', 'fantasy', 'horror') DEFAULT 'adventure',
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

-- 插入示例故事数据
INSERT INTO stories (title, description, story_type, unlock_cost, is_active) VALUES
('神秘森林冒险', '探索一片神秘的森林，发现隐藏的秘密和宝藏。', 'adventure', 3000, TRUE),
('古堡谜案', '解开古老城堡中的谜团，找出真相。', 'mystery', 5000, TRUE),
('星际旅程', '踏上星际旅行，探索未知的星球和文明。', 'scifi', 8000, TRUE);

-- 插入示例章节数据（仅为第一个故事）
INSERT INTO story_chapters (story_id, title, content, order_num) VALUES
(1, '进入森林', '你站在一片神秘森林的边缘。茂密的树木在你面前延伸，阳光透过树叶形成斑驳的光影。你听到远处传来鸟鸣和流水的声音。你决定...', 1),
(1, '小径探索', '你沿着一条蜿蜒的小径前进。四周的植被越来越茂密，空气中弥漫着泥土和植物的芬芳。突然，你看到前方的路分叉了。', 2),
(1, '神秘湖泊', '你来到一个平静的湖泊边。湖水清澈见底，倒映着蓝天和周围的树木。湖中央有一个小岛，岛上似乎有什么在闪闪发光。', 3),
(1, '古老遗迹', '你发现了一处古老的石头建筑，被藤蔓和苔藓覆盖。入口处刻着奇怪的符号，似乎是某种远古文明的遗迹。', 4),
(1, '宝藏发现', '经过一番探索，你终于找到了传说中的森林宝藏！这是一个装满古老金币和宝石的箱子，旁边还有一本记载着森林历史的古书。', 5);

-- 插入示例选择数据
INSERT INTO story_choices (chapter_id, text, next_chapter_id) VALUES
(1, '沿着明显的小径前进', 2),
(1, '向森林深处探索', 4),
(2, '选择左边的路', 3),
(2, '选择右边的路', 4),
(3, '尝试游到小岛', 5),
(3, '继续沿着湖边行走', 4),
(4, '进入遗迹探索', 5),
(4, '返回森林寻找其他路径', 2);

-- 修改 story_chapters 表中的 order 列名为 order_num
ALTER TABLE story_chapters CHANGE COLUMN `order` order_num INT DEFAULT 0;