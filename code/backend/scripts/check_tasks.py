"""检查数据库中的任务数据"""
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.task import Task
from app.models.goal import Goal
from app.models.plan import Plan

db = SessionLocal()

# 检查任务
tasks = db.query(Task).all()
print(f'=== 任务总数: {len(tasks)} ===')
for t in tasks[:10]:
    print(f'ID: {t.id}, 标题: {t.title}, 截止日期: {t.due_date}, 完成: {t.completed}')

# 检查今日任务
from datetime import date
today = date.today()
today_tasks = db.query(Task).join(Goal).filter(Task.due_date == today).all()
print(f'\n=== 今日任务: {len(today_tasks)} ===')
for t in today_tasks:
    print(f'ID: {t.id}, 标题: {t.title}, 完成: {t.completed}')

# 检查规划
plans = db.query(Plan).all()
print(f'\n=== 规划总数: {len(plans)} ===')
for p in plans:
    content = p.content[:100] if p.content else 'None'
    print(f'ID: {p.id}, 目标ID: {p.goal_id}, 内容前缀: {content}')

db.close()
