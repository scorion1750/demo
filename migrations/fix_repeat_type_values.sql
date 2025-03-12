-- 修复 tasks 表中的 repeat_type 值
UPDATE tasks SET repeat_type = 'none' WHERE repeat_type = 'NONE';
UPDATE tasks SET repeat_type = 'daily' WHERE repeat_type = 'DAILY';
UPDATE tasks SET repeat_type = 'weekly' WHERE repeat_type = 'WEEKLY';
UPDATE tasks SET repeat_type = 'monthly' WHERE repeat_type = 'MONTHLY';

-- 修复 task_plans 表中的 repeat_type 值
UPDATE task_plans SET repeat_type = 'none' WHERE repeat_type = 'NONE';
UPDATE task_plans SET repeat_type = 'daily' WHERE repeat_type = 'DAILY';
UPDATE task_plans SET repeat_type = 'weekly' WHERE repeat_type = 'WEEKLY';
UPDATE task_plans SET repeat_type = 'monthly' WHERE repeat_type = 'MONTHLY'; 