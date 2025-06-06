# -*- coding: utf-8 -*-
"""
核心模块
包含ETABS API连接、模型构建和异常处理
"""

from .api_connector import ETABSConnector
from .model_builder import ETABSModelBuilder
from .exceptions import *

__all__ = [
    # 连接器
    'ETABSConnector',

    # 模型构建器
    'ETABSModelBuilder',

    # 异常类
    'ETABSError', 'ETABSConnectionError', 'ETABSAPIError', 'ETABSModelError',
    'ETABSAnalysisError', 'ETABSResultsError', 'ETABSGeometryError',
    'ETABSMaterialError', 'ETABSLoadError', 'DotNetLoadError', 'ConfigurationError'
]