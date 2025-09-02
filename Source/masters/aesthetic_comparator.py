"""
Petersen 美学对比分析器

专门进行不同数学参数组合的音乐美学对比分析，
量化参数对音乐效果的影响，建立数学与美学的映射关系。
"""

import sys
import time
import json
import itertools
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np

# 添加libs路径
current_dir = Path(__file__).parent
libs_dir = current_dir.parent / "libs"
if str(libs_dir) not in sys.path:
    sys.path.insert(0, str(libs_dir))

try:
    from petersen_scale import PetersenScale, PHI_PRESETS, DELTA_THETA_PRESETS
    from petersen_chord import PetersenChordExtender, CHORD_RATIOS
    from petersen_composer import PetersenAutoComposer, COMPOSITION_STYLES
except ImportError as e:
    print(f"⚠️ 导入基础模块失败: {e}")

class ComparisonDimension(Enum):
    """对比维度"""
    PHI_VALUES = "phi_values"
    DELTA_THETA_VALUES = "delta_theta_values"
    CHORD_COMBINATIONS = "chord_combinations"
    STYLE_VARIATIONS = "style_variations"
    COMPREHENSIVE = "comprehensive"

@dataclass
class AestheticMetrics:
    """美学指标"""
    harmonic_consonance: float = 0.0      # 和声协和度
    melodic_smoothness: float = 0.0       # 旋律流畅度
    rhythmic_interest: float = 0.0        # 节奏趣味性
    structural_coherence: float = 0.0     # 结构连贯性
    emotional_impact: float = 0.0         # 情感冲击力
    mathematical_elegance: float = 0.0    # 数学优雅度
    overall_beauty: float = 0.0           # 整体美感

@dataclass
class ComparisonResult:
    """对比结果"""
    comparison_id: str
    dimension: ComparisonDimension
    base_theme: str
    parameter_sets: List[Dict[str, Any]]
    aesthetic_scores: List[AestheticMetrics]
    ranking: List[int]  # 排名索引
    insights: List[str]
    recommendations: List[str]

