#!/usr/bin/env python3
"""
Petersen音阶完整音阶测试

测试8个音区(3-10)的完整Petersen音阶，验证：
1. 完整120键音阶的音高关系
2. 不同乐器的音色表现
3. 音效控制的实际效果
4. Petersen音阶的和谐特性

目标：8个音区 × 15个音符/音区 = 120个音符，覆盖完整MIDI键盘
"""

from PetersenFluidSynth import create_player, InstrumentType
from PetersenScale import ELEMENTS_CN
import ctypes
import time
import math

class FullScaleTestPlayer:
    """完整音阶测试播放器"""
    
    def __init__(self, soundfont_path="../Soundfonts/FluidR3_GM.sf2"):
        self.player = create_player(soundfont_path)
        self.setup_audio_effects()
        
    def setup_audio_effects(self):
        """设置音频效果"""
        # 添加MIDI控制器函数签名
        self.player.fluidsynth.fluid_synth_cc.restype = ctypes.c_int
        self.player.fluidsynth.fluid_synth_cc.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        
        # 尝试设置内置音效
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
    
    def set_audio_effects(self, preset="hall"):
        """设置音频效果预设"""
        presets = {
            "dry": {"reverb": 0.0, "chorus": 0.0},      # 干声
            "room": {"reverb": 0.3, "chorus": 0.1},     # 房间
            "hall": {"reverb": 0.6, "chorus": 0.2},     # 音乐厅  
            "cathedral": {"reverb": 0.9, "chorus": 0.1}, # 教堂
            "chorus": {"reverb": 0.2, "chorus": 0.6},   # 合唱
        }
        
        settings = presets.get(preset, presets["hall"])
        
        if self.has_builtin_effects:
            # 设置混响
            self.player.fluidsynth.fluid_synth_set_reverb(
                self.player.synth,
                settings["reverb"],  # room size
                0.4,                 # damping
                0.6,                 # width  
                0.8                  # level
            )
            
            # 设置合唱
            self.player.fluidsynth.fluid_synth_set_chorus(
                self.player.synth,
                3,                   # voice count
                settings["chorus"],  # level
                1.0,                # speed
                8.0,                # depth
                0                   # type (sine)
            )
            print(f"✓ 音效预设: {preset} (混响:{settings['reverb']:.1f}, 合唱:{settings['chorus']:.1f})")
        else:
            # 使用CC控制器
            channel = self.player.current_channel
            self.player.fluidsynth.fluid_synth_cc(
                self.player.synth, channel, 91, int(settings["reverb"] * 127)
            )
            self.player.fluidsynth.fluid_synth_cc(
                self.player.synth, channel, 93, int(settings["chorus"] * 127)
            )
            print(f"✓ CC音效: {preset} (混响:{int(settings['reverb']*127)}, 合唱:{int(settings['chorus']*127)})")
    
    def set_expression(self, brightness=100, resonance=64):
        """设置表现力参数"""
        channel = self.player.current_channel
        
        # 设置音色亮度
        self.player.fluidsynth.fluid_synth_cc(self.player.synth, channel, 1, brightness)
        # 设置滤波器共振
        self.player.fluidsynth.fluid_synth_cc(self.player.synth, channel, 71, resonance)
        # 设置音量
        self.player.fluidsynth.fluid_synth_cc(self.player.synth, channel, 7, 100)
        
        print(f"✓ 表现力设置: 亮度={brightness}, 共振={resonance}")

def get_test_instruments():
    """获取测试乐器列表"""
    return [
        # 乐器名称, 类型, 音效预设, 表现力设置
        ('Piano', InstrumentType.PIANO, 'room', {'brightness': 90, 'resonance': 60}),
        ('String Ensemble', InstrumentType.STRING_ENSEMBLE, 'hall', {'brightness': 100, 'resonance': 80}),
        ('Choir', InstrumentType.CHOIR, 'cathedral', {'brightness': 80, 'resonance': 70}),
        ('Synth Pad', InstrumentType.SYNTH_PAD, 'chorus', {'brightness': 110, 'resonance': 90}),
        ('Harp', InstrumentType.HARP, 'hall', {'brightness': 120, 'resonance': 50}),
    ]

