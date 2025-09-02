"""
Petersen音阶播放库

集成PetersenScale生成和FluidSynth播放功能的高级接口库。
提供便捷的频率选择、MIDI映射、音色切换和播放控制功能。

主要功能：
- 基于PetersenScale的灵活频率选择（频率范围、音区、五行、极性等）
- 自动MIDI键映射和调音设置
- 多种音色和播放模式
- 实时演奏和序列播放支持

核心API：
  - PetersenPlayer(soundfont_path, **scale_params)
  - player.select_frequencies(**filters) -> 选择频率子集
  - player.load_instrument(program) -> 切换音色
  - player.play_sequence(notes, **timing) -> 播放序列
  - player.play_interactive() -> 交互式演奏

使用示例：
  ```python
  # 创建播放器
  player = PetersenPlayer("../Soundfonts/FluidR3_GM.sf2", F_base=20.0, delta_theta=4.8)
  
  # 选择特定频率
  player.select_frequencies(freq_range=(100, 1000), elements=['金', '木'], polarities=['阴', '中'])
  
  # 设置音色并播放
  player.load_instrument('Piano')
  player.play_sequence(['J-', 'J0', 'M-', 'M0'], note_duration=0.5)
  ```
"""

import ctypes
import time
import math
from typing import List, Dict, Optional, Union, Tuple, Set
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from PetersenScale import PetersenScale, ScaleEntry, ELEMENTS_CN, ELEMENTS_PY

class InstrumentType(Enum):
    """预定义的MIDI乐器类型"""
    PIANO = 0
    ELECTRIC_PIANO = 4
    HARPSICHORD = 6
    CELESTA = 8
    VIOLIN = 40
    CELLO = 42
    HARP = 46
    TIMPANI = 47
    STRING_ENSEMBLE = 48
    CHOIR = 52
    FLUTE = 73
    PAN_FLUTE = 75
    SHAKUHACHI = 77
    GUITAR = 25
    ELECTRIC_GUITAR = 27
    BASS = 32
    SYNTH_LEAD = 80
    SYNTH_PAD = 88

@dataclass
class PlayNote:
    """播放音符数据结构"""
    key_name: str
    frequency: float
    midi_key: int
    velocity: int = 80
    duration: float = 0.5

class FrequencyFilter:
    """频率过滤器，用于选择Petersen音阶的子集"""
    
    def __init__(self):
        self.freq_range: Optional[Tuple[float, float]] = None
        self.zones: Optional[Set[int]] = None
        self.elements: Optional[Set[str]] = None  # 中文名或拼音
        self.polarities: Optional[Set[str]] = None  # '阴', '中', '阳' 或 '-', '0', '+'
        self.key_names: Optional[Set[str]] = None  # 直接指定音名
        
    def matches(self, entry: ScaleEntry) -> bool:
        """检查条目是否匹配过滤条件"""
        # 频率范围过滤
        if self.freq_range:
            min_f, max_f = self.freq_range
            if not (min_f <= entry.freq <= max_f):
                return False
        
        # 音区过滤
        if self.zones and entry.n not in self.zones:
            return False
        
        # 五行过滤
        if self.elements:
            element_cn = ELEMENTS_CN[entry.e]
            element_py = ELEMENTS_PY[entry.e]
            if not (element_cn in self.elements or element_py in self.elements):
                return False
        
        # 极性过滤
        if self.polarities:
            polarity_cn = {-1: '阴', 0: '中', 1: '阳'}[entry.p]
            polarity_symbol = {-1: '-', 0: '0', 1: '+'}[entry.p]
            if not (polarity_cn in self.polarities or polarity_symbol in self.polarities):
                return False
        
        # 直接音名过滤
        if self.key_names:
            if not (entry.key_short in self.key_names or entry.key_long in self.key_names):
                return False
        
        return True

