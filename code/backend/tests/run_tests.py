"""
测试运行脚本
提供便捷的测试运行命令
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print('='*60)

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    """主函数"""
    os.chdir(os.path.dirname(os.path.dirname(__file__)))

    if len(sys.argv) < 2:
        print("""
测试运行脚本使用说明:

用法:
  python tests/run_tests.py <command>

可用命令:
  all           - 运行所有测试
  unit          - 运行单元测试
  api           - 运行API集成测试
  integration   - 运行集成测试
  phase2        - 运行Phase 2功能测试
  conversation  - 运行对话测试
  event         - 运行日程测试
  timeline      - 运行时间线测试
  conflict      - 运行冲突检测测试
  schedule      - 运行时间分配测试
  coverage      - 运行测试并生成覆盖率报告
  fast          - 运行快速测试(跳过慢速测试)
  verbose       - 详细模式运行所有测试

示例:
  python tests/run_tests.py all
  python tests/run_tests.py phase2
  python tests/run_tests.py coverage
        """)
        return

    command = sys.argv[1].lower()

    # 基础参数
    base_args = ["pytest", "tests/", "-v"]

    if command == "all":
        success = run_command(
            base_args,
            "所有测试"
        )

    elif command == "unit":
        success = run_command(
            base_args + [
                "tests/test_conflict_service.py",
                "tests/test_schedule_service.py",
                "tests/test_ai_service.py",
                "tests/test_task_unit.py"
            ],
            "单元测试"
        )

    elif command == "api":
        success = run_command(
            base_args + [
                "tests/test_auth.py",
                "tests/test_goals.py",
                "tests/test_plans.py",
                "tests/test_tasks.py",
                "tests/test_conversation_api.py",
                "tests/test_event_api.py",
                "tests/test_time_preference_api.py",
                "tests/test_timeline_api.py"
            ],
            "API集成测试"
        )

    elif command == "integration":
        success = run_command(
            base_args + [
                "tests/test_integration_phase2.py"
            ],
            "集成测试"
        )

    elif command == "phase2":
        success = run_command(
            base_args + [
                "tests/test_conversation_api.py",
                "tests/test_event_api.py",
                "tests/test_time_preference_api.py",
                "tests/test_timeline_api.py",
                "tests/test_conflict_service.py",
                "tests/test_schedule_service.py",
                "tests/test_integration_phase2.py"
            ],
            "Phase 2 功能测试"
        )

    elif command == "conversation":
        success = run_command(
            base_args + ["tests/test_conversation_api.py"],
            "对话测试"
        )

    elif command == "event":
        success = run_command(
            base_args + ["tests/test_event_api.py"],
            "日程测试"
        )

    elif command == "timeline":
        success = run_command(
            base_args + ["tests/test_timeline_api.py"],
            "时间线测试"
        )

    elif command == "conflict":
        success = run_command(
            base_args + ["tests/test_conflict_service.py"],
            "冲突检测测试"
        )

    elif command == "schedule":
        success = run_command(
            base_args + ["tests/test_schedule_service.py"],
            "时间分配测试"
        )

    elif command == "coverage":
        success = run_command(
            base_args + [
                "--cov=app",
                "--cov-report=html",
                "--cov-report=term"
            ],
            "测试并生成覆盖率报告"
        )
        if success:
            print("\n覆盖率报告已生成: htmlcov/index.html")

    elif command == "fast":
        success = run_command(
            base_args + ["-m", "not slow"],
            "快速测试(跳过慢速测试)"
        )

    elif command == "verbose":
        success = run_command(
            base_args + ["-s"],
            "详细模式"
        )

    else:
        print(f"未知命令: {command}")
        print("运行 'python tests/run_tests.py' 查看帮助")
        return

    if success:
        print(f"\n✓ 测试命令执行成功")
    else:
        print(f"\n✗ 测试命令执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
