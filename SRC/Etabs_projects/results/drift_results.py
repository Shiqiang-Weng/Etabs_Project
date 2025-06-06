# -*- coding: utf-8 -*-
"""
层间位移角（Story Drift）提取模块
"""

import traceback
from utils import check_ret, get_etabs_modules
from config import DRIFT_LIMIT_PERMIL  # 例如 1.0


def extract_story_drifts(sap_model, load_cases=None):
    """
    提取相对层间位移角 (‰) 并返回结构化数据

    Parameters
    ----------
    sap_model : ETABS SapModel
    load_cases : list[str] | None
        需要提取的工况 / 组合名称列表；None 时使用默认值 ["RS-X", "RS-Y"]

    Returns
    -------
    dict
        包含位移角记录和最大值信息的字典
    """
    ETABSv1, System, _ = get_etabs_modules()

    # 默认工况列表
    if load_cases is None:
        load_cases = ["RS-X", "RS-Y"]

    print(f"\n📊 --- 层间位移角提取 ({', '.join(load_cases)}) ---")

    # --- 0. 基本检查 -----------------------------------------------------
    if not sap_model or not hasattr(sap_model, "Results") or sap_model.Results is None:
        raise RuntimeError("SapModel 结果不可用，无法提取 Story Drift")

    results_api = sap_model.Results
    setup_api = results_api.Setup

    # --- 1. 选择输出工况 --------------------------------------------------
    print("🔧 设置输出工况...")
    check_ret(setup_api.DeselectAllCasesAndCombosForOutput(),
              "Setup.DeselectAllCasesAndCombosForOutput", (0, 1))

    for case in load_cases:
        check_ret(setup_api.SetCaseSelectedForOutput(case),
                  f"Setup.SetCaseSelectedForOutput({case})", (0, 1))

    # 设置相对位移角 (0 = Relative, 1 = Absolute)
    if hasattr(setup_api, "Drift"):
        check_ret(setup_api.Drift(0), "Setup.Drift(Relative)", (0, 1))
        print("✅ 已设置为相对位移角模式")

    # --- 2. 调用 StoryDrifts API -------------------------------------------
    print("🔄 调用 StoryDrifts API...")

    # 初始化参数
    n = System.Int32(0)
    story = System.Array.CreateInstance(System.String, 0)
    case = System.Array.CreateInstance(System.String, 0)
    stepTp = System.Array.CreateInstance(System.String, 0)
    stepNo = System.Array.CreateInstance(System.Double, 0)
    direc = System.Array.CreateInstance(System.String, 0)
    drift = System.Array.CreateInstance(System.Double, 0)
    label = System.Array.CreateInstance(System.String, 0)
    x = System.Array.CreateInstance(System.Double, 0)
    y = System.Array.CreateInstance(System.Double, 0)
    z = System.Array.CreateInstance(System.Double, 0)

    # 兼容不同版本的枚举
    try:
        ITEMTYPE_STORY = ETABSv1.eItemTypeElm.Story
    except AttributeError:
        ITEMTYPE_STORY = 0  # 旧版本 API

    # 尝试不同的API调用方式
    ret = None
    try:
        # 方式1: 带枚举参数
        ret = results_api.StoryDrifts(
            "", ITEMTYPE_STORY,
            n, story, case, stepTp, stepNo,
            direc, drift, label, x, y, z
        )
        print("✅ 使用方式1成功调用StoryDrifts API")
    except TypeError:
        try:
            # 方式2: 不带前两个参数
            ret = results_api.StoryDrifts(
                n, story, case, stepTp, stepNo,
                direc, drift, label, x, y, z
            )
            print("✅ 使用方式2成功调用StoryDrifts API")
        except Exception as e:
            raise RuntimeError(f"StoryDrifts API 调用失败: {e}")

    if ret is None:
        raise RuntimeError("StoryDrifts API 调用失败")

    check_ret(ret[0], "Results.StoryDrifts", (0, 1))

    # 获取返回的数据
    num_results = ret[1]
    story_list = list(ret[2]) if ret[2] is not None else []
    case_list = list(ret[3]) if ret[3] is not None else []
    steptype_list = list(ret[4]) if ret[4] is not None else []
    stepnum_list = list(ret[5]) if ret[5] is not None else []
    direction_list = list(ret[6]) if ret[6] is not None else []
    drift_list = list(ret[7]) if ret[7] is not None else []
    label_list = list(ret[8]) if ret[8] is not None else []
    x_list = list(ret[9]) if ret[9] is not None else []
    y_list = list(ret[10]) if ret[10] is not None else []
    z_list = list(ret[11]) if ret[11] is not None else []

    if num_results == 0:
        print("⚠️ 警告: StoryDrifts 返回 0 条记录")
        print("可能原因：")
        print("  1. 分析未完成或失败")
        print("  2. 选择的工况没有位移结果")
        print("  3. 模型缺少楼层定义")
        return {
            "records": [],
            "max_drift_X": None,
            "max_drift_Y": None,
            "limit_permil": DRIFT_LIMIT_PERMIL,
            "error": "无位移角数据"
        }

    print(f"📋 成功获取 {num_results} 条位移角记录")

    # --- 3. 整理结果 ------------------------------------------------------
    records = []
    max_drift = {"X": (0.0, None), "Y": (0.0, None)}  # 初始化为0.0而不是-1.0

    for i in range(num_results):
        drift_rad = drift_list[i]
        drift_permil = drift_rad * 1000.0  # 转换为‰

        # 确定方向
        dir_raw = direction_list[i].upper().strip()
        if dir_raw in ("U1", "UX", "X"):
            dir_key = "X"
        elif dir_raw in ("U2", "UY", "Y"):
            dir_key = "Y"
        else:
            dir_key = "?"

        rec = {
            "story": story_list[i],
            "load_case": case_list[i],
            "direction": dir_key,
            "drift_permil": round(drift_permil, 4),
            "drift_rad": drift_rad,
            "step_type": steptype_list[i],
            "step_num": stepnum_list[i],
            "label": label_list[i],
            "x": x_list[i],
            "y": y_list[i],
            "z": z_list[i]
        }
        records.append(rec)

        # 记录最大值 - 修复逻辑
        if dir_key in max_drift:
            current_abs = abs(drift_permil)
            stored_abs = abs(max_drift[dir_key][0])
            if current_abs > stored_abs:
                max_drift[dir_key] = (drift_permil, i)

    # --- 4. 打印结果 & 合规性检查 -----------------------------------------
    print(f"\n{'楼层':<15}{'工况/组合':<25}{'方向':<8}{'δ (‰)':>12}")
    print("-" * 60)
    for r in records:
        print(f"{r['story']:<15}{r['load_case']:<25}{r['direction']:<8}{r['drift_permil']:>12.4f}")

    print("\n🎯 ★ 最大层间位移角汇总 ★")
    print("-" * 50)

    max_drift_results = {}

    for axis in ("X", "Y"):
        val, idx = max_drift[axis]
        if idx is None or abs(val) == 0.0:
            print(f"{axis} 方向：无有效数据")
            max_drift_results[f"max_drift_{axis}"] = None
            continue

        abs_val = abs(val)
        is_ok = abs_val <= DRIFT_LIMIT_PERMIL
        status = "✅ 满足规范" if is_ok else "⚠️ 超出限值"

        info = records[idx]
        print(f"{axis} 方向最大: {abs_val:.4f}‰")
        print(f"  位置: {info['story']} 层")
        print(f"  工况: {info['load_case']}")
        print(f"  状态: {status} (限值: {DRIFT_LIMIT_PERMIL}‰)")
        print(f"  原始值: {val:.4f}‰")

        max_drift_results[f"max_drift_{axis}"] = {
            "value_permil": val,
            "abs_value_permil": abs_val,
            "story": info['story'],
            "load_case": info['load_case'],
            "is_ok": is_ok,
            "limit_permil": DRIFT_LIMIT_PERMIL
        }
        print()

    # --- 5. 返回结构化结果 -------------------------------------------------
    result = {
        "records": records,
        "total_records": num_results,
        "load_cases": load_cases,
        "limit_permil": DRIFT_LIMIT_PERMIL,
        **max_drift_results
    }

    # 添加整体评估
    all_ok = all(
        info["is_ok"] for info in max_drift_results.values()
        if info is not None
    )
    result["overall_status"] = "满足规范要求" if all_ok else "存在超限"

    print(f"📊 整体评估: {result['overall_status']}")
    print("--- 层间位移角提取完毕 ---")

    return result


