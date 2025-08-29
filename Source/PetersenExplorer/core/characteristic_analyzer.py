"""
Petersen音律特性分析器
负责深度分析每个音律系统的特性，包括音程质量、和声潜力、音乐表达能力等
"""
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math
import sys
from pathlib import Path

# 添加父级路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from PetersenScale_Phi import PetersenScale_Phi

class IntervalQuality(Enum):
    """音程质量分类"""
    UNISON = "unison"              # 同度类
    MICROTONE = "microtone"        # 微分音
    SEMITONE = "semitone"          # 半音类  
    TONE = "tone"                  # 全音类
    MINOR_THIRD = "minor_third"    # 小三度类
    MAJOR_THIRD = "major_third"    # 大三度类
    FOURTH = "fourth"              # 四度类
    TRITONE = "tritone"            # 三全音类
    FIFTH = "fifth"                # 五度类
    MINOR_SIXTH = "minor_sixth"    # 小六度类
    MAJOR_SIXTH = "major_sixth"    # 大六度类
    MINOR_SEVENTH = "minor_seventh" # 小七度类
    MAJOR_SEVENTH = "major_seventh" # 大七度类
    OCTAVE = "octave"              # 八度类
    LARGE_INTERVAL = "large"       # 大音程

@dataclass
class IntervalAnalysis:
    """音程分析结果"""
    cents: float
    ratio: float
    quality: IntervalQuality
    consonance_score: float        # 协和度评分 (0-1)
    naturalness_score: float       # 自然度评分 (0-1)
    traditional_similarity: float  # 与传统音程的相似度 (0-1)

@dataclass
class HarmonicPotential:
    """和声潜力分析"""
    chord_building_score: float       # 和弦构建能力 (0-1)
    voice_leading_score: float        # 声部进行流畅度 (0-1)
    consonant_interval_ratio: float   # 协和音程比例
    dissonant_interval_ratio: float   # 不协和音程比例
    harmonic_complexity: float        # 和声复杂度
    recommended_chord_sizes: List[int] # 推荐和弦大小

@dataclass
class MelodicCharacteristics:
    """旋律特性分析"""
    step_motion_ratio: float          # 级进运动比例
    leap_motion_ratio: float          # 跳进运动比例
    melodic_flow_score: float         # 旋律流畅度 (0-1)
    expressive_range_score: float     # 表达力范围 (0-1)
    singability_score: float          # 可唱性 (0-1)
    recommended_tempo_range: Tuple[int, int] # 推荐速度范围(BPM)

@dataclass
class ScaleCharacteristics:
    """音阶综合特性"""
    # 基础信息
    entry_count: int
    frequency_range: Tuple[float, float]
    frequency_density: float
    
    # 音程分析
    interval_analyses: List[IntervalAnalysis]
    interval_variety_score: float
    
    # 音乐潜力
    harmonic_potential: HarmonicPotential
    melodic_characteristics: MelodicCharacteristics
    
    # 风格特征
    traditional_compatibility: float   # 传统兼容性 (0-1)
    experimental_potential: float      # 实验潜力 (0-1)
    world_music_affinity: float        # 世界音乐亲和性 (0-1)
    therapeutic_potential: float       # 治疗潜力 (0-1)
    
    # 综合评分
    overall_musicality: float          # 整体音乐性 (0-1)
    innovation_score: float            # 创新性评分 (0-1)
    practical_viability: float         # 实用可行性 (0-1)

