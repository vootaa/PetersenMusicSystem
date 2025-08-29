"""
Petersen音律探索报告生成器
生成详细的分析报告和可视化结果
"""
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import json
import csv
from pathlib import Path
from datetime import datetime
import sys

# 添加父级路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

try:
    # 尝试相对导入
    from ..core.parameter_explorer import ExplorationResult
    from ..core.evaluation_framework import ComprehensiveEvaluation
    from ..core.classification_system import ClassificationResult
    from ..audio.playback_tester import SystemPlaybackAssessment
except ImportError:
    # 回退到绝对导入
    try:
        from core.parameter_explorer import ExplorationResult
        from core.evaluation_framework import ComprehensiveEvaluation
        from core.classification_system import ClassificationResult
        from audio.playback_tester import SystemPlaybackAssessment
    except ImportError:
        # 创建简化的替代类
        from typing import NamedTuple
        
        class ExplorationResult(NamedTuple):
            parameters: Any
            scale: Any
            entries: List
            success: bool
            basic_metrics: Dict
        
        class ComprehensiveEvaluation(NamedTuple):
            dimension_scores: Dict
            weighted_total_score: float
            category_recommendation: str
            application_suggestions: List
            strengths: List
            limitations: List
            overall_viability: str
        
        class ClassificationResult(NamedTuple):
            primary_category: Any
            confidence_score: float
        
        class SystemPlaybackAssessment(NamedTuple):
            overall_playability: float
            technical_score: float
            musical_score: float
            recommended_for_audio: bool

@dataclass
class ExplorationSummary:
    """探索总结"""
    total_combinations_tested: int
    successful_systems: int
    failed_systems: int
    exploration_duration: float
    top_systems: List[Dict[str, Any]]
    category_distribution: Dict[str, int]
    recommendation_summary: Dict[str, Any]

