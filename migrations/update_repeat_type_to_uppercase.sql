-- 修改 task_plans 表中的 repeat_type 值为大写
UPDATE task_plans SET repeat_type = 'NONE' WHERE repeat_type = 'none';
UPDATE task_plans SET repeat_type = 'DAILY' WHERE repeat_type = 'daily';
UPDATE task_plans SET repeat_type = 'WEEKLY' WHERE repeat_type = 'weekly';
UPDATE task_plans SET repeat_type = 'MONTHLY' WHERE repeat_type = 'monthly';

-- 修改 tasks 表中的 repeat_type 值为大写（如果需要）
UPDATE tasks SET repeat_type = 'NONE' WHERE repeat_type = 'none';
UPDATE tasks SET repeat_type = 'DAILY' WHERE repeat_type = 'daily';
UPDATE tasks SET repeat_type = 'WEEKLY' WHERE repeat_type = 'weekly';
UPDATE tasks SET repeat_type = 'MONTHLY' WHERE repeat_type = 'monthly'; 