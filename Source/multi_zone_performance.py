#!/usr/bin/env python3
"""
Petersen音阶多乐器按方位极性演奏演示

使用音域宽广的乐器，按乐器->方位->极性的三重循环演奏。
从低音区到高音区连续播放，展示不同乐器在Petersen音阶系统中的表现。

演奏策略：
1. 外层：选择音域宽广的乐器
2. 中层：按五行方位（金、木、水、火、土）
3. 内层：按极性（阴、中、阳）
4. 音符：从低频到高频连续播放
"""

from PetersenFluidSynth import create_player, InstrumentType
from PetersenScale import ELEMENTS_CN
import time

def main():
    """主演奏函数"""
    print("=== Petersen音阶多乐器按方位极性演奏演示 ===\n")
    
    # 选择音域宽广的乐器（适合全频段）
    instruments = [
        ('Piano', InstrumentType.PIANO, 20, 4000),           # 钢琴：最宽音域
        ('String Ensemble', InstrumentType.STRING_ENSEMBLE, 60, 3000),  # 弦乐组：宽音域
        ('Synth Lead', InstrumentType.SYNTH_LEAD, 30, 5000), # 合成器：可覆盖全频段
        ('Harp', InstrumentType.HARP, 32, 2500),             # 竖琴：较宽音域
        ('Electric Piano', InstrumentType.ELECTRIC_PIANO, 25, 3500), # 电钢琴：宽音域
    ]
    
    # 极性定义
    polarities = [
        (-1, '阴', '-'),
        (0, '中', '0'),
        (1, '阳', '+')
    ]
    
    try:
        with create_player() as player:
            print(f"✓ 创建播放器成功")
            
            # 从Player获取所有可用音区
            target_zones = list(set(entry.n for entry in player.all_entries))
            target_zones.sort()
            print(f"✓ 检测到音区: {target_zones}")
            print(f"✓ 总音阶条目: {len(player.all_entries)}\n")
            
            # 最外层：乐器循环
            for instrument_idx, (instrument_name, instrument_type, freq_min, freq_max) in enumerate(instruments):
                print(f"\n{'='*60}")
                print(f"乐器 {instrument_idx+1}/{len(instruments)}: {instrument_name}")
                print(f"适用频率范围: {freq_min} - {freq_max} Hz")
                print(f"{'='*60}")
                
                # 加载乐器
                player.load_instrument(instrument_type)
                time.sleep(0.5)  # 乐器切换暂停
                
                # 中层：五行方位循环
                for element_idx, element in enumerate(ELEMENTS_CN):
                    print(f"\n--- 方位: {element} ({element_idx+1}/5) ---")
                    
                    # 内层：极性循环
                    for polarity_value, polarity_cn, polarity_symbol in polarities:
                        print(f"\n  极性: {polarity_cn} ({polarity_symbol})")
                        
                        # 选择当前方位和极性的频率
                        selected = player.select_frequencies(
                            zones=target_zones,
                            elements=[element],
                            polarities=[polarity_cn],
                            freq_range=(freq_min, freq_max),  # 限制在乐器适用范围内
                            max_keys=64  # 每个组合最多64个音符
                        )
                        
                        if not selected:
                            print(f"    ⚠️  无适合频率，跳过")
                            continue
                        
                        # 按频率排序（从低到高）
                        selected.sort(key=lambda x: x.freq)
                        
                        # 显示详细信息
                        freqs = [e.freq for e in selected]
                        zones_used = list(set(e.n for e in selected))
                        zones_used.sort()
                        
                        print(f"    音符数量: {len(selected)}")
                        print(f"    频率范围: {min(freqs):.2f} - {max(freqs):.2f} Hz")
                        print(f"    涉及音区: {zones_used}")
                        
                        # 显示将要播放的音符
                        key_names = [e.key_short for e in selected]
                        print(f"    音符序列: {' '.join(key_names)}")
                        
                        # 连续播放（从低频到高频）
                        print(f"    ♪ 播放中...")
                        
                        # 使用渐强效果：从低音到高音音量逐渐增强
                        base_velocity = 60
                        for i, entry in enumerate(selected):
                            # 计算动态音量（低音较轻，高音较重）
                            velocity = min(127, base_velocity + int(i * 40 / len(selected)))
                            
                            print(f"      {i+1:2d}/{len(selected):2d}: {entry.key_short} "
                                  f"({entry.freq:6.2f} Hz, V={velocity})", end="", flush=True)
                            
                            # 播放音符
                            midi_key = i  # 使用索引作为MIDI键
                            if midi_key in player.midi_mapping:
                                # 添加音效：音符重叠效果
                                player.fluidsynth.fluid_synth_noteon(
                                    player.synth, player.current_channel, midi_key, velocity
                                )
                                time.sleep(0.3)  # 音符持续0.3秒
                                
                                # 不立即关闭，让音符自然衰减并与下一个重叠
                                player.fluidsynth.fluid_synth_noteoff(
                                    player.synth, player.current_channel, midi_key
                                )
                                time.sleep(0.4)  # 0.4秒间隔
                                print(" ✓")
                            else:
                                print(" ✗")
                        
                        # 极性间暂停
                        time.sleep(0.8)
                    
                    # 方位间暂停
                    time.sleep(1.2)
                
                # 乐器间较长暂停
                print(f"\n--- {instrument_name} 演奏完成 ---")
                time.sleep(2.0)
            
            # 最终演示：所有乐器的和谐演奏
            print(f"\n{'='*60}")
            print(f"最终演示：五行和谐")
            print(f"{'='*60}")
            
            # 从每个方位选择一个代表音符（中音区，中性极性）
            harmony_notes = []
            for element in ELEMENTS_CN:
                element_entries = player.select_frequencies(
                    zones=[5, 6, 7],  # 中音区
                    elements=[element],
                    polarities=['中'],
                    freq_range=(200, 800),  # 中频范围
                    max_keys=1
                )
                if element_entries:
                    harmony_notes.extend(element_entries)
            
            if harmony_notes:
                # 按频率排序
                harmony_notes.sort(key=lambda x: x.freq)
                player.selected_entries = harmony_notes
                player._map_to_midi_keys()
                
                # 使用钢琴演奏最终和谐
                player.load_instrument(InstrumentType.PIANO)
                harmony_keys = [e.key_short for e in harmony_notes]
                
                print(f"五行代表音符: {' '.join(harmony_keys)}")
                print(f"频率: {[f'{e.freq:.1f}' for e in harmony_notes]} Hz")
                
                # 琶音效果
                print("♪ 琶音演奏...")
                for i, (midi_key, entry) in enumerate(player.midi_mapping.items()):
                    print(f"  {entry.key_short} ({entry.freq:.1f} Hz)")
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, 90
                    )
                    time.sleep(0.1)
                
                # 和弦效果
                print("♪ 和弦演奏...")
                time.sleep(0.5)
                for midi_key, entry in player.midi_mapping.items():
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, 80
                    )
                
                time.sleep(3.0)  # 保持和弦3秒
                
                # 停止所有音符
                for midi_key in player.midi_mapping:
                    player.fluidsynth.fluid_synth_noteoff(
                        player.synth, player.current_channel, midi_key
                    )
            
            print(f"\n✓ 所有演示完成")
            
    except FileNotFoundError as e:
        print(f"❌ SoundFont文件未找到: {e}")
        print("请确保SoundFont文件路径正确")
    except Exception as e:
        print(f"❌ 演奏过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()