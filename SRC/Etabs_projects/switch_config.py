#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置切换脚本
用于快速切换不同的结构类型配置
"""

import os
import sys
from pathlib import Path

# 配置类型定义
CONFIG_TYPES = {
    "1": {
        "name": "SHEAR_WALL",
        "description": "剪力墙结构 - 33层联肢剪力墙",
        "features": [
            "剪力墙2×2网格划分",
            "连梁4×4网格划分",
            "楼板4×4膜单元",
            "墙-梁-墙分段布置"
        ]
    },
    "2": {
        "name": "FRAME",
        "description": "框架结构 - 33层钢筋混凝土框架",
        "features": [
            "柱梁线单元建模",
            "主梁、次梁多层次",
            "灵活柱网布置",
            "楼板薄板单元"
        ]
    }
}

CONFIG_FILE_PATH = Path(__file__).parent / "config" / "__init__.py"


def read_current_config():
    """
    读取当前配置类型

    Returns:
        str: 当前配置类型
    """
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找STRUCTURE_TYPE行
        for line in content.split('\n'):
            if line.strip().startswith('STRUCTURE_TYPE ='):
                if 'SHEAR_WALL' in line:
                    return 'SHEAR_WALL'
                elif 'FRAME' in line:
                    return 'FRAME'

        return 'UNKNOWN'

    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return 'ERROR'


def update_config(new_type):
    """
    更新配置类型

    Parameters:
        new_type: 新的配置类型
    """
    try:
        # 读取当前文件内容
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换STRUCTURE_TYPE行
        lines = content.split('\n')
        updated_lines = []

        for line in lines:
            if line.strip().startswith('STRUCTURE_TYPE ='):
                updated_lines.append(f'STRUCTURE_TYPE = "{new_type}"  # 可选: "SHEAR_WALL", "FRAME"')
            else:
                updated_lines.append(line)

        # 写回文件
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))

        print(f"✅ 配置已切换到: {new_type}")

    except Exception as e:
        print(f"❌ 更新配置失败: {e}")


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("  ETABS 结构类型配置切换工具")
    print("  支持剪力墙和框架结构快速切换")
    print("=" * 60)


def print_config_options():
    """打印配置选项"""
    print("\n📋 可用的结构类型配置:")
    print("-" * 50)

    for key, config in CONFIG_TYPES.items():
        print(f"[{key}] {config['description']}")
        for feature in config['features']:
            print(f"    ✓ {feature}")
        print()


def print_current_status():
    """打印当前状态"""
    current = read_current_config()
    print(f"\n🎯 当前配置: {current}")

    if current in [config['name'] for config in CONFIG_TYPES.values()]:
        config_info = next(config for config in CONFIG_TYPES.values() if config['name'] == current)
        print(f"   描述: {config_info['description']}")
    else:
        print("   ⚠️ 未识别的配置类型或配置文件有误")


def validate_environment():
    """验证环境"""
    issues = []

    # 检查配置文件是否存在
    if not CONFIG_FILE_PATH.exists():
        issues.append(f"配置文件不存在: {CONFIG_FILE_PATH}")

    # 检查配置目录结构
    config_dir = CONFIG_FILE_PATH.parent
    required_files = [
        "config_shear_wall.py",
        "config_frame.py"
    ]

    for file in required_files:
        file_path = config_dir / file
        if not file_path.exists():
            issues.append(f"配置文件不存在: {file}")

    if issues:
        print("\n⚠️ 环境验证发现问题:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("\n✅ 环境验证通过")
        return True


def interactive_switch():
    """交互式切换"""
    print_current_status()
    print_config_options()

    while True:
        try:
            choice = input("请选择结构类型 [1-2] (或按 q 退出): ").strip()

            if choice.lower() == 'q':
                print("👋 退出切换工具")
                return

            if choice not in CONFIG_TYPES:
                print("❌ 无效选择，请重新输入")
                continue

            new_type = CONFIG_TYPES[choice]['name']
            current_type = read_current_config()

            if new_type == current_type:
                print(f"💡 当前已经是 {new_type} 配置")
                continue

            # 确认切换
            config_desc = CONFIG_TYPES[choice]['description']
            confirm = input(f"\n确认切换到 '{config_desc}' ? [y/N]: ").strip().lower()

            if confirm in ['y', 'yes']:
                update_config(new_type)
                print(f"\n🎉 切换完成！")
                print(f"💡 请重新运行 main.py 以使用新配置")
                return
            else:
                print("❌ 取消切换")

        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出切换工具")
            return
        except Exception as e:
            print(f"❌ 切换过程出错: {e}")


def batch_switch(target_type):
    """批量切换（非交互式）"""
    if target_type not in [config['name'] for config in CONFIG_TYPES.values()]:
        print(f"❌ 不支持的配置类型: {target_type}")
        return False

    current_type = read_current_config()
    if target_type == current_type:
        print(f"💡 当前已经是 {target_type} 配置")
        return True

    update_config(target_type)
    return True


def main():
    """主函数"""
    print_banner()

    # 验证环境
    if not validate_environment():
        print("\n❌ 环境验证失败，请检查配置文件")
        return

    # 检查命令行参数
    if len(sys.argv) > 1:
        # 批量模式
        target_type = sys.argv[1].upper()
        if batch_switch(target_type):
            print(f"✅ 已切换到 {target_type} 配置")
        else:
            print("❌ 批量切换失败")
    else:
        # 交互模式
        interactive_switch()


def print_usage():
    """打印使用说明"""
    print("\n📖 使用说明:")
    print("   交互模式: python switch_config.py")
    print("   批量模式: python switch_config.py SHEAR_WALL")
    print("   批量模式: python switch_config.py FRAME")
    print("\n🔧 手动切换:")
    print("   编辑 config/__init__.py 文件")
    print("   修改 STRUCTURE_TYPE = \"SHEAR_WALL\" 或 \"FRAME\"")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        print_usage()

    input("\n按回车键退出...")