class PetersenPlayer:
    """
    Petersen音阶播放器
    
    整合PetersenScale生成和FluidSynth播放功能的高级接口
    """
    
    def __init__(self, 
                 soundfont_path: str,
                 fluidsynth_lib: str = "/opt/homebrew/lib/libfluidsynth.dylib",
                 F_base: float = 20.0,
                 delta_theta: float = 4.8,
                 F_min: float = 30.0,
                 F_max: float = 6000.0,
                 reference: float = 440.0):
        """
        初始化播放器
        
        Args:
            soundfont_path: SoundFont文件路径
            fluidsynth_lib: FluidSynth库路径
            F_base, delta_theta, F_min, F_max, reference: PetersenScale参数
        """
        self.soundfont_path = Path(soundfont_path)
        if not self.soundfont_path.exists():
            raise FileNotFoundError(f"SoundFont file not found: {soundfont_path}")
        
        # 初始化PetersenScale
        self.scale = PetersenScale(F_base, delta_theta, F_min, F_max, reference)
        self.all_entries = self.scale.generate_raw()
        self.selected_entries: List[ScaleEntry] = []
        self.midi_mapping: Dict[int, ScaleEntry] = {}  # midi_key -> entry
        
        # 初始化FluidSynth（使用更保守的方式）
        self.fluidsynth = None
        self.settings = None
        self.synth = None
        self.driver = None
        self.sf_id = None
        self.current_channel = 0
        self.tuning_enabled = False
        self.tuning_method = None
        
        print(f"✓ Generated {len(self.all_entries)} Petersen scale entries")
        
        # 启动FluidSynth
        try:
            self.fluidsynth = ctypes.CDLL(fluidsynth_lib)
            print(f"✓ Loaded FluidSynth from: {fluidsynth_lib}")
            self._setup_fluidsynth_signatures()
            self._init_fluidsynth()
        except Exception as e:
            self.cleanup()
            raise Exception(f"FluidSynth initialization failed: {e}")
        
    def _setup_fluidsynth_signatures(self):
        """设置FluidSynth函数签名"""
        try:
            # 基本函数签名
            self.fluidsynth.new_fluid_settings.restype = ctypes.c_void_p
            self.fluidsynth.new_fluid_synth.restype = ctypes.c_void_p
            self.fluidsynth.new_fluid_synth.argtypes = [ctypes.c_void_p]
            self.fluidsynth.new_fluid_audio_driver.restype = ctypes.c_void_p
            self.fluidsynth.new_fluid_audio_driver.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            
            # SoundFont函数
            self.fluidsynth.fluid_synth_sfload.restype = ctypes.c_int
            self.fluidsynth.fluid_synth_sfload.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
            
            # 程序切换
            self.fluidsynth.fluid_synth_program_change.restype = ctypes.c_int
            self.fluidsynth.fluid_synth_program_change.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
            
            # 音符控制
            self.fluidsynth.fluid_synth_noteon.restype = ctypes.c_int
            self.fluidsynth.fluid_synth_noteon.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
            self.fluidsynth.fluid_synth_noteoff.restype = ctypes.c_int
            self.fluidsynth.fluid_synth_noteoff.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
            
            # 弯音轮（作为备用方案）
            self.fluidsynth.fluid_synth_pitch_bend.restype = ctypes.c_int
            self.fluidsynth.fluid_synth_pitch_bend.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
            
            # 清理函数
            self.fluidsynth.delete_fluid_audio_driver.argtypes = [ctypes.c_void_p]
            self.fluidsynth.delete_fluid_synth.argtypes = [ctypes.c_void_p]
            self.fluidsynth.delete_fluid_settings.argtypes = [ctypes.c_void_p]
            
            # 尝试调音API（可选）
            self.tuning_method = 'pitch_bend'  # 默认使用弯音轮
            try:
                # 尝试新版本调音API
                self.fluidsynth.fluid_synth_activate_key_tuning.restype = ctypes.c_int
                self.fluidsynth.fluid_synth_activate_key_tuning.argtypes = [
                    ctypes.c_void_p, ctypes.c_int, ctypes.c_int, 
                    ctypes.c_char_p, ctypes.POINTER(ctypes.c_double), ctypes.c_int
                ]
                self.tuning_method = 'activate_key_tuning'
                print("✓ 检测到 activate_key_tuning API")
            except AttributeError:
                try:
                    # 尝试旧版本调音API
                    self.fluidsynth.fluid_synth_create_key_tuning.restype = ctypes.c_int
                    self.fluidsynth.fluid_synth_create_key_tuning.argtypes = [
                        ctypes.c_void_p, ctypes.c_int, ctypes.c_int, 
                        ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)
                    ]
                    self.fluidsynth.fluid_synth_select_tuning.restype = ctypes.c_int
                    self.fluidsynth.fluid_synth_select_tuning.argtypes = [
                        ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
                    ]
                    self.tuning_method = 'create_key_tuning'
                    print("✓ 检测到 create_key_tuning API")
                except AttributeError:
                    print("⚠️  仅支持弯音轮调音（精度有限）")
                    
        except Exception as e:
            raise Exception(f"Failed to setup FluidSynth function signatures: {e}")
    
    def _init_fluidsynth(self):
        """初始化FluidSynth引擎"""
        try:
            # 创建设置
            print("创建FluidSynth设置...")
            self.settings = self.fluidsynth.new_fluid_settings()
            if not self.settings:
                raise Exception("Failed to create FluidSynth settings")
            
            # 创建合成器
            print("创建FluidSynth合成器...")
            self.synth = self.fluidsynth.new_fluid_synth(self.settings)
            if not self.synth:
                raise Exception("Failed to create FluidSynth synthesizer")
            
            # 创建音频驱动
            print("创建FluidSynth音频驱动...")
            self.driver = self.fluidsynth.new_fluid_audio_driver(self.settings, self.synth)
            if not self.driver:
                raise Exception("Failed to create FluidSynth audio driver")
            
            # 加载SoundFont
            print(f"加载SoundFont: {self.soundfont_path}")
            sf_path_bytes = str(self.soundfont_path).encode('utf-8')
            self.sf_id = self.fluidsynth.fluid_synth_sfload(self.synth, sf_path_bytes, 1)
            if self.sf_id == -1:
                raise Exception(f"Failed to load SoundFont: {self.soundfont_path}")
            
            print(f"✓ FluidSynth初始化成功，SoundFont已加载 (ID: {self.sf_id})")
            
        except Exception as e:
            self.cleanup()
            raise Exception(f"FluidSynth initialization failed: {e}")
    
    def select_frequencies(self, 
                          freq_range: Optional[Tuple[float, float]] = None,
                          zones: Optional[List[int]] = None,
                          elements: Optional[List[str]] = None,
                          polarities: Optional[List[str]] = None,
                          key_names: Optional[List[str]] = None,
                          max_keys: int = 120) -> List[ScaleEntry]:
        """
        选择符合条件的频率子集
        
        Args:
            freq_range: 频率范围 (min_hz, max_hz)
            zones: 音区列表，如 [5, 6, 7]
            elements: 五行列表，如 ['金', '木'] 或 ['J', 'M']
            polarities: 极性列表，如 ['阴', '中'] 或 ['-', '0']
            key_names: 直接指定音名，如 ['J-', 'M0', 'S+']
            max_keys: 最大选择数量，防止超出MIDI键限制
        
        Returns:
            选中的ScaleEntry列表，按频率排序
        """
        # 创建过滤器
        filter_obj = FrequencyFilter()
        filter_obj.freq_range = freq_range
        filter_obj.zones = set(zones) if zones else None
        filter_obj.elements = set(elements) if elements else None
        filter_obj.polarities = set(polarities) if polarities else None
        filter_obj.key_names = set(key_names) if key_names else None
        
        # 应用过滤器
        filtered = [entry for entry in self.all_entries if filter_obj.matches(entry)]
        
        # 按频率排序并限制数量
        filtered.sort(key=lambda x: x.freq)
        if len(filtered) > max_keys:
            print(f"⚠️  选择了{len(filtered)}个频率，截取前{max_keys}个")
            filtered = filtered[:max_keys]
        
        self.selected_entries = filtered
        self._map_to_midi_keys()
        
        print(f"✓ 选择了 {len(self.selected_entries)} 个频率")
        if self.selected_entries:
            freqs = [e.freq for e in self.selected_entries]
            print(f"  频率范围: {min(freqs):.2f} - {max(freqs):.2f} Hz")
            print(f"  前5个音名: {[e.key_short for e in self.selected_entries[:5]]}")
        
        return self.selected_entries
    
    def _map_to_midi_keys(self):
        """将选择的频率映射到MIDI键并设置调音"""
        self.midi_mapping.clear()
        
        # 创建频率数组
        frequencies = []
        for i, entry in enumerate(self.selected_entries):
            if i >= 128:  # MIDI键限制
                break
            
            midi_key = i
            self.midi_mapping[midi_key] = entry
            frequencies.append(entry.freq)
        
        # 填充剩余的MIDI键到128个（使用标准音高）
        while len(frequencies) < 128:
            # 标准MIDI音高公式：f = 440 * 2^((n-69)/12)
            midi_key = len(frequencies)
            standard_freq = 440.0 * (2 ** ((midi_key - 69) / 12.0))
            frequencies.append(standard_freq)
        
        # 应用调音（仅在有自定义频率时）
        if len(self.midi_mapping) > 0:
            if self.tuning_method == 'activate_key_tuning':
                self._apply_activate_key_tuning(frequencies)
            elif self.tuning_method == 'create_key_tuning':
                self._apply_create_key_tuning(frequencies)
            else:
                print("⚠️  将在播放时使用弯音轮调音")
                
        print(f"✓ 映射了 {len(self.midi_mapping)} 个频率到MIDI键")
    
    def _apply_activate_key_tuning(self, frequencies: List[float]):
        """使用activate_key_tuning API应用调音"""
        try:
            # 创建频率数组
            freq_array = (ctypes.c_double * 128)(*frequencies)
            
            # 激活键调音
            tuning_name = b"Petersen_Tuning"
            result = self.fluidsynth.fluid_synth_activate_key_tuning(
                self.synth, 0, 0, tuning_name, freq_array, 1
            )
            
            if result == 0:
                self.tuning_enabled = True
                print("✓ 调音已激活")
            else:
                print(f"⚠️  调音激活返回代码: {result}")
                self.tuning_enabled = False
        except Exception as e:
            print(f"❌ 调音激活失败: {e}")
            self.tuning_enabled = False
    
    def _apply_create_key_tuning(self, frequencies: List[float]):
        """使用create_key_tuning API应用调音"""
        try:
            # 创建频率数组
            freq_array = (ctypes.c_double * 128)(*frequencies)
            
            # 创建调音
            tuning_name = b"Petersen_Tuning"
            result1 = self.fluidsynth.fluid_synth_create_key_tuning(
                self.synth, 0, 0, tuning_name, freq_array
            )
            
            # 选择调音
            result2 = self.fluidsynth.fluid_synth_select_tuning(
                self.synth, self.current_channel, 0, 0
            )
            
            if result1 == 0 and result2 == 0:
                self.tuning_enabled = True
                print("✓ 调音已创建并选择")
            else:
                print(f"⚠️  调音创建结果: {result1}, 选择结果: {result2}")
                self.tuning_enabled = False
        except Exception as e:
            print(f"❌ 调音创建失败: {e}")
            self.tuning_enabled = False
    
    def _calculate_pitch_bend(self, target_freq: float, midi_key: int) -> int:
        """计算达到目标频率所需的弯音轮值"""
        # 标准MIDI音高
        standard_freq = 440.0 * (2 ** ((midi_key - 69) / 12.0))
        
        # 计算音分差
        cents_diff = 1200.0 * math.log2(target_freq / standard_freq)
        
        # 弯音轮范围通常是±200音分，对应±8192
        pitch_bend = int((cents_diff / 200.0) * 8192)
        
        # 限制在有效范围内
        return max(-8192, min(8191, pitch_bend))
    
    def load_instrument(self, instrument: Union[str, int, InstrumentType]):
        """
        加载乐器音色
        
        Args:
            instrument: 乐器名称(str)、MIDI程序号(int)或InstrumentType枚举
        """
        if isinstance(instrument, str):
            # 通过名称查找
            instrument_map = {
                'Piano': InstrumentType.PIANO,
                'Electric Piano': InstrumentType.ELECTRIC_PIANO,
                'Harpsichord': InstrumentType.HARPSICHORD,
                'Violin': InstrumentType.VIOLIN,
                'Cello': InstrumentType.CELLO,
                'Flute': InstrumentType.FLUTE,
                'Guitar': InstrumentType.GUITAR,
                'Harp': InstrumentType.HARP,
                'Choir': InstrumentType.CHOIR,
                'Synth': InstrumentType.SYNTH_LEAD,
            }
            if instrument in instrument_map:
                program = instrument_map[instrument].value
            else:
                raise ValueError(f"Unknown instrument: {instrument}")
        elif isinstance(instrument, InstrumentType):
            program = instrument.value
        elif isinstance(instrument, int):
            program = instrument
        else:
            raise TypeError("instrument must be str, int, or InstrumentType")
        
        # 设置MIDI程序
        result = self.fluidsynth.fluid_synth_program_change(self.synth, self.current_channel, program)
        if result == 0:
            print(f"✓ 加载乐器: 程序号 {program}")
        else:
            print(f"⚠️  乐器加载可能失败: 程序号 {program}, 返回码 {result}")
    
    def play_note(self, key_name: str, duration: float = 0.5, velocity: int = 80) -> bool:
        """
        播放单个音符
        
        Args:
            key_name: 音名，如 'J-', 'M0', 'S+'
            duration: 持续时间(秒)
            velocity: 力度 (0-127)
        
        Returns:
            成功播放返回True，否则False
        """
        # 查找对应的MIDI键
        midi_key = None
        for mk, entry in self.midi_mapping.items():
            if entry.key_short == key_name or entry.key_long == key_name:
                midi_key = mk
                break
        
        if midi_key is None:
            print(f"❌ 未找到音名: {key_name}")
            return False
        
        entry = self.midi_mapping[midi_key]
        print(f"播放: {entry.key_short} ({entry.freq:.3f} Hz) [MIDI {midi_key}]")
        
        # 如果没有激活调音，使用弯音轮
        if not self.tuning_enabled and self.tuning_method == 'pitch_bend':
            pitch_bend = self._calculate_pitch_bend(entry.freq, midi_key)
            self.fluidsynth.fluid_synth_pitch_bend(self.synth, self.current_channel, pitch_bend + 8192)
        
        # 播放音符
        result_on = self.fluidsynth.fluid_synth_noteon(self.synth, self.current_channel, midi_key, velocity)
        if result_on != 0:
            print(f"⚠️  noteon返回码: {result_on}")
            
        time.sleep(duration)
        
        result_off = self.fluidsynth.fluid_synth_noteoff(self.synth, self.current_channel, midi_key)
        if result_off != 0:
            print(f"⚠️  noteoff返回码: {result_off}")
        
        # 重置弯音轮
        if not self.tuning_enabled and self.tuning_method == 'pitch_bend':
            self.fluidsynth.fluid_synth_pitch_bend(self.synth, self.current_channel, 8192)
        
        return True
    
    def play_sequence(self, 
                     key_names: List[str],
                     note_duration: float = 0.5,
                     note_gap: float = 0.1,
                     velocity: int = 80) -> int:
        """
        播放音符序列
        
        Args:
            key_names: 音名列表
            note_duration: 每个音符持续时间(秒)
            note_gap: 音符间隔时间(秒)
            velocity: 力度
        
        Returns:
            成功播放的音符数
        """
        played_count = 0
        print(f"=== 播放序列: {len(key_names)} 个音符 ===")
        
        for key_name in key_names:
            if self.play_note(key_name, note_duration, velocity):
                played_count += 1
            time.sleep(note_gap)
        
        print(f"✓ 序列播放完成: {played_count}/{len(key_names)}")
        return played_count
    
    def play_all_selected(self, 
                         note_duration: float = 0.3,
                         note_gap: float = 0.05) -> None:
        """播放所有选中的频率"""
        if not self.selected_entries:
            print("❌ 没有选中的频率")
            return
        
        print(f"=== 播放所有选中频率: {len(self.selected_entries)} 个 ===")
        
        for i, (midi_key, entry) in enumerate(self.midi_mapping.items()):
            print(f"{i+1:3d}: {entry.key_short} {entry.key_long} {entry.freq:.3f} Hz")
            
            # 如果没有激活调音，使用弯音轮
            if not self.tuning_enabled and self.tuning_method == 'pitch_bend':
                pitch_bend = self._calculate_pitch_bend(entry.freq, midi_key)
                self.fluidsynth.fluid_synth_pitch_bend(self.synth, self.current_channel, pitch_bend + 8192)
            
            self.fluidsynth.fluid_synth_noteon(self.synth, self.current_channel, midi_key, 80)
            time.sleep(note_duration)
            self.fluidsynth.fluid_synth_noteoff(self.synth, self.current_channel, midi_key)
            
            # 重置弯音轮
            if not self.tuning_enabled and self.tuning_method == 'pitch_bend':
                self.fluidsynth.fluid_synth_pitch_bend(self.synth, self.current_channel, 8192)
            
            time.sleep(note_gap)
        
        print("✓ 全部播放完成")
    
    def play_interactive(self):
        """交互式演奏模式"""
        if not self.selected_entries:
            print("❌ 没有选中的频率，请先调用 select_frequencies()")
            return
        
        print(f"\n=== 交互式演奏模式 ===")
        print(f"可用音符 ({len(self.midi_mapping)} 个):")
        
        # 显示可用音名
        for i, (midi_key, entry) in enumerate(self.midi_mapping.items()):
            print(f"{i:2d}: {entry.key_short:4s} {entry.key_long:<6s} {entry.freq:8.3f} Hz")
        
        print(f"\n指令:")
        print(f"  输入音名 (如 'J-', 'M0') 播放音符")
        print(f"  输入数字 (如 '0', '1') 按索引播放")
        print(f"  'all' - 播放全部")
        print(f"  'q' - 退出")
        
        while True:
            try:
                cmd = input("\n> ").strip()
                
                if cmd.lower() == 'q':
                    break
                elif cmd.lower() == 'all':
                    self.play_all_selected()
                elif cmd.isdigit():
                    idx = int(cmd)
                    if 0 <= idx < len(self.midi_mapping):
                        midi_keys = list(self.midi_mapping.keys())
                        entry = self.midi_mapping[midi_keys[idx]]
                        self.play_note(entry.key_short)
                    else:
                        print(f"❌ 无效索引，请输入 0-{len(self.midi_mapping)-1}")
                else:
                    # 尝试作为音名播放
                    if not self.play_note(cmd):
                        print(f"❌ 无效指令: {cmd}")
                        
            except KeyboardInterrupt:
                print("\n中断演奏")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
        
        print("退出交互模式")
    
    def get_selection_info(self) -> Dict:
        """获取当前选择的详细信息"""
        if not self.selected_entries:
            return {"message": "没有选中的频率"}
        
        freqs = [e.freq for e in self.selected_entries]
        zones = list(set(e.n for e in self.selected_entries))
        elements = list(set(ELEMENTS_CN[e.e] for e in self.selected_entries))
        polarities = list(set({-1: '阴', 0: '中', 1: '阳'}[e.p] for e in self.selected_entries))
        
        return {
            "total_entries": len(self.selected_entries),
            "frequency_range": (min(freqs), max(freqs)),
            "zones_used": sorted(zones),
            "elements_used": elements,
            "polarities_used": polarities,
            "key_names": [e.key_short for e in self.selected_entries],
            "midi_mapping_count": len(self.midi_mapping),
            "tuning_enabled": self.tuning_enabled,
            "tuning_method": self.tuning_method
        }
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.driver:
                self.fluidsynth.delete_fluid_audio_driver(self.driver)
                self.driver = None
            if self.synth:
                self.fluidsynth.delete_fluid_synth(self.synth)
                self.synth = None
            if self.settings:
                self.fluidsynth.delete_fluid_settings(self.settings)
                self.settings = None
            print("✓ FluidSynth资源已清理")
        except Exception as e:
            print(f"⚠️  清理资源时出错: {e}")
    
    def __del__(self):
        """析构函数，自动清理资源"""
        self.cleanup()
    
    def __enter__(self):
        """上下文管理器支持"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器支持"""
        self.cleanup()

