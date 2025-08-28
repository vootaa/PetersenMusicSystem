"""
表现力控制模块
提供动态力度曲线、节奏变化、踏板控制等音乐表现力功能
"""
import time
import math
from typing import List, Dict, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.analysis import PerformanceAnalyzer
from utils.constants import VELOCITY_CURVES, DYNAMIC_PATTERNS, CC_CONTROLLERS

class DynamicPattern(Enum):
    """动态模式枚举"""
    LINEAR = "linear"
    CRESCENDO = "crescendo"
    DIMINUENDO = "diminuendo"
    ARCH = "arch"
    WAVE = "wave"
    ACCENT = "accent"
    TERRACED = "terraced"

class TimingStyle(Enum):
    """节奏风格枚举"""
    MECHANICAL = "mechanical"
    RUBATO = "rubato"
    ACCELERANDO = "accelerando"
    RITARDANDO = "ritardando"
    SWING = "swing"
    STACCATO = "staccato"
    LEGATO = "legato"

@dataclass
class ExpressionParameters:
    """表现力参数"""
    dynamic_pattern: DynamicPattern = DynamicPattern.LINEAR
    timing_style: TimingStyle = TimingStyle.MECHANICAL
    velocity_base: int = 80
    velocity_range: Tuple[int, int] = (40, 120)
    duration_base: float = 0.5
    duration_variance: float = 0.1
    gap_base: float = 0.1
    gap_variance: float = 0.05
    
    # 踏板控制
    use_sustain_pedal: bool = False
    sustain_probability: float = 0.3
    use_soft_pedal: bool = False
    
    # 高级表现力
    phrase_shaping: bool = True
    accent_beats: List[int] = None
    microtiming_deviation: float = 0.02

