# SRC/Etabs_projects/main.py (完整修改)

from Etabs_projects.core.api_connector import ApiConnector
from Etabs_projects.core.model_builder import ModelBuilder
from Etabs_projects.loads.load_patterns import define_load_patterns
from Etabs_projects.loads.dead_live_loads import apply_dead_and_live_loads
# 新增导入
from Etabs_projects.loads.load_combinations_GB import get_uls_combinations_gb, create_load_combinations_in_etabs
from Etabs_projects.analysis.analysis_runner import AnalysisRunner
# 新增导入
from Etabs_projects.results.design_manager_GB import DesignManagerGB


def main():
    # --- 1. 连接到ETABS ---
    connector = ApiConnector()
    sap_model = connector.get_sap_model()

    # --- 2. 建模 (假设已完成) ---
    # builder = ModelBuilder(sap_model)
    # builder.build_model()
    # ...

    # --- 3. 定义和施加荷载 ---
    # 定义荷载工况
    define_load_patterns(sap_model)
    # 施加重力荷载
    apply_dead_and_live_loads(sap_model)

    # ****** 新增：创建中国规范荷载组合 ******
    print("\n--- 创建荷载组合 ---")
    combo_recipes = get_uls_combinations_gb()
    create_load_combinations_in_etabs(sap_model, combo_recipes)

    # --- 4. 运行分析 ---
    print("\n--- 运行结构分析 ---")
    analysis_runner = AnalysisRunner(sap_model)
    analysis_runner.run_analysis()

    # --- 5. ****** 新增：运行中国规范配筋设计 ****** ---
    print("\n--- 运行中国规范混凝土设计 ---")
    try:
        # 初始化设计管理器
        design_manager = DesignManagerGB(sap_model)
        # 设置规范并选择组合
        design_manager.setup_design()
        # 运行设计
        design_manager.run_concrete_design()
        # 获取并保存结果
        design_manager.get_design_summary()
        design_manager.save_results()
        print("配筋设计和结果导出完成。")
    except Exception as e:
        print(f"配筋设计过程中发生错误: {e}")

    # --- 6. 结束 ---
    connector.release_etabs()
    print("\n流程结束。")


if __name__ == "__main__":
    main()