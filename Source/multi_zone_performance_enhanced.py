#!/usr/bin/env python3
"""
Petersen音阶增强表现力演奏系统

专为Petersen黄金比例音阶设计的高质量音乐演奏系统。
包含完整的表现力控制、音效处理和针对非平均律的特殊优化。

主要特性：
1. 完整的FluidSynth音效控制（混响、合唱、滤波等）
2. 动态表现力（力度曲线、时值变化、踏板效果）
3. 针对Petersen音阶优化的乐器选择
4. 专业级音色和音效处理
"""

from PetersenFluidSynth import create_player, InstrumentType
from PetersenScale import ELEMENTS_CN
import ctypes
import time
import math
import random

class EnhancedPetersenPlayer:
    """增强版Petersen音阶播放器"""
    
    def __init__(self, soundfont_path="../Soundfonts/FluidR3_GM.sf2"):
        self.player = create_player(soundfont_path)
        self.setup_enhanced_controls()
        
    def setup_enhanced_controls(self):
        """设置增强控制功能"""
        # 添加MIDI控制器函数签名
        self.player.fluidsynth.fluid_synth_cc.restype = ctypes.c_int
        self.player.fluidsynth.fluid_synth_cc.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        
        # 添加音效设置函数
        try:
            self.player.fluidsynth.fluid_synth_set_reverb.restype = ctypes.c_int
            self.player.fluidsynth.fluid_synth_set_reverb.argtypes = [
                ctypes.c_void_p, ctypes.c_double, ctypes.c_double, 
                ctypes.c_double, ctypes.c_double
            ]
            
            self.player.fluidsynth.fluid_synth_set_chorus.restype = ctypes.c_int
            self.player.fluidsynth.fluid_synth_set_chorus.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_double,
                ctypes.c_double, ctypes.c_double, ctypes.c_int
            ]
            self.has_builtin_effects = True
            print("✓ 检测到内置音效支持")
        except AttributeError:
            self.has_builtin_effects = False
            print("⚠️  使用CC控制器模拟音效")
    
    def setup_reverb_and_chorus(self, reverb_level=0.7, chorus_level=0.4):
        """设置混响和合唱效果"""
        if self.has_builtin_effects:
            # 内置音效设置
            self.player.fluidsynth.fluid_synth_set_reverb(
                self.player.synth, 
                reverb_level,  # roomsize (0.0-1.2)
                0.4,           # damping (0.0-1.0)  
                0.6,           # width (0.0-100.0)
                0.3            # level (0.0-1.0)
            )
            
            self.player.fluidsynth.fluid_synth_set_chorus(
                self.player.synth,
                3,             # voice count (0-99)
                chorus_level,  # level (0.0-10.0)
                1.2,          # speed (0.29-5.0)
                8.0,          # depth (0.0-40.0)
                0             # type (sine=0, triangle=1)
            )
            print(f"✓ 内置音效已设置 - 混响:{reverb_level:.1f}, 合唱:{chorus_level:.1f}")
        else:
            # 使用CC控制器
            channel = self.player.current_channel
            self.player.fluidsynth.fluid_synth_cc(
                self.player.synth, channel, 91, int(reverb_level * 127)
            )
            self.player.fluidsynth.fluid_synth_cc(
                self.player.synth, channel, 93, int(chorus_level * 127)
            )
            print(f"✓ CC音效已设置 - 混响:{int(reverb_level*127)}, 合唱:{int(chorus_level*127)}")
    
    def set_expression_controls(self, channel, expression_type="warm"):
        """设置表现力控制器"""
        expression_presets = {
            "warm": {        # 温暖音色
                "cutoff": 100,      # CC74: 滤波器截止频率
                "resonance": 60,    # CC71: 滤波器共振
                "attack": 70,       # CC73: 音头时间
                "release": 80,      # CC72: 释放时间
                "brightness": 110,  # CC1: 调制轮(亮度)
            },
            "bright": {      # 明亮音色
                "cutoff": 127,
                "resonance": 40,
                "attack": 30,
                "release": 60,
                "brightness": 127,
            },
            "soft": {        # 柔和音色
                "cutoff": 80,
                "resonance": 80,
                "attack": 100,
                "release": 100,
                "brightness": 70,
            },
            "dynamic": {     # 动态音色
                "cutoff": 90,
                "resonance": 50,
                "attack": 50,
                "release": 70,
                "brightness": 90,
            }
        }
        
        preset = expression_presets.get(expression_type, expression_presets["warm"])
        
        for cc_name, cc_value in preset.items():
            cc_number = {
                "cutoff": 74,
                "resonance": 71,
                "attack": 73,
                "release": 72,
                "brightness": 1,
            }[cc_name]
            
            self.player.fluidsynth.fluid_synth_cc(
                self.player.synth, channel, cc_number, cc_value
            )
        
        print(f"✓ 表现力控制已设置: {expression_type}")
    
    def sustain_pedal(self, channel, on=True):
        """延音踏板控制"""
        value = 127 if on else 0
        self.player.fluidsynth.fluid_synth_cc(
            self.player.synth, channel, 64, value  # CC64: 延音踏板
        )
        status = "开启" if on else "关闭"
        print(f"🎹 延音踏板: {status}")
    
    def calculate_dynamic_velocity(self, note_index, total_notes, base_velocity=60, curve_type="crescendo"):
        """计算动态力度曲线"""
        progress = note_index / max(1, total_notes - 1)
        
        curves = {
            "crescendo": lambda p: base_velocity + int((127 - base_velocity) * p),           # 渐强
            "diminuendo": lambda p: 127 - int((127 - base_velocity) * p),                   # 渐弱  
            "arch": lambda p: base_velocity + int((127 - base_velocity) * math.sin(p * math.pi)), # 拱形
            "wave": lambda p: base_velocity + int(30 * math.sin(p * 4 * math.pi)),         # 波浪
            "random": lambda p: base_velocity + random.randint(-20, 40),                    # 随机变化
        }
        
        velocity = curves.get(curve_type, curves["crescendo"])(progress)
        return max(30, min(127, velocity))
    
    def calculate_timing_variation(self, note_index, total_notes, base_duration=1.0, variation_type="rubato"):
        """计算时值微妙变化"""
        progress = note_index / max(1, total_notes - 1)
        
        variations = {
            "rubato": lambda p: base_duration * (0.9 + 0.2 * math.sin(p * 6 * math.pi)),  # 自由节拍
            "accelerando": lambda p: base_duration * (1.2 - 0.4 * p),                      # 渐快
            "ritardando": lambda p: base_duration * (0.8 + 0.4 * p),                       # 渐慢
            "swing": lambda p: base_duration * (1.1 if note_index % 2 else 0.9),          # 摇摆
            "steady": lambda p: base_duration,                                             # 稳定
        }
        
        duration = variations.get(variation_type, variations["rubato"])(progress)
        return max(0.3, min(2.0, duration))

