# -*- coding: utf-8 -*-
"""
荷载模块
包含所有荷载相关的定义和设置
"""

from .load_patterns import define_all_load_patterns
from .dead_live_loads import assign_all_dead_live_loads
from .mass_source import define_all_mass_sources
from .response_spectrum import define_all_response_spectrum

# 尝试导入框架结构专用荷载模块
try:
    from .frame_loads import assign_all_frame_loads

    FRAME_LOADS_AVAILABLE = True
except ImportError:
    FRAME_LOADS_AVAILABLE = False


# 主要接口函数
def define_all_loads(sap_model, wall_names: list, cb_names: list):
    """
    定义所有荷载的主接口

    Parameters:
        sap_model: ETABS SapModel对象
        wall_names: 墙体名称列表（对于框架结构，这里是柱名称）
        cb_names: 连梁名称列表（对于框架结构，这里是梁名称）
    """
    print("\n⚖️ 开始定义所有荷载...")

    # 1. 定义荷载模式和工况
    define_all_load_patterns(sap_model)

    # 2. 定义质量源和楼面约束
    define_all_mass_sources(sap_model)

    # 3. 定义反应谱函数和工况
    define_all_response_spectrum(sap_model)

    # 4. 根据结构类型分配荷载
    try:
        from config import STRUCTURE_TYPE, ENABLE_FRAME_COLUMNS, ENABLE_FRAME_BEAMS

        if STRUCTURE_TYPE == "FRAME" and (ENABLE_FRAME_COLUMNS or ENABLE_FRAME_BEAMS):
            # 框架结构荷载分配
            print("\n📊 分配框架结构荷载...")

            if FRAME_LOADS_AVAILABLE:
                # 使用专门的框架荷载分配函数
                assign_all_frame_loads(sap_model, wall_names, cb_names)
            else:
                print("⚠️ 框架荷载模块不可用，使用通用荷载分配")
                assign_all_dead_live_loads(sap_model, [], [])  # 空列表，因为框架结构主要是楼板荷载
        else:
            # 剪力墙结构或其他结构类型
            print("\n📊 分配剪力墙/通用结构荷载...")
            assign_all_dead_live_loads(sap_model, wall_names, cb_names)

    except ImportError:
        print("⚠️ 无法获取结构类型配置，使用默认荷载分配")
        assign_all_dead_live_loads(sap_model, wall_names, cb_names)

    print("✅ 所有荷载定义完成")


def get_load_summary():
    """
    获取荷载配置摘要

    Returns:
        dict: 荷载配置信息
    """
    summary = {
        'load_patterns': ['DEAD', 'LIVE'],
        'load_cases': ['DEAD', 'LIVE', 'MODAL_RS', 'RS-X', 'RS-Y'],
        'mass_source': 'DEAD(1.0) + LIVE(0.5)',
        'response_spectrum': 'GB50011'
    }

    try:
        from config import (
            STRUCTURE_TYPE, DEFAULT_DEAD_SUPER_SLAB, DEFAULT_LIVE_LOAD_SLAB,
            RS_DESIGN_INTENSITY, RS_BASE_ACCEL_G, RS_SITE_CLASS
        )

        summary['structure_type'] = STRUCTURE_TYPE
        summary['slab_dead_load'] = f"{DEFAULT_DEAD_SUPER_SLAB} kPa"
        summary['slab_live_load'] = f"{DEFAULT_LIVE_LOAD_SLAB} kPa"
        summary['seismic_intensity'] = f"{RS_DESIGN_INTENSITY}度"
        summary['design_acceleration'] = f"{RS_BASE_ACCEL_G}g"
        summary['site_class'] = RS_SITE_CLASS

        if STRUCTURE_TYPE == "FRAME":
            try:
                from config import BEAM_DEAD_LOAD, BEAM_LIVE_LOAD, COLUMN_AXIAL_LOAD
                summary['beam_dead_load'] = f"{BEAM_DEAD_LOAD} kN/m"
                summary['beam_live_load'] = f"{BEAM_LIVE_LOAD} kN/m"
                summary['column_axial_load'] = f"{COLUMN_AXIAL_LOAD} kN"
            except ImportError:
                summary['frame_loads'] = "未配置"

    except ImportError:
        summary['config_status'] = "配置文件不完整"

    return summary


def print_load_summary():
    """
    打印荷载配置摘要
    """
    summary = get_load_summary()

    print(f"\n⚖️ 荷载配置摘要:")
    print(f"   结构类型: {summary.get('structure_type', '未知')}")
    print(f"   楼板恒荷载: {summary.get('slab_dead_load', '未配置')}")
    print(f"   楼板活荷载: {summary.get('slab_live_load', '未配置')}")

    if summary.get('structure_type') == "FRAME":
        print(f"   梁恒荷载: {summary.get('beam_dead_load', '未配置')}")
        print(f"   梁活荷载: {summary.get('beam_live_load', '未配置')}")
        print(f"   柱轴向荷载: {summary.get('column_axial_load', '未配置')}")

    print(f"   地震设防烈度: {summary.get('seismic_intensity', '未配置')}")
    print(f"   设计加速度: {summary.get('design_acceleration', '未配置')}")
    print(f"   场地类别: {summary.get('site_class', '未配置')}")
    print(f"   质量源: {summary.get('mass_source', '未配置')}")


__all__ = [
    'define_all_loads',
    'define_all_load_patterns',
    'assign_all_dead_live_loads',
    'define_all_mass_sources',
    'define_all_response_spectrum',
    'get_load_summary',
    'print_load_summary'
]

# 如果框架荷载模块可用，则添加到导出列表
if FRAME_LOADS_AVAILABLE:
    __all__.append('assign_all_frame_loads')