# 便利函数
def create_player(soundfont_path: str = "../Soundfonts/FluidR3_GM.sf2", **kwargs) -> PetersenPlayer:
    """
    便利函数：创建PetersenPlayer实例
    
    Args:
        soundfont_path: SoundFont文件路径
        **kwargs: 传递给PetersenPlayer的其他参数
    
    Returns:
        PetersenPlayer实例
    """
    return PetersenPlayer(soundfont_path, **kwargs)

def quick_play(key_names: List[str], 
               instrument: str = 'Piano',
               soundfont_path: str = "../Soundfonts/FluidR3_GM.sf2",
               **scale_params) -> None:
    """
    便利函数：快速播放指定音名序列
    
    Args:
        key_names: 要播放的音名列表
        instrument: 乐器名称
        soundfont_path: SoundFont路径
        **scale_params: PetersenScale参数
    """
    with create_player(soundfont_path, **scale_params) as player:
        # 选择包含指定音名的频率
        player.select_frequencies(key_names=key_names)
        player.load_instrument(instrument)
        player.play_sequence(key_names)

if __name__ == "__main__":
    """
    库测试代码
    """
    print("=== PetersenFluidSynth 库测试 ===\n")
    
    try:
        # 测试基本功能
        with create_player() as player:
            # 选择中音区的金木水频率
            player.select_frequencies(
                freq_range=(100, 1000),
                elements=['金', '木', '水'],
                polarities=['阴', '中']
            )
            
            # 显示选择信息
            info = player.get_selection_info()
            print(f"选择信息: {info}")
            
            # 测试不同乐器
            instruments = ['Piano', 'Violin', 'Flute']
            for instrument in instruments:
                print(f"\n--- 测试乐器: {instrument} ---")
                player.load_instrument(instrument)
                
                # 播放前几个音符
                if len(player.selected_entries) >= 3:
                    test_keys = [e.key_short for e in player.selected_entries[:3]]
                    player.play_sequence(test_keys, note_duration=0.4)
        
        print(f"\n✓ 库测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()