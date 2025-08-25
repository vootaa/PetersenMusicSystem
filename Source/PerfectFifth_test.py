#!/usr/bin/env python3
"""
Steinway钢琴完全五度专项测试 (φ = 1.5)

专门探索φ=1.5（完全五度关系）在Petersen音阶中的表现。
这个比例结合了传统和声的稳定性和Petersen系统的创新性。

特色功能：
1. 完全五度音阶的和声分析
2. 中国五声音阶风格的演奏
3. 多层次和弦构建
4. 传统与创新的融合演示
"""

import argparse
from steinway_frequency_accurate_test import FrequencyAccuratePlayer
from PetersenFluidSynth import InstrumentType
import time
import math

class PerfectFifthPlayer(FrequencyAccuratePlayer):
    """完全五度专项播放器"""
    
    def __init__(self, f_base=55.0, soundfont_path="../Soundfonts/steinway_concert_piano.sf2"):
        super().__init__(phi=1.5, f_base=f_base, soundfont_path=soundfont_path)
        print(f"🎵 完全五度音阶系统 (φ = 1.5)")
        print(f"   这是传统和声中最稳定的音程关系")
    
    def analyze_fifth_harmony(self):
        """分析完全五度的和声特性"""
        print(f"\n📊 完全五度和声分析:")
        print(f"   比例: 3:2 = 1.5")
        print(f"   音程: 完全五度 (7个半音)")
        print(f"   音分: 约702音分 (标准700音分)")
        print(f"   特性: 极其稳定，产生强烈共鸣")
        
        # 演示频率序列
        base_freq = self.f_base
        print(f"\n   频率序列示例 (基音 {base_freq} Hz):")
        
        freqs = []
        note_names = []
        for i in range(8):
            freq = base_freq * (1.5 ** i)
            freqs.append(freq)
            
            # 转换为音符名称
            a4_freq = 440.0
            semitones = 12 * math.log2(freq / a4_freq)
            midi_note = round(69 + semitones)
            octave = (midi_note - 12) // 12
            note_idx = midi_note % 12
            note_names_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            note_name = note_names_list[note_idx] + str(octave)
            note_names.append(note_name)
            
            print(f"      {i+1}: {freq:7.1f} Hz → {note_name:>4s}")
            
            if freq > 2000:  # 限制频率范围
                break
        
        return freqs[:6], note_names[:6]  # 返回前6个音符
    
    def create_pentatonic_melody(self):
        """创建五声音阶风格的旋律"""
        # 选择合适的音符构建五声音阶
        base_freq = self.f_base * (1.5 ** 4)  # 中音区开始
        
        # 构建类似五声音阶的音符选择
        melody_ratios = [1.0, 1.125, 1.25, 1.5, 1.6875, 2.0]  # 五声音阶比例近似
        melody_freqs = [base_freq * ratio for ratio in melody_ratios]
        
        print(f"\n🎶 五声音阶风格旋律:")
        print(f"   基音: {base_freq:.1f} Hz")
        print(f"   音符序列:")
        
        for i, freq in enumerate(melody_freqs):
            midi_note, standard_freq, cents_dev = self.find_closest_midi_note(freq)
            note_names_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octave = (midi_note - 12) // 12
            note_name = note_names_list[midi_note % 12] + str(octave)
            print(f"      {i+1}: {freq:6.1f} Hz → {note_name:>4s} ({cents_dev:+4.0f}音分)")
        
        return melody_freqs
    
    def create_harmonic_stack(self, base_freq, layers=4):
        """创建和声叠置"""
        stack = []
        
        # 基础和弦：基音 + 五度 + 九度 + 十三度等
        for i in range(layers):
            freq = base_freq * (1.5 ** i)
            stack.append(freq)
        
        return stack

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Steinway钢琴完全五度专项测试")
    parser.add_argument('--f_base', type=float, default=55.0, help='基础频率 (默认: 55.0 Hz)')
    parser.add_argument('--soundfont', type=str, default="../Soundfonts/steinway_concert_piano.sf2")
    
    args = parser.parse_args()
    
    print("=== Steinway钢琴完全五度专项测试 ===\n")
    print("探索φ=1.5在钢琴上的和声美学")
    
    try:
        # 创建完全五度播放器
        fifth_player = PerfectFifthPlayer(f_base=args.f_base, soundfont_path=args.soundfont)
        
        # 加载钢琴
        fifth_player.player.load_instrument(InstrumentType.PIANO)
        
        # 设置音效（温暖的音乐厅效果）
        fifth_player.player.fluidsynth.fluid_synth_cc(fifth_player.player.synth, 0, 91, 80)  # 混响
        fifth_player.player.fluidsynth.fluid_synth_cc(fifth_player.player.synth, 0, 93, 40)  # 合唱
        time.sleep(1.0)
        
        # 分析和声特性
        freqs, note_names = fifth_player.analyze_fifth_harmony()
        
        print(f"\n🎼 开始完全五度音阶演示")
        print(f"═══════════════════════════════════════════════════════════")
        
        # 演示1: 基础五度序列
        print(f"\n🎵 演示1: 纯完全五度序列")
        print(f"   从低音到高音，每个音符都是前一个的1.5倍")
        
        for i, freq in enumerate(freqs):
            print(f"   播放: {note_names[i]} ({freq:.1f} Hz)")
            fifth_player.play_note_accurate(freq, velocity=75, duration=1.0, use_accurate=True)
            time.sleep(0.5)
        
        time.sleep(1.5)
        
        # 演示2: 五声音阶风格旋律
        print(f"\n🎶 演示2: 五声音阶风格旋律")
        melody_freqs = fifth_player.create_pentatonic_melody()
        
        # 正向演奏
        print(f"   ♪ 上行旋律...")
        for freq in melody_freqs:
            fifth_player.play_note_accurate(freq, velocity=70, duration=0.8, use_accurate=True)
            time.sleep(0.3)
        
        time.sleep(1.0)
        
        # 反向演奏
        print(f"   ♪ 下行旋律...")
        for freq in reversed(melody_freqs):
            fifth_player.play_note_accurate(freq, velocity=70, duration=0.8, use_accurate=True)
            time.sleep(0.3)
        
        time.sleep(1.5)
        
        # 演示3: 多层和声叠置
        print(f"\n🏗️  演示3: 完全五度和声叠置")
        
        base_freq = args.f_base * (1.5 ** 3)  # 选择中音区基音
        harmonic_stack = fifth_player.create_harmonic_stack(base_freq, layers=5)
        
        print(f"   基音: {base_freq:.1f} Hz")
        print(f"   和声层次:")
        for i, freq in enumerate(harmonic_stack):
            midi_note, _, cents_dev = fifth_player.find_closest_midi_note(freq)
            note_names_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            note_name = note_names_list[midi_note % 12] + str((midi_note - 12) // 12)
            print(f"      层{i+1}: {freq:6.1f} Hz → {note_name} ({cents_dev:+4.0f}音分)")
        
        # 逐层添加和声
        print(f"\n   ♪ 逐层构建和声...")
        active_notes = []
        
        for i, freq in enumerate(harmonic_stack):
            print(f"      添加第{i+1}层...")
            
            midi_note, _, cents_dev = fifth_player.find_closest_midi_note(freq)
            
            # 设置弯音轮
            if fifth_player.has_pitch_bend and abs(cents_dev) > 5:
                pitch_bend = int(8192 + (cents_dev / 200.0) * 8192)
                pitch_bend = max(0, min(16383, pitch_bend))
                fifth_player.player.fluidsynth.fluid_synth_pitch_bend(
                    fifth_player.player.synth, fifth_player.player.current_channel, pitch_bend
                )
            
            # 启动音符
            velocity = 70 + i * 5  # 高层音符稍轻
            fifth_player.player.fluidsynth.fluid_synth_noteon(
                fifth_player.player.synth, fifth_player.player.current_channel, midi_note, velocity
            )
            
            active_notes.append(midi_note)
            
            # 重置弯音轮
            if fifth_player.has_pitch_bend:
                fifth_player.player.fluidsynth.fluid_synth_pitch_bend(
                    fifth_player.player.synth, fifth_player.player.current_channel, 8192
                )
            
            time.sleep(1.2)  # 让每层和声叠加效果明显
        
        print(f"   ♪ 完整和声共鸣...")
        time.sleep(4.0)  # 享受完整和声
        
        # 停止所有音符
        for midi_note in active_notes:
            fifth_player.player.fluidsynth.fluid_synth_noteoff(
                fifth_player.player.synth, fifth_player.player.current_channel, midi_note
            )
        
        time.sleep(2.0)
        
        # 演示4: 对比效果
        print(f"\n⚖️  演示4: 与其他φ值对比")
        
        test_base = args.f_base * (1.5 ** 4)
        comparison_data = [
            (1.5, "完全五度", "稳定和谐"),
            (1.618, "黄金比例", "神秘独特"),
            (2.0, "纯八度", "传统完美")
        ]
        
        for phi, name, description in comparison_data:
            print(f"\n   🎹 {name} (φ={phi}) - {description}")
            
            # 构建三和弦
            chord_freqs = [test_base * (phi ** i) for i in range(3)]
            
            print(f"      和弦频率: {[f'{f:.0f}' for f in chord_freqs]} Hz")
            
            # 琶音
            print(f"      ♪ 琶音...")
            for freq in chord_freqs:
                fifth_player.play_note_accurate(freq, velocity=75, duration=0.6, use_accurate=True)
                time.sleep(0.2)
            
            time.sleep(0.8)
            
            # 和弦
            print(f"      ♪ 和弦...")
            midi_notes = []
            for freq in chord_freqs:
                midi_note, _, cents_dev = fifth_player.find_closest_midi_note(freq)
                midi_notes.append(midi_note)
                
                if fifth_player.has_pitch_bend and abs(cents_dev) > 5:
                    pitch_bend = int(8192 + (cents_dev / 200.0) * 8192)
                    fifth_player.player.fluidsynth.fluid_synth_pitch_bend(
                        fifth_player.player.synth, fifth_player.player.current_channel, pitch_bend
                    )
                
                fifth_player.player.fluidsynth.fluid_synth_noteon(
                    fifth_player.player.synth, fifth_player.player.current_channel, midi_note, 75
                )
                
                if fifth_player.has_pitch_bend:
                    fifth_player.player.fluidsynth.fluid_synth_pitch_bend(
                        fifth_player.player.synth, fifth_player.player.current_channel, 8192
                    )
                
                time.sleep(0.1)
            
            time.sleep(2.0)
            
            # 停止和弦
            for midi_note in midi_notes:
                fifth_player.player.fluidsynth.fluid_synth_noteoff(
                    fifth_player.player.synth, fifth_player.player.current_channel, midi_note
                )
            
            time.sleep(1.0)
        
        # 总结
        print(f"\n🌟 完全五度测试总结:")
        print(f"   ✓ φ=1.5 提供了传统和声的稳定性")
        print(f"   ✓ 保持了Petersen系统的创新性")
        print(f"   ✓ 产生丰富而和谐的共鸣效果")
        print(f"   ✓ 比黄金比例更适合钢琴演奏")
        print(f"   ✓ 创造出类似东方五声音阶的美感")
        
        print(f"\n   💡 建议:")
        print(f"      - 用于冥想音乐：极其稳定和谐")
        print(f"      - 用于现代作曲：传统与创新结合")
        print(f"      - 用于治疗音乐：完全五度的治愈力")
        
        print(f"\n✨ 完全五度专项测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()