# 为了兼容旧代码，保留原函数名
def extract_story_drifts_improved(sap_model, target_load_cases):
    """
    兼容性函数，调用新的extract_story_drifts函数

    Parameters
    ----------
    sap_model : ETABS SapModel
    target_load_cases : list[str]
        目标工况列表

    Returns
    -------
    dict
        格式化的结果字典
    """
    try:
        result = extract_story_drifts(sap_model, target_load_cases)

        # 转换为旧格式以保持兼容性
        if result.get("error"):
            return {"error": result["error"]}

        # 构造兼容的返回格式
        max_drifts = {}
        for direction in ["X", "Y"]:
            key = f"max_drift_{direction}"
            if result.get(key):
                max_drifts[direction] = {
                    "max_drift": result[key]["abs_value_permil"],
                    "story": result[key]["story"],
                    "load_case": result[key]["load_case"],
                    "raw_drift": result[key]["value_permil"]
                }
            else:
                max_drifts[direction] = None

        return {
            "total_records": result["total_records"],
            "all_drifts": [
                {
                    "story": rec["story"],
                    "load_case": rec["load_case"],
                    "direction": rec["direction"],
                    "drift_rad": rec["drift_rad"],
                    "drift_permil": rec["drift_permil"],
                    "step_type": rec["step_type"],
                    "step_num": rec["step_num"],
                    "label": rec["label"],
                    "x": rec["x"],
                    "y": rec["y"],
                    "z": rec["z"]
                }
                for rec in result["records"]
            ],
            "max_drifts": max_drifts,
            "target_cases": target_load_cases
        }

    except Exception as e:
        print(f"❌ 层间位移角提取失败: {e}")
        traceback.print_exc()
        return {"error": str(e)}