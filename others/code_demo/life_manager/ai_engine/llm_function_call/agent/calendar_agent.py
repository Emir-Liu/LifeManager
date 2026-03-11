from langchain.agents import create_agent
from calendar_engine.tools.calendar_tools import (
    list_events,
    create_event,
    update_event,
    delete_event,
    get_event,
    list_calendars,
    sync_event,
    list_all_events
)
from ai_engine.config.config import LLMConfig
from ai_engine.utils.llm_operator import LLMOperator

def create_calendar_agent():
    """创建日历助手Agent（新版 API）

    Args:
    
    Returns:
        Agent实例
    """

    # 定义工具列表
    tools = [
        list_events,
        create_event,
        update_event,
        delete_event,
        get_event,
        list_calendars,
        sync_event,
        list_all_events
    ]

    # 使用LLMOperator获取LLM
    llm_config = LLMConfig()
    llm = LLMOperator(llm_config).get_llm()

    # 使用新版 LangChain API (create_agent)
    print("使用新版 LangChain API (create_agent)")
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt="""你是一个日历助手,可以帮助用户管理Google Calendar日程。

你拥有以下工具:
- list_events: 查询特定日历的事件列表
- create_event: 创建新事件
- update_event: 更新已有事件
- delete_event: 删除事件
- get_event: 获取事件详情
- list_calendars: 查询日历列表
- sync_event: 跨日历同步事件
- list_all_events: 聚合查询所有日历的事件

注意事项:
1. 时间格式使用ISO 8601格式,如: 2024-03-11T10:00:00
2. 支持provider参数: google, outlook, apple (目前仅支持google)
3. 在创建/更新事件时,尽量收集完整信息(标题、时间、描述、地点等)
4. 如果用户没有指定具体日期,应该询问用户
5. 响应要友好、简洁,使用中文回答

重要：当用户询问关于日历、日程、会议、安排等问题时，你必须调用相应的工具来获取或操作日历数据。不要只是给出一般性的建议。
"""
    )


def create_calendar_agent_with_config(
    model: str = "gpt-4",
    temperature: float = 0,
    max_iterations: int = 15,
    max_execution_time: float = 300,
    return_intermediate_steps: bool = False
):
    """创建日历助手Agent(带完整配置)

    Args:
        model: 使用的LLM模型
        temperature: 温度参数
        max_iterations: 最大迭代次数
        max_execution_time: 最大执行时间(秒)
        return_intermediate_steps: 是否返回中间步骤

    Returns:
        Agent实例
    """

    # 定义工具列表
    tools = [
        list_events,
        create_event,
        update_event,
        delete_event,
        get_event,
        list_calendars,
        sync_event,
        list_all_events
    ]

    # 使用LLMOperator获取LLM
    llm_config = LLMConfig()
    llm = LLMOperator(llm_config).get_llm()

    # 使用新版 LangChain API (create_agent)
    print("使用新版 LangChain API (create_agent)")
    # 新版 create_agent 不支持 max_iterations 等参数
    # 这些功能需要通过 LangGraph 实现
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt="""你是一个日历助手,可以帮助用户管理Google Calendar日程。

你拥有以下工具:
- list_events: 查询特定日历的事件列表
- create_event: 创建新事件
- update_event: 更新已有事件
- delete_event: 删除事件
- get_event: 获取事件详情
- list_calendars: 查询日历列表
- sync_event: 跨日历同步事件
- list_all_events: 聚合查询所有日历的事件

注意事项:
1. 时间格式使用ISO 8601格式,如: 2024-03-11T10:00:00
2. 支持provider参数: google, outlook, apple (目前仅支持google)
3. 在创建/更新事件时,尽量收集完整信息(标题、时间、描述、地点等)
4. 如果用户没有指定具体日期,应该询问用户
5. 响应要友好、简洁,使用中文回答

重要：当用户询问关于日历、日程、会议、安排等问题时，你必须调用相应的工具来获取或操作日历数据。不要只是给出一般性的建议。
"""
    )