def get_suitable_instruments_for_petersen():
    """获取适合Petersen音阶的乐器列表"""
    return [
        # 音色名称, 乐器类型, 频率范围, 表现力类型, 音效设置
        ('Choir Aahs', InstrumentType.CHOIR, (80, 1000), 'warm', {'reverb': 0.8, 'chorus': 0.3}),
        ('String Ensemble', InstrumentType.STRING_ENSEMBLE, (60, 2000), 'dynamic', {'reverb': 0.6, 'chorus': 0.4}),
        ('Warm Pad', InstrumentType.SYNTH_PAD, (30, 3000), 'soft', {'reverb': 0.9, 'chorus': 0.5}),
        ('Flute', InstrumentType.FLUTE, (200, 2000), 'bright', {'reverb': 0.4, 'chorus': 0.2}),
        ('Harp', InstrumentType.HARP, (40, 2500), 'warm', {'reverb': 0.5, 'chorus': 0.3}),
        ('Electric Piano', InstrumentType.ELECTRIC_PIANO, (50, 2000), 'dynamic', {'reverb': 0.3, 'chorus': 0.6}),
        ('Synth Lead', InstrumentType.SYNTH_LEAD, (100, 4000), 'bright', {'reverb': 0.4, 'chorus': 0.4}),
        ('Pan Flute', InstrumentType.PAN_FLUTE, (150, 1500), 'soft', {'reverb': 0.7, 'chorus': 0.2}),
    ]

