"""
PetersenExplorer - Petersen音律系统全面探索工具包

这个包提供了完整的Petersen音律系统探索、分析、评估和验证功能。

主要模块:
- core: 核心探索和分析引擎
- audio: 音频播放测试功能
- reporting: 报告生成和可视化

使用示例:
    from PetersenExplorer import quick_exploration, PetersenMainExplorer
    
    # 快速探索
    summary = quick_exploration()
    
    # 详细探索
    explorer = PetersenMainExplorer()
    result = explorer.run_complete_exploration()
"""

__version__ = "1.0.0"
__author__ = "PetersenMusicSystem Development Team"

# 导入主要类和函数 - 容错版本
try:
    from .main_explorer import (
        PetersenMainExplorer,
        ExplorationConfiguration,
        quick_exploration
    )
    MAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 主模块导入失败: {e}")
    MAIN_AVAILABLE = False

try:
    from .core.parameter_explorer import (
        ParameterSpaceExplorer,
        ExplorationParameters,
        ExplorationResult
    )
except ImportError:
    pass

from .core.evaluation_framework import (
    MultiDimensionalEvaluator,
    ComprehensiveEvaluation,
    EvaluationDimension
)

from .core.classification_system import (
    OpenClassificationSystem,
    ClassificationResult,
    PrimaryCategory
)

from .audio.playback_tester import (
    PetersenPlaybackTester,
    SystemPlaybackAssessment,
    PlaybackTestType
)

from .audio.musicality_validator import (
    PetersenMusicalityValidator,
    MusicalityValidationResult,
    MusicalContext
)

from .reporting.report_generator import (
    PetersenExplorationReportGenerator
)

# 便捷导入别名
Explorer = PetersenMainExplorer
Config = ExplorationConfiguration
quick_explore = quick_exploration

if MAIN_AVAILABLE:
    Explorer = PetersenMainExplorer
    Config = ExplorationConfiguration
    quick_explore = quick_exploration
else:
    Explorer = None
    Config = None
    quick_explore = None

__all__ = [
    # 主要类
    'PetersenMainExplorer', 'Explorer',
    'ExplorationConfiguration', 'Config',
    'ParameterSpaceExplorer',
    'MultiDimensionalEvaluator',
    'OpenClassificationSystem',
    'PetersenPlaybackTester',
    'PetersenExplorationReportGenerator',
    
    # 数据类
    'ExplorationParameters',
    'ExplorationResult', 
    'ComprehensiveEvaluation',
    'ClassificationResult',
    'SystemPlaybackAssessment',
    
    # 枚举
    'EvaluationDimension',
    'PrimaryCategory', 
    'PlaybackTestType',
    
    # 便捷函数
    'quick_exploration', 'quick_explore',
    'explore_specific_presets'
]

# 包级别配置
DEFAULT_CONFIG = ExplorationConfiguration(
    f_base_candidates=[110.0, 146.83, 220.0, 261.63, 293.66],
    f_min=110.0,
    f_max=880.0,
    min_entries=5,
    max_entries=60,
    enable_audio_testing=True,
    enable_detailed_analysis=True,
    enable_reporting=True,
    max_workers=4,
    audio_test_sample_size=20
)

def get_version_info():
    """获取版本信息"""
    return {
        'version': __version__,
        'author': __author__,
        'description': 'Petersen音律系统全面探索工具包'
    }

def print_welcome():
    """打印欢迎信息"""
    print("🎼" + "="*58 + "🎼")
    print("   PetersenExplorer - Petersen音律系统探索工具包")
    print(f"   版本: {__version__}")
    print("   开放性原则：多样性、潜力、创新性、适应性")
    print("🎼" + "="*58 + "🎼")

# 包初始化时的欢迎信息（可选）
if __name__ != "__main__":
    import os
    if os.environ.get("PETERSEN_EXPLORER_WELCOME", "1") == "1":
        print_welcome()