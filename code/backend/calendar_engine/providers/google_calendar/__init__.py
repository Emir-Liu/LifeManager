from calendar_engine.providers.google_calendar.provider import GoogleCalendarProvider
from calendar_engine.core.factory import CalendarProviderFactory

# 注册Google Calendar提供者
CalendarProviderFactory.register('google', GoogleCalendarProvider)

__all__ = ['GoogleCalendarProvider']
