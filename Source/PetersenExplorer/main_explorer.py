"""
Petersen音律系统主探索控制器
协调所有模块，执行完整的探索和分析流程
"""
from typing import List, Dict, Tuple, Optional, Any, Callable
from dataclasses import dataclass
import time
import json
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

# 添加父级路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

# 导入核心模块
from .core.parameter_explorer import ParameterSpaceExplorer, ExplorationResult, format_exploration_result
from .core.characteristic_analyzer import CharacteristicAnalyzer
from .core.evaluation_framework import MultiDimensionalEvaluator, ComprehensiveEvaluation
from .core.classification_system import OpenClassificationSystem, ClassificationResult, format_classification_result
from .audio.playback_tester import PetersenPlaybackTester, SystemPlaybackAssessment, format_playback_assessment
from .reporting.report_generator import PetersenExplorationReportGenerator

@dataclass
class ExplorationConfiguration:
    """探索配置"""
    # 参数空间配置
    f_base_candidates: List[float] = None
    f_min: float = 110.0
    f_max: float = 880.0
    
    # 筛选标准
    min_entries: int = 5
    max_entries: int = 60
    min_interval_cents: float = 5.0
    max_interval_cents: float = 600.0
    
    # 分析配置
    enable_audio_testing: bool = True
    enable_detailed_analysis: bool = True
    enable_reporting: bool = True
    
    # 性能配置
    max_workers: int = 4
    batch_size: int = 50
    
    # 音频配置
    steinway_soundfont: str = "GD_Steinway_Model_D274.sf2"  # 或 "GD_Steinway_Model_D274II.sf2"
    audio_test_sample_size: int = 20  # 音频测试的系统数量
    
    # 报告配置
    report_name: str = None
    output_dir: Path = None

