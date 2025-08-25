#!/usr/bin/env python3
"""
Steinway音色专项测试

使用高质量Steinway钢琴SoundFont测试Petersen音阶的表现力。
专注于单一乐器的多种音效预设和表现力控制。

测试目标：
1. 探索Steinway钢琴在不同音效下的表现
2. 验证Petersen音阶在专业钢琴音色下的效果
3. 测试各种表现力参数的实际影响
4. 发现最佳的音效组合
"""

from PetersenFluidSynth import create_player, InstrumentType
from PetersenScale import ELEMENTS_CN
import ctypes
import time
import math

class SteinwayTestPlayer:
    """Steinway钢琴专项测试播放器"""
    
    def __init__(self, soundfont_path="../Soundfonts/steinway_concert_piano.sf2"):
        print(f"🎹 加载Steinway音色: {soundfont_path}")
        self.player = create_player(soundfont_path)
        self.setup_audio_controls()
        
    def setup_audio_controls(self):
        """设置音频控制"""
        # MIDI控制器
        self.player.fluidsynth.fluid_synth_cc.restype = ctypes.c_int
        self.player.fluidsynth.fluid_synth_cc.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        
        # 内置音效
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
            print("✓ 内置音效控制已启用")
        except AttributeError:
            self.has_builtin_effects = False
            print("⚠️  使用CC控制器模拟音效")
    
    def apply_effect_preset(self, preset_name):
        """应用音效预设"""
        presets = {
            # 基础音效
            "dry": {
                "name": "干声 (无音效)",
                "reverb": {"room": 0.0, "damp": 0.0, "width": 0.0, "level": 0.0},
                "chorus": {"voices": 0, "level": 0.0, "speed": 1.0, "depth": 0.0},
                "expression": {"brightness": 127, "resonance": 64, "attack": 64, "release": 64}
            },
            
            # 房间环境
            "intimate": {
                "name": "私密空间 (小房间)",
                "reverb": {"room": 0.2, "damp": 0.7, "width": 0.3, "level": 0.4},
                "chorus": {"voices": 0, "level": 0.0, "speed": 1.0, "depth": 0.0},
                "expression": {"brightness": 100, "resonance": 80, "attack": 70, "release": 90}
            },
            
            "livingroom": {
                "name": "客厅 (中等房间)",
                "reverb": {"room": 0.4, "damp": 0.5, "width": 0.5, "level": 0.5},
                "chorus": {"voices": 1, "level": 0.1, "speed": 0.8, "depth": 2.0},
                "expression": {"brightness": 110, "resonance": 70, "attack": 60, "release": 80}
            },
            
            "studio": {
                "name": "录音室 (专业环境)",
                "reverb": {"room": 0.3, "damp": 0.4, "width": 0.8, "level": 0.6},
                "chorus": {"voices": 2, "level": 0.2, "speed": 1.2, "depth": 3.0},
                "expression": {"brightness": 115, "resonance": 75, "attack": 50, "release": 70}
            },
            
            # 演出场所
            "recital": {
                "name": "独奏厅 (小型音乐厅)",
                "reverb": {"room": 0.6, "damp": 0.3, "width": 0.7, "level": 0.7},
                "chorus": {"voices": 1, "level": 0.15, "speed": 0.9, "depth": 2.5},
                "expression": {"brightness": 105, "resonance": 85, "attack": 55, "release": 85}
            },
            
            "concert": {
                "name": "音乐厅 (大型演出厅)",
                "reverb": {"room": 0.8, "damp": 0.2, "width": 0.9, "level": 0.8},
                "chorus": {"voices": 2, "level": 0.25, "speed": 1.0, "depth": 4.0},
                "expression": {"brightness": 120, "resonance": 60, "attack": 45, "release": 75}
            },
            
            "cathedral": {
                "name": "大教堂 (宏伟空间)",
                "reverb": {"room": 1.0, "damp": 0.1, "width": 1.0, "level": 0.9},
                "chorus": {"voices": 3, "level": 0.2, "speed": 0.7, "depth": 5.0},
                "expression": {"brightness": 95, "resonance": 90, "attack": 80, "release": 110}
            },
            
            # 特殊效果
            "warm": {
                "name": "温暖音色 (暖色调)",
                "reverb": {"room": 0.4, "damp": 0.6, "width": 0.6, "level": 0.5},
                "chorus": {"voices": 2, "level": 0.3, "speed": 0.6, "depth": 3.5},
                "expression": {"brightness": 80, "resonance": 95, "attack": 85, "release": 100}
            },
            
            "bright": {
                "name": "明亮音色 (清晰通透)",
                "reverb": {"room": 0.3, "damp": 0.2, "width": 0.4, "level": 0.4},
                "chorus": {"voices": 1, "level": 0.4, "speed": 1.5, "depth": 2.0},
                "expression": {"brightness": 127, "resonance": 40, "attack": 30, "release": 50}
            },
            
            "dreamy": {
                "name": "梦幻音色 (飘渺感)",
                "reverb": {"room": 0.7, "damp": 0.1, "width": 0.8, "level": 0.8},
                "chorus": {"voices": 4, "level": 0.6, "speed": 0.5, "depth": 8.0},
                "expression": {"brightness": 70, "resonance": 100, "attack": 100, "release": 127}
            },
            
            "percussive": {
                "name": "打击音色 (强音头)",
                "reverb": {"room": 0.2, "damp": 0.8, "width": 0.3, "level": 0.3},
                "chorus": {"voices": 0, "level": 0.0, "speed": 1.0, "depth": 0.0},
                "expression": {"brightness": 127, "resonance": 30, "attack": 10, "release": 40}
            },
            
            "legato": {
                "name": "连音音色 (流畅连接)",
                "reverb": {"room": 0.5, "damp": 0.4, "width": 0.7, "level": 0.6},
                "chorus": {"voices": 2, "level": 0.35, "speed": 0.8, "depth": 4.5},
                "expression": {"brightness": 90, "resonance": 80, "attack": 90, "release": 110}
            }
        }
        
        if preset_name not in presets:
            print(f"❌ 未知预设: {preset_name}")
            return
        
        preset = presets[preset_name]
        print(f"\n🎨 应用音效预设: {preset['name']}")
        
        # 设置混响
        if self.has_builtin_effects:
            rev = preset["reverb"]
            self.player.fluidsynth.fluid_synth_set_reverb(
                self.player.synth, rev["room"], rev["damp"], rev["width"], rev["level"]
            )
            print(f"   混响: 房间={rev['room']:.1f}, 阻尼={rev['damp']:.1f}, 宽度={rev['width']:.1f}, 电平={rev['level']:.1f}")
        
        # 设置合唱
        if self.has_builtin_effects:
            cho = preset["chorus"]
            self.player.fluidsynth.fluid_synth_set_chorus(
                self.player.synth, cho["voices"], cho["level"], cho["speed"], cho["depth"], 0
            )
            print(f"   合唱: 声部={cho['voices']}, 电平={cho['level']:.1f}, 速度={cho['speed']:.1f}, 深度={cho['depth']:.1f}")
        
        # 设置表现力参数
        channel = self.player.current_channel
        expr = preset["expression"]
        
        self.player.fluidsynth.fluid_synth_cc(self.player.synth, channel, 1, expr["brightness"])   # 调制轮(亮度)
        self.player.fluidsynth.fluid_synth_cc(self.player.synth, channel, 71, expr["resonance"])   # 滤波器共振
        self.player.fluidsynth.fluid_synth_cc(self.player.synth, channel, 73, expr["attack"])      # 音头时间
        self.player.fluidsynth.fluid_synth_cc(self.player.synth, channel, 72, expr["release"])     # 释放时间
        self.player.fluidsynth.fluid_synth_cc(self.player.synth, channel, 7, 110)                  # 主音量
        
        print(f"   表现力: 亮度={expr['brightness']}, 共振={expr['resonance']}, 音头={expr['attack']}, 释放={expr['release']}")
        
        return preset["name"]

