"""
Petersen 大师级演奏渲染器

专为Petersen定制钢琴设计的高级演奏渲染系统，整合演奏技法与高质量音源。
支持实时试听和高质量WAV渲染两种模式，提供从基础到超人级的演奏技法。

主要功能：
- 实时预览模式：小范围旋律的即时试听（<100ms延迟）
- 高质量渲染模式：大范围作品的WAV/FLAC输出
- 智能技法应用：根据内容和模式自动选择演奏技法
- 专业音源管理：优化的Steinway等钢琴音色支持
- 表现力控制：动态、节奏、踏板等专业表现力

使用示例：
```python
# 实时试听
renderer = PetersenVirtuosoRenderer(mode="real_time")
renderer.quick_preview(scale_pattern, techniques=["thirds_parallel"])

# 高质量渲染
renderer = PetersenVirtuosoRenderer(mode="high_quality")
wav_path = renderer.render_composition(
    composition, 
    "virtuoso_performance.wav",
    techniques="adaptive",
    quality_level="studio"
)

# 交互式探索
explorer = renderer.create_interactive_explorer()
explorer.play_single_note(note_entry, technique="octave_doubling")
```
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Any, Callable
from collections import defaultdict
import math
import time
import threading
import queue
from datetime import datetime
from enum import Enum

# 音频处理
try:
    import soundfile as sf
    import numpy as np
    from scipy import signal
    HAS_AUDIO_LIBS = True
except ImportError:
    HAS_AUDIO_LIBS = False

# 导入Petersen系统模块
try:
    from .petersen_scale import PetersenScale, ScaleEntry
    from .petersen_composer import MultiTrackComposition
    from .petersen_performance import (
        PetersenPerformanceRenderer, PerformanceComposition, 
        PerformanceNote, PerformanceLevel, PERFORMANCE_TECHNIQUES
    )
    from .petersen_player import PetersenPlayer
    from .soundfont_manager import SoundFontManager, SoundFontInfo
    from .frequency_accurate import FrequencyAccuratePlayback
    from .expression_control import ExpressionController, ExpressionParameters
    from .audio_effects import AdvancedAudioEffects, EffectSettings
except ImportError:
    from petersen_scale import PetersenScale, ScaleEntry
    from petersen_composer import MultiTrackComposition
    from petersen_performance import (
        PetersenPerformanceRenderer, PerformanceComposition,
        PerformanceNote, PerformanceLevel, PERFORMANCE_TECHNIQUES
    )
    from petersen_player import PetersenPlayer
    from soundfont_manager import SoundFontManager, SoundFontInfo
    from frequency_accurate import FrequencyAccuratePlayback
    from expression_control import ExpressionController, ExpressionParameters
    from audio_effects import AdvancedAudioEffects, EffectSettings

class RenderMode(Enum):
    """渲染模式"""
    REAL_TIME = "real_time"           # 实时预览模式
    HIGH_QUALITY = "high_quality"     # 高质量渲染模式
    INTERACTIVE = "interactive"       # 交互式探索模式

class QualityLevel(Enum):
    """质量级别"""
    DRAFT = "draft"                   # 草稿质量（快速预览）
    STANDARD = "standard"             # 标准质量
    HIGH = "high"                     # 高质量
    STUDIO = "studio"                 # 录音室质量

@dataclass
class RenderSettings:
    """渲染设置"""
    mode: RenderMode                  # 渲染模式
    quality_level: QualityLevel       # 质量级别
    sample_rate: int = 44100          # 采样率
    bit_depth: int = 16               # 位深度
    buffer_size: int = 512            # 缓冲区大小
    max_polyphony: int = 64           # 最大复音数
    latency_target_ms: float = 50.0   # 目标延迟（毫秒）
    
    # 技法限制
    max_parallel_voices: int = 3      # 最大并行声部
    enable_superhuman_techniques: bool = False  # 是否启用超人技法
    technique_density: str = "moderate"  # 技法密度
    
    # 音效设置
    enable_reverb: bool = True        # 启用混响
    enable_expression: bool = True    # 启用表现力控制
    enable_effects: bool = True       # 启用音效处理

@dataclass
class PianoConfiguration:
    """钢琴配置"""
    soundfont_path: Optional[Path] = None     # SoundFont路径
    piano_program: int = 0                    # 钢琴音色程序号
    velocity_curve: str = "natural"          # 力度曲线
    pedal_model: str = "steinway"            # 踏板模型
    room_acoustics: str = "concert_hall"     # 房间声学
    microphone_position: str = "balanced"   # 麦克风位置

# 预设钢琴配置
PIANO_PRESETS = {
    "steinway_concert": PianoConfiguration(
        soundfont_path=None,  # 将自动搜索
        piano_program=0,
        velocity_curve="concert",
        pedal_model="steinway",
        room_acoustics="concert_hall",
        microphone_position="balanced"
    ),
    
    "steinway_intimate": PianoConfiguration(
        soundfont_path=None,
        piano_program=0,
        velocity_curve="intimate",
        pedal_model="steinway",
        room_acoustics="recital_hall",
        microphone_position="close"
    ),
    
    "steinway_studio": PianoConfiguration(
        soundfont_path=None,
        piano_program=0,
        velocity_curve="natural",
        pedal_model="steinway",
        room_acoustics="studio",
        microphone_position="studio_mix"
    )
}

# 质量级别对应的渲染设置
QUALITY_PRESETS = {
    QualityLevel.DRAFT: RenderSettings(
        mode=RenderMode.REAL_TIME,
        quality_level=QualityLevel.DRAFT,
        sample_rate=22050,
        bit_depth=16,
        buffer_size=1024,
        max_polyphony=32,
        latency_target_ms=100.0,
        max_parallel_voices=2,
        enable_superhuman_techniques=False,
        technique_density="sparse",
        enable_reverb=False,
        enable_expression=False,
        enable_effects=False
    ),
    
    QualityLevel.STANDARD: RenderSettings(
        mode=RenderMode.REAL_TIME,
        quality_level=QualityLevel.STANDARD,
        sample_rate=44100,
        bit_depth=16,
        buffer_size=512,
        max_polyphony=64,
        latency_target_ms=50.0,
        max_parallel_voices=3,
        enable_superhuman_techniques=False,
        technique_density="moderate",
        enable_reverb=True,
        enable_expression=True,
        enable_effects=True
    ),
    
    QualityLevel.HIGH: RenderSettings(
        mode=RenderMode.HIGH_QUALITY,
        quality_level=QualityLevel.HIGH,
        sample_rate=48000,
        bit_depth=24,
        buffer_size=256,
        max_polyphony=128,
        latency_target_ms=20.0,
        max_parallel_voices=5,
        enable_superhuman_techniques=True,
        technique_density="rich",
        enable_reverb=True,
        enable_expression=True,
        enable_effects=True
    ),
    
    QualityLevel.STUDIO: RenderSettings(
        mode=RenderMode.HIGH_QUALITY,
        quality_level=QualityLevel.STUDIO,
        sample_rate=96000,
        bit_depth=32,
        buffer_size=128,
        max_polyphony=256,
        latency_target_ms=10.0,
        max_parallel_voices=8,
        enable_superhuman_techniques=True,
        technique_density="extreme",
        enable_reverb=True,
        enable_expression=True,
        enable_effects=True
    )
}

@dataclass
class RenderProgress:
    """渲染进度信息"""
    current_measure: int = 0          # 当前小节
    total_measures: int = 0           # 总小节数
    current_second: float = 0.0       # 当前时间（秒）
    total_seconds: float = 0.0        # 总时长（秒）
    completion_ratio: float = 0.0     # 完成比例
    estimated_time_remaining: float = 0.0  # 预计剩余时间
    current_technique: str = ""       # 当前处理的技法
    quality_metrics: Dict[str, float] = field(default_factory=dict)

class PetersenVirtuosoRenderer:
    """Petersen大师级演奏渲染器"""
    
    def __init__(self,
                 mode: Union[str, RenderMode] = RenderMode.STANDARD,
                 quality: Union[str, QualityLevel] = QualityLevel.STANDARD,
                 piano_preset: str = "steinway_concert",
                 custom_soundfont: Optional[Path] = None):
        """
        初始化大师级演奏渲染器
        
        Args:
            mode: 渲染模式
            quality: 质量级别
            piano_preset: 钢琴预设
            custom_soundfont: 自定义SoundFont路径
        """
        # 处理枚举参数
        if isinstance(mode, str):
            self.render_mode = RenderMode(mode)
        else:
            self.render_mode = mode
            
        if isinstance(quality, str):
            self.quality_level = QualityLevel(quality)
        else:
            self.quality_level = quality
        
        # 获取渲染设置
        self.render_settings = QUALITY_PRESETS[self.quality_level].copy()
        self.render_settings.mode = self.render_mode
        
        # 配置钢琴
        self.piano_config = PIANO_PRESETS.get(piano_preset, PIANO_PRESETS["steinway_concert"])
        if custom_soundfont:
            self.piano_config.soundfont_path = Path(custom_soundfont)
        
        # 初始化子系统
        self._init_subsystems()
        
        # 状态变量
        self.is_initialized = False
        self.current_performance = None
        self.render_thread = None
        self.progress_callback = None
        
        print(f"Petersen大师级渲染器初始化完成")
        print(f"模式: {self.render_mode.value}, 质量: {self.quality_level.value}")
        print(f"钢琴预设: {piano_preset}")
    
    def _init_subsystems(self):
        """初始化子系统"""
        try:
            # SoundFont管理器
            self.soundfont_manager = SoundFontManager()
            
            # 性能渲染器
            self.performance_renderer = PetersenPerformanceRenderer(
                performance_level=PerformanceLevel.SUPERHUMAN if self.render_settings.enable_superhuman_techniques else PerformanceLevel.ADVANCED,
                technique_density=self.render_settings.technique_density,
                expression_style="natural"
            )
            
            # 音频子系统（如果在实时模式下）
            if self.render_mode == RenderMode.REAL_TIME:
                self._init_realtime_audio()
            
            print("子系统初始化完成")
            
        except Exception as e:
            print(f"子系统初始化失败: {e}")
            raise
    
    def _init_realtime_audio(self):
        """初始化实时音频系统"""
        try:
            # 查找最佳SoundFont
            best_soundfont = self._find_best_piano_soundfont()
            
            if best_soundfont:
                # 初始化实时播放器
                self.frequency_player = FrequencyAccuratePlayback(
                    soundfont_path=str(best_soundfont.path),
                    sample_rate=self.render_settings.sample_rate,
                    buffer_size=self.render_settings.buffer_size
                )
                
                # 表现力控制器
                self.expression_controller = ExpressionController()
                
                # 音效处理器
                self.audio_effects = AdvancedAudioEffects()
                
                print(f"实时音频系统初始化完成，使用: {best_soundfont.name}")
            else:
                print("警告: 未找到合适的钢琴SoundFont，将使用系统默认")
                self.frequency_player = None
                
        except Exception as e:
            print(f"实时音频系统初始化失败: {e}")
            self.frequency_player = None
    
    def _find_best_piano_soundfont(self) -> Optional[SoundFontInfo]:
        """查找最佳钢琴SoundFont"""
        # 优先级列表
        preferred_names = [
            "GD_Steinway_Model_D274",
            "GD_Steinway_Model_D274II", 
            "Steinway",
            "Piano"
        ]
        
        # 如果指定了自定义SoundFont
        if self.piano_config.soundfont_path and self.piano_config.soundfont_path.exists():
            soundfont_info = self.soundfont_manager.analyze_soundfont(self.piano_config.soundfont_path)
            if soundfont_info and soundfont_info.has_piano:
                return soundfont_info
        
        # 搜索系统中的SoundFont
        available_soundfonts = self.soundfont_manager.scan_system_soundfonts()
        
        # 按优先级查找
        for preferred_name in preferred_names:
            for sf_info in available_soundfonts:
                if preferred_name.lower() in sf_info.name.lower() and sf_info.has_piano:
                    return sf_info
        
        # 返回第一个包含钢琴的SoundFont
        for sf_info in available_soundfonts:
            if sf_info.has_piano:
                return sf_info
        
        return None
    
    def quick_preview(self,
                     scale_entries: List[ScaleEntry],
                     pattern: str = "ascending",
                     techniques: List[str] = None,
                     duration_per_note: float = 0.5) -> bool:
        """
        快速预览音阶模式
        
        Args:
            scale_entries: 音阶条目列表
            pattern: 演奏模式 ("ascending", "descending", "arpeggio")
            techniques: 演奏技法列表
            duration_per_note: 每个音符持续时间
            
        Returns:
            是否成功播放
        """
        if self.render_mode != RenderMode.REAL_TIME:
            print("快速预览需要实时模式")
            return False
        
        if not self.frequency_player:
            print("实时播放器未初始化")
            return False
        
        print(f"开始快速预览: {pattern}模式, {len(scale_entries)}个音符")
        
        # 准备播放序列
        play_sequence = self._prepare_preview_sequence(scale_entries, pattern)
        
        # 应用技法
        if techniques:
            enhanced_sequence = self._apply_preview_techniques(play_sequence, techniques)
        else:
            enhanced_sequence = play_sequence
        
        # 实时播放
        try:
            for i, (entry, technique_info) in enumerate(enhanced_sequence):
                # 播放主音符
                self.frequency_player.play_frequency(
                    frequency=entry.frequency,
                    duration=duration_per_note,
                    velocity=80
                )
                
                # 播放并行音符（如果有）
                if technique_info.get("parallel_frequencies"):
                    for parallel_freq, velocity_factor in technique_info["parallel_frequencies"]:
                        self.frequency_player.play_frequency(
                            frequency=parallel_freq,
                            duration=duration_per_note * 0.8,
                            velocity=int(80 * velocity_factor)
                        )
                
                # 短暂间隔
                time.sleep(duration_per_note * 0.1)
            
            print("快速预览完成")
            return True
            
        except Exception as e:
            print(f"快速预览失败: {e}")
            return False
    
    def _prepare_preview_sequence(self, scale_entries: List[ScaleEntry], pattern: str) -> List[Tuple[ScaleEntry, Dict]]:
        """准备预览序列"""
        sequence = []
        
        if pattern == "ascending":
            for entry in scale_entries:
                sequence.append((entry, {}))
                
        elif pattern == "descending":
            for entry in reversed(scale_entries):
                sequence.append((entry, {}))
                
        elif pattern == "arpeggio":
            # 琶音模式：1-3-5-8-5-3-1
            if len(scale_entries) >= 8:
                arpeggio_indices = [0, 2, 4, 7, 4, 2, 0]
                for idx in arpeggio_indices:
                    if idx < len(scale_entries):
                        sequence.append((scale_entries[idx], {}))
        
        return sequence
    
    def _apply_preview_techniques(self, 
                                sequence: List[Tuple[ScaleEntry, Dict]], 
                                techniques: List[str]) -> List[Tuple[ScaleEntry, Dict]]:
        """为预览序列应用技法"""
        enhanced_sequence = []
        
        for entry, base_info in sequence:
            technique_info = base_info.copy()
            
            # 应用选择的技法
            for tech_name in techniques:
                if tech_name in PERFORMANCE_TECHNIQUES:
                    tech_config = PERFORMANCE_TECHNIQUES[tech_name]
                    
                    if tech_config["type"].value == "parallel":
                        # 添加并行频率
                        parallel_freqs = []
                        intervals = tech_config.get("parallel_intervals", [])
                        velocity_factors = tech_config.get("velocity_factors", [1.0] * len(intervals))
                        
                        for interval, vel_factor in zip(intervals[:self.render_settings.max_parallel_voices], velocity_factors):
                            parallel_freq = entry.frequency * interval
                            parallel_freqs.append((parallel_freq, vel_factor))
                        
                        technique_info["parallel_frequencies"] = parallel_freqs
                        technique_info["applied_techniques"] = technique_info.get("applied_techniques", []) + [tech_name]
            
            enhanced_sequence.append((entry, technique_info))
        
        return enhanced_sequence
    
    def render_composition(self,
                          composition: Union[MultiTrackComposition, PerformanceComposition],
                          output_path: Union[str, Path],
                          techniques: Union[str, List[str]] = "adaptive",
                          progress_callback: Optional[Callable[[RenderProgress], None]] = None) -> Optional[Path]:
        """
        渲染完整作曲到WAV文件
        
        Args:
            composition: 作曲对象
            output_path: 输出路径
            techniques: 技法选择 ("adaptive", "none", 或技法列表)
            progress_callback: 进度回调函数
            
        Returns:
            成功时返回输出文件路径
        """
        if not HAS_AUDIO_LIBS:
            print("缺少音频处理库，无法进行高质量渲染")
            return None
        
        output_path = Path(output_path)
        self.progress_callback = progress_callback
        
        print(f"开始渲染作曲到: {output_path}")
        print(f"质量级别: {self.quality_level.value}")
        
        try:
            # 准备性能作曲
            if isinstance(composition, MultiTrackComposition):
                print("应用演奏技法...")
                performance_composition = self._prepare_performance_composition(composition, techniques)
            else:
                performance_composition = composition
            
            # 创建渲染进度
            progress = RenderProgress(
                total_measures=performance_composition.original_composition.total_measures,
                total_seconds=performance_composition.original_composition.get_total_duration_seconds()
            )
            
            # 开始渲染
            audio_data = self._render_to_audio(performance_composition, progress)
            
            if audio_data is not None:
                # 保存到文件
                self._save_audio_file(audio_data, output_path)
                
                print(f"渲染完成: {output_path}")
                return output_path
            else:
                print("渲染失败")
                return None
                
        except Exception as e:
            print(f"渲染过程出错: {e}")
            return None
    
    def _prepare_performance_composition(self, 
                                       composition: MultiTrackComposition,
                                       techniques: Union[str, List[str]]) -> PerformanceComposition:
        """准备性能作曲"""
        if techniques == "adaptive":
            # 自适应技法选择
            selected_techniques = None  # 让性能渲染器自动选择
        elif techniques == "none":
            selected_techniques = []
        elif isinstance(techniques, list):
            selected_techniques = techniques
        else:
            selected_techniques = None
        
        # 应用性能渲染
        performance_composition = self.performance_renderer.render_full_performance(
            composition,
            techniques=selected_techniques,
            auto_select_techniques=(selected_techniques is None)
        )
        
        return performance_composition
    
    def _render_to_audio(self, 
                        performance_composition: PerformanceComposition,
                        progress: RenderProgress) -> Optional[np.ndarray]:
        """渲染到音频数据"""
        try:
            # 获取最佳SoundFont
            best_soundfont = self._find_best_piano_soundfont()
            if not best_soundfont:
                print("无法找到合适的钢琴SoundFont")
                return None
            
            # 创建高质量播放器
            high_quality_player = FrequencyAccuratePlayback(
                soundfont_path=str(best_soundfont.path),
                sample_rate=self.render_settings.sample_rate,
                buffer_size=self.render_settings.buffer_size
            )
            
            # 获取所有演奏事件
            all_events = performance_composition.get_all_performance_events()
            total_duration = performance_composition.original_composition.get_total_duration_seconds()
            
            # 分配音频缓冲区
            total_samples = int(total_duration * self.render_settings.sample_rate) + self.render_settings.sample_rate
            audio_buffer = np.zeros((total_samples, 2), dtype=np.float32)  # 立体声
            
            print(f"开始渲染 {len(all_events)} 个演奏事件...")
            
            # 逐事件渲染
            for event_idx, (time, track_type, perf_note) in enumerate(all_events):
                
                # 更新进度
                progress.current_second = time
                progress.completion_ratio = event_idx / len(all_events)
                progress.current_technique = getattr(perf_note, 'articulation', 'normal')
                
                if self.progress_callback:
                    self.progress_callback(progress)
                
                # 渲染主音符
                self._render_performance_note(perf_note, time, audio_buffer, high_quality_player)
            
            # 应用后处理效果
            if self.render_settings.enable_effects:
                audio_buffer = self._apply_post_processing(audio_buffer)
            
            print("音频渲染完成")
            return audio_buffer
            
        except Exception as e:
            print(f"音频渲染失败: {e}")
            return None
    
    def _render_performance_note(self,
                               perf_note: PerformanceNote,
                               start_time: float,
                               audio_buffer: np.ndarray,
                               player: FrequencyAccuratePlayback):
        """渲染单个演奏音符"""
        sample_rate = self.render_settings.sample_rate
        start_sample = int(start_time * sample_rate)
        
        # 获取所有频率（主音符 + 并行声部）
        all_frequencies = perf_note.get_all_frequencies()
        
        for freq, time_offset, velocity in all_frequencies:
            note_start_sample = start_sample + int(time_offset * sample_rate)
            
            if note_start_sample < len(audio_buffer):
                # 生成音符音频
                note_audio = self._generate_note_audio(
                    frequency=freq,
                    duration=perf_note.get_total_duration(),
                    velocity=velocity,
                    sample_rate=sample_rate
                )
                
                # 混合到主缓冲区
                end_sample = min(note_start_sample + len(note_audio), len(audio_buffer))
                mix_length = end_sample - note_start_sample
                
                if mix_length > 0:
                    # 简单的线性混合
                    audio_buffer[note_start_sample:end_sample] += note_audio[:mix_length].reshape(-1, 1)
        
        # 渲染装饰音
        for ornament in perf_note.ornaments:
            ornament_start_sample = start_sample + int(ornament.timing_offset * sample_rate)
            
            if ornament_start_sample < len(audio_buffer):
                ornament_audio = self._generate_note_audio(
                    frequency=ornament.frequency,
                    duration=ornament.duration,
                    velocity=ornament.velocity,
                    sample_rate=sample_rate
                )
                
                end_sample = min(ornament_start_sample + len(ornament_audio), len(audio_buffer))
                mix_length = end_sample - ornament_start_sample
                
                if mix_length > 0:
                    audio_buffer[ornament_start_sample:end_sample] += ornament_audio[:mix_length].reshape(-1, 1)
    
    def _generate_note_audio(self,
                           frequency: float,
                           duration: float,
                           velocity: int,
                           sample_rate: int) -> np.ndarray:
        """生成音符音频数据"""
        # 这里应该使用真正的SoundFont合成
        # 现在使用简化的正弦波生成作为占位符
        
        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples)
        
        # 基础正弦波
        audio = np.sin(2 * np.pi * frequency * t)
        
        # 添加谐波（模拟钢琴音色）
        audio += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)  # 二次谐波
        audio += 0.1 * np.sin(2 * np.pi * frequency * 3 * t)  # 三次谐波
        
        # 应用ADSR包络
        attack_time = 0.05
        decay_time = 0.1
        sustain_level = 0.7
        release_time = duration * 0.3
        
        envelope = self._generate_adsr_envelope(num_samples, attack_time, decay_time, sustain_level, release_time, sample_rate)
        audio *= envelope
        
        # 应用力度
        velocity_factor = velocity / 127.0
        audio *= velocity_factor
        
        # 防止削波
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0.8:
            audio *= 0.8 / max_amplitude
        
        return audio.astype(np.float32)
    
    def _generate_adsr_envelope(self,
                              num_samples: int,
                              attack_time: float,
                              decay_time: float,
                              sustain_level: float,
                              release_time: float,
                              sample_rate: int) -> np.ndarray:
        """生成ADSR包络"""
        envelope = np.zeros(num_samples)
        
        attack_samples = int(attack_time * sample_rate)
        decay_samples = int(decay_time * sample_rate)
        release_samples = int(release_time * sample_rate)
        
        current_sample = 0
        
        # Attack
        if current_sample < num_samples and attack_samples > 0:
            end_sample = min(current_sample + attack_samples, num_samples)
            envelope[current_sample:end_sample] = np.linspace(0, 1, end_sample - current_sample)
            current_sample = end_sample
        
        # Decay
        if current_sample < num_samples and decay_samples > 0:
            end_sample = min(current_sample + decay_samples, num_samples)
            envelope[current_sample:end_sample] = np.linspace(1, sustain_level, end_sample - current_sample)
            current_sample = end_sample
        
        # Sustain
        sustain_samples = num_samples - current_sample - release_samples
        if sustain_samples > 0:
            end_sample = current_sample + sustain_samples
            envelope[current_sample:end_sample] = sustain_level
            current_sample = end_sample
        
        # Release
        if current_sample < num_samples:
            envelope[current_sample:] = np.linspace(sustain_level, 0, num_samples - current_sample)
        
        return envelope
    
    def _apply_post_processing(self, audio_buffer: np.ndarray) -> np.ndarray:
        """应用后处理效果"""
        processed = audio_buffer.copy()
        
        if self.render_settings.enable_reverb:
            # 简化的混响效果
            processed = self._apply_simple_reverb(processed)
        
        # 动态范围压缩
        processed = self._apply_compression(processed)
        
        # 最终限制器
        processed = self._apply_limiter(processed)
        
        return processed
    
    def _apply_simple_reverb(self, audio: np.ndarray) -> np.ndarray:
        """应用简单混响"""
        # 使用延迟和反馈的简化混响
        delay_samples = int(0.03 * self.render_settings.sample_rate)  # 30ms延迟
        feedback = 0.3
        mix = 0.2
        
        if len(audio.shape) == 1:
            audio = audio.reshape(-1, 1)
        
        reverb_audio = audio.copy()
        
        for channel in range(audio.shape[1]):
            delayed = np.zeros_like(audio[:, channel])
            
            for i in range(delay_samples, len(audio)):
                delayed[i] = audio[i - delay_samples, channel] + feedback * delayed[i - delay_samples]
            
            reverb_audio[:, channel] = audio[:, channel] + mix * delayed
        
        return reverb_audio
    
    def _apply_compression(self, audio: np.ndarray, threshold: float = 0.7, ratio: float = 4.0) -> np.ndarray:
        """应用动态范围压缩"""
        compressed = audio.copy()
        
        # 简化的压缩器
        above_threshold = np.abs(compressed) > threshold
        compressed[above_threshold] = np.sign(compressed[above_threshold]) * (
            threshold + (np.abs(compressed[above_threshold]) - threshold) / ratio
        )
        
        return compressed
    
    def _apply_limiter(self, audio: np.ndarray, ceiling: float = 0.95) -> np.ndarray:
        """应用限制器防止削波"""
        limited = audio.copy()
        
        max_amplitude = np.max(np.abs(limited))
        if max_amplitude > ceiling:
            limited *= ceiling / max_amplitude
        
        return limited
    
    def _save_audio_file(self, audio_data: np.ndarray, output_path: Path):
        """保存音频文件"""
        try:
            # 确保音频数据是正确的格式
            if len(audio_data.shape) == 1:
                audio_data = audio_data.reshape(-1, 1)
            
            # 转换位深度
            if self.render_settings.bit_depth == 16:
                audio_data = (audio_data * 32767).astype(np.int16)
            elif self.render_settings.bit_depth == 24:
                audio_data = (audio_data * 8388607).astype(np.int32)
            elif self.render_settings.bit_depth == 32:
                audio_data = audio_data.astype(np.float32)
            
            # 保存文件
            sf.write(
                file=str(output_path),
                data=audio_data,
                samplerate=self.render_settings.sample_rate,
                subtype=f"PCM_{self.render_settings.bit_depth}"
            )
            
            print(f"音频文件已保存: {output_path}")
            print(f"格式: {self.render_settings.sample_rate}Hz, {self.render_settings.bit_depth}bit")
            
        except Exception as e:
            print(f"保存音频文件失败: {e}")
            raise
    
    def create_interactive_explorer(self) -> 'InteractiveExplorer':
        """创建交互式探索器"""
        return InteractiveExplorer(self)
    
    def get_available_techniques(self) -> List[str]:
        """获取可用的演奏技法"""
        available = []
        
        for name, technique in PERFORMANCE_TECHNIQUES.items():
            if self._is_technique_available(technique):
                available.append(name)
        
        return available
    
    def _is_technique_available(self, technique: Dict) -> bool:
        """检查技法是否可用"""
        technique_level = technique["level"]
        
        if technique_level == PerformanceLevel.SUPERHUMAN:
            return self.render_settings.enable_superhuman_techniques
        
        return True
    
    def get_render_statistics(self) -> Dict[str, Any]:
        """获取渲染统计信息"""
        stats = {
            "renderer_info": {
                "mode": self.render_mode.value,
                "quality_level": self.quality_level.value,
                "sample_rate": self.render_settings.sample_rate,
                "bit_depth": self.render_settings.bit_depth,
                "max_polyphony": self.render_settings.max_polyphony
            },
            
            "piano_config": {
                "soundfont": str(self.piano_config.soundfont_path) if self.piano_config.soundfont_path else "auto",
                "velocity_curve": self.piano_config.velocity_curve,
                "pedal_model": self.piano_config.pedal_model,
                "room_acoustics": self.piano_config.room_acoustics
            },
            
            "technique_settings": {
                "max_parallel_voices": self.render_settings.max_parallel_voices,
                "superhuman_enabled": self.render_settings.enable_superhuman_techniques,
                "technique_density": self.render_settings.technique_density,
                "available_techniques": len(self.get_available_techniques())
            },
            
            "performance_metrics": {
                "target_latency_ms": self.render_settings.latency_target_ms,
                "effects_enabled": self.render_settings.enable_effects,
                "expression_enabled": self.render_settings.enable_expression
            }
        }
        
        return stats

class InteractiveExplorer:
    """交互式音阶探索器"""
    
    def __init__(self, renderer: PetersenVirtuosoRenderer):
        """
        初始化交互式探索器
        
        Args:
            renderer: 父渲染器
        """
        self.renderer = renderer
        self.current_scale = None
        self.playing_notes = set()
        
        if renderer.render_mode != RenderMode.REAL_TIME:
            print("警告: 交互式探索器建议使用实时模式")
    
    def play_single_note(self,
                        scale_entry: ScaleEntry,
                        technique: str = "none",
                        duration: float = 2.0,
                        velocity: int = 80) -> bool:
        """
        播放单个音符
        
        Args:
            scale_entry: 音阶条目
            technique: 演奏技法
            duration: 持续时间
            velocity: 力度
            
        Returns:
            是否成功播放
        """
        if not self.renderer.frequency_player:
            print("实时播放器不可用")
            return False
        
        try:
            print(f"播放音符: {scale_entry.key_short} ({scale_entry.frequency:.2f}Hz)")
            
            # 播放主音符
            self.renderer.frequency_player.play_frequency(
                frequency=scale_entry.frequency,
                duration=duration,
                velocity=velocity
            )
            
            # 应用技法
            if technique != "none" and technique in PERFORMANCE_TECHNIQUES:
                self._apply_technique_to_note(scale_entry, technique, duration, velocity)
            
            return True
            
        except Exception as e:
            print(f"播放失败: {e}")
            return False
    
    def _apply_technique_to_note(self,
                               scale_entry: ScaleEntry,
                               technique: str,
                               duration: float,
                               velocity: int):
        """为单个音符应用技法"""
        tech_config = PERFORMANCE_TECHNIQUES[technique]
        
        if tech_config["type"].value == "parallel":
            # 播放并行音符
            intervals = tech_config.get("parallel_intervals", [])
            velocity_factors = tech_config.get("velocity_factors", [1.0] * len(intervals))
            
            for interval, vel_factor in zip(intervals, velocity_factors):
                parallel_freq = scale_entry.frequency * interval
                parallel_velocity = int(velocity * vel_factor)
                
                self.renderer.frequency_player.play_frequency(
                    frequency=parallel_freq,
                    duration=duration * 0.9,
                    velocity=parallel_velocity
                )
    
    def play_chord(self,
                  scale_entries: List[ScaleEntry],
                  duration: float = 3.0,
                  velocity: int = 80) -> bool:
        """
        播放和弦
        
        Args:
            scale_entries: 和弦音符列表
            duration: 持续时间
            velocity: 力度
            
        Returns:
            是否成功播放
        """
        if not self.renderer.frequency_player:
            return False
        
        try:
            print(f"播放和弦: {len(scale_entries)}个音符")
            
            for entry in scale_entries:
                self.renderer.frequency_player.play_frequency(
                    frequency=entry.frequency,
                    duration=duration,
                    velocity=velocity
                )
            
            return True
            
        except Exception as e:
            print(f"和弦播放失败: {e}")
            return False
    
    def demonstrate_technique(self,
                            scale_entry: ScaleEntry,
                            technique: str) -> bool:
        """
        演示特定技法
        
        Args:
            scale_entry: 基础音符
            technique: 技法名称
            
        Returns:
            是否成功演示
        """
        if technique not in PERFORMANCE_TECHNIQUES:
            print(f"未知技法: {technique}")
            return False
        
        tech_config = PERFORMANCE_TECHNIQUES[technique]
        
        print(f"演示技法: {tech_config['description']}")
        print(f"级别: {tech_config['level'].value}")
        
        # 先播放原始音符
        print("原始音符:")
        self.play_single_note(scale_entry, "none", 1.5)
        
        time.sleep(0.5)
        
        # 再播放应用技法的版本
        print(f"应用{technique}:")
        self.play_single_note(scale_entry, technique, 1.5)
        
        return True

def demo_virtuoso_renderer():
    """演示大师级渲染器"""
    from petersen_scale import PetersenScale
    from petersen_composer import PetersenAutoComposer
    from petersen_chord import PetersenChordExtender
    
    print("=== Petersen大师级演奏渲染器演示 ===\n")
    
    # 创建基础作曲
    print("1. 创建基础作曲...")
    base_scale = PetersenScale(F_base=55.0, phi=2.0)
    chord_extender = PetersenChordExtender(base_scale)
    composer = PetersenAutoComposer(
        petersen_scale=base_scale,
        chord_extender=chord_extender,
        composition_style="balanced_journey"
    )
    basic_composition = composer.compose(measures=4)
    
    # 实时预览模式
    print("\n2. 实时预览模式...")
    real_time_renderer = PetersenVirtuosoRenderer(
        mode=RenderMode.REAL_TIME,
        quality=QualityLevel.STANDARD,
        piano_preset="steinway_concert"
    )
    
    # 快速预览音阶
    scale_entries = base_scale.get_scale_entries()[:8]
    real_time_renderer.quick_preview(
        scale_entries,
        pattern="arpeggio",
        techniques=["thirds_parallel"],
        duration_per_note=0.3
    )
    
    # 交互式探索
    print("\n3. 交互式探索...")
    explorer = real_time_renderer.create_interactive_explorer()
    
    # 演示技法
    if scale_entries:
        explorer.demonstrate_technique(scale_entries[0], "octave_doubling")
    
    # 高质量渲染模式
    print("\n4. 高质量渲染模式...")
    studio_renderer = PetersenVirtuosoRenderer(
        mode=RenderMode.HIGH_QUALITY,
        quality=QualityLevel.STUDIO,
        piano_preset="steinway_studio"
    )
    
    # 渲染完整作品
    def progress_callback(progress: RenderProgress):
        print(f"渲染进度: {progress.completion_ratio:.1%} - {progress.current_technique}")
    
    output_path = studio_renderer.render_composition(
        basic_composition,
        "demo_virtuoso_performance.wav",
        techniques="adaptive",
        progress_callback=progress_callback
    )
    
    if output_path:
        print(f"\n完整作品已渲染到: {output_path}")
    
    # 显示统计信息
    print("\n5. 渲染器统计信息:")
    stats = studio_renderer.get_render_statistics()
    
    print(f"渲染模式: {stats['renderer_info']['mode']}")
    print(f"质量级别: {stats['renderer_info']['quality_level']}")
    print(f"采样率: {stats['renderer_info']['sample_rate']}Hz")
    print(f"最大并行声部: {stats['technique_settings']['max_parallel_voices']}")
    print(f"可用技法数量: {stats['technique_settings']['available_techniques']}")

if __name__ == "__main__":
    demo_virtuoso_renderer()