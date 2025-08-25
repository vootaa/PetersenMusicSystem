#!/usr/bin/env python3
"""
Steinway钢琴可调参数测试

使用命令行参数调节Petersen音阶参数，寻找最佳的音响效果。
增加倍频和弦功能，探索更丰富的和声效果。

用法:
    python steinway_adjustable_test.py --f_base 20.0 --delta_theta 4.8
    python steinway_adjustable_test.py --f_base 27.5 --delta_theta 3.6
    python steinway_adjustable_test.py --help

参数说明:
    --f_base: 基础频率 (默认: 20.0 Hz)
    --delta_theta: 角度增量 (默认: 4.8 度)
    --soundfont: SoundFont文件路径
    --preset: 默认音效预设
"""

import argparse
import sys
from PetersenFluidSynth import create_player, InstrumentType
from PetersenScale import ELEMENTS_CN
import ctypes
import time
import math

class AdjustableSteinwayPlayer:
    """可调参数Steinway测试播放器"""
    
    def __init__(self, f_base=20.0, delta_theta=4.8, soundfont_path="../Soundfonts/steinway_concert_piano.sf2"):
        print(f"🎹 参数设置:")
        print(f"   基础频率 (F_base): {f_base} Hz")
        print(f"   角度增量 (delta_theta): {delta_theta} 度")
        print(f"   SoundFont: {soundfont_path}")
        
        # 使用自定义参数创建播放器
        self.player = create_player(
            soundfont_path=soundfont_path,
            F_base=f_base,
            delta_theta=delta_theta
        )
        self.f_base = f_base
        self.delta_theta = delta_theta
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
    
    def apply_effect_preset(self, preset_name="concert"):
        """应用音效预设（简化版）"""
        presets = {
            "dry": {"reverb": 0.0, "chorus": 0.0, "brightness": 127},
            "room": {"reverb": 0.4, "chorus": 0.1, "brightness": 110},
            "hall": {"reverb": 0.6, "chorus": 0.2, "brightness": 105},
            "concert": {"reverb": 0.7, "chorus": 0.3, "brightness": 115},
            "cathedral": {"reverb": 0.9, "chorus": 0.2, "brightness": 95},
            "warm": {"reverb": 0.5, "chorus": 0.4, "brightness": 85},
            "bright": {"reverb": 0.3, "chorus": 0.1, "brightness": 127}
        }
        
        if preset_name not in presets:
            preset_name = "concert"
        
        preset = presets[preset_name]
        
        # 设置混响和合唱
        if self.has_builtin_effects:
            self.player.fluidsynth.fluid_synth_set_reverb(
                self.player.synth, preset["reverb"], 0.4, 0.6, 0.8
            )
            self.player.fluidsynth.fluid_synth_set_chorus(
                self.player.synth, 2, preset["chorus"], 1.0, 4.0, 0
            )
        
        # 设置亮度
        channel = self.player.current_channel
        self.player.fluidsynth.fluid_synth_cc(
            self.player.synth, channel, 1, preset["brightness"]
        )
        
        print(f"✓ 音效预设: {preset_name} (混响:{preset['reverb']:.1f}, 合唱:{preset['chorus']:.1f}, 亮度:{preset['brightness']})")
    
    def find_harmonic_series(self, base_entry, max_harmonics=8):
        """寻找基音的倍频谐波"""
        harmonics = [base_entry]  # 基音
        base_freq = base_entry.freq
        
        # 寻找倍频（2倍、3倍、4倍等）
        for harmonic_num in range(2, max_harmonics + 1):
            target_freq = base_freq * harmonic_num
            
            # 在音阶中寻找最接近的频率
            closest_entry = None
            min_ratio_error = float('inf')
            
            for entry in self.player.all_entries:
                if entry.freq > target_freq * 0.95 and entry.freq < target_freq * 1.05:  # 5%容差
                    ratio_error = abs(entry.freq / target_freq - 1.0)
                    if ratio_error < min_ratio_error:
                        min_ratio_error = ratio_error
                        closest_entry = entry
            
            if closest_entry:
                harmonics.append(closest_entry)
                print(f"      {harmonic_num}倍频: {closest_entry.key_short} ({closest_entry.freq:.1f}Hz, 误差:{min_ratio_error*100:.1f}%)")
        
        return harmonics
    
    def find_golden_ratio_chord(self, base_entry, max_notes=6):
        """寻找基于黄金比例的和弦"""
        phi = (1 + 5**0.5) / 2.0  # 黄金比例
        chord = [base_entry]
        base_freq = base_entry.freq
        
        # 寻找黄金比例倍数的音符
        for i in range(1, max_notes):
            target_freq = base_freq * (phi ** i)
            
            # 寻找最接近的音符
            closest_entry = None
            min_freq_error = float('inf')
            
            for entry in self.player.all_entries:
                freq_error = abs(entry.freq - target_freq)
                if freq_error < min_freq_error and entry.freq > base_freq:
                    min_freq_error = freq_error
                    closest_entry = entry
            
            if closest_entry and closest_entry not in chord:
                chord.append(closest_entry)
                ratio = closest_entry.freq / base_freq
                print(f"      φ^{i}: {closest_entry.key_short} ({closest_entry.freq:.1f}Hz, 比例:{ratio:.3f})")
        
        return chord

