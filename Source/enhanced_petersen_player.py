"""
增强版Petersen音阶播放器
整合所有功能模块，提供统一的高级API接口
"""
import time
import ctypes
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass

import sys
from pathlib import Path

# 添加当前目录到路径
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 导入所有功能模块
from frequency_accurate import FrequencyAccuratePlayback
from audio_effects import AdvancedAudioEffects, EffectSettings
from expression_control import ExpressionController, ExpressionParameters
from soundfont_manager import SoundFontManager
from performance_modes import PerformanceModes, PerformanceMode
from utils.analysis import FrequencyAnalyzer, analyze_petersen_scale_characteristics
from utils.constants import DEFAULT_SOUNDFONTS, DEFAULT_PLAY_PARAMS
from utils.presets import COMPLETE_PRESET_COMBINATIONS

@dataclass
class PlayerConfiguration:
    """播放器配置"""
    soundfont_directory: str = "../Soundfonts"
    default_soundfont: str = ""
    default_channel: int = 0
    sample_rate: int = 44100
    buffer_size: int = 1024
    audio_driver: str = "coreaudio"  # alsa, pulse, jack, coreaudio (macOS)
    enable_accurate_frequency: bool = True
    enable_effects: bool = True
    enable_expression: bool = True
    auto_optimize_settings: bool = True

