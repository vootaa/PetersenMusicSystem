"""
基础使用演示
展示Enhanced Petersen Player的基本功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from enhanced_petersen_player import create_player, quick_demo, compare_frequencies

def basic_playback_demo():
    """基础播放演示"""
    print("🎵 === 基础播放演示 ===")
    
    # 创建播放器
    with create_player(soundfont_dir="../../Soundfonts") as player:
        # 检查系统状态
        status = player.get_system_status()
        print(f"系统状态: {status['status']}")
        print(f"可用SoundFont: {status['soundfont_summary']['total_soundfonts']}")

        # 如果没有SoundFont，跳过演示
        if not player.sf_manager or not player.sf_manager.soundfonts:
            print("⚠️  无SoundFont文件，跳过播放演示")
            return
        
        # 简单的音阶演示
        demo_frequencies = [
            261.63,  # C4
            293.66,  # D4
            329.63,  # E4
            349.23,  # F4
            392.00,  # G4
            440.00,  # A4
            493.88,  # B4
            523.25   # C5
        ]
        demo_names = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
        
        print("\n🎼 播放C大调音阶...")
        success = player.play_frequencies(
            demo_frequencies, 
            demo_names,
            velocity=85,
            duration=0.8,
            gap=0.2
        )
        
        if success:
            print("✅ 播放完成")
        else:
            print("❌ 播放失败")
        
        # 显示播放统计
        final_stats = player.get_system_status()['session_stats']
        print(f"\n📊 播放统计:")
        print(f"   音符总数: {final_stats['notes_played']}")
        print(f"   播放时长: {final_stats['total_play_time']:.1f}秒")

def soundfont_switching_demo():
    """SoundFont切换演示"""
    print("\n🎛️  === SoundFont切换演示 ===")
    
    with create_player(soundfont_dir="../../Soundfonts") as player:
        # 获取可用的SoundFont列表
        sf_summary = player.sf_manager.get_soundfont_summary() if player.sf_manager else {'soundfont_details': {}}
        available_sfs = list(sf_summary['soundfont_details'].keys())
        
        if len(available_sfs) < 2:
            print("⚠️  需要至少2个SoundFont文件进行演示，跳过")
            return
        
        # 测试音符
        test_chord = [261.63, 329.63, 392.00]  # C大三和弦
        chord_names = ["C4", "E4", "G4"]
        
        print(f"发现 {len(available_sfs)} 个SoundFont文件")
        
        # 逐个切换并演示
        for i, sf_name in enumerate(available_sfs[:3]):  # 最多演示3个
            print(f"\n🎵 切换到: {sf_name}")
            
            success = player.switch_soundfont(sf_name)
            if success:
                # 播放测试和弦
                player.play_frequencies(test_chord, chord_names, duration=1.5)
                print(f"   ✅ SoundFont {i+1} 演示完成")
            else:
                print(f"   ❌ SoundFont {i+1} 加载失败")

def instrument_comparison_demo():
    """乐器对比演示"""
    print("\n🎺 === 乐器对比演示 ===")
    
    with create_player(soundfont_dir="../../Soundfonts") as player:
        # 确保有SoundFont加载
        if not player.sf_manager or not player.sf_manager.current_soundfont:
            print("❌ 未加载SoundFont")
            return
        
        # 获取可用乐器
        instruments = player.sf_manager.get_available_instruments()
        if len(instruments) < 3:
            print("⚠️  可用乐器较少，演示可能不完整")
        
        # 选择几种不同类型的乐器
        demo_instruments = []
        categories_wanted = ['piano', 'strings', 'brass', 'woodwind']
        
        for category in categories_wanted:
            for inst in instruments:
                if category in inst.category and len(demo_instruments) < 4:
                    demo_instruments.append(inst)
                    break
        
        if not demo_instruments:
            demo_instruments = instruments[:4]  # 至少选择前4个
        
        # 演示旋律
        melody = [261.63, 293.66, 329.63, 349.23, 392.00]
        melody_names = ["C4", "D4", "E4", "F4", "G4"]
        
        print(f"将使用 {len(demo_instruments)} 种乐器演示相同旋律:")
        
        for inst in demo_instruments:
            print(f"\n🎵 {inst.name} (程序 {inst.program})")
            
            # 切换乐器
            success = player.switch_instrument(inst.program)
            if success:
                # 播放旋律
                player.play_frequencies(melody, melody_names, duration=0.6, gap=0.1)
            else:
                print(f"   ❌ 乐器切换失败")

if __name__ == "__main__":
    print("🎵 Enhanced Petersen Player - 基础使用演示")
    print("=" * 50)
    
    try:
        basic_playback_demo()
        soundfont_switching_demo()
        instrument_comparison_demo()
        
        print("\n🎉 所有演示完成!")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        pass