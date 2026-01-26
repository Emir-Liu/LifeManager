# LifeManager 数据库设计文档

## 概述

本文档描述了 LifeManager 应用的数据库设计，包括表结构、关系、索引等详细信息。

## 技术栈

- **数据库**: PostgreSQL 15+ (生产环境) / SQLite (开发环境)
- **ORM**: SQLAlchemy
- **迁移工具**: Alembic

## 数据库命名规范

- 表名: 小写，复数，如 `users`, `goals`
- 字段名: 小写，蛇形命名，如 `created_at`, `user_id`
- 主键: 统一使用 `id`
- 时间字段: 使用 `datetime` 或 `timestamp` 类型，时区为 UTC
- 外键: `{table}_id` 格式

## 表结构设计

### 1. users (用户表)

存储用户基本信息和认证信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 用户ID |
| phone | VARCHAR(20) | UNIQUE, NOT NULL | 手机号 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希值 |
| nickname | VARCHAR(100) | NULLABLE | 用户昵称 |
| avatar_url | VARCHAR(500) | NULLABLE | 头像URL |
| fcm_token | VARCHAR(255) | NULLABLE | Firebase推送Token |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| last_login_at | TIMESTAMP | NULLABLE | 最后登录时间 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NULLABLE | 更新时间 |

**索引**:
- `idx_users_phone` (phone)
- `idx_users_created_at` (created_at)

**关系**:
- 一对多 `goals`
- 一对多 `settings`

---

### 2. goals (目标表)

存储用户的目标信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 目标ID |
| user_id | BIGINT | FK(users.id), NOT NULL | 用户ID |
| title | VARCHAR(200) | NOT NULL | 目标标题 |
| description | TEXT | NULLABLE | 目标描述 |
| target_date | DATE | NULLABLE | 目标完成日期 |
| priority | SMALLINT | DEFAULT 1 | 优先级: 0=低, 1=中, 2=高 |
| status | VARCHAR(20) | DEFAULT 'planning' | 状态: planning, ongoing, completed, paused |
| progress | INT | DEFAULT 0 | 进度百分比(0-100) |
| total_tasks | INT | DEFAULT 0 | 总任务数 |
| completed_tasks | INT | DEFAULT 0 | 已完成任务数 |
| estimated_hours | INT | NULLABLE | 预计总工时 |
| spent_hours | INT | DEFAULT 0 | 已用工时 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NULLABLE | 更新时间 |

**索引**:
- `idx_goals_user_id` (user_id)
- `idx_goals_status` (status)
- `idx_goals_target_date` (target_date)
- `idx_goals_created_at` (created_at)

**关系**:
- 多对一 `users`
- 一对多 `plans`
- 一对多 `tasks`

---

### 3. plans (规划表)

存储目标的执行规划信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 规划ID |
| goal_id | BIGINT | FK(goals.id), NOT NULL | 目标ID |
| title | VARCHAR(200) | NOT NULL | 规划标题 |
| description | TEXT | NULLABLE | 规划描述 |
| estimated_hours | INT | NULLABLE | 预计总工时 |
| ai_generated | BOOLEAN | DEFAULT TRUE | 是否AI生成 |
| status | VARCHAR(20) | DEFAULT 'draft' | 状态: draft, confirmed, abandoned |
 stages_json | JSONB | NULLABLE | 阶段信息(JSON格式) |
| user_preference | TEXT | NULLABLE | 用户偏好备注 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NULLABLE | 更新时间 |

**索引**:
- `idx_plans_goal_id` (goal_id)
- `idx_plans_status` (status)

**关系**:
- 多对一 `goals`
- 一对多 `plan_stages`

---

### 4. plan_stages (规划阶段表)

存储规划的各个阶段信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 阶段ID |
| plan_id | BIGINT | FK(plans.id), NOT NULL | 规划ID |
| stage_order | INT | NOT NULL | 阶段顺序 |
| title | VARCHAR(200) | NOT NULL | 阶段标题 |
| description | TEXT | NULLABLE | 阶段描述 |
| estimated_hours | INT | NULLABLE | 预计工时 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**索引**:
- `idx_plan_stages_plan_id` (plan_id)
- `idx_plan_stages_order` (plan_id, stage_order)

