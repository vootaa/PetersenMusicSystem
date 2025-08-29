"""
PetersenExplorer演示脚本
展示如何使用PetersenExplorer进行各种类型的音律探索
"""

import sys
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from PetersenExplorer import (
    PetersenMainExplorer, ExplorationConfiguration,
    quick_exploration, explore_specific_presets,
    print_welcome
)

def demo_quick_exploration():
    """演示快速探索功能"""
    print("\n🚀 演示1: 快速探索")
    print("="*50)
    
    # 使用默认配置进行快速探索
    print("执行快速探索（使用默认配置）...")
    
    summary = quick_exploration(
        f_base_list=[220.0, 261.63],  # 只测试两个基频
        enable_audio=False  # 演示模式关闭音频测试
    )
    
    print(f"✅ 快速探索完成")
    print(f"   状态: {summary['status']}")
    print(f"   测试组合: {summary['statistics']['total_combinations']}")
    print(f"   成功系统: {summary['statistics']['successful_systems']}")
    print(f"   耗时: {summary['duration']:.1f}秒")

def demo_specific_presets():
    """演示特定预设探索"""
    print("\n🎯 演示2: 特定预设探索")
    print("="*50)
    
    # 探索特定的φ和δθ组合
    phi_names = ["golden", "silver", "bronze"]
    delta_theta_names = ["petersen_original", "harmonic_minor", "pentatonic"]
    
    print(f"探索指定预设组合...")
    print(f"φ预设: {phi_names}")
    print(f"δθ预设: {delta_theta_names}")
    
    results = explore_specific_presets(
        phi_names=phi_names,
        delta_theta_names=delta_theta_names,
        f_base=220.0
    )
    
    print(f"\n📊 探索结果:")
    for result in results:
        status = "✅" if result.success else "❌"
        entry_count = len(result.entries) if result.success else 0
        print(f"   {status} {result.parameters.phi_name} × {result.parameters.delta_theta_name}: {entry_count} 音符")

def demo_comprehensive_exploration():
    """演示综合探索"""
    print("\n🔬 演示3: 综合探索")
    print("="*50)
    
    # 配置详细的探索参数
    config = ExplorationConfiguration(
        f_base_candidates=[146.83, 220.0, 293.66],  # D3, A3, D4
        f_min=100.0,
        f_max=1000.0,
        min_entries=6,
        max_entries=40,
        enable_detailed_analysis=True,
        enable_audio_testing=False,  # 演示模式关闭音频测试
        enable_reporting=True,
        max_workers=2,  # 减少线程数以避免演示时过载
        report_name="demo_exploration"
    )
    
    print("配置综合探索参数...")
    print(f"   F_base候选: {config.f_base_candidates}")
    print(f"   音符范围: {config.min_entries}-{config.max_entries}")
    print(f"   功能: 详细分析✅, 音频测试❌, 报告生成✅")
    
    # 创建探索器
    explorer = PetersenMainExplorer(config)
    
    # 添加进度回调
    def progress_callback(stage, current, total, data):
        if current % 5 == 0 or current == total:
            percentage = current / total * 100
            print(f"   📊 {stage}: {current}/{total} ({percentage:.1f}%)")
    
    explorer.add_progress_callback(progress_callback)
    
    # 执行探索
    print("\n开始综合探索...")
    summary = explorer.run_complete_exploration()
    
    print(f"\n📋 综合探索完成")
    print(f"   状态: {summary['status']}")
    print(f"   总耗时: {summary['duration']:.1f}秒")
    print(f"   成功系统: {summary['statistics']['successful_systems']}")
    print(f"   分析系统: {summary['statistics']['analyzed_systems']}")
    
    # 显示分类分布
    if summary['category_distribution']:
        print(f"\n🏷️ 系统分类分布:")
        for category, count in summary['category_distribution'].items():
            print(f"   {category}: {count} 个系统")
    
    # 显示顶级系统
    print(f"\n🏆 前5名系统:")
    top_systems = explorer.get_top_systems(5)
    for i, (result, evaluation, classification) in enumerate(top_systems, 1):
        params = result.parameters
        category = classification.primary_category.value if classification else "未知"
        score = evaluation.weighted_total_score if evaluation else 0
        print(f"   {i}. {params.phi_name} × {params.delta_theta_name} (评分: {score:.3f}, 类别: {category})")
    
    # 导出顶级系统
    print(f"\n📁 导出前3名系统...")
    try:
        exported_files = explorer.export_top_systems_for_player(3)
        print(f"   成功导出 {len(exported_files)} 个文件:")
        for file_path in exported_files:
            print(f"   📄 {file_path.name}")
    except Exception as e:
        print(f"   ❌ 导出失败: {str(e)}")

def demo_analysis_only():
    """演示仅分析模式"""
    print("\n🔍 演示4: 仅分析模式")
    print("="*50)
    
    # 先快速生成一些系统
    print("生成测试系统...")
    results = explore_specific_presets(
        phi_names=["golden", "silver"],
        delta_theta_names=["petersen_original", "harmonic_minor"],
        f_base=220.0
    )
    
    successful_results = [r for r in results if r.success]
    if not successful_results:
        print("❌ 没有成功的系统可供分析")
        return
    
    print(f"✅ 生成 {len(successful_results)} 个成功系统")
    
    # 创建分析器进行详细分析
    from PetersenExplorer.core.characteristic_analyzer import CharacteristicAnalyzer
    from PetersenExplorer.core.evaluation_framework import MultiDimensionalEvaluator
    from PetersenExplorer.core.classification_system import OpenClassificationSystem
    
    analyzer = CharacteristicAnalyzer()
    evaluator = MultiDimensionalEvaluator()
    classifier = OpenClassificationSystem()
    
    print(f"\n📊 详细分析 {len(successful_results)} 个系统...")
    
    for i, result in enumerate(successful_results, 1):
        print(f"\n🔬 分析系统 {i}: {result.parameters.phi_name} × {result.parameters.delta_theta_name}")
        
        try:
            # 特性分析
            characteristics = analyzer.analyze_scale_characteristics(result.scale, result.entries)
            print(f"   📈 音符数: {characteristics.entry_count}")
            print(f"   🎵 音程多样性: {characteristics.interval_variety_score:.3f}")
            
            # 多维度评估
            evaluation = evaluator.evaluate_comprehensive(characteristics)
            print(f"   📊 综合评分: {evaluation.weighted_total_score:.3f}")
            print(f"   🎼 传统兼容性: {evaluation.dimension_scores['traditional_compatibility'].score:.3f}")
            print(f"   🔬 实验创新性: {evaluation.dimension_scores['experimental_innovation'].score:.3f}")
            
            # 分类
            classification = classifier.classify_system(evaluation)
            print(f"   🏷️ 主要类别: {classification.primary_category.value}")
            print(f"   🎯 应用建议: {', '.join(classification.priority_applications[:2])}")
            
        except Exception as e:
            print(f"   ❌ 分析失败: {str(e)}")

def main():
    """主演示函数"""
    print_welcome()
    
    print("\n🎼 PetersenExplorer 功能演示")
    print("这个演示将展示PetersenExplorer的主要功能")
    
    try:
        # 演示1: 快速探索
        demo_quick_exploration()
        
        # 演示2: 特定预设探索  
        demo_specific_presets()
        
        # 演示3: 综合探索
        demo_comprehensive_exploration()
        
        # 演示4: 仅分析模式
        demo_analysis_only()
        
        print("\n🎉 所有演示完成！")
        print("查看生成的报告和导出文件以获取更多详细信息。")
        
    except KeyboardInterrupt:
        print("\n⚠️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()