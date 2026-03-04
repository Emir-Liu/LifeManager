
import os
os.environ["TESTING"] = "true"
from app.core.database import Base, engine
from app.models import (
    User, Goal, Plan, Task, 
    Conversation, Message, Action, 
    Event, TimePreference
)

print("创建所有表...")
Base.metadata.create_all(bind=engine)
print("✅ 测试数据库初始化完成")
    