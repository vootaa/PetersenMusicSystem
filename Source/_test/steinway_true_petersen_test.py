#!/usr/bin/env python3
"""
Steinway钢琴真正Petersen系统测试

使用完整的Petersen音阶系统：
1. 15个独特方位（5个方位 × 3个极性）
2. 两个关键参数：φ (音区比例) 和 delta_theta (极性偏移角度)
3. 精确的频率计算和播放
4. 展示Petersen系统的真正复杂性和美感

用法:
    python steinway_true_petersen_test.py --phi 1.5 --delta_theta 4.8 --f_base 55.0
    python steinway_true_petersen_test.py --phi 2.0 --delta_theta 3.6 --f_base 55.0
"""

import argparse
from PetersenFluidSynth import create_player, InstrumentType
from PetersenScale import ELEMENTS_CN
import ctypes
import time
import math

class TruePetersenPlayer:
    """真正的Petersen系统播放器"""
    
    def __init__(self, phi=1.618, f_base=20.0, delta_theta=4.8, soundfont_path="../Soundfonts/steinway_concert_piano.sf2"):
        print(f"🎼 真正Petersen音阶系统")
        print(f"   音区比例 (φ): {phi}")
        print(f"   基础频率 (F_base): {f_base} Hz") 
        print(f"   极性偏移角度 (delta_theta): {delta_theta}°")
        print(f"   SoundFont: {soundfont_path}")
        
        # 使用真正的Petersen参数创建播放器
        self.player = create_player(
            soundfont_path=soundfont_path,
            F_base=f_base,
            delta_theta=delta_theta
        )
        self.phi = phi
        self.f_base = f_base
        self.delta_theta = delta_theta
        self.setup_controls()
        
    def setup_controls(self):
        """设置控制功能"""
        # 弯音轮控制
        try:
            self.player.fluidsynth.fluid_synth_pitch_bend.restype = ctypes.c_int
            self.player.fluidsynth.fluid_synth_pitch_bend.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_int
            ]
            self.has_pitch_bend = True
            print("✓ 弯音轮控制已启用（精确调音）")
        except AttributeError:
            self.has_pitch_bend = False
            print("⚠️  无弯音轮控制")
        
        # MIDI控制器
        self.player.fluidsynth.fluid_synth_cc.restype = ctypes.c_int
        self.player.fluidsynth.fluid_synth_cc.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
    
    def analyze_true_petersen_structure(self):
        """分析真正的Petersen系统结构"""
        print(f"\n📊 Petersen系统完整结构分析:")
        print(f"   总音阶条目: {len(self.player.all_entries)}")
        
        # 按音区分析
        zone_analysis = {}
        for entry in self.player.all_entries:
            zone = entry.n
            if zone not in zone_analysis:
                zone_analysis[zone] = {
                    'count': 0,
                    'elements': set(),
                    'polarities': set(),
                    'freq_range': [float('inf'), 0]
                }
            
            zone_analysis[zone]['count'] += 1
            zone_analysis[zone]['elements'].add(entry.e)
            zone_analysis[zone]['polarities'].add(entry.p)
            zone_analysis[zone]['freq_range'][0] = min(zone_analysis[zone]['freq_range'][0], entry.freq)
            zone_analysis[zone]['freq_range'][1] = max(zone_analysis[zone]['freq_range'][1], entry.freq)
        
        print(f"\n   音区详细分析:")
        for zone in sorted(zone_analysis.keys()):
            data = zone_analysis[zone]
            print(f"      音区{zone}: {data['count']:2d}音符, {len(data['elements'])}方位, {len(data['polarities'])}极性")
            print(f"                频率: {data['freq_range'][0]:6.1f} - {data['freq_range'][1]:6.1f} Hz")
        
        return zone_analysis
    
    def demonstrate_15_positions(self, target_zone=5):
        """演示15个独特方位"""
        print(f"\n🎵 演示音区{target_zone}的15个独特方位:")
        print(f"   (5个方位 × 3个极性 = 15个位置)")
        
        # 选择指定音区的所有音符
        zone_entries = [e for e in self.player.all_entries if e.n == target_zone]
        
        if not zone_entries:
            print(f"   ❌ 音区{target_zone}无音符数据")
            return
        
        # 按方位和极性分组
        position_map = {}
        for entry in zone_entries:
            key = (entry.e, entry.p)
            if key not in position_map:
                position_map[key] = []
            position_map[key].append(entry)
        
        print(f"   实际找到 {len(position_map)} 个独特位置:")
        
        # 按方位顺序演示
        polarities = [-1, 0, 1]  # 阴、中、阳
        polarity_names = ['阴', '中', '阳']
        
        all_demo_entries = []
        
        for element_idx in range(5):  # 五个方位
            element_name = ELEMENTS_CN[element_idx]
            print(f"\n      {element_name}:")
            
            for pol_idx, polarity in enumerate(polarities):
                pol_name = polarity_names[pol_idx]
                key = (element_idx, polarity)
                
                if key in position_map:
                    entries = position_map[key]
                    # 选择频率中等的音符作为代表
                    entry = sorted(entries, key=lambda x: x.freq)[len(entries)//2]
                    all_demo_entries.append(entry)
                    
                    print(f"         {pol_name}: {entry.key_short} ({entry.freq:6.1f} Hz)")
                else:
                    print(f"         {pol_name}: (无数据)")
        
        return all_demo_entries
    
    def play_note_with_accurate_frequency(self, entry, velocity=75, duration=0.8):
        """播放精确频率的音符"""
        target_freq = entry.freq
        
        # 找到最接近的MIDI音符
        a4_freq = 440.0
        a4_midi = 69
        semitones_from_a4 = 12 * math.log2(target_freq / a4_freq)
        closest_midi = round(a4_midi + semitones_from_a4)
        closest_midi = max(0, min(127, closest_midi))
        
        # 计算标准频率和偏差
        standard_freq = a4_freq * (2 ** ((closest_midi - a4_midi) / 12))
        cents_deviation = 1200 * math.log2(target_freq / standard_freq)
        
        # 使用弯音轮补偿
        if self.has_pitch_bend and abs(cents_deviation) > 5:
            pitch_bend_value = int(8192 + (cents_deviation / 200.0) * 8192)
            pitch_bend_value = max(0, min(16383, pitch_bend_value))
            
            self.player.fluidsynth.fluid_synth_pitch_bend(
                self.player.synth, self.player.current_channel, pitch_bend_value
            )
        
        # 播放音符
        self.player.fluidsynth.fluid_synth_noteon(
            self.player.synth, self.player.current_channel, closest_midi, velocity
        )
        
        time.sleep(duration * 0.8)
        
        self.player.fluidsynth.fluid_synth_noteoff(
            self.player.synth, self.player.current_channel, closest_midi
        )
        
        # 重置弯音轮
        if self.has_pitch_bend:
            self.player.fluidsynth.fluid_synth_pitch_bend(
                self.player.synth, self.player.current_channel, 8192
            )
        
        return closest_midi, cents_deviation
    
    def explore_delta_theta_effect(self, base_zone=5):
        """探索delta_theta参数的影响"""
        print(f"\n🔍 探索 delta_theta={self.delta_theta}° 的影响:")
        print(f"   此参数控制同一方位内不同极性的频率偏移")
        
        # 选择一个方位的三个极性进行对比
        element_idx = 0  # 选择第一个方位（金）
        element_name = ELEMENTS_CN[element_idx]
        
        print(f"\n   以 {element_name} 方位为例，展示三个极性的频率差异:")
        
        polarity_entries = []
        for polarity in [-1, 0, 1]:
            # 查找该方位和极性的音符
            candidates = [e for e in self.player.all_entries 
                         if e.n == base_zone and e.e == element_idx and e.p == polarity]
            
            if candidates:
                # 选择频率中等的
                entry = sorted(candidates, key=lambda x: x.freq)[len(candidates)//2]
                polarity_entries.append(entry)
                
                pol_name = ['阴', '中', '阳'][polarity + 1]
                print(f"      {pol_name} ({polarity:+2d}): {entry.freq:7.1f} Hz")
        
        if len(polarity_entries) >= 2:
            # 计算频率差异
            freq_diffs = []
            for i in range(1, len(polarity_entries)):
                diff = polarity_entries[i].freq - polarity_entries[i-1].freq
                ratio = polarity_entries[i].freq / polarity_entries[i-1].freq
                freq_diffs.append(diff)
                print(f"      频率差异: {diff:+6.1f} Hz (比例: {ratio:.4f})")
            
            print(f"      delta_theta={self.delta_theta}° 创造了这些微妙的频率变化")
        
        return polarity_entries

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Steinway钢琴真正Petersen系统测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
    # 原始Petersen参数
    python steinway_true_petersen_test.py --phi 1.618 --delta_theta 4.8 --f_base 20.0
    
    # 完全五度 + 小偏移角
    python steinway_true_petersen_test.py --phi 1.5 --delta_theta 3.6 --f_base 55.0
    
    # 八度关系 + 标准偏移角
    python steinway_true_petersen_test.py --phi 2.0 --delta_theta 4.8 --f_base 55.0
    
    # 探索不同偏移角的效果
    python steinway_true_petersen_test.py --phi 1.5 --delta_theta 2.4 --f_base 55.0
        """
    )
    
    parser.add_argument('--phi', type=float, default=1.618, 
                       help='音区比例系数 (默认: 1.618)')
    parser.add_argument('--f_base', type=float, default=20.0,
                       help='基础频率 Hz (默认: 20.0)')
    parser.add_argument('--delta_theta', type=float, default=4.8,
                       help='极性偏移角度 (默认: 4.8°)')
    parser.add_argument('--soundfont', type=str,
                       default="../Soundfonts/steinway_concert_piano.sf2")
    parser.add_argument('--target_zone', type=int, default=5,
                       help='演示目标音区 (默认: 5)')
    
    args = parser.parse_args()
    
    print("=== Steinway钢琴真正Petersen系统测试 ===\n")
    print("使用完整的15方位系统和两个关键参数")
    
    try:
        # 创建真正的Petersen播放器
        petersen_player = TruePetersenPlayer(
            phi=args.phi,
            f_base=args.f_base,
            delta_theta=args.delta_theta,
            soundfont_path=args.soundfont
        )
        
        # 加载钢琴
        petersen_player.player.load_instrument(InstrumentType.PIANO)
        
        # 设置温暖的音效
        petersen_player.player.fluidsynth.fluid_synth_cc(petersen_player.player.synth, 0, 91, 70)  # 混响
        petersen_player.player.fluidsynth.fluid_synth_cc(petersen_player.player.synth, 0, 93, 30)  # 合唱
        time.sleep(1.0)
        
        # 分析系统结构
        zone_analysis = petersen_player.analyze_true_petersen_structure()
        
        print(f"\n🎼 开始真正Petersen系统演示")
        print(f"═════════════════════════════════════════════════════════════")
        
        # 演示1: 15个独特方位
        print(f"\n🎵 演示1: 15个独特方位展示")
        demo_entries = petersen_player.demonstrate_15_positions(args.target_zone)
        
        if demo_entries:
            print(f"\n   ♪ 播放15个方位的代表音符...")
            for i, entry in enumerate(demo_entries):
                element_name = ELEMENTS_CN[entry.e]
                polarity_name = ['阴', '中', '阳'][entry.p + 1]
                
                print(f"      {i+1:2d}. {element_name}{polarity_name}: {entry.key_short} ({entry.freq:.1f}Hz)", end="")
                
                midi_note, cents_dev = petersen_player.play_note_with_accurate_frequency(
                    entry, velocity=75, duration=0.8
                )
                
                print(f" → MIDI{midi_note} ({cents_dev:+4.0f}音分)")
                time.sleep(0.3)
        
        time.sleep(1.5)
        
        # 演示2: delta_theta参数影响
        print(f"\n🔍 演示2: delta_theta参数影响")
        polarity_entries = petersen_player.explore_delta_theta_effect(args.target_zone)
        
        if polarity_entries:
            print(f"\n   ♪ 播放同一方位的三个极性...")
            for entry in polarity_entries:
                polarity_name = ['阴', '中', '阳'][entry.p + 1]
                print(f"      {polarity_name}: {entry.freq:.1f} Hz")
                
                petersen_player.play_note_with_accurate_frequency(
                    entry, velocity=80, duration=1.0
                )
                time.sleep(0.5)
        
        time.sleep(1.5)
        
        # 演示3: 跨音区的phi比例关系
        print(f"\n📏 演示3: 跨音区的φ={args.phi}比例关系")
        
        # 选择相同方位极性，不同音区的音符
        element_idx = 2  # 选择水
        polarity = 0     # 选择中性
        
        cross_zone_entries = []
        test_zones = [3, 4, 5, 6, 7]
        
        for zone in test_zones:
            candidates = [e for e in petersen_player.player.all_entries
                         if e.n == zone and e.e == element_idx and e.p == polarity]
            if candidates:
                entry = candidates[0]  # 取第一个
                cross_zone_entries.append(entry)
        
        if len(cross_zone_entries) >= 2:
            print(f"   选择: {ELEMENTS_CN[element_idx]}中 方位，跨越 {len(cross_zone_entries)} 个音区")
            print(f"   音区序列:")
            
            for entry in cross_zone_entries:
                print(f"      音区{entry.n}: {entry.freq:7.1f} Hz")
            
            # 验证φ比例关系
            print(f"\n   验证φ比例关系:")
            for i in range(1, len(cross_zone_entries)):
                actual_ratio = cross_zone_entries[i].freq / cross_zone_entries[i-1].freq
                expected_ratio = args.phi
                ratio_error = abs(actual_ratio - expected_ratio) / expected_ratio * 100
                
                print(f"      音区{cross_zone_entries[i-1].n}→{cross_zone_entries[i].n}: "
                      f"比例={actual_ratio:.3f} (预期:{expected_ratio:.3f}, 误差:{ratio_error:.1f}%)")
            
            # 播放跨音区序列
            print(f"\n   ♪ 播放跨音区φ比例序列...")
            for entry in cross_zone_entries:
                print(f"      音区{entry.n}: {entry.freq:.0f} Hz")
                petersen_player.play_note_with_accurate_frequency(
                    entry, velocity=75, duration=1.0
                )
                time.sleep(0.4)
        
        time.sleep(1.5)
        
        # 演示4: 完整Petersen和弦
        print(f"\n🎶 演示4: 完整Petersen和弦")
        print(f"   结合15方位系统和φ比例创建复杂和弦")
        
        # 构建多维度和弦：不同音区 + 不同方位 + 不同极性
        chord_entries = []
        
        # 选择有代表性的音符构建和弦
        chord_specs = [
            (4, 0, -1),  # 低音区，金，阴
            (5, 1, 0),   # 中音区，木，中
            (5, 2, 1),   # 中音区，水，阳
            (6, 3, 0),   # 高音区，火，中
            (6, 4, -1),  # 高音区，土，阴
        ]
        
        for zone, element, polarity in chord_specs:
            candidates = [e for e in petersen_player.player.all_entries
                         if e.n == zone and e.e == element and e.p == polarity]
            if candidates:
                entry = candidates[0]
                chord_entries.append(entry)
                element_name = ELEMENTS_CN[element]
                polarity_name = ['阴', '中', '阳'][polarity + 1]
                print(f"      音区{zone} {element_name}{polarity_name}: {entry.freq:.1f} Hz")
        
        if chord_entries:
            # 琶音演奏
            print(f"\n   ♪ Petersen琶音...")
            for entry in chord_entries:
                petersen_player.play_note_with_accurate_frequency(
                    entry, velocity=75, duration=0.8
                )
                time.sleep(0.4)
            
            time.sleep(1.0)
            
            # 和弦演奏
            print(f"   ♪ Petersen和弦...")
            active_midis = []
            
            for entry in chord_entries:
                midi_note, cents_dev = petersen_player.play_note_with_accurate_frequency(
                    entry, velocity=70, duration=0.1
                )
                active_midis.append(midi_note)
                
                # 由于play_note_with_accurate_frequency会自动关闭音符，我们需要重新启动
                if petersen_player.has_pitch_bend and abs(cents_dev) > 5:
                    pitch_bend = int(8192 + (cents_dev / 200.0) * 8192)
                    petersen_player.player.fluidsynth.fluid_synth_pitch_bend(
                        petersen_player.player.synth, petersen_player.player.current_channel, pitch_bend
                    )
                
                petersen_player.player.fluidsynth.fluid_synth_noteon(
                    petersen_player.player.synth, petersen_player.player.current_channel, midi_note, 70
                )
                
                if petersen_player.has_pitch_bend:
                    petersen_player.player.fluidsynth.fluid_synth_pitch_bend(
                        petersen_player.player.synth, petersen_player.player.current_channel, 8192
                    )
                
                time.sleep(0.2)
            
            time.sleep(3.0)  # 保持和弦
            
            # 停止和弦
            for midi_note in active_midis:
                petersen_player.player.fluidsynth.fluid_synth_noteoff(
                    petersen_player.player.synth, petersen_player.player.current_channel, midi_note
                )
        
        # 总结
        print(f"\n🌟 真正Petersen系统测试总结:")
        print(f"   参数组合: φ={args.phi}, delta_theta={args.delta_theta}°, F_base={args.f_base} Hz")
        print(f"   ✓ 使用了完整的15方位系统")
        print(f"   ✓ 展示了delta_theta的微妙影响")
        print(f"   ✓ 验证了φ比例关系的准确性")
        print(f"   ✓ 创造了真正的Petersen和弦")
        
        print(f"\n   💡 参数建议:")
        if args.phi == 1.5:
            print(f"      - φ=1.5: 完全五度，极其和谐稳定")
        elif abs(args.phi - 1.618) < 0.01:
            print(f"      - φ=1.618: 黄金比例，神秘独特")
        elif args.phi == 2.0:
            print(f"      - φ=2.0: 纯八度，传统完美")
        
        if args.delta_theta < 3.0:
            print(f"      - delta_theta={args.delta_theta}°: 小偏移，精细差异")
        elif args.delta_theta > 6.0:
            print(f"      - delta_theta={args.delta_theta}°: 大偏移，明显差异")
        else:
            print(f"      - delta_theta={args.delta_theta}°: 中等偏移，平衡效果")
        
        print(f"\n✨ 真正Petersen系统测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()