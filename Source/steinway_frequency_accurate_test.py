#!/usr/bin/env python3
"""
Steinway钢琴精确频率测试

解决频率映射问题，支持：
1. 精确频率播放（而非12平均律近似）
2. 八度关系测试 (φ=2)
3. 频率偏差分析和补偿
4. 真实vs近似频率对比

用法:
    python steinway_frequency_accurate_test.py --phi 2.0 --f_base 55.0
    python steinway_frequency_accurate_test.py --phi 1.618 --f_base 55.0 --accurate_freq
"""

import argparse
import sys
from PetersenFluidSynth import create_player, InstrumentType
from PetersenScale import ELEMENTS_CN
import ctypes
import time
import math

class FrequencyAccuratePlayer:
    """精确频率播放器"""
    
    def __init__(self, phi=1.618, f_base=55.0, soundfont_path="../Soundfonts/steinway_concert_piano.sf2"):
        print(f"🎹 精确频率播放器")
        print(f"   比例系数 (φ): {phi}")
        print(f"   基础频率 (F_base): {f_base} Hz")
        print(f"   SoundFont: {soundfont_path}")
        
        # 创建播放器（注意：这里仍使用原始参数生成音阶结构）
        self.player = create_player(soundfont_path=soundfont_path)
        self.phi = phi
        self.f_base = f_base
        self.setup_frequency_control()
        
    def setup_frequency_control(self):
        """设置频率控制"""
        # 弯音轮控制（用于精确调音）
        try:
            self.player.fluidsynth.fluid_synth_pitch_bend.restype = ctypes.c_int
            self.player.fluidsynth.fluid_synth_pitch_bend.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_int
            ]
            self.has_pitch_bend = True
            print("✓ 弯音轮控制已启用（精确调音）")
        except AttributeError:
            self.has_pitch_bend = False
            print("⚠️  无弯音轮控制，使用近似频率")
        
        # 音效控制
        self.player.fluidsynth.fluid_synth_cc.restype = ctypes.c_int
        self.player.fluidsynth.fluid_synth_cc.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
    
    def generate_custom_scale(self, zones=None, max_keys=120):
        """生成自定义音阶（使用指定的φ值）"""
        if zones is None:
            zones = list(range(3, 11))
        
        custom_entries = []
        
        # 为每个音区生成音符
        for n in zones:
            base_freq_for_zone = self.f_base * (self.phi ** n)
            
            # 为每个音区生成15个音符（模拟原始结构）
            for i in range(15):
                # 使用简化的频率分布
                angle_factor = i / 15.0  # 0到1之间
                freq = base_freq_for_zone * (1 + 0.5 * angle_factor)  # 简单的频率分布
                
                # 创建伪条目（简化版）
                entry = type('Entry', (), {
                    'freq': freq,
                    'n': n,
                    'e': i % 5,  # 五行循环
                    'p': (i % 3) - 1,  # 极性：-1, 0, 1
                    'key_short': f"Z{n}E{i%5}P{(i%3)-1}"
                })()
                
                custom_entries.append(entry)
                
                if len(custom_entries) >= max_keys:
                    break
            
            if len(custom_entries) >= max_keys:
                break
        
        return custom_entries[:max_keys]
    
    def find_closest_midi_note(self, target_freq):
        """找到最接近目标频率的MIDI音符"""
        # A4 = 440 Hz = MIDI 69
        a4_freq = 440.0
        a4_midi = 69
        
        # 计算目标频率对应的MIDI音符
        semitones_from_a4 = 12 * math.log2(target_freq / a4_freq)
        closest_midi = round(a4_midi + semitones_from_a4)
        
        # 限制在MIDI范围内
        closest_midi = max(0, min(127, closest_midi))
        
        # 计算该MIDI音符的标准频率
        standard_freq = a4_freq * (2 ** ((closest_midi - a4_midi) / 12))
        
        # 计算频率偏差（音分）
        cents_deviation = 1200 * math.log2(target_freq / standard_freq)
        
        return closest_midi, standard_freq, cents_deviation
    
    def play_note_accurate(self, target_freq, velocity=80, duration=1.0, use_accurate=True):
        """播放精确频率的音符"""
        midi_note, standard_freq, cents_deviation = self.find_closest_midi_note(target_freq)
        
        print(f"    目标:{target_freq:6.1f}Hz → MIDI{midi_note:3d} ({standard_freq:6.1f}Hz) 偏差:{cents_deviation:+5.1f}音分")
        
        if use_accurate and self.has_pitch_bend and abs(cents_deviation) > 5:
            # 使用弯音轮补偿频率偏差
            # 弯音轮范围通常是±200音分，8192为中心值
            pitch_bend_value = int(8192 + (cents_deviation / 200.0) * 8192)
            pitch_bend_value = max(0, min(16383, pitch_bend_value))
            
            self.player.fluidsynth.fluid_synth_pitch_bend(
                self.player.synth, self.player.current_channel, pitch_bend_value
            )
            print(f"      → 弯音轮补偿: {pitch_bend_value} (精确频率)")
        else:
            # 重置弯音轮到中心
            if self.has_pitch_bend:
                self.player.fluidsynth.fluid_synth_pitch_bend(
                    self.player.synth, self.player.current_channel, 8192
                )
        
        # 播放音符
        self.player.fluidsynth.fluid_synth_noteon(
            self.player.synth, self.player.current_channel, midi_note, velocity
        )
        
        time.sleep(duration * 0.8)
        
        self.player.fluidsynth.fluid_synth_noteoff(
            self.player.synth, self.player.current_channel, midi_note
        )
        
        # 重置弯音轮
        if self.has_pitch_bend:
            self.player.fluidsynth.fluid_synth_pitch_bend(
                self.player.synth, self.player.current_channel, 8192
            )
        
        return midi_note, cents_deviation