class CharacteristicAnalyzer:
    """特性分析器"""
    
    def __init__(self):
        # 传统音程参考值（音分）
        self.traditional_intervals = {
            0: "unison",
            100: "semitone", 
            200: "tone",
            300: "minor_third",
            400: "major_third", 
            500: "fourth",
            600: "tritone",
            700: "fifth",
            800: "minor_sixth",
            900: "major_sixth",
            1000: "minor_seventh",
            1100: "major_seventh",
            1200: "octave"
        }
        
        # 协和度权重表
        self.consonance_weights = {
            IntervalQuality.UNISON: 1.0,
            IntervalQuality.OCTAVE: 1.0,
            IntervalQuality.FIFTH: 0.9,
            IntervalQuality.FOURTH: 0.8,
            IntervalQuality.MAJOR_THIRD: 0.7,
            IntervalQuality.MINOR_THIRD: 0.7,
            IntervalQuality.MAJOR_SIXTH: 0.6,
            IntervalQuality.MINOR_SIXTH: 0.6,
            IntervalQuality.TONE: 0.4,
            IntervalQuality.MINOR_SEVENTH: 0.3,
            IntervalQuality.MAJOR_SEVENTH: 0.2,
            IntervalQuality.TRITONE: 0.1,
            IntervalQuality.MICROTONE: 0.3,
            IntervalQuality.SEMITONE: 0.5,
            IntervalQuality.LARGE_INTERVAL: 0.2
        }
    
    def analyze_scale_characteristics(self, 
                                    scale: PetersenScale_Phi, 
                                    entries: List) -> ScaleCharacteristics:
        """
        分析音阶的完整特性
        
        Args:
            scale: 音阶对象
            entries: 音阶条目列表
            
        Returns:
            ScaleCharacteristics: 完整特性分析
        """
        if not entries:
            return self._create_empty_characteristics()
        
        # 基础信息
        frequencies = [entry.freq for entry in entries]
        intervals = scale.analyze_intervals()
        
        # 音程分析
        interval_analyses = self._analyze_intervals(intervals)
        interval_variety_score = self._calculate_interval_variety(interval_analyses)
        
        # 和声潜力分析
        harmonic_potential = self._analyze_harmonic_potential(interval_analyses, entries)
        
        # 旋律特性分析
        melodic_characteristics = self._analyze_melodic_characteristics(interval_analyses)
        
        # 风格特征分析
        style_scores = self._analyze_style_characteristics(interval_analyses, entries)
        
        # 综合评分
        overall_scores = self._calculate_overall_scores(
            interval_analyses, harmonic_potential, melodic_characteristics, style_scores
        )
        
        return ScaleCharacteristics(
            # 基础信息
            entry_count=len(entries),
            frequency_range=(min(frequencies), max(frequencies)),
            frequency_density=len(entries) / (max(frequencies) - min(frequencies)) * 100,
            
            # 音程分析
            interval_analyses=interval_analyses,
            interval_variety_score=interval_variety_score,
            
            # 音乐潜力
            harmonic_potential=harmonic_potential,
            melodic_characteristics=melodic_characteristics,
            
            # 风格特征
            traditional_compatibility=style_scores['traditional_compatibility'],
            experimental_potential=style_scores['experimental_potential'],
            world_music_affinity=style_scores['world_music_affinity'],
            therapeutic_potential=style_scores['therapeutic_potential'],
            
            # 综合评分
            overall_musicality=overall_scores['overall_musicality'],
            innovation_score=overall_scores['innovation_score'],
            practical_viability=overall_scores['practical_viability']
        )
    
    def _analyze_intervals(self, intervals: List[Dict]) -> List[IntervalAnalysis]:
        """分析音程列表"""
        analyses = []
        
        for interval in intervals:
            cents = interval['cents']
            ratio = interval['ratio']
            
            # 判断音程质量
            quality = self._classify_interval_quality(cents)
            
            # 计算协和度
            consonance_score = self._calculate_consonance_score(quality, cents)
            
            # 计算自然度
            naturalness_score = self._calculate_naturalness_score(cents)
            
            # 计算与传统音程的相似度
            traditional_similarity = self._calculate_traditional_similarity(cents)
            
            analyses.append(IntervalAnalysis(
                cents=cents,
                ratio=ratio,
                quality=quality,
                consonance_score=consonance_score,
                naturalness_score=naturalness_score,
                traditional_similarity=traditional_similarity
            ))
        
        return analyses
    
    def _classify_interval_quality(self, cents: float) -> IntervalQuality:
        """根据音分值分类音程质量"""
        if cents < 25:
            return IntervalQuality.UNISON
        elif cents < 75:
            return IntervalQuality.MICROTONE
        elif cents < 150:
            return IntervalQuality.SEMITONE
        elif cents < 250:
            return IntervalQuality.TONE
        elif cents < 350:
            return IntervalQuality.MINOR_THIRD
        elif cents < 450:
            return IntervalQuality.MAJOR_THIRD
        elif cents < 550:
            return IntervalQuality.FOURTH
        elif cents < 650:
            return IntervalQuality.TRITONE
        elif cents < 750:
            return IntervalQuality.FIFTH
        elif cents < 850:
            return IntervalQuality.MINOR_SIXTH
        elif cents < 950:
            return IntervalQuality.MAJOR_SIXTH
        elif cents < 1050:
            return IntervalQuality.MINOR_SEVENTH
        elif cents < 1150:
            return IntervalQuality.MAJOR_SEVENTH
        elif cents < 1250:
            return IntervalQuality.OCTAVE
        else:
            return IntervalQuality.LARGE_INTERVAL
    
    def _calculate_consonance_score(self, quality: IntervalQuality, cents: float) -> float:
        """计算协和度评分"""
        base_score = self.consonance_weights.get(quality, 0.1)
        
        # 对传统音程附近的音程给予奖励
        traditional_bonus = 0
        for traditional_cents in self.traditional_intervals.keys():
            distance = abs(cents - traditional_cents)
            if distance < 25:  # 25音分内
                traditional_bonus = (25 - distance) / 25 * 0.2
                break
        
        return min(1.0, base_score + traditional_bonus)
    
    def _calculate_naturalness_score(self, cents: float) -> float:
        """计算自然度评分（基于心理声学）"""
        # 自然音程范围（基于泛音列和常见音程）
        natural_ranges = [
            (0, 25, 1.0),      # 同度
            (95, 105, 0.8),    # 半音
            (195, 205, 0.9),   # 全音
            (295, 305, 0.8),   # 小三度
            (385, 415, 0.9),   # 大三度
            (495, 505, 0.95),  # 完全四度
            (695, 705, 1.0),   # 完全五度
            (795, 805, 0.7),   # 小六度
            (895, 905, 0.8),   # 大六度
            (1195, 1205, 1.0), # 八度
        ]
        
        for low, high, score in natural_ranges:
            if low <= cents <= high:
                return score
        
        # 计算到最近自然音程的距离
        min_distance = float('inf')
        for low, high, _ in natural_ranges:
            center = (low + high) / 2
            distance = abs(cents - center)
            min_distance = min(min_distance, distance)
        
        # 距离越远，自然度越低
        return max(0.0, 1.0 - min_distance / 100.0)
    
    def _calculate_traditional_similarity(self, cents: float) -> float:
        """计算与传统音程的相似度"""
        min_distance = float('inf')
        
        for traditional_cents in self.traditional_intervals.keys():
            distance = abs(cents - traditional_cents)
            min_distance = min(min_distance, distance)
        
        # 转换为相似度（距离越小相似度越高）
        return max(0.0, 1.0 - min_distance / 100.0)
    
    def _create_empty_characteristics(self) -> ScaleCharacteristics:
        """创建空的特性对象"""
        return ScaleCharacteristics(
            entry_count=0,
            frequency_range=(0, 0),
            frequency_density=0,
            interval_analyses=[],
            interval_variety_score=0,
            harmonic_potential=HarmonicPotential(0, 0, 0, 0, 0, []),
            melodic_characteristics=MelodicCharacteristics(0, 0, 0, 0, 0, (60, 120)),
            traditional_compatibility=0,
            experimental_potential=0,
            world_music_affinity=0,
            therapeutic_potential=0,
            overall_musicality=0,
            innovation_score=0,
            practical_viability=0
        )
    
    def _calculate_interval_variety(self, interval_analyses: List[IntervalAnalysis]) -> float:
        """计算音程多样性评分"""
        if not interval_analyses:
            return 0.0
        
        # 统计不同质量的音程
        quality_counts = {}
        for analysis in interval_analyses:
            quality = analysis.quality
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        # 多样性 = 不同类型数 / 总可能类型数
        variety_ratio = len(quality_counts) / len(IntervalQuality)
        
        # 考虑分布均匀性（香农熵）
        total = len(interval_analyses)
        entropy = 0
        for count in quality_counts.values():
            prob = count / total
            entropy -= prob * math.log2(prob)
        
        max_entropy = math.log2(len(quality_counts))
        entropy_ratio = entropy / max_entropy if max_entropy > 0 else 0
        
        return (variety_ratio + entropy_ratio) / 2
    
    def _analyze_harmonic_potential(self, interval_analyses: List[IntervalAnalysis], entries: List) -> HarmonicPotential:
        """分析和声潜力"""
        if not interval_analyses:
            return HarmonicPotential(0, 0, 0, 1, 0, [])
        
        # 计算协和音程比例
        consonant_count = sum(1 for a in interval_analyses if a.consonance_score >= 0.7)
        consonant_ratio = consonant_count / len(interval_analyses)
        dissonant_ratio = 1.0 - consonant_ratio
        
        # 和弦构建能力评分
        chord_building_score = min(1.0, consonant_ratio * 1.5)
        
        # 声部进行评分（基于音程平滑度）
        voice_leading_score = self._calculate_melodic_fluency(entries)
        
        # 和声复杂度
        complexity = len(set(round(a.cents, 0) for a in interval_analyses)) / len(interval_analyses)
        
        # 推荐和弦大小
        if consonant_ratio >= 0.8:
            recommended_sizes = [3, 4, 5]
        elif consonant_ratio >= 0.6:
            recommended_sizes = [3, 4]
        else:
            recommended_sizes = [3]
        
        return HarmonicPotential(
            chord_building_score=chord_building_score,
            voice_leading_score=voice_leading_score,
            consonant_interval_ratio=consonant_ratio,
            dissonant_interval_ratio=dissonant_ratio,
            harmonic_complexity=complexity,
            recommended_chord_sizes=recommended_sizes
        )

