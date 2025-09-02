#!/usr/bin/env python3
"""基于实际文件结构的测试"""

import sys
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(current_dir))

def test_core_imports():
    """测试核心模块导入"""
    print("🔍 测试核心模块导入...")
    
    try:
        from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
        print("✅ PetersenScale_Phi 导入成功")
    except Exception as e:
        print(f"❌ PetersenScale_Phi 导入失败: {e}")
        return False
    
    try:
        from core.evaluation_framework import MultiDimensionalEvaluator, EvaluationDimension
        print("✅ 评估框架导入成功")
    except Exception as e:
        print(f"❌ 评估框架导入失败: {e}")
        return False
    
    try:
        from core.classification_system import OpenClassificationSystem, PrimaryCategory
        print("✅ 分类系统导入成功")
    except Exception as e:
        print(f"❌ 分类系统导入失败: {e}")
        return False
    
    try:
        from core.parameter_explorer import ParameterSpaceExplorer
        print("✅ 参数探索器导入成功")
    except Exception as e:
        print(f"❌ 参数探索器导入失败: {e}")
        return False
    
    return True

def test_audio_modules():
    """测试音频模块"""
    print("\n🔍 测试音频模块...")
    
    try:
        from audio.playback_tester import ENHANCED_PLAYER_AVAILABLE
        if ENHANCED_PLAYER_AVAILABLE:
            print("✅ 音频模块可用")
        else:
            print("⚠️ 音频模块不可用，将跳过音频验证")
        return True
    except Exception as e:
        print(f"⚠️ 音频模块测试异常: {e}")
        return True  # 音频模块是可选的

def test_main_system():
    """测试主系统"""
    print("\n🔍 测试主系统...")
    
    try:
        from main_explorer import ExplorationConfiguration, PetersenMainExplorer
        
        config = ExplorationConfiguration(
            f_base_candidates=[220.0],
            enable_audio_testing=False,
            enable_detailed_analysis=True,
            max_workers=1
        )
        
        explorer = PetersenMainExplorer(config)
        print("✅ 主探索器创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 主系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎼 PetersenExplorer 实际结构测试")
    print("=" * 50)
    
    all_passed = True
    
    if not test_core_imports():
        all_passed = False
    
    if not test_audio_modules():
        all_passed = False
    
    if not test_main_system():
        all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！系统已修复")
        sys.exit(0)
    else:
        print("\n❌ 测试失败，需要进一步修复")
        sys.exit(1)