**关系**:
- 多对一 `plans`

---

### 5. tasks (任务表)

存储具体的任务信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 任务ID |
| goal_id | BIGINT | FK(goals.id), NOT NULL | 目标ID |
| plan_id | BIGINT | FK(plans.id), NULLABLE | 规划ID |
| plan_stage_id | BIGINT | FK(plan_stages.id), NULLABLE | 规划阶段ID |
| title | VARCHAR(200) | NOT NULL | 任务标题 |
| description | TEXT | NULLABLE | 任务描述 |
| scheduled_date | DATE | NOT NULL | 计划日期 |
| scheduled_time | TIME | NULLABLE | 计划时间 |
| duration_minutes | INT | NULLABLE | 预计时长(分钟) |
| actual_duration_minutes | INT | NULLABLE | 实际时长(分钟) |
| priority | SMALLINT | DEFAULT 1 | 优先级: 0=低, 1=中, 2=高 |
| status | VARCHAR(20) | DEFAULT 'pending' | 状态: pending, in_progress, completed, skipped |
| completed_at | TIMESTAMP | NULLABLE | 完成时间 |
| notes | TEXT | NULLABLE | 完成备注 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NULLABLE | 更新时间 |

**索引**:
- `idx_tasks_goal_id` (goal_id)
- `idx_tasks_plan_id` (plan_id)
- `idx_tasks_scheduled_date` (scheduled_date)
- `idx_tasks_status` (status)
- `idx_tasks_goal_status` (goal_id, status)
- 复合索引 `idx_tasks_user_date`: (goal_id->user_id, scheduled_date, status)

**关系**:
- 多对一 `goals`
- 多对一 `plans`
- 多对一 `plan_stages`
- 一对多 `reminders`
- 一对多 `task_completions`

---

### 6. reminders (提醒表)

存储任务提醒信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 提醒ID |
| user_id | BIGINT | FK(users.id), NOT NULL | 用户ID |
| task_id | BIGINT | FK(tasks.id), NOT NULL | 任务ID |
| remind_type | VARCHAR(20) | DEFAULT 'before' | 提醒类型: before=提前, at=准时, after=延后 |
| remind_minutes | INT | NULLABLE | 提前/延后分钟数 |
| remind_time | TIMESTAMP | NOT NULL | 提醒时间 |
| message | TEXT | NULLABLE | 提醒消息 |
| status | VARCHAR(20) | DEFAULT 'pending' | 状态: pending, sent, failed, cancelled |
| sent_at | TIMESTAMP | NULLABLE | 发送时间 |
| error_message | TEXT | NULLABLE | 错误信息 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**索引**:
- `idx_reminders_user_id` (user_id)
- `idx_reminders_task_id` (task_id)
- `idx_reminders_remind_time` (remind_time)
- `idx_reminders_status` (status)

**关系**:
- 多对一 `users`
- 多对一 `tasks`

---

### 7. task_completions (任务完成记录表)

存储任务完成的历史记录，用于统计分析。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 记录ID |
| task_id | BIGINT | FK(tasks.id), NOT NULL | 任务ID |
| goal_id | BIGINT | FK(goals.id), NOT NULL | 目标ID |
| user_id | BIGINT | FK(users.id), NOT NULL | 用户ID |
| completed_at | TIMESTAMP | NOT NULL | 完成时间 |
| scheduled_date | DATE | NOT NULL | 计划日期 |
| scheduled_time | TIME | NULLABLE | 计划时间 |
| actual_duration_minutes | INT | NULLABLE | 实际时长 |
| estimated_duration_minutes | INT | NULLABLE | 预计时长 |
| notes | TEXT | NULLABLE | 备注 |
| mood | SMALLINT | NULLABLE | 完成时心情: 1-5 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 记录创建时间 |

**索引**:
- `idx_task_completions_task_id` (task_id)
- `idx_task_completions_user_id` (user_id)
- `idx_task_completions_completed_at` (completed_at)
- `idx_task_completions_goal_id` (goal_id)

