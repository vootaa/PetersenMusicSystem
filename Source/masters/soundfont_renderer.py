"""
高质量SoundFont渲染器

负责将Petersen作曲转换为高质量WAV音频文件，这是整个系统最终输出的核心组件。
支持录音室级别的音频渲染，确保数学模型的音乐美学能够以最佳音质呈现。

主要功能：
- 精确频率SoundFont渲染
- 多种质量级别支持
- 批量音频生成
- 音效处理链集成
- 实时进度监控

技术特点：
- 使用FluidSynth进行专业音频合成
- 支持48kHz/24bit录音室质量
- 精确的Petersen频率补偿
- 完整的音效处理流水线
"""

import sys
import time
import wave
import array
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum

# 导入音频处理库
try:
    import fluidsynth
    import numpy as np
    FLUIDSYNTH_AVAILABLE = True
except ImportError:
    FLUIDSYNTH_AVAILABLE = False
    print("⚠️ FluidSynth不可用，将使用模拟渲染")

# 添加libs路径
current_dir = Path(__file__).parent
libs_dir = current_dir.parent / "libs"
if str(libs_dir) not in sys.path:
    sys.path.insert(0, str(libs_dir))

try:
    from frequency_accurate import FrequencyAccuratePlayback
    from audio_effects import AdvancedAudioEffects, EffectSettings
    from expression_control import ExpressionController, ExpressionParameters
    from utils.constants import DEFAULT_SOUNDFONTS
except ImportError as e:
    print(f"⚠️ 导入音频模块失败: {e}")

class RenderQuality(Enum):
    """渲染质量级别"""
    DRAFT = "draft"           # 22kHz, 16bit, 基础音效
    STANDARD = "standard"     # 44.1kHz, 16bit, 标准音效
    HIGH = "high"            # 44.1kHz, 24bit, 高级音效
    STUDIO = "studio"        # 48kHz, 24bit, 录音室音效

@dataclass
class RenderSettings:
    """渲染设置"""
    quality: RenderQuality = RenderQuality.STANDARD
    sample_rate: int = 44100
    bit_depth: int = 16
    buffer_size: int = 512
    enable_effects: bool = True
    enable_expression: bool = True
    normalize_audio: bool = True
    fade_in_ms: int = 50
    fade_out_ms: int = 200

@dataclass
class RenderProgress:
    """渲染进度"""
    total_notes: int = 0
    rendered_notes: int = 0
    current_measure: int = 0
    total_measures: int = 0
    elapsed_time: float = 0.0
    estimated_remaining: float = 0.0
    status: str = "准备中"