def main():
    """主演奏函数"""
    print("=== Petersen音阶增强表现力演奏系统 ===\n")
    
    # 推荐高质量SoundFont信息
    print("📄 推荐高质量SoundFont:")
    print("   1. GeneralUser GS v1.471 (免费, 高质量)")
    print("      下载: http://www.schristiancollins.com/generaluser.php")
    print("   2. FluidR3_GM2-2.sf2 (免费升级版)")  
    print("      下载: https://github.com/FluidSynth/fluidsynth/wiki/SoundFont")
    print("   3. Steinway Grand Piano (商业, 专业级)")
    print("      搜索: 'Steinway Grand Piano SoundFont'\n")
    
    # 演奏参数设置
    dynamics_curves = ['crescendo', 'diminuendo', 'arch', 'wave']
    timing_variations = ['rubato', 'accelerando', 'ritardando', 'steady']
    
    # 极性定义
    polarities = [
        (-1, '阴', '-'),
        (0, '中', '0'), 
        (1, '阳', '+')
    ]
    
    try:
        # 创建增强播放器
        enhanced_player = EnhancedPetersenPlayer()
        player = enhanced_player.player
        
        print(f"✓ 增强播放器创建成功")
        
        # 获取音区
        target_zones = list(set(entry.n for entry in player.all_entries))
        target_zones.sort()
        print(f"✓ 检测到音区: {target_zones}")
        
        # 获取适合的乐器
        instruments = get_suitable_instruments_for_petersen()
        
        print(f"\n🎼 开始增强演奏 - {len(instruments)} 种乐器 × 5 方位 × 3 极性")
        print(f"═══════════════════════════════════════════════════════════\n")
        
        # 最外层：乐器循环
        for inst_idx, (instrument_name, instrument_type, freq_range, expression_type, effects) in enumerate(instruments):
            freq_min, freq_max = freq_range
            
            print(f"\n🎹 乐器 {inst_idx+1}/{len(instruments)}: {instrument_name}")
            print(f"   频率范围: {freq_min}-{freq_max} Hz | 表现力: {expression_type}")
            print(f"   音效设置: 混响={effects['reverb']:.1f}, 合唱={effects['chorus']:.1f}")
            print(f"───────────────────────────────────────────────────────────")
            
            # 加载乐器
            player.load_instrument(instrument_type)
            
            # 设置音效和表现力
            enhanced_player.setup_reverb_and_chorus(effects['reverb'], effects['chorus'])
            enhanced_player.set_expression_controls(player.current_channel, expression_type)
            time.sleep(0.8)
            
            # 中层：五行方位循环
            for element_idx, element in enumerate(ELEMENTS_CN):
                print(f"\n  🌟 方位: {element} ({element_idx+1}/5)")
                
                # 内层：极性循环
                for polarity_idx, (polarity_value, polarity_cn, polarity_symbol) in enumerate(polarities):
                    print(f"\n    ⚊ 极性: {polarity_cn} ({polarity_symbol})")
                    
                    # 选择频率
                    selected = player.select_frequencies(
                        zones=target_zones,
                        elements=[element],
                        polarities=[polarity_cn],
                        freq_range=(freq_min, freq_max),
                        max_keys=32  # 限制音符数量以保持演奏流畅
                    )
                    
                    if not selected:
                        print("      ⚠️  无适合频率，跳过")
                        continue
                    
                    # 按频率排序
                    selected.sort(key=lambda x: x.freq)
                    
                    # 显示信息
                    freqs = [e.freq for e in selected]
                    print(f"      音符数: {len(selected)} | 频率: {min(freqs):.1f}-{max(freqs):.1f} Hz")
                    
                    # 选择动态曲线和时值变化
                    curve_type = dynamics_curves[inst_idx % len(dynamics_curves)]
                    timing_type = timing_variations[element_idx % len(timing_variations)]
                    
                    print(f"      力度曲线: {curve_type} | 时值变化: {timing_type}")
                    
                    # 开启延音踏板（为某些乐器）
                    use_sustain = instrument_name in ['Electric Piano', 'Warm Pad', 'Harp']
                    if use_sustain:
                        enhanced_player.sustain_pedal(player.current_channel, True)
                    
                    # 演奏音符序列
                    print(f"      ♪ 演奏中:", end="", flush=True)
                    
                    for i, entry in enumerate(selected):
                        # 计算动态参数
                        velocity = enhanced_player.calculate_dynamic_velocity(
                            i, len(selected), 65, curve_type
                        )
                        duration = enhanced_player.calculate_timing_variation(
                            i, len(selected), 0.8, timing_type
                        )
                        
                        # 播放音符
                        midi_key = i
                        if midi_key in player.midi_mapping:
                            player.fluidsynth.fluid_synth_noteon(
                                player.synth, player.current_channel, midi_key, velocity
                            )
                            
                            # 显示进度
                            if i % 4 == 0:
                                print(f" {entry.key_short}", end="", flush=True)
                            
                            time.sleep(duration * 0.7)  # 音符持续时间
                            
                            player.fluidsynth.fluid_synth_noteoff(
                                player.synth, player.current_channel, midi_key
                            )
                            
                            time.sleep(duration * 0.3)  # 间隔时间
                    
                    print(" ✓")
                    
                    # 关闭延音踏板
                    if use_sustain:
                        enhanced_player.sustain_pedal(player.current_channel, False)
                    
                    # 极性间暂停
                    time.sleep(0.5)
                
                # 方位间暂停
                time.sleep(1.0)
            
            # 乐器间暂停
            print(f"\n  ✓ {instrument_name} 演奏完成")
            time.sleep(1.5)
        
        # 最终和谐演示
        print(f"\n🌈 最终演示：五行和谐共鸣")
        print(f"═══════════════════════════════════════════════════════════")
        
        # 创建五行和谐音符
        harmony_notes = []
        for element in ELEMENTS_CN:
            element_entries = player.select_frequencies(
                zones=[5, 6, 7],  # 中音区
                elements=[element],
                polarities=['中'],  # 中性极性
                freq_range=(150, 1000),
                max_keys=1
            )
            if element_entries:
                harmony_notes.extend(element_entries)
        
        if harmony_notes:
            harmony_notes.sort(key=lambda x: x.freq)
            player.selected_entries = harmony_notes
            player._map_to_midi_keys()
            
            # 使用最佳乐器演奏最终和谐
            player.load_instrument(InstrumentType.CHOIR)
            enhanced_player.setup_reverb_and_chorus(0.9, 0.4)
            enhanced_player.set_expression_controls(player.current_channel, 'warm')
            
            print(f"五行代表音符: {[e.key_short for e in harmony_notes]}")
            print(f"频率 (Hz): {[f'{e.freq:.1f}' for e in harmony_notes]}")
            
            # 开启延音踏板
            enhanced_player.sustain_pedal(player.current_channel, True)
            
            # 琶音演奏
            print("♪ 五行琶音...")
            for i, (midi_key, entry) in enumerate(player.midi_mapping.items()):
                velocity = 85 + i * 8  # 逐渐增强
                player.fluidsynth.fluid_synth_noteon(
                    player.synth, player.current_channel, midi_key, velocity
                )
                print(f"  {entry.key_short} ({entry.freq:.1f} Hz)")
                time.sleep(0.8)
            
            time.sleep(1.0)
            
            # 和弦共鸣
            print("♪ 和谐共鸣...")
            for midi_key, entry in player.midi_mapping.items():
                player.fluidsynth.fluid_synth_noteon(
                    player.synth, player.current_channel, midi_key, 90
                )
            
            time.sleep(4.0)  # 保持和弦4秒
            
            # 渐弱结束
            for midi_key in player.midi_mapping:
                player.fluidsynth.fluid_synth_noteoff(
                    player.synth, player.current_channel, midi_key
                )
            
            enhanced_player.sustain_pedal(player.current_channel, False)
        
        print(f"\n✨ 增强演奏完成！")
        
    except FileNotFoundError as e:
        print(f"❌ SoundFont文件未找到: {e}")
        print("💡 请下载推荐的高质量SoundFont文件")
    except Exception as e:
        print(f"❌ 演奏过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()