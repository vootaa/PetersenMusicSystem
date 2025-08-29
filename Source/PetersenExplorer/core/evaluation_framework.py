"""
Petersen音律多维度评估框架
实现传统音乐理论、非平均律理论、创新潜力等多重评估标准
"""
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field 
from enum import Enum

import sys
from pathlib import Path

# 添加父级路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from .characteristic_analyzer import ScaleCharacteristics, IntervalAnalysis, IntervalQuality

class EvaluationDimension(Enum):
    """评估维度"""
    TRADITIONAL_COMPATIBILITY = "traditional_compatibility"
    MICROTONAL_POTENTIAL = "microtonal_potential"
    WORLD_MUSIC_AFFINITY = "world_music_affinity"
    EXPERIMENTAL_INNOVATION = "experimental_innovation"
    THERAPEUTIC_VALUE = "therapeutic_value"
    HARMONIC_RICHNESS = "harmonic_richness"
    MELODIC_EXPRESSIVENESS = "melodic_expressiveness"
    TECHNICAL_FEASIBILITY = "technical_feasibility"

@dataclass
class DimensionScore:
    """维度评分"""
    score: float  # 0-1
    confidence: float  # 评估置信度 0-1
    details: Dict[str, Any] = field(default_factory=dict)  # 评分详情

@dataclass
class EvaluationScore:
    """单项评估得分"""
    dimension: EvaluationDimension
    score: float  # 0-1
    confidence: float  # 评估置信度 0-1
    reasoning: str  # 评分理由
    details: Dict[str, Any]  # 详细数据

@dataclass
class ComprehensiveEvaluation:
    """综合评估结果"""
    dimension_scores: Dict[str, DimensionScore]
    weighted_total_score: float
    category_recommendation: str = ""
    application_suggestions: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    overall_viability: str = "" # "high", "medium", "low", "experimental"
    note_count: int = 0 