class HighQualitySoundFontRenderer:
    """高质量SoundFont渲染器"""
    
    def __init__(self, master_studio):
        """
        初始化渲染器
        
        Args:
            master_studio: PetersenMasterStudio实例
        """
        self.master_studio = master_studio
        
        # 渲染组件
        self.fluidsynth_lib = None
        self.synth = None
        self.current_soundfont_id = None
        
        # 渲染状态
        self.is_initialized = False
        self.current_settings = RenderSettings()
        self.render_progress = RenderProgress()
        self.is_rendering = False
        
        # 音频缓冲
        self.audio_buffer = []
        self.buffer_lock = threading.Lock()
        
        # 初始化渲染器
        self._initialize_renderer()
    
    def _initialize_renderer(self):
        """初始化渲染器"""
        try:
            if not FLUIDSYNTH_AVAILABLE:
                print("⚠️ FluidSynth不可用，将使用模拟模式")
                self.is_initialized = False
                return
            
            # 初始化FluidSynth
            self.fluidsynth_lib = fluidsynth
            self.synth = fluidsynth.Synth()
            
            # 设置默认参数
            self.synth.setting('audio.sample-format', '16bits')
            self.synth.setting('audio.buffer-size', str(self.current_settings.buffer_size))
            
            # 启动音频驱动
            self.synth.start()
            
            self.is_initialized = True
            print("✓ 高质量渲染器初始化完成")
            
        except Exception as e:
            print(f"❌ 渲染器初始化失败: {e}")
            self.is_initialized = False
    
    def load_soundfont(self, soundfont_path: str) -> bool:
        """
        加载SoundFont文件
        
        Args:
            soundfont_path: SoundFont文件路径
            
        Returns:
            bool: 加载是否成功
        """
        if not self.is_initialized:
            return False
        
        try:
            # 检查文件是否存在
            sf_path = Path(soundfont_path)
            if not sf_path.exists():
                # 尝试在配置的SoundFont目录中查找
                sf_dir = self.master_studio.config.soundfont_directory
                sf_path = sf_dir / soundfont_path
                
                if not sf_path.exists():
                    print(f"❌ SoundFont文件不存在: {soundfont_path}")
                    return False
            
            # 卸载当前SoundFont
            if self.current_soundfont_id is not None:
                self.synth.sfunload(self.current_soundfont_id)
            
            # 加载新SoundFont
            self.current_soundfont_id = self.synth.sfload(str(sf_path))
            
            if self.current_soundfont_id != -1:
                # 设置程序
                self.synth.program_select(0, self.current_soundfont_id, 0, 0)
                print(f"✓ SoundFont已加载: {sf_path.name}")
                return True
            else:
                print(f"❌ SoundFont加载失败: {sf_path}")
                return False
                
        except Exception as e:
            print(f"❌ SoundFont加载错误: {e}")
            return False
    
    def configure_quality(self, quality: RenderQuality):
        """
        配置渲染质量
        
        Args:
            quality: 质量级别
        """
        quality_settings = {
            RenderQuality.DRAFT: RenderSettings(
                quality=quality,
                sample_rate=22050,
                bit_depth=16,
                buffer_size=1024,
                enable_effects=False,
                enable_expression=False
            ),
            RenderQuality.STANDARD: RenderSettings(
                quality=quality,
                sample_rate=44100,
                bit_depth=16,
                buffer_size=512,
                enable_effects=True,
                enable_expression=True
            ),
            RenderQuality.HIGH: RenderSettings(
                quality=quality,
                sample_rate=44100,
                bit_depth=24,
                buffer_size=256,
                enable_effects=True,
                enable_expression=True
            ),
            RenderQuality.STUDIO: RenderSettings(
                quality=quality,
                sample_rate=48000,
                bit_depth=24,
                buffer_size=128,
                enable_effects=True,
                enable_expression=True,
                normalize_audio=True
            )
        }
        
        self.current_settings = quality_settings[quality]
        
        # 更新FluidSynth设置
        if self.is_initialized:
            try:
                self.synth.setting('synth.sample-rate', str(self.current_settings.sample_rate))
                
                if self.current_settings.bit_depth == 24:
                    self.synth.setting('audio.sample-format', 'float')
                else:
                    self.synth.setting('audio.sample-format', '16bits')
                
                print(f"✓ 渲染质量已设置为: {quality.value}")
                print(f"   采样率: {self.current_settings.sample_rate}Hz")
                print(f"   位深度: {self.current_settings.bit_depth}bit")
                
            except Exception as e:
                print(f"⚠️ 质量设置更新警告: {e}")
    
    def render_composition(self, composition, output_path: Path, 
                          quality: Optional[RenderQuality] = None) -> Optional[Path]:
        """
        渲染完整作曲到WAV文件
        
        Args:
            composition: 作曲对象
            output_path: 输出文件路径
            quality: 渲染质量（可选）
            
        Returns:
            Path: 成功时返回输出文件路径，失败时返回None
        """
        if not self.is_initialized:
            print("❌ 渲染器未初始化")
            return None
        
        try:
            # 设置质量
            if quality:
                self.configure_quality(quality)
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 开始渲染
            self.is_rendering = True
            self.render_progress.status = "正在渲染..."
            
            print(f"🎵 开始渲染: {output_path.name}")
            print(f"   质量: {self.current_settings.quality.value}")
            
            # 加载首选SoundFont
            if not self._ensure_soundfont_loaded():
                return None
            
            # 提取作曲数据
            render_data = self._extract_composition_data(composition)
            if not render_data:
                print("❌ 无法提取作曲数据")
                return None
            
            # 执行渲染
            audio_data = self._render_audio_data(render_data)
            if not audio_data:
                print("❌ 音频渲染失败")
                return None
            
            # 后处理
            if self.current_settings.normalize_audio:
                audio_data = self._normalize_audio(audio_data)
            
            audio_data = self._apply_fade(audio_data)
            
            # 保存WAV文件
            success = self._save_wav_file(audio_data, output_path)
            
            if success:
                print(f"✓ 渲染完成: {output_path.name}")
                print(f"   文件大小: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
                return output_path
            else:
                return None
                
        except Exception as e:
            print(f"❌ 渲染失败: {e}")
            return None
        finally:
            self.is_rendering = False
            self.render_progress.status = "完成"
    
    def render_composition_realtime(self, composition, preview_duration: float = 10.0) -> bool:
        """
        实时渲染作曲预览
        
        Args:
            composition: 作曲对象
            preview_duration: 预览时长（秒）
            
        Returns:
            bool: 渲染是否成功
        """
        if not self.is_initialized:
            print("❌ 渲染器未初始化")
            return False
        
        try:
            print(f"🔊 实时预览 ({preview_duration}秒)...")
            
            # 确保SoundFont已加载
            if not self._ensure_soundfont_loaded():
                return False
            
            # 提取预览数据
            preview_data = self._extract_preview_data(composition, preview_duration)
            
            # 实时播放
            return self._play_realtime(preview_data)
            
        except Exception as e:
            print(f"❌ 实时渲染失败: {e}")
            return False
    
    def _ensure_soundfont_loaded(self) -> bool:
        """确保SoundFont已加载"""
        if self.current_soundfont_id is not None:
            return True
        
        # 尝试加载首选SoundFont
        preferred_sf = self.master_studio.config.preferred_soundfont
        if self.load_soundfont(preferred_sf):
            return True
        
        # 尝试备选SoundFont
        alternative_sf = self.master_studio.config.alternative_soundfont
        if self.load_soundfont(alternative_sf):
            return True
        
        print("❌ 无法加载任何SoundFont")
        return False
    
    def _extract_composition_data(self, composition) -> Optional[Dict[str, Any]]:
        """
        从作曲对象提取渲染数据
        
        Args:
            composition: 作曲对象
            
        Returns:
            Dict: 渲染数据，包含音符、时间、表现力等信息
        """
        try:
            render_data = {
                "notes": [],
                "total_duration": 0.0,
                "tempo": 120,  # 默认BPM
                "measures": []
            }
            
            # 检查作曲对象的接口
            if hasattr(composition, 'get_render_data'):
                # 标准接口
                return composition.get_render_data()
            
            elif hasattr(composition, 'bass_track') and hasattr(composition, 'chord_track'):
                # 从轨道数据提取
                render_data = self._extract_from_tracks(composition)
            
            elif hasattr(composition, 'get_all_notes'):
                # 从音符列表提取
                notes = composition.get_all_notes()
                render_data["notes"] = self._convert_notes_to_render_format(notes)
            
            else:
                # 尝试通用方法
                print("⚠️ 作曲对象接口未知，尝试通用提取...")
                render_data = self._extract_generic(composition)
            
            return render_data if render_data["notes"] else None
            
        except Exception as e:
            print(f"❌ 作曲数据提取失败: {e}")
            return None
    
    def _extract_from_tracks(self, composition) -> Dict[str, Any]:
        """从轨道数据提取渲染信息"""
        render_data = {
            "notes": [],
            "total_duration": 0.0,
            "tempo": getattr(composition, 'bpm', 120),
            "measures": []
        }
        
        # 处理低音轨道
        if hasattr(composition, 'bass_track') and composition.bass_track:
            bass_notes = self._extract_track_notes(composition.bass_track, "bass")
            render_data["notes"].extend(bass_notes)
        
        # 处理和弦轨道
        if hasattr(composition, 'chord_track') and composition.chord_track:
            chord_notes = self._extract_track_notes(composition.chord_track, "chord")
            render_data["notes"].extend(chord_notes)
        
        # 处理旋律轨道
        if hasattr(composition, 'melody_track') and composition.melody_track:
            melody_notes = self._extract_track_notes(composition.melody_track, "melody")
            render_data["notes"].extend(melody_notes)
        
        # 计算总时长
        if render_data["notes"]:
            max_end_time = max(note["start_time"] + note["duration"] for note in render_data["notes"])
            render_data["total_duration"] = max_end_time
        
        return render_data
    
    def _extract_track_notes(self, track, track_type: str) -> List[Dict[str, Any]]:
        """从单个轨道提取音符"""
        notes = []
        
        try:
            if hasattr(track, 'notes') and track.notes:
                for note_info in track.notes:
                    note_data = {
                        "frequency": getattr(note_info, 'frequency', 440.0),
                        "start_time": getattr(note_info, 'start_time', 0.0),
                        "duration": getattr(note_info, 'duration', 0.5),
                        "velocity": getattr(note_info, 'velocity', 80),
                        "track_type": track_type
                    }
                    notes.append(note_data)
            
        except Exception as e:
            print(f"⚠️ 轨道 {track_type} 音符提取警告: {e}")
        
        return notes
    
    def _convert_notes_to_render_format(self, notes) -> List[Dict[str, Any]]:
        """转换音符到渲染格式"""
        render_notes = []
        
        for note in notes:
            try:
                render_note = {
                    "frequency": getattr(note, 'frequency', 440.0),
                    "start_time": getattr(note, 'start_time', 0.0),
                    "duration": getattr(note, 'duration', 0.5),
                    "velocity": getattr(note, 'velocity', 80),
                    "track_type": getattr(note, 'track_type', 'unknown')
                }
                render_notes.append(render_note)
                
            except Exception as e:
                print(f"⚠️ 音符转换警告: {e}")
                continue
        
        return render_notes
    
    def _extract_generic(self, composition) -> Dict[str, Any]:
        """通用作曲数据提取"""
        render_data = {
            "notes": [],
            "total_duration": 8.0,  # 默认8秒
            "tempo": 120,
            "measures": []
        }
        
        # 尝试获取基础音阶进行演示
        if hasattr(composition, 'petersen_scale'):
            scale = composition.petersen_scale
            scale_entries = scale.get_scale_entries()[:8]  # 取前8个音
            
            for i, entry in enumerate(scale_entries):
                note_data = {
                    "frequency": entry.freq,
                    "start_time": i * 0.8,  # 每个音符0.8秒间隔
                    "duration": 0.6,
                    "velocity": 80,
                    "track_type": "scale_demo"
                }
                render_data["notes"].append(note_data)
        
        return render_data
    
    def _render_audio_data(self, render_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        渲染音频数据
        
        Args:
            render_data: 渲染数据
            
        Returns:
            numpy.ndarray: 音频数据数组
        """
        if not FLUIDSYNTH_AVAILABLE:
            return self._simulate_audio_data(render_data)
        
        try:
            # 准备渲染
            notes = render_data["notes"]
            total_duration = render_data["total_duration"]
            sample_rate = self.current_settings.sample_rate
            
            # 计算总样本数
            total_samples = int(total_duration * sample_rate)
            
            # 更新进度
            self.render_progress.total_notes = len(notes)
            self.render_progress.rendered_notes = 0
            
            print(f"   音符数量: {len(notes)}")
            print(f"   总时长: {total_duration:.1f}秒")
            print(f"   采样点: {total_samples:,}")
            
            # 创建音频缓冲区
            if self.current_settings.bit_depth == 24:
                audio_buffer = np.zeros(total_samples, dtype=np.float32)
            else:
                audio_buffer = np.zeros(total_samples, dtype=np.int16)
            
            # 渲染每个音符
            for i, note in enumerate(notes):
                if not self.is_rendering:  # 检查是否被取消
                    break
                
                self._render_single_note(note, audio_buffer, sample_rate)
                
                self.render_progress.rendered_notes = i + 1
                
                # 显示进度
                if (i + 1) % 10 == 0 or (i + 1) == len(notes):
                    progress = (i + 1) / len(notes) * 100
                    print(f"   渲染进度: {progress:.1f}% ({i + 1}/{len(notes)})")
            
            return audio_buffer
            
        except Exception as e:
            print(f"❌ 音频数据渲染失败: {e}")
            return None
    
    def _render_single_note(self, note: Dict[str, Any], audio_buffer: np.ndarray, sample_rate: int):
        """渲染单个音符到音频缓冲区"""
        try:
            # 计算MIDI音符号和弯音轮值
            frequency = note["frequency"]
            midi_note, pitch_bend = self._frequency_to_midi_with_bend(frequency)
            
            # 计算时间参数
            start_sample = int(note["start_time"] * sample_rate)
            duration_samples = int(note["duration"] * sample_rate)
            
            # 确保不超出缓冲区
            if start_sample >= len(audio_buffer):
                return
            
            end_sample = min(start_sample + duration_samples, len(audio_buffer))
            actual_duration = (end_sample - start_sample) / sample_rate
            
            # 设置弯音轮
            if pitch_bend != 8192:  # 非中性值
                self.synth.pitch_bend(0, pitch_bend)
            
            # 开始音符
            self.synth.noteon(0, midi_note, note["velocity"])
            
            # 渲染这个音符的音频段
            note_samples = end_sample - start_sample
            if note_samples > 0:
                # 生成音频
                note_audio = self.synth.get_samples(note_samples)
                
                if note_audio is not None and len(note_audio) == note_samples:
                    # 添加到主缓冲区
                    audio_buffer[start_sample:end_sample] += note_audio
            
            # 停止音符
            self.synth.noteoff(0, midi_note)
            
            # 重置弯音轮
            if pitch_bend != 8192:
                self.synth.pitch_bend(0, 8192)
            
        except Exception as e:
            print(f"⚠️ 音符渲染警告: {e}")
    
    def _frequency_to_midi_with_bend(self, frequency: float) -> Tuple[int, int]:
        """
        将频率转换为MIDI音符号和弯音轮值
        
        Args:
            frequency: 频率(Hz)
            
        Returns:
            Tuple[int, int]: (MIDI音符号, 弯音轮值)
        """
        # 计算最接近的MIDI音符
        midi_note_float = 69 + 12 * np.log2(frequency / 440.0)
        midi_note = int(round(midi_note_float))
        
        # 计算音分差异
        midi_freq = 440.0 * (2 ** ((midi_note - 69) / 12))
        cents_diff = 1200 * np.log2(frequency / midi_freq)
        
        # 转换为弯音轮值 (范围: 0-16383, 中性值: 8192)
        # 弯音轮范围通常是±200音分
        bend_range = 200.0  # 音分
        pitch_bend = 8192 + int((cents_diff / bend_range) * 8192)
        
        # 限制在有效范围内
        pitch_bend = max(0, min(16383, pitch_bend))
        
        return midi_note, pitch_bend
    
    def _simulate_audio_data(self, render_data: Dict[str, Any]) -> np.ndarray:
        """模拟音频数据（当FluidSynth不可用时）"""
        notes = render_data["notes"]
        total_duration = render_data["total_duration"]
        sample_rate = self.current_settings.sample_rate
        
        total_samples = int(total_duration * sample_rate)
        audio_buffer = np.zeros(total_samples, dtype=np.float32)
        
        print("   使用模拟音频渲染...")
        
        # 为每个音符生成简单的正弦波
        for note in notes:
            frequency = note["frequency"]
            start_sample = int(note["start_time"] * sample_rate)
            duration_samples = int(note["duration"] * sample_rate)
            
            if start_sample >= len(audio_buffer):
                continue
            
            end_sample = min(start_sample + duration_samples, len(audio_buffer))
            
            # 生成正弦波
            t = np.linspace(0, note["duration"], end_sample - start_sample)
            amplitude = note["velocity"] / 127.0 * 0.1  # 降低音量
            sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
            
            # 添加到缓冲区
            audio_buffer[start_sample:end_sample] += sine_wave
        
        return audio_buffer
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """音频标准化"""
        if len(audio_data) == 0:
            return audio_data
        
        # 找到峰值
        peak = np.max(np.abs(audio_data))
        
        if peak > 0:
            # 标准化到-1dB以避免削波
            target_peak = 0.891  # 约-1dB
            audio_data = audio_data * (target_peak / peak)
        
        return audio_data
    
    def _apply_fade(self, audio_data: np.ndarray) -> np.ndarray:
        """应用淡入淡出效果"""
        if len(audio_data) == 0:
            return audio_data
        
        sample_rate = self.current_settings.sample_rate
        
        # 淡入
        fade_in_samples = int(self.current_settings.fade_in_ms * sample_rate / 1000)
        if fade_in_samples > 0 and fade_in_samples < len(audio_data):
            fade_in = np.linspace(0, 1, fade_in_samples)
            audio_data[:fade_in_samples] *= fade_in
        
        # 淡出
        fade_out_samples = int(self.current_settings.fade_out_ms * sample_rate / 1000)
        if fade_out_samples > 0 and fade_out_samples < len(audio_data):
            fade_out = np.linspace(1, 0, fade_out_samples)
            audio_data[-fade_out_samples:] *= fade_out
        
        return audio_data
    
    def _save_wav_file(self, audio_data: np.ndarray, output_path: Path) -> bool:
        """
        保存WAV文件
        
        Args:
            audio_data: 音频数据
            output_path: 输出路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 转换数据格式
            if self.current_settings.bit_depth == 24:
                # 24位浮点转换为24位整数
                audio_int = (audio_data * (2**23 - 1)).astype(np.int32)
                sample_width = 3
            else:
                # 16位
                audio_int = (audio_data * (2**15 - 1)).astype(np.int16)
                sample_width = 2
            
            # 写入WAV文件
            with wave.open(str(output_path), 'wb') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(self.current_settings.sample_rate)
                
                if self.current_settings.bit_depth == 24:
                    # 24位需要特殊处理
                    audio_bytes = audio_int.tobytes()
                else:
                    audio_bytes = audio_int.tobytes()
                
                wav_file.writeframes(audio_bytes)
            
            return True
            
        except Exception as e:
            print(f"❌ WAV文件保存失败: {e}")
            return False
    
    def _extract_preview_data(self, composition, duration: float) -> Dict[str, Any]:
        """提取预览数据（截取前几秒）"""
        full_data = self._extract_composition_data(composition)
        
        if not full_data:
            return {"notes": [], "total_duration": 0.0}
        
        # 过滤出指定时长内的音符
        preview_notes = [
            note for note in full_data["notes"]
            if note["start_time"] < duration
        ]
        
        # 调整音符时长
        for note in preview_notes:
            if note["start_time"] + note["duration"] > duration:
                note["duration"] = duration - note["start_time"]
        
        return {
            "notes": preview_notes,
            "total_duration": duration,
            "tempo": full_data.get("tempo", 120)
        }
    
    def _play_realtime(self, preview_data: Dict[str, Any]) -> bool:
        """实时播放预览数据"""
        if not FLUIDSYNTH_AVAILABLE:
            print("⚠️ FluidSynth不可用，跳过实时播放")
            return False
        
        try:
            notes = preview_data["notes"]
            
            # 按开始时间排序
            notes.sort(key=lambda x: x["start_time"])
            
            start_time = time.time()
            
            for note in notes:
                # 等待到音符开始时间
                target_time = start_time + note["start_time"]
                current_time = time.time()
                
                if target_time > current_time:
                    time.sleep(target_time - current_time)
                
                # 计算MIDI参数
                midi_note, pitch_bend = self._frequency_to_midi_with_bend(note["frequency"])
                
                # 设置弯音轮
                if pitch_bend != 8192:
                    self.synth.pitch_bend(0, pitch_bend)
                
                # 播放音符
                self.synth.noteon(0, midi_note, note["velocity"])
                
                # 等待音符时长
                time.sleep(note["duration"])
                
                # 停止音符
                self.synth.noteoff(0, midi_note)
                
                # 重置弯音轮
                if pitch_bend != 8192:
                    self.synth.pitch_bend(0, 8192)
            
            return True
            
        except Exception as e:
            print(f"❌ 实时播放失败: {e}")
            return False
    
    def get_render_progress(self) -> RenderProgress:
        """获取当前渲染进度"""
        return self.render_progress
    
    def cancel_render(self):
        """取消当前渲染"""
        self.is_rendering = False
        self.render_progress.status = "已取消"
    
    def cleanup(self):
        """清理资源"""
        if self.synth:
            try:
                self.synth.delete()
            except:
                pass
        
        self.is_initialized = False
        self.current_soundfont_id = None

# ========== 便利函数 ==========

def create_studio_renderer(master_studio, quality: RenderQuality = RenderQuality.STANDARD) -> HighQualitySoundFontRenderer:
    """
    创建录音室级别渲染器
    
    Args:
        master_studio: PetersenMasterStudio实例
        quality: 渲染质量
        
    Returns:
        HighQualitySoundFontRenderer: 配置好的渲染器
    """
    renderer = HighQualitySoundFontRenderer(master_studio)
    
    if renderer.is_initialized:
        renderer.configure_quality(quality)
    
    return renderer

def render_composition_to_wav(composition, output_path: str, 
                             master_studio, quality: str = "high") -> bool:
    """
    便利函数：将作曲渲染为WAV文件
    
    Args:
        composition: 作曲对象
        output_path: 输出文件路径
        master_studio: PetersenMasterStudio实例
        quality: 质量级别字符串
        
    Returns:
        bool: 渲染是否成功
    """
    quality_enum = RenderQuality(quality.lower())
    
    with create_studio_renderer(master_studio, quality_enum) as renderer:
        result_path = renderer.render_composition(composition, Path(output_path), quality_enum)
        return result_path is not None

if __name__ == "__main__":
    print("🎵 Petersen高质量SoundFont渲染器")
    print("这是一个支持模块，请通过PetersenMasterStudio使用")