**关系**:
- 多对一 `tasks`
- 多对一 `goals`
- 多对一 `users`

---

### 8. user_settings (用户设置表)

存储用户的各种偏好设置。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 设置ID |
| user_id | BIGINT | FK(users.id), UNIQUE, NOT NULL | 用户ID |
| remind_before_minutes | INT | DEFAULT 5 | 提前提醒分钟数 |
| push_enabled | BOOLEAN | DEFAULT TRUE | 推送通知开关 |
| vibration_enabled | BOOLEAN | DEFAULT TRUE | 震动开关 |
| sound_enabled | BOOLEAN | DEFAULT TRUE | 提示音开关 |
| first_day_of_week | INT | DEFAULT 1 | 每周第一天: 0=周日, 1=周一 |
| default_calendar_view | VARCHAR(20) | DEFAULT 'week' | 默认日历视图: day, week, month |
| quiet_hours_start | TIME | DEFAULT '22:00' | 免打扰开始时间 |
| quiet_hours_end | TIME | DEFAULT '08:00' | 免打扰结束时间 |
| daily_hours | INT | DEFAULT 2 | 每日默认工时 |
| weekend_hours | INT | DEFAULT 4 | 周末默认工时 |
| timezone | VARCHAR(50) | DEFAULT 'Asia/Shanghai' | 时区 |
| theme | VARCHAR(20) | DEFAULT 'light' | 主题: light, dark, auto |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NULLABLE | 更新时间 |

**索引**:
- `idx_user_settings_user_id` (user_id, UNIQUE)

**关系**:
- 多对一 `users`

---

### 9. feedbacks (用户反馈表)

存储用户反馈信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 反馈ID |
| user_id | BIGINT | FK(users.id), NOT NULL | 用户ID |
| type | VARCHAR(20) | NOT NULL | 反馈类型: bug, feature, other |
| title | VARCHAR(200) | NOT NULL | 反馈标题 |
| content | TEXT | NOT NULL | 反馈内容 |
| screenshot_url | VARCHAR(500) | NULLABLE | 截图URL |
| status | VARCHAR(20) | DEFAULT 'pending' | 处理状态: pending, processing, resolved, closed |
| admin_reply | TEXT | NULLABLE | 管理员回复 |
| replied_at | TIMESTAMP | NULLABLE | 回复时间 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**索引**:
- `idx_feedbacks_user_id` (user_id)
- `idx_feedbacks_status` (status)
- `idx_feedbacks_type` (type)

**关系**:
- 多对一 `users`

---

### 10. statistics_cache (统计缓存表)

缓存常用的统计数据，避免频繁计算。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 缓存ID |
| user_id | BIGINT | FK(users.id), NOT NULL | 用户ID |
| cache_key | VARCHAR(100) | NOT NULL | 缓存键 |
| cache_value | JSONB | NOT NULL | 缓存值(JSON) |
| period | VARCHAR(20) | NOT NULL | 统计周期: daily, weekly, monthly |
| cache_date | DATE | NOT NULL | 缓存日期 |
| expires_at | TIMESTAMP | NOT NULL | 过期时间 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**索引**:
- `idx_statistics_cache_user_key` (user_id, cache_key)
- `idx_statistics_cache_expires` (expires_at)

**关系**:
- 多对一 `users`

---

## ER 图

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   users     │1     N│   goals     │1     N│    plans    │
└─────────────┘───────└─────────────┘───────└─────────────┘
     │1 N                   │1 N                   │1 N
     │                      │                      │
     └──────────────N ┌─────┘    N─────────────N └─────┐
                      │                             │
                N ────┴────1                  N ─────┴───1
         ┌─────────────┐              ┌─────────────┐
         │   tasks     │              │ plan_stages │
         └─────────────┘              └─────────────┘
              │1 N
              │
         N ───┴──1
   ┌──────────────────┐
   │   reminders      │
   └──────────────────┘

┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  user_      │1     1│   users     │1     N│  feedbacks  │
│  settings   │       └─────────────┘       └─────────────┘
└─────────────┘              │
                             │1 N
                       N ────┴──1
                ┌─────────────┐
                │task_        │
                │completions  │
                └─────────────┘

┌─────────────┐       ┌─────────────┐
│   users     │1     N│statistics_  │
└─────────────┘       │  cache      │
                      └─────────────┘
```

---

## 数据库视图

### v_task_summary (任务汇总视图)

```sql
CREATE VIEW v_task_summary AS
SELECT
    g.id as goal_id,
    g.title as goal_title,
    g.user_id,
    COUNT(t.id) as total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
    SUM(CASE WHEN t.status = 'pending' THEN 1 ELSE 0 END) as pending_tasks,
    SUM(CASE WHEN t.status = 'skipped' THEN 1 ELSE 0 END) as skipped_tasks,
    SUM(t.actual_duration_minutes) / 60 as total_spent_hours
FROM goals g
LEFT JOIN tasks t ON g.id = t.goal_id
GROUP BY g.id;
```

### v_daily_stats (每日统计视图)

```sql
CREATE VIEW v_daily_stats AS
SELECT
    tc.user_id,
    tc.scheduled_date,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN tc.actual_duration_minutes IS NOT NULL THEN 1 ELSE 0 END) as completed_tasks,
    SUM(tc.actual_duration_minutes) / 60 as total_hours,
    SUM(tc.estimated_duration_minutes - tc.actual_duration_minutes) / 60 as time_diff_hours
FROM task_completions tc
GROUP BY tc.user_id, tc.scheduled_date;
```

---

## 存储过程

### update_goal_progress (更新目标进度)

```sql
CREATE OR REPLACE FUNCTION update_goal_progress(p_goal_id BIGINT)
RETURNS INTEGER AS $$
DECLARE
    v_progress INTEGER;
BEGIN
    SELECT
        CASE
            WHEN total_tasks = 0 THEN 0
            ELSE ROUND((completed_tasks::FLOAT / total_tasks) * 100)
        END
    INTO v_progress
    FROM (
        SELECT
            COUNT(*) as total_tasks,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
        FROM tasks
        WHERE goal_id = p_goal_id
    ) t;

    UPDATE goals
    SET progress = v_progress,
        completed_tasks = (
            SELECT COUNT(*) FROM tasks WHERE goal_id = p_goal_id AND status = 'completed'
        ),
        spent_hours = (
            COALESCE(SUM(actual_duration_minutes), 0) / 60.0
        ),
        updated_at = NOW()
    WHERE id = p_goal_id;

    RETURN v_progress;
