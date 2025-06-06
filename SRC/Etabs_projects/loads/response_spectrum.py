# -*- coding: utf-8 -*-
"""
反应谱函数定义模块
"""

import math
from utils import check_ret, arr, get_etabs_modules
from config import (
    RS_BASE_ACCEL_G, RS_CHARACTERISTIC_PERIOD, RS_DAMPING_RATIO,
    GRAVITY_ACCEL, RS_FUNCTION_NAME, MODAL_CASE_NAME, GENERATE_RS_COMBOS
)


def china_response_spectrum(T: float, zeta: float, alpha_max: float,
                            Tg: float, g: float = GRAVITY_ACCEL) -> float:
    """
    中国规范反应谱函数

    Parameters:
        T: 周期 (s)
        zeta: 阻尼比
        alpha_max: 最大地震影响系数
        Tg: 场地特征周期 (s)
        g: 重力加速度 (m/s²)

    Returns:
        float: 反应谱值 (m/s²)
    """
    gamma = 0.9 + (0.05 - zeta) / (0.3 + 6.0 * zeta)
    eta1 = max(0.0, 0.02 + (0.05 - zeta) / (4.0 + 32.0 * zeta))
    eta2 = max(0.55, 1.0 + (0.05 - zeta) / (0.08 + 1.6 * zeta))

    current_alpha_coeff: float

    if T < 0:
        current_alpha_coeff = 0.0
    elif T == 0.0:
        current_alpha_coeff = 0.45 * alpha_max
    elif T <= 0.1:
        current_alpha_coeff = min((0.45 + 10.0 * (eta2 - 0.45) * T) * alpha_max, eta2 * alpha_max)
    elif T <= Tg:
        current_alpha_coeff = eta2 * alpha_max
    elif T <= 5.0 * Tg:
        current_alpha_coeff = ((Tg / T) ** gamma) * eta2 * alpha_max
    elif T <= 6.0:
        alpha_at_5Tg_coeff = (0.2 ** gamma) * eta2
        current_alpha_coeff = (alpha_at_5Tg_coeff - eta1 * (T - 5.0 * Tg)) * alpha_max
    else:
        alpha_at_5Tg_coeff = (0.2 ** gamma) * eta2
        current_alpha_coeff = (alpha_at_5Tg_coeff - eta1 * (6.0 - 5.0 * Tg)) * alpha_max

    current_alpha_coeff = max(current_alpha_coeff, 0.20 * alpha_max)
    current_alpha_coeff = max(0.0, current_alpha_coeff)

    return current_alpha_coeff * g


def generate_response_spectrum_data():
    """
    生成反应谱数据

    Returns:
        tuple: (periods, values) 周期和对应的反应谱值
    """
    # 定义周期点
    periods = sorted(list(set({
        0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, RS_CHARACTERISTIC_PERIOD,
        0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0
    })))

    # 计算对应的反应谱值（以g为单位）
    values = [
        round(
            china_response_spectrum(
                T=t,
                zeta=RS_DAMPING_RATIO,
                alpha_max=RS_BASE_ACCEL_G,
                Tg=RS_CHARACTERISTIC_PERIOD,
                g=GRAVITY_ACCEL
            ) / GRAVITY_ACCEL,
            6
        ) for t in periods
    ]

    return periods, values


