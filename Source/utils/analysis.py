"""
音频分析和频率计算工具
"""
import math
import numpy as np
from typing import Tuple, List, Dict, Optional

import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from constants import CENTS_PER_SEMITONE, CENTS_PER_OCTAVE

class FrequencyAnalyzer:
    """频率分析器"""
    
    @staticmethod
    def midi_note_to_frequency(midi_note: int, a4_frequency: float = 440.0) -> float:
        """MIDI音符号转频率"""
        return a4_frequency * (2 ** ((midi_note - 69) / 12.0))
    
    @staticmethod
    def frequency_to_midi_note(frequency: float, a4_frequency: float = 440.0) -> float:
        """频率转MIDI音符号（可能是小数）"""
        return 69 + 12 * math.log2(frequency / a4_frequency)
    
    @staticmethod
    def frequency_error_in_cents(target_freq: float, reference_freq: float) -> float:
        """
        计算频率误差（音分）
        
        Args:
            target_freq: 目标频率
            reference_freq: 参考频率
            
        Returns:
            频率误差（音分），正值表示目标频率高于参考频率
        """
        if reference_freq <= 0 or target_freq <= 0:
            return 0.0
        return 1200 * math.log2(target_freq / reference_freq)
    
    @staticmethod
    def frequency_to_midi_note_integer(frequency: float, a4_frequency: float = 440.0) -> int:
        """
        频率转最接近的整数MIDI音符号
        
        Args:
            frequency: 频率
            a4_frequency: A4参考频率
            
        Returns:
            最接近的整数MIDI音符号
        """
        exact_midi = FrequencyAnalyzer.frequency_to_midi_note(frequency, a4_frequency)
        return int(round(exact_midi))
    
    @staticmethod
    def find_closest_midi_note(target_frequency: float, 
                             a4_frequency: float = 440.0) -> Tuple[int, float, float]:
        """
        找到最接近目标频率的MIDI音符
        
        Returns:
            (midi_note, standard_frequency, cents_deviation)
        """
        exact_midi = FrequencyAnalyzer.frequency_to_midi_note(target_frequency, a4_frequency)
        closest_midi = round(exact_midi)
        
        # 限制在有效MIDI范围内
        closest_midi = max(0, min(127, closest_midi))
        
        standard_freq = FrequencyAnalyzer.midi_note_to_frequency(closest_midi, a4_frequency)
        cents_deviation = FrequencyAnalyzer.frequency_error_in_cents(target_frequency, standard_freq)
        
        return closest_midi, standard_freq, cents_deviation
    
    @staticmethod
    def calculate_pitch_bend(target_frequency: float, 
                           midi_note: int,
                           a4_frequency: float = 440.0,
                           bend_range_cents: float = 200.0) -> int:
        """
        计算达到目标频率所需的弯音轮值
        
        Returns:
            弯音轮值 (0-16383, 8192为中性)
        """
        standard_freq = FrequencyAnalyzer.midi_note_to_frequency(midi_note, a4_frequency)
        cents_diff = 1200 * math.log2(target_frequency / standard_freq)
        
        # 转换为弯音轮值
        bend_ratio = cents_diff / bend_range_cents
        bend_value = int(8192 + bend_ratio * 8192)
        
        # 限制在有效范围内
        return max(0, min(16383, bend_value))
    
    @staticmethod
    def analyze_frequency_deviation(frequencies: List[float], 
                                  a4_frequency: float = 440.0) -> Dict:
        """
        分析频率列表的偏差统计
        
        Returns:
            包含偏差统计信息的字典
        """
        deviations = []
        midi_notes = []
        
        for freq in frequencies:
            midi_note, standard_freq, cents_dev = FrequencyAnalyzer.find_closest_midi_note(freq, a4_frequency)
            deviations.append(abs(cents_dev))
            midi_notes.append(midi_note)
        
        return {
            'frequencies': frequencies,
            'midi_notes': midi_notes,
            'cents_deviations': deviations,
            'max_deviation': max(deviations) if deviations else 0,
            'avg_deviation': sum(deviations) / len(deviations) if deviations else 0,
            'needs_compensation_count': sum(1 for d in deviations if d > 5.0),
            'compensation_percentage': (sum(1 for d in deviations if d > 5.0) / len(deviations) * 100) if deviations else 0
        }

