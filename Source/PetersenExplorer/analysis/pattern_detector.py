"""
模式检测器
检测Petersen音律系统中的数学和音乐模式
"""
from typing import List, Dict, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import math
import statistics
from collections import defaultdict, Counter

@dataclass
class PatternInfo:
    """模式信息"""
    pattern_type: str
    description: str
    occurrences: int
    confidence: float
    mathematical_basis: Optional[str] = None
    musical_significance: Optional[str] = None
    examples: List[Any] = None

@dataclass
class PatternAnalysis:
    """模式分析结果"""
    detected_patterns: List[PatternInfo]
    symmetry_analysis: Dict[str, Any]
    mathematical_relationships: Dict[str, Any]
    scaling_patterns: Dict[str, Any]
    sequence_patterns: Dict[str, Any]
    frequency_ratios: Dict[str, Any]
    geometric_patterns: Dict[str, Any]
    fractal_properties: Dict[str, Any]

class PatternType(Enum):
    """模式类型"""
    ARITHMETIC_SEQUENCE = "arithmetic_sequence"
    GEOMETRIC_SEQUENCE = "geometric_sequence"
    FIBONACCI_LIKE = "fibonacci_like"
    GOLDEN_RATIO = "golden_ratio"
    HARMONIC_SERIES = "harmonic_series"
    SYMMETRIC = "symmetric"
    SPIRAL = "spiral"
    FRACTAL = "fractal"
    PERIODIC = "periodic"
    LOGARITHMIC = "logarithmic"

