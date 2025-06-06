# -*- coding: utf-8 -*-
"""
框架内力提取模块 - 修复版本 v2.1
用于提取ETABS框架构件（柱、梁）内力
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import traceback
import os

from utils import get_etabs_modules, check_ret


class FrameForcesExtractor:
    """
    用于提取ETABS框架构件（柱、梁）内力的类 - 修复版本 v2.1
    """

    def __init__(self, etabs_model):
        """
        初始化提取器

        Args:
            etabs_model: ETABS SapModel 对象
        """
        self.SapModel = etabs_model
        self.ETABSv1, self.System, self.COMException = get_etabs_modules()

        if not all([self.ETABSv1, self.System]):
            raise RuntimeError("ETABS API模块未正确加载")

    def get_all_frame_elements(self) -> Dict[str, List[str]]:
        """
        获取所有框架构件的名称 (基于名称模式)
        """
        if not hasattr(self.SapModel, 'FrameObj') or not self.SapModel.FrameObj:
            print("❌ 错误: FrameObj不可用")
            return {'columns': [], 'beams': [], 'all_frames': []}

        try:
            num_val = self.System.Int32(0)
            names_val = self.System.Array[self.System.String](0)
            ret_tuple = self.SapModel.FrameObj.GetNameList(num_val, names_val)
            check_ret(ret_tuple[0], "FrameObj.GetNameList")

            all_frames = list(ret_tuple[2]) if ret_tuple[1] > 0 and ret_tuple[2] is not None else []
            columns = [name for name in all_frames if "COL_" in name.upper()]
            beams = [name for name in all_frames if "BEAM_" in name.upper()]

            print(f"✅ 构件分类完成: {len(columns)} 根柱, {len(beams)} 根梁")
            return {'columns': columns, 'beams': beams, 'all_frames': all_frames}

        except Exception as e:
            print(f"❌ 获取框架构件列表失败: {e}")
            return {'columns': [], 'beams': [], 'all_frames': []}

    def _prepare_output_params(self) -> tuple:
        """准备用于FrameForce API调用的输出参数"""
        return (
            self.System.Int32(0),  # NumberResults
            self.System.Array[self.System.String](0),  # Obj
            self.System.Array[self.System.Double](0),  # ObjSta
            self.System.Array[self.System.String](0),  # Elm
            self.System.Array[self.System.Double](0),  # ElmSta
            self.System.Array[self.System.String](0),  # LoadCase
            self.System.Array[self.System.String](0),  # StepType
            self.System.Array[self.System.Double](0),  # StepNum
            self.System.Array[self.System.Double](0),  # P
            self.System.Array[self.System.Double](0),  # V2
            self.System.Array[self.System.Double](0),  # V3
            self.System.Array[self.System.Double](0),  # T
            self.System.Array[self.System.Double](0),  # M2
            self.System.Array[self.System.Double](0),  # M3
        )

    def extract_all_frame_forces(self, load_cases_to_extract: List[str]) -> pd.DataFrame:
        """
        提取所有框架构件在指定工况下的内力
        """
        # 1. 设置结果输出工况
        setup = self.SapModel.Results.Setup
        setup.DeselectAllCasesAndCombosForOutput()
        for case in load_cases_to_extract:
            ret = setup.SetCaseSelectedForOutput(case)
            check_ret(ret, f"SetCaseSelectedForOutput({case})", (0, 1))

        # 2. 获取所有框架构件
        frame_elements = self.get_all_frame_elements()
        all_frames = frame_elements.get('all_frames', [])
        if not all_frames:
            return pd.DataFrame()

        # 3. 提取内力
        all_forces_data = []
        print(f"📊 开始提取 {len(all_frames)} 个框架构件的内力...")

        for i, frame_name in enumerate(all_frames):
            params = self._prepare_output_params()
            try:
                ret_tuple = self.SapModel.Results.FrameForce(frame_name, self.ETABSv1.eItemTypeElm.ObjectElm, *params)

                if ret_tuple[0] in (0, 1) and ret_tuple[1] > 0:
                    num_results = ret_tuple[1]
                    # Unpack all results
                    _, _, obj_names, obj_stas, elm_names, elm_stas, load_cases, step_types, step_nums, p, v2, v3, t, m2, m3 = ret_tuple

                    for j in range(num_results):
                        all_forces_data.append({
                            'Frame_Name': obj_names[j],
                            'Element_Type': 'Column' if obj_names[j] in frame_elements['columns'] else 'Beam',
                            'Load_Case_Combo': load_cases[j],
                            'Distance_Station': obj_stas[j],
                            'Axial_Force_P': p[j],
                            'Shear_V2': v2[j],
                            'Shear_V3': v3[j],
                            'Torsion_T': t[j],
                            'Moment_M2': m2[j],
                            'Moment_M3': m3[j]
                        })
            except Exception as e:
                print(f"⚠️ 构件 {frame_name} 内力提取失败: {e}")

            if (i + 1) % 50 == 0:
                print(f"  ...已处理 {i + 1}/{len(all_frames)} 构件")

        print(f"✅ 内力提取完成，共 {len(all_forces_data)} 条记录")
        return pd.DataFrame(all_forces_data)

    def get_max_forces_by_element(self, df: pd.DataFrame) -> pd.DataFrame:
        """按构件统计最大内力"""
        if df.empty:
            return pd.DataFrame()

        max_forces = df.groupby(['Frame_Name', 'Element_Type', 'Load_Case_Combo']).agg(
            P_max=('Axial_Force_P', 'max'),
            P_min=('Axial_Force_P', 'min'),
            V2_max=('Shear_V2', lambda x: x.abs().max()),
            V3_max=('Shear_V3', lambda x: x.abs().max()),
            T_max=('Torsion_T', lambda x: x.abs().max()),
            M2_max=('Moment_M2', lambda x: x.abs().max()),
            M3_max=('Moment_M3', lambda x: x.abs().max()),
        ).round(2).reset_index()
        return max_forces

    def export_forces_to_excel(self, df: pd.DataFrame, filename: str):
        """导出内力数据到Excel"""
        if df.empty:
            print(f"⚠️ 数据为空，未导出到 Excel 文件: {filename}")
            return

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detailed_Forces', index=False)
            max_forces_df = self.get_max_forces_by_element(df)
            if not max_forces_df.empty:
                max_forces_df.to_excel(writer, sheet_name='Max_Forces_Summary', index=False)
        print(f"✅ 内力数据已导出到: {filename}")

    def create_forces_summary_report(self, df: pd.DataFrame) -> Dict:
        """创建内力汇总报告"""
        if df.empty:
            return {'error': 'No data'}

        return {
            'total_elements': len(df['Frame_Name'].unique()),
            'columns_count': len(df[df['Element_Type'] == 'Column']['Frame_Name'].unique()),
            'beams_count': len(df[df['Element_Type'] == 'Beam']['Frame_Name'].unique()),
            'total_records': len(df),
        }


def extract_frame_forces_main(sap_model, output_path: str = "./results_output",
                              load_cases: list = None) -> tuple:
    """
    提取框架内力的主接口函数
    """
    if load_cases is None:
        load_cases = ["DEAD", "LIVE", "RS-X", "RS-Y"]

    try:
        print("🔍 开始提取框架构件内力...")
        extractor = FrameForcesExtractor(sap_model)

        forces_df = extractor.extract_all_frame_forces(load_cases)

        if forces_df.empty:
            print("⚠️ 未提取到内力数据")
            return pd.DataFrame(), {"error": "无内力数据"}

        excel_filename = os.path.join(output_path, "frame_forces_analysis.xlsx")
        extractor.export_forces_to_excel(forces_df, excel_filename)

        summary_report = extractor.create_forces_summary_report(forces_df)
        summary_filename = os.path.join(output_path, "forces_summary_report.json")
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, indent=2, ensure_ascii=False)
        print(f"📊 汇总报告已保存: {summary_filename}")

        return forces_df, summary_report

    except Exception as e:
        print(f"❌ 框架内力提取失败: {e}")
        traceback.print_exc()
        return pd.DataFrame(), {"error": str(e)}