# -*- coding: utf-8 -*-
"""
模态结果提取模块
"""

import traceback
from utils import check_ret, get_etabs_modules
from config import MODAL_CASE_NAME


def extract_modal_periods(sap_model):
    """
    提取模态周期和频率

    Parameters:
        sap_model: ETABS SapModel对象

    Returns:
        dict: 模态周期信息
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model or not hasattr(sap_model, "Results") or sap_model.Results is None:
        print("❌ 错误: 结果不可用，无法提取模态周期")
        return {}

    print("\n📊 --- 模态周期和频率 ---")

    results_api = sap_model.Results

    # 初始化参数
    _Num_MP, _LC_MP, _ST_MP, _SN_MP, _P_MP, _F_MP, _CF_MP, _EV_MP = (
        System.Int32(0),
        System.Array[System.String](0),
        System.Array[System.String](0),
        System.Array[System.Double](0),
        System.Array[System.Double](0),
        System.Array[System.Double](0),
        System.Array[System.Double](0),
        System.Array[System.Double](0)
    )

    try:
        mp_res = results_api.ModalPeriod(_Num_MP, _LC_MP, _ST_MP, _SN_MP, _P_MP, _F_MP, _CF_MP, _EV_MP)
        ret_code = check_ret(mp_res[0], "Results.ModalPeriod", (0, 1))

        if ret_code == 1:
            print("  💡 提示: 模态周期结果可能不完整或无数据，但将尝试继续处理...")

        num_m = mp_res[1]
        p_val = list(mp_res[5]) if mp_res[5] is not None else []

        modal_info = {}

        if num_m > 0 and p_val:
            print(f"  找到 {num_m} 个模态，显示前10个:")
            print(f"{'振型号':<5} {'周期 (s)':<12} {'频率 (Hz)':<12}")
            print("-" * 32)

            modal_info['count'] = num_m
            modal_info['periods'] = p_val[:10]
            modal_info['frequencies'] = []
            modal_info['all_periods'] = p_val

            for i in range(min(num_m, 10)):
                T_curr = p_val[i]
                freq_curr = 1.0 / T_curr if T_curr > 0 else 0
                modal_info['frequencies'].append(freq_curr)
                print(f"{i + 1:<5} {T_curr:<12.4f} {freq_curr:<12.4f}")

            print("\n💡 扭转-平动周期比分析将在质量参与系数部分进行")

        else:
            print("  未找到模态周期结果或数据为空")
            print("  可能原因: 1) 模态分析未完成 2) 模态工况未正确定义 3) 结构质量分布问题")
            modal_info['error'] = "无模态周期数据"

    except Exception as e:
        print(f"  ❌ 提取模态周期时发生错误: {e}")
        modal_info['error'] = str(e)

    return modal_info


def extract_modal_participation(sap_model):
    """
    提取模态参与质量系数

    Parameters:
        sap_model: ETABS SapModel对象

    Returns:
        dict: 模态参与质量系数信息
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model or not hasattr(sap_model, "Results") or sap_model.Results is None:
        print("❌ 错误: 结果不可用，无法提取模态参与质量系数")
        return {}

    print("\n📊 --- 模态参与质量系数 ---")

    results_api = sap_model.Results

    # 初始化参数
    params = [System.Int32(0)] + [System.Array[System.String](0)] * 2 + [System.Array[System.Double](0)] * 14

    try:
        mpmr_res = results_api.ModalParticipatingMassRatios(*params)
        ret_code = check_ret(mpmr_res[0], "ModalParticipatingMassRatios", (0, 1))

        if ret_code == 1:
            print("  💡 提示: 质量参与系数结果可能不完整或无数据，但将尝试继续处理...")

        if len(mpmr_res) < 18:
            print(f"  ⚠️ 警告: ModalParticipatingMassRatios 返回了 {len(mpmr_res)} 个值，预期为 18")
            return {'error': 'API返回值数量不正确'}

        num_m_mpmr = mpmr_res[1]
        period_val = list(mpmr_res[5]) if mpmr_res[5] is not None else []
        ux_val = list(mpmr_res[6]) if mpmr_res[6] is not None else []
        uy_val = list(mpmr_res[7]) if mpmr_res[7] is not None else []
        uz_val = list(mpmr_res[8]) if mpmr_res[8] is not None else []
        sum_ux_val = list(mpmr_res[9]) if mpmr_res[9] is not None else []
        sum_uy_val = list(mpmr_res[10]) if mpmr_res[10] is not None else []
        sum_uz_val = list(mpmr_res[11]) if mpmr_res[11] is not None else []
        rx_val = list(mpmr_res[12]) if mpmr_res[12] is not None else []
        ry_val = list(mpmr_res[13]) if mpmr_res[13] is not None else []
        rz_val = list(mpmr_res[14]) if mpmr_res[14] is not None else []
        sum_rx_val = list(mpmr_res[15]) if mpmr_res[15] is not None else []
        sum_ry_val = list(mpmr_res[16]) if mpmr_res[16] is not None else []
        sum_rz_val = list(mpmr_res[17]) if mpmr_res[17] is not None else []

        participation_info = {}

        all_lists = [period_val, ux_val, uy_val, uz_val, sum_ux_val, sum_uy_val, sum_uz_val,
                     rx_val, ry_val, rz_val, sum_rx_val, sum_ry_val, sum_rz_val]

        if num_m_mpmr > 0 and all(all_lists):
            print(f"  找到 {num_m_mpmr} 个模态的质量参与系数，显示前15个:")
            print(
                f"{'振型号':<5} {'周期(s)':<10} {'UX':<8} {'UY':<8} {'UZ':<8} {'RX':<8} {'RY':<8} {'RZ':<8} | {'SumUX':<8} {'SumUY':<8} {'SumUZ':<8} {'SumRX':<8} {'SumRY':<8} {'SumRZ':<8}")
            print("-" * 130)

            participation_info['count'] = num_m_mpmr
            participation_info['periods'] = period_val[:15]
            participation_info['ux'] = ux_val[:15]
            participation_info['uy'] = uy_val[:15]
            participation_info['uz'] = uz_val[:15]
            participation_info['sum_ux'] = sum_ux_val[:15]
            participation_info['sum_uy'] = sum_uy_val[:15]
            participation_info['sum_uz'] = sum_uz_val[:15]

            # 存储所有模态的参与系数用于周期比分析
            participation_info['all_periods'] = period_val
            participation_info['all_ux'] = ux_val
            participation_info['all_uy'] = uy_val
            participation_info['all_rz'] = rz_val

            for i in range(min(num_m_mpmr, 15)):
                T_c = period_val[i]
                print(f"{i + 1:<5} {T_c:<10.4f} "
                      f"{ux_val[i]:<8.4f} {uy_val[i]:<8.4f} {uz_val[i]:<8.4f} "
                      f"{rx_val[i]:<8.4f} {ry_val[i]:<8.4f} {rz_val[i]:<8.4f} | "
                      f"{sum_ux_val[i]:<8.4f} {sum_uy_val[i]:<8.4f} {sum_uz_val[i]:<8.4f} "
                      f"{sum_rx_val[i]:<8.4f} {sum_ry_val[i]:<8.4f} {sum_rz_val[i]:<8.4f}")

            # 识别第一个各方向主导模态
            first_x_translational_period = None
            first_y_translational_period = None
            first_torsional_period = None

            # 找第一个X方向平动模态（UX最大）
            for i in range(min(10, len(period_val))):
                if ux_val[i] > 0.3 and first_x_translational_period is None:
                    first_x_translational_period = period_val[i]
                    print(
                        f"\n🎯 第一X向平动模态: T1x = {first_x_translational_period:.4f}s (第{i + 1}振型, UX={ux_val[i]:.3f})")
                    break

            # 找第一个Y方向平动模态（UY最大）
            for i in range(min(10, len(period_val))):
                if uy_val[i] > 0.3 and first_y_translational_period is None:
                    first_y_translational_period = period_val[i]
                    print(
                        f"🎯 第一Y向平动模态: T1y = {first_y_translational_period:.4f}s (第{i + 1}振型, UY={uy_val[i]:.3f})")
                    break

            # 找第一个扭转模态（RZ最大）
            for i in range(min(10, len(period_val))):
                if rz_val[i] > 0.3 and first_torsional_period is None:
                    first_torsional_period = period_val[i]
                    print(f"🌀 第一扭转模态: Tt = {first_torsional_period:.4f}s (第{i + 1}振型, RZ={rz_val[i]:.3f})")
                    break

            # 计算扭转-平动周期比
            if first_torsional_period:
                print(f"\n📊 === 扭转-平动周期比分析 ===")

                if first_y_translational_period:
                    tt_t1y_ratio = first_torsional_period / first_y_translational_period
                    participation_info['tt_t1y_ratio'] = tt_t1y_ratio
                    warning_y = "✅ 扭转效应较小" if tt_t1y_ratio < 0.9 else "⚠️ 扭转效应显著"
                    print(
                        f"Tt/T1y = {first_torsional_period:.4f}/{first_y_translational_period:.4f} = {tt_t1y_ratio:.3f} {warning_y}")

                if first_x_translational_period:
                    tt_t1x_ratio = first_torsional_period / first_x_translational_period
                    participation_info['tt_t1x_ratio'] = tt_t1x_ratio
                    warning_x = "✅ 扭转效应较小" if tt_t1x_ratio < 0.9 else "⚠️ 扭转效应显著"
                    print(
                        f"Tt/T1x = {first_torsional_period:.4f}/{first_x_translational_period:.4f} = {tt_t1x_ratio:.3f} {warning_x}")

                # 存储所有相关信息
                participation_info['first_x_translational_period'] = first_x_translational_period
                participation_info['first_y_translational_period'] = first_y_translational_period
                participation_info['first_torsional_period'] = first_torsional_period

                print("=================================")
            else:
                print("⚠️ 无法识别明确的扭转主导模态")

            # 最终累积质量参与系数
            final_sums = {
                'ux': sum_ux_val[-1],
                'uy': sum_uy_val[-1],
                'uz': sum_uz_val[-1],
                'rx': sum_rx_val[-1],
                'ry': sum_ry_val[-1],
                'rz': sum_rz_val[-1]
            }

            participation_info['final_sums'] = final_sums

            print("\n--- 最终累积质量参与系数 ---")
            min_ratio = 0.90
            for direction, value in final_sums.items():
                status = "(OK)" if value >= min_ratio else f"(⚠️ < {min_ratio})"
                print(f"Sum{direction.upper()}: {value:.3f} {status}")

        else:
            print("  未找到模态参与质量系数结果或数据不完整")
            participation_info['error'] = "无模态参与质量系数数据"

    except Exception as e:
        print(f"  ❌ 提取模态参与质量系数时发生错误: {e}")
        traceback.print_exc()
        participation_info['error'] = str(e)

    return participation_info


