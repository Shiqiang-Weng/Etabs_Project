# SRC/Etabs_projects/results/design_manager_GB.py

import pandas as pd
import json


class DesignManagerGB:
    """
    通过调用ETABS API来管理和执行基于中国规范的混凝土设计。
    """

    def __init__(self, sap_model):
        self.sap_model = sap_model
        self.d_concrete = sap_model.DesignConcrete
        self.design_results = []

    def setup_design(self, design_code="GB 50010-2010"):
        """
        设置设计规范并选择用于设计的荷载组合。
        """
        # 1. 设置设计规范
        self.d_concrete.SetCode(design_code)
        print(f"成功设置混凝土设计规范为: {design_code}")

        # 2. 自动选择所有以 "ULS" 开头的组合进行设计
        all_combos = self.sap_model.RespCombo.GetNameList()[1]
        for combo_name in all_combos:
            if combo_name.startswith("ULS"):
                self.d_concrete.SetComboSelected(True, combo_name)
                print(f"已选择组合 '{combo_name}' 用于设计。")

    def run_concrete_design(self):
        """
        启动ETABS内置的混凝土设计。
        """
        print("开始运行ETABS混凝土设计...")
        result = self.d_concrete.StartDesign()
        if result == 0:
            print("ETABS混凝土设计完成。")
        else:
            print(f"ETABS混凝土设计失败，错误码: {result}")
            raise Exception("ETABS design check failed.")

    def get_design_summary(self):
        """
        从ETABS中提取所有框架构件的设计结果摘要。
        """
        frame_names = self.sap_model.FrameObj.GetNameList()[1]

        for frame in frame_names:
            # 获取构件的设计结果
            # 返回值格式: (Name, PMMRatio, VMajorRatio, VMinorRatio, AsTotal, ShearRebar, Error, Warning)
            summary = self.d_concrete.GetSummaryResults(frame)

            design_info = {
                "FrameName": summary[0],
                "PMM_Ratio": f"{summary[1]:.3f}",  # 轴力弯矩设计比（应力比）
                "V_Ratio": f"{summary[2]:.3f}",  # 主向剪力比
                "Total_As_Required_mm2": f"{summary[4]:.2f}",  # 总纵筋面积 (mm^2)
                "Shear_Rebar_Av_s_mm2_m": f"{summary[5]:.2f}",  # 箍筋需求 (mm^2/m)
                "Error": summary[6],
                "Warning": summary[7]
            }
            self.design_results.append(design_info)

        return self.design_results

    def save_results(self, output_path="results_output/etabs_design_summary_GB"):
        """
        将设计结果保存为 JSON 和 Excel 文件。
        """
        if not self.design_results:
            print("没有设计结果可保存。")
            return

        # 保存为 JSON
        json_path = f"{output_path}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.design_results, f, indent=4, ensure_ascii=False)
        print(f"设计结果已保存到: {json_path}")

        # 保存为 Excel
        excel_path = f"{output_path}.xlsx"
        df = pd.DataFrame(self.design_results)
        df.to_excel(excel_path, index=False)
        print(f"设计结果已保存到: {excel_path}")