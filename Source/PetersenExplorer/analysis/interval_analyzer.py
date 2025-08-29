"""
音程分析器
分析Petersen音律系统的音程特性和关系
"""
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math
import statistics
from collections import defaultdict

@dataclass
class IntervalInfo:
    """音程信息"""
    name: str
    cents: float
    frequency_ratio: float
    just_intonation_ratio: Optional[Tuple[int, int]] = None
    deviation_from_just: Optional[float] = None
    category: str = "unknown"  # consonant, dissonant, neutral

@dataclass
class IntervalAnalysis:
    """音程分析结果"""
    intervals: List[IntervalInfo]
    interval_distribution: Dict[str, int]
    consonance_profile: Dict[str, float]
    micro_intervals_count: int
    large_intervals_count: int
    unique_intervals_count: int
    interval_complexity_score: float
    harmonic_potential_score: float
    melodic_potential_score: float

class IntervalCategory(Enum):
    """音程类别"""
    UNISON = "unison"
    MICROTONE = "microtone"
    SEMITONE = "semitone"
    TONE = "tone"
    MINOR_THIRD = "minor_third"
    MAJOR_THIRD = "major_third"
    FOURTH = "fourth"
    TRITONE = "tritone"
    FIFTH = "fifth"
    MINOR_SIXTH = "minor_sixth"
    MAJOR_SIXTH = "major_sixth"
    MINOR_SEVENTH = "minor_seventh"
    MAJOR_SEVENTH = "major_seventh"
    OCTAVE = "octave"
    LARGE = "large"

