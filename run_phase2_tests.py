"""
Phase 2 测试执行脚本
简化的测试执行工具,用于运行Phase 2测试
"""
import os
import sys
import subprocess

def run_command(cmd, description):
    """执行命令并打印结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )

        print("\n输出:")
        print(result.stdout)

        if result.stderr:
            print("\n错误:")
            print(result.stderr)

        print(f"\n返回码: {result.returncode}")

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("\n❌ 执行超时")
        return False
    except Exception as e:
        print(f"\n❌ 执行异常: {e}")
        return False


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         LifeManager Phase 2 测试执行脚本                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 设置工作目录
    os.chdir("e:/project/LifeManager/backend")

    results = {}

    # 测试1: 检查后端环境
    print("\n[步骤 1/6] 检查后端环境...")
    results["环境检查"] = run_command(
        "python --version",
        "检查Python版本"
    )

    # 测试2: 检查依赖
    print("\n[步骤 2/6] 检查依赖...")
    results["依赖检查"] = run_command(
        "pip list | findstr fastapi pytest",
        "检查关键依赖"
    )

    # 测试3: 初始化测试数据库
    print("\n[步骤 3/6] 初始化测试数据库...")
    results["数据库初始化"] = run_command(
        "python -c \"from app.core.database import Base, engine; Base.metadata.create_all(bind=engine); print('数据库初始化成功')\"",
        "创建测试数据库表"
    )

    # 测试4: 运行Phase 2后端测试
    print("\n[步骤 4/6] 运行Phase 2后端测试...")
    results["后端测试"] = run_command(
        "python -m pytest ../tests/integration/test_phase2_backend.py -v --tb=line",
        "Phase 2后端单元测试"
    )

    # 测试5: 运行集成测试
    print("\n[步骤 5/6] 运行集成测试...")
    results["集成测试"] = run_command(
        "python -m pytest ../tests/integration/test_phase2_integration.py -v --tb=line",
        "Phase 2集成测试"
    )

    # 测试6: 生成测试报告
    print("\n[步骤 6/6] 生成测试报告...")
    print("测试报告位置: ../tests/PHASE2_TEST_REPORT.md")

    # 打印总结
    print("""
╔═══════════════════════════════════════════════════════════╗
║                      测试结果总结                         ║
╚═══════════════════════════════════════════════════════════╝
    """)

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20s} {status}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print("\n⚠️  部分测试失败,请检查日志")
        return 1


if __name__ == "__main__":
    sys.exit(main())