class AestheticComparator:
    """美学对比分析器"""
    
    def __init__(self, master_studio):
        self.master_studio = master_studio
        self.comparison_history: List[ComparisonResult] = []
        print("✓ 美学对比分析器已初始化")
    
    def run_comparison(self, dimension: ComparisonDimension = ComparisonDimension.PHI_VALUES,
                      base_theme: str = "harmonic_beauty") -> ComparisonResult:
        """运行美学对比分析"""
        comparison_id = f"aesthetic_{int(time.time())}"
        
        print(f"🎨 开始美学对比分析: {dimension.value}")
        print(f"   基础主题: {base_theme}")
        
        # 生成对比参数集
        parameter_sets = self._generate_comparison_parameters(dimension)
        
        print(f"   对比组数: {len(parameter_sets)}")
        
        # 创建对比作品
        comparison_works = []
        for i, params in enumerate(parameter_sets, 1):
            print(f"\n🎼 创建对比作品 {i}/{len(parameter_sets)}...")
            work = self._create_comparison_work(params, base_theme)
            if work:
                comparison_works.append(work)
            else:
                print(f"   ❌ 对比作品 {i} 创建失败")
        
        # 美学评估
        print(f"\n📊 进行美学评估...")
        aesthetic_scores = []
        for work in comparison_works:
            score = self._evaluate_aesthetic_metrics(work)
            aesthetic_scores.append(score)
        
        # 排名分析
        ranking = self._calculate_ranking(aesthetic_scores)
        
        # 生成洞察和建议
        insights = self._generate_insights(parameter_sets, aesthetic_scores, ranking)
        recommendations = self._generate_recommendations(parameter_sets, aesthetic_scores, ranking)
        
        result = ComparisonResult(
            comparison_id=comparison_id,
            dimension=dimension,
            base_theme=base_theme,
            parameter_sets=parameter_sets,
            aesthetic_scores=aesthetic_scores,
            ranking=ranking,
            insights=insights,
            recommendations=recommendations
        )
        
        self.comparison_history.append(result)
        
        # 显示结果
        self._display_comparison_results(result)
        
        return result
    
    def _generate_comparison_parameters(self, dimension: ComparisonDimension) -> List[Dict[str, Any]]:
        """生成对比参数集"""
        if dimension == ComparisonDimension.PHI_VALUES:
            return [
                {"phi_name": "golden", "delta_theta_name": "15.0", "chord_set": "major_seventh"},
                {"phi_name": "octave", "delta_theta_name": "15.0", "chord_set": "major_seventh"},
                {"phi_name": "fifth", "delta_theta_name": "15.0", "chord_set": "major_seventh"},
                {"phi_name": "fourth", "delta_theta_name": "15.0", "chord_set": "major_seventh"}
            ]
        elif dimension == ComparisonDimension.DELTA_THETA_VALUES:
            return [
                {"phi_name": "golden", "delta_theta_name": "4.8", "chord_set": "major_seventh"},
                {"phi_name": "golden", "delta_theta_name": "8.0", "chord_set": "major_seventh"},
                {"phi_name": "golden", "delta_theta_name": "15.0", "chord_set": "major_seventh"},
                {"phi_name": "golden", "delta_theta_name": "24.0", "chord_set": "major_seventh"}
            ]
        elif dimension == ComparisonDimension.CHORD_COMBINATIONS:
            return [
                {"phi_name": "golden", "delta_theta_name": "15.0", "chord_set": "major_triad"},
                {"phi_name": "golden", "delta_theta_name": "15.0", "chord_set": "minor_seventh"},
                {"phi_name": "golden", "delta_theta_name": "15.0", "chord_set": "complex_jazz"},
                {"phi_name": "golden", "delta_theta_name": "15.0", "chord_set": "quartal"}
            ]
        else:
            # 综合对比
            return [
                {"phi_name": "golden", "delta_theta_name": "15.0", "chord_set": "major_seventh"},
                {"phi_name": "octave", "delta_theta_name": "24.0", "chord_set": "quartal"},
                {"phi_name": "fifth", "delta_theta_name": "4.8", "chord_set": "complex_jazz"}
            ]
    
    def _create_comparison_work(self, params: Dict[str, Any], base_theme: str):
        """创建对比作品"""
        try:
            # 创建音阶和组件
            scale = PetersenScale(
                F_base=55.0,
                phi=PHI_PRESETS[params["phi_name"]],
                delta_theta=DELTA_THETA_PRESETS[params["delta_theta_name"]]
            )
            
            chord_extender = PetersenChordExtender(
                petersen_scale=scale,
                chord_ratios=CHORD_RATIOS[params["chord_set"]]
            )
            
            composer = PetersenAutoComposer(
                petersen_scale=scale,
                chord_extender=chord_extender,
                composition_style=COMPOSITION_STYLES["balanced_journey"],
                bpm=120
            )
            
            # 生成4小节的对比作品
            composition = composer.compose(measures=4)
            
            return {
                "composition": composition,
                "parameters": params,
                "scale": scale,
                "chord_extender": chord_extender
            }
            
        except Exception as e:
            print(f"   ❌ 对比作品创建失败: {e}")
            return None
    
    def _evaluate_aesthetic_metrics(self, work: Dict[str, Any]) -> AestheticMetrics:
        """评估美学指标"""
        params = work["parameters"]
        
        # 和声协和度（基于φ值）
        phi_consonance = {
            "golden": 0.95, "octave": 0.90, "fifth": 0.85, "fourth": 0.80,
            "major_third": 0.75, "minor_third": 0.70
        }
        harmonic_consonance = phi_consonance.get(params["phi_name"], 0.60)
        
        # 旋律流畅度（基于δθ值）
        delta_theta_value = DELTA_THETA_PRESETS[params["delta_theta_name"]]
        if delta_theta_value <= 8.0:
            melodic_smoothness = 0.90
        elif delta_theta_value <= 15.0:
            melodic_smoothness = 0.80
        elif delta_theta_value <= 24.0:
            melodic_smoothness = 0.70
        else:
            melodic_smoothness = 0.60
        
        # 和弦复杂度贡献
        chord_complexity = {
            "major_triad": 0.60, "minor_triad": 0.65, "major_seventh": 0.80,
            "minor_seventh": 0.85, "complex_jazz": 0.95, "quartal": 0.75
        }
        rhythmic_interest = chord_complexity.get(params["chord_set"], 0.70)
        
        # 计算其他指标
        structural_coherence = (harmonic_consonance + melodic_smoothness) / 2
        emotional_impact = rhythmic_interest * 0.8 + harmonic_consonance * 0.2
        mathematical_elegance = harmonic_consonance * 0.6 + melodic_smoothness * 0.4
        overall_beauty = (harmonic_consonance + melodic_smoothness + rhythmic_interest + 
                         structural_coherence + emotional_impact + mathematical_elegance) / 6
        
        return AestheticMetrics(
            harmonic_consonance=harmonic_consonance,
            melodic_smoothness=melodic_smoothness,
            rhythmic_interest=rhythmic_interest,
            structural_coherence=structural_coherence,
            emotional_impact=emotional_impact,
            mathematical_elegance=mathematical_elegance,
            overall_beauty=overall_beauty
        )
    
    def _calculate_ranking(self, aesthetic_scores: List[AestheticMetrics]) -> List[int]:
        """计算排名"""
        # 按整体美感排序
        scores_with_index = [(score.overall_beauty, i) for i, score in enumerate(aesthetic_scores)]
        scores_with_index.sort(key=lambda x: x[0], reverse=True)
        
        return [index for _, index in scores_with_index]
    
    def _generate_insights(self, parameter_sets: List[Dict[str, Any]], 
                          aesthetic_scores: List[AestheticMetrics], 
                          ranking: List[int]) -> List[str]:
        """生成分析洞察"""
        insights = []
        
        best_index = ranking[0]
        best_params = parameter_sets[best_index]
        best_score = aesthetic_scores[best_index]
        
        insights.append(f"最佳美学效果组合: φ={best_params['phi_name']}, δθ={best_params['delta_theta_name']}, 和弦={best_params['chord_set']}")
        insights.append(f"最高整体美感得分: {best_score.overall_beauty:.3f}")
        
        # 分析各维度表现
        if best_score.harmonic_consonance > 0.85:
            insights.append("和声协和度表现优异，音程关系纯净和谐")
        
        if best_score.mathematical_elegance > 0.80:
            insights.append("数学优雅度突出，体现了数学与音乐的完美结合")
        
        return insights
    
    def _generate_recommendations(self, parameter_sets: List[Dict[str, Any]], 
                                aesthetic_scores: List[AestheticMetrics], 
                                ranking: List[int]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        best_params = parameter_sets[ranking[0]]
        
        recommendations.append(f"推荐使用φ值: {best_params['phi_name']} 以获得最佳和声效果")
        recommendations.append(f"建议δθ值设置: {best_params['delta_theta_name']} 确保旋律流畅性")
        recommendations.append(f"优选和弦配置: {best_params['chord_set']} 提升整体表现力")
        
        # 通用建议
        recommendations.append("黄金比例通常提供最自然的和声美感")
        recommendations.append("较小的δθ值创造更丰富的旋律变化")
        recommendations.append("复杂和弦增加现代感，简单和弦保持纯净性")
        
        return recommendations
    
    def _display_comparison_results(self, result: ComparisonResult):
        """显示对比结果"""
        print(f"\n🏆 美学对比分析结果")
        print("=" * 50)
        
        print(f"📊 排名结果:")
        for i, rank_index in enumerate(result.ranking, 1):
            params = result.parameter_sets[rank_index]
            score = result.aesthetic_scores[rank_index]
            
            print(f"   {i}. φ={params['phi_name']}, δθ={params['delta_theta_name']}, 和弦={params['chord_set']}")
            print(f"      整体美感: {score.overall_beauty:.3f}")
            print(f"      和声协和: {score.harmonic_consonance:.3f}, 旋律流畅: {score.melodic_smoothness:.3f}")
        
        print(f"\n💡 分析洞察:")
        for insight in result.insights:
            print(f"   • {insight}")
        
        print(f"\n📋 建议:")
        for rec in result.recommendations:
            print(f"   • {rec}")