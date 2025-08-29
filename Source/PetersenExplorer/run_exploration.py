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
            from core.parameter_explorer import ParameterSpaceExplorer
            from core.evaluation_framework import MultiDimensionalEvaluator
            print("✅ 使用完整分析模块")
            use_full_system = True
        except ImportError as e:
            print(f"⚠️ 完整模块不可用: {e}")
            print("🔄 使用简化模式...")
            use_full_system = False
        
        if use_full_system:
            return run_full_exploration()
        else:
            return run_basic_exploration()
            
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_basic_exploration():
    """基础探索模式"""
    from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
    
    print("\n🚀 启动基础音律探索")
    
    results = []
    count = 0
    max_tests = 10
    
    phi_items = list(PHI_PRESETS.items())[:3]  # 测试前3个φ值
    theta_items = list(DELTA_THETA_PRESETS.items())[:3]  # 测试前3个δθ值
    
    for phi_name, phi_value in phi_items:
        for theta_name, theta_value in theta_items:
            count += 1
            if count > max_tests:
                break
                
            try:
                print(f"  📊 [{count}/{max_tests}] 测试: {phi_name} × {theta_name}")
                
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

def run_full_exploration():
    """完整探索模式"""
    from core.parameter_explorer import ParameterSpaceExplorer
    from core.evaluation_framework import MultiDimensionalEvaluator
    
    print("\n🚀 启动完整音律探索")
    
    # 创建探索器
    explorer = ParameterSpaceExplorer([220.0])
    evaluator = MultiDimensionalEvaluator()
    
    # 运行探索
    def progress_callback(current, total, result):
        if current % 3 == 0:
            status = "✅" if result.success else "❌"
            count = len(result.entries) if result.success else 0
            print(f"  📊 [{current}/{min(total, 15)}] {result.parameters.phi_name}×{result.parameters.delta_theta_name}: {count} 音符 {status}")
        return current < 15  # 限制15个测试
    
    results = explorer.explore_all_combinations(progress_callback=progress_callback)
    successful = [r for r in results if r.success and len(r.entries) >= 5]
    
    print(f"\n✅ 完整探索完成！{len(successful)}/{len(results)} 系统成功")
    
    if successful:
        # 评估前5个系统
        print(f"\n🔬 开始详细评估...")
        
        evaluated_systems = []
        for i, result in enumerate(successful[:5], 1):
            try:
                evaluation = evaluator.evaluate_comprehensive()
                evaluated_systems.append((result, evaluation))
                print(f"  📊 [{i}/5] {result.parameters.phi_name}×{result.parameters.delta_theta_name}: "
                      f"评分={evaluation.weighted_total_score:.3f}")
            except Exception as e:
                print(f"  ❌ 评估失败: {str(e)[:50]}...")
                continue
        
        if evaluated_systems:
            # 按评分排序
            evaluated_systems.sort(key=lambda x: x[1].weighted_total_score, reverse=True)
            
            print(f"\n🏆 最佳音律系统:")
            best_result, best_eval = evaluated_systems[0]
            print(f"   系统: {best_result.parameters.phi_name} × {best_result.parameters.delta_theta_name}")
            print(f"   评分: {best_eval.weighted_total_score:.3f}")
            print(f"   类别: {best_eval.category_recommendation}")
            print(f"   应用: {', '.join(best_eval.application_suggestions[:2])}")
        
        return True
    else:
        print(f"\n❌ 未发现有效的音律系统")
        return False

def main():
    """主函数"""
    try:
        success = simple_exploration()
        print(f"\n{'✅ 探索成功完成!' if success else '❌ 探索未完成'}")
        return success
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断探索")
        return False
    except Exception as e:
        print(f"\n❌ 意外错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)