#!/usr/bin/env python3
"""测试修复后的系统"""

import sys
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(current_dir))

def test_imports():
    """测试所有导入"""
    print("🔍 测试导入...")
    
    try:
        from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
        print("✅ PetersenScale_Phi 导入成功")
    except Exception as e:
        print(f"❌ PetersenScale_Phi 导入失败: {e}")
        return False
    
    try:
        from core.evaluation_framework import MultiDimensionalEvaluator, EvaluationScore, DimensionScore
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
        from main_explorer import PetersenMainExplorer, ExplorationConfiguration
        print("✅ 主探索器导入成功")
    except Exception as e:
        print(f"❌ 主探索器导入失败: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        from main_explorer import ExplorationConfiguration, PetersenMainExplorer
        
        config = ExplorationConfiguration(
            f_base_candidates=[220.0],
            enable_audio_testing=False,
            enable_detailed_analysis=True,
            max_workers=1
        )
        
        explorer = PetersenMainExplorer(config)
        print("✅ 探索器创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎼 PetersenExplorer 修复验证")
    print("="*50)
    
    if test_imports() and test_basic_functionality():
        print("\n🎉 所有测试通过！系统已修复")
        sys.exit(0)
    else:
        print("\n❌ 测试失败，需要进一步修复")
        sys.exit(1)