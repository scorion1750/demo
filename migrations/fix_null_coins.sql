-- 修复 users 表中的 NULL coins 值
UPDATE users SET coins = 0 WHERE coins IS NULL;

-- 修复 tasks 表中的 NULL coins_reward 值
UPDATE tasks SET coins_reward = 0 WHERE coins_reward IS NULL;

-- 确保这些列不允许 NULL 值
ALTER TABLE users MODIFY COLUMN coins BIGINT NOT NULL DEFAULT 0;
ALTER TABLE tasks MODIFY COLUMN coins_reward BIGINT NOT NULL DEFAULT 0; 