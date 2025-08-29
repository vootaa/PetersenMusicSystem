"""
简单的测试脚本，验证基础功能
"""
import sys
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

def test_basic_imports():
    """测试基础导入"""
    print("🔧 测试基础导入...")
    
    try:
        from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
        print("✅ PetersenScale_Phi 导入成功")
        
        print(f"📊 可用φ预设: {len(PHI_PRESETS)}")
        print(f"📊 可用δθ预设: {len(DELTA_THETA_PRESETS)}")
        
        # 测试创建音阶
        scale = PetersenScale_Phi(F_base=220.0, delta_theta=4.8, phi=1.618)
        entries = scale.generate()
        print(f"✅ 测试音阶生成成功: {len(entries)} 个音符")
        
        return True
        
    except Exception as e:
        print(f"❌ 基础导入失败: {e}")
        return False

def test_petersen_explorer():
    """测试PetersenExplorer基础功能"""
    print("\n🚀 测试PetersenExplorer...")
    
    try:
        from main_explorer import PetersenMainExplorer, ExplorationConfiguration
        print("✅ 主探索器导入成功")
        
        # 创建简单配置
        config = ExplorationConfiguration(
            f_base_candidates=[220.0],
            enable_audio_testing=False,
            enable_detailed_analysis=False,  # 暂时关闭详细分析
            enable_reporting=False,
            min_entries=1,
            max_entries=50
        )
        
        print("✅ 配置创建成功")
        
        # 创建探索器
        explorer = PetersenMainExplorer(config)
        print("✅ 探索器创建成功")
        
        # 运行简化探索
        print("\n📡 开始简化探索...")
        summary = explorer.run_complete_exploration()
        
        print(f"\n📋 探索结果:")
        print(f"   状态: {summary.get('status', '未知')}")
        print(f"   处理系统: {summary.get('statistics', {}).get('total_combinations', 0)}")
        print(f"   成功系统: {summary.get('statistics', {}).get('successful_systems', 0)}")
        print(f"   耗时: {summary.get('duration', 0):.1f} 秒")
        
        return True
        
    except Exception as e:
        print(f"❌ PetersenExplorer测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🎼 PetersenExplorer 基础功能测试")
    print("=" * 50)
    
    # 测试基础导入
    if not test_basic_imports():
        print("\n❌ 基础功能测试失败，请检查PetersenScale_Phi模块")
        return
    
    # 测试探索器
    if not test_petersen_explorer():
        print("\n❌ 探索器测试失败")
        return
    
    print("\n✅ 所有基础测试通过！")
    print("🎉 PetersenExplorer 基础功能正常")

if __name__ == "__main__":
    main()