def _analyze_melodic_characteristics(self, interval_analyses: List[IntervalAnalysis]) -> MelodicCharacteristics:
    """分析旋律特性"""
    if not interval_analyses:
        return MelodicCharacteristics(0, 0, 0, 0, 0, (60, 120))
    
    # 统计级进和跳进
    step_motion = sum(1 for a in interval_analyses if a.cents <= 200)
    leap_motion = len(interval_analyses) - step_motion
    
    step_ratio = step_motion / len(interval_analyses)
    leap_ratio = leap_motion / len(interval_analyses)
    
    # 旋律流畅度
    flow_score = self._calculate_melodic_fluency_from_analyses(interval_analyses)
    
    # 表达范围
    cents_range = max(a.cents for a in interval_analyses) - min(a.cents for a in interval_analyses)
    range_score = min(1.0, cents_range / 1200.0)
    
    # 可唱性（基于音程大小和流畅度）
    singability_score = step_ratio * 0.6 + flow_score * 0.4
    
    # 推荐速度
    if flow_score >= 0.8:
        tempo_range = (80, 140)
    elif flow_score >= 0.6:
        tempo_range = (60, 120)
    else:
        tempo_range = (40, 100)
    
    return MelodicCharacteristics(
        step_motion_ratio=step_ratio,
        leap_motion_ratio=leap_ratio,
        melodic_flow_score=flow_score,
        expressive_range_score=range_score,
        singability_score=singability_score,
        recommended_tempo_range=tempo_range
    )