def test_phi_comparison():
    """对比不同φ值的效果"""
    test_configs = [
        {"phi": 2.0, "name": "八度关系", "f_base": 55.0},      # 传统八度
        {"phi": 1.618, "name": "黄金比例", "f_base": 55.0},    # 黄金比例
        {"phi": 1.5, "name": "完全五度", "f_base": 55.0},      # 完全五度近似
        {"phi": 1.414, "name": "增四度", "f_base": 55.0},      # 增四度（三全音）
    ]
    
    print(f"\n🔍 不同φ值对比测试:")
    print(f"基音: 55 Hz (A1)")
    print(f"测试5个音区的频率分布\n")
    
    for config in test_configs:
        phi = config["phi"]
        name = config["name"]
        f_base = config["f_base"]
        
        print(f"📊 {name} (φ = {phi})")
        print(f"   音区频率:")
        
        frequencies = []
        for n in range(3, 8):  # 测试5个音区
            freq = f_base * (phi ** n)
            frequencies.append(freq)
            
            # 分析与12平均律的关系
            a4_freq = 440.0
            semitones_from_a4 = 12 * math.log2(freq / a4_freq)
            closest_midi = round(69 + semitones_from_a4)
            standard_freq = a4_freq * (2 ** ((closest_midi - 69) / 12))
            cents_deviation = 1200 * math.log2(freq / standard_freq)
            
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octave = (closest_midi - 12) // 12
            note_name = note_names[closest_midi % 12] + str(octave)
            
            print(f"      音区{n}: {freq:7.1f}Hz → {note_name:>4s} ({cents_deviation:+5.1f}音分)")
        
        # 分析音程关系
        intervals = []
        for i in range(1, len(frequencies)):
            ratio = frequencies[i] / frequencies[i-1]
            intervals.append(ratio)
        
        print(f"   相邻音区比例: {[f'{r:.3f}' for r in intervals]}")
        print()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Steinway钢琴精确频率测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
    # 八度关系测试（传统音程）
    python steinway_frequency_accurate_test.py --phi 2.0 --f_base 55.0
    
    # 黄金比例测试（Petersen原始）
    python steinway_frequency_accurate_test.py --phi 1.618 --f_base 55.0
    
    # 完全五度测试
    python steinway_frequency_accurate_test.py --phi 1.5 --f_base 55.0
    
    # 精确频率vs近似频率对比
    python steinway_frequency_accurate_test.py --phi 2.0 --compare_accuracy
        """
    )
    
    parser.add_argument('--phi', type=float, default=1.618,
                       help='音区间比例系数 (默认: 1.618黄金比例)')
    parser.add_argument('--f_base', type=float, default=55.0,
                       help='基础频率 Hz (默认: 55.0, A1)')
    parser.add_argument('--soundfont', type=str,
                       default="../Soundfonts/steinway_concert_piano.sf2",
                       help='SoundFont文件路径')
    parser.add_argument('--compare_accuracy', action='store_true',
                       help='对比精确频率vs近似频率')
    parser.add_argument('--analyze_only', action='store_true',
                       help='仅分析频率，不播放声音')
    
    args = parser.parse_args()
    
    print("=== Steinway钢琴精确频率测试 ===\n")
    
    # 先进行φ值对比分析
    test_phi_comparison()
    
    if args.analyze_only:
        print("✓ 分析完成，未播放声音")
        return
    
    try:
        # 创建精确频率播放器
        freq_player = FrequencyAccuratePlayer(
            phi=args.phi,
            f_base=args.f_base,
            soundfont_path=args.soundfont
        )
        
        # 生成自定义音阶
        custom_scale = freq_player.generate_custom_scale(zones=list(range(3, 8)), max_keys=50)
        
        print(f"\n✓ 生成自定义音阶: {len(custom_scale)} 个音符")
        print(f"   φ = {args.phi}, F_base = {args.f_base} Hz")
        
        # 加载钢琴
        freq_player.player.load_instrument(InstrumentType.PIANO)
        time.sleep(1.0)
        
        print(f"\n🎼 开始精确频率测试")
        print(f"═══════════════════════════════════════════════════════════════")
        
        # 测试1: 音阶演奏对比
        if args.compare_accuracy:
            print(f"\n📊 测试1: 精确频率 vs 近似频率对比")
            
            test_notes = custom_scale[:12]  # 取前12个音符测试
            
            print(f"\n   🎵 近似频率演奏 (标准12平均律):")
            for i, entry in enumerate(test_notes):
                midi_note, cents_dev = freq_player.play_note_accurate(
                    entry.freq, velocity=75, duration=0.6, use_accurate=False
                )
                time.sleep(0.2)
            
            time.sleep(1.5)
            
            print(f"\n   🎯 精确频率演奏 (弯音轮补偿):")
            for i, entry in enumerate(test_notes):
                midi_note, cents_dev = freq_player.play_note_accurate(
                    entry.freq, velocity=75, duration=0.6, use_accurate=True
                )
                time.sleep(0.2)
        
        # 测试2: 和弦对比（八度 vs 黄金比例）
        print(f"\n🎶 测试2: 和弦音程对比")
        
        # 选择基音
        base_freq = args.f_base * (args.phi ** 4)  # 中音区
        print(f"\n   基音: {base_freq:.1f} Hz")
        
        # 构建和弦（基音 + φ^1 + φ^2 + φ^3）
        chord_freqs = []
        for i in range(4):
            freq = base_freq * (args.phi ** i)
            chord_freqs.append(freq)
        
        print(f"   和弦频率: {[f'{f:.1f}' for f in chord_freqs]} Hz")
        
        # 琶音演奏
        print(f"\n   ♪ 琶音演奏...")
        for freq in chord_freqs:
            freq_player.play_note_accurate(freq, velocity=80, duration=0.8, use_accurate=True)
            time.sleep(0.3)
        
        time.sleep(1.0)
        
        # 和弦演奏
        print(f"\n   ♪ 和弦演奏...")
        midi_notes = []
        for freq in chord_freqs:
            midi_note, standard_freq, cents_dev = freq_player.find_closest_midi_note(freq)
            midi_notes.append(midi_note)
            
            # 设置弯音轮
            if freq_player.has_pitch_bend and abs(cents_dev) > 5:
                pitch_bend = int(8192 + (cents_dev / 200.0) * 8192)
                pitch_bend = max(0, min(16383, pitch_bend))
                freq_player.player.fluidsynth.fluid_synth_pitch_bend(
                    freq_player.player.synth, freq_player.player.current_channel, pitch_bend
                )
            
            freq_player.player.fluidsynth.fluid_synth_noteon(
                freq_player.player.synth, freq_player.player.current_channel, midi_note, 75
            )
            time.sleep(0.2)
        
        time.sleep(3.0)  # 保持和弦
        
        # 停止和弦
        for midi_note in midi_notes:
            freq_player.player.fluidsynth.fluid_synth_noteoff(
                freq_player.player.synth, freq_player.player.current_channel, midi_note
            )
        
        # 重置弯音轮
        if freq_player.has_pitch_bend:
            freq_player.player.fluidsynth.fluid_synth_pitch_bend(
                freq_player.player.synth, freq_player.player.current_channel, 8192
            )
        
        # 评估和建议
        print(f"\n📋 测试评估:")
        print(f"   当前参数: φ={args.phi}, F_base={args.f_base} Hz")
        
        if args.phi == 2.0:
            print(f"   ✓ 八度关系：与12平均律完全兼容，听起来\"调好弦\"")
        elif abs(args.phi - 1.618) < 0.01:
            print(f"   ⚠️  黄金比例：独特音程，但与传统调音有偏差")
        elif abs(args.phi - 1.5) < 0.01:
            print(f"   ♪ 完全五度：接近传统和声，较为和谐")
        
        print(f"\n   💡 建议:")
        print(f"      - φ=2.0: 最接近传统钢琴调音")
        print(f"      - φ=1.5: 平衡创新与和谐")
        print(f"      - φ=1.618: 保持Petersen原始理念")
        
        print(f"\n✨ 精确频率测试完成！")
        
    except FileNotFoundError as e:
        print(f"❌ SoundFont文件未找到: {e}")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()