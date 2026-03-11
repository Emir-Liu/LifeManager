from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Event:
    """统一事件数据模型"""
    id: str
    calendar_id: str
    summary: str
    start_time: str
    end_time: str
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    status: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'calendar_id': self.calendar_id,
            'summary': self.summary,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'description': self.description,
            'location': self.location,
            'attendees': self.attendees,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """从字典创建Event实例"""
        return cls(**data)


@dataclass
class Calendar:
    """统一日历数据模型"""
    id: str
    summary: str
    description: Optional[str] = None
    primary: bool = False
    color_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'summary': self.summary,
            'description': self.description,
            'primary': self.primary,
            'color_id': self.color_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Calendar':
        """从字典创建Calendar实例"""
        return cls(**data)