def _calculate_melodic_fluency_from_analyses(self, interval_analyses: List[IntervalAnalysis]) -> float:
    """从音程分析计算旋律流畅度"""
    if not interval_analyses:
        return 0.0
    
    # 基于自然度和协和度的平均值
    naturalness_avg = sum(a.naturalness_score for a in interval_analyses) / len(interval_analyses)
    consonance_avg = sum(a.consonance_score for a in interval_analyses) / len(interval_analyses)
    
    return (naturalness_avg * 0.6 + consonance_avg * 0.4)

def _analyze_style_characteristics(self, interval_analyses: List[IntervalAnalysis], entries: List) -> Dict[str, float]:
    """分析风格特征"""
    traditional_score = sum(a.traditional_similarity for a in interval_analyses) / len(interval_analyses) if interval_analyses else 0
    
    # 实验潜力基于独特性
    unique_intervals = len(set(round(a.cents, 0) for a in interval_analyses))
    experimental_score = min(1.0, unique_intervals / 12.0)
    
    # 世界音乐亲和性（简化评估）
    world_music_score = 0.5  # 默认中等
    
    # 治疗潜力基于协和度
    therapeutic_score = sum(a.consonance_score for a in interval_analyses) / len(interval_analyses) if interval_analyses else 0
    
    return {
        'traditional_compatibility': traditional_score,
        'experimental_potential': experimental_score,
        'world_music_affinity': world_music_score,
        'therapeutic_potential': therapeutic_score
    }

def _calculate_overall_scores(self, interval_analyses, harmonic_potential, melodic_characteristics, style_scores) -> Dict[str, float]:
    """计算综合评分"""
    # 整体音乐性
    musicality = (
        harmonic_potential.chord_building_score * 0.3 +
        melodic_characteristics.melodic_flow_score * 0.3 +
        style_scores['traditional_compatibility'] * 0.2 +
        harmonic_potential.consonant_interval_ratio * 0.2
    )
    
    # 创新性评分
    innovation = style_scores['experimental_potential']
    
    # 实用可行性
    viability = (
        style_scores['traditional_compatibility'] * 0.4 +
        harmonic_potential.chord_building_score * 0.3 +
        melodic_characteristics.singability_score * 0.3
    )
    
    return {
        'overall_musicality': musicality,
        'innovation_score': innovation,
        'practical_viability': viability
    }