class PatternDetector:
    """模式检测器"""
    
    def __init__(self):
        """初始化模式检测器"""
        self.golden_ratio = (1 + math.sqrt(5)) / 2
        self.tolerance = 0.05  # 5%容差
        self.min_sequence_length = 3
        
        # 重要数学常数
        self.math_constants = {
            "phi": self.golden_ratio,
            "e": math.e,
            "pi": math.pi,
            "sqrt2": math.sqrt(2),
            "sqrt3": math.sqrt(3),
            "sqrt5": math.sqrt(5)
        }
    
    def detect_patterns(self, entries: List) -> PatternAnalysis:
        """
        检测所有模式
        
        Args:
            entries: 音律条目列表
            
        Returns:
            PatternAnalysis: 模式分析结果
        """
        if len(entries) < 3:
            return PatternAnalysis(
                detected_patterns=[],
                symmetry_analysis={},
                mathematical_relationships={},
                scaling_patterns={},
                sequence_patterns={},
                frequency_ratios={},
                geometric_patterns={},
                fractal_properties={}
            )
        
        frequencies = [entry.freq for entry in entries]
        
        # 检测各种模式
        detected_patterns = []
        
        # 序列模式
        sequence_patterns = self._detect_sequence_patterns(frequencies)
        detected_patterns.extend(self._convert_sequence_to_pattern_info(sequence_patterns))
        
        # 比率模式
        ratio_patterns = self._detect_ratio_patterns(frequencies)
        detected_patterns.extend(self._convert_ratio_to_pattern_info(ratio_patterns))
        
        # 对称模式
        symmetry_analysis = self._analyze_symmetry(frequencies)
        detected_patterns.extend(self._convert_symmetry_to_pattern_info(symmetry_analysis))
        
        # 几何模式
        geometric_patterns = self._detect_geometric_patterns(frequencies)
        detected_patterns.extend(self._convert_geometric_to_pattern_info(geometric_patterns))
        
        # 分形特性
        fractal_properties = self._analyze_fractal_properties(frequencies)
        
        # 数学关系
        mathematical_relationships = self._detect_mathematical_relationships(frequencies)
        
        # 缩放模式
        scaling_patterns = self._detect_scaling_patterns(frequencies)
        
        return PatternAnalysis(
            detected_patterns=detected_patterns,
            symmetry_analysis=symmetry_analysis,
            mathematical_relationships=mathematical_relationships,
            scaling_patterns=scaling_patterns,
            sequence_patterns=sequence_patterns,
            frequency_ratios=ratio_patterns,
            geometric_patterns=geometric_patterns,
            fractal_properties=fractal_properties
        )
    
    def _detect_sequence_patterns(self, frequencies: List[float]) -> Dict[str, Any]:
        """检测序列模式"""
        patterns = {}
        
        # 等差序列检测
        arithmetic_patterns = self._detect_arithmetic_sequences(frequencies)
        patterns["arithmetic"] = arithmetic_patterns
        
        # 等比序列检测
        geometric_patterns = self._detect_geometric_sequences(frequencies)
        patterns["geometric"] = geometric_patterns
        
        # 斐波那契类序列检测
        fibonacci_patterns = self._detect_fibonacci_like_sequences(frequencies)
        patterns["fibonacci"] = fibonacci_patterns
        
        # 周期性模式检测
        periodic_patterns = self._detect_periodic_patterns(frequencies)
        patterns["periodic"] = periodic_patterns
        
        return patterns
    
    def _detect_arithmetic_sequences(self, frequencies: List[float]) -> List[Dict]:
        """检测等差序列"""
        sequences = []
        n = len(frequencies)
        
        for start in range(n - 2):
            for length in range(3, min(n - start + 1, 8)):  # 最长7个元素
                subseq = frequencies[start:start + length]
                
                # 检查是否为等差数列
                differences = [subseq[i+1] - subseq[i] for i in range(len(subseq) - 1)]
                
                if len(differences) > 1:
                    avg_diff = statistics.mean(differences)
                    if avg_diff > 0:  # 避免除零
                        relative_errors = [abs(d - avg_diff) / avg_diff for d in differences]
                        max_error = max(relative_errors)
                        
                        if max_error < self.tolerance:
                            sequences.append({
                                "start_index": start,
                                "length": length,
                                "difference": avg_diff,
                                "sequence": subseq,
                                "confidence": 1.0 - max_error
                            })
        
        return sequences
    
    def _detect_geometric_sequences(self, frequencies: List[float]) -> List[Dict]:
        """检测等比序列"""
        sequences = []
        n = len(frequencies)
        
        for start in range(n - 2):
            for length in range(3, min(n - start + 1, 8)):
                subseq = frequencies[start:start + length]
                
                # 检查是否为等比数列
                if all(f > 0 for f in subseq):  # 确保所有频率为正
                    ratios = [subseq[i+1] / subseq[i] for i in range(len(subseq) - 1)]
                    
                    if len(ratios) > 1:
                        avg_ratio = statistics.mean(ratios)
                        if avg_ratio > 0:
                            relative_errors = [abs(r - avg_ratio) / avg_ratio for r in ratios]
                            max_error = max(relative_errors)
                            
                            if max_error < self.tolerance:
                                sequences.append({
                                    "start_index": start,
                                    "length": length,
                                    "ratio": avg_ratio,
                                    "sequence": subseq,
                                    "confidence": 1.0 - max_error
                                })
        
        return sequences
    
    def _detect_fibonacci_like_sequences(self, frequencies: List[float]) -> List[Dict]:
        """检测斐波那契类序列"""
        sequences = []
        n = len(frequencies)
        
        for start in range(n - 2):
            for length in range(3, min(n - start + 1, 8)):
                subseq = frequencies[start:start + length]
                
                # 检查是否类似斐波那契序列：F(n) = F(n-1) + F(n-2)
                if length >= 3:
                    errors = []
                    for i in range(2, len(subseq)):
                        expected = subseq[i-1] + subseq[i-2]
                        if expected > 0:
                            error = abs(subseq[i] - expected) / expected
                            errors.append(error)
                    
                    if errors and max(errors) < self.tolerance * 2:  # 放宽容差
                        avg_error = statistics.mean(errors)
                        sequences.append({
                            "start_index": start,
                            "length": length,
                            "sequence": subseq,
                            "confidence": 1.0 - avg_error,
                            "type": "fibonacci_like"
                        })
        
        return sequences
    
    def _detect_periodic_patterns(self, frequencies: List[float]) -> List[Dict]:
        """检测周期性模式"""
        patterns = []
        n = len(frequencies)
        
        # 检测不同周期长度
        for period in range(2, min(n // 2, 6)):
            for start in range(n - period * 2 + 1):
                # 提取两个周期
                pattern1 = frequencies[start:start + period]
                pattern2 = frequencies[start + period:start + period * 2]
                
                if len(pattern1) == len(pattern2) == period:
                    # 计算相似度
                    errors = []
                    for i in range(period):
                        if pattern1[i] > 0:
                            error = abs(pattern1[i] - pattern2[i]) / pattern1[i]
                            errors.append(error)
                    
                    if errors and max(errors) < self.tolerance:
                        avg_error = statistics.mean(errors)
                        patterns.append({
                            "start_index": start,
                            "period": period,
                            "pattern": pattern1,
                            "confidence": 1.0 - avg_error,
                            "repetitions": 2
                        })
        
        return patterns
    
    def _detect_ratio_patterns(self, frequencies: List[float]) -> Dict[str, Any]:
        """检测比率模式"""
        patterns = {}
        
        # 计算所有相邻比率
        ratios = []
        for i in range(len(frequencies) - 1):
            if frequencies[i] > 0:
                ratio = frequencies[i + 1] / frequencies[i]
                ratios.append(ratio)
        
        patterns["adjacent_ratios"] = ratios
        
        # 检测特殊比率
        special_ratios = self._detect_special_ratios(ratios)
        patterns["special_ratios"] = special_ratios
        
        # 检测黄金比例
        golden_ratio_patterns = self._detect_golden_ratio_patterns(ratios)
        patterns["golden_ratio"] = golden_ratio_patterns
        
        # 检测泛音列关系
        harmonic_patterns = self._detect_harmonic_series_patterns(frequencies)
        patterns["harmonic_series"] = harmonic_patterns
        
        return patterns
    
    def _detect_special_ratios(self, ratios: List[float]) -> List[Dict]:
        """检测特殊比率"""
        special_patterns = []
        
        for constant_name, constant_value in self.math_constants.items():
            matches = []
            for i, ratio in enumerate(ratios):
                if abs(ratio - constant_value) / constant_value < self.tolerance:
                    matches.append({
                        "index": i,
                        "ratio": ratio,
                        "expected": constant_value,
                        "error": abs(ratio - constant_value) / constant_value
                    })
            
            if matches:
                avg_error = statistics.mean([m["error"] for m in matches])
                special_patterns.append({
                    "constant": constant_name,
                    "value": constant_value,
                    "matches": matches,
                    "count": len(matches),
                    "confidence": 1.0 - avg_error
                })
        
        return special_patterns
    
    def _detect_golden_ratio_patterns(self, ratios: List[float]) -> Dict[str, Any]:
        """检测黄金比例模式"""
        golden_matches = []
        
        for i, ratio in enumerate(ratios):
            # 检测φ
            if abs(ratio - self.golden_ratio) / self.golden_ratio < self.tolerance:
                golden_matches.append({
                    "index": i,
                    "ratio": ratio,
                    "type": "phi",
                    "error": abs(ratio - self.golden_ratio) / self.golden_ratio
                })
            
            # 检测1/φ
            inverse_phi = 1.0 / self.golden_ratio
            if abs(ratio - inverse_phi) / inverse_phi < self.tolerance:
                golden_matches.append({
                    "index": i,
                    "ratio": ratio,
                    "type": "inverse_phi",
                    "error": abs(ratio - inverse_phi) / inverse_phi
                })
            
            # 检测φ²
            phi_squared = self.golden_ratio ** 2
            if abs(ratio - phi_squared) / phi_squared < self.tolerance:
                golden_matches.append({
                    "index": i,
                    "ratio": ratio,
                    "type": "phi_squared",
                    "error": abs(ratio - phi_squared) / phi_squared
                })
        
        return {
            "matches": golden_matches,
            "total_count": len(golden_matches),
            "phi_dominance": len(golden_matches) / len(ratios) if ratios else 0
        }
    
    def _detect_harmonic_series_patterns(self, frequencies: List[float]) -> Dict[str, Any]:
        """检测泛音列模式"""
        if not frequencies:
            return {}
        
        # 以最低频率为基频
        fundamental = min(frequencies)
        
        harmonic_matches = []
        for i, freq in enumerate(frequencies):
            # 检查是否为整数倍泛音
            harmonic_number = freq / fundamental
            closest_integer = round(harmonic_number)
            
            if closest_integer > 0:
                error = abs(harmonic_number - closest_integer) / closest_integer
                if error < self.tolerance:
                    harmonic_matches.append({
                        "index": i,
                        "frequency": freq,
                        "harmonic_number": closest_integer,
                        "exact_ratio": harmonic_number,
                        "error": error
                    })
        
        return {
            "fundamental": fundamental,
            "matches": harmonic_matches,
            "harmonic_count": len(harmonic_matches),
            "coverage": len(harmonic_matches) / len(frequencies)
        }
    
    def _analyze_symmetry(self, frequencies: List[float]) -> Dict[str, Any]:
        """分析对称性"""
        symmetry_analysis = {}
        
        # 镜像对称检测
        mirror_symmetry = self._detect_mirror_symmetry(frequencies)
        symmetry_analysis["mirror"] = mirror_symmetry
        
        # 旋转对称检测（在对数空间中）"""