def analyze_scale_parameters(f_base, delta_theta):
    """分析音阶参数的特性"""
    phi = (1 + 5**0.5) / 2.0
    
    print(f"\n📊 参数分析:")
    print(f"   基础频率: {f_base} Hz")
    print(f"   角度增量: {delta_theta} 度")
    print(f"   每音区倍数: φ = {phi:.6f}")
    print(f"   音区频率比: {phi:.3f} : 1")
    
    # 计算一些关键频率
    key_freqs = []
    for n in range(3, 11):
        freq = f_base * (phi ** n)
        key_freqs.append(freq)
    
    print(f"   音区3-10频率范围: {key_freqs[0]:.1f} - {key_freqs[-1]:.1f} Hz")
    
    # 分析与12平均律的偏差
    a4_target = 440.0  # A4标准音高
    # 寻找最接近A4的音符
    closest_ratio = min(key_freqs, key=lambda x: abs(x - a4_target)) / a4_target
    cents_deviation = 1200 * math.log2(closest_ratio)
    print(f"   与A4偏差: {cents_deviation:.1f} 音分")
    
    return key_freqs

def main():
    """主函数"""
    # 命令行参数解析
    parser = argparse.ArgumentParser(
        description="Steinway钢琴可调参数测试 - 探索不同Petersen音阶参数的音响效果",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
    # 使用默认参数
    python steinway_adjustable_test.py
    
    # 调整基础频率使其更接近钢琴最低音
    python steinway_adjustable_test.py --f_base 27.5 --delta_theta 4.8
    
    # 使用更小的角度增量获得更紧密的音程
    python steinway_adjustable_test.py --f_base 20.0 --delta_theta 3.6
    
    # 指定不同的SoundFont和音效
    python steinway_adjustable_test.py --f_base 30.0 --soundfont ../Soundfonts/FluidR3_GM.sf2 --preset hall
        """
    )
    
    parser.add_argument('--f_base', type=float, default=20.0,
                       help='基础频率 (Hz, 默认: 20.0)')
    parser.add_argument('--delta_theta', type=float, default=4.8,
                       help='角度增量 (度, 默认: 4.8)')
    parser.add_argument('--soundfont', type=str, 
                       default="../Soundfonts/steinway_concert_piano.sf2",
                       help='SoundFont文件路径')
    parser.add_argument('--preset', type=str, default="concert",
                       choices=['dry', 'room', 'hall', 'concert', 'cathedral', 'warm', 'bright'],
                       help='默认音效预设')
    
    args = parser.parse_args()
    
    print("=== Steinway钢琴可调参数测试 ===\n")
    
    # 分析参数
    analyze_scale_parameters(args.f_base, args.delta_theta)
    
    try:
        # 创建可调参数播放器
        steinway = AdjustableSteinwayPlayer(
            f_base=args.f_base,
            delta_theta=args.delta_theta,
            soundfont_path=args.soundfont
        )
        player = steinway.player
        
        print(f"\n✓ Steinway播放器创建成功")
        
        # 选择完整音阶
        target_zones = list(range(3, 11))
        full_scale = player.select_frequencies(zones=target_zones, max_keys=120)
        full_scale.sort(key=lambda x: x.freq)
        
        print(f"✓ 生成音阶: {len(full_scale)} 个音符")
        freqs = [e.freq for e in full_scale]
        print(f"   频率范围: {min(freqs):.1f} - {max(freqs):.1f} Hz")
        
        # 加载钢琴并设置音效
        player.load_instrument(InstrumentType.PIANO)
        steinway.apply_effect_preset(args.preset)
        time.sleep(1.0)
        
        print(f"\n🎼 开始测试当前参数下的音响效果")
        print(f"═══════════════════════════════════════════════════════════════")
        
        # 测试1: 快速音阶演奏（判断"调弦"效果）
        print(f"\n📈 测试1: 完整音阶演奏 (评估整体调音效果)")
        print(f"   播放所有{len(full_scale)}个音符，从低到高...")
        
        for i, entry in enumerate(full_scale):
            midi_key = i
            if midi_key in player.midi_mapping:
                velocity = 65 + (i % 30)  # 轻微力度变化
                
                player.fluidsynth.fluid_synth_noteon(
                    player.synth, player.current_channel, midi_key, velocity
                )
                
                # 显示进度
                if i % 20 == 0:
                    print(f"   音区{entry.n}: {entry.key_short} ({entry.freq:.0f}Hz)")
                
                time.sleep(0.12)  # 快速播放
                
                player.fluidsynth.fluid_synth_noteoff(
                    player.synth, player.current_channel, midi_key
                )
                
                time.sleep(0.03)
        
        print(f"   ✓ 完整音阶演奏完成")
        time.sleep(1.5)
        
        # 测试2: 倍频和弦测试
        print(f"\n🎶 测试2: 倍频和弦 (验证谐波和谐性)")
        
        # 选择几个基音测试倍频
        base_note_indices = [15, 35, 55]  # 低音、中音、高音
        
        for base_idx in base_note_indices:
            if base_idx < len(full_scale):
                base_entry = full_scale[base_idx]
                print(f"\n   基音: {base_entry.key_short} ({base_entry.freq:.1f}Hz)")
                
                # 寻找倍频谐波
                harmonics = steinway.find_harmonic_series(base_entry, max_harmonics=6)
                
                if len(harmonics) > 1:
                    print(f"   找到 {len(harmonics)} 个谐波:")
                    
                    # 播放倍频和弦
                    print(f"   ♪ 倍频琶音...")
                    for harmonic in harmonics:
                        midi_key = full_scale.index(harmonic)
                        if midi_key in player.midi_mapping:
                            player.fluidsynth.fluid_synth_noteon(
                                player.synth, player.current_channel, midi_key, 75
                            )
                            time.sleep(0.5)
                    
                    time.sleep(1.0)
                    
                    # 和弦演奏
                    print(f"   ♪ 倍频和弦...")
                    for harmonic in harmonics:
                        midi_key = full_scale.index(harmonic)
                        if midi_key in player.midi_mapping:
                            player.fluidsynth.fluid_synth_noteon(
                                player.synth, player.current_channel, midi_key, 70
                            )
                    
                    time.sleep(2.0)
                    
                    # 停止和弦
                    for harmonic in harmonics:
                        midi_key = full_scale.index(harmonic)
                        if midi_key in player.midi_mapping:
                            player.fluidsynth.fluid_synth_noteoff(
                                player.synth, player.current_channel, midi_key
                            )
                    
                    time.sleep(1.0)
        
        # 测试3: 黄金比例和弦
        print(f"\n🌟 测试3: 黄金比例和弦 (验证Petersen特色)")
        
        # 选择中音区的基音
        base_entry = full_scale[40] if len(full_scale) > 40 else full_scale[len(full_scale)//2]
        print(f"\n   基音: {base_entry.key_short} ({base_entry.freq:.1f}Hz)")
        
        # 构建黄金比例和弦
        golden_chord = steinway.find_golden_ratio_chord(base_entry, max_notes=5)
        
        if len(golden_chord) > 1:
            print(f"   黄金比例和弦 ({len(golden_chord)} 音):")
            
            # 琶音演奏
            print(f"   ♪ 黄金琶音...")
            for note in golden_chord:
                midi_key = full_scale.index(note)
                if midi_key in player.midi_mapping:
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, 80
                    )
                    time.sleep(0.6)
            
            time.sleep(1.0)
            
            # 和弦演奏
            print(f"   ♪ 黄金和弦...")
            for note in golden_chord:
                midi_key = full_scale.index(note)
                if midi_key in player.midi_mapping:
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, 75
                    )
            
            time.sleep(3.0)
            
            # 停止和弦
            for note in golden_chord:
                midi_key = full_scale.index(note)
                if midi_key in player.midi_mapping:
                    player.fluidsynth.fluid_synth_noteoff(
                        player.synth, player.current_channel, midi_key
                    )
        
        # 参数评估建议
        print(f"\n📋 参数评估和建议:")
        print(f"   当前参数: F_base={args.f_base} Hz, delta_theta={args.delta_theta}°")
        print(f"   ")
        print(f"   💡 调音效果评估:")
        print(f"      - 如果音阶听起来\"失调\"，尝试调整 F_base 使其更接近钢琴标准音")
        print(f"      - 如果音程太宽，减小 delta_theta (如 3.6)")
        print(f"      - 如果音程太窄，增大 delta_theta (如 5.4)")
        print(f"   ")
        print(f"   🎯 建议尝试的参数组合:")
        print(f"      --f_base 27.5 --delta_theta 4.8  # 钢琴A0基础")
        print(f"      --f_base 32.7 --delta_theta 4.0  # 更紧密音程")
        print(f"      --f_base 20.0 --delta_theta 5.2  # 更宽广音程")
        
        print(f"\n✨ 测试完成！请尝试不同参数组合寻找最佳效果")
        
    except FileNotFoundError as e:
        print(f"❌ SoundFont文件未找到: {e}")
        print(f"💡 请检查文件路径: {args.soundfont}")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()