def extract_modal_and_mass_info(sap_model):
    """
    提取模态信息和质量参与系数

    Parameters:
        sap_model: ETABS SapModel对象

    Returns:
        dict: 完整的模态信息
    """
    print(f"\n🔍 --- 开始提取模态信息和质量参与系数 ---")

    if not sap_model or not hasattr(sap_model, "Results") or sap_model.Results is None:
        print("❌ 错误: 结果不可用，无法提取模态信息")
        return {}

    results_api = sap_model.Results
    setup_api = results_api.Setup

    # 重新选择模态工况
    print(f"🎯 重新选择模态工况 '{MODAL_CASE_NAME}' 进行结果输出...")
    check_ret(setup_api.DeselectAllCasesAndCombosForOutput(), "DeselectAllCasesForModal", (0, 1))
    check_ret(setup_api.SetCaseSelectedForOutput(MODAL_CASE_NAME), f"SetCaseSelectedForModal({MODAL_CASE_NAME})",
              (0, 1))

    # 提取模态周期
    modal_periods = extract_modal_periods(sap_model)

    # 提取模态参与质量系数
    modal_participation = extract_modal_participation(sap_model)

    print("--- 模态信息和质量参与系数提取完毕 ---")

    return {
        'periods': modal_periods,
        'participation': modal_participation
    }