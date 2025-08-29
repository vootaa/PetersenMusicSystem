"""
Petersen音律系统主探索控制器
协调所有模块，执行完整的探索和分析流程
"""
import time
import traceback
from typing import List, Dict, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
from pathlib import Path

# 添加父级路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(current_dir))

# 在文件开头添加更好的导入处理
try:
    # 首先尝试导入PetersenScale_Phi
    from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
    PETERSEN_SCALE_AVAILABLE = True
except ImportError as e:
    print(f"❌ 无法导入PetersenScale_Phi: {e}")
    print("请确保PetersenScale_Phi.py在正确的路径中")
    sys.exit(1)

# 导入核心模块
try:
    from core.parameter_explorer import ParameterSpaceExplorer, ExplorationResult
    from core.characteristic_analyzer import CharacteristicAnalyzer  
    from core.evaluation_framework import MultiDimensionalEvaluator, ComprehensiveEvaluation
    from core.classification_system import OpenClassificationSystem, ClassificationResult
    from reporting.report_generator import PetersenExplorationReportGenerator
    CORE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 核心模块导入失败: {e}")
    CORE_MODULES_AVAILABLE = False
    
    # 简化类定义
    class ExplorationResult:
        def __init__(self, parameters, scale, entries, success, basic_metrics=None):
            self.parameters = parameters
            self.scale = scale
            self.entries = entries
            self.success = success
            self.basic_metrics = basic_metrics or {}
    
    class ParameterSpaceExplorer:
        def __init__(self, f_base_candidates, f_min, f_max):
            self.f_base_candidates = f_base_candidates
            self.f_min = f_min
            self.f_max = f_max
            self.total_combinations = len(PHI_PRESETS) * len(DELTA_THETA_PRESETS) * len(f_base_candidates)
        
        def explore_all_combinations(self, progress_callback=None, error_callback=None):
            return self._simplified_exploration(progress_callback, error_callback)
        
        def _simplified_exploration(self, progress_callback, error_callback):
            # 简化的探索实现
            results = []
            count = 0
            
            for phi_name, phi_value in list(PHI_PRESETS.items())[:5]:  # 限制测试数量
                for theta_name, theta_value in list(DELTA_THETA_PRESETS.items())[:5]:
                    for f_base in self.f_base_candidates:
                        count += 1
                        
                        try:
                            from types import SimpleNamespace
                            params = SimpleNamespace(
                                phi_name=phi_name,
                                phi_value=phi_value,
                                delta_theta_name=theta_name,
                                delta_theta_value=theta_value,
                                f_base=f_base
                            )
                            
                            scale = PetersenScale_Phi(
                                F_base=f_base,
                                delta_theta=theta_value,
                                phi=phi_value,
                                F_min=self.f_min,
                                F_max=self.f_max
                            )
                            
                            entries = scale.generate()
                            
                            result = ExplorationResult(
                                parameters=params,
                                scale=scale,
                                entries=entries,
                                success=True,
                                basic_metrics={
                                    'entry_count': len(entries),
                                    'frequency_range': (entries[0]['freq'], entries[-1]['freq']) if entries else (0, 0)
                                }
                            )
                            
                            results.append(result)
                            
                            if progress_callback:
                                progress_callback(count, min(25, self.total_combinations), result)
                            
                        except Exception as e:
                            if error_callback:
                                error_callback(params, str(e))
                            continue
            
            return results
        
        def filter_by_criteria(self, results=None, **kwargs):
            if not hasattr(self, '_last_results'):
                return []
            results = results or self._last_results
            return [r for r in results if r.success and len(r.entries) >= kwargs.get('min_entries', 5)]
    
    class CharacteristicAnalyzer:
        def analyze_scale_characteristics(self, scale, entries):
            return None
    
    class MultiDimensionalEvaluator:
        def evaluate_comprehensive(self, characteristics):
            return None
    
    class OpenClassificationSystem:
        def classify_system(self, evaluation):
            return None
    
    class PetersenExplorationReportGenerator:
        def __init__(self, **kwargs):
            pass
        
        def generate_comprehensive_report(self, **kwargs):
            return Path("./report.txt")

# 条件导入音频模块
try:
    from audio.playback_tester import PetersenPlaybackTester, SystemPlaybackAssessment
    AUDIO_AVAILABLE = True
except ImportError:
    print("⚠️ 音频测试模块不可用，将跳过音频验证")
    PetersenPlaybackTester = None
    SystemPlaybackAssessment = None
    AUDIO_AVAILABLE = False

