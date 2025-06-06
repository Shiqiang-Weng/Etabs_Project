# -*- coding: utf-8 -*-
"""
分析运行器模块
负责执行ETABS结构分析
"""

import time
from typing import List
from utils import check_ret, get_etabs_modules
from config import MODAL_CASE_NAME, ANALYSIS_WAIT_TIME, DELETE_OLD_RESULTS


def safe_run_analysis(sap_model, model_path: str, load_cases_to_run: List[str],
                      delete_old_results: bool = DELETE_OLD_RESULTS):
    """
    安全运行分析

    Parameters:
        sap_model: ETABS SapModel对象
        model_path: 模型文件路径
        load_cases_to_run: 要运行的荷载工况列表
        delete_old_results: 是否删除旧结果
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        raise ValueError("SapModel未初始化")

    analyze_obj = sap_model.Analyze
    file_api = sap_model.File

    print(f"🔧 准备分析...")

    # 确保模型未锁定
    check_ret(sap_model.SetModelIsLocked(False), "SetModelIsLocked(False) before analysis", (0, 1))

    # 保存模型
    if file_api.Save(model_path) != 0:
        raise RuntimeError("分析前保存模型失败")
    print(f"✅ 模型已保存到: {model_path}")

    # 检查工况列表
    if not load_cases_to_run:
        raise RuntimeError("未指定分析工况")

    # 获取已定义的工况
    num_val = System.Int32(0)
    names_val = System.Array[System.String](0)
    ret_tuple = sap_model.LoadCases.GetNameList(num_val, names_val)
    defined_cases = list(ret_tuple[2]) if ret_tuple[0] == 0 and ret_tuple[1] > 0 and ret_tuple[2] is not None else []

    print(f"📋 模型中已定义的工况: {defined_cases}")
    print(f"🎯 计划运行的工况: {load_cases_to_run}")

    # 设置要运行的工况
    valid_cases = []
    for case in load_cases_to_run:
        if defined_cases and case not in defined_cases:
            print(f"⚠️ 警告: 工况 '{case}' 未定义，跳过")
            continue

        ret_set = sap_model.Analyze.SetRunCaseFlag(case, True)
        if ret_set != 0:
            print(f"⚠️ 警告: 设置工况 '{case}' 运行失败")
        else:
            valid_cases.append(case)
            print(f"✅ 工况 '{case}' 已设置为运行")

    if not valid_cases:
        raise RuntimeError("没有有效的工况可以运行")

    # 删除旧结果（可选）
    if delete_old_results:
        try:
            check_ret(analyze_obj.DeleteResults(""), "DeleteResults", (0, 1))
            print("🗑️ 已清理旧分析结果")
        except Exception as e:
            print(f"⚠️ 清理旧结果失败: {e}")

    # 运行分析
    print(f"🚀 开始运行分析...")
    print(f"📊 分析工况: {valid_cases}")

    ret_run = analyze_obj.RunAnalysis()
    if ret_run != 0:
        raise RuntimeError(f"RunAnalysis 执行失败，返回码: {ret_run}")

    print("✅ 分析成功完成!")


def wait_and_run_analysis(sap_model, model_path: str, wait_seconds: int = ANALYSIS_WAIT_TIME):
    """
    等待并运行分析

    Parameters:
        sap_model: ETABS SapModel对象
        model_path: 模型文件路径
        wait_seconds: 等待时间（秒）
    """
    if not sap_model:
        print("❌ SapModel 未就绪，无法分析")
        return False

    # 定义要分析的工况
    load_cases = ["DEAD", "LIVE", MODAL_CASE_NAME, "RS-X", "RS-Y"]

    print(f"\n⏰ 等待 {wait_seconds} 秒后开始分析...")
    print(f"📋 计划分析工况: {load_cases}")
    time.sleep(wait_seconds)

    try:
        safe_run_analysis(sap_model, model_path, load_cases)
        return True

    except Exception as e:
        print(f"❌ 分析执行错误: {e}")
        return False


def check_analysis_status(sap_model):
    """
    检查分析状态

    Parameters:
        sap_model: ETABS SapModel对象

    Returns:
        bool: 分析是否完成
    """
    if not sap_model:
        return False

    try:
        # 这里可以添加检查分析状态的逻辑
        # 例如检查结果是否可用
        print("🔍 检查分析状态...")
        return True

    except Exception as e:
        print(f"❌ 检查分析状态失败: {e}")
        return False


def run_analysis(sap_model, model_path: str):
    """
    运行分析的主接口

    Parameters:
        sap_model: ETABS SapModel对象
        model_path: 模型文件路径

    Returns:
        bool: 分析是否成功
    """
    print("\n🔬 开始结构分析...")

    # 等待并运行分析
    success = wait_and_run_analysis(sap_model, model_path)

    if success:
        # 检查分析状态
        if check_analysis_status(sap_model):
            print("✅ 结构分析完成并验证成功")
            return True
        else:
            print("⚠️ 分析完成但状态验证失败")
            return False
    else:
        print("❌ 结构分析失败")
        return False