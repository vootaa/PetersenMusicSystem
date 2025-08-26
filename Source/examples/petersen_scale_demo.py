"""
Petersen音阶专用演示
展示针对Petersen音阶的专业功能
"""
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "Source"))

from enhanced_petersen_player import create_player
from utils.analysis import analyze_petersen_scale_characteristics

@dataclass
class PetersenEntry:
    """Petersen音阶条目（示例数据结构）"""
    freq: float
    key_name: str
    cents_deviation: float = 0.0
    octave: int = 4
    
# 示例Petersen音阶数据（实际数据应从您的系统获取）
SAMPLE_PETERSEN_SCALE = [
    PetersenEntry(261.626, "C4", 0.0),
    PetersenEntry(277.183, "C#4", 7.0),    # 稍微偏离12平均律
    PetersenEntry(293.665, "D4", 0.0),
    PetersenEntry(311.127, "D#4", 3.9),    # 微调
    PetersenEntry(329.628, "E4", 0.0),
    PetersenEntry(349.228, "F4", 0.0),
    PetersenEntry(369.994, "F#4", -1.9),   # 微调
    PetersenEntry(391.995, "G4", 0.0),
    PetersenEntry(415.305, "G#4", 4.5),    # 微调
    PetersenEntry(440.000, "A4", 0.0),
    PetersenEntry(466.164, "A#4", -6.8),   # 微调
    PetersenEntry(493.883, "B4", 0.0),
    PetersenEntry(523.251, "C5", 0.0),
]

def petersen_analysis_demo():
    """Petersen音阶分析演示"""
    print("🔬 === Petersen音阶分析演示 ===")
    
    # 分析音阶特性
    characteristics = analyze_petersen_scale_characteristics(SAMPLE_PETERSEN_SCALE)
    
    print("📊 音阶分析结果:")
    print(f"   总条目数: {characteristics.get('total_entries', 0)}")
    print(f"   频率范围: {characteristics.get('frequency_range', (0, 0))[0]:.1f} - {characteristics.get('frequency_range', (0, 0))[1]:.1f} Hz")
    print(f"   跨越八度: {characteristics.get('spans_octaves', 0):.1f}")
    print(f"   平均偏差: {characteristics.get('avg_deviation', 0):.1f} 音分")
    print(f"   最大偏差: {characteristics.get('max_deviation', 0):.1f} 音分")
    
    # 显示需要特殊处理的音符
    deviations = characteristics.get('cent_deviations', [])
    if any(abs(d) > 5 for d in deviations):
        print("\n⚠️  显著偏离12平均律的音符:")
        for i, (entry, deviation) in enumerate(zip(SAMPLE_PETERSEN_SCALE, deviations)):
            if abs(deviation) > 5:
                print(f"   {entry.key_name}: {deviation:+.1f} 音分")

def frequency_accuracy_demo():
    """频率精确度演示"""
    print("\n🎯 === 频率精确度演示 ===")
    
    with create_player() as player:
        # 提取频率和音名
        frequencies = [entry.freq for entry in SAMPLE_PETERSEN_SCALE]
        key_names = [entry.key_name for entry in SAMPLE_PETERSEN_SCALE]
        
        # 执行精确度分析演示
        analysis = player.demonstrate_frequency_accuracy(frequencies, key_names)
        
        print("\n📈 精确度分析详情:")
        if analysis:
            print(f"   补偿策略: Pitch Bend")
            print(f"   补偿有效性: {analysis.get('compensation_effectiveness', 0):.1f}%")
            print(f"   残余误差: {analysis.get('residual_error', 0):.1f} 音分")

def multi_mode_comparison_demo():
    """多模式对比演示"""
    print("\n🎭 === 多演奏模式对比演示 ===")
    
    with create_player() as player:
        modes_to_demo = [
            ("solo_piano", "romantic", "浪漫主义钢琴独奏"),
            ("solo_piano", "classical", "古典主义钢琴独奏"),
            ("orchestral", "chamber", "室内乐编制"),
            ("comparison", "12tet_vs_petersen", "12平均律对比"),
        ]
        
        # 使用音阶的一部分进行演示（避免过长）
        demo_scale = SAMPLE_PETERSEN_SCALE[:8]  # 一个八度
        
        for mode, style_or_arrangement, description in modes_to_demo:
            print(f"\n🎵 演示模式: {description}")
            
            try:
                if mode == "orchestral":
                    success = player.play_petersen_scale(
                        demo_scale, mode=mode, arrangement=style_or_arrangement
                    )
                elif mode == "comparison":
                    success = player.play_petersen_scale(
                        demo_scale, mode=mode, comparison_type=style_or_arrangement
                    )
                else:
                    success = player.play_petersen_scale(
                        demo_scale, mode=mode, style=style_or_arrangement
                    )
                
                if success:
                    print(f"   ✅ {description} 演示完成")
                else:
                    print(f"   ⚠️  {description} 演示部分失败")
                    
            except Exception as e:
                print(f"   ❌ {description} 演示失败: {e}")

