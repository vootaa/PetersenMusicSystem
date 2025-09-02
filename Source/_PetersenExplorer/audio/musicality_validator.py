"""
Petersen音律音乐性验证器
评估音律系统的音乐表现力和实际应用价值
"""
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
import math
from pathlib import Path
import sys

# 添加父级路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent.parent))

from ..core.parameter_explorer import ExplorationResult

class MusicalContext(Enum):
    """音乐语境类型"""
    MELODIC = "melodic"              # 旋律性
    HARMONIC = "harmonic"            # 和声性
    RHYTHMIC = "rhythmic"            # 节奏性
    MODAL = "modal"                  # 调式性
    CHROMATIC = "chromatic"          # 半音性
    PENTATONIC = "pentatonic"        # 五声性

class MusicalInterval(Enum):
    """音乐音程类型"""
    UNISON = "unison"
    MINOR_SECOND = "minor_second"
    MAJOR_SECOND = "major_second"
    MINOR_THIRD = "minor_third"
    MAJOR_THIRD = "major_third"
    PERFECT_FOURTH = "perfect_fourth"
    TRITONE = "tritone"
    PERFECT_FIFTH = "perfect_fifth"
    MINOR_SIXTH = "minor_sixth"
    MAJOR_SIXTH = "major_sixth"
    MINOR_SEVENTH = "minor_seventh"
    MAJOR_SEVENTH = "major_seventh"
    OCTAVE = "octave"

@dataclass
class MusicalityMetrics:
    """音乐性指标"""
    melodic_fluency: float           # 旋律流畅度 (0-1)
    harmonic_stability: float       # 和声稳定性 (0-1)
    interval_consonance: float      # 音程协和度 (0-1)
    scale_completeness: float       # 音阶完整性 (0-1)
    modal_character: float          # 调式特征 (0-1)
    expressive_range: float         # 表达范围 (0-1)
    cultural_familiarity: float     # 文化熟悉度 (0-1)
    emotional_depth: float          # 情感深度 (0-1)
    
    @property
    def overall_musicality(self) -> float:
        """整体音乐性评分"""
        weights = {
            'melodic_fluency': 0.2,
            'harmonic_stability': 0.15,
            'interval_consonance': 0.15,
            'scale_completeness': 0.1,
            'modal_character': 0.1,
            'expressive_range': 0.15,
            'cultural_familiarity': 0.1,
            'emotional_depth': 0.05
        }
        
        return sum(getattr(self, attr) * weight for attr, weight in weights.items())

@dataclass
class ContextualAssessment:
    """语境化评估"""
    context: MusicalContext
    suitability_score: float        # 适用性评分 (0-1)
    strengths: List[str]             # 优势特点
    limitations: List[str]           # 局限性
    suggested_applications: List[str] # 建议应用

@dataclass
class MusicalityValidationResult:
    """音乐性验证结果"""
    metrics: MusicalityMetrics
    contextual_assessments: List[ContextualAssessment]
    interval_analysis: Dict[str, float]
    chord_potential: Dict[str, float]
    recommended_usage: List[str]
    cautions: List[str]
    overall_validation: bool
    confidence_level: float

