# -*- coding: utf-8 -*-
"""
.NET 运行时和 ETABS API 加载工具
"""

import sys
from typing import Any, Optional

from config.settings import ETABS_DLL_PATH

# 全局变量，存储加载的模块
ETABSv1: Optional[Any] = None
System: Optional[Any] = None
COMException: Optional[Any] = None


def load_dotnet_etabs_api() -> bool:
    """
    加载.NET运行时和ETABS API

    Returns:
        bool: 加载成功返回True，失败返回False
    """
    global ETABSv1, System, COMException

    print("\n正在加载.NET 运行时...")

    try:
        # 加载 .NET Framework
        from pythonnet import load
        load("netfx")
        print(".NET Framework 运行时 (netfx)已尝试加载。")

        # 导入CLR和System
        import clr
        import System as Sys
        System = Sys

        from System.Runtime.InteropServices import COMException as ComExc
        COMException = ComExc
        print(".NET 运行时及 System 相关库已成功加载。")

        # 加载ETABS API
        print(f"正在从指定路径加载 ETABS API: {ETABS_DLL_PATH}")
        clr.AddReference(ETABS_DLL_PATH)

        import ETABSv1 as EtabsApiModule
        ETABSv1 = EtabsApiModule
        print("ETABS API 引用已成功加载。现在可以通过 ETABSv1.xxx 访问其成员。")

        return True

    except ImportError as exc:
        error_msg = (
            f"致命错误: pythonnet 库缺失或加载失败: {exc}。\n"
            f"请通过 'pip install pythonnet' 命令安装。"
        )
        print(error_msg)
        return False

    except FileNotFoundError:
        error_msg = (
            f"致命错误: 在路径 {ETABS_DLL_PATH} 未找到 ETABSv1.dll 文件。\n"
            f"请确认 ETABS 安装正确, 并且 ETABS_DLL_PATH 配置无误。"
        )
        print(error_msg)
        return False

    except Exception as e:
        error_msg = f"致命错误: 加载.NET 运行时, System 库, 或 ETABS API 时发生意外错误: {e}"
        print(error_msg)
        return False


def get_etabs_modules():
    """
    获取已加载的ETABS模块

    Returns:
        tuple: (ETABSv1, System, COMException)
    """
    return ETABSv1, System, COMException


def is_dotnet_loaded() -> bool:
    """
    检查.NET运行时是否已加载

    Returns:
        bool: 已加载返回True
    """
    return all(module is not None for module in [ETABSv1, System, COMException])