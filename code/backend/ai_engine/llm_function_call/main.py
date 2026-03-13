#!/usr/bin/env python3
"""
LLM日历助手 - 交互式命令行工具
支持通过自然语言管理Google Calendar日程
使用 LangGraph 实现
"""

import sys
import os
import calendar  # 先导入标准库calendar，避免命名冲突
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from calendar_engine.core.factory import CalendarProviderFactory
from ai_engine.llm_function_call.graph.calendar_graph import create_calendar_graph
from langchain_core.messages import HumanMessage, AIMessage


def setup_providers():
    """设置日历提供者"""
    # 导入Google Calendar提供者(自动注册)
    import calendar_engine.providers.google_calendar
    
    # 创建Google Calendar提供者
    # 注意: 需要提供正确的凭证文件路径
    credentials_path = os.path.join(
        os.path.dirname(__file__),
        '../../calendar_engine/providers/google_calendar/service/desktop_client_secret_*.json'
    )
    token_path = os.path.join(
        os.path.dirname(__file__),
        '../../calendar_engine/providers/google_calendar/service/token.json'
    )
    
    print(f"使用凭证路径: {credentials_path}")
    print(f"使用token路径: {token_path}")
    
    # 注册默认Google Calendar提供者到工厂
    # 注意: 这里需要实际的凭证文件路径
    print("\n注意: 请确保Google Calendar凭证文件已配置")
    print("凭证文件位置: calendar_engine/providers/google_calendar/service/")


def main():
    """主函数"""
    print("=" * 60)
    print("LLM日历助手 (LangGraph 版本)")
    print("支持通过自然语言管理Google Calendar日程")
    print("=" * 60)

    # 设置日历提供者
    setup_providers()

    # 创建日历 LangGraph
    print("\n正在初始化日历助手...")
    calendar_graph = create_calendar_graph()
    print("日历助手初始化完成!")

    # 使用说明
    print("\n使用说明:")
    print("- 输入自然语言描述,如: '帮我查询今天有什么安排'")
    print("- 输入 'stream' 开启流式输出模式")
    print("- 输入 'graph' 查看图结构")
    print("- 输入 'export' 导出图结构为PNG")
    print("- 输入 'quit' 或 'exit' 退出程序")
    print("- 输入 'help' 查看帮助信息")
    print()

    # 流式输出模式标志
    stream_mode = False

    # 当前会话 ID
    current_thread_id = "default_thread"

    while True:
        try:
            user_input = input("你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见!")
                break
            
            if user_input.lower() in ['help', '帮助']:
                print_help()
                continue

            if user_input.lower() in ['stream', '流式']:
                stream_mode = not stream_mode
                mode_str = "开启" if stream_mode else "关闭"
                print(f"\n流式输出模式已{mode_str}\n")
                continue

            if user_input.lower() in ['graph', '图结构']:
                print("\n" + calendar_graph.get_graph_ascii() + "\n")
                continue

            if user_input.lower() in ['export', '导出']:
                output_path = os.path.join(
                    os.path.dirname(__file__),
                    "calendar_graph.png"
                )
                calendar_graph.get_graph_png(output_path)
                continue

            # 调用日历助手
            print("\n助手: ", end="", flush=True)

            if stream_mode:
                # 流式输出模式
                try:
                    for event in calendar_graph.stream(user_input, stream_mode="messages", thread_id=current_thread_id):
                        for message in event:
                            if isinstance(message, AIMessage):
                                # 检查是否有工具调用
                                if hasattr(message, 'tool_calls') and message.tool_calls:
                                    # 显示工具调用信息
                                    for tool_call in message.tool_calls:
                                        print(f"\n调用工具：{tool_call['name']}")
                                        if tool_call['args']:
                                            # 格式化显示参数
                                            args_str = json.dumps(tool_call['args'], ensure_ascii=False, indent=2)
                                            print(f"参数：{args_str}")
                                # 流式打印内容
                                content = message.content
                                if content:
                                    print(content, end="", flush=True)
                except Exception as e:
                    print(f"\n错误: {e}")
                print()
            else:
                # 普通模式
                try:
                    result = calendar_graph.invoke(user_input, thread_id=current_thread_id)
                    messages = result.get("messages", [])
                    if messages:
                        last_message = messages[-1]
                        if isinstance(last_message, AIMessage):
                            # 检查是否有工具调用
                            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                                # 显示工具调用信息
                                for tool_call in last_message.tool_calls:
                                    print(f"调用工具：{tool_call['name']}")
                                    if tool_call['args']:
                                        args_str = json.dumps(tool_call['args'], ensure_ascii=False, indent=2)
                                        print(f"参数：{args_str}")
                            print(last_message.content)
                        else:
                            print(last_message)
                    else:
                        print(result)
                except Exception as e:
                    print(f"错误: {e}")
            print()
            
        except KeyboardInterrupt:
            print("\n\n再见!")
            break
        except Exception as e:
            print(f"\n错误: {e}\n")
            continue


def print_help():
    """打印帮助信息"""
    help_text = """
可用命令示例:

查询相关:
- "帮我查询今天有什么安排"
- "这周有哪些会议?"
- "查询下周的所有日程"
- "查看明天下午3点到5点的安排"

创建事件:
- "明天上午10点到11点开一个团队会议"
- "创建一个事件: 周五下午2点开会,地点在会议室A"
- "下周二14:00-15:00与客户会面,电话会议"

更新事件:
- "把明天下午3点的会议改到4点"
- "更新今天的会议,地点改到会议室B"
- "把周五的会议标题改为'项目评审会'"

删除事件:
- "删除下周二的健身预约"
- "取消明天下午的会议"

日历管理:
- "查询我有哪些日历"
- "列出所有日历"
- "查看主日历的配置"

跨日历同步:
- "把周五的健身预约同步到Google日历"
- "把今天下午的会议同步到所有日历"

聚合查询:
- "查询所有日历中本周的会议"
- "查看所有日历下个月的安排"
"""
    print(help_text)


if __name__ == "__main__":
    main()