class PetersenMusicalityValidator:
    """Petersen音律音乐性验证器"""
    
    def __init__(self):
        """初始化验证器"""
        # 标准音程比率（以音分为单位）
        self.standard_intervals = {
            MusicalInterval.UNISON: 0,
            MusicalInterval.MINOR_SECOND: 100,
            MusicalInterval.MAJOR_SECOND: 200,
            MusicalInterval.MINOR_THIRD: 300,
            MusicalInterval.MAJOR_THIRD: 400,
            MusicalInterval.PERFECT_FOURTH: 500,
            MusicalInterval.TRITONE: 600,
            MusicalInterval.PERFECT_FIFTH: 700,
            MusicalInterval.MINOR_SIXTH: 800,
            MusicalInterval.MAJOR_SIXTH: 900,
            MusicalInterval.MINOR_SEVENTH: 1000,
            MusicalInterval.MAJOR_SEVENTH: 1100,
            MusicalInterval.OCTAVE: 1200
        }
        
        # 和弦构建模板
        self.chord_templates = {
            'major_triad': [0, 400, 700],      # 大三和弦
            'minor_triad': [0, 300, 700],      # 小三和弦
            'diminished': [0, 300, 600],       # 减三和弦
            'augmented': [0, 400, 800],        # 增三和弦
            'dominant_7th': [0, 400, 700, 1000], # 属七和弦
            'major_7th': [0, 400, 700, 1100],  # 大七和弦
            'minor_7th': [0, 300, 700, 1000]   # 小七和弦
        }
        
        # 调式模板
        self.modal_templates = {
            'ionian': [0, 200, 400, 500, 700, 900, 1100],      # 自然大调
            'dorian': [0, 200, 300, 500, 700, 900, 1000],      # 多利亚调式
            'phrygian': [0, 100, 300, 500, 700, 800, 1000],    # 弗里吉亚调式
            'lydian': [0, 200, 400, 600, 700, 900, 1100],      # 利底亚调式
            'mixolydian': [0, 200, 400, 500, 700, 900, 1000],  # 混合利底亚调式
            'aeolian': [0, 200, 300, 500, 700, 800, 1000],     # 自然小调
            'locrian': [0, 100, 300, 500, 600, 800, 1000],     # 洛克里亚调式
            'pentatonic_major': [0, 200, 400, 700, 900],       # 大调五声音阶
            'pentatonic_minor': [0, 300, 500, 700, 1000]       # 小调五声音阶
        }
    
    def validate_musicality(self, exploration_result: ExplorationResult) -> MusicalityValidationResult:
        """
        验证音律系统的音乐性
        
        Args:
            exploration_result: 探索结果
            
        Returns:
            MusicalityValidationResult: 音乐性验证结果
        """
        if not exploration_result.success or not exploration_result.entries:
            return self._create_failed_validation(exploration_result, "无效的探索结果")
        
        print(f"🎵 验证音律系统音乐性: {exploration_result.parameters.phi_name} × {exploration_result.parameters.delta_theta_name}")
        
        # 计算基础指标
        metrics = self._calculate_musicality_metrics(exploration_result)
        
        # 语境化评估
        contextual_assessments = self._perform_contextual_assessments(exploration_result)
        
        # 音程分析
        interval_analysis = self._analyze_intervals(exploration_result)
        
        # 和弦潜力分析
        chord_potential = self._analyze_chord_potential(exploration_result)
        
        # 生成建议和注意事项
        recommended_usage, cautions = self._generate_usage_recommendations(
            metrics, contextual_assessments, interval_analysis, chord_potential
        )
        
        # 整体验证判断
        overall_validation = metrics.overall_musicality >= 0.6
        confidence_level = self._calculate_confidence_level(metrics, exploration_result)
        
        return MusicalityValidationResult(
            metrics=metrics,
            contextual_assessments=contextual_assessments,
            interval_analysis=interval_analysis,
            chord_potential=chord_potential,
            recommended_usage=recommended_usage,
            cautions=cautions,
            overall_validation=overall_validation,
            confidence_level=confidence_level
        )
    
    def _calculate_musicality_metrics(self, exploration_result: ExplorationResult) -> MusicalityMetrics:
        """计算音乐性指标"""
        entries = exploration_result.entries
        
        # 1. 旋律流畅度：基于相邻音程的平滑度
        melodic_fluency = self._calculate_melodic_fluency(entries)
        
        # 2. 和声稳定性：基于协和音程的比例
        harmonic_stability = self._calculate_harmonic_stability(entries)
        
        # 3. 音程协和度：基于传统音程理论
        interval_consonance = self._calculate_interval_consonance(entries)
        
        # 4. 音阶完整性：覆盖八度的均匀性
        scale_completeness = self._calculate_scale_completeness(entries)
        
        # 5. 调式特征：与已知调式的相似度
        modal_character = self._calculate_modal_character(entries)
        
        # 6. 表达范围：音域和音程多样性
        expressive_range = self._calculate_expressive_range(entries)
        
        # 7. 文化熟悉度：与常见音律的相似度
        cultural_familiarity = self._calculate_cultural_familiarity(entries)
        
        # 8. 情感深度：基于音程情感色彩
        emotional_depth = self._calculate_emotional_depth(entries)
        
        return MusicalityMetrics(
            melodic_fluency=melodic_fluency,
            harmonic_stability=harmonic_stability,
            interval_consonance=interval_consonance,
            scale_completeness=scale_completeness,
            modal_character=modal_character,
            expressive_range=expressive_range,
            cultural_familiarity=cultural_familiarity,
            emotional_depth=emotional_depth
        )
    
    def _calculate_melodic_fluency(self, entries: List) -> float:
        """计算旋律流畅度"""
        if len(entries) < 2:
            return 0.0
        
        # 计算相邻音程
        intervals = []
        for i in range(len(entries) - 1):
            freq_ratio = entries[i+1].freq / entries[i].freq
            cents = 1200 * math.log2(freq_ratio)
            intervals.append(abs(cents))
        
        # 评估音程大小的合理性（避免过大跳跃）
        reasonable_intervals = [interval for interval in intervals if 50 <= interval <= 400]
        fluency_ratio = len(reasonable_intervals) / len(intervals)
        
        # 评估音程变化的平滑性
        if len(intervals) > 2:
            interval_changes = [abs(intervals[i+1] - intervals[i]) for i in range(len(intervals)-1)]
            avg_change = np.mean(interval_changes)
            smoothness = max(0, 1 - avg_change / 200)  # 200音分作为参考
        else:
            smoothness = 1.0
        
        return (fluency_ratio * 0.7 + smoothness * 0.3)
    
    def _calculate_harmonic_stability(self, entries: List) -> float:
        """计算和声稳定性"""
        if len(entries) < 3:
            return 0.0
        
        stable_intervals = 0
        total_combinations = 0
        
        # 检查所有音符组合的协和性
        for i in range(len(entries)):
            for j in range(i+1, len(entries)):
                freq_ratio = entries[j].freq / entries[i].freq
                cents = 1200 * math.log2(freq_ratio) % 1200  # 归约到八度内
                
                # 判断是否为协和音程
                if self._is_consonant_interval(cents):
                    stable_intervals += 1
                total_combinations += 1
        
        return stable_intervals / total_combinations if total_combinations > 0 else 0.0
    
    def _is_consonant_interval(self, cents: float) -> bool:
        """判断音程是否协和"""
        consonant_intervals = [0, 100, 200, 300, 400, 500, 700, 800, 900, 1200]
        tolerance = 50  # 50音分的容差
        
        for consonant in consonant_intervals:
            if abs(cents - consonant) <= tolerance:
                return True
        return False
    
    def _calculate_interval_consonance(self, entries: List) -> float:
        """计算音程协和度"""
        if len(entries) < 2:
            return 0.0
        
        consonance_scores = []
        
        for i in range(len(entries)):
            for j in range(i+1, len(entries)):
                freq_ratio = entries[j].freq / entries[i].freq
                cents = 1200 * math.log2(freq_ratio) % 1200
                
                # 基于简单比率计算协和度
                consonance = self._calculate_ratio_consonance(freq_ratio)
                consonance_scores.append(consonance)
        
        return np.mean(consonance_scores) if consonance_scores else 0.0
    
    def _calculate_ratio_consonance(self, freq_ratio: float) -> float:
        """基于频率比计算协和度"""
        # 寻找最简整数比
        for denom in range(1, 17):  # 检查分母1-16
            for numer in range(1, int(denom * freq_ratio) + 2):
                ratio = numer / denom
                if abs(ratio - freq_ratio) / freq_ratio < 0.01:  # 1%容差
                    # 协和度与复杂度成反比
                    complexity = numer + denom
                    return max(0, 1 - (complexity - 2) / 30)
        
        return 0.1  # 复杂比率的基础协和度
    
    def _calculate_scale_completeness(self, entries: List) -> float:
        """计算音阶完整性"""
        if len(entries) < 5:
            return len(entries) / 7  # 基于七音音阶标准
        
        # 计算音符在八度内的分布
        frequencies = [entry.freq for entry in entries]
        base_freq = min(frequencies)
        
        # 归约到一个八度内
        normalized_cents = []
        for freq in frequencies:
            cents = 1200 * math.log2(freq / base_freq) % 1200
            normalized_cents.append(cents)
        
        normalized_cents.sort()
        
        # 评估分布均匀性
        if len(normalized_cents) > 1:
            gaps = [normalized_cents[i+1] - normalized_cents[i] for i in range(len(normalized_cents)-1)]
            gaps.append(1200 - normalized_cents[-1] + normalized_cents[0])  # 循环回到起点
            
            # 理想情况下音程分布相对均匀
            ideal_gap = 1200 / len(normalized_cents)
            gap_variance = np.var([abs(gap - ideal_gap) for gap in gaps])
            uniformity = max(0, 1 - gap_variance / (ideal_gap * ideal_gap))
        else:
            uniformity = 0.0
        
        # 音符数量得分
        count_score = min(1.0, len(entries) / 12)  # 12音为满分
        
        return (uniformity * 0.7 + count_score * 0.3)
    
    def _calculate_modal_character(self, entries: List) -> float:
        """计算调式特征强度"""
        if len(entries) < 5:
            return 0.0
        
        # 归约到八度内并排序
        base_freq = min(entry.freq for entry in entries)
        cents_values = []
        
        for entry in entries:
            cents = 1200 * math.log2(entry.freq / base_freq) % 1200
            cents_values.append(cents)
        
        cents_values = sorted(set(cents_values))  # 去重并排序
        
        # 与各种调式模板比较
        best_similarity = 0.0
        
        for mode_name, template in self.modal_templates.items():
            similarity = self._calculate_template_similarity(cents_values, template)
            best_similarity = max(best_similarity, similarity)
        
        return best_similarity
    
    def _calculate_template_similarity(self, cents_values: List[float], template: List[int]) -> float:
        """计算与模板的相似度"""
        if not cents_values or not template:
            return 0.0
        
        matches = 0
        tolerance = 50  # 50音分容差
        
        for template_cent in template:
            for actual_cent in cents_values:
                if abs(actual_cent - template_cent) <= tolerance:
                    matches += 1
                    break
        
        # 考虑覆盖度和精确度
        coverage = matches / len(template)
        precision = matches / len(cents_values) if cents_values else 0
        
        return (coverage * 0.6 + precision * 0.4)
    
    def _calculate_expressive_range(self, entries: List) -> float:
        """计算表达范围"""
        if len(entries) < 3:
            return 0.0
        
        frequencies = [entry.freq for entry in entries]
        
        # 音域范围
        freq_range = max(frequencies) / min(frequencies)
        range_score = min(1.0, math.log2(freq_range) / 3)  # 3个八度为满分
        
        # 音程多样性
        intervals = set()
        for i in range(len(entries)):
            for j in range(i+1, len(entries)):
                freq_ratio = entries[j].freq / entries[i].freq
                cents = round(1200 * math.log2(freq_ratio) % 1200, 0)
                intervals.add(cents)
        
        diversity_score = min(1.0, len(intervals) / 12)  # 12种不同音程为满分
        
        return (range_score * 0.5 + diversity_score * 0.5)
    
    def _calculate_cultural_familiarity(self, entries: List) -> float:
        """计算文化熟悉度"""
        if len(entries) < 5:
            return 0.0
        
        # 与西方传统音律的相似度
        western_similarity = self._calculate_western_similarity(entries)
        
        # 与世界音乐传统的相似度
        world_similarity = self._calculate_world_music_similarity(entries)
        
        return max(western_similarity, world_similarity)
    
    def _calculate_western_similarity(self, entries: List) -> float:
        """计算与西方音乐传统的相似度"""
        # 简化实现：检查是否包含主要协和音程
        base_freq = min(entry.freq for entry in entries)
        
        major_intervals = [200, 400, 500, 700, 900]  # 大二度、大三度、纯四度、纯五度、大六度
        found_intervals = 0
        
        for entry in entries:
            cents = 1200 * math.log2(entry.freq / base_freq) % 1200
            for major_interval in major_intervals:
                if abs(cents - major_interval) <= 50:
                    found_intervals += 1
                    break
        
        return found_intervals / len(major_intervals)
    
    def _calculate_world_music_similarity(self, entries: List) -> float:
        """计算与世界音乐传统的相似度"""
        # 简化实现：检查五声音阶特征
        pentatonic_score = self._calculate_template_similarity(
            [1200 * math.log2(entry.freq / min(e.freq for e in entries)) % 1200 for entry in entries],
            self.modal_templates['pentatonic_major']
        )
        
        return pentatonic_score
    
    def _calculate_emotional_depth(self, entries: List) -> float:
        """计算情感深度"""
        if len(entries) < 3:
            return 0.0
        
        # 基于音程的情感色彩评估
        emotional_intervals = {
            # 音程（音分）: 情感强度
            100: 0.9,   # 小二度：紧张
            300: 0.7,   # 小三度：忧郁
            400: 0.8,   # 大三度：明亮
            600: 0.9,   # 三全音：不稳定
            700: 0.6,   # 纯五度：稳定
            900: 0.7,   # 大六度：开阔
            1000: 0.8   # 小七度：悬置
        }
        
        total_emotion = 0.0
        count = 0
        
        for i in range(len(entries)):
            for j in range(i+1, len(entries)):
                freq_ratio = entries[j].freq / entries[i].freq
                cents = round(1200 * math.log2(freq_ratio) % 1200, -1)  # 舍入到10音分
                
                if cents in emotional_intervals:
                    total_emotion += emotional_intervals[cents]
                    count += 1
        
        return total_emotion / count if count > 0 else 0.5
    
    def _perform_contextual_assessments(self, exploration_result: ExplorationResult) -> List[ContextualAssessment]:
        """执行语境化评估"""
        assessments = []
        
        for context in MusicalContext:
            assessment = self._assess_context(exploration_result, context)
            assessments.append(assessment)
        
        return assessments
    
    def _assess_context(self, exploration_result: ExplorationResult, context: MusicalContext) -> ContextualAssessment:
        """评估特定音乐语境的适用性"""
        entries = exploration_result.entries
        
        if context == MusicalContext.MELODIC:
            return self._assess_melodic_context(entries)
        elif context == MusicalContext.HARMONIC:
            return self._assess_harmonic_context(entries)
        elif context == MusicalContext.MODAL:
            return self._assess_modal_context(entries)
        elif context == MusicalContext.PENTATONIC:
            return self._assess_pentatonic_context(entries)
        else:
            # 其他语境的简化评估
            return ContextualAssessment(
                context=context,
                suitability_score=0.5,
                strengths=["需要进一步分析"],
                limitations=["评估功能待完善"],
                suggested_applications=["实验性应用"]
            )
    
    def _assess_melodic_context(self, entries: List) -> ContextualAssessment:
        """评估旋律语境适用性"""
        melodic_fluency = self._calculate_melodic_fluency(entries)
        
        strengths = []
        limitations = []
        applications = []
        
        if melodic_fluency >= 0.7:
            strengths.append("旋律线条流畅自然")
            applications.append("独奏乐器演奏")
        elif melodic_fluency >= 0.5:
            strengths.append("旋律具有一定连贯性")
            applications.append("现代音乐创作")
        else:
            limitations.append("旋律跳跃较大")
            applications.append("实验性音响设计")
        
        return ContextualAssessment(
            context=MusicalContext.MELODIC,
            suitability_score=melodic_fluency,
            strengths=strengths,
            limitations=limitations,
            suggested_applications=applications
        )
    
    def _assess_harmonic_context(self, entries: List) -> ContextualAssessment:
        """评估和声语境适用性"""
        harmonic_stability = self._calculate_harmonic_stability(entries)
        
        strengths = []
        limitations = []
        applications = []
        
        if harmonic_stability >= 0.6:
            strengths.append("和声稳定性良好")
            applications.append("和声编配")
        else:
            limitations.append("和声较为不稳定")
            applications.append("音响纹理设计")
        
        return ContextualAssessment(
            context=MusicalContext.HARMONIC,
            suitability_score=harmonic_stability,
            strengths=strengths,
            limitations=limitations,
            suggested_applications=applications
        )
    
    def _assess_modal_context(self, entries: List) -> ContextualAssessment:
        """评估调式语境适用性"""
        modal_character = self._calculate_modal_character(entries)
        
        strengths = []
        limitations = []
        applications = []
        
        if modal_character >= 0.6:
            strengths.append("具有明确的调式特征")
            applications.append("传统风格音乐")
        else:
            strengths.append("独特的音响色彩")
            applications.append("现代实验音乐")
        
        return ContextualAssessment(
            context=MusicalContext.MODAL,
            suitability_score=modal_character,
            strengths=strengths,
            limitations=limitations,
            suggested_applications=applications
        )
    
    def _assess_pentatonic_context(self, entries: List) -> ContextualAssessment:
        """评估五声音阶语境适用性"""
        pentatonic_similarity = self._calculate_template_similarity(
            [1200 * math.log2(entry.freq / min(e.freq for e in entries)) % 1200 for entry in entries],
            self.modal_templates['pentatonic_major']
        )
        
        strengths = []
        limitations = []
        applications = []
        
        if pentatonic_similarity >= 0.6:
            strengths.append("具有五声音阶特征")
            applications.append("世界音乐融合")
        else:
            limitations.append("与五声传统距离较远")
            applications.append("西方现代音乐")
        
        return ContextualAssessment(
            context=MusicalContext.PENTATONIC,
            suitability_score=pentatonic_similarity,
            strengths=strengths,
            limitations=limitations,
            suggested_applications=applications
        )
    
    def _analyze_intervals(self, exploration_result: ExplorationResult) -> Dict[str, float]:
        """分析音程特性"""
        entries = exploration_result.entries
        interval_stats = {}
        
        if len(entries) < 2:
            return interval_stats
        
        # 统计各类音程
        for interval_type, target_cents in self.standard_intervals.items():
            count = 0
            total_pairs = 0
            
            for i in range(len(entries)):
                for j in range(i+1, len(entries)):
                    freq_ratio = entries[j].freq / entries[i].freq
                    cents = 1200 * math.log2(freq_ratio) % 1200
                    total_pairs += 1
                    
                    if abs(cents - target_cents) <= 50:  # 50音分容差
                        count += 1
            
            interval_stats[interval_type.value] = count / total_pairs if total_pairs > 0 else 0.0
        
        return interval_stats
    
    def _analyze_chord_potential(self, exploration_result: ExplorationResult) -> Dict[str, float]:
        """分析和弦构建潜力"""
        entries = exploration_result.entries
        chord_potential = {}
        
        if len(entries) < 3:
            return chord_potential
        
        # 分析各类和弦的构建可能性
        for chord_type, template in self.chord_templates.items():
            best_match = 0.0
            
            # 尝试以每个音符为根音构建和弦
            for root_entry in entries:
                match_score = self._calculate_chord_match(root_entry, entries, template)
                best_match = max(best_match, match_score)
            
            chord_potential[chord_type] = best_match
        
        return chord_potential
    
    def _calculate_chord_match(self, root_entry, all_entries: List, template: List[int]) -> float:
        """计算和弦匹配度"""
        matched_notes = 0
        
        for target_cents in template:
            target_freq = root_entry.freq * (2 ** (target_cents / 1200))
            
            # 寻找最接近的音符
            best_match = float('inf')
            for entry in all_entries:
                freq_diff = abs(entry.freq - target_freq) / target_freq
                if freq_diff < best_match:
                    best_match = freq_diff
            
            # 如果差异在5%以内，认为匹配
            if best_match <= 0.05:
                matched_notes += 1
        
        return matched_notes / len(template)
    
    def _generate_usage_recommendations(self, metrics: MusicalityMetrics,
                                      contextual_assessments: List[ContextualAssessment],
                                      interval_analysis: Dict[str, float],
                                      chord_potential: Dict[str, float]) -> Tuple[List[str], List[str]]:
        """生成使用建议和注意事项"""
        recommendations = []
        cautions = []
        
        # 基于整体音乐性评分的建议
        if metrics.overall_musicality >= 0.8:
            recommendations.append("该音律系统具有优秀的音乐表现力，适合专业音乐创作")
        elif metrics.overall_musicality >= 0.6:
            recommendations.append("该音律系统具有良好的音乐性，适合实验性音乐探索")
        else:
            recommendations.append("该音律系统适合作为音响设计和声音艺术的材料")
            cautions.append("音乐性评分较低，在传统音乐应用中需要谨慎")
        
        # 基于特定指标的建议
        if metrics.melodic_fluency >= 0.7:
            recommendations.append("旋律表现力强，适合独奏乐器和声乐创作")
        elif metrics.melodic_fluency < 0.4:
            cautions.append("旋律连贯性不足，建议专注于和声或纹理应用")
        
        if metrics.harmonic_stability >= 0.6:
            recommendations.append("和声稳定性好，可用于和弦进行和复调音乐")
        else:
            cautions.append("和声较为不稳定，在传统和声应用中需要特殊处理")
        
        # 基于语境评估的建议
        for assessment in contextual_assessments:
            if assessment.suitability_score >= 0.7:
                recommendations.extend(assessment.suggested_applications)
        
        # 基于和弦潜力的建议
        strong_chords = [chord for chord, score in chord_potential.items() if score >= 0.7]
        if strong_chords:
            recommendations.append(f"和弦构建能力强，特别适合：{', '.join(strong_chords)}")
        elif not any(score >= 0.5 for score in chord_potential.values()):
            cautions.append("和弦构建能力有限，更适合单音线条或音响纹理")
        
        return recommendations, cautions
    
    def _calculate_confidence_level(self, metrics: MusicalityMetrics, 
                                  exploration_result: ExplorationResult) -> float:
        """计算评估置信度"""
        # 基于音符数量和分布的置信度
        entry_count = len(exploration_result.entries)
        count_confidence = min(1.0, entry_count / 12)  # 12音符以上置信度较高
        
        # 基于指标一致性的置信度
        metric_values = [
            metrics.melodic_fluency,
            metrics.harmonic_stability,
            metrics.interval_consonance,
            metrics.scale_completeness
        ]
        consistency = 1.0 - np.std(metric_values)  # 标准差越小，一致性越高
        
        return (count_confidence * 0.6 + consistency * 0.4)
    
    def _create_failed_validation(self, exploration_result: ExplorationResult, 
                                reason: str) -> MusicalityValidationResult:
        """创建失败的验证结果"""
        return MusicalityValidationResult(
            metrics=MusicalityMetrics(0, 0, 0, 0, 0, 0, 0, 0),
            contextual_assessments=[],
            interval_analysis={},
            chord_potential={},
            recommended_usage=[],
            cautions=[f"验证失败: {reason}"],
            overall_validation=False,
            confidence_level=0.0
        )