def define_response_spectrum_functions_in_etabs(sap_model):
    """
    在ETABS中定义反应谱函数

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        raise ValueError("SapModel未初始化")

    print(f"\n📈 定义反应谱函数 '{RS_FUNCTION_NAME}'...")

    # 生成反应谱数据
    periods, values = generate_response_spectrum_data()

    # 准备数据库表数据
    db = sap_model.DatabaseTables
    key = "Functions - Response Spectrum - User Defined"
    fields = arr(["Name", "Period", "Value", "Damping Ratio"], System.String)

    # 构造数据行
    data_py = []
    for i, period in enumerate(periods):
        data_py.extend([
            RS_FUNCTION_NAME,
            str(round(period, 4)),
            str(round(values[i], 6)),
            str(RS_DAMPING_RATIO)
        ])

    # 设置表格数据
    check_ret(
        db.SetTableForEditingArray(
            key,
            System.Int32(0),
            fields,
            System.Int32(len(periods)),
            arr(data_py, System.String)
        ),
        f"SetTableForEditingArray({RS_FUNCTION_NAME})"
    )

    # 应用表格编辑
    nfe, ne, nw, ni, log = (
        System.Int32(0), System.Int32(0), System.Int32(0),
        System.Int32(0), System.String("")
    )
    ret_apply = db.ApplyEditedTables(True, nfe, ne, nw, ni, log)
    check_ret(ret_apply[0], f"ApplyEditedTables({RS_FUNCTION_NAME})")

    if ret_apply[1] > 0:
        raise RuntimeError("反应谱函数定义失败 (致命错误)")

    print(f"✅ 反应谱函数 '{RS_FUNCTION_NAME}' 定义成功")
    print(f"   周期范围: {min(periods):.3f}s - {max(periods):.1f}s")
    print(f"   数据点数: {len(periods)} 个")


def define_modal_and_rs_cases(sap_model):
    """
    定义模态和反应谱工况

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        raise ValueError("SapModel未初始化")

    print(f"\n🔬 定义模态和反应谱工况...")

    lc = sap_model.LoadCases
    mod_api = lc.ModalEigen
    rs_api = lc.ResponseSpectrum

    # 检查现有模态工况
    num_val = System.Int32(0)
    names_val = System.Array[System.String](0)
    ret_tuple = lc.GetNameList(num_val, names_val, ETABSv1.eLoadCaseType.Modal)
    check_ret(ret_tuple[0], "GetNameList(Modal)")

    existing_modals = list(ret_tuple[2]) if ret_tuple[1] > 0 and ret_tuple[2] is not None else []

    # 定义模态工况
    if MODAL_CASE_NAME not in existing_modals:
        check_ret(mod_api.SetCase(MODAL_CASE_NAME), f"ModalEigen.SetCase({MODAL_CASE_NAME})")

    # 设置求解器
    if hasattr(mod_api, "SetEigenSolver"):
        check_ret(mod_api.SetEigenSolver(MODAL_CASE_NAME, 0), f"SetEigenSolver({MODAL_CASE_NAME})")
    elif hasattr(mod_api, "SetModalSolverOption"):
        check_ret(mod_api.SetModalSolverOption(MODAL_CASE_NAME, 0), f"SetModalSolverOption({MODAL_CASE_NAME})")

    # 设置模态数量
    check_ret(mod_api.SetNumberModes(MODAL_CASE_NAME, 60, 1), f"SetNumberModes({MODAL_CASE_NAME})", (0, 1))

    # 定义反应谱工况
    rs_cases_created = []
    for direction_label, u_dir_code in [("X", "U1"), ("Y", "U2")]:
        case_name = f"RS-{direction_label}"

        # 创建反应谱工况
        check_ret(rs_api.SetCase(case_name), f"RS.SetCase({case_name})", (0, 1))

        # 设置荷载
        check_ret(
            rs_api.SetLoads(
                case_name,
                1,
                arr([u_dir_code], System.String),
                arr([RS_FUNCTION_NAME], System.String),
                arr([GRAVITY_ACCEL]),
                arr(["Global"], System.String),
                arr([0.0])
            ),
            f"RS.SetLoads({case_name})"
        )

        # 设置模态工况
        check_ret(rs_api.SetModalCase(case_name, MODAL_CASE_NAME), f"RS.SetModalCase({case_name})")

        # 设置模态组合方法（CQC）
        if hasattr(rs_api, "SetModalComb"):
            check_ret(
                rs_api.SetModalComb(case_name, 0, 0.0, RS_DAMPING_RATIO, 0),
                f"RS.SetModalComb({case_name})"
            )

        # 设置缺失质量
        if hasattr(rs_api, "SetMissingMass"):
            check_ret(rs_api.SetMissingMass(case_name, True), f"RS.SetMissingMass({case_name})")

        # 设置偶然偏心
        if hasattr(rs_api, "SetAccidentalEccen"):
            check_ret(
                rs_api.SetAccidentalEccen(case_name, 0.05, True, True),
                f"RS.SetAccidentalEccen({case_name})"
            )

        rs_cases_created.append(case_name)
        print(f"✅ 反应谱工况 '{case_name}' 定义完毕")

    # 生成地震效应组合
    if GENERATE_RS_COMBOS and len(rs_cases_created) == 2:
        _generate_seismic_combinations(sap_model, rs_cases_created)

    print("✅ 模态和反应谱工况定义完毕")


def _generate_seismic_combinations(sap_model, rs_cases: list):
    """
    生成地震效应组合

    Parameters:
        sap_model: ETABS SapModel对象
        rs_cases: 反应谱工况列表
    """
    ETABSv1, System, COMException = get_etabs_modules()

    combo_api = sap_model.RespCombo
    rs_ex, rs_ey = rs_cases[0], rs_cases[1]

    # 定义组合
    combos = [
        (f"E1_{rs_ex}_p03{rs_ey}", [(rs_ex, 1.0), (rs_ey, 0.3)]),
        (f"E2_{rs_ex}_m03{rs_ey}", [(rs_ex, 1.0), (rs_ey, -0.3)]),
        (f"E3_p03{rs_ex}_{rs_ey}", [(rs_ex, 0.3), (rs_ey, 1.0)]),
        (f"E4_m03{rs_ex}_{rs_ey}", [(rs_ex, -0.3), (rs_ey, 1.0)])
    ]

    for name, case_sfs in combos:
        # 添加组合
        check_ret(combo_api.Add(name, 0), f"RespCombo.Add({name})", (0, 1))  # 0 for SRSS

        # 设置工况列表
        for case, sf in case_sfs:
            check_ret(
                combo_api.SetCaseList(name, ETABSv1.eCNameType.LoadCase, System.String(case), System.Double(sf)),
                f"RespCombo.SetCaseList({name})"
            )

    print("✅ 地震效应组合定义完毕")


def define_all_response_spectrum(sap_model):
    """
    定义所有反应谱相关内容

    Parameters:
        sap_model: ETABS SapModel对象
    """
    print("\n📊 开始定义反应谱函数和工况...")

    define_response_spectrum_functions_in_etabs(sap_model)
    define_modal_and_rs_cases(sap_model)

    print("✅ 反应谱函数和工况定义完成")