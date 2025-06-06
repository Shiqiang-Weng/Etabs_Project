# -*- coding: utf-8 -*-
"""
结果模块
包含所有分析结果的提取功能
"""

from .modal_results import extract_modal_and_mass_info
from .drift_results import extract_story_drifts_improved
from .frame_forces import extract_frame_forces_main

def extract_all_results(sap_model):
    """
    提取所有分析结果的主接口

    Parameters:
        sap_model: ETABS SapModel对象

    Returns:
        dict: 所有结果信息
    """
    print("\n📊 开始提取所有分析结果...")

    all_results = {}

    # 1. 提取模态信息和质量参与系数
    print("\n🔍 提取模态信息和质量参与系数...")
    all_results['modal'] = extract_modal_and_mass_info(sap_model)

    # 2. 提取层间位移角
    print("\n🔍 提取层间位移角...")
    drift_cases = ["RS-X", "RS-Y"]
    all_results['drift'] = extract_story_drifts_improved(sap_model, drift_cases)

    # 3. 提取框架内力
    try:
        from config import ENABLE_FRAME_COLUMNS, ENABLE_FRAME_BEAMS, STRUCTURE_TYPE

        if (ENABLE_FRAME_COLUMNS or ENABLE_FRAME_BEAMS) and STRUCTURE_TYPE == "FRAME":
            print("\n🔍 提取框架构件内力...")
            frame_load_cases = ["DEAD", "LIVE", "RS-X", "RS-Y"]
            forces_df, forces_summary = extract_frame_forces_main(
                sap_model,
                output_path="./results_output",
                load_cases=frame_load_cases
            )
            all_results['frame_forces'] = {
                'data_records': len(forces_df) if not forces_df.empty else 0,
                'summary': forces_summary,
                'extracted_cases': frame_load_cases
            }
        else:
            print("⏭️ 跳过框架内力提取（非框架结构）")
            all_results['frame_forces'] = {'skipped': '非框架结构'}

    except ImportError:
        print("⚠️ 无法获取结构类型配置，跳过框架内力提取")
        all_results['frame_forces'] = {'error': '配置不可用'}

    # --- 输出结果汇总 ---
    print("\n📋 === 结果提取汇总 ===")

    # ... (existing summary printouts for modal and drift)

    # New summary for story shear and mass
    if 'story_data' in all_results:
        story_info = all_results['story_data']
        if 'story_forces' in story_info and not story_info['story_forces'].empty:
            print(f"✅ 楼层剪力: 成功提取 {len(story_info['story_forces'])} 条记录")
        else:
            print("❌ 楼层剪力: 未提取到数据")

        if 'story_mass' in story_info and not story_info['story_mass'].empty:
            print(f"✅ 楼层质量: 成功提取 {len(story_info['story_mass'])} 条记录")
        else:
            print("❌ 楼层质量: 未提取到数据")

    # ... (existing summary printout for frame forces)

    print("======================")
    print("✅ 所有结果提取完成")

    return all_results


__all__ = [
    'extract_all_results',
    'extract_modal_and_mass_info',
    'extract_story_drifts_improved',
    'extract_frame_forces_main',
]