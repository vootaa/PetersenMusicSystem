"""
和声评估器
评估Petersen音律系统的和声构建能力和潜力
"""
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum
import itertools
import math
from collections import defaultdict

@dataclass
class ChordInfo:
    """和弦信息"""
    notes: List[int]  # 音符索引
    frequencies: List[float]
    intervals: List[float]  # 音程（音分）
    chord_type: str
    quality: str  # major, minor, diminished, augmented, complex
    dissonance_level: float
    harmonic_complexity: float
    traditional_match: Optional[str] = None

@dataclass
class HarmonyAnalysis:
    """和声分析结果"""
    available_chords: List[ChordInfo]
    chord_type_distribution: Dict[str, int]
    harmonic_richness_score: float
    chord_progression_potential: float
    voice_leading_quality: float
    functional_harmony_compatibility: float
    extended_harmony_potential: float
    modulation_flexibility: float

class ChordType(Enum):
    """和弦类型"""
    TRIAD_MAJOR = "major_triad"
    TRIAD_MINOR = "minor_triad"
    TRIAD_DIMINISHED = "diminished_triad"
    TRIAD_AUGMENTED = "augmented_triad"
    SEVENTH_MAJOR = "major_seventh"
    SEVENTH_MINOR = "minor_seventh"
    SEVENTH_DOMINANT = "dominant_seventh"
    SEVENTH_DIMINISHED = "diminished_seventh"
    EXTENDED = "extended"
    SUSPENDED = "suspended"
    QUARTAL = "quartal"
    CLUSTER = "cluster"
    MICROTONAL = "microtonal"
    EXOTIC = "exotic"

