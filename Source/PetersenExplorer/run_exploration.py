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

def simple_exploration():
    """简化的探索流程"""
    print("🎼" + "="*60 + "🎼")
    print("   PetersenExplorer - 音律探索系统")
    print("🎼" + "="*60 + "🎼")
    
    try:
        # 导入基础模块
        from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
        
        print(f"📊 可用预设: φ={len(PHI_PRESETS)}, δθ={len(DELTA_THETA_PRESETS)}")
        
        # 尝试导入完整模块
        try:
            from main_explorer import PetersenMainExplorer, ExplorationConfiguration
            print("✅ 使用完整PetersenExplorer系统")
            use_full_system = True
        except ImportError as e:
            print(f"⚠️ 完整模块不可用: {e}")
            print("🔄 使用简化模式...")
            use_full_system = False
        
        if use_full_system:
            return run_complete_exploration()
        else:
            return run_basic_exploration()
            
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_complete_exploration():
    """运行完整的PetersenExplorer探索"""
    from main_explorer import PetersenMainExplorer, ExplorationConfiguration
    
    print("\n🚀 启动完整PetersenExplorer系统")

    # 统一的输出目录管理
    base_output_dir = Path("./output")
    timestamp = int(time.time())
    session_output_dir = base_output_dir / f"session_{timestamp}"

    soundfont_choice = input("选择SoundFont (1=D274, 2=D274II, 其他=禁用音频): ").strip()

    if soundfont_choice == "1":
        preferred_soundfont = "GD_Steinway_Model_D274.sf2"
        enable_audio = True
    elif soundfont_choice == "2":
        preferred_soundfont = "GD_Steinway_Model_D274II.sf2"
        enable_audio = True
    else:
        preferred_soundfont = None
        enable_audio = False
    
    # 配置完整探索参数
    config = ExplorationConfiguration(
        # 参数空间配置
        f_base_candidates=[110.0, 146.83, 220.0, 261.63, 293.66],
        f_min=110.0,
        f_max=880.0,
        
        # 筛选标准
        min_entries=5,
        max_entries=60,
        
        # 功能开关
        enable_audio_testing=enable_audio,      # 启用音频测试
        enable_detailed_analysis=True,          # 启用详细分析
        enable_reporting=True,                  # 启用报告生成

        #SoundFont
        preferred_soundfont=preferred_soundfont,
        
        # 性能配置
        max_workers=4,
        audio_test_sample_size=10,      # 测试前10个最优系统
        
        # 报告配置
        output_dir=session_output_dir, 
        report_name=f"petersen_exploration_{timestamp}",
    )

    print(f"📁 输出目录: {session_output_dir}")
    
    print(f"⚙️ 配置概览:")
    print(f"   - 基频候选: {len(config.f_base_candidates)} 个")
    print(f"   - 音频测试: {'启用' if config.enable_audio_testing else '禁用'}")
    print(f"   - 详细分析: {'启用' if config.enable_detailed_analysis else '禁用'}")
    print(f"   - 报告生成: {'启用' if config.enable_reporting else '禁用'}")
    print(f"   - 音频测试样本: {config.audio_test_sample_size} 个系统")
    
    # 创建探索器并运行
    explorer = PetersenMainExplorer(config)
    
    try:
        # 调用完整探索流程
        summary = explorer.run_complete_exploration()
        
        # 显示探索结果摘要
        print_exploration_summary(summary, explorer)
        
        return summary.get("status") == "completed"
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断探索")
        return False
    except Exception as e:
        print(f"\n❌ 探索过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_exploration_summary(summary, explorer):
    """打印探索结果摘要"""
    print("\n" + "="*80)
    print("🎉 PetersenExplorer 完整探索结果摘要")
    print("="*80)
    
    if summary.get("status") == "completed":
        stats = summary.get("statistics", {})
        
        print(f"📊 统计信息:")
        print(f"   • 总测试组合: {stats.get('total_combinations', 0)}")
        print(f"   • 成功生成系统: {stats.get('successful_systems', 0)}")
        print(f"   • 详细分析系统: {stats.get('analyzed_systems', 0)}")
        print(f"   • 分类系统: {stats.get('classified_systems', 0)}")
        print(f"   • 音频测试系统: {stats.get('audio_tested_systems', 0)}")
        print(f"   • 音频推荐系统: {stats.get('audio_recommended_systems', 0)}")
        
        # 分类分布
        category_dist = summary.get("category_distribution", {})
        if category_dist:
            print(f"\n🏷️ 系统分类分布:")
            for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {category}: {count} 个系统")
        
        # 顶级系统
        top_systems = summary.get("top_systems", [])
        if top_systems:
            print(f"\n🏆 顶级音律系统 (前10名):")
            for i, system in enumerate(top_systems[:10], 1):
                print(f"   {i:2d}. φ={system['phi_name']}, δθ={system['delta_theta_name']}, "
                      f"F_base={system['f_base']}Hz (评分: {system['score']:.3f})")
        
        # 性能指标
        perf = summary.get("performance_metrics", {})
        duration = summary.get("duration", 0)
        print(f"\n⏱️ 性能指标:")
        print(f"   • 总耗时: {duration:.1f} 秒")
        print(f"   • 平均分析时间: {perf.get('avg_analysis_time', 0):.3f} 秒/系统")
        print(f"   • 成功率: {perf.get('success_rate', 0):.1%}")
        
        # 获取详细的系统推荐
        print_system_recommendations(explorer)
        
    else:
        print(f"❌ 探索状态: {summary.get('status', 'unknown')}")
        if "error" in summary:
            print(f"   错误: {summary['error']}")

def print_system_recommendations(explorer):
    """打印系统推荐"""
    print(f"\n💡 应用推荐:")
    
    # 传统音乐系统
    traditional_systems = explorer.get_top_systems(3, criteria="traditional")
    if traditional_systems:
        print(f"   🎼 传统音乐应用 (前3名):")
        for i, (result, evaluation, classification) in enumerate(traditional_systems, 1):
            params = result.parameters
            score = evaluation.dimension_scores['traditional_compatibility'].score if evaluation else 0
            print(f"      {i}. {params.phi_name} × {params.delta_theta_name} (兼容性: {score:.3f})")
    
    # 实验音乐系统
    experimental_systems = explorer.get_top_systems(3, criteria="experimental")
    if experimental_systems:
        print(f"   🔬 实验音乐应用 (前3名):")
        for i, (result, evaluation, classification) in enumerate(experimental_systems, 1):
            params = result.parameters
            score = evaluation.dimension_scores['experimental_innovation'].score if evaluation else 0
            print(f"      {i}. {params.phi_name} × {params.delta_theta_name} (创新性: {score:.3f})")
    
    # 音频播放推荐
    audio_systems = explorer.get_top_systems(3, criteria="audio")
    if audio_systems:
        print(f"   🎵 音频播放推荐 (前3名):")
        for i, (result, evaluation, classification) in enumerate(audio_systems, 1):
            params = result.parameters
            result_key = explorer._get_result_key(result)
            if result_key in explorer.audio_assessments:
                assessment = explorer.audio_assessments[result_key]
                playability = assessment.overall_playability if hasattr(assessment, 'overall_playability') else 0
                print(f"      {i}. {params.phi_name} × {params.delta_theta_name} (播放能力: {playability:.3f})")

def run_basic_exploration():
    """基础探索模式（备用方案）"""
    from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
    
    print("\n🚀 启动基础音律探索（简化模式）")
    
    results = []
    count = 0
    max_tests = 15
    
    phi_items = list(PHI_PRESETS.items())[:5]  # 测试前5个φ值
    theta_items = list(DELTA_THETA_PRESETS.items())[:3]  # 测试前3个δθ值
    
    for phi_name, phi_data in phi_items:
        for theta_name, theta_data in theta_items:
            count += 1
            if count > max_tests:
                break
                
            try:
                print(f"  📊 [{count}/{max_tests}] 测试: {phi_name} × {theta_name}")
                
                phi_value = phi_data.get('value') if isinstance(phi_data, dict) else phi_data
                theta_value = theta_data.get('value') if isinstance(theta_data, dict) else theta_data
                
                scale = PetersenScale_Phi(
                    F_base=220.0,
                    delta_theta=theta_value,
                    phi=phi_value,
                    F_min=110.0,
                    F_max=880.0
                )
                
                entries = scale.generate()
                
                if entries and len(entries) >= 5:
                    freq_range = (entries[0]['freq'], entries[-1]['freq'])
                    print(f"      ✅ 生成 {len(entries)} 个音符 ({freq_range[0]:.1f}-{freq_range[1]:.1f} Hz)")
                    
                    # 简单评分
                    score = min(1.0, len(entries) / 20.0)  # 基于音符数量的简单评分
                    
                    results.append({
                        'phi_name': phi_name,
                        'theta_name': theta_name,
                        'entry_count': len(entries),
                        'freq_range': freq_range,
                        'score': score
                    })
                else:
                    print(f"      ❌ 生成失败或音符过少")
                
            except Exception as e:
                print(f"      ❌ 错误: {str(e)[:50]}...")
                continue
    
    # 显示结果
    if results:
        print(f"\n🎉 基础探索完成！发现 {len(results)} 个有效音律系统")
        
        # 按评分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n🏆 前5名音律系统:")
        for i, result in enumerate(results[:5], 1):
            print(f"   {i}. {result['phi_name']} × {result['theta_name']}")
            print(f"      音符数: {result['entry_count']}, 评分: {result['score']:.3f}")
        
        return True
    else:
        print(f"\n❌ 未发现有效的音律系统")
        return False

def main():
    """主函数"""
    try:
        print("🎼 PetersenExplorer - 音律探索系统")
        print(f"🕒 启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        success = run_complete_exploration()
        
        if success:
            print(f"\n✅ 探索成功完成!")
            print(f"📁 查看输出目录获取详细报告和音频测试结果")
        else:
            print(f"\n❌ 探索未完成")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断探索")
        return False
    except Exception as e:
        print(f"\n❌ 意外错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)