class EnhancedPetersenPlayer:
    """
    增强版Petersen音阶播放器
    
    集成精确频率播放、高级音效、表现力控制、SoundFont管理和多种演奏模式
    """
    
    def __init__(self, config: Optional[PlayerConfiguration] = None):
        """
        初始化增强播放器
        
        Args:
            config: 播放器配置，None使用默认配置
        """
        self.config = config or PlayerConfiguration()
        
        # 核心组件
        self.fluidsynth = None
        self.synth = None
        self.adriver = None
        
        # 功能模块
        self.freq_player: Optional[FrequencyAccuratePlayback] = None
        self.effects: Optional[AdvancedAudioEffects] = None
        self.expression: Optional[ExpressionController] = None
        self.sf_manager: Optional[SoundFontManager] = None
        self.performance_modes: Optional[PerformanceModes] = None
        
        # 状态信息
        self.is_initialized = False
        self.current_channel = self.config.default_channel
        
        # 统计信息
        self.session_stats = {
            'notes_played': 0,
            'sequences_played': 0,
            'total_play_time': 0.0,
            'accuracy_compensations': 0,
            'soundfonts_loaded': 0,
            'start_time': time.time()
        }
        
        print("🎵 Enhanced Petersen Player 初始化中...")
        self._initialize()
    
    def _initialize(self) -> bool:
        """初始化所有组件"""
        try:
            # 初始化FluidSynth核心
            if not self._init_fluidsynth():
                return False
            
            # 初始化功能模块
            if not self._init_modules():
                return False
            
            # 应用初始配置
            if not self._apply_initial_config():
                return False
            
            self.is_initialized = True
            print("✅ Enhanced Petersen Player 初始化完成")
            self._print_welcome_info()
            
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    def _init_fluidsynth(self) -> bool:
        """初始化FluidSynth核心"""
        try:
            # 检测操作系统并加载合适的库
            if sys.platform == "darwin":  # macOS
                lib_names = [
                    "/opt/homebrew/lib/libfluidsynth.dylib",
                    "/usr/local/lib/libfluidsynth.dylib",
                    "libfluidsynth.dylib"
                ]
            elif sys.platform.startswith("linux"):
                lib_names = [
                    "/usr/lib/x86_64-linux-gnu/libfluidsynth.so",
                    "/usr/lib/libfluidsynth.so",
                    "libfluidsynth.so"
                ]
            else:  # Windows
                lib_names = ["libfluidsynth.dll", "fluidsynth.dll"]
            
            # 尝试加载库
            self.fluidsynth = None
            for lib_name in lib_names:
                try:
                    self.fluidsynth = ctypes.CDLL(lib_name)
                    print(f"✓ FluidSynth库加载成功: {lib_name}")
                    break
                except OSError:
                    continue
            
            if not self.fluidsynth:
                print("❌ 无法加载FluidSynth库")
                print("请安装FluidSynth:")
                print("  - macOS: brew install fluid-synth")
                print("  - Ubuntu: sudo apt-get install libfluidsynth-dev")
                print("  - Windows: 下载并安装FluidSynth DLL")
                return False
            
            # 设置函数原型
            self._setup_fluidsynth_prototypes()
            
            # 创建设置对象
            settings = self.fluidsynth.new_fluid_settings()
            if not settings:
                print("❌ 无法创建FluidSynth设置")
                return False
            
            # 配置音频设置
            self._configure_audio_settings(settings)
            
            # 创建合成器
            self.synth = self.fluidsynth.new_fluid_synth(settings)
            if not self.synth:
                print("❌ 无法创建FluidSynth合成器")
                return False
            
            # 创建音频驱动
            self.adriver = self.fluidsynth.new_fluid_audio_driver(settings, self.synth)
            if not self.adriver:
                print("⚠️  音频驱动创建失败，将使用文件输出")
            
            print("✓ FluidSynth核心初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ FluidSynth初始化异常: {e}")
            return False
    
    def _setup_fluidsynth_prototypes(self):
        """设置FluidSynth函数原型"""
        # 基础函数
        self.fluidsynth.new_fluid_settings.restype = ctypes.c_void_p
        self.fluidsynth.new_fluid_synth.argtypes = [ctypes.c_void_p]
        self.fluidsynth.new_fluid_synth.restype = ctypes.c_void_p
        self.fluidsynth.new_fluid_audio_driver.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.fluidsynth.new_fluid_audio_driver.restype = ctypes.c_void_p
        
        # 音符控制
        self.fluidsynth.fluid_synth_noteon.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.fluidsynth.fluid_synth_noteon.restype = ctypes.c_int
        self.fluidsynth.fluid_synth_noteoff.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.fluidsynth.fluid_synth_noteoff.restype = ctypes.c_int
        
        # SoundFont控制
        self.fluidsynth.fluid_synth_sfload.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
        self.fluidsynth.fluid_synth_sfload.restype = ctypes.c_int
        self.fluidsynth.fluid_synth_sfunload.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.fluidsynth.fluid_synth_sfunload.restype = ctypes.c_int
        
        # 乐器和控制器
        self.fluidsynth.fluid_synth_program_change.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.fluidsynth.fluid_synth_program_change.restype = ctypes.c_int
        self.fluidsynth.fluid_synth_cc.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.fluidsynth.fluid_synth_cc.restype = ctypes.c_int
        self.fluidsynth.fluid_synth_pitch_bend.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        self.fluidsynth.fluid_synth_pitch_bend.restype = ctypes.c_int
        
        # 音效控制（可选）
        try:
            self.fluidsynth.fluid_synth_set_reverb.argtypes = [
                ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double
            ]
            self.fluidsynth.fluid_synth_set_reverb.restype = ctypes.c_int
            
            self.fluidsynth.fluid_synth_set_chorus.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int
            ]
            self.fluidsynth.fluid_synth_set_chorus.restype = ctypes.c_int
        except AttributeError:
            print("⚠️  部分音效API不可用")
        
        # 设置函数
        try:
            self.fluidsynth.fluid_settings_setstr.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
            self.fluidsynth.fluid_settings_setstr.restype = ctypes.c_int
            self.fluidsynth.fluid_settings_setnum.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
            self.fluidsynth.fluid_settings_setnum.restype = ctypes.c_int
            self.fluidsynth.fluid_settings_setint.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
            self.fluidsynth.fluid_settings_setint.restype = ctypes.c_int
        except AttributeError:
            print("⚠️  部分设置API不可用")
    
    def _configure_audio_settings(self, settings):
        """配置音频设置"""
        try:
            # 设置音频驱动
            if hasattr(self.fluidsynth, 'fluid_settings_setstr'):
                self.fluidsynth.fluid_settings_setstr(
                    settings, b"audio.driver", self.config.audio_driver.encode('utf-8')
                )
            
            # 设置采样率
            if hasattr(self.fluidsynth, 'fluid_settings_setnum'):
                self.fluidsynth.fluid_settings_setnum(
                    settings, b"synth.sample-rate", float(self.config.sample_rate)
                )
            
            # 设置缓冲区大小
            if hasattr(self.fluidsynth, 'fluid_settings_setint'):
                self.fluidsynth.fluid_settings_setint(
                    settings, b"audio.period-size", self.config.buffer_size
                )
                
                # 设置音色数量
                self.fluidsynth.fluid_settings_setint(
                    settings, b"synth.polyphony", 256
                )
            
            print(f"✓ 音频配置: {self.config.audio_driver}, {self.config.sample_rate}Hz, {self.config.buffer_size}样本")
            
        except Exception as e:
            print(f"⚠️  音频设置异常: {e}")
    
    def _init_modules(self) -> bool:
        """初始化功能模块"""
        try:
            # 精确频率播放器
            self.freq_player = FrequencyAccuratePlayback(
                self.fluidsynth, self.synth, self.current_channel
            )
            
            # 音效控制器
            self.effects = AdvancedAudioEffects(
                self.fluidsynth, self.synth, self.current_channel
            )
            
            # 表现力控制器
            self.expression = ExpressionController(
                self.fluidsynth, self.synth, self.current_channel
            )
            
            # SoundFont管理器
            self.sf_manager = SoundFontManager(
                self.fluidsynth, self.synth, self.config.soundfont_directory
            )
            
            # 演奏模式控制器
            self.performance_modes = PerformanceModes(
                self.freq_player, self.effects, self.expression, self.sf_manager
            )
            
            print("✓ 所有功能模块初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 模块初始化失败: {e}")
            return False
    
    def _apply_initial_config(self) -> bool:
        """应用初始配置"""
        try:
            # 加载默认SoundFont
            if self.config.default_soundfont:
                success = self.sf_manager.load_soundfont(self.config.default_soundfont)
                if success:
                    self.session_stats['soundfonts_loaded'] += 1
            else:
                # 尝试自动选择最佳SoundFont
                best_sf = self.sf_manager.get_best_soundfont_for_task("demo")
                if best_sf:
                    success = self.sf_manager.load_soundfont(best_sf)
                    if success:
                        self.session_stats['soundfonts_loaded'] += 1
                        print(f"✓ 自动选择SoundFont: {best_sf}")
            
            # 应用自动优化
            if self.config.auto_optimize_settings:
                self._auto_optimize_settings()
            
            return True
            
        except Exception as e:
            print(f"⚠️  初始配置异常: {e}")
            return True  # 非致命错误
    
    def _auto_optimize_settings(self):
        """自动优化设置"""
        current_sf = self.sf_manager.current_soundfont
        if current_sf:
            sf_info = self.sf_manager.soundfonts[current_sf]
            
            # 根据SoundFont类型自动优化音效
            self.effects.optimize_for_soundfont(current_sf, sf_info.file_size_mb)
            
            # 设置合适的表现力预设
            if sf_info.sf_type.value == "piano_specialized":
                self.expression.apply_expression_preset("romantic")
            elif sf_info.sf_type.value == "orchestral":
                self.expression.apply_expression_preset("classical")
            else:
                self.expression.apply_expression_preset("expressive")
    
    def _print_welcome_info(self):
        """打印欢迎信息"""
        print("\n" + "="*60)
        print("🎵 Enhanced Petersen Music System")
        print("="*60)
        
        # SoundFont信息
        sf_summary = self.sf_manager.get_soundfont_summary()
        print(f"📁 发现 {sf_summary['total_soundfonts']} 个SoundFont文件")
        if sf_summary['current_soundfont']:
            current_info = sf_summary['soundfont_details'][sf_summary['current_soundfont']]
            print(f"🎼 当前SoundFont: {sf_summary['current_soundfont']} ({current_info['type']}, {current_info['size_mb']:.1f}MB)")
        
        # 功能状态
        print(f"⚡ 精确频率播放: {'启用' if self.config.enable_accurate_frequency else '禁用'}")
        print(f"🎛️  音效处理: {'启用' if self.config.enable_effects else '禁用'}")
        print(f"🎭 表现力控制: {'启用' if self.config.enable_expression else '禁用'}")
        
        # 可用模式
        available_modes = self.performance_modes.get_available_modes()
        print(f"🎯 可用演奏模式: {len(available_modes)} 种")
        
        print("="*60)
        print("准备就绪! 开始您的Petersen音阶之旅...")
        print("="*60 + "\n")
    
    # ========== 高级API接口 ==========
    
    def play_frequencies(self, 
                        frequencies: List[float],
                        key_names: Optional[List[str]] = None,
                        **kwargs) -> bool:
        """
        播放频率序列（高级接口）
        
        Args:
            frequencies: 频率列表
            key_names: 音名列表（可选）
            **kwargs: 其他播放参数
            
        Returns:
            播放成功返回True
        """
        if not self._check_ready():
            return False
        
        # 合并默认参数
        params = DEFAULT_PLAY_PARAMS.copy()
        params.update(kwargs)
        
        start_time = time.time()
        
        try:
            # 根据配置选择播放方式
            if params.get('use_accurate_frequency', True) and self.config.enable_accurate_frequency:
                success_count = self.freq_player.play_accurate_sequence(
                    frequencies, 
                    key_names=key_names,
                    **{k: v for k, v in params.items() if k not in ['use_accurate_frequency']}
                )
                success = success_count == len(frequencies)
            else:
                # 使用简单播放（待实现）
                success = self._play_simple_sequence(frequencies, key_names, params)
            
            # 更新统计
            play_time = time.time() - start_time
            self.session_stats['notes_played'] += len(frequencies)
            self.session_stats['sequences_played'] += 1
            self.session_stats['total_play_time'] += play_time
            
            return success
            
        except Exception as e:
            print(f"❌ 播放异常: {e}")
            return False
    
    def play_petersen_scale(self,
                           scale_entries,
                           mode: str = "solo_piano",
                           style: str = "romantic",
                           **kwargs) -> bool:
        """
        播放Petersen音阶（专用接口）
        
        Args:
            scale_entries: Petersen音阶条目列表
            mode: 演奏模式
            style: 演奏风格
            **kwargs: 其他参数
            
        Returns:
            播放成功返回True
        """
        if not self._check_ready():
            return False
        
        # 提取频率和音名
        frequencies = [entry.freq for entry in scale_entries]
        key_names = [getattr(entry, 'key_name', f"Entry{i+1}") for i, entry in enumerate(scale_entries)]
        
        # 分析音阶特性
        characteristics = analyze_petersen_scale_characteristics(scale_entries)
        print(f"🔍 音阶分析: {characteristics.get('total_entries', 0)} 个音符, "
              f"跨越 {characteristics.get('spans_octaves', 0):.1f} 个八度")
        
        # 选择演奏模式
        try:
            if mode == "solo_piano":
                return self.performance_modes.execute_solo_piano_mode(frequencies, key_names, style)
            elif mode == "orchestral":
                arrangement = kwargs.get('arrangement', 'chamber')
                return self.performance_modes.execute_orchestral_mode(frequencies, key_names, arrangement)
            elif mode == "comparison":
                comparison_type = kwargs.get('comparison_type', '12tet_vs_petersen')
                return self.performance_modes.execute_comparison_demo(frequencies, key_names, comparison_type)
            elif mode == "educational":
                lesson_type = kwargs.get('lesson_type', 'basic_theory')
                return self.performance_modes.execute_educational_mode(frequencies, key_names, lesson_type)
            else:
                # 默认使用频率播放
                return self.play_frequencies(frequencies, key_names, **kwargs)
        
        except Exception as e:
            print(f"❌ 演奏模式异常: {e}")
            return False
    
    def demonstrate_frequency_accuracy(self, frequencies: List[float], key_names: Optional[List[str]] = None) -> Dict:
        """
        演示频率精确度
        
        Args:
            frequencies: 频率列表
            key_names: 音名列表
            
        Returns:
            精确度分析结果
        """
        if not self._check_ready():
            return {}
        
        print("\n🔬 === 频率精确度演示 ===")
        
        # 分析频率精确度需求
        analysis = self.freq_player.analyze_frequency_accuracy(frequencies)
        
        print(f"📊 精确度分析:")
        print(f"   总音符: {len(frequencies)}")
        print(f"   需要补偿: {analysis['pitch_bend_compensation_needed']} ({analysis['compensation_percentage']:.1f}%)")
        print(f"   最大偏差: {analysis['max_deviation']:.1f} 音分")
        print(f"   补偿有效性: {analysis['compensation_effectiveness']:.1f}%")
        
        # 执行对比演示
        self.performance_modes.execute_comparison_demo(frequencies, key_names, "12tet_vs_petersen")
        
        return analysis
    
    def quick_soundfont_demo(self) -> bool:
        """快速SoundFont演示"""
        if not self._check_ready():
            return False
        
        # 生成演示频率（C大调音阶）
        demo_frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
        demo_names = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
        
        return self.performance_modes.execute_comparison_demo(
            demo_frequencies, demo_names, "soundfont_quality"
        )
    
    def switch_soundfont(self, sf_name: str, auto_optimize: bool = True) -> bool:
        """
        切换SoundFont
        
        Args:
            sf_name: SoundFont文件名
            auto_optimize: 是否自动优化设置
            
        Returns:
            切换成功返回True
        """
        if not self._check_ready():
            return False
        
        success = self.sf_manager.load_soundfont(sf_name)
        if success:
            self.session_stats['soundfonts_loaded'] += 1
            
            if auto_optimize:
                self._auto_optimize_settings()
                print("✓ 设置已自动优化")
        
        return success
    
    def switch_instrument(self, program: int, channel: Optional[int] = None) -> bool:
        """
        切换乐器
        
        Args:
            program: MIDI程序号
            channel: MIDI通道（None使用当前通道）
            
        Returns:
            切换成功返回True
        """
        if not self._check_ready():
            return False
        
        target_channel = channel or self.current_channel
        
        try:
            result = self.fluidsynth.fluid_synth_program_change(
                self.synth, target_channel, program
            )
            
            if result == 0:
                print(f"✓ 乐器切换成功: 程序 {program}")
                return True
            else:
                print(f"⚠️  乐器切换警告: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 乐器切换异常: {e}")
            return False
    
    def apply_preset_combination(self, 
                                effect_preset: str = "hall",
                                expression_preset: str = "romantic") -> bool:
        """
        应用预设组合
        
        Args:
            effect_preset: 音效预设名称
            expression_preset: 表现力预设名称
            
        Returns:
            应用成功返回True
        """
        if not self._check_ready():
            return False
        
        success1 = self.effects.apply_effect_preset(effect_preset)
        success2 = self.expression.apply_expression_preset(expression_preset)
        
        return success1 and success2
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        if not self.is_initialized:
            return {'status': 'not_initialized'}
        
        return {
            'status': 'ready',
            'session_stats': self.session_stats.copy(),
            'soundfont_summary': self.sf_manager.get_soundfont_summary(),
            'current_effects': self.effects.get_current_settings(),
            'current_expression': self.expression.get_current_parameters(),
            'accuracy_report': self.freq_player.get_accuracy_report() if self.freq_player else None,
            'available_modes': self.performance_modes.get_available_modes(),
            'runtime_seconds': time.time() - self.session_stats['start_time']
        }
    
    def _check_ready(self) -> bool:
        """检查系统是否就绪"""
        if not self.is_initialized:
            print("❌ 系统未初始化")
            return False
        
        if not self.sf_manager.current_soundfont:
            print("⚠️  未加载SoundFont，尝试自动加载...")
            best_sf = self.sf_manager.get_best_soundfont_for_task("demo")
            if best_sf and self.sf_manager.load_soundfont(best_sf):
                print(f"✓ 自动加载: {best_sf}")
                return True
            else:
                print("❌ 无可用的SoundFont")
                return False
        
        return True
    
    def _play_simple_sequence(self, frequencies: List[float], 
                            key_names: Optional[List[str]], 
                            params: Dict) -> bool:
        """简单序列播放（不使用精确频率补偿）"""
        # 这是一个简化版本的实现
        velocity = params.get('velocity', 80)
        duration = params.get('duration', 0.5)
        gap = params.get('gap', 0.1)
        
        for i, freq in enumerate(frequencies):
            # 找到最接近的MIDI音符（不使用补偿）
            midi_note, _, _ = FrequencyAnalyzer.find_closest_midi_note(freq)
            
            # 播放音符
            self.fluidsynth.fluid_synth_noteon(self.synth, self.current_channel, midi_note, velocity)
            time.sleep(duration)
            self.fluidsynth.fluid_synth_noteoff(self.synth, self.current_channel, midi_note)
            
            if i < len(frequencies) - 1:
                time.sleep(gap)
        
        return True
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.sf_manager:
                self.sf_manager.cleanup()
            
            if self.expression:
                self.expression.reset_pedals()
            
            if self.adriver:
                self.fluidsynth.delete_fluid_audio_driver(self.adriver)
            
            if self.synth:
                self.fluidsynth.delete_fluid_synth(self.synth)
            
            print("✓ 资源清理完成")
            
        except Exception as e:
            print(f"⚠️  清理异常: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()

# ========== 便利函数 ==========

def create_player(soundfont_dir: str = "../Soundfonts", **kwargs) -> EnhancedPetersenPlayer:
    """
    创建播放器的便利函数
    
    Args:
        soundfont_dir: SoundFont目录
        **kwargs: 其他配置参数
        
    Returns:
        配置好的播放器实例
    """
    config = PlayerConfiguration(soundfont_directory=soundfont_dir, **kwargs)
    return EnhancedPetersenPlayer(config)

def quick_demo(scale_entries, mode: str = "solo_piano") -> bool:
    """
    快速演示的便利函数
    
    Args:
        scale_entries: Petersen音阶条目
        mode: 演奏模式
        
    Returns:
        演示成功返回True
    """
    try:
        with create_player() as player:
            return player.play_petersen_scale(scale_entries, mode=mode)
    except Exception as e:
        print(f"❌ 快速演示失败: {e}")
        return False

def compare_frequencies(frequencies: List[float], key_names: Optional[List[str]] = None) -> bool:
    """
    频率对比的便利函数
    
    Args:
        frequencies: 频率列表
        key_names: 音名列表
        
    Returns:
        对比成功返回True
    """
    try:
        with create_player() as player:
            return player.demonstrate_frequency_accuracy(frequencies, key_names)
    except Exception as e:
        print(f"❌ 频率对比失败: {e}")
        return False

def soundfont_showcase() -> bool:
    """
    SoundFont展示的便利函数
    
    Returns:
        展示成功返回True
    """
    try:
        with create_player() as player:
            return player.quick_soundfont_demo()
    except Exception as e:
        print(f"❌ SoundFont展示失败: {e}")
        return False