class IntervalAnalyzer:
    """音程分析器"""
    
    def __init__(self):
        """初始化音程分析器"""
        # 纯律音程参考表（音分）
        self.just_intervals = {
            "unison": (0, (1, 1)),
            "minor_second": (111.73, (16, 15)),
            "major_second": (203.91, (9, 8)),
            "minor_third": (315.64, (6, 5)),
            "major_third": (386.31, (5, 4)),
            "fourth": (498.04, (4, 3)),
            "tritone": (590.22, (7, 5)),
            "fifth": (701.96, (3, 2)),
            "minor_sixth": (813.69, (8, 5)),
            "major_sixth": (884.36, (5, 3)),
            "minor_seventh": (996.09, (16, 9)),
            "major_seventh": (1088.27, (15, 8)),
            "octave": (1200.0, (2, 1))
        }
        
        # 十二平均律音程参考表
        self.equal_temp_intervals = {
            "unison": 0,
            "minor_second": 100,
            "major_second": 200,
            "minor_third": 300,
            "major_third": 400,
            "fourth": 500,
            "tritone": 600,
            "fifth": 700,
            "minor_sixth": 800,
            "major_sixth": 900,
            "minor_seventh": 1000,
            "major_seventh": 1100,
            "octave": 1200
        }
        
        # 协和性权重
        self.consonance_weights = {
            "unison": 1.0,
            "octave": 1.0,
            "fifth": 0.9,
            "fourth": 0.8,
            "major_third": 0.7,
            "minor_third": 0.7,
            "major_sixth": 0.6,
            "minor_sixth": 0.6,
            "major_second": 0.4,
            "minor_second": 0.3,
            "major_seventh": 0.2,
            "minor_seventh": 0.2,
            "tritone": 0.1
        }
    
    def analyze_intervals(self, entries: List) -> IntervalAnalysis:
        """
        分析音程结构
        
        Args:
            entries: 音律条目列表
            
        Returns:
            IntervalAnalysis: 音程分析结果
        """
        if len(entries) < 2:
            return IntervalAnalysis(
                intervals=[],
                interval_distribution={},
                consonance_profile={},
                micro_intervals_count=0,
                large_intervals_count=0,
                unique_intervals_count=0,
                interval_complexity_score=0.0,
                harmonic_potential_score=0.0,
                melodic_potential_score=0.0
            )
        
        # 计算所有相邻音程
        intervals = []
        frequencies = [entry.freq for entry in entries]
        
        for i in range(len(frequencies) - 1):
            freq1, freq2 = frequencies[i], frequencies[i + 1]
            cents = self._freq_to_cents(freq2 / freq1)
            ratio = freq2 / freq1
            
            interval_info = self._analyze_single_interval(cents, ratio)
            intervals.append(interval_info)
        
        # 分析音程分布
        interval_distribution = self._calculate_interval_distribution(intervals)
        
        # 计算协和性轮廓
        consonance_profile = self._calculate_consonance_profile(intervals)
        
        # 统计特殊音程
        micro_intervals_count = len([i for i in intervals if i.cents < 100 and i.cents > 10])
        large_intervals_count = len([i for i in intervals if i.cents > 600])
        unique_intervals_count = len(set(round(i.cents, 1) for i in intervals))
        
        # 计算复杂度评分
        interval_complexity_score = self._calculate_complexity_score(intervals)
        
        # 计算和声潜力
        harmonic_potential_score = self._calculate_harmonic_potential(intervals)
        
        # 计算旋律潜力
        melodic_potential_score = self._calculate_melodic_potential(intervals)
        
        return IntervalAnalysis(
            intervals=intervals,
            interval_distribution=interval_distribution,
            consonance_profile=consonance_profile,
            micro_intervals_count=micro_intervals_count,
            large_intervals_count=large_intervals_count,
            unique_intervals_count=unique_intervals_count,
            interval_complexity_score=interval_complexity_score,
            harmonic_potential_score=harmonic_potential_score,
            melodic_potential_score=melodic_potential_score
        )
    
    def _analyze_single_interval(self, cents: float, ratio: float) -> IntervalInfo:
        """分析单个音程"""
        # 确定音程名称和类别
        name, category = self._classify_interval(cents)
        
        # 查找最接近的纯律音程
        just_ratio, deviation = self._find_closest_just_interval(cents)
        
        return IntervalInfo(
            name=name,
            cents=cents,
            frequency_ratio=ratio,
            just_intonation_ratio=just_ratio,
            deviation_from_just=deviation,
            category=category
        )
    
    def _classify_interval(self, cents: float) -> Tuple[str, str]:
        """分类音程"""
        # 将音程规范化到一个八度内
        normalized_cents = cents % 1200
        
        # 分类逻辑
        if normalized_cents < 25:
            return "unison", "consonant"
        elif normalized_cents < 75:
            return "quarter_tone", "microtone"
        elif normalized_cents < 125:
            return "minor_second", "dissonant"
        elif normalized_cents < 175:
            return "neutral_second", "neutral"
        elif normalized_cents < 225:
            return "major_second", "neutral"
        elif normalized_cents < 275:
            return "neutral_third", "neutral"
        elif normalized_cents < 325:
            return "minor_third", "consonant"
        elif normalized_cents < 375:
            return "intermediate_third", "neutral"
        elif normalized_cents < 425:
            return "major_third", "consonant"
        elif normalized_cents < 475:
            return "narrow_fourth", "neutral"
        elif normalized_cents < 525:
            return "fourth", "consonant"
        elif normalized_cents < 575:
            return "augmented_fourth", "dissonant"
        elif normalized_cents < 625:
            return "tritone", "dissonant"
        elif normalized_cents < 675:
            return "diminished_fifth", "dissonant"
        elif normalized_cents < 725:
            return "fifth", "consonant"
        elif normalized_cents < 775:
            return "augmented_fifth", "neutral"
        elif normalized_cents < 825:
            return "minor_sixth", "consonant"
        elif normalized_cents < 875:
            return "neutral_sixth", "neutral"
        elif normalized_cents < 925:
            return "major_sixth", "consonant"
        elif normalized_cents < 975:
            return "neutral_seventh", "neutral"
        elif normalized_cents < 1025:
            return "minor_seventh", "dissonant"
        elif normalized_cents < 1075:
            return "intermediate_seventh", "neutral"
        elif normalized_cents < 1125:
            return "major_seventh", "dissonant"
        elif normalized_cents < 1175:
            return "leading_tone", "dissonant"
        else:
            return "octave", "consonant"
    
    def _find_closest_just_interval(self, cents: float) -> Tuple[Optional[Tuple[int, int]], Optional[float]]:
        """找到最接近的纯律音程"""
        normalized_cents = cents % 1200
        min_deviation = float('inf')
        closest_ratio = None
        
        for interval_name, (just_cents, ratio) in self.just_intervals.items():
            deviation = abs(normalized_cents - just_cents)
            if deviation < min_deviation:
                min_deviation = deviation
                closest_ratio = ratio
        
        return closest_ratio, min_deviation
    
    def _calculate_interval_distribution(self, intervals: List[IntervalInfo]) -> Dict[str, int]:
        """计算音程分布"""
        distribution = defaultdict(int)
        
        for interval in intervals:
            # 按类别统计
            distribution[interval.category] += 1
            
            # 按大小范围统计
            if interval.cents < 50:
                distribution["micro"] += 1
            elif interval.cents < 200:
                distribution["small"] += 1
            elif interval.cents < 400:
                distribution["medium"] += 1
            elif interval.cents < 700:
                distribution["large"] += 1
            else:
                distribution["very_large"] += 1
        
        return dict(distribution)
    
    def _calculate_consonance_profile(self, intervals: List[IntervalInfo]) -> Dict[str, float]:
        """计算协和性轮廓"""
        total_intervals = len(intervals)
        if total_intervals == 0:
            return {}
        
        consonant_count = len([i for i in intervals if i.category == "consonant"])
        dissonant_count = len([i for i in intervals if i.category == "dissonant"])
        neutral_count = len([i for i in intervals if i.category == "neutral"])
        
        return {
            "consonance_ratio": consonant_count / total_intervals,
            "dissonance_ratio": dissonant_count / total_intervals,
            "neutral_ratio": neutral_count / total_intervals,
            "overall_consonance": (consonant_count + neutral_count * 0.5) / total_intervals
        }
    
    def _calculate_complexity_score(self, intervals: List[IntervalInfo]) -> float:
        """计算音程复杂度评分"""
        if not intervals:
            return 0.0
        
        # 基于音程多样性和偏离纯律的程度
        cents_values = [i.cents for i in intervals]
        
        # 多样性评分
        unique_intervals = len(set(round(c, 0) for c in cents_values))
        diversity_score = min(unique_intervals / len(intervals), 1.0)
        
        # 偏离评分（偏离越大，复杂度越高）
        deviations = [i.deviation_from_just for i in intervals if i.deviation_from_just is not None]
        if deviations:
            avg_deviation = statistics.mean(deviations)
            deviation_score = min(avg_deviation / 50.0, 1.0)  # 50音分作为参考
        else:
            deviation_score = 0.5
        
        # 音程大小变化评分
        if len(cents_values) > 1:
            variance = statistics.variance(cents_values)
            variance_score = min(variance / 10000.0, 1.0)  # 标准化
        else:
            variance_score = 0.0
        
        return (diversity_score * 0.4 + deviation_score * 0.4 + variance_score * 0.2)
    
    def _calculate_harmonic_potential(self, intervals: List[IntervalInfo]) -> float:
        """计算和声潜力评分"""
        if not intervals:
            return 0.0
        
        # 基于协和音程的数量和质量
        harmonic_score = 0.0
        total_weight = 0.0
        
        for interval in intervals:
            # 根据音程名称分配权重
            weight = 1.0
            score = 0.0
            
            if interval.category == "consonant":
                score = 0.8
                if "third" in interval.name or "sixth" in interval.name:
                    score = 0.9  # 三度和六度对和声特别重要
                elif "fifth" in interval.name or "fourth" in interval.name:
                    score = 1.0  # 纯五度和纯四度最重要
            elif interval.category == "neutral":
                score = 0.5
            else:  # dissonant
                score = 0.2
            
            # 考虑偏离纯律的影响
            if interval.deviation_from_just is not None:
                deviation_penalty = min(interval.deviation_from_just / 20.0, 0.3)
                score *= (1.0 - deviation_penalty)
            
            harmonic_score += score * weight
            total_weight += weight
        
        return harmonic_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_melodic_potential(self, intervals: List[IntervalInfo]) -> float:
        """计算旋律潜力评分"""
        if not intervals:
            return 0.0
        
        # 基于音程大小的适宜性和流畅性
        melodic_score = 0.0
        total_intervals = len(intervals)
        
        for interval in intervals:
            score = 0.0
            
            # 旋律友好性评分
            if 100 <= interval.cents <= 300:  # 大小二度
                score = 0.9
            elif 300 <= interval.cents <= 500:  # 三度和四度
                score = 0.8
            elif interval.cents < 100:  # 微分音
                score = 0.6
            elif 500 <= interval.cents <= 700:  # 五度
                score = 0.7
            else:  # 大音程
                score = 0.4
            
            melodic_score += score
        
        return melodic_score / total_intervals
    
    def _freq_to_cents(self, ratio: float) -> float:
        """将频率比转换为音分"""
        if ratio <= 0:
            return 0
        return 1200 * math.log2(ratio)
    
    def analyze_interval_relationships(self, entries: List) -> Dict[str, Any]:
        """分析音程关系网络"""
        if len(entries) < 3:
            return {}
        
        frequencies = [entry.freq for entry in entries]
        n = len(frequencies)
        
        # 计算所有可能的音程
        all_intervals = []
        for i in range(n):
            for j in range(i + 1, n):
                ratio = frequencies[j] / frequencies[i]
                cents = self._freq_to_cents(ratio)
                all_intervals.append(cents)
        
        # 分析音程网络特征
        interval_matrix = {}
        for i, freq_i in enumerate(frequencies):
            interval_matrix[i] = {}
            for j, freq_j in enumerate(frequencies):
                if i != j:
                    ratio = freq_j / freq_i if freq_j > freq_i else freq_i / freq_j
                    cents = self._freq_to_cents(ratio)
                    interval_matrix[i][j] = cents
        
        # 寻找特殊关系
        special_relationships = self._find_special_relationships(interval_matrix)
        
        return {
            "total_intervals": len(all_intervals),
            "unique_intervals": len(set(round(c, 1) for c in all_intervals)),
            "interval_matrix": interval_matrix,
            "special_relationships": special_relationships,
            "interval_statistics": {
                "mean": statistics.mean(all_intervals),
                "median": statistics.median(all_intervals),
                "std_dev": statistics.stdev(all_intervals) if len(all_intervals) > 1 else 0
            }
        }
    
    def _find_special_relationships(self, interval_matrix: Dict) -> List[Dict]:
        """寻找特殊的音程关系"""
        special_relationships = []
        
        # 查找纯律关系
        for i in interval_matrix:
            for j in interval_matrix[i]:
                cents = interval_matrix[i][j]
                
                # 检查是否接近纯律音程
                for interval_name, (just_cents, ratio) in self.just_intervals.items():
                    if abs(cents - just_cents) < 10:  # 10音分容差
                        special_relationships.append({
                            "type": "just_intonation",
                            "interval_name": interval_name,
                            "notes": (i, j),
                            "cents": cents,
                            "ratio": ratio,
                            "deviation": abs(cents - just_cents)
                        })
        
        return special_relationships