class PetersenMainExplorer:
    """Petersen音律系统主探索器"""
    
    def __init__(self, config: ExplorationConfiguration = None):
        """
        初始化主探索器
        
        Args:
            config: 探索配置
        """
        self.config = config or ExplorationConfiguration()
        
        # 初始化各模块
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
        
        # 探索状态
        self.exploration_results: List[ExplorationResult] = []
        self.characteristics: Dict[str, Any] = {}
        self.evaluations: Dict[str, ComprehensiveEvaluation] = {}
        self.classifications: Dict[str, ClassificationResult] = {}
        self.audio_assessments: Dict[str, SystemPlaybackAssessment] = {}
        
        # 进度回调
        self.progress_callbacks: List[Callable] = []
    
    def add_progress_callback(self, callback: Callable):
        """添加进度回调函数"""
        self.progress_callbacks.append(callback)
    
    def run_complete_exploration(self) -> Dict[str, Any]:
        """
        运行完整的探索流程
        
        Returns:
            Dict: 探索结果摘要
        """
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
                print("❌ 没有成功的系统，终止探索")
                return {"status": "failed", "reason": "no_successful_systems"}
            
            # 应用筛选标准
            filtered_results = self.parameter_explorer.filter_by_criteria(
                min_entries=self.config.min_entries,
                max_entries=self.config.max_entries,
                min_interval_cents=self.config.min_interval_cents,
                max_interval_cents=self.config.max_interval_cents
            )
            
            print(f"📋 筛选后系统数: {len(filtered_results)}")
            
            if not filtered_results:
                print("⚠️ 筛选后无可用系统，放宽筛选标准")
                filtered_results = successful_results[:50]  # 取前50个
            
            # 第二阶段：深度特性分析
            if self.config.enable_detailed_analysis:
                print("\n" + "="*60)
                print("🔬 第二阶段：深度特性分析")
                print("="*60)
                self._run_detailed_analysis(filtered_results)
            
            # 第三阶段：音频验证测试
            if self.config.enable_audio_testing:
                print("\n" + "="*60)
                print("🎵 第三阶段：音频验证测试")
                print("="*60)
                self._run_audio_testing(filtered_results)
            
            # 第四阶段：报告生成
            if self.config.enable_reporting:
                print("\n" + "="*60)
                print("📋 第四阶段：综合报告生成")
                print("="*60)
                report_path = self._generate_comprehensive_report()
                print(f"📄 报告已生成: {report_path}")
            
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
            print(f"🎵 音频推荐: {len([a for a in self.audio_assessments.values() if a.recommended_for_audio])}")
            
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
            
            if current % 20 == 0 or current == total:  # 每20个或最后一个显示进度
                print(f"   [{current:4d}/{total}] ({percentage:5.1f}%) {status} {result.parameters.phi_name} × {result.parameters.delta_theta_name}")
            
            # 调用外部回调
            for callback in self.progress_callbacks:
                callback("parameter_exploration", current, total, result)
        
        def error_callback(params, error):
            if "频率范围" not in error:  # 只显示非常见错误
                print(f"   ⚠️ 错误: {params.phi_name} × {params.delta_theta_name} - {error}")
        
        self.exploration_results = self.parameter_explorer.explore_all_combinations(
            progress_callback=progress_callback,
            error_callback=error_callback
        )
    
    def _run_detailed_analysis(self, filtered_results: List[ExplorationResult]):
        """运行详度分析"""
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
                print(f"   ❌ 分析失败 {result_key}: {str(e)}")
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
                if completed % 10 == 0 or completed == len(filtered_results):
                    print(f"   📊 已完成分析: {completed}/{len(filtered_results)} ({completed/len(filtered_results)*100:.1f}%)")
                
                # 调用进度回调
                for callback in self.progress_callbacks:
                    callback("detailed_analysis", completed, len(filtered_results), None)
        
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
                    score = self.evaluations[result_key].weighted_total_score
                    scored_systems.append((score, result))
            
            scored_systems.sort(key=lambda x: x[0], reverse=True)
            test_systems = [system[1] for system in scored_systems[:self.config.audio_test_sample_size]]
        
        print(f"🎵 测试 {len(test_systems)} 个优选系统的音频播放能力...")
        
        try:
            with PetersenPlaybackTester(soundfont_path=self.config.steinway_soundfont) as tester:
                for i, result in enumerate(test_systems, 1):
                    result_key = self._get_result_key(result)
                    
                    print(f"\n🎼 [{i}/{len(test_systems)}] 测试系统: {result_key}")
                    
                    try:
                        assessment = tester.test_system_playability(
                            result,
                            interactive=False  # 非交互模式
                        )
                        self.audio_assessments[result_key] = assessment
                        
                        # 调用进度回调
                        for callback in self.progress_callbacks:
                            callback("audio_testing", i, len(test_systems), assessment)
                    
                    except Exception as e:
                        print(f"   ❌ 音频测试失败: {str(e)}")
        
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
                # 找到对应的exploration_result
                matching_result = None
                for result in successful_results:
                    if self._get_result_key(result) == result_key:
                        matching_result = result
                        break
                
                if matching_result:
                    top_systems.append({
                        'result_key': result_key,
                        'score': score,
                        'parameters': matching_result.parameters,
                        'entry_count': len(matching_result.entries),
                        'category': self.classifications.get(result_key, {}).primary_category.value if result_key in self.classifications else 'unknown'
                    })
        
        # 音频推荐统计
        audio_recommended_count = sum(1 for a in self.audio_assessments.values() if a.recommended_for_audio)
        
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
        """
        获取顶级系统
        
        Args:
            count: 返回数量
            criteria: 排序标准 ("overall", "traditional", "experimental", "audio")
            
        Returns:
            List: 顶级系统列表
        """
        if not self.evaluations:
            return []
        
        systems = []
        
        for result in self.exploration_results:
            if not result.success:
                continue
                
            result_key = self._get_result_key(result)
            
            if result_key in self.evaluations:
                evaluation = self.evaluations[result_key]
                classification = self.classifications.get(result_key)
                
                # 根据标准计算排序分数
                if criteria == "overall":
                    score = evaluation.weighted_total_score
                elif criteria == "traditional":
                    score = evaluation.dimension_scores['traditional_compatibility'].score
                elif criteria == "experimental":
                    score = evaluation.dimension_scores['experimental_innovation'].score
                elif criteria == "audio":
                    if result_key in self.audio_assessments:
                        score = self.audio_assessments[result_key].overall_playability
                    else:
                        score = 0
                else:
                    score = evaluation.weighted_total_score
                
                systems.append((score, result, evaluation, classification))
        
        # 按分数排序
        systems.sort(key=lambda x: x[0], reverse=True)
        
        return [(result, eval, classif) for score, result, eval, classif in systems[:count]]
    
    def export_top_systems_for_player(self, count: int = 5, output_dir: Path = None) -> List[Path]:
        """
        导出顶级系统为Enhanced Petersen Player可用格式
        
        Args:
            count: 导出数量
            output_dir: 输出目录
            
        Returns:
            List[Path]: 导出文件路径列表
        """
        top_systems = self.get_top_systems(count)
        
        if not output_dir:
            output_dir = Path("./exported_scales")
        output_dir.mkdir(exist_ok=True)
        
        exported_files = []
        
        for i, (result, evaluation, classification) in enumerate(top_systems, 1):
            # 生成文件名
            params = result.parameters
            filename = f"petersen_scale_{i:02d}_{params.phi_name}_{params.delta_theta_name}_{params.f_base}Hz.json"
            file_path = output_dir / filename
            
            # 准备导出数据
            scale_data = {
                "name": f"Petersen Scale #{i}",
                "description": f"φ={params.phi_name}({params.phi_value:.6f}), δθ={params.delta_theta_name}({params.delta_theta_value}°)",
                "parameters": {
                    "phi_name": params.phi_name,
                    "phi_value": params.phi_value,
                    "delta_theta_name": params.delta_theta_name,
                    "delta_theta_value": params.delta_theta_value,
                    "f_base": params.f_base,
                    "f_min": params.f_min,
                    "f_max": params.f_max
                },
                "entries": [
                    {
                        "frequency": entry.freq,
                        "key_short": entry.key_short,
                        "key_long": entry.key_long,
                        "midi_note": getattr(entry, 'midi_note', None),
                        "cents_from_base": getattr(entry, 'cents_from_base', None)
                    }
                    for entry in result.entries
                ],
                "evaluation": {
                    "weighted_total_score": evaluation.weighted_total_score,
                    "category": classification.primary_category.value if classification else "unknown",
                    "strengths": evaluation.strengths,
                    "applications": evaluation.application_suggestions
                } if evaluation else None,
                "metadata": {
                    "generated_by": "PetersenExplorer",
                    "generation_time": time.time(),
                    "entry_count": len(result.entries)
                }
            }
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(scale_data, f, indent=2, ensure_ascii=False)
            
            exported_files.append(file_path)
            print(f"   📁 导出: {filename}")
        
        print(f"✅ 已导出 {len(exported_files)} 个顶级音律系统")
        return exported_files
    
    def _get_result_key(self, result: ExplorationResult) -> str:
        """获取结果的唯一键"""
        params = result.parameters
        return f"{params.phi_name}_{params.delta_theta_name}_{params.f_base}"
    
    def _format_config(self) -> str:
        """格式化配置信息"""
        config_items = [
            f"F_base候选数: {len(self.config.f_base_candidates or [])}" if self.config.f_base_candidates else "F_base: 默认",
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
                     enable_audio: bool = True) -> Dict[str, Any]:
    """
    快速探索功能
    
    Args:
        f_base_list: F_base候选值列表
        output_dir: 输出目录
        enable_audio: 是否启用音频测试
        
    Returns:
        Dict: 探索结果摘要
    """
    config = ExplorationConfiguration(
        f_base_candidates=f_base_list,
        enable_audio_testing=enable_audio,
        output_dir=output_dir,
        audio_test_sample_size=10 if enable_audio else 0
    )
    
    explorer = PetersenMainExplorer(config)
    return explorer.run_complete_exploration()

