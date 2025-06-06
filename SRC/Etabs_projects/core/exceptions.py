# -*- coding: utf-8 -*-
"""
自定义异常类
定义ETABS自动化过程中可能出现的各种异常
"""


class ETABSError(Exception):
    """ETABS相关错误的基类"""
    pass


class ETABSConnectionError(ETABSError):
    """ETABS连接错误"""
    pass


class ETABSAPIError(ETABSError):
    """ETABS API调用错误"""
    def __init__(self, message: str, api_function: str = "", return_code: int = None):
        super().__init__(message)
        self.api_function = api_function
        self.return_code = return_code


class ETABSModelError(ETABSError):
    """ETABS模型错误"""
    pass


class ETABSAnalysisError(ETABSError):
    """ETABS分析错误"""
    pass


class ETABSResultsError(ETABSError):
    """ETABS结果提取错误"""
    pass


class ETABSGeometryError(ETABSError):
    """ETABS几何创建错误"""
    pass


class ETABSMaterialError(ETABSError):
    """ETABS材料定义错误"""
    pass


class ETABSLoadError(ETABSError):
    """ETABS荷载定义错误"""
    pass


class DotNetLoadError(ETABSError):
    """
    .NET运行时加载错误
    """
    pass


class ConfigurationError(ETABSError):
    """
    配置错误
    """
    pass