def expression_showcase():
    """表现力展示"""
    print("\n🎨 === 表现力风格展示 ===")
    
    with create_player() as player:
        # 选择一个短旋律进行表现力对比
        melody_scale = SAMPLE_PETERSEN_SCALE[0:5]  # C4到E4
        
        expression_styles = [
            ("mechanical", "机械式演奏"),
            ("romantic", "浪漫主义风格"),
            ("jazz", "爵士摇摆风格"),
            ("gentle", "轻柔风格")
        ]
        
        print("将用相同旋律演示不同表现力风格:")
        for entry in melody_scale:
            print(f"   {entry.key_name}: {entry.freq:.2f}Hz")
        
        for style, description in expression_styles:
            print(f"\n🎵 {description}")
            
            # 应用表现力预设
            player.expression.apply_expression_preset(style)
            
            # 播放旋律
            frequencies = [entry.freq for entry in melody_scale]
            key_names = [entry.key_name for entry in melody_scale]
            
            success = player.play_frequencies(frequencies, key_names)
            if success:
                print(f"   ✅ {description} 完成")

def effects_showcase():
    """音效展示"""
    print("\n🎛️  === 音效空间展示 ===")
    
    with create_player() as player:
        # 选择一个和弦进行音效对比
        chord_entries = [SAMPLE_PETERSEN_SCALE[0], SAMPLE_PETERSEN_SCALE[2], 
                        SAMPLE_PETERSEN_SCALE[4], SAMPLE_PETERSEN_SCALE[6]]  # C-E-G-B
        
        effect_presets = [
            ("dry", "干声（无效果）"),
            ("intimate", "亲密空间"),
            ("hall", "音乐厅"),
            ("cathedral", "大教堂")
        ]
        
        frequencies = [entry.freq for entry in chord_entries]
        key_names = [entry.key_name for entry in chord_entries]
        
        print("将用和弦演示不同空间音效:")
        for entry in chord_entries:
            print(f"   {entry.key_name}: {entry.freq:.2f}Hz")
        
        for preset, description in effect_presets:
            print(f"\n🎵 {description}")
            
            # 应用音效预设
            player.effects.apply_effect_preset(preset)
            
            # 播放和弦
            success = player.play_frequencies(frequencies, key_names, duration=2.0)
            if success:
                print(f"   ✅ {description} 完成")

def educational_mode_demo():
    """教育模式演示"""
    print("\n📚 === 教育模式演示 ===")
    
    with create_player() as player:
        educational_lessons = [
            ("basic_theory", "基础理论"),
            ("frequency_analysis", "频率分析"),
            ("harmonic_series", "谐波系列")
        ]
        
        for lesson_type, description in educational_lessons:
            print(f"\n📖 {description}课程:")
            
            success = player.play_petersen_scale(
                SAMPLE_PETERSEN_SCALE[:6],  # 使用前6个音符
                mode="educational",
                lesson_type=lesson_type
            )
            
            if success:
                print(f"   ✅ {description}课程完成")

def complete_system_showcase():
    """完整系统展示"""
    print("\n🌟 === 完整系统功能展示 ===")
    
    with create_player() as player:
        # 显示系统配置
        status = player.get_system_status()
        print("📊 系统状态:")
        print(f"   运行时间: {status['runtime_seconds']:.1f}秒")
        print(f"   已播放音符: {status['session_stats']['notes_played']}")
        print(f"   已加载SoundFont: {status['session_stats']['soundfonts_loaded']}")
        
        # 显示可用模式
        modes = status['available_modes']
        print(f"\n🎯 可用演奏模式:")
        for mode, options in modes.items():
            print(f"   {mode}: {', '.join(options)}")
        
        # 显示当前音效设置
        effects_info = status['current_effects']
        print(f"\n🎛️  当前音效设置:")
        if 'reverb' in effects_info:
            reverb = effects_info['reverb']
            print(f"   混响: 房间大小={reverb.get('room_size', 0):.1f}, 级别={reverb.get('level', 0):.1f}")
        
        # 演示完整Petersen音阶
        print(f"\n🎵 完整Petersen音阶演示 ({len(SAMPLE_PETERSEN_SCALE)} 个音符):")
        success = player.play_petersen_scale(
            SAMPLE_PETERSEN_SCALE,
            mode="solo_piano",
            style="romantic"
        )
        
        if success:
            print("   ✅ 完整音阶演示成功")
            
            # 最终统计
            final_status = player.get_system_status()
            final_stats = final_status['session_stats']
            print(f"\n📈 最终统计:")
            print(f"   总播放音符: {final_stats['notes_played']}")
            print(f"   总播放时长: {final_stats['total_play_time']:.1f}秒")
            print(f"   演示序列数: {final_stats['sequences_played']}")

if __name__ == "__main__":
    print("🎵 Enhanced Petersen Player - Petersen音阶专用演示")
    print("=" * 60)
    
    try:
        petersen_analysis_demo()
        frequency_accuracy_demo()
        multi_mode_comparison_demo()
        expression_showcase()
        effects_showcase()
        educational_mode_demo()
        complete_system_showcase()
        
        print("\n🎉 Petersen音阶演示完成!")
        print("🎵 感谢您体验Enhanced Petersen Music System!")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()