def main():
    """主测试函数"""
    print("=== Petersen音阶完整音阶测试 ===\n")
    print("目标：测试8个音区(3-10)的完整120键音阶")
    print("验证：音高关系、音色表现、音效控制\n")
    
    try:
        # 创建测试播放器
        test_player = FullScaleTestPlayer()
        player = test_player.player
        
        print(f"✓ 测试播放器创建成功")
        
        # 选择完整8个音区
        target_zones = list(range(3, 11))  # [3, 4, 5, 6, 7, 8, 9, 10]
        print(f"✓ 目标音区: {target_zones}")
        
        # 选择完整音阶（所有方位、所有极性）
        full_scale = player.select_frequencies(
            zones=target_zones,
            max_keys=120  # 完整MIDI键盘范围
        )
        
        print(f"✓ 选择了完整音阶: {len(full_scale)} 个音符")
        
        if not full_scale:
            print("❌ 无法获取音阶数据")
            return
        
        # 按频率排序（从低到高）
        full_scale.sort(key=lambda x: x.freq)
        
        # 显示音阶信息
        freqs = [e.freq for e in full_scale]
        print(f"   频率范围: {min(freqs):.2f} - {max(freqs):.2f} Hz")
        print(f"   音区分布: {len(target_zones)} 个音区")
        print(f"   五行分布: {len(set(e.e for e in full_scale))} 种方位")
        print(f"   极性分布: {len(set(e.p for e in full_scale))} 种极性")
        
        # 按音区统计
        zone_counts = {}
        for entry in full_scale:
            zone_counts[entry.n] = zone_counts.get(entry.n, 0) + 1
        print(f"   每音区音符数: {zone_counts}")
        
        # 获取测试乐器
        test_instruments = get_test_instruments()
        
        print(f"\n🎼 开始完整音阶测试")
        print(f"═════════════════════════════════════════════════════════════\n")
        
        # 对每种乐器进行测试
        for inst_idx, (instrument_name, instrument_type, effect_preset, expression) in enumerate(test_instruments):
            print(f"🎹 测试乐器 {inst_idx+1}/{len(test_instruments)}: {instrument_name}")
            print(f"   音效预设: {effect_preset}")
            print(f"   表现力: {expression}")
            print(f"─────────────────────────────────────────────────────────────")
            
            # 加载乐器
            player.load_instrument(instrument_type)
            time.sleep(0.5)
            
            # 设置音效和表现力
            test_player.set_audio_effects(effect_preset)
            test_player.set_expression(**expression)
            time.sleep(0.3)
            
            # 测试1：快速音阶演奏（检验音高关系）
            print(f"\n   📈 测试1: 快速音阶演奏 (验证音高关系)")
            print(f"      播放完整音阶，从低音到高音...")
            
            for i, entry in enumerate(full_scale):
                midi_key = i
                if midi_key in player.midi_mapping:
                    # 快速播放，突出音高变化
                    velocity = 70 + (i % 20)  # 轻微的力度变化
                    
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, velocity
                    )
                    
                    # 显示进度
                    if i % 15 == 0:
                        print(f"      音区{entry.n}: {entry.key_short} ({entry.freq:.1f}Hz)", end="", flush=True)
                    elif i % 5 == 0:
                        print(".", end="", flush=True)
                    
                    time.sleep(0.15)  # 快速播放
                    
                    player.fluidsynth.fluid_synth_noteoff(
                        player.synth, player.current_channel, midi_key
                    )
                    
                    time.sleep(0.05)  # 短间隔
            
            print(" ✓")
            time.sleep(1.0)
            
            # 测试2：分音区演奏（检验音区特性）
            print(f"\n   🎵 测试2: 分音区演奏 (验证音区特性)")
            
            for zone in target_zones:
                zone_notes = [e for e in full_scale if e.n == zone]
                if not zone_notes:
                    continue
                
                print(f"      音区 {zone}: {len(zone_notes)} 个音符", end="", flush=True)
                
                # 播放该音区的所有音符
                for j, entry in enumerate(zone_notes):
                    midi_key = full_scale.index(entry)
                    if midi_key in player.midi_mapping:
                        velocity = 80
                        
                        player.fluidsynth.fluid_synth_noteon(
                            player.synth, player.current_channel, midi_key, velocity
                        )
                        time.sleep(0.3)
                        player.fluidsynth.fluid_synth_noteoff(
                            player.synth, player.current_channel, midi_key
                        )
                        time.sleep(0.1)
                
                print(" ✓")
            
            time.sleep(1.5)
            
            # 测试3：和谐音程演奏（检验Petersen音阶特性）
            print(f"\n   🎶 测试3: 和谐音程演奏 (验证Petersen特性)")
            
            # 选择代表性音符构建和谐音程
            harmony_indices = [0, 15, 30, 45, 60, 75, 90, 105]  # 间隔选择
            harmony_notes = [full_scale[i] for i in harmony_indices if i < len(full_scale)]
            
            print(f"      选择 {len(harmony_notes)} 个代表音符构建和谐:")
            for note in harmony_notes:
                print(f"        {note.key_short} ({note.freq:.1f}Hz)")
            
            # 先琶音演奏
            print(f"      ♪ 琶音演奏...")
            for i, entry in enumerate(harmony_notes):
                midi_key = full_scale.index(entry)
                if midi_key in player.midi_mapping:
                    velocity = 85 + i * 5
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, velocity
                    )
                    time.sleep(0.6)
            
            time.sleep(1.0)
            
            # 再和弦演奏
            print(f"      ♪ 和弦演奏...")
            for entry in harmony_notes:
                midi_key = full_scale.index(entry)
                if midi_key in player.midi_mapping:
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, 80
                    )
            
            time.sleep(3.0)  # 保持和弦
            
            # 停止所有音符
            for entry in harmony_notes:
                midi_key = full_scale.index(entry)
                if midi_key in player.midi_mapping:
                    player.fluidsynth.fluid_synth_noteoff(
                        player.synth, player.current_channel, midi_key
                    )
            
            print(f"\n  ✓ {instrument_name} 测试完成")
            print(f"─────────────────────────────────────────────────────────────")
            time.sleep(2.0)
        
        # 最终综合测试
        print(f"\n🌟 最终综合测试：Petersen音阶全景展示")
        print(f"═════════════════════════════════════════════════════════════")
        
        # 使用最佳乐器进行最终展示
        player.load_instrument(InstrumentType.CHOIR)
        test_player.set_audio_effects("cathedral")
        test_player.set_expression(brightness=95, resonance=75)
        
        print(f"使用 Choir + Cathedral 效果进行最终展示")
        print(f"完整音阶: {len(full_scale)} 个音符")
        
        # 慢速完整演奏，突出Petersen音阶的特殊音程关系
        print(f"♪ 完整Petersen音阶演奏 (慢速，突出音程关系)...")
        
        for i, entry in enumerate(full_scale):
            midi_key = i
            if midi_key in player.midi_mapping:
                # 计算动态力度（低音轻，高音重）
                velocity = 60 + int((i / len(full_scale)) * 40)
                
                player.fluidsynth.fluid_synth_noteon(
                    player.synth, player.current_channel, midi_key, velocity
                )
                
                # 每10个音符显示进度
                if i % 10 == 0:
                    progress = (i / len(full_scale)) * 100
                    print(f"  进度: {progress:5.1f}% - 音区{entry.n} {entry.key_short} ({entry.freq:.1f}Hz)")
                
                time.sleep(0.4)  # 慢速播放，让每个音符都能听清
                
                player.fluidsynth.fluid_synth_noteoff(
                    player.synth, player.current_channel, midi_key
                )
                
                time.sleep(0.2)
        
        print(f"\n✨ 完整音阶测试完成！")
        print(f"   总计播放: {len(full_scale)} 个音符")
        print(f"   覆盖频率: {min(freqs):.1f} - {max(freqs):.1f} Hz")
        print(f"   覆盖音区: {len(target_zones)} 个音区")
        
    except FileNotFoundError as e:
        print(f"❌ SoundFont文件未找到: {e}")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()