class MultiDimensionalEvaluator:
    """多维度评估器"""
    
    def __init__(self):
        # 评估权重配置（可调整）
        self.dimension_weights = {
            EvaluationDimension.TRADITIONAL_COMPATIBILITY: 0.15,
            EvaluationDimension.MICROTONAL_POTENTIAL: 0.15,
            EvaluationDimension.WORLD_MUSIC_AFFINITY: 0.10,
            EvaluationDimension.EXPERIMENTAL_INNOVATION: 0.20,
            EvaluationDimension.THERAPEUTIC_VALUE: 0.10,
            EvaluationDimension.HARMONIC_RICHNESS: 0.15,
            EvaluationDimension.MELODIC_EXPRESSIVENESS: 0.10,
            EvaluationDimension.TECHNICAL_FEASIBILITY: 0.05
        }
        
        # 传统音程参考
        self.traditional_intervals_cents = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200]
        
        # 世界音乐音程参考
        self.world_music_intervals = {
            'arabic_quarter_tones': [0, 50, 100, 150, 200, 250, 300, 350, 400],
            'indian_shrutis': [0, 90, 112, 182, 204, 294, 316, 386, 408, 498, 520, 590, 612, 702, 724, 794, 816, 906, 928, 996, 1018, 1108],
            'gamelan_pelog': [0, 100, 300, 700, 900, 1200],
            'gamelan_slendro': [0, 240, 480, 720, 960, 1200]
        }
    
    def evaluate_comprehensive(self, characteristics) -> ComprehensiveEvaluation:
        """执行综合评估"""
        try:
            dimension_scores = {}
            
            # 使用标准化的维度名称
            standard_dimensions = {
                'harmonic_complexity': self._evaluate_harmonic_complexity,
                'melodic_potential': self._evaluate_melodic_potential,
                'compositional_versatility': self._evaluate_compositional_versatility,
                'performance_difficulty': self._evaluate_performance_difficulty,
                'theoretical_interest': self._evaluate_theoretical_interest,
                'practical_usability': self._evaluate_practical_usability
            }
            
            # 计算各维度分数
            for dimension_name, evaluator in standard_dimensions.items():
                try:
                    score = evaluator(characteristics)
                    confidence = 0.8  # 默认置信度
                    
                    dimension_scores[dimension_name] = DimensionScore(
                        score=score,
                        confidence=confidence,
                        details={'method': evaluator.__name__}
                    )
                except Exception as e:
                    print(f"维度 {dimension_name} 评估失败: {e}")
                    dimension_scores[dimension_name] = DimensionScore(
                        score=0.5,
                        confidence=0.3,
                        details={'error': str(e)}
                    )
            
            # 计算加权总分
            weights = {
                'harmonic_complexity': 0.2,
                'melodic_potential': 0.2,
                'compositional_versatility': 0.15,
                'performance_difficulty': 0.15,
                'theoretical_interest': 0.15,
                'practical_usability': 0.15
            }
            
            weighted_total = sum(
                dimension_scores[dim].score * weight 
                for dim, weight in weights.items()
                if dim in dimension_scores
            )
            
            return ComprehensiveEvaluation(
                dimension_scores=dimension_scores,
                weighted_total_score=weighted_total,
                note_count=len(characteristics.get('entries', [])),
                application_suggestions=[],
                strengths=[],
                limitations=[],
                overall_viability="experimental" if weighted_total < 0.6 else "viable"
            )
            
        except Exception as e:
            print(f"综合评估失败: {e}")
            # 返回默认评估
            return ComprehensiveEvaluation(
                dimension_scores={},
                weighted_total_score=0.5,
                note_count=0,
                application_suggestions=[],
                strengths=[],
                limitations=[f"评估失败: {e}"],
                overall_viability="unknown"
            )

    def _create_default_characteristics(self):
        """创建默认特性对象"""
        from types import SimpleNamespace
        return SimpleNamespace(
            entry_count=12,
            frequency_range=(220, 440),
            interval_analyses=[],
            traditional_compatibility=0.5,
            experimental_potential=0.7
        )

    def _simple_traditional_eval(self, characteristics) -> EvaluationScore:
        """简化的传统兼容性评估"""
        score = getattr(characteristics, 'traditional_compatibility', 0.5)
        return EvaluationScore(
            dimension=EvaluationDimension.TRADITIONAL_COMPATIBILITY,
            score=score, 
            confidence=0.7, 
            reasoning=f"传统兼容性: {score:.1%}", 
            details={}
        )

    def _simple_microtonal_eval(self, characteristics) -> EvaluationScore:
        """简化的微分音评估"""
        entry_count = getattr(characteristics, 'entry_count', 12)
        score = min(1.0, (entry_count - 12) / 20) if entry_count > 12 else 0.3
        return EvaluationScore(
            dimension=EvaluationDimension.MICROTONAL_POTENTIAL,
            score=score, 
            confidence=0.6, 
            reasoning=f"微分音潜力: {score:.1%}", 
            details={}
        )

    def _simple_innovation_eval(self, characteristics) -> EvaluationScore:
        """简化的创新性评估"""
        score = getattr(characteristics, 'experimental_potential', 0.7)
        return EvaluationScore(
            dimension=EvaluationDimension.EXPERIMENTAL_INNOVATION,
            score=score, 
            confidence=0.6, 
            reasoning=f"创新性: {score:.1%}", 
            details={}
        )

    def _simple_harmonic_eval(self, characteristics) -> EvaluationScore:
        """简化的和声评估"""
        entry_count = getattr(characteristics, 'entry_count', 12)
        score = min(1.0, entry_count / 15) if entry_count >= 3 else 0.2
        return EvaluationScore(
            dimension=EvaluationDimension.HARMONIC_RICHNESS,
            score=score, 
            confidence=0.5, 
            reasoning=f"和声丰富度: {score:.1%}", 
            details={}
        )

    def _simple_technical_eval(self, characteristics) -> EvaluationScore:
        """简化的技术可行性评估"""
        freq_range = getattr(characteristics, 'frequency_range', (220, 440))
        if 100 <= freq_range[0] <= 400 and 300 <= freq_range[1] <= 2000:
            score = 0.9
        else:
            score = 0.6
        return EvaluationScore(
            dimension=EvaluationDimension.TECHNICAL_FEASIBILITY,
            score=score, 
            confidence=0.9, 
            reasoning=f"技术可行性: {score:.1%}", 
            details={}
        )
    
    def evaluate_comprehensive_detailed(self, characteristics: ScaleCharacteristics) -> ComprehensiveEvaluation:
        """
        执行详细综合评估 - 完整版本
        
        Args:
            characteristics: 音阶特性
            
        Returns:
            ComprehensiveEvaluation: 综合评估结果
        """
        dimension_scores = {}
        
        # 逐项评估
        dimension_scores[EvaluationDimension.TRADITIONAL_COMPATIBILITY] = \
            self._evaluate_traditional_compatibility(characteristics)
        
        dimension_scores[EvaluationDimension.MICROTONAL_POTENTIAL] = \
            self._evaluate_microtonal_potential(characteristics)
        
        dimension_scores[EvaluationDimension.WORLD_MUSIC_AFFINITY] = \
            self._evaluate_world_music_affinity(characteristics)
        
        dimension_scores[EvaluationDimension.EXPERIMENTAL_INNOVATION] = \
            self._evaluate_experimental_innovation(characteristics)
        
        dimension_scores[EvaluationDimension.THERAPEUTIC_VALUE] = \
            self._evaluate_therapeutic_value(characteristics)
        
        dimension_scores[EvaluationDimension.HARMONIC_RICHNESS] = \
            self._evaluate_harmonic_richness(characteristics)
        
        dimension_scores[EvaluationDimension.MELODIC_EXPRESSIVENESS] = \
            self._evaluate_melodic_expressiveness(characteristics)
        
        dimension_scores[EvaluationDimension.TECHNICAL_FEASIBILITY] = \
            self._evaluate_technical_feasibility(characteristics)
        
        # 计算加权总分
        weighted_total_score = sum(
            score.score * self.dimension_weights[dimension]
            for dimension, score in dimension_scores.items()
        )
        
        # 生成推荐和建议
        category_recommendation = self._determine_category(dimension_scores, weighted_total_score)
        application_suggestions = self._generate_application_suggestions(dimension_scores)
        strengths = self._identify_strengths(dimension_scores)
        limitations = self._identify_limitations(dimension_scores)
        overall_viability = self._assess_overall_viability(weighted_total_score, dimension_scores)
        
        return ComprehensiveEvaluation(
            dimension_scores=dimension_scores,
            weighted_total_score=weighted_total_score,
            category_recommendation=category_recommendation,
            application_suggestions=application_suggestions,
            strengths=strengths,
            limitations=limitations,
            overall_viability=overall_viability
        )
    
    def _evaluate_traditional_compatibility(self, characteristics: ScaleCharacteristics) -> EvaluationScore:
        """评估传统音乐兼容性"""
        if not characteristics.interval_analyses:
            return EvaluationScore(
                dimension=EvaluationDimension.TRADITIONAL_COMPATIBILITY,
                score=0.0,
                confidence=1.0,
                reasoning="无音程数据",
                details={}
            )
        
        # 计算与传统音程的匹配度
        traditional_matches = 0
        close_matches = 0
        
        for analysis in characteristics.interval_analyses:
            cents = analysis.cents
            
            # 精确匹配（±10音分）
            for trad_cents in self.traditional_intervals_cents:
                if abs(cents - trad_cents) <= 10:
                    traditional_matches += 1
                    break
            
            # 接近匹配（±25音分）
            for trad_cents in self.traditional_intervals_cents:
                if abs(cents - trad_cents) <= 25:
                    close_matches += 1
                    break
        
        total_intervals = len(characteristics.interval_analyses)
        exact_ratio = traditional_matches / total_intervals
        close_ratio = close_matches / total_intervals
        
        # 综合评分
        score = (exact_ratio * 0.8 + close_ratio * 0.2)
        
        # 考虑音程自然度
        avg_naturalness = sum(a.naturalness_score for a in characteristics.interval_analyses) / total_intervals
        score = (score * 0.7 + avg_naturalness * 0.3)
        
        details = {
            'exact_matches': traditional_matches,
            'close_matches': close_matches,
            'total_intervals': total_intervals,
            'exact_ratio': exact_ratio,
            'close_ratio': close_ratio,
            'avg_naturalness': avg_naturalness
        }
        
        if score >= 0.7:
            reasoning = f"高度兼容：{exact_ratio:.1%}精确匹配，{close_ratio:.1%}接近匹配"
        elif score >= 0.4:
            reasoning = f"中等兼容：{exact_ratio:.1%}精确匹配，{close_ratio:.1%}接近匹配"
        else:
            reasoning = f"低兼容性：{exact_ratio:.1%}精确匹配，{close_ratio:.1%}接近匹配"
        
        return EvaluationScore(
            dimension=EvaluationDimension.TRADITIONAL_COMPATIBILITY,
            score=score,
            confidence=0.9,
            reasoning=reasoning,
            details=details
        )
    
    def _evaluate_microtonal_potential(self, characteristics: ScaleCharacteristics) -> EvaluationScore:
        """评估微分音潜力"""
        if not characteristics.interval_analyses:
            return EvaluationScore(
                dimension=EvaluationDimension.MICROTONAL_POTENTIAL,
                score=0.0,
                confidence=1.0,
                reasoning="无音程数据",
                details={}
            )
        
        # 统计微分音特征
        microtonal_intervals = sum(1 for a in characteristics.interval_analyses 
                                 if a.quality == IntervalQuality.MICROTONE)
        quarter_tone_intervals = sum(1 for a in characteristics.interval_analyses 
                                   if 40 <= a.cents <= 60)  # 1/4音附近
        
        total_intervals = len(characteristics.interval_analyses)
        microtonal_ratio = microtonal_intervals / total_intervals
        quarter_tone_ratio = quarter_tone_intervals / total_intervals
        
        # 音程密度（微分音系统通常有更多音符）
        density_bonus = min(0.3, (characteristics.entry_count - 12) / 50) if characteristics.entry_count > 12 else 0
        
        # 音程变化平滑度
        cents_values = [a.cents for a in characteristics.interval_analyses]
        if len(cents_values) > 1:
            cents_std = math.sqrt(sum((x - sum(cents_values)/len(cents_values))**2 for x in cents_values) / len(cents_values))
            smoothness_score = max(0, 1 - cents_std / 200)  # 标准差越小越平滑
        else:
            smoothness_score = 0
        
        # 综合评分
        score = (microtonal_ratio * 0.4 + quarter_tone_ratio * 0.3 + 
                density_bonus + smoothness_score * 0.3)
        score = min(1.0, score)
        
        details = {
            'microtonal_intervals': microtonal_intervals,
            'quarter_tone_intervals': quarter_tone_intervals,
            'total_intervals': total_intervals,
            'microtonal_ratio': microtonal_ratio,
            'quarter_tone_ratio': quarter_tone_ratio,
            'density_bonus': density_bonus,
            'smoothness_score': smoothness_score
        }
        
        if score >= 0.7:
            reasoning = f"优秀微分音系统：{microtonal_ratio:.1%}微分音，密度高"
        elif score >= 0.4:
            reasoning = f"中等微分音潜力：{microtonal_ratio:.1%}微分音"
        else:
            reasoning = f"有限微分音特征：{microtonal_ratio:.1%}微分音"
        
        return EvaluationScore(
            dimension=EvaluationDimension.MICROTONAL_POTENTIAL,
            score=score,
            confidence=0.8,
            reasoning=reasoning,
            details=details
        )
    
    def _evaluate_world_music_affinity(self, characteristics: ScaleCharacteristics) -> EvaluationScore:
        """评估世界音乐亲和性"""
        if not characteristics.interval_analyses:
            return EvaluationScore(
                dimension=EvaluationDimension.WORLD_MUSIC_AFFINITY,
                score=0.0,
                confidence=1.0,
                reasoning="无音程数据",
                details={}
            )
        
        affinity_scores = {}
        
        for culture, intervals in self.world_music_intervals.items():
            matches = 0
            for analysis in characteristics.interval_analyses:
                for ref_cents in intervals:
                    if abs(analysis.cents - ref_cents) <= 20:  # ±20音分容差
                        matches += 1
                        break
            
            affinity_ratio = matches / len(characteristics.interval_analyses)
            affinity_scores[culture] = affinity_ratio
        
        # 最高亲和性作为主要得分
        max_affinity = max(affinity_scores.values())
        
        # 多文化兼容性奖励
        high_affinity_count = sum(1 for score in affinity_scores.values() if score >= 0.3)
        multicultural_bonus = min(0.2, high_affinity_count * 0.05)
        
        score = min(1.0, max_affinity + multicultural_bonus)
        
        best_culture = max(affinity_scores.items(), key=lambda x: x[1])
        
        details = {
            'affinity_scores': affinity_scores,
            'max_affinity': max_affinity,
            'best_culture': best_culture[0],
            'best_affinity_score': best_culture[1],
            'multicultural_bonus': multicultural_bonus
        }
        
        reasoning = f"与{best_culture[0]}音乐最亲和({best_culture[1]:.1%}匹配)"
        
        return EvaluationScore(
            dimension=EvaluationDimension.WORLD_MUSIC_AFFINITY,
            score=score,
            confidence=0.7,
            reasoning=reasoning,
            details=details
        )
    
    def _evaluate_experimental_innovation(self, characteristics: ScaleCharacteristics) -> EvaluationScore:
        """评估实验创新潜力"""
        # 创新性指标
        uniqueness_factors = []
        
        # 1. 音程分布的独特性
        interval_cents = [a.cents for a in characteristics.interval_analyses]
        if interval_cents:
            # 非常规音程比例
            unusual_intervals = sum(1 for cents in interval_cents 
                                  if not any(abs(cents - ref) <= 25 for ref in self.traditional_intervals_cents))
            unusual_ratio = unusual_intervals / len(interval_cents)
            uniqueness_factors.append(('unusual_intervals', unusual_ratio))
            
            # 音程跨度多样性
            span_variety = len(set(round(cents / 50) * 50 for cents in interval_cents)) / 24  # 24个50音分区间
            uniqueness_factors.append(('span_variety', span_variety))
        
        # 2. 音符密度创新性
        if characteristics.entry_count > 20:
            density_innovation = min(1.0, (characteristics.entry_count - 12) / 40)
        elif characteristics.entry_count < 8:
            density_innovation = min(1.0, (12 - characteristics.entry_count) / 8)
        else:
            density_innovation = 0.2  # 常规密度
        uniqueness_factors.append(('density_innovation', density_innovation))
        
        # 3. 和声复杂度
        if hasattr(characteristics, 'harmonic_potential'):
            harmonic_complexity = characteristics.harmonic_potential.harmonic_complexity
            uniqueness_factors.append(('harmonic_complexity', harmonic_complexity))
        
        # 综合创新评分
        if uniqueness_factors:
            score = sum(factor[1] for factor in uniqueness_factors) / len(uniqueness_factors)
        else:
            score = 0.0
        
        details = dict(uniqueness_factors)
        
        if score >= 0.7:
            reasoning = "高度创新：具有独特的音程结构和表达潜力"
        elif score >= 0.4:
            reasoning = "中等创新：在某些方面具有创新特征"
        else:
            reasoning = "有限创新：相对传统的音程结构"
        
        return EvaluationScore(
            dimension=EvaluationDimension.EXPERIMENTAL_INNOVATION,
            score=score,
            confidence=0.6,
            reasoning=reasoning,
            details=details
        )
    
    def _evaluate_therapeutic_value(self, characteristics: ScaleCharacteristics) -> EvaluationScore:
        """评估音乐治疗价值"""
        therapeutic_factors = []
        
        # 1. 协和音程比例（治疗音乐偏好协和）
        if characteristics.interval_analyses:
            consonant_count = sum(1 for a in characteristics.interval_analyses 
                                if a.consonance_score >= 0.6)
            consonant_ratio = consonant_count / len(characteristics.interval_analyses)
            therapeutic_factors.append(('consonance', consonant_ratio))
        
        # 2. 频率范围适宜性（中频段更适合治疗）
        freq_min, freq_max = characteristics.frequency_range
        if 100 <= freq_min <= 300 and 400 <= freq_max <= 1000:
            freq_suitability = 1.0
        elif 80 <= freq_min <= 400 and 300 <= freq_max <= 1200:
            freq_suitability = 0.8
        else:
            freq_suitability = 0.4
        therapeutic_factors.append(('frequency_suitability', freq_suitability))
        
        # 3. 音程平滑度（避免突兀跳跃）
        if characteristics.interval_analyses:
            large_leaps = sum(1 for a in characteristics.interval_analyses if a.cents > 400)
            leap_ratio = large_leaps / len(characteristics.interval_analyses)
            smoothness = 1.0 - leap_ratio
            therapeutic_factors.append(('smoothness', smoothness))
        
        # 4. 音符数量适中性（不过于复杂）
        if 8 <= characteristics.entry_count <= 20:
            complexity_suitability = 1.0
        elif 5 <= characteristics.entry_count <= 30:
            complexity_suitability = 0.7
        else:
            complexity_suitability = 0.3
        therapeutic_factors.append(('complexity_suitability', complexity_suitability))
        
        # 综合治疗价值评分
        score = sum(factor[1] for factor in therapeutic_factors) / len(therapeutic_factors)
        
        details = dict(therapeutic_factors)
        
        if score >= 0.7:
            reasoning = "优秀治疗潜力：协和、平滑、适中复杂度"
        elif score >= 0.5:
            reasoning = "中等治疗潜力：具备部分治疗特征"
        else:
            reasoning = "有限治疗潜力：可能过于复杂或不协和"
        
        return EvaluationScore(
            dimension=EvaluationDimension.THERAPEUTIC_VALUE,
            score=score,
            confidence=0.7,
            reasoning=reasoning,
            details=details
        )
    
    def _evaluate_harmonic_richness(self, characteristics: ScaleCharacteristics) -> EvaluationScore:
        """评估和声丰富度"""
        if not hasattr(characteristics, 'harmonic_potential'):
            return EvaluationScore(
                dimension=EvaluationDimension.HARMONIC_RICHNESS,
                score=0.0,
                confidence=0.5,
                reasoning="缺少和声分析数据",
                details={}
            )
        
        harmonic = characteristics.harmonic_potential
        
        # 和声评分因子
        factors = [
            ('chord_building', harmonic.chord_building_score),
            ('voice_leading', harmonic.voice_leading_score),
            ('consonant_ratio', harmonic.consonant_interval_ratio),
            ('complexity', min(1.0, harmonic.harmonic_complexity))
        ]
        
        # 加权平均
        weights = [0.3, 0.2, 0.3, 0.2]
        score = sum(f[1] * w for f, w in zip(factors, weights))
        
        details = dict(factors)
        details['recommended_chord_sizes'] = harmonic.recommended_chord_sizes
        
        if score >= 0.8:
            reasoning = "丰富和声：支持复杂和弦构建和流畅声部进行"
        elif score >= 0.6:
            reasoning = "中等和声：具备基本和声功能"
        else:
            reasoning = "有限和声：和声构建能力受限"
        
        return EvaluationScore(
            dimension=EvaluationDimension.HARMONIC_RICHNESS,
            score=score,
            confidence=0.8,
            reasoning=reasoning,
            details=details
        )
    
    def _evaluate_melodic_expressiveness(self, characteristics: ScaleCharacteristics) -> EvaluationScore:
        """评估旋律表达力"""
        if not hasattr(characteristics, 'melodic_characteristics'):
            return EvaluationScore(
                dimension=EvaluationDimension.MELODIC_EXPRESSIVENESS,
                score=0.0,
                confidence=0.5,
                reasoning="缺少旋律分析数据",
                details={}
            )
        
        melodic = characteristics.melodic_characteristics
        
        # 表达力评分因子
        factors = [
            ('flow', melodic.melodic_flow_score),
            ('expressive_range', melodic.expressive_range_score),
            ('singability', melodic.singability_score),
            ('step_motion_balance', abs(melodic.step_motion_ratio - 0.7))  # 理想级进比例约70%
        ]
        
        # 计算得分
        base_score = (factors[0][1] + factors[1][1] + factors[2][1]) / 3
        balance_penalty = factors[3][1] * 0.3
        score = max(0, base_score - balance_penalty)
        
        details = dict(factors)
        details['recommended_tempo'] = melodic.recommended_tempo_range
        
        if score >= 0.8:
            reasoning = "优秀表达力：流畅、富有表现力、易于演奏"
        elif score >= 0.6:
            reasoning = "良好表达力：具备基本旋律表达能力"
        else:
            reasoning = "有限表达力：旋律构建可能存在困难"
        
        return EvaluationScore(
            dimension=EvaluationDimension.MELODIC_EXPRESSIVENESS,
            score=score,
            confidence=0.8,
            reasoning=reasoning,
            details=details
        )
    
    def _evaluate_technical_feasibility(self, characteristics: ScaleCharacteristics) -> EvaluationScore:
        """评估技术可行性"""
        feasibility_factors = []
        
        # 1. 音符数量合理性
        if 5 <= characteristics.entry_count <= 50:
            count_feasibility = 1.0
        elif characteristics.entry_count <= 3 or characteristics.entry_count >= 100:
            count_feasibility = 0.2
        else:
            count_feasibility = 0.7
        feasibility_factors.append(('note_count', count_feasibility))
        
        # 2. 频率范围合理性
        freq_min, freq_max = characteristics.frequency_range
        if 50 <= freq_min <= 200 and 400 <= freq_max <= 2000:
            freq_feasibility = 1.0
        elif 20 <= freq_min <= 400 and 200 <= freq_max <= 4000:
            freq_feasibility = 0.8
        else:
            freq_feasibility = 0.5
        feasibility_factors.append(('frequency_range', freq_feasibility))
        
        # 3. 音程大小合理性
        if characteristics.interval_analyses:
            extreme_intervals = sum(1 for a in characteristics.interval_analyses 
                                  if a.cents < 5 or a.cents > 800)
            extreme_ratio = extreme_intervals / len(characteristics.interval_analyses)
            interval_feasibility = 1.0 - extreme_ratio
            feasibility_factors.append(('interval_feasibility', interval_feasibility))
        
        # 综合可行性
        score = sum(f[1] for f in feasibility_factors) / len(feasibility_factors)
        
        details = dict(feasibility_factors)
        
        if score >= 0.8:
            reasoning = "技术完全可行：所有参数在合理范围内"
        elif score >= 0.6:
            reasoning = "基本可行：可能需要特殊调整"
        else:
            reasoning = "技术挑战：存在实现困难"
        
        return EvaluationScore(
            dimension=EvaluationDimension.TECHNICAL_FEASIBILITY,
            score=score,
            confidence=0.9,
            reasoning=reasoning,
            details=details
        )
    
    def _determine_category(self, dimension_scores: Dict, total_score: float) -> str:
        """确定音律系统类别"""
        # 获取各维度得分
        traditional = dimension_scores[EvaluationDimension.TRADITIONAL_COMPATIBILITY].score
        microtonal = dimension_scores[EvaluationDimension.MICROTONAL_POTENTIAL].score
        world_music = dimension_scores[EvaluationDimension.WORLD_MUSIC_AFFINITY].score
        experimental = dimension_scores[EvaluationDimension.EXPERIMENTAL_INNOVATION].score
        therapeutic = dimension_scores[EvaluationDimension.THERAPEUTIC_VALUE].score
        
        # 分类逻辑
        if traditional >= 0.7:
            return "传统扩展型"
        elif microtonal >= 0.7:
            return "微分音探索型"
        elif world_music >= 0.6:
            return "世界音乐融合型"
        elif therapeutic >= 0.7:
            return "治疗功能型"
        elif experimental >= 0.7:
            return "实验前卫型"
        elif total_score >= 0.6:
            return "综合应用型"
        else:
            return "探索研究型"
    
    def _generate_application_suggestions(self, dimension_scores: Dict) -> List[str]:
        """生成应用建议"""
        suggestions = []
        
        for dimension, score in dimension_scores.items():
            if score.score >= 0.7:
                if dimension == EvaluationDimension.TRADITIONAL_COMPATIBILITY:
                    suggestions.append("适合传统乐器编曲和古典音乐改编")
                elif dimension == EvaluationDimension.MICROTONAL_POTENTIAL:
                    suggestions.append("适合现代微分音作品和电子音乐")
                elif dimension == EvaluationDimension.WORLD_MUSIC_AFFINITY:
                    suggestions.append("适合世界音乐融合和跨文化项目")
                elif dimension == EvaluationDimension.EXPERIMENTAL_INNOVATION:
                    suggestions.append("适合实验音乐和声音艺术创作")
                elif dimension == EvaluationDimension.THERAPEUTIC_VALUE:
                    suggestions.append("适合音乐治疗和冥想音乐")
                elif dimension == EvaluationDimension.HARMONIC_RICHNESS:
                    suggestions.append("适合复调音乐和和声探索")
                elif dimension == EvaluationDimension.MELODIC_EXPRESSIVENESS:
                    suggestions.append("适合独奏乐器和声乐作品")
        
        return suggestions if suggestions else ["适合理论研究和教学演示"]
    
    def _identify_strengths(self, dimension_scores: Dict) -> List[str]:
        """识别优势"""
        strengths = []
        
        for dimension, score in dimension_scores.items():
            if score.score >= 0.8:
                strengths.append(f"{dimension.value}: {score.reasoning}")
        
        return strengths
    
    def _identify_limitations(self, dimension_scores: Dict) -> List[str]:
        """识别局限性"""
        limitations = []
        
        for dimension, score in dimension_scores.items():
            if score.score <= 0.3:
                limitations.append(f"{dimension.value}: {score.reasoning}")
        
        return limitations
    
    def _assess_overall_viability(self, total_score: float, dimension_scores: Dict) -> str:
        """评估整体可行性"""
        feasibility = dimension_scores[EvaluationDimension.TECHNICAL_FEASIBILITY].score
        
        if total_score >= 0.8 and feasibility >= 0.7:
            return "high"
        elif total_score >= 0.6 and feasibility >= 0.5:
            return "medium"
        elif total_score >= 0.4 or feasibility >= 0.7:
            return "low"
        else:
            return "experimental"