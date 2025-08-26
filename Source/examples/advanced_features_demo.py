"""
高级功能演示
展示Enhanced Petersen Player的高级和专业功能
"""
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "Source"))

from enhanced_petersen_player import create_player, PlayerConfiguration
from utils.presets import (
    COMPLETE_PRESET_COMBINATIONS, 
    recommend_preset_for_context,
    analyze_preset_suitability
)

def custom_configuration_demo():
    """自定义配置演示"""
    print("⚙️  === 自定义配置演示 ===")
    
    # 创建自定义配置
    custom_config = PlayerConfiguration(
        soundfont_directory="../Soundfonts",
        sample_rate=48000,  # 更高采样率
        buffer_size=512,    # 更小缓冲区（更低延迟）
        audio_driver="coreaudio" if sys.platform == "darwin" else "pulse",
        auto_optimize_settings=True,
        enable_accurate_frequency=True
    )
    
    print(f"📊 自定义配置:")
    print(f"   采样率: {custom_config.sample_rate}Hz")
    print(f"   缓冲区: {custom_config.buffer_size}样本")
    print(f"   音频驱动: {custom_config.audio_driver}")
    print(f"   自动优化: {custom_config.auto_optimize_settings}")
    
    with create_player(config=custom_config) as player:
        print("✅ 自定义配置播放器创建成功")
        
        # 测试高质量播放
        test_frequencies = [440.0, 554.37, 659.25]  # A4-C#5-E5 和弦
        player.play_frequencies(test_frequencies, duration=2.0)

def preset_system_demo():
    """预设系统演示"""
    print("\n🎨 === 预设系统演示 ===")
    
    with create_player() as player:
        print("📋 可用完整预设:")
        for preset_name, preset_info in COMPLETE_PRESET_COMBINATIONS.items():
            print(f"   {preset_name}: {preset_info.description}")
        
        # 演示几个有代表性的预设
        demo_presets = [
            "steinway_concert_grand",
            "jazz_club_session", 
            "cathedral_sacred"
        ]
        
        # 测试旋律
        melody = [261.63, 329.63, 392.00, 523.25]  # C-E-G-C 音阶
        melody_names = ["C4", "E4", "G4", "C5"]
        
        for preset_name in demo_presets:
            if preset_name not in COMPLETE_PRESET_COMBINATIONS:
                continue
                
            preset = COMPLETE_PRESET_COMBINATIONS[preset_name]
            print(f"\n🎵 演示预设: {preset.name}")
            print(f"   描述: {preset.description}")
            
            # 应用预设组合
            success = player.apply_preset_combination(
                preset.effect_preset,
                preset.expression_preset
            )
            
            if success:
                # 播放测试旋律
                player.play_frequencies(melody, melody_names, duration=0.8)
                print(f"   ✅ {preset.name} 演示完成")
            else:
                print(f"   ❌ {preset.name} 应用失败")

def intelligent_recommendation_demo():
    """智能推荐演示"""
    print("\n🤖 === 智能推荐系统演示 ===")
    
    with create_player() as player:
        # 获取可用SoundFont
        sf_summary = player.sf_manager.get_soundfont_summary()
        available_sfs = list(sf_summary['soundfont_details'].keys())
        
        # 不同上下文的推荐
        contexts = [
            ("concert", "音乐会演出"),
            ("study", "学习练习"),
            ("recording", "录音制作"),
            ("jazz", "爵士演出")
        ]
        
        print("🎯 不同上下文的预设推荐:")
        for context, description in contexts:
            recommended = recommend_preset_for_context(
                context, 
                available_soundfonts=available_sfs
            )
            print(f"   {description}: {recommended}")
        
        # 分析预设适用性
        print("\n📊 预设适用性分析:")
        test_frequency_range = (200.0, 1000.0)  # 测试频率范围
        test_note_count = 12
        
        for preset_name in ["steinway_concert_grand", "jazz_club_session"]:
            analysis = analyze_preset_suitability(
                preset_name, test_frequency_range, test_note_count
            )
            print(f"   {preset_name}:")
            print(f"     适用性: {analysis.get('suitability', 'unknown')}")
            print(f"     分数: {analysis.get('score', 0):.2f}")
            if analysis.get('recommendations'):
                for rec in analysis['recommendations'][:2]:  # 只显示前2个建议
                    print(f"     建议: {rec}")