def format_interval_analysis(analysis: IntervalAnalysis) -> str:
    """格式化音程分析结果"""
    lines = []
    
    lines.append("🎵 === 音程结构分析 ===")
    lines.append(f"📊 音程总数: {len(analysis.intervals)}")
    lines.append(f"🎯 独特音程: {analysis.unique_intervals_count}")
    lines.append(f"🔬 微分音程: {analysis.micro_intervals_count}")
    lines.append(f"📏 大音程: {analysis.large_intervals_count}")
    
    lines.append(f"\n📈 复杂度评分: {analysis.interval_complexity_score:.3f}")
    lines.append(f"🎼 和声潜力: {analysis.harmonic_potential_score:.3f}")
    lines.append(f"🎵 旋律潜力: {analysis.melodic_potential_score:.3f}")
    
    if analysis.consonance_profile:
        lines.append(f"\n🎶 协和性轮廓:")
        lines.append(f"   协和音程: {analysis.consonance_profile.get('consonance_ratio', 0):.1%}")
        lines.append(f"   不协和音程: {analysis.consonance_profile.get('dissonance_ratio', 0):.1%}")
        lines.append(f"   中性音程: {analysis.consonance_profile.get('neutral_ratio', 0):.1%}")
        lines.append(f"   整体协和度: {analysis.consonance_profile.get('overall_consonance', 0):.1%}")
    
    if analysis.interval_distribution:
        lines.append(f"\n📊 音程分布:")
        for category, count in analysis.interval_distribution.items():
            lines.append(f"   {category}: {count}")
    
    return "\n".join(lines)