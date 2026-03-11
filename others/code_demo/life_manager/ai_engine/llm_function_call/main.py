#!/usr/bin/env python3
"""
LLM日历助手 - 交互式命令行工具
支持通过自然语言管理Google Calendar日程
"""

import sys
import os
import calendar  # 先导入标准库calendar，避免命名冲突

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from calendar_engine.core.factory import CalendarProviderFactory
from ai_engine.llm_function_call.agent.calendar_agent import create_calendar_agent


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
    print("LLM日历助手")
    print("支持通过自然语言管理Google Calendar日程")
    print("=" * 60)
    
    # 设置日历提供者
    setup_providers()
    
    # 创建日历Agent
    print("\n正在初始化日历助手...")
    agent = create_calendar_agent()
    print("日历助手初始化完成!")
    
    # 交互式对话
    print("\n使用说明:")
    print("- 输入自然语言描述,如: '帮我查询今天有什么安排'")
    print("- 输入 'quit' 或 'exit' 退出程序")
    print("- 输入 'help' 查看帮助信息")
    print()
    
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
            
            # 调用Agent - 新版 API 使用 messages 格式
            print("\n助手: ", end="", flush=True)

            # 新版 API 使用 messages 格式
            try:
                result = agent.invoke({
                    "messages": [{"role": "user", "content": user_input}]
                })

                # 提取响应
                if hasattr(result, 'messages') and result.messages:
                    # 返回的是消息列表，取最后一个消息
                    last_message = result.messages[-1]
                    print(getattr(last_message, 'content', str(last_message)))
                elif isinstance(result, dict) and 'output' in result:
                    print(result['output'])
                else:
                    print(result)
            except Exception as e:
                # 如果新版格式失败，尝试旧版格式
                try:
                    result = agent.invoke({"input": user_input})
                    if 'output' in result:
                        print(result['output'])
                    else:
                        print(result)
                except Exception as e2:
                    print(f"错误: {e2}")
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