def explore_specific_presets(phi_names: List[str] = None,
                           delta_theta_names: List[str] = None,
                           f_base: float = 220.0) -> List[ExplorationResult]:
    """
    探索特定预设组合
    
    Args:
        phi_names: φ预设名称列表
        delta_theta_names: δθ预设名称列表  
        f_base: 基础频率
        
    Returns:
        List[ExplorationResult]: 探索结果
    """
    from PetersenScale_Phi import PHI_PRESETS, DELTA_THETA_PRESETS
    
    # 过滤预设
    phi_presets = {k: v for k, v in PHI_PRESETS.items() if not phi_names or k in phi_names}
    dth_presets = {k: v for k, v in DELTA_THETA_PRESETS.items() if not delta_theta_names or k in delta_theta_names}
    
    print(f"🎯 探索特定预设组合:")
    print(f"   φ预设: {list(phi_presets.keys())}")
    print(f"   δθ预设: {list(dth_presets.keys())}")
    print(f"   F_base: {f_base}Hz")
    
    explorer = ParameterSpaceExplorer(f_base_candidates=[f_base])
    results = []
    
    for phi_name, phi_value in phi_presets.items():
        for dth_name, dth_value in dth_presets.items():
            from .core.parameter_explorer import ExplorationParameters
            
            params = ExplorationParameters(
                phi_name=phi_name,
                phi_value=phi_value,
                delta_theta_name=dth_name,
                delta_theta_value=dth_value,
                f_base=f_base
            )
            
            result = explorer.explore_single_combination(params)
            results.append(result)
            
            status = "✅" if result.success else "❌"
            print(f"   {status} {phi_name} × {dth_name}: {len(result.entries) if result.success else 0} 音符")
    
    return results

if __name__ == "__main__":
    # 演示用法
    print("🎼 Petersen音律系统探索器 - 演示模式")
    
    # 快速演示探索
    print("\n1️⃣ 快速探索演示 (部分参数):")
    demo_config = ExplorationConfiguration(
        f_base_candidates=[220.0, 261.63],  # 只测试A3和C4
        enable_audio_testing=False,  # 演示模式关闭音频测试
        enable_detailed_analysis=True,
        audio_test_sample_size=5
    )
    
    explorer = PetersenMainExplorer(demo_config)
    
    # 添加简单的进度显示
    def simple_progress(stage, current, total, data):
        if current % 10 == 0 or current == total:
            print(f"   📊 {stage}: {current}/{total} ({current/total*100:.1f}%)")
    
    explorer.add_progress_callback(simple_progress)
    
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
            print(f"   {i}. {params.phi_name} × {params.delta_theta_name} (评分: {evaluation.weighted_total_score:.3f})")
        
        # 导出顶级系统
        print("\n📁 导出前3名系统...")
        exported = explorer.export_top_systems_for_player(3)
        print(f"   导出完成: {len(exported)} 个文件")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断探索")
    except Exception as e:
        print(f"\n❌ 演示过程出错: {str(e)}")
        import traceback
        traceback.print_exc()