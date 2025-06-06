# SRC/Etabs_projects/loads/load_combinations_GB.py

def get_uls_combinations_gb():
    """
    定义基于 GB 50010-2010 的承载能力极限状态（ULS）荷载组合的“配方”。
    注意：这里仅为示例，实际项目中需要根据地震、风荷载等情况进行扩充。
    """
    combinations = [
        # 组合名称, 荷载工况, 比例因子
        {'name': 'ULS-1', 'case': 'DEAD', 'factor': 1.2},
        {'name': 'ULS-1', 'case': 'LIVE', 'factor': 1.4},

        {'name': 'ULS-2', 'case': 'DEAD', 'factor': 1.2},
        {'name': 'ULS-2', 'case': 'LIVE', 'factor': 0.7},
        {'name': 'ULS-2', 'case': 'WIND-X', 'factor': 1.4},  # 假设有风荷载

        {'name': 'ULS-3', 'case': 'DEAD', 'factor': 1.0},
        {'name': 'ULS-3', 'case': 'WIND-X', 'factor': 1.4},

        # ... 此处可以添加更多组合，例如考虑地震作用的组合
        # 例如：
        # {'name': 'ULS-EQX', 'case': 'DEAD', 'factor': 1.2},
        # {'name': 'ULS-EQX', 'case': 'LIVE', 'factor': 1.0},
        # {'name': 'ULS-EQX', 'case': 'EQX', 'factor': 1.3},
    ]
    return combinations


def create_load_combinations_in_etabs(sap_model, combinations_data):
    """
    使用API在ETABS模型中创建荷载组合。

    :param sap_model: ETABS模型对象
    :param combinations_data: 从 get_uls_combinations_gb() 获取的组合定义
    """
    combo_api = sap_model.RespCombo

    # 将数据按组合名称分组
    from collections import defaultdict
    grouped_combos = defaultdict(list)
    for combo in combinations_data:
        grouped_combos[combo['name']].append((combo['case'], combo['factor']))

    for combo_name, cases in grouped_combos.items():
        # 添加一个新的线性相加（Linear Add）类型的组合
        combo_api.Add(combo_name, 0)  # 0 for Linear Add type

        # 为该组合添加荷载工况和系数
        for case_name, factor in cases:
            combo_api.SetCaseList(combo_name, 0, case_name, factor)  # eCNameType = 0 for LoadCase
        print(f"成功在ETABS中创建荷载组合: {combo_name}")