class PetersenExplorationReportGenerator:
    """Petersen探索报告生成器"""
    
    def __init__(self, output_dir: Path = None):
        """
        初始化报告生成器
        
        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = output_dir or Path("./reports")
        self.output_path = self.output_dir
        self.output_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        (self.output_dir / "detailed").mkdir(exist_ok=True)
        (self.output_dir / "summaries").mkdir(exist_ok=True)
        (self.output_dir / "data").mkdir(exist_ok=True)
        (self.output_dir / "audio_tests").mkdir(exist_ok=True)
    
    def generate_comprehensive_report(self,
                                    exploration_results: List[ExplorationResult],
                                    evaluations: Dict[str, ComprehensiveEvaluation] = None,
                                    classifications: Dict[str, ClassificationResult] = None,
                                    audio_assessments: Dict[str, SystemPlaybackAssessment] = None,
                                    report_name: str = None) -> Path:
        """
        生成综合探索报告
        
        Args:
            exploration_results: 探索结果列表
            evaluations: 评估结果字典
            classifications: 分类结果字典
            audio_assessments: 音频评估结果字典
            report_name: 报告名称
            
        Returns:
            Path: 生成的报告文件路径
        """
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"petersen_exploration_{timestamp}"
        
        print(f"📋 生成综合探索报告: {report_name}")
        
        # 创建报告目录
        report_dir = self.output_dir / report_name
        report_dir.mkdir(exist_ok=True)
        
        # 生成各部分报告
        self._generate_executive_summary(exploration_results, evaluations, 
                                       classifications, audio_assessments, report_dir)
        
        self._generate_detailed_analysis(exploration_results, evaluations,
                                       classifications, audio_assessments, report_dir)
        
        self._generate_data_exports(exploration_results, evaluations,
                                  classifications, audio_assessments, report_dir)
        
        self._generate_recommendations(exploration_results, evaluations,
                                     classifications, audio_assessments, report_dir)
        
        # 生成主报告索引
        main_report_path = self._generate_main_report_index(report_dir, report_name)
        
        print(f"✅ 报告生成完成: {main_report_path}")
        return main_report_path
    
    def _generate_executive_summary(self, exploration_results, evaluations, classifications, audio_assessments):
        """生成执行摘要"""
        with open(self.output_path / "executive_summary.md", "w", encoding="utf-8") as f:
            f.write("# PetersenExplorer 探索执行摘要\n\n")
            
            # 基本统计
            successful_results = [r for r in exploration_results if r.success]
            total_count = len(exploration_results)
            success_count = len(successful_results)
            
            f.write("## 📊 基本统计\n\n")
            
            # 修复格式化问题
            if total_count > 0:
                success_rate = (success_count / total_count) * 100
                f.write(f"- **总测试组合**: {total_count}\n")
                f.write(f"- **成功生成**: {success_count} ({success_rate:.1f}%)\n")
            else:
                f.write(f"- **总测试组合**: {total_count}\n")
                f.write(f"- **成功生成**: {success_count} (0.0%)\n")
            
            f.write(f"- **详细分析**: {len(evaluations)}\n")
            f.write(f"- **系统分类**: {len(classifications)}\n")
            f.write(f"- **音频测试**: {len(audio_assessments)}\n\n")
            
            # 分类分布
            if classifications:
                f.write("## 🏷️ 系统分类分布\n\n")
                category_counts = {}
                for classification in classifications.values():
                    category = classification.category if hasattr(classification, 'category') else "未分类"
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- **{category}**: {count} 个系统\n")
                f.write("\n")
            
            # 评估结果摘要
            if evaluations:
                f.write("## 🎯 评估结果摘要\n\n")
                scores = [eval_result.weighted_total_score if hasattr(eval_result, 'weighted_total_score') else 0 
                        for eval_result in evaluations.values()]
                
                if scores:
                    f.write(f"- **平均评分**: {sum(scores)/len(scores):.3f}\n")
                    f.write(f"- **最高评分**: {max(scores):.3f}\n")
                    f.write(f"- **最低评分**: {min(scores):.3f}\n")
            
            f.write("\n---\n")
            f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    def _generate_detailed_analysis(self, exploration_results: List[ExplorationResult],
                                  evaluations: Dict, classifications: Dict,
                                  audio_assessments: Dict, report_dir: Path):
        """生成详细分析报告"""
        analysis_dir = report_dir / "detailed_analysis"
        analysis_dir.mkdir(exist_ok=True)
        
        # φ值分析
        self._analyze_phi_presets(exploration_results, evaluations, analysis_dir)
        
        # δθ值分析
        self._analyze_delta_theta_presets(exploration_results, evaluations, analysis_dir)
        
        # F_base分析
        self._analyze_f_base_effects(exploration_results, evaluations, analysis_dir)
        
        # 音乐特性分析
        if evaluations:
            self._analyze_musical_characteristics(evaluations, analysis_dir)
        
        # 音频测试分析
        if audio_assessments:
            self._analyze_audio_performance(audio_assessments, analysis_dir)
    
    def _analyze_phi_presets(self, exploration_results: List[ExplorationResult],
                           evaluations: Dict, analysis_dir: Path):
        """分析φ预设的影响"""
        phi_analysis_path = analysis_dir / "phi_presets_analysis.md"
        
        # 按φ值分组
        phi_groups = {}
        for result in exploration_results:
            if result.success:
                phi_name = result.parameters.phi_name
                if phi_name not in phi_groups:
                    phi_groups[phi_name] = []
                phi_groups[phi_name].append(result)
        
        with open(phi_analysis_path, 'w', encoding='utf-8') as f:
            f.write("# φ值预设分析\n\n")
            
            for phi_name, results in sorted(phi_groups.items()):
                f.write(f"## φ = {phi_name} ({results[0].parameters.phi_value:.6f})\n\n")
                
                # 统计信息
                f.write(f"- **成功组合数**: {len(results)}\n")
                
                # 音符数量统计
                entry_counts = [len(r.entries) for r in results]
                if entry_counts:
                    f.write(f"- **音符数量范围**: {min(entry_counts)} - {max(entry_counts)}\n")
                    f.write(f"- **平均音符数**: {sum(entry_counts)/len(entry_counts):.1f}\n")
                
                # 音程特性
                if results[0].basic_metrics and 'avg_interval_cents' in results[0].basic_metrics:
                    avg_intervals = [r.basic_metrics['avg_interval_cents'] for r in results 
                                   if r.basic_metrics and 'avg_interval_cents' in r.basic_metrics]
                    if avg_intervals:
                        f.write(f"- **平均音程**: {sum(avg_intervals)/len(avg_intervals):.1f} 音分\n")
                
                # 评估得分统计
                if evaluations:
                    eval_scores = []
                    for result in results:
                        result_key = self._get_result_key(result)
                        if result_key in evaluations:
                            eval_scores.append(evaluations[result_key].weighted_total_score)
                    
                    if eval_scores:
                        f.write(f"- **平均评估得分**: {sum(eval_scores)/len(eval_scores):.3f}\n")
                        f.write(f"- **最高评估得分**: {max(eval_scores):.3f}\n")
                
                f.write("\n")
    
    def _analyze_delta_theta_presets(self, exploration_results: List[ExplorationResult],
                                   evaluations: Dict, analysis_dir: Path):
        """分析δθ预设的影响"""
        dth_analysis_path = analysis_dir / "delta_theta_presets_analysis.md"
        
        # 按δθ值分组
        dth_groups = {}
        for result in exploration_results:
            if result.success:
                dth_name = result.parameters.delta_theta_name
                if dth_name not in dth_groups:
                    dth_groups[dth_name] = []
                dth_groups[dth_name].append(result)
        
        with open(dth_analysis_path, 'w', encoding='utf-8') as f:
            f.write("# δθ值预设分析\n\n")
            
            for dth_name, results in sorted(dth_groups.items()):
                f.write(f"## δθ = {dth_name} ({results[0].parameters.delta_theta_value}°)\n\n")
                
                # 类似φ值的统计分析
                f.write(f"- **成功组合数**: {len(results)}\n")
                
                entry_counts = [len(r.entries) for r in results]
                if entry_counts:
                    f.write(f"- **音符数量范围**: {min(entry_counts)} - {max(entry_counts)}\n")
                    f.write(f"- **平均音符数**: {sum(entry_counts)/len(entry_counts):.1f}\n")
                
                f.write("\n")
    
    def _generate_data_exports(self, exploration_results: List[ExplorationResult],
                             evaluations: Dict, classifications: Dict,
                             audio_assessments: Dict, report_dir: Path):
        """生成数据导出文件"""
        data_dir = report_dir / "data_exports"
        data_dir.mkdir(exist_ok=True)
        
        # CSV格式的完整数据
        self._export_complete_data_csv(exploration_results, evaluations, 
                                     classifications, audio_assessments, data_dir)
        
        # JSON格式的详细数据
        self._export_detailed_data_json(exploration_results, evaluations,
                                      classifications, audio_assessments, data_dir)
        
        # 音阶文件导出
        self._export_scale_files(exploration_results, data_dir)
    
    def _export_complete_data_csv(self, exploration_results: List[ExplorationResult],
                                evaluations: Dict, classifications: Dict,
                                audio_assessments: Dict, data_dir: Path):
        """导出完整数据为CSV"""
        csv_path = data_dir / "complete_exploration_data.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = [
                'phi_name', 'phi_value', 'delta_theta_name', 'delta_theta_value', 'f_base',
                'success', 'entry_count', 'min_freq', 'max_freq',
                'avg_interval_cents', 'micro_interval_ratio', 'large_interval_ratio'
            ]
            
            if evaluations:
                headers.extend([
                    'weighted_total_score', 'traditional_compatibility', 'microtonal_potential',
                    'experimental_innovation', 'therapeutic_value', 'harmonic_richness'
                ])
            
            if classifications:
                headers.extend(['primary_category', 'confidence_score'])
            
            if audio_assessments:
                headers.extend(['overall_playability', 'technical_score', 'musical_score', 'audio_recommended'])
            
            writer.writerow(headers)
            
            # 写入数据行
            for result in exploration_results:
                row = [
                    result.parameters.phi_name,
                    result.parameters.phi_value,
                    result.parameters.delta_theta_name,
                    result.parameters.delta_theta_value,
                    result.parameters.f_base,
                    result.success,
                    len(result.entries) if result.success else 0
                ]
                
                if result.success and result.entries:
                    frequencies = [e.freq for e in result.entries]
                    row.extend([min(frequencies), max(frequencies)])
                else:
                    row.extend([0, 0])
                
                # 添加基础指标
                if result.basic_metrics:
                    row.extend([
                        result.basic_metrics.get('avg_interval_cents', 0),
                        result.basic_metrics.get('micro_interval_ratio', 0),
                        result.basic_metrics.get('large_interval_ratio', 0)
                    ])
                else:
                    row.extend([0, 0, 0])
                
                # 添加评估数据
                result_key = self._get_result_key(result)
                
                if evaluations and result_key in evaluations:
                    eval_result = evaluations[result_key]
                    row.extend([
                        eval_result.weighted_total_score,
                        eval_result.dimension_scores['traditional_compatibility'].score,
                        eval_result.dimension_scores['microtonal_potential'].score,
                        eval_result.dimension_scores['experimental_innovation'].score,
                        eval_result.dimension_scores['therapeutic_value'].score,
                        eval_result.dimension_scores['harmonic_richness'].score
                    ])
                elif evaluations:
                    row.extend([0] * 6)
                
                # 添加分类数据
                if classifications and result_key in classifications:
                    class_result = classifications[result_key]
                    row.extend([
                        class_result.primary_category.value,
                        class_result.confidence_score
                    ])
                elif classifications:
                    row.extend(['', 0])
                
                # 添加音频测试数据
                if audio_assessments and result_key in audio_assessments:
                    audio_result = audio_assessments[result_key]
                    row.extend([
                        audio_result.overall_playability,
                        audio_result.technical_score,
                        audio_result.musical_score,
                        audio_result.recommended_for_audio
                    ])
                elif audio_assessments:
                    row.extend([0, 0, 0, False])
                
                writer.writerow(row)
    
    def _identify_top_systems(self, successful_results: List[ExplorationResult],
                            evaluations: Dict, count: int = 10) -> List[Dict[str, Any]]:
        """识别前N名系统"""
        systems = []
        
        for result in successful_results:
            result_key = self._get_result_key(result)
            system = {'exploration_result': result}
            
            if evaluations and result_key in evaluations:
                system['evaluation'] = evaluations[result_key]
            
            systems.append(system)
        
        # 按评估得分排序
        if evaluations:
            systems.sort(key=lambda x: x.get('evaluation', type('obj', (object,), {'weighted_total_score': 0})).weighted_total_score, reverse=True)
        else:
            # 如果没有评估，按音符数量排序
            systems.sort(key=lambda x: len(x['exploration_result'].entries), reverse=True)
        
        return systems[:count]
    
    def _get_result_key(self, result: ExplorationResult) -> str:
        """获取结果的唯一键"""
        params = result.parameters
        return f"{params.phi_name}_{params.delta_theta_name}_{params.f_base}"
    
    def _generate_key_findings(self, successful_results: List[ExplorationResult],
                             evaluations: Dict, classifications: Dict) -> str:
        """生成关键发现"""
        findings = []
        
        # 成功率发现
        total_systems = len(successful_results)
        findings.append(f"成功生成了 {total_systems} 个可用的音律系统，显示Petersen音律具有丰富的参数空间。")
        
        # 音符数量分布
        entry_counts = [len(r.entries) for r in successful_results]
        if entry_counts:
            avg_entries = sum(entry_counts) / len(entry_counts)
            max_entries = max(entry_counts)
            min_entries = min(entry_counts)
            findings.append(f"音符数量分布从 {min_entries} 到 {max_entries}，平均 {avg_entries:.1f} 个音符，展现了从简约到复杂的多样性。")
        
        # 评估发现
        if evaluations:
            high_traditional = sum(1 for e in evaluations.values() 
                                 if e.dimension_scores['traditional_compatibility'].score >= 0.7)
            high_experimental = sum(1 for e in evaluations.values() 
                                  if e.dimension_scores['experimental_innovation'].score >= 0.7)
            
            findings.append(f"发现 {high_traditional} 个传统兼容系统和 {high_experimental} 个高创新系统，证明Petersen音律既能传承传统又能开拓创新。")
        
        return "\n".join(f"- {finding}" for finding in findings)
    
    def _generate_application_recommendations(self, top_systems: List[Dict[str, Any]]) -> str:
        """生成应用建议"""
        recommendations = []
        
        if not top_systems:
            return "- 暂无足够数据生成应用建议。"
        
        # 传统音乐应用
        traditional_systems = [s for s in top_systems 
                             if 'evaluation' in s and 
                             s['evaluation'].dimension_scores['traditional_compatibility'].score >= 0.7]
        if traditional_systems:
            recommendations.append("**传统音乐应用**: 发现多个高传统兼容性系统，适合古典音乐编曲和室内乐创作。")
        
        # 实验音乐应用
        experimental_systems = [s for s in top_systems 
                              if 'evaluation' in s and 
                              s['evaluation'].dimension_scores['experimental_innovation'].score >= 0.7]
        if experimental_systems:
            recommendations.append("**实验音乐应用**: 识别出创新性系统，适合现代作曲和电子音乐制作。")
        
        # 教育应用
        moderate_systems = [s for s in top_systems 
                          if len(s['exploration_result'].entries) >= 8 and len(s['exploration_result'].entries) <= 20]
        if moderate_systems:
            recommendations.append("**教育应用**: 中等复杂度系统适合音乐教育和听力训练。")
        
        return "\n".join(f"- {rec}" for rec in recommendations)
    
    def _generate_main_report_index(self, report_dir: Path, report_name: str) -> Path:
        """生成主报告索引"""
        index_path = report_dir / "README.md"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(f"# {report_name} - Petersen音律系统探索报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 📋 报告结构\n\n")
            f.write("### 核心报告\n")
            f.write("- [执行摘要](executive_summary.md) - 关键发现和推荐\n")
            f.write("- [详细分析](detailed_analysis/) - 深度参数分析\n")
            f.write("- [应用建议](recommendations.md) - 实用指导\n\n")
            
            f.write("### 数据文件\n")
            f.write("- [数据导出](data_exports/) - CSV和JSON格式数据\n")
            f.write("- [音阶文件](data_exports/scale_files/) - 可导入的音阶文件\n\n")
            
            f.write("### 技术文档\n")
            f.write("- [方法论](methodology.md) - 评估方法和标准\n")
            f.write("- [参数说明](parameter_reference.md) - φ和δθ预设详解\n\n")
            
            f.write("## 🎯 快速导航\n\n")
            f.write("- **寻找最佳系统**: 查看[执行摘要](executive_summary.md)的优秀系统推荐\n")
            f.write("- **了解参数影响**: 查看[详细分析](detailed_analysis/)\n")
            f.write("- **获取使用建议**: 查看[应用建议](recommendations.md)\n")
            f.write("- **下载数据**: 查看[数据导出](data_exports/)\n")
        
        return index_path
    
    # 其他辅助方法...
    def _export_detailed_data_json(self, exploration_results, evaluations, 
                                 classifications, audio_assessments, data_dir):
        """导出详细JSON数据"""
        # 实现JSON导出逻辑
        pass
    
    def _export_scale_files(self, exploration_results, data_dir):
        """导出音阶文件"""
        # 实现音阶文件导出逻辑
        pass
    
    def _analyze_f_base_effects(self, exploration_results, evaluations, analysis_dir):
        """分析F_base效应"""
        # 实现F_base分析逻辑
        pass
    
    def _analyze_musical_characteristics(self, evaluations, analysis_dir):
        """分析音乐特性"""
        # 实现音乐特性分析逻辑
        pass
    
    def _analyze_audio_performance(self, audio_assessments, analysis_dir):
        """分析音频性能"""
        # 实现音频性能分析逻辑
        pass