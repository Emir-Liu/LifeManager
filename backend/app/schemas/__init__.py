"""
Schemas
"""
from .user import UserCreate, UserLogin, UserResponse, Token
from .goal import GoalCreate, GoalUpdate, GoalResponse, GoalDetailResponse
from .plan import PlanGenerateRequest, PlanCreate, PlanUpdate, PlanResponse, PlanDetailResponse
from .task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

__all__ = [
    "UserRegister", "UserLogin", "UserResponse", "Token",
    "GoalCreate", "GoalUpdate", "GoalResponse", "GoalDetailResponse",
    "PlanGenerateRequest", "PlanCreate", "PlanUpdate", "PlanResponse", "PlanDetailResponse",
    "TaskCreate", "TaskUpdate", "TaskResponse", "TaskListResponse"
]
