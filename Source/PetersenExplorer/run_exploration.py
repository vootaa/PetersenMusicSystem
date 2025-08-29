"""
PetersenExplorer启动脚本
简化的入口点，用于快速开始探索
"""
import sys
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

from main_explorer import PetersenMainExplorer, ExplorationConfiguration

def main():
    """主函数"""
    print("🎼 PetersenExplorer - Petersen音律系统探索工具")
    print("="*60)
    
    # 简单配置
    config = ExplorationConfiguration(
        f_base_candidates=[220.0],  # 仅测试A3以加快速度
        enable_audio_testing=False,  # 暂时关闭音频测试
        enable_detailed_analysis=True,
        enable_reporting=True,
        max_workers=1,  # 单线程避免复杂性
        min_entries=3,  # 降低要求
        max_entries=30
    )
    
    print("📋 配置信息:")
    print(f"   基频候选: {config.f_base_candidates}")
    print(f"   音符范围: {config.min_entries}-{config.max_entries}")
    print(f"   详细分析: {'✅' if config.enable_detailed_analysis else '❌'}")
    print(f"   音频测试: {'✅' if config.enable_audio_testing else '❌'}")
    print(f"   报告生成: {'✅' if config.enable_reporting else '❌'}")
    
    try:
        # 创建探索器
        explorer = PetersenMainExplorer(config)
        
        # 运行探索
        print("\n🚀 开始探索...")
        summary = explorer.run_complete_exploration()
        
        # 显示结果
        print("\n📊 探索完成!")
        if summary.get('status') == 'completed':
            stats = summary['statistics']
            print(f"   成功生成: {stats['successful_systems']} 个音律系统")
            print(f"   分析完成: {stats['analyzed_systems']} 个系统")
            print(f"   处理时间: {summary['duration']:.1f} 秒")
            
            # 显示顶级系统
            top_systems = explorer.get_top_systems(5)
            if top_systems:
                print("\n🏆 前5名音律系统:")
                for i, (result, evaluation, classification) in enumerate(top_systems, 1):
                    params = result.parameters
                    score = evaluation.weighted_total_score if evaluation else 0
                    category = classification.primary_category.value if classification else "未分类"
                    print(f"   {i}. {params.phi_name} × {params.delta_theta_name}")
                    print(f"      评分: {score:.3f}, 类别: {category}")
                    print(f"      音符数: {len(result.entries)}")
        else:
            print(f"   探索状态: {summary.get('status', '未知')}")
            if 'error' in summary:
                print(f"   错误信息: {summary['error']}")
        
        print("\n✅ 探索流程完成!")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断探索")
    except Exception as e:
        print(f"\n❌ 探索过程中发生错误:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()