def real_time_effects_demo():
    """实时音效演示"""
    print("\n🎛️  === 实时音效调节演示 ===")
    
    with create_player() as player:
        # 基础音符用于测试
        test_note_freq = 440.0  # A4
        test_note_name = "A4"
        
        print("🎵 将演示实时音效调节 (播放相同音符，不同效果)")
        
        # 动态调节混响
        reverb_levels = [0.0, 0.3, 0.6, 0.9]
        
        for level in reverb_levels:
            print(f"\n🔊 混响级别: {level:.1f}")
            
            # 创建自定义音效设置
            custom_effect = player.effects.create_custom_preset(
                f"reverb_{level}",
                reverb_level=level,
                reverb_room_size=0.5,
                brightness=70
            )
            
            # 应用设置
            player.effects.apply_effect_settings(custom_effect)
            
            # 播放测试音符
            player.play_frequencies([test_note_freq], [test_note_name], duration=1.5)
        
        # 动态调节表现力
        print("\n🎭 表现力动态调节:")
        
        velocity_patterns = [
            (60, "轻柔"),
            (85, "中等"),
            (110, "强烈"),
            (127, "最强")
        ]
        
        for velocity, description in velocity_patterns:
            print(f"   {description} (力度: {velocity})")
            player.play_frequencies([test_note_freq], [test_note_name], 
                                  velocity=velocity, duration=0.8)

def soundfont_analysis_demo():
    """SoundFont分析演示"""
    print("\n🔍 === SoundFont深度分析演示 ===")
    
    with create_player() as player:
        sf_summary = player.sf_manager.get_soundfont_summary()
        
        print("📁 SoundFont详细分析:")
        for sf_name, sf_details in sf_summary['soundfont_details'].items():
            print(f"\n🎼 {sf_name}:")
            print(f"   类型: {sf_details['type']}")
            print(f"   大小: {sf_details['size_mb']:.1f}MB")
            print(f"   质量评分: {sf_details['quality_score']:.2f}")
            print(f"   乐器数量: {sf_details['instrument_count']}")
            print(f"   推荐用途: {sf_details['recommended_use']}")
            
            # 如果是当前加载的SoundFont，显示更多信息
            if sf_details.get('is_loaded', False):
                print("   📊 乐器分类统计:")
                instruments = player.sf_manager.get_available_instruments(sf_name)
                category_count = {}
                for inst in instruments:
                    category = inst.category
                    category_count[category] = category_count.get(category, 0) + 1
                
                for category, count in sorted(category_count.items()):
                    print(f"     {category}: {count}个")

def performance_optimization_demo():
    """性能优化演示"""
    print("\n⚡ === 性能优化演示 ===")
    
    with create_player() as player:
        # 准备测试数据
        long_sequence = []
        for i in range(24):  # 两个八度的半音阶
            freq = 261.63 * (2 ** (i / 12))  # 从C4开始的半音阶
            long_sequence.append(freq)
        
        print(f"📊 性能测试: {len(long_sequence)} 个音符序列")
        
        # 测试不同播放模式的性能
        test_modes = [
            ("简单播放", {"use_accurate_frequency": False, "duration": 0.3, "gap": 0.1}),
            ("精确频率播放", {"use_accurate_frequency": True, "duration": 0.3, "gap": 0.1}),
            ("高表现力播放", {"use_accurate_frequency": True, "duration": 0.5, "gap": 0.2})
        ]
        
        for mode_name, params in test_modes:
            print(f"\n🎵 {mode_name}:")
            
            start_time = time.time()
            success = player.play_frequencies(long_sequence, **params)
            elapsed_time = time.time() - start_time
            
            if success:
                print(f"   ✅ 完成时间: {elapsed_time:.2f}秒")
                print(f"   ⚡ 平均每音符: {elapsed_time/len(long_sequence)*1000:.1f}ms")
            else:
                print(f"   ❌ 播放失败")

