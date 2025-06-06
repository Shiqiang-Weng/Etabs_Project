# -*- coding: utf-8 -*-
"""
通用辅助函数
包含ETABS API调用的通用工具函数
"""

import sys
from typing import List, Any, Tuple, Union

from utils.dotnet import get_etabs_modules


def check_ret(ret_val, func_name: str, ok_codes: tuple = (0,)) -> int:
    """
    统一检查 ETABS API 的返回值

    Parameters:
        ret_val: int | tuple - API返回值
        func_name: str - 函数名称，用于报错和日志
        ok_codes: tuple - 允许的返回码，默认 (0,)

    Returns:
        int: 返回码
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if System is None:
        sys.exit("System module missing in check_ret")

    code = ret_val[0] if isinstance(ret_val, tuple) and len(ret_val) > 0 else ret_val

    # 允许特定函数返回1（对象已存在/数值未改变）
    if code == 1 and any(
            kw in func_name
            for kw in [
                "SetNumberModes", "SetMaterial", "SetWall", "SetSlab",
                "SetRectangle", "SetCase", "Add(", "AddByCoord", "SetDiaphragm",
                "SetPier", "SetSpandrel", "SetSelfWTMultiplier", "SetLoadUniform",
                "SetRunCaseFlag", "DeselectAllCasesAndCombosForOutput",
                "SetCaseSelectedForOutput", "Drift", "SetModifiers",
                # 结果提取相关函数允许返回1
                "Results.ModalPeriod", "Results.ModalParticipatingMassRatios",
                "Results.StoryDrifts", "Results.", "ModalPeriod",
                "ModalParticipatingMassRatios", "StoryDrifts", "GetNameList",
                "RefreshView",
            ]
    ):
        if "Results." in func_name or any(
                x in func_name for x in ["ModalPeriod", "StoryDrifts", "ModalParticipatingMassRatios"]
        ):
            print(f"信息: {func_name} 返回 1（可能无结果数据），将继续处理。")
        else:
            print(f"信息: {func_name} 返回 1（对象已存在 / 数值未改变），脚本继续。")
        return code

    if code not in ok_codes:
        error_message = (
            f"函数 {func_name} 调用出错: API 返回代码 {code}，"
            f"预期 {ok_codes}。完整返回值: {ret_val}"
        )
        print(error_message)
        sys.exit(f"关键错误: {error_message}")

    return code


def arr(py_list: List[Any], sys_type=None):
    """
    将Python列表转换为.NET数组

    Parameters:
        py_list: Python列表
        sys_type: .NET类型，默认为System.Double

    Returns:
        .NET数组
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if System is None:
        sys.exit("System module missing in arr")

    if sys_type is None:
        sys_type = System.Double

    a = System.Array[sys_type](len(py_list))
    for i, val in enumerate(py_list):
        a[i] = val
    return a


def add_area_by_coord_custom(area_object_api, num_points: int,
                             x_coords_py: List[float], y_coords_py: List[float],
                             z_coords_py: List[float], prop_name: str,
                             user_name_in: str, csys: str = "Global") -> Tuple[int, str]:
    """
    自定义面对象创建函数

    Parameters:
        area_object_api: ETABS面对象API
        num_points: 点的数量
        x_coords_py: X坐标列表
        y_coords_py: Y坐标列表
        z_coords_py: Z坐标列表
        prop_name: 属性名称
        user_name_in: 用户定义名称
        csys: 坐标系，默认"Global"

    Returns:
        tuple: (状态码, 实际名称)
    """
    ETABSv1, System, COMException = get_etabs_modules()

    etabs_assigned_name_ref = System.String("")
    x_api, y_api, z_api = arr(x_coords_py), arr(y_coords_py), arr(z_coords_py)

    ret_tuple = area_object_api.AddByCoord(
        num_points, x_api, y_api, z_api, etabs_assigned_name_ref,
        prop_name, user_name_in, csys
    )

    api_status = ret_tuple[0]
    actual_name = ""
    name_from_tuple_orig_logic = None

    # 尝试从返回元组中获取名称
    for idx in [3, 4]:
        if idx < len(ret_tuple) and isinstance(ret_tuple[idx], str) and ret_tuple[idx].strip():
            name_from_tuple_orig_logic = ret_tuple[idx]
            break

    name_from_ref = str(etabs_assigned_name_ref) if etabs_assigned_name_ref and str(
        etabs_assigned_name_ref).strip() else None

    # 优先使用ref中的名称，然后是元组中的名称，最后回退到用户输入
    if name_from_ref:
        actual_name = name_from_ref
    elif name_from_tuple_orig_logic:
        actual_name = name_from_tuple_orig_logic
    else:
        actual_name = user_name_in

    return api_status, actual_name


def add_frame_by_coord_custom(frame_object_api, x1: float, y1: float, z1: float,
                              x2: float, y2: float, z2: float, prop_name: str,
                              user_name_in: str, csys: str = "Global") -> Tuple[int, str]:
    """
    自定义框架对象创建函数

    Parameters:
        frame_object_api: ETABS框架对象API
        x1, y1, z1: 起点坐标
        x2, y2, z2: 终点坐标
        prop_name: 属性名称
        user_name_in: 用户定义名称
        csys: 坐标系，默认"Global"

    Returns:
        tuple: (状态码, 实际名称)
    """
    ETABSv1, System, COMException = get_etabs_modules()

    etabs_assigned_name_ref = System.String("")
    ret_tuple = frame_object_api.AddByCoord(
        x1, y1, z1, x2, y2, z2, etabs_assigned_name_ref,
        prop_name, user_name_in, csys
    )

    api_status = ret_tuple[0]
    actual_name = ""
    name_from_tuple = None
    name_idx_in_tuple = 1  # 标准索引

    if (name_idx_in_tuple < len(ret_tuple) and
            isinstance(ret_tuple[name_idx_in_tuple], str) and
            ret_tuple[name_idx_in_tuple].strip()):
        name_from_tuple = ret_tuple[name_idx_in_tuple]

    name_from_ref = str(etabs_assigned_name_ref) if etabs_assigned_name_ref and str(
        etabs_assigned_name_ref).strip() else None

    if name_from_ref:
        actual_name = name_from_ref
    elif name_from_tuple:
        actual_name = name_from_tuple
    else:
        actual_name = user_name_in

    return api_status, actual_name