class ExpressionController:
    """表现力控制器"""
    
    def __init__(self, fluidsynth_lib, synth, current_channel: int = 0):
        """
        初始化表现力控制器
        
        Args:
            fluidsynth_lib: FluidSynth动态库对象
            synth: FluidSynth合成器对象
            current_channel: 当前MIDI通道
        """
        self.fluidsynth = fluidsynth_lib
        self.synth = synth
        self.current_channel = current_channel
        
        # 当前表现力参数
        self.current_params = ExpressionParameters()
        
        # 踏板状态
        self.sustain_pressed = False
        self.soft_pressed = False
        
        # 表现力预设
        self.presets = self._create_expression_presets()
        
        print("✓ 表现力控制器已初始化")
    
    def _create_expression_presets(self) -> Dict[str, ExpressionParameters]:
        """创建表现力预设"""
        presets = {
            'mechanical': ExpressionParameters(
                dynamic_pattern=DynamicPattern.LINEAR,
                timing_style=TimingStyle.MECHANICAL,
                velocity_base=80,
                velocity_range=(75, 85),
                duration_variance=0.0,
                gap_variance=0.0
            ),
            
            'expressive': ExpressionParameters(
                dynamic_pattern=DynamicPattern.ARCH,
                timing_style=TimingStyle.RUBATO,
                velocity_base=75,
                velocity_range=(50, 110),
                duration_variance=0.15,
                gap_variance=0.08,
                phrase_shaping=True,
                microtiming_deviation=0.03
            ),
            
            'romantic': ExpressionParameters(
                dynamic_pattern=DynamicPattern.WAVE,
                timing_style=TimingStyle.RUBATO,
                velocity_base=70,
                velocity_range=(45, 115),
                duration_variance=0.2,
                gap_variance=0.1,
                use_sustain_pedal=True,
                sustain_probability=0.6,
                phrase_shaping=True,
                microtiming_deviation=0.05
            ),
            
            'classical': ExpressionParameters(
                dynamic_pattern=DynamicPattern.TERRACED,
                timing_style=TimingStyle.MECHANICAL,
                velocity_base=85,
                velocity_range=(60, 105),
                duration_variance=0.05,
                gap_variance=0.02,
                use_sustain_pedal=True,
                sustain_probability=0.2,
                phrase_shaping=True
            ),
            
            'jazz': ExpressionParameters(
                dynamic_pattern=DynamicPattern.ACCENT,
                timing_style=TimingStyle.SWING,
                velocity_base=90,
                velocity_range=(70, 120),
                duration_variance=0.3,
                gap_variance=0.15,
                accent_beats=[0, 2],  # 强拍重音
                microtiming_deviation=0.08
            ),
            
            'gentle': ExpressionParameters(
                dynamic_pattern=DynamicPattern.LINEAR,
                timing_style=TimingStyle.LEGATO,
                velocity_base=60,
                velocity_range=(45, 75),
                duration_variance=0.1,
                gap_variance=0.0,
                use_soft_pedal=True,
                phrase_shaping=True
            ),
            
            'dramatic': ExpressionParameters(
                dynamic_pattern=DynamicPattern.ARCH,
                timing_style=TimingStyle.RUBATO,
                velocity_base=95,
                velocity_range=(30, 127),
                duration_variance=0.25,
                gap_variance=0.12,
                use_sustain_pedal=True,
                sustain_probability=0.8,
                phrase_shaping=True,
                microtiming_deviation=0.06
            ),
            
            'study': ExpressionParameters(
                dynamic_pattern=DynamicPattern.CRESCENDO,
                timing_style=TimingStyle.ACCELERANDO,
                velocity_base=75,
                velocity_range=(60, 100),
                duration_variance=0.08,
                gap_variance=0.03,
                phrase_shaping=True
            )
        }
        
        return presets
    
    def apply_expression_preset(self, preset_name: str) -> bool:
        """
        应用表现力预设
        
        Args:
            preset_name: 预设名称
            
        Returns:
            应用成功返回True
        """
        if preset_name not in self.presets:
            print(f"❌ 未知预设: {preset_name}")
            print(f"可用预设: {list(self.presets.keys())}")
            return False
        
        self.current_params = self.presets[preset_name]
        print(f"✓ 表现力预设 '{preset_name}' 已应用")
        return True
    
    def calculate_expression_sequence(self, 
                                    note_count: int,
                                    frequencies: Optional[List[float]] = None,
                                    key_names: Optional[List[str]] = None) -> Dict[str, List]:
        """
        计算表现力序列
        
        Args:
            note_count: 音符数量
            frequencies: 频率列表(可选，用于频率相关的表现力调整)
            key_names: 音名列表(可选)
            
        Returns:
            包含力度、时值、间隔等的表现力数据
        """
        if note_count <= 0:
            return {}
        
        params = self.current_params
        
        # 计算力度序列
        velocities = self._calculate_velocity_sequence(note_count, frequencies)
        
        # 计算时值序列
        durations = self._calculate_duration_sequence(note_count)
        
        # 计算间隔序列
        gaps = self._calculate_gap_sequence(note_count)
        
        # 计算踏板序列
        sustain_events = self._calculate_sustain_sequence(note_count)
        soft_events = self._calculate_soft_pedal_sequence(note_count)
        
        # 计算微调时间
        microtimings = self._calculate_microtiming_sequence(note_count)
        
        return {
            'velocities': velocities,
            'durations': durations,
            'gaps': gaps,
            'sustain_events': sustain_events,
            'soft_events': soft_events,
            'microtimings': microtimings,
            'total_duration': sum(durations) + sum(gaps[:-1]) if gaps else sum(durations)
        }
    
    def _calculate_velocity_sequence(self, note_count: int, frequencies: Optional[List[float]] = None) -> List[int]:
        """计算力度序列"""
        params = self.current_params
        base_vel = params.velocity_base
        min_vel, max_vel = params.velocity_range
        
        velocities = []
        
        for i in range(note_count):
            # 基础动态模式
            dynamic_factor = self._get_dynamic_factor(i, note_count, params.dynamic_pattern)
            
            # 频率相关调整
            freq_factor = 1.0
            if frequencies and i < len(frequencies):
                freq_factor = self._get_frequency_velocity_factor(frequencies[i])
            
            # 重音处理
            accent_factor = 1.0
            if params.accent_beats and i % 4 in params.accent_beats:
                accent_factor = 1.2
            
            # 短语塑形
            phrase_factor = 1.0
            if params.phrase_shaping:
                phrase_factor = self._get_phrase_factor(i, note_count)
            
            # 计算最终力度
            velocity = base_vel * dynamic_factor * freq_factor * accent_factor * phrase_factor
            velocity = max(min_vel, min(max_vel, int(velocity)))
            
            velocities.append(velocity)
        
        return velocities
    
    def _calculate_duration_sequence(self, note_count: int) -> List[float]:
        """计算时值序列"""
        params = self.current_params
        base_duration = params.duration_base
        variance = params.duration_variance
        
        durations = []
        
        for i in range(note_count):
            # 时值风格调整
            style_factor = self._get_timing_style_factor(i, note_count, params.timing_style)
            
            # 随机变化
            random_factor = 1.0
            if variance > 0:
                import random
                random_factor = 1.0 + random.uniform(-variance, variance)
            
            duration = base_duration * style_factor * random_factor
            duration = max(0.1, duration)  # 最小时值
            
            durations.append(duration)
        
        return durations
    
    def _calculate_gap_sequence(self, note_count: int) -> List[float]:
        """计算间隔序列"""
        params = self.current_params
        base_gap = params.gap_base
        variance = params.gap_variance
        
        gaps = []
        
        for i in range(note_count):
            # legato风格几乎没有间隔
            if params.timing_style == TimingStyle.LEGATO:
                gap = base_gap * 0.1
            # staccato风格间隔较大
            elif params.timing_style == TimingStyle.STACCATO:
                gap = base_gap * 2.0
            else:
                gap = base_gap
            
            # 随机变化
            if variance > 0:
                import random
                gap += random.uniform(-variance, variance)
            
            gap = max(0.0, gap)
            gaps.append(gap)
        
        return gaps
    
    def _calculate_sustain_sequence(self, note_count: int) -> List[bool]:
        """计算延音踏板序列"""
        params = self.current_params
        
        if not params.use_sustain_pedal:
            return [False] * note_count
        
        sustain_events = []
        
        for i in range(note_count):
            use_sustain = False
            
            # 基于概率决定是否使用踏板
            import random
            if random.random() < params.sustain_probability:
                use_sustain = True
            
            # 在短语开始和结束处更可能使用踏板
            if params.phrase_shaping:
                phrase_position = (i % 8) / 8.0  # 假设8音符为一个短语
                if phrase_position < 0.2 or phrase_position > 0.8:
                    use_sustain = True
            
            sustain_events.append(use_sustain)
        
        return sustain_events
    
    def _calculate_soft_pedal_sequence(self, note_count: int) -> List[bool]:
        """计算弱音踏板序列"""
        params = self.current_params
        
        if not params.use_soft_pedal:
            return [False] * note_count
        
        # 弱音踏板通常在整个段落中保持一致
        return [True] * note_count
    
    def _calculate_microtiming_sequence(self, note_count: int) -> List[float]:
        """计算微调时间序列"""
        params = self.current_params
        deviation = params.microtiming_deviation
        
        if deviation <= 0:
            return [0.0] * note_count
        
        microtimings = []
        
        for i in range(note_count):
            import random
            # 微调时间，通常是很小的提前或延后
            microtiming = random.uniform(-deviation, deviation)
            microtimings.append(microtiming)
        
        return microtimings
    
    def _get_dynamic_factor(self, index: int, total: int, pattern: DynamicPattern) -> float:
        """获取动态模式因子"""
        if total <= 1:
            return 1.0
        
        position = index / (total - 1)
        
        if pattern == DynamicPattern.CRESCENDO:
            return 0.7 + 0.6 * position
        elif pattern == DynamicPattern.DIMINUENDO:
            return 1.3 - 0.6 * position
        elif pattern == DynamicPattern.ARCH:
            return 0.7 + 0.6 * (1 - abs(2 * position - 1))
        elif pattern == DynamicPattern.WAVE:
            return 0.8 + 0.4 * math.sin(position * math.pi * 2)
        elif pattern == DynamicPattern.ACCENT:
            return 1.2 if index % 4 == 0 else 0.9
        elif pattern == DynamicPattern.TERRACED:
            return 1.1 if (index // 4) % 2 == 0 else 0.9
        else:  # LINEAR
            return 1.0
    
    def _get_frequency_velocity_factor(self, frequency: float) -> float:
        """根据频率调整力度因子"""
        if frequency < 100:
            return 1.1  # 低频增强
        elif frequency > 2000:
            return 0.9  # 高频稍弱
        else:
            return 1.0
    
    def _get_phrase_factor(self, index: int, total: int) -> float:
        """获取短语塑形因子"""
        phrase_length = 8  # 假设短语长度
        phrase_position = (index % phrase_length) / phrase_length
        
        # 短语中间稍强，开始和结束稍弱
        return 0.9 + 0.2 * math.sin(phrase_position * math.pi)
    
    def _get_timing_style_factor(self, index: int, total: int, style: TimingStyle) -> float:
        """获取时值风格因子"""
        if total <= 1:
            return 1.0
        
        position = index / (total - 1)
        
        if style == TimingStyle.ACCELERANDO:
            return 1.3 - 0.6 * position  # 逐渐加快（时值减少）
        elif style == TimingStyle.RITARDANDO:
            return 0.7 + 0.6 * position  # 逐渐放慢（时值增加）
        elif style == TimingStyle.RUBATO:
            return 0.9 + 0.2 * math.sin(position * math.pi * 4)  # 灵活变化
        elif style == TimingStyle.SWING:
            return 1.2 if index % 2 == 0 else 0.8  # 摇摆节奏
        elif style == TimingStyle.STACCATO:
            return 0.5  # 短促
        elif style == TimingStyle.LEGATO:
            return 1.2  # 连贯
        else:  # MECHANICAL
            return 1.0
    
    def apply_pedal_control(self, sustain_event: bool, soft_event: bool) -> None:
        """应用踏板控制"""
        # 延音踏板
        if sustain_event != self.sustain_pressed:
            self._set_sustain_pedal(sustain_event)
            self.sustain_pressed = sustain_event
        
        # 弱音踏板
        if soft_event != self.soft_pressed:
            self._set_soft_pedal(soft_event)
            self.soft_pressed = soft_event
    
    def _set_sustain_pedal(self, pressed: bool) -> bool:
        """设置延音踏板"""
        try:
            value = 127 if pressed else 0
            result = self.fluidsynth.fluid_synth_cc(
                self.synth, self.current_channel,
                CC_CONTROLLERS['sustain_pedal'], value
            )
            return result == 0
        except Exception:
            return False
    
    def _set_soft_pedal(self, pressed: bool) -> bool:
        """设置弱音踏板"""
        try:
            value = 127 if pressed else 0
            result = self.fluidsynth.fluid_synth_cc(
                self.synth, self.current_channel,
                CC_CONTROLLERS['soft_pedal'], value
            )
            return result == 0
        except Exception:
            return False
    
    def get_available_presets(self) -> List[str]:
        """获取可用预设列表"""
        return list(self.presets.keys())
    
    def get_current_parameters(self) -> ExpressionParameters:
        """获取当前表现力参数"""
        return self.current_params
    
    def create_custom_expression(self, name: str, **kwargs) -> ExpressionParameters:
        """创建自定义表现力设置"""
        # 从当前参数开始
        params = ExpressionParameters(
            dynamic_pattern=self.current_params.dynamic_pattern,
            timing_style=self.current_params.timing_style,
            velocity_base=self.current_params.velocity_base,
            velocity_range=self.current_params.velocity_range,
            duration_base=self.current_params.duration_base,
            duration_variance=self.current_params.duration_variance,
            gap_base=self.current_params.gap_base,
            gap_variance=self.current_params.gap_variance,
            use_sustain_pedal=self.current_params.use_sustain_pedal,
            sustain_probability=self.current_params.sustain_probability,
            use_soft_pedal=self.current_params.use_soft_pedal,
            phrase_shaping=self.current_params.phrase_shaping,
            accent_beats=self.current_params.accent_beats.copy() if self.current_params.accent_beats else None,
            microtiming_deviation=self.current_params.microtiming_deviation
        )
        
        # 应用自定义参数
        for key, value in kwargs.items():
            if hasattr(params, key):
                setattr(params, key, value)
            else:
                print(f"⚠️  未知参数: {key}")
        
        # 保存预设
        self.presets[name] = params
        print(f"✓ 自定义表现力预设 '{name}' 已创建")
        
        return params
    
    def reset_pedals(self) -> None:
        """重置所有踏板到默认状态"""
        try:
            if self.synth and self.fluidsynth:
                # 只重置当前通道的踏板
                self.fluidsynth.fluid_synth_cc(self.synth, self.current_channel, 64, 0)  # 延音踏板
                self.fluidsynth.fluid_synth_cc(self.synth, self.current_channel, 66, 0)  # 软踏板  
                self.fluidsynth.fluid_synth_cc(self.synth, self.current_channel, 67, 0)  # 弱音踏板
                
                print("✓ 踏板已重置")
        except:
            pass