def error_handling_demo():
    """错误处理演示"""
    print("\n🛡️  === 错误处理与恢复演示 ===")
    
    with create_player() as player:
        print("🧪 故意触发各种错误情况:")
        
        # 1. 无效频率测试
        print("\n1️⃣  无效频率测试:")
        invalid_frequencies = [0, -100, 50000]  # 无效频率
        success = player.play_frequencies(invalid_frequencies)
        print(f"   结果: {'部分成功' if not success else '意外成功'}")
        
        # 2. 无效SoundFont测试
        print("\n2️⃣  无效SoundFont测试:")
        success = player.switch_soundfont("nonexistent_soundfont.sf2")
        print(f"   结果: {'失败 (预期)' if not success else '意外成功'}")
        
        # 3. 无效乐器测试
        print("\n3️⃣  无效乐器测试:")
        success = player.switch_instrument(999)  # 无效程序号
        print(f"   结果: {'失败 (预期)' if not success else '意外成功'}")
        
        # 4. 系统恢复测试
        print("\n4️⃣  系统恢复测试:")
        # 确保系统仍然可以正常工作
        test_freq = [440.0]
        success = player.play_frequencies(test_freq)
        print(f"   恢复状态: {'正常' if success else '异常'}")
        
        # 5. 显示最终系统状态
        status = player.get_system_status()
        print(f"\n📊 最终系统状态: {status['status']}")

def comprehensive_demo():
    """综合演示"""
    print("\n🌟 === 综合功能演示 ===")
    
    with create_player() as player:
        print("🎵 执行完整的音乐演示流程:")
        
        # 1. 自动选择最佳设置
        print("\n1️⃣  自动优化设置...")
        player._auto_optimize_settings()
        
        # 2. 加载专业预设
        print("\n2️⃣  应用专业预设...")
        success = player.apply_preset_combination("hall", "romantic")
        
        # 3. 演示复杂音乐结构
        print("\n3️⃣  演示音乐结构...")
        
        # 和弦进行：C - Am - F - G
        chord_progression = [
            ([261.63, 329.63, 392.00], ["C4", "E4", "G4"]),     # C major
            ([220.00, 261.63, 329.63], ["A3", "C4", "E4"]),     # A minor  
            ([174.61, 220.00, 261.63], ["F3", "A3", "C4"]),     # F major
            ([196.00, 246.94, 293.66], ["G3", "B3", "D4"])      # G major
        ]
        
        print("   🎵 和弦进行演示:")
        for i, (chord_freqs, chord_names) in enumerate(chord_progression):
            print(f"     和弦 {i+1}: {' - '.join(chord_names)}")
            player.play_frequencies(chord_freqs, chord_names, duration=2.0)
            time.sleep(0.5)  # 和弦间停顿
        
        # 4. 显示完整统计
        print("\n4️⃣  演示统计:")
        final_status = player.get_system_status()
        stats = final_status['session_stats']
        
        print(f"   📊 播放统计:")
        print(f"     总音符数: {stats['notes_played']}")
        print(f"     序列数: {stats['sequences_played']}")
        print(f"     总时长: {stats['total_play_time']:.1f}秒")
        print(f"     运行时间: {final_status['runtime_seconds']:.1f}秒")
        
        print("\n✨ 综合演示完成!")

if __name__ == "__main__":
    print("🎵 Enhanced Petersen Player - 高级功能演示")
    print("=" * 60)
    
    try:
        custom_configuration_demo()
        preset_system_demo()
        intelligent_recommendation_demo()
        real_time_effects_demo()
        soundfont_analysis_demo()
        performance_optimization_demo()
        error_handling_demo()
        comprehensive_demo()
        
        print("\n🎉 所有高级功能演示完成!")
        print("🚀 Enhanced Petersen Music System 功能全面展示结束!")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()