def format_musicality_validation(result: MusicalityValidationResult) -> str:
    """格式化音乐性验证结果"""
    output = []
    
    output.append("🎵 === 音乐性验证结果 ===")
    output.append(f"📊 整体音乐性: {result.metrics.overall_musicality:.1%}")
    output.append(f"🎯 验证通过: {'是' if result.overall_validation else '否'}")
    output.append(f"📈 置信度: {result.confidence_level:.1%}")
    
    output.append("\n📋 详细指标:")
    output.append(f"   🎼 旋律流畅度: {result.metrics.melodic_fluency:.1%}")
    output.append(f"   🎵 和声稳定性: {result.metrics.harmonic_stability:.1%}")
    output.append(f"   🎶 音程协和度: {result.metrics.interval_consonance:.1%}")
    output.append(f"   📈 音阶完整性: {result.metrics.scale_completeness:.1%}")
    output.append(f"   🎭 调式特征: {result.metrics.modal_character:.1%}")
    output.append(f"   🌈 表达范围: {result.metrics.expressive_range:.1%}")
    
    if result.recommended_usage:
        output.append("\n💡 使用建议:")
        for recommendation in result.recommended_usage:
            output.append(f"   • {recommendation}")
    
    if result.cautions:
        output.append("\n⚠️ 注意事项:")
        for caution in result.cautions:
            output.append(f"   • {caution}")
    
    return "\n".join(output)