class HarmonyEvaluator:
    """和声评估器"""
    
    def __init__(self):
        """初始化和声评估器"""
        # 传统和弦模板（音分）
        self.chord_templates = {
            "major_triad": [0, 386, 702],  # 1-3-5 (纯律)
            "minor_triad": [0, 316, 702],  # 1-♭3-5
            "diminished_triad": [0, 316, 590],  # 1-♭3-♭5
            "augmented_triad": [0, 386, 814],  # 1-3-#5
            "major_seventh": [0, 386, 702, 1088],  # 1-3-5-7
            "minor_seventh": [0, 316, 702, 996],  # 1-♭3-5-♭7
            "dominant_seventh": [0, 386, 702, 996],  # 1-3-5-♭7
            "suspended_fourth": [0, 498, 702],  # 1-4-5
            "suspended_second": [0, 204, 702],  # 1-2-5
        }
        
        # 和弦质量评分权重
        self.chord_quality_weights = {
            "major_triad": 1.0,
            "minor_triad": 1.0,
            "dominant_seventh": 0.9,
            "major_seventh": 0.8,
            "minor_seventh": 0.8,
            "suspended_fourth": 0.7,
            "suspended_second": 0.6,
            "diminished_triad": 0.5,
            "augmented_triad": 0.4,
            "exotic": 0.3
        }
        
        # 不协和度参考值
        self.dissonance_factors = {
            "unison": 0.0,
            "octave": 0.0,
            "fifth": 0.1,
            "fourth": 0.2,
            "major_third": 0.3,
            "minor_third": 0.3,
            "major_sixth": 0.4,
            "minor_sixth": 0.4,
            "major_second": 0.7,
            "minor_second": 0.9,
            "major_seventh": 0.8,
            "minor_seventh": 0.6,
            "tritone": 1.0
        }
    
    def evaluate_harmony(self, entries: List) -> HarmonyAnalysis:
        """
        评估和声能力
        
        Args:
            entries: 音律条目列表
            
        Returns:
            HarmonyAnalysis: 和声分析结果
        """
        if len(entries) < 3:
            return HarmonyAnalysis(
                available_chords=[],
                chord_type_distribution={},
                harmonic_richness_score=0.0,
                chord_progression_potential=0.0,
                voice_leading_quality=0.0,
                functional_harmony_compatibility=0.0,
                extended_harmony_potential=0.0,
                modulation_flexibility=0.0
            )
        
        frequencies = [entry.freq for entry in entries]
        
        # 分析所有可能的和弦
        available_chords = self._analyze_all_chords(frequencies)
        
        # 计算和弦类型分布
        chord_type_distribution = self._calculate_chord_distribution(available_chords)
        
        # 计算各项评分
        harmonic_richness_score = self._calculate_harmonic_richness(available_chords)
        chord_progression_potential = self._calculate_progression_potential(available_chords, frequencies)
        voice_leading_quality = self._calculate_voice_leading_quality(available_chords, frequencies)
        functional_harmony_compatibility = self._calculate_functional_compatibility(available_chords)
        extended_harmony_potential = self._calculate_extended_harmony_potential(available_chords)
        modulation_flexibility = self._calculate_modulation_flexibility(available_chords, frequencies)
        
        return HarmonyAnalysis(
            available_chords=available_chords,
            chord_type_distribution=chord_type_distribution,
            harmonic_richness_score=harmonic_richness_score,
            chord_progression_potential=chord_progression_potential,
            voice_leading_quality=voice_leading_quality,
            functional_harmony_compatibility=functional_harmony_compatibility,
            extended_harmony_potential=extended_harmony_potential,
            modulation_flexibility=modulation_flexibility
        )
    
    def _analyze_all_chords(self, frequencies: List[float]) -> List[ChordInfo]:
        """分析所有可能的和弦"""
        chords = []
        n = len(frequencies)
        
        # 分析三和弦
        for combination in itertools.combinations(range(n), 3):
            chord = self._analyze_chord(combination, frequencies)
            if chord:
                chords.append(chord)
        
        # 分析四和弦
        if n >= 4:
            for combination in itertools.combinations(range(n), 4):
                chord = self._analyze_chord(combination, frequencies)
                if chord:
                    chords.append(chord)
        
        # 分析五和弦及以上（限制数量）
        if n >= 5:
            for size in range(5, min(n + 1, 7)):  # 最多分析到六和弦
                # 随机采样以避免组合爆炸
                combinations = list(itertools.combinations(range(n), size))
                if len(combinations) > 20:  # 限制组合数量
                    import random
                    combinations = random.sample(combinations, 20)
                
                for combination in combinations:
                    chord = self._analyze_chord(combination, frequencies)
                    if chord:
                        chords.append(chord)
        
        return chords
    
    def _analyze_chord(self, note_indices: Tuple[int, ...], frequencies: List[float]) -> Optional[ChordInfo]:
        """分析单个和弦"""
        if len(note_indices) < 3:
            return None
        
        # 获取和弦音符的频率
        chord_frequencies = [frequencies[i] for i in note_indices]
        chord_frequencies.sort()
        
        # 计算音程（相对于根音）
        root_freq = chord_frequencies[0]
        intervals = []
        
        for freq in chord_frequencies:
            if freq == root_freq:
                intervals.append(0.0)
            else:
                ratio = freq / root_freq
                cents = 1200 * math.log2(ratio)
                intervals.append(cents)
        
        # 识别和弦类型
        chord_type, quality, traditional_match = self._identify_chord_type(intervals)
        
        # 计算不协和度
        dissonance_level = self._calculate_chord_dissonance(intervals)
        
        # 计算和声复杂度
        harmonic_complexity = self._calculate_harmonic_complexity(intervals)
        
        return ChordInfo(
            notes=list(note_indices),
            frequencies=chord_frequencies,
            intervals=intervals,
            chord_type=chord_type,
            quality=quality,
            dissonance_level=dissonance_level,
            harmonic_complexity=harmonic_complexity,
            traditional_match=traditional_match
        )
    
    def _identify_chord_type(self, intervals: List[float]) -> Tuple[str, str, Optional[str]]:
        """识别和弦类型"""
        if len(intervals) < 3:
            return "incomplete", "unknown", None
        
        # 标准化音程到八度内
        normalized_intervals = [i % 1200 for i in intervals[1:]]  # 排除根音
        normalized_intervals.sort()
        
        # 与模板匹配
        best_match = None
        best_score = float('inf')
        
        for template_name, template_intervals in self.chord_templates.items():
            template_normalized = template_intervals[1:]  # 排除根音
            
            if len(template_normalized) == len(normalized_intervals):
                # 计算匹配度
                total_deviation = 0
                for i, template_interval in enumerate(template_normalized):
                    min_deviation = min(
                        abs(normalized_intervals[i] - template_interval),
                        abs(normalized_intervals[i] - (template_interval + 1200)),
                        abs((normalized_intervals[i] + 1200) - template_interval)
                    )
                    total_deviation += min_deviation
                
                avg_deviation = total_deviation / len(template_normalized)
                
                if avg_deviation < best_score:
                    best_score = avg_deviation
                    best_match = template_name
        
        # 根据匹配结果确定类型和质量
        if best_match and best_score < 50:  # 50音分容差
            chord_type = best_match
            if "major" in best_match:
                quality = "major"
            elif "minor" in best_match:
                quality = "minor"
            elif "diminished" in best_match:
                quality = "diminished"
            elif "augmented" in best_match:
                quality = "augmented"
            else:
                quality = "other"
            traditional_match = best_match
        else:
            # 分析非传统和弦
            chord_type, quality = self._classify_exotic_chord(normalized_intervals)
            traditional_match = None
        
        return chord_type, quality, traditional_match
    
    def _classify_exotic_chord(self, intervals: List[float]) -> Tuple[str, str]:
        """分类非传统和弦"""
        if not intervals:
            return "empty", "unknown"
        
        # 检查四度叠置
        quartal_threshold = 50  # 50音分容差
        is_quartal = True
        for interval in intervals:
            if not (450 < interval < 550):  # 约500音分（纯四度）
                is_quartal = False
                break
        
        if is_quartal and len(intervals) >= 2:
            return "quartal", "quartal"
        
        # 检查簇状和弦
        max_interval = max(intervals)
        if max_interval < 300:  # 所有音程都在小三度以内
            return "cluster", "cluster"
        
        # 检查微分音和弦
        has_microtones = any(50 < interval < 150 for interval in intervals)
        if has_microtones:
            return "microtonal", "microtonal"
        
        # 检查扩展和弦
        if len(intervals) > 4:
            return "extended", "extended"
        
        return "exotic", "complex"
    
    def _calculate_chord_dissonance(self, intervals: List[float]) -> float:
        """计算和弦不协和度"""
        if len(intervals) < 2:
            return 0.0
        
        total_dissonance = 0.0
        pair_count = 0
        
        # 计算所有音程对的不协和度
        for i in range(len(intervals)):
            for j in range(i + 1, len(intervals)):
                interval_cents = abs(intervals[j] - intervals[i])
                interval_cents = interval_cents % 1200  # 标准化到八度内
                
                # 查找最接近的已知音程
                min_diff = float('inf')
                for interval_name, cents in self.chord_templates.get("reference_intervals", {}).items():
                    diff = min(abs(interval_cents - cents), abs(interval_cents - (cents + 1200)))
                    if diff < min_diff:
                        min_diff = diff
                
                # 基于音程大小估算不协和度
                if interval_cents < 100:  # 小二度及微分音
                    dissonance = 0.9
                elif interval_cents < 200:  # 大二度
                    dissonance = 0.7
                elif 200 <= interval_cents < 400:  # 三度
                    dissonance = 0.3
                elif 400 <= interval_cents < 500:  # 四度
                    dissonance = 0.2
                elif 500 <= interval_cents < 600:  # 增四度/减五度
                    dissonance = 1.0
                elif 600 <= interval_cents < 800:  # 五度
                    dissonance = 0.1
                else:  # 六度、七度
                    dissonance = 0.4
                
                total_dissonance += dissonance
                pair_count += 1
        
        return total_dissonance / pair_count if pair_count > 0 else 0.0
    
    def _calculate_harmonic_complexity(self, intervals: List[float]) -> float:
        """计算和声复杂度"""
        if len(intervals) < 2:
            return 0.0
        
        # 基于音程数量和独特性
        unique_intervals = len(set(round(i, 0) for i in intervals))
        complexity_from_variety = min(unique_intervals / len(intervals), 1.0)
        
        # 基于音程大小的分散程度
        if len(intervals) > 1:
            import statistics
            interval_range = max(intervals) - min(intervals)
            complexity_from_range = min(interval_range / 1200.0, 1.0)
        else:
            complexity_from_range = 0.0
        
        return (complexity_from_variety + complexity_from_range) / 2
    
    def _calculate_chord_distribution(self, chords: List[ChordInfo]) -> Dict[str, int]:
        """计算和弦类型分布"""
        distribution = defaultdict(int)
        
        for chord in chords:
            distribution[chord.chord_type] += 1
            distribution[chord.quality] += 1
        
        return dict(distribution)
    
    def _calculate_harmonic_richness(self, chords: List[ChordInfo]) -> float:
        """计算和声丰富度"""
        if not chords:
            return 0.0
        
        # 基于和弦类型多样性
        unique_types = len(set(chord.chord_type for chord in chords))
        type_diversity = min(unique_types / 10.0, 1.0)  # 假设10种类型为满分
        
        # 基于质量评分加权
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for chord in chords:
            weight = self.chord_quality_weights.get(chord.chord_type, 0.2)
            score = 1.0 - chord.dissonance_level  # 不协和度越低，评分越高
            
            total_weighted_score += score * weight
            total_weight += weight
        
        quality_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        return (type_diversity * 0.6 + quality_score * 0.4)
    
    def _calculate_progression_potential(self, chords: List[ChordInfo], frequencies: List[float]) -> float:
        """计算和弦进行潜力"""
        if len(chords) < 2:
            return 0.0
        
        # 分析和弦间的关系
        progression_score = 0.0
        comparison_count = 0
        
        for i, chord1 in enumerate(chords[:10]):  # 限制比较数量
            for chord2 in chords[i+1:i+6]:  # 每个和弦与后续5个比较
                # 计算共同音数量
                common_notes = len(set(chord1.notes) & set(chord2.notes))
                voice_leading_quality = common_notes / max(len(chord1.notes), len(chord2.notes))
                
                # 计算根音关系
                root_interval = abs(chord1.frequencies[0] - chord2.frequencies[0])
                root_cents = 1200 * math.log2(chord2.frequencies[0] / chord1.frequencies[0])
                
                # 评估进行质量
                if abs(root_cents - 700) < 50:  # 五度关系
                    root_quality = 1.0
                elif abs(root_cents - 500) < 50:  # 四度关系
                    root_quality = 0.9
                elif abs(root_cents - 400) < 50 or abs(root_cents - 300) < 50:  # 三度关系
                    root_quality = 0.8
                else:
                    root_quality = 0.5
                
                progression_quality = (voice_leading_quality * 0.6 + root_quality * 0.4)
                progression_score += progression_quality
                comparison_count += 1
        
        return progression_score / comparison_count if comparison_count > 0 else 0.0
    
    def _calculate_voice_leading_quality(self, chords: List[ChordInfo], frequencies: List[float]) -> float:
        """计算声部进行质量"""
        if len(chords) < 2:
            return 0.0
        
        # 简化评估：基于和弦间的平均音程距离
        total_smoothness = 0.0
        comparison_count = 0
        
        for i, chord1 in enumerate(chords[:5]):  # 限制数量
            for chord2 in chords[i+1:i+3]:
                # 计算最近声部移动
                min_movements = []
                
                for note1 in chord1.frequencies:
                    min_distance = min(abs(note1 - note2) for note2 in chord2.frequencies)
                    min_movements.append(min_distance)
                
                # 平滑度评分：移动距离越小越好
                avg_movement = sum(min_movements) / len(min_movements)
                smoothness = max(0, 1.0 - avg_movement / 200.0)  # 200Hz作为参考
                
                total_smoothness += smoothness
                comparison_count += 1
        
        return total_smoothness / comparison_count if comparison_count > 0 else 0.0
    
    def _calculate_functional_compatibility(self, chords: List[ChordInfo]) -> float:
        """计算功能和声兼容性"""
        if not chords:
            return 0.0
        
        # 统计传统和弦类型
        traditional_chords = [c for c in chords if c.traditional_match is not None]
        traditional_ratio = len(traditional_chords) / len(chords)
        
        # 检查主要功能和弦的存在
        essential_functions = ["major_triad", "minor_triad", "dominant_seventh"]
        available_functions = set(c.traditional_match for c in traditional_chords if c.traditional_match)
        
        function_coverage = len(available_functions & set(essential_functions)) / len(essential_functions)
        
        return (traditional_ratio * 0.7 + function_coverage * 0.3)
    
    def _calculate_extended_harmony_potential(self, chords: List[ChordInfo]) -> float:
        """计算扩展和声潜力"""
        if not chords:
            return 0.0
        
        # 统计扩展和弦和复杂和弦
        extended_chords = [c for c in chords if len(c.notes) > 3 or c.chord_type in ["extended", "exotic", "microtonal"]]
        extended_ratio = len(extended_chords) / len(chords)
        
        # 评估和声复杂度分布
        avg_complexity = sum(c.harmonic_complexity for c in chords) / len(chords)
        
        return (extended_ratio * 0.6 + avg_complexity * 0.4)
    
    def _calculate_modulation_flexibility(self, chords: List[ChordInfo], frequencies: List[float]) -> float:
        """计算转调灵活性"""
        if len(frequencies) < 7:  # 需要足够的音符支持转调
            return 0.0
        
        # 简化评估：基于可用音符的分布和和弦多样性
        frequency_range = max(frequencies) - min(frequencies)
        range_score = min(frequency_range / 1000.0, 1.0)  # 1000Hz作为参考范围
        
        # 和弦根音分布
        root_frequencies = [c.frequencies[0] for c in chords]
        unique_roots = len(set(round(f, 1) for f in root_frequencies))
        root_diversity = min(unique_roots / 7.0, 1.0)  # 7个不同根音为理想
        
        return (range_score * 0.5 + root_diversity * 0.5)

def format_harmony_analysis(analysis: HarmonyAnalysis) -> str:
    """格式化和声分析结果"""
    lines = []
    
    lines.append("🎼 === 和声构建能力分析 ===")
    lines.append(f"🎵 可用和弦: {len(analysis.available_chords)}")
    
    lines.append(f"\n📊 综合评分:")
    lines.append(f"   和声丰富度: {analysis.harmonic_richness_score:.3f}")
    lines.append(f"   进行潜力: {analysis.chord_progression_potential:.3f}")
    lines.append(f"   声部质量: {analysis.voice_leading_quality:.3f}")
    lines.append(f"   功能兼容性: {analysis.functional_harmony_compatibility:.3f}")
    lines.append(f"   扩展潜力: {analysis.extended_harmony_potential:.3f}")
    lines.append(f"   转调灵活性: {analysis.modulation_flexibility:.3f}")
    
    if analysis.chord_type_distribution:
        lines.append(f"\n🎯 和弦类型分布:")
        sorted_types = sorted(analysis.chord_type_distribution.items(), key=lambda x: x[1], reverse=True)
        for chord_type, count in sorted_types[:8]:  # 显示前8种
            lines.append(f"   {chord_type}: {count}")
    
    return "\n".join(lines)