class SoundFontAnalyzer:
    """SoundFont分析器"""
    
    @staticmethod
    def detect_piano_quality(sf_size_mb: float, sf_name: str) -> str:
        """根据文件大小和名称推断钢琴音质"""
        if 'steinway' in sf_name.lower():
            if sf_size_mb > 500:
                return 'professional_grand'
            else:
                return 'high_quality_grand'
        elif sf_size_mb > 100:
            return 'good_quality'
        elif sf_size_mb > 50:
            return 'standard_quality'
        else:
            return 'basic_quality'
    
    @staticmethod
    def estimate_instrument_count(sf_size_mb: float, sf_name: str) -> int:
        """估算SoundFont包含的乐器数量"""
        if 'orchestra' in sf_name.lower() or 'symphonic' in sf_name.lower():
            return max(50, int(sf_size_mb / 10))
        elif 'steinway' in sf_name.lower() or 'piano' in sf_name.lower():
            return 8  # 通常只有钢琴系列
        else:
            return max(10, int(sf_size_mb / 5))
    
    @staticmethod
    def recommend_settings(sf_name: str, sf_size_mb: float) -> Dict:
        """根据SoundFont特性推荐设置"""
        settings = {
            'reverb': {'room_size': 0.2, 'damping': 0.0, 'width': 0.5, 'level': 0.9},
            'chorus': {'voices': 3, 'level': 2.0, 'speed': 0.3, 'depth': 8.0},
            'use_effects': True,
            'velocity_sensitivity': 0.8,
            'recommended_instruments': []
        }
        
        if 'steinway' in sf_name.lower():
            # 专业钢琴设置
            settings['reverb'] = {'room_size': 0.4, 'damping': 0.1, 'width': 0.8, 'level': 0.7}
            settings['chorus']['level'] = 0.5  # 钢琴少用合唱
            settings['velocity_sensitivity'] = 0.9
            settings['recommended_instruments'] = ['acoustic_grand', 'bright_acoustic']
            
        elif 'orchestra' in sf_name.lower():
            # 管弦乐设置
            settings['reverb'] = {'room_size': 0.6, 'damping': 0.2, 'width': 1.0, 'level': 0.8}
            settings['velocity_sensitivity'] = 0.7
            settings['recommended_instruments'] = ['violin', 'flute', 'trumpet', 'acoustic_grand']
        
        return settings

class PerformanceAnalyzer:
    """演奏性能分析器"""
    
    @staticmethod
    def calculate_optimal_velocity_curve(frequencies: List[float], 
                                       target_dynamic: str = 'balanced') -> List[int]:
        """计算最优力度曲线"""
        count = len(frequencies)
        if count == 0:
            return []
        
        base_velocity = 80
        velocities = []
        
        for i, freq in enumerate(frequencies):
            # 根据频率调整基础力度
            if freq < 100:
                freq_factor = 0.9  # 低频稍弱
            elif freq > 2000:
                freq_factor = 0.85  # 高频稍弱
            else:
                freq_factor = 1.0
            
            # 根据动态模式调整
            if target_dynamic == 'crescendo':
                dynamic_factor = 0.6 + 0.4 * (i / (count - 1)) if count > 1 else 1.0
            elif target_dynamic == 'diminuendo':
                dynamic_factor = 1.0 - 0.4 * (i / (count - 1)) if count > 1 else 1.0
            elif target_dynamic == 'arch':
                mid_point = count / 2
                if i <= mid_point:
                    dynamic_factor = 0.6 + 0.4 * (i / mid_point)
                else:
                    dynamic_factor = 1.0 - 0.4 * ((i - mid_point) / mid_point)
            else:  # balanced
                dynamic_factor = 1.0
            
            velocity = int(base_velocity * freq_factor * dynamic_factor)
            velocities.append(max(1, min(127, velocity)))
        
        return velocities
    
    @staticmethod
    def calculate_timing_variations(note_count: int, 
                                  base_duration: float = 0.5,
                                  timing_style: str = 'mechanical') -> List[float]:
        """计算时值变化"""
        if timing_style == 'mechanical':
            return [base_duration] * note_count
        
        durations = []
        for i in range(note_count):
            if timing_style == 'rubato':
                # 轻微的时值变化
                variation = 0.9 + 0.2 * math.sin(i * 0.5)
                durations.append(base_duration * variation)
            elif timing_style == 'accelerando':
                # 逐渐加快
                factor = 1.0 - 0.3 * (i / note_count) if note_count > 0 else 1.0
                durations.append(base_duration * factor)
            elif timing_style == 'ritardando':
                # 逐渐放慢
                factor = 1.0 + 0.5 * (i / note_count) if note_count > 0 else 1.0
                durations.append(base_duration * factor)
            else:
                durations.append(base_duration)
        
        return durations

def analyze_petersen_scale_characteristics(scale_entries) -> Dict:
    """分析Petersen音阶特性"""
    if not scale_entries:
        return {}
    
    frequencies = [entry.freq for entry in scale_entries]
    zones = [entry.n for entry in scale_entries]
    elements = [entry.e for entry in scale_entries]
    polarities = [entry.p for entry in scale_entries]
    
    freq_analysis = FrequencyAnalyzer.analyze_frequency_deviation(frequencies)
    
    return {
        'frequency_analysis': freq_analysis,
        'frequency_range': (min(frequencies), max(frequencies)),
        'zone_distribution': {z: zones.count(z) for z in set(zones)},
        'element_distribution': {e: elements.count(e) for e in set(elements)},
        'polarity_distribution': {p: polarities.count(p) for p in set(polarities)},
        'total_entries': len(scale_entries),
        'spans_octaves': math.log2(max(frequencies) / min(frequencies)) if frequencies else 0,
        'recommended_velocity_curve': PerformanceAnalyzer.calculate_optimal_velocity_curve(frequencies)
    }