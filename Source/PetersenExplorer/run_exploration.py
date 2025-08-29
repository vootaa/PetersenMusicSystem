#!/usr/bin/env python3
"""
PetersenExplorer统一执行入口
一键启动完整的音律探索系统
"""
import sys
import time
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(current_dir))

from main_explorer import PetersenMainExplorer, ExplorationConfiguration

def main():
    """主执行函数"""
    print("🎼" + "="*60 + "🎼")
    print("   PetersenExplorer - 完整音律探索系统")
    print("   开放性原则：多样性、潜力、创新性、适应性")
    print("🎼" + "="*60 + "🎼")
    
    # 配置探索参数
    config = ExplorationConfiguration(
        f_base_candidates=[110.0, 220.0, 261.63, 293.66],  # A2, A3, C4, D4
        f_min=110.0,
        f_max=880.0,
        min_entries=5,
        max_entries=200,  # 调整以适应实际生成数量
        enable_detailed_analysis=True,
        enable_audio_testing=False,  # 可根据需要开启
        enable_reporting=True,
        max_workers=2,
        report_name=f"petersen_exploration_{int(time.time())}"
    )
    
    print(f"\n📋 探索配置:")
    print(f"   基频候选: {config.f_base_candidates}")
    print(f"   频率范围: {config.f_min}-{config.f_max} Hz")
    print(f"   音符范围: {config.min_entries}-{config.max_entries}")
    print(f"   详细分析: {'开启' if config.enable_detailed_analysis else '关闭'}")
    print(f"   音频测试: {'开启' if config.enable_audio_testing else '关闭'}")
    print(f"   报告生成: {'开启' if config.enable_reporting else '关闭'}")
    
    try:
        # 创建并运行探索器
        explorer = PetersenMainExplorer(config)
        summary = explorer.run_complete_exploration()
        
        # 显示结果摘要
        print(f"\n🎉 探索完成!")
        print(f"   状态: {summary.get('status', '未知')}")
        print(f"   处理时间: {summary.get('duration', 0):.1f} 秒")
        
        if summary.get('statistics'):
            stats = summary['statistics']
            print(f"   测试系统: {stats.get('total_combinations', 0)}")
            print(f"   成功系统: {stats.get('successful_systems', 0)}")
            print(f"   分析系统: {stats.get('analyzed_systems', 0)}")
            print(f"   成功率: {stats.get('success_rate', 0):.1%}")
        
        # 显示顶级系统
        if summary.get('top_systems'):
            print(f"\n🏆 发现的优秀音律系统:")
            for i, system in enumerate(summary['top_systems'][:5], 1):
                print(f"   {i}. {system['phi_name']} × {system['delta_theta_name']} "
                      f"(评分: {system['score']:.3f})")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断探索")
        return False
    except Exception as e:
        print(f"\n❌ 探索失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)