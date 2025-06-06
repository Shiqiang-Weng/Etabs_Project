# -*- coding: utf-8 -*-
"""
荷载模式定义模块
"""

from utils import check_ret, get_etabs_modules


def ensure_dead_pattern(sap_model):
    """
    确保恒荷载模式存在

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        raise ValueError("SapModel未初始化")

    lp = sap_model.LoadPatterns

    # 添加恒荷载模式
    check_ret(
        lp.Add("DEAD", ETABSv1.eLoadPatternType.Dead, 1.0, True),
        "LoadPatterns.Add(DEAD)",
        (0, 1)
    )

    # 设置自重系数
    check_ret(
        lp.SetSelfWTMultiplier("DEAD", 1.0),
        "SetSelfWTMultiplier(DEAD)",
        (0, 1)
    )

    print("✅ DEAD 荷载模式已确保存在")


def ensure_live_pattern(sap_model):
    """
    确保活荷载模式存在

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        raise ValueError("SapModel未初始化")

    lp = sap_model.LoadPatterns

    # 添加活荷载模式
    ret = lp.Add("LIVE", ETABSv1.eLoadPatternType.Live, 0.0, True)
    check_ret(ret, "LoadPatterns.Add(LIVE)", (0, 1))

    if ret == 0:
        print("✅ 荷载模式 'LIVE' 已成功添加")


def define_static_load_cases(sap_model):
    """
    定义静力荷载工况

    Parameters:
        sap_model: ETABS SapModel对象
    """
    from utils import arr

    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        raise ValueError("SapModel未初始化")

    static_lc = sap_model.LoadCases.StaticLinear

    for pattern in ["DEAD", "LIVE"]:
        # 设置工况
        check_ret(
            static_lc.SetCase(pattern),
            f"StaticLinear.SetCase({pattern})",
            (0, 1)
        )

        # 设置荷载
        check_ret(
            static_lc.SetLoads(
                pattern,
                1,
                arr(["Load"], System.String),
                arr([pattern], System.String),
                arr([1.0])
            ),
            f"StaticLinear.SetLoads({pattern})"
        )

    print("✅ 静力荷载工况定义完毕")


def define_all_load_patterns(sap_model):
    """
    定义所有荷载模式

    Parameters:
        sap_model: ETABS SapModel对象
    """
    print("\n⚖️ 开始定义荷载模式...")

    ensure_dead_pattern(sap_model)
    ensure_live_pattern(sap_model)
    define_static_load_cases(sap_model)

    print("✅ 所有荷载模式定义完成")