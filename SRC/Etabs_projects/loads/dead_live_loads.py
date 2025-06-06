# -*- coding: utf-8 -*-
"""
恒荷载和活荷载定义模块
"""

from typing import List
from utils import check_ret, get_etabs_modules
from config import DEFAULT_DEAD_SUPER_SLAB, DEFAULT_LIVE_LOAD_SLAB, DEFAULT_FINISH_LOAD_KPA


def assign_dead_and_live_loads_to_slabs(sap_model,
                                        dead_kpa: float = DEFAULT_DEAD_SUPER_SLAB,
                                        live_kpa: float = DEFAULT_LIVE_LOAD_SLAB):
    """
    为楼板分配恒荷载和活荷载

    Parameters:
        sap_model: ETABS SapModel对象
        dead_kpa: 恒荷载大小 (kPa)
        live_kpa: 活荷载大小 (kPa)
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        raise ValueError("SapModel未初始化")

    area_obj = sap_model.AreaObj

    # 获取所有面对象名称
    num_val = System.Int32(0)
    names_val = System.Array[System.String](0)
    ret_tuple = area_obj.GetNameList(num_val, names_val)
    check_ret(ret_tuple[0], "AreaObj.GetNameList (for slab loads)")

    all_area_names = list(ret_tuple[2]) if ret_tuple[1] > 0 and ret_tuple[2] is not None else []

    # 筛选楼板对象
    slabs_to_load = [name for name in all_area_names if name.startswith("SLAB_")]

    if not slabs_to_load:
        print("⚠️ 警告: 未找到 'SLAB_' 开头的楼板")
        return

    print(f"正在为 {len(slabs_to_load)} 个楼板网格单元施加荷载...")

    # 为每个楼板施加荷载
    for slab_name in slabs_to_load:
        # 施加恒荷载
        check_ret(
            area_obj.SetLoadUniform(
                slab_name, "DEAD", abs(dead_kpa), 10, True, "Global",
                ETABSv1.eItemType.Objects
            ),
            f"SetLoadUniform DEAD on {slab_name}",
            (0, 1)
        )

        # 施加活荷载
        check_ret(
            area_obj.SetLoadUniform(
                slab_name, "LIVE", abs(live_kpa), 10, True, "Global",
                ETABSv1.eItemType.Objects
            ),
            f"SetLoadUniform LIVE on {slab_name}",
            (0, 1)
        )

    print(f"✅ 已为 {len(slabs_to_load)} 个楼板施加 DEAD({dead_kpa} kPa) 和 LIVE({live_kpa} kPa) 荷载")


def assign_finish_loads_to_vertical_elements(sap_model, wall_names: List[str],
                                             cb_names: List[str],
                                             finish_kpa: float = DEFAULT_FINISH_LOAD_KPA):
    """
    为竖向构件分配面层荷载

    Parameters:
        sap_model: ETABS SapModel对象
        wall_names: 墙体名称列表
        cb_names: 连梁名称列表
        finish_kpa: 面层荷载大小 (kPa)
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        raise ValueError("SapModel未初始化")

    area_obj = sap_model.AreaObj
    elements_to_load = wall_names + cb_names

    if not elements_to_load:
        print("⚠️ 警告: 无墙或连梁名称列表，不施加面层荷载")
        return

    print(f"正在为 {len(elements_to_load)} 个竖向构件施加面层荷载...")

    # 为每个竖向构件施加面层荷载
    for panel_name in elements_to_load:
        if not panel_name or not panel_name.strip():
            continue

        check_ret(
            area_obj.SetLoadUniform(
                panel_name, "DEAD", abs(finish_kpa), 10, True, "Global",
                ETABSv1.eItemType.Objects
            ),
            f"SetLoadUniform (finish) on {panel_name}",
            (0, 1)
        )

    print(f"✅ 已为 {len(elements_to_load)} 个竖向构件施加面层荷载({finish_kpa} kPa)")


def assign_all_dead_live_loads(sap_model, wall_names: List[str], cb_names: List[str]):
    """
    分配所有恒荷载和活荷载

    Parameters:
        sap_model: ETABS SapModel对象
        wall_names: 墙体名称列表
        cb_names: 连梁名称列表
    """
    print("\n📦 开始分配恒荷载和活荷载...")

    # 楼板荷载
    assign_dead_and_live_loads_to_slabs(sap_model)

    # 竖向构件面层荷载
    assign_finish_loads_to_vertical_elements(sap_model, wall_names, cb_names)

    print("✅ 所有恒荷载和活荷载分配完成")