def main():
    """主测试函数"""
    print("=== Steinway钢琴专项音效测试 ===\n")
    print("使用高质量Steinway Concert Piano SoundFont")
    print("测试多种音效预设在Petersen音阶上的表现\n")
    
    try:
        # 创建Steinway测试播放器
        steinway = SteinwayTestPlayer()
        player = steinway.player
        
        print(f"✓ Steinway钢琴加载成功")
        
        # 选择完整音阶
        target_zones = list(range(3, 11))  # 8个音区
        full_scale = player.select_frequencies(zones=target_zones, max_keys=120)
        full_scale.sort(key=lambda x: x.freq)
        
        print(f"✓ 加载完整音阶: {len(full_scale)} 个音符")
        freqs = [e.freq for e in full_scale]
        print(f"   频率范围: {min(freqs):.1f} - {max(freqs):.1f} Hz")
        
        # 加载钢琴音色
        player.load_instrument(InstrumentType.PIANO)
        time.sleep(1.0)
        
        # 音效预设列表
        effect_presets = [
            "dry", "intimate", "livingroom", "studio", 
            "recital", "concert", "cathedral",
            "warm", "bright", "dreamy", "percussive", "legato"
        ]
        
        print(f"\n🎼 开始Steinway音效测试")
        print(f"   总计 {len(effect_presets)} 种音效预设")
        print(f"═══════════════════════════════════════════════════════════════════════\n")
        
        # 为每种音效预设进行测试
        for preset_idx, preset_name in enumerate(effect_presets):
            print(f"🎹 测试 {preset_idx+1}/{len(effect_presets)}")
            
            # 应用音效预设
            preset_display_name = steinway.apply_effect_preset(preset_name)
            time.sleep(1.0)  # 让音效设置生效
            
            # 测试1: 音阶片段演奏（快速验证音效）
            print(f"\n   📈 快速音阶片段 (验证音效特征)")
            
            # 选择代表性音符：低音、中音、高音各几个
            test_indices = [0, 8, 16, 30, 45, 60, 75, 90, 105, len(full_scale)-1]
            test_notes = [full_scale[i] for i in test_indices if i < len(full_scale)]
            
            print(f"      播放 {len(test_notes)} 个代表音符...")
            for i, entry in enumerate(test_notes):
                midi_key = full_scale.index(entry)
                if midi_key in player.midi_mapping:
                    velocity = 70 + (i * 5)  # 逐渐增强
                    
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, velocity
                    )
                    
                    print(f"        {entry.key_short} ({entry.freq:.0f}Hz)", end="", flush=True)
                    time.sleep(0.6)
                    
                    player.fluidsynth.fluid_synth_noteoff(
                        player.synth, player.current_channel, midi_key
                    )
                    
                    time.sleep(0.3)
                    print(" ♪")
            
            # 测试2: 和弦演奏（验证音效在和谐音程上的表现）
            print(f"\n   🎶 和弦演奏 (验证音效和谐性)")
            
            # 选择Petersen音阶的和谐音程
            harmony_indices = [10, 25, 40, 55, 70]  # 黄金比例间隔
            harmony_notes = [full_scale[i] for i in harmony_indices if i < len(full_scale)]
            
            print(f"      构建 {len(harmony_notes)} 音和弦:")
            for note in harmony_notes:
                print(f"        {note.key_short} ({note.freq:.1f}Hz) - {ELEMENTS_CN[note.e]}")
            
            # 琶音演奏
            print(f"      ♪ 琶音演奏...")
            for i, entry in enumerate(harmony_notes):
                midi_key = full_scale.index(entry)
                if midi_key in player.midi_mapping:
                    velocity = 75 + i * 8
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, velocity
                    )
                    time.sleep(0.8)
            
            time.sleep(1.0)
            
            # 和弦演奏
            print(f"      ♪ 和弦演奏...")
            for entry in harmony_notes:
                midi_key = full_scale.index(entry)
                if midi_key in player.midi_mapping:
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, 82
                    )
            
            time.sleep(2.5)  # 保持和弦，感受音效
            
            # 停止和弦
            for entry in harmony_notes:
                midi_key = full_scale.index(entry)
                if midi_key in player.midi_mapping:
                    player.fluidsynth.fluid_synth_noteoff(
                        player.synth, player.current_channel, midi_key
                    )
            
            # 测试3: 动态演奏（验证音效的表现力）
            print(f"\n   🎭 动态表现演奏 (验证表现力)")
            
            # 选择一个八度的音符进行动态演奏
            octave_start = 40
            octave_notes = full_scale[octave_start:octave_start+12] if octave_start+12 <= len(full_scale) else full_scale[octave_start:octave_start+8]
            
            print(f"      动态演奏 {len(octave_notes)} 个音符 (pp到ff)...")
            
            # 从很轻到很重的力度变化
            for i, entry in enumerate(octave_notes):
                midi_key = full_scale.index(entry)
                if midi_key in player.midi_mapping:
                    # 力度从30到120的动态变化
                    velocity = 30 + int((i / (len(octave_notes) - 1)) * 90)
                    
                    # 添加踏板效果（延音踏板）
                    if i == 0:
                        player.fluidsynth.fluid_synth_cc(player.synth, player.current_channel, 64, 127)
                    
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, velocity
                    )
                    
                    dynamic_marks = ["pp", "p", "mp", "mf", "f", "ff"]
                    dynamic = dynamic_marks[min(i * len(dynamic_marks) // len(octave_notes), len(dynamic_marks)-1)]
                    print(f"        {entry.key_short} {dynamic} (v={velocity})")
                    
                    time.sleep(0.7)
                    
                    player.fluidsynth.fluid_synth_noteoff(
                        player.synth, player.current_channel, midi_key
                    )
                    
                    time.sleep(0.4)
                    
                    # 释放踏板
                    if i == len(octave_notes) - 1:
                        player.fluidsynth.fluid_synth_cc(player.synth, player.current_channel, 64, 0)
            
            print(f"\n  ✓ {preset_display_name} 测试完成")
            print(f"─────────────────────────────────────────────────────────────────────")
            time.sleep(2.0)  # 预设间暂停
        
        # 最终对比演示
        print(f"\n🌟 最终对比演示")
        print(f"═══════════════════════════════════════════════════════════════════════")
        print(f"使用3种对比鲜明的音效演奏同一段Petersen音阶片段\n")
        
        # 选择一段优美的音阶片段
        demo_indices = list(range(20, 35))  # 中音区的15个音符
        demo_notes = [full_scale[i] for i in demo_indices if i < len(full_scale)]
        
        print(f"演示片段: {len(demo_notes)} 个音符")
        print(f"音符序列: {' '.join([n.key_short for n in demo_notes])}")
        
        # 三种对比音效
        comparison_presets = ["dry", "concert", "dreamy"]
        
        for preset in comparison_presets:
            print(f"\n🎹 {preset.upper()} 音效演示:")
            steinway.apply_effect_preset(preset)
            time.sleep(0.8)
            
            print(f"   ♪ 演奏中...", end="", flush=True)
            
            for i, entry in enumerate(demo_notes):
                midi_key = full_scale.index(entry)
                if midi_key in player.midi_mapping:
                    # 优美的力度曲线
                    velocity = 65 + int(20 * math.sin(i * math.pi / len(demo_notes)))
                    
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, velocity
                    )
                    
                    if i % 3 == 0:
                        print(".", end="", flush=True)
                    
                    time.sleep(0.5)
                    
                    player.fluidsynth.fluid_synth_noteoff(
                        player.synth, player.current_channel, midi_key
                    )
                    
                    time.sleep(0.2)
            
            print(" ✓")
            time.sleep(1.5)
        
        print(f"\n✨ Steinway钢琴音效测试完成！")
        print(f"   测试了 {len(effect_presets)} 种音效预设")
        print(f"   展示了Steinway钢琴在Petersen音阶上的丰富表现力")
        print(f"   建议根据音乐风格选择合适的音效预设")
        
    except FileNotFoundError as e:
        print(f"❌ Steinway SoundFont文件未找到: {e}")
        print(f"💡 请确保 steinway_concert_piano.sf2 文件位于正确路径")
        print(f"   可以尝试修改 soundfont_path 参数")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()