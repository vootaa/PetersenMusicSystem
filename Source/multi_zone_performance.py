#!/usr/bin/env python3
"""
Petersen音阶多音区演奏演示

使用不同乐器按方位演奏不同音区。
演示PetersenFluidSynth库的多音区和多乐器功能。

演奏策略：按方位（金、木、水、火、土）选择音符，每个方位使用不同乐器演奏所有音区
"""

from PetersenFluidSynth import create_player, InstrumentType
from PetersenScale import ELEMENTS_CN
import time

def main():
    """主演奏函数"""
    print("=== Petersen音阶按方位多音区演奏演示 ===\n")
    
    # 定义乐器序列（对应五行方位）
    instruments = [
        ('Piano', InstrumentType.PIANO),           # 金
        ('Violin', InstrumentType.VIOLIN),         # 木
        ('Flute', InstrumentType.FLUTE),          # 水
        ('Guitar', InstrumentType.GUITAR),         # 火
        ('Harp', InstrumentType.HARP)             # 土
    ]
    
    try:
        with create_player() as player:
            print(f"✓ 创建播放器成功")
            
            # 从Player获取所有可用音区
            target_zones = list(set(entry.n for entry in player.all_entries))
            target_zones.sort()
            print(f"✓ 检测到音区: {target_zones}")
            
            # 按方位演奏
            for i, element in enumerate(ELEMENTS_CN):  # ['金', '木', '水', '火', '土']
                instrument_name, instrument_type = instruments[i]
                
                print(f"\n=== 方位: {element} - 乐器: {instrument_name} ===")
                
                # 按当前方位选择所有音区的频率
                selected = player.select_frequencies(
                    zones=target_zones,  # 使用所有可用音区
                    elements=[element],   # 只选择当前方位
                    max_keys=50          # 每个方位最多50个音符
                )
                
                if not selected:
                    print(f"⚠️  方位 {element} 没有找到频率")
                    continue
                
                # 加载乐器
                player.load_instrument(instrument_type)
                
                # 显示方位信息
                freqs = [e.freq for e in selected]
                zones_used = list(set(e.n for e in selected))
                zones_used.sort()
                
                print(f"  频率范围: {min(freqs):.2f} - {max(freqs):.2f} Hz")
                print(f"  音符数量: {len(selected)}")
                print(f"  涉及音区: {zones_used}")
                
                # 播放方位中的音符（按音区分组演奏）
                for zone in zones_used:
                    zone_notes = [e for e in selected if e.n == zone]
                    if zone_notes:
                        print(f"    音区 {zone}: {len(zone_notes)} 个音符")
                        
                        # 每个音区播放前3个音符
                        play_count = min(3, len(zone_notes))
                        test_keys = [e.key_short for e in zone_notes[:play_count]]
                        
                        print(f"      播放: {' '.join(test_keys)}")
                        player.play_sequence(
                            test_keys, 
                            note_duration=0.5,
                            note_gap=0.1,
                            velocity=80
                        )
                        time.sleep(0.2)  # 音区间短暂暂停
                
                # 方位间较长暂停
                time.sleep(1.0)
            
            print(f"\n=== 按方位演奏完成 ===")
            
            # 最后播放一个综合示例：五行和谐
            print(f"\n=== 综合演示：五行和谐 ===")
            
            # 从每个方位选择一个代表音符
            harmony_notes = []
            for element in ELEMENTS_CN:
                element_entries = player.select_frequencies(
                    zones=target_zones,
                    elements=[element],
                    max_keys=1  # 每个方位只取1个
                )
                if element_entries:
                    harmony_notes.extend(element_entries)
            
            if harmony_notes:
                # 按频率排序
                harmony_notes.sort(key=lambda x: x.freq)
                player.selected_entries = harmony_notes
                player._map_to_midi_keys()
                
                # 使用Choir演奏和谐音符
                player.load_instrument(InstrumentType.CHOIR)
                harmony_keys = [e.key_short for e in harmony_notes]
                print(f"  五行和谐: {' '.join(harmony_keys)}")
                
                # 先单独播放每个音符
                print("  单独播放...")
                player.play_sequence(
                    harmony_keys,
                    note_duration=0.8,
                    note_gap=0.2,
                    velocity=85
                )
                
                time.sleep(1.0)
                
                # 再同时播放（和弦效果）
                print("  和弦效果...")
                for i, (midi_key, entry) in enumerate(player.midi_mapping.items()):
                    print(f"    启动: {entry.key_short}")
                    player.fluidsynth.fluid_synth_noteon(
                        player.synth, player.current_channel, midi_key, 70
                    )
                    time.sleep(0.1)  # 短暂延迟创造层次感
                
                time.sleep(2.0)  # 保持和弦2秒
                
                # 停止所有音符
                for midi_key, entry in player.midi_mapping.items():
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