END;
$$ LANGUAGE plpgsql;
```

### update_spent_hours (更新实际工时)

```sql
CREATE OR REPLACE FUNCTION update_spent_hours(p_task_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE tasks
    SET spent_hours = (
        COALESCE(actual_duration_minutes, 0) / 60.0
    )
    WHERE id = p_task_id;

    PERFORM update_goal_progress(
        (SELECT goal_id FROM tasks WHERE id = p_task_id)
    );
END;
$$ LANGUAGE plpgsql;
```

---

## 触发器

### trg_update_goal_progress (任务状态更新时自动更新目标进度)

```sql
CREATE OR REPLACE FUNCTION trg_update_goal_progress_func()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status != OLD.status OR NEW.actual_duration_minutes IS DISTINCT FROM OLD.actual_duration_minutes THEN
        PERFORM update_goal_progress(NEW.goal_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_goal_progress
AFTER UPDATE OR INSERT ON tasks
FOR EACH ROW
EXECUTE FUNCTION trg_update_goal_progress_func();
```

### trg_update_timestamps (自动更新 updated_at)

```sql
CREATE OR REPLACE FUNCTION trg_update_timestamps_func()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为需要的表创建触发器
CREATE TRIGGER trg_users_update_timestamps
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION trg_update_timestamps_func();

CREATE TRIGGER trg_goals_update_timestamps
BEFORE UPDATE ON goals
FOR EACH ROW
EXECUTE FUNCTION trg_update_timestamps_func();

CREATE TRIGGER trg_tasks_update_timestamps
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION trg_update_timestamps_func();
```

---

## 初始化数据

### 插入默认设置

```sql
-- 为已存在的用户创建默认设置
INSERT INTO user_settings (user_id, remind_before_minutes, push_enabled)
SELECT id, 5, TRUE
FROM users
WHERE id NOT IN (SELECT user_id FROM user_settings);
```

### 创建测试数据

```sql
-- 测试用户
INSERT INTO users (phone, password_hash, nickname) VALUES
('13800000001', '$2b$12$hash...', '测试用户1'),
('13800000002', '$2b$12$hash...', '测试用户2');

-- 测试目标
INSERT INTO goals (user_id, title, description, target_date, priority, status) VALUES
(1, '学习Python', '在3个月内掌握Python编程', '2026-04-23', 2, 'ongoing'),
(1, '坚持跑步', '每周跑步3次，每次5公里', '2026-06-30', 1, 'ongoing');

-- 测试任务
INSERT INTO tasks (goal_id, title, scheduled_date, scheduled_time, duration_minutes, status) VALUES
(1, '完成第一章练习', '2026-01-26', '19:00:00', 60, 'pending'),
(1, '完成第二章练习', '2026-01-27', '19:00:00', 60, 'pending'),
(2, '周一跑步', '2026-01-27', '06:30:00', 30, 'pending');
```

---

## 性能优化建议

### 1. 索引优化

- 为经常查询的字段创建索引
- 使用复合索引优化多条件查询
- 定期分析索引使用情况

### 2. 查询优化

- 避免使用 `SELECT *`
- 使用 `LIMIT` 分页查询
- 合理使用 `JOIN` 和子查询
- 对于大数据量表使用分区

### 3. 数据库配置

```ini
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

### 4. 定期维护

```sql
-- 定期分析表
ANALYZE goals;
ANALYZE tasks;

-- 定期清理过期数据
DELETE FROM reminders WHERE status = 'sent' AND sent_at < NOW() - INTERVAL '30 days';

-- 定期清理缓存
DELETE FROM statistics_cache WHERE expires_at < NOW();
```

---

## 备份和恢复

### 备份

```bash
# 全量备份
pg_dump -U postgres -d lifemanager > backup_$(date +%Y%m%d).sql

# 只备份结构
pg_dump -U postgres -d lifemanager --schema-only > backup_schema.sql

# 只备份数据
pg_dump -U postgres -d lifemanager --data-only > backup_data.sql
```

### 恢复

```bash
# 恢复备份
psql -U postgres -d lifemanager < backup_20260123.sql
```

---

## 数据库迁移

### 使用 Alembic

```bash
# 创建迁移
alembic revision --autogenerate -m "Add new column to tasks"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## 安全建议

1. **最小权限原则**: 应用数据库用户只授予必要的权限
2. **加密敏感数据**: 密码等敏感信息必须加密存储
3. **使用参数化查询**: 防止SQL注入
4. **定期备份**: 设置自动备份策略
5. **访问控制**: 使用防火墙限制数据库访问
6. **审计日志**: 记录重要操作日志

---

## 附录

### 状态码定义

#### 目标状态 (goal.status)
- `planning`: 规划中
- `ongoing`: 进行中
- `completed`: 已完成
- `paused`: 已暂停

#### 任务状态 (task.status)
- `pending`: 待开始
- `in_progress`: 进行中
- `completed`: 已完成
- `skipped`: 已跳过

#### 提醒状态 (reminder.status)
- `pending`: 待发送
- `sent`: 已发送
- `failed`: 发送失败
- `cancelled`: 已取消

#### 优先级 (priority)
- `0`: 低
- `1`: 中
- `2`: 高

#### 反馈类型 (feedback.type)
- `bug`: 问题反馈
- `feature`: 功能建议
- `other`: 其他

#### 反馈状态 (feedback.status)
- `pending`: 待处理
- `processing`: 处理中
- `resolved`: 已解决
- `closed`: 已关闭