@dataclass
class ExplorationConfiguration:
    """探索配置"""
    # 参数空间配置
    f_base_candidates: List[float] = field(default_factory=lambda: [110.0, 220.0, 261.63])
    f_min: float = 110.0
    f_max: float = 880.0
    
    # 筛选标准
    min_entries: int = 5
    max_entries: int = 60
    min_interval_cents: float = 5.0
    max_interval_cents: float = 600.0
    
    # 分析配置
    enable_audio_testing: bool = False  # 默认关闭音频测试
    enable_detailed_analysis: bool = True
    enable_reporting: bool = True
    
    # 性能配置
    max_workers: int = 2  # 减少并发数
    batch_size: int = 50
    
    # 音频配置
    steinway_soundfont: str = "GD_Steinway_Model_D274.sf2"  # 或 "GD_Steinway_Model_D274II.sf2"
    audio_test_sample_size: int = 5  # 音频测试的系统数量
    
    # 报告配置
    report_name: str = None
    output_dir: Path = None

class PetersenMainExplorer:
    """Petersen音律系统主探索器"""
    
    def __init__(self, config: ExplorationConfiguration = None):
        """初始化主探索器"""
        self.config = config or ExplorationConfiguration()
        
        # 初始化各模块
        try:
            self.parameter_explorer = ParameterSpaceExplorer(
                f_base_candidates=self.config.f_base_candidates,
                f_min=self.config.f_min,
                f_max=self.config.f_max
            )
            
            self.characteristic_analyzer = CharacteristicAnalyzer()
            self.evaluator = MultiDimensionalEvaluator()
            self.classifier = OpenClassificationSystem()
            
            if self.config.enable_reporting:
                self.report_generator = PetersenExplorationReportGenerator(
                    output_dir=self.config.output_dir
                )
        except Exception as e:
            print(f"⚠️ 模块初始化警告: {e}")
            print("将使用基础功能模式")
        
        # 探索状态
        self.exploration_results: List[ExplorationResult] = []
        self.characteristics: Dict[str, Any] = {}
        self.evaluations: Dict[str, ComprehensiveEvaluation] = {}
        self.classifications: Dict[str, ClassificationResult] = {}
        self.audio_assessments: Dict[str, Any] = {}
        
        # 进度回调
        self.progress_callbacks: List[Callable] = []
    
    def add_progress_callback(self, callback: Callable):
        """添加进度回调函数"""
        self.progress_callbacks.append(callback)
    
    def run_complete_exploration(self) -> Dict[str, Any]:
        """运行完整的探索流程"""
        print("🚀 开始Petersen音律系统完整探索")
        print(f"📊 预计测试组合数: {self.parameter_explorer.total_combinations}")
        print(f"⚙️ 配置: {self._format_config()}")
        
        start_time = time.time()
        
        try:
            # 第一阶段：参数空间探索
            print("\n" + "="*60)
            print("📡 第一阶段：参数空间系统性探索")
            print("="*60)
            self._run_parameter_exploration()
            
            # 筛选成功的结果
            successful_results = [r for r in self.exploration_results if r.success]
            print(f"\n✅ 参数探索完成：{len(successful_results)}/{len(self.exploration_results)} 成功")
            
            if not successful_results:
                return {"status": "no_valid_systems", "duration": time.time() - start_time}
            
            # 应用筛选标准
            filtered_results = self.parameter_explorer.filter_by_criteria(
                min_entries=self.config.min_entries,
                max_entries=self.config.max_entries,
                min_interval_cents=self.config.min_interval_cents,
                max_interval_cents=self.config.max_interval_cents
            )
            
            print(f"📋 筛选后系统数: {len(filtered_results)}")
            
            if not filtered_results:
                return {"status": "no_systems_pass_filter", "duration": time.time() - start_time}
            
            # 第二阶段：深度特性分析
            if self.config.enable_detailed_analysis:
                print("\n" + "="*60)
                print("🔬 第二阶段：深度特性分析")
                print("="*60)
                self._run_detailed_analysis(filtered_results)
            
            # 第三阶段：音频验证测试（可选）
            if self.config.enable_audio_testing and AUDIO_AVAILABLE:
                print("\n" + "="*60)
                print("🎵 第三阶段：音频验证测试")
                print("="*60)
                self._run_audio_testing(filtered_results)
            
            # 第四阶段：报告生成
            if self.config.enable_reporting:
                print("\n" + "="*60)
                print("📋 第四阶段：报告生成")
                print("="*60)
                self._generate_comprehensive_report()
            
            # 生成探索摘要
            exploration_duration = time.time() - start_time
            summary = self._generate_exploration_summary(exploration_duration)
            
            print("\n" + "="*60)
            print("🎉 Petersen音律系统探索完成")
            print("="*60)
            print(f"⏱️ 总耗时: {exploration_duration:.1f} 秒")
            print(f"📊 处理系统: {len(self.exploration_results)}")
            print(f"✅ 成功系统: {len(successful_results)}")
            print(f"🏆 优秀系统: {len([e for e in self.evaluations.values() if e.weighted_total_score >= 0.7])}")
            
            return summary
            
        except Exception as e:
            print(f"\n❌ 探索过程中发生错误: {str(e)}")
            print(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    def _run_parameter_exploration(self):
        """运行参数空间探索"""
        def progress_callback(current, total, result):
            percentage = current / total * 100
            status = "✅" if result.success else "❌"
            
            if current % 5 == 0 or current == total:
                print(f"  📊 进度: {current}/{total} ({percentage:.1f}%) {status}")
        
        def error_callback(params, error):
            if len(error) < 50:
                print(f"⚠️ 生成失败: {params.phi_name}×{params.delta_theta_name} - {error}")
        
        if CORE_MODULES_AVAILABLE:
            self.exploration_results = self.parameter_explorer.explore_all_combinations(
                progress_callback=progress_callback,
                error_callback=error_callback
            )
        else:
            self.exploration_results = self.parameter_explorer._simplified_exploration(
                progress_callback, error_callback
            )
            self.parameter_explorer._last_results = self.exploration_results

    def _run_simple_exploration(self):
        """简化的探索模式，用于测试基本功能"""
        print("🔧 运行简化探索模式...")
        
        # 创建一些示例结果用于测试
        from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
        
        sample_results = []
        phi_names = list(PHI_PRESETS.keys())[:3]  # 只测试前3个φ值
        delta_theta_names = list(DELTA_THETA_PRESETS.keys())[:3]  # 只测试前3个δθ值
        
        for phi_name in phi_names:
            for delta_theta_name in delta_theta_names:
                try:
                    phi_value = PHI_PRESETS[phi_name]['value']
                    delta_theta_value = DELTA_THETA_PRESETS[delta_theta_name]['value']
                    
                    scale = PetersenScale_Phi(
                        F_base=220.0,
                        delta_theta=delta_theta_value,
                        phi=phi_value,
                        F_min=self.config.f_min,
                        F_max=self.config.f_max
                    )
                    
                    entries = scale.generate()
                    
                    # 创建简单的结果对象
                    result = type('ExplorationResult', (), {
                        'success': True,
                        'parameters': type('Parameters', (), {
                            'phi_name': phi_name,
                            'delta_theta_name': delta_theta_name,
                            'f_base': 220.0
                        })(),
                        'entries': entries,
                        'scale': scale,
                        'basic_metrics': {
                            'entry_count': len(entries),
                            'frequency_range': (entries[0]['frequency'], entries[-1]['frequency']) if entries else (0, 0)
                        }
                    })()
                    
                    sample_results.append(result)
                    print(f"  ✅ {phi_name} × {delta_theta_name}: {len(entries)} 音符")
                    
                except Exception as e:
                    print(f"  ❌ {phi_name} × {delta_theta_name}: {str(e)}")
        
        self.exploration_results = sample_results
        print(f"📊 简化探索完成：生成 {len(sample_results)} 个测试系统")
    
    def _apply_filters(self, results):
        """应用筛选条件"""
        filtered = []
        for result in results:
            if hasattr(result, 'entries') and result.entries:
                entry_count = len(result.entries)
                if self.config.min_entries <= entry_count <= self.config.max_entries:
                    filtered.append(result)
        return filtered
    
    def _run_detailed_analysis(self, filtered_results: List[ExplorationResult]):
        """运行详细分析"""
        print(f"🔬 分析 {len(filtered_results)} 个筛选后的系统...")
        
        def analyze_single_system(result: ExplorationResult) -> Tuple[str, Any, ComprehensiveEvaluation, ClassificationResult]:
            """分析单个系统"""
            result_key = self._get_result_key(result)
            
            try:
                # 特性分析
                characteristics = self.characteristic_analyzer.analyze_scale_characteristics(
                    result.scale, result.entries
                )
                
                # 多维度评估
                evaluation = self.evaluator.evaluate_comprehensive(characteristics)
                
                # 开放性分类
                classification = self.classifier.classify_system(evaluation)
                
                return result_key, characteristics, evaluation, classification
                
            except Exception as e:
                print(f"❌ 分析系统失败 {result_key}: {e}")
                return result_key, None, None, None
        
        # 使用线程池并行分析
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # 提交分析任务
            futures = {
                executor.submit(analyze_single_system, result): result 
                for result in filtered_results
            }
            
            completed = 0
            for future in as_completed(futures):
                result_key, characteristics, evaluation, classification = future.result()
                
                if characteristics and evaluation and classification:
                    self.characteristics[result_key] = characteristics
                    self.evaluations[result_key] = evaluation
                    self.classifications[result_key] = classification
                
                completed += 1
                if completed % 5 == 0:
                    print(f"  📊 分析进度: {completed}/{len(filtered_results)}")
        
        print(f"✅ 详细分析完成：{len(self.evaluations)} 个系统获得评估结果")
    
    def _run_audio_testing(self, filtered_results: List[ExplorationResult]):
        """运行音频测试"""
        # 选择前N个最优系统进行音频测试
        if not self.evaluations:
            print("⚠️ 没有评估结果，随机选择系统进行音频测试")
            test_systems = filtered_results[:self.config.audio_test_sample_size]
        else:
            # 按评估得分排序选择
            scored_systems = []
            for result in filtered_results:
                result_key = self._get_result_key(result)
                if result_key in self.evaluations:
                    evaluation = self.evaluations[result_key]
                    scored_systems.append((evaluation.weighted_total_score, result))
            
            scored_systems.sort(key=lambda x: x[0], reverse=True)
            test_systems = [system[1] for system in scored_systems[:self.config.audio_test_sample_size]]
        
        print(f"🎵 测试 {len(test_systems)} 个优选系统的音频播放能力...")
        
        try:
            with PetersenPlaybackTester(soundfont_path=self.config.steinway_soundfont) as tester:
                for i, result in enumerate(test_systems, 1):
                    result_key = self._get_result_key(result)
                    print(f"  🎼 [{i}/{len(test_systems)}] 测试 {result_key}")
                    
                    assessment = tester.test_system_playability(result, interactive=False)
                    self.audio_assessments[result_key] = assessment
        
        except Exception as e:
            print(f"⚠️ 音频测试模块初始化失败: {str(e)}")
            print("   跳过音频测试阶段")
        
        print(f"✅ 音频测试完成：{len(self.audio_assessments)} 个系统获得播放评估")
    
    def _generate_comprehensive_report(self) -> Path:
        """生成综合报告"""
        print("📋 生成综合探索报告...")
        
        report_path = self.report_generator.generate_comprehensive_report(
            exploration_results=self.exploration_results,
            evaluations=self.evaluations,
            classifications=self.classifications,
            audio_assessments=self.audio_assessments,
            report_name=self.config.report_name
        )
        
        print(f"✅ 报告已生成: {report_path}")
        return report_path
    
    def _generate_exploration_summary(self, duration: float) -> Dict[str, Any]:
        """生成探索摘要"""
        successful_results = [r for r in self.exploration_results if r.success]
        
        # 统计分类分布
        category_distribution = {}
        for classification in self.classifications.values():
            category = classification.primary_category.value
            category_distribution[category] = category_distribution.get(category, 0) + 1
        
        # 识别顶级系统
        top_systems = []
        if self.evaluations:
            scored_systems = [
                (eval_result.weighted_total_score, result_key, eval_result)
                for result_key, eval_result in self.evaluations.items()
            ]
            scored_systems.sort(key=lambda x: x[0], reverse=True)
            
            for score, result_key, evaluation in scored_systems[:10]:
                params_parts = result_key.split('_')
                top_systems.append({
                    'result_key': result_key,
                    'phi_name': params_parts[0] if len(params_parts) > 0 else "unknown",
                    'delta_theta_name': params_parts[1] if len(params_parts) > 1 else "unknown",
                    'f_base': params_parts[2] if len(params_parts) > 2 else "unknown",
                    'score': score
                })
        
        # 音频推荐统计
        audio_recommended_count = sum(1 for a in self.audio_assessments.values() 
                                    if hasattr(a, 'recommended_for_audio') and a.recommended_for_audio)
        
        return {
            "status": "completed",
            "duration": duration,
            "statistics": {
                "total_combinations": len(self.exploration_results),
                "successful_systems": len(successful_results),
                "failed_systems": len(self.exploration_results) - len(successful_results),
                "analyzed_systems": len(self.evaluations),
                "classified_systems": len(self.classifications),
                "audio_tested_systems": len(self.audio_assessments),
                "audio_recommended_systems": audio_recommended_count
            },
            "category_distribution": category_distribution,
            "top_systems": top_systems,
            "performance_metrics": {
                "avg_analysis_time": duration / len(self.evaluations) if self.evaluations else 0,
                "success_rate": len(successful_results) / len(self.exploration_results) if self.exploration_results else 0
            }
        }
    
    def get_top_systems(self, count: int = 10, 
                       criteria: str = "overall") -> List[Tuple[ExplorationResult, ComprehensiveEvaluation, ClassificationResult]]:
        """获取顶级系统"""
        if not self.evaluations:
            return []
        
        systems = []
        
        for result in self.exploration_results:
            if not result.success:
                continue
                
            result_key = self._get_result_key(result)
            
            if result_key in self.evaluations:
                eval_result = self.evaluations[result_key]
                classif_result = self.classifications.get(result_key)
                
                if criteria == "traditional":
                    score = eval_result.dimension_scores['traditional_compatibility'].score
                elif criteria == "experimental":
                    score = eval_result.dimension_scores['experimental_innovation'].score
                elif criteria == "audio" and result_key in self.audio_assessments:
                    assessment = self.audio_assessments[result_key]
                    score = getattr(assessment, 'overall_playability', 0)
                else:
                    score = eval_result.weighted_total_score
                
                systems.append((score, result, eval_result, classif_result))
        
        # 按分数排序
        systems.sort(key=lambda x: x[0], reverse=True)
        
        return [(result, eval, classif) for score, result, eval, classif in systems[:count]]
    
    def _get_result_key(self, result: ExplorationResult) -> str:
        """获取结果的唯一键"""
        params = result.parameters
        return f"{params.phi_name}_{params.delta_theta_name}_{params.f_base}"
    
    def _format_config(self) -> str:
        """格式化配置信息"""
        config_items = [
            f"F_base候选数: {len(self.config.f_base_candidates)}",
            f"频率范围: {self.config.f_min}-{self.config.f_max}Hz",
            f"音符筛选: {self.config.min_entries}-{self.config.max_entries}个",
            f"并行度: {self.config.max_workers}线程"
        ]
        
        features = []
        if self.config.enable_detailed_analysis:
            features.append("详细分析")
        if self.config.enable_audio_testing:
            features.append("音频测试")
        if self.config.enable_reporting:
            features.append("报告生成")
        
        if features:
            config_items.append(f"功能: {', '.join(features)}")
        
        return " | ".join(config_items)

# 便捷功能函数
def quick_exploration(f_base_list: List[float] = None, 
                     output_dir: Path = None,
                     enable_audio: bool = False) -> Dict[str, Any]:
    """快速探索功能"""
    config = ExplorationConfiguration(
        f_base_candidates=f_base_list or [220.0, 261.63],
        enable_audio_testing=enable_audio,
        output_dir=output_dir,
        audio_test_sample_size=3 if enable_audio else 0
    )
    
    explorer = PetersenMainExplorer(config)
    return explorer.run_complete_exploration()

if __name__ == "__main__":
    # 演示用法
    print("🎼 Petersen音律系统探索器 - 演示模式")
    
    # 快速演示探索
    print("\n1️⃣ 快速探索演示:")
    demo_config = ExplorationConfiguration(
        f_base_candidates=[220.0],  # 只测试A3
        enable_audio_testing=False,
        enable_detailed_analysis=True,
        audio_test_sample_size=0
    )
    
    explorer = PetersenMainExplorer(demo_config)
    
    try:
        summary = explorer.run_complete_exploration()
        
        print("\n📋 探索摘要:")
        print(f"   总计组合: {summary['statistics']['total_combinations']}")
        print(f"   成功系统: {summary['statistics']['successful_systems']}")
        print(f"   分析系统: {summary['statistics']['analyzed_systems']}")
        
        # 显示前5名系统
        print("\n🏆 前5名系统:")
        top_systems = explorer.get_top_systems(5)
        for i, (result, evaluation, classification) in enumerate(top_systems, 1):
            params = result.parameters
            score = getattr(evaluation, 'weighted_total_score', 0) if evaluation else 0
            category = getattr(classification.primary_category, 'value', '未知') if classification else "未分类"
            print(f"   {i}. {params.phi_name} × {params.delta_theta_name} "
                  f"(评分: {score:.3f}, 类别: {category})")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断探索")
    except Exception as e:
        print(f"\n❌ 演示过程出错: {str(e)}")
        traceback.print_exc()