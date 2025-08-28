"""
Petersen音阶专用演示
展示针对Petersen音阶的专业功能
使用PetersenScale_Phi生成真实的Petersen音阶数据
"""
from dataclasses import dataclass
from typing import List

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from enhanced_petersen_player import create_player
from utils.analysis import analyze_petersen_scale_characteristics
from PetersenScale_Phi import PetersenScale_Phi, PHI

@dataclass
class PetersenEntry:
    """Petersen音阶条目"""
    freq: float
    key_name: str
    cents_deviation: float = 0.0
    octave: int = 4

def generate_petersen_scale(phi: float = PHI, delta_theta: float = 4.8, 
                          F_base: float = 261.63, F_min: float = 30.0, 
                          F_max: float = 6000.0, max_entries: Optional[int] = None) -> List[PetersenEntry]:
    """
    使用PetersenScale_Phi生成真实的Petersen音阶数据
    
    Args:
        phi: 比例系数，默认黄金比例
        delta_theta: 极性偏移角度，默认4.8°
        F_base: 基准频率，默认C4 (261.63 Hz)
        F_min: 最小频率限制
        F_max: 最大频率限制
        max_entries: 最大条目数限制（可选，用于演示）
    
    Returns:
        PetersenEntry列表
    """
    # 创建PetersenScale_Phi实例
    scale = PetersenScale_Phi(
        F_base=F_base,
        delta_theta=delta_theta,
        phi=phi,
        F_min=F_min,
        F_max=F_max
    )
    
    # 生成音阶条目
    entries = scale.generate()
    
    # 转换为PetersenEntry格式
    petersen_entries = []
    for entry in entries:
        # 计算八度（基于频率）
        octave = int(round((entry['freq'] / 261.63) ** (1/12) * 4))  # 近似计算
        
        petersen_entry = PetersenEntry(
            freq=entry['freq'],
            key_name=entry['key_short'],  # 使用短名，如 "J-"
            cents_deviation=entry['cents_ref'],  # 相对于参考频率的音分值
            octave=octave
        )
        petersen_entries.append(petersen_entry)
        
        # 如果设置了最大条目数限制
        if max_entries and len(petersen_entries) >= max_entries:
            break
    
    return petersen_entries  


def petersen_analysis_demo(phi: float = PHI, delta_theta: float = 4.8):
    """Petersen音阶分析演示（使用实际数据）"""
    print("🔬 === Petersen音阶分析演示 ===")
    
    # 生成实际Petersen音阶数据
    scale_data = generate_petersen_scale(phi=phi, delta_theta=delta_theta, max_entries=20)
    
    # 转换为analyze_petersen_scale_characteristics所需的格式
    analysis_data = [
        {'freq': entry.freq, 'key_name': entry.key_name, 'cents_deviation': entry.cents_deviation}
        for entry in scale_data
    ]
    
    # 分析音阶特性
    characteristics = analyze_petersen_scale_characteristics(analysis_data)
    
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
        for i, (entry, deviation) in enumerate(zip(scale_data, deviations)):
            if abs(deviation) > 5:
                print(f"   {entry.key_name}: {deviation:+.1f} 音分")

def frequency_accuracy_demo(phi: float = PHI, delta_theta: float = 4.8):
    """频率精确度演示（使用实际数据）"""
    print("\n🎯 === 频率精确度演示 ===")
    
    with create_player() as player:
        # 生成实际Petersen音阶数据
        scale_data = generate_petersen_scale(phi=phi, delta_theta=delta_theta, max_entries=12)
        
        # 提取频率和音名
        frequencies = [entry.freq for entry in scale_data]
        key_names = [entry.key_name for entry in scale_data]
        
        # 执行精确度分析演示
        analysis = player.demonstrate_frequency_accuracy(frequencies, key_names)
        
        print("\n📈 精确度分析详情:")
        if analysis:
            print(f"   补偿策略: Pitch Bend")
            print(f"   补偿有效性: {analysis.get('compensation_effectiveness', 0):.1f}%")
            print(f"   残余误差: {analysis.get('residual_error', 0):.1f} 音分")

def multi_mode_comparison_demo(phi: float = PHI, delta_theta: float = 4.8):
    """多模式对比演示（使用实际数据）"""
    print("\n🎭 === 多演奏模式对比演示 ===")
    
    with create_player() as player:
        modes_to_demo = [
            ("solo_piano", "romantic", "浪漫主义钢琴独奏"),
            ("solo_piano", "classical", "古典主义钢琴独奏"),
            ("orchestral", "chamber", "室内乐编制"),
            ("comparison", "12tet_vs_petersen", "12平均律对比"),
        ]
        
        # 生成实际Petersen音阶数据（一个八度）
        demo_scale = generate_petersen_scale(phi=phi, delta_theta=delta_theta, max_entries=8)
        
        for mode, style_or_arrangement, description in modes_to_demo:
            print(f"\n🎵 演示模式: {description}")
            
            try:
                # 转换为player所需的格式
                scale_entries = [
                    {'freq': entry.freq, 'key_name': entry.key_name, 'cents_deviation': entry.cents_deviation}
                    for entry in demo_scale
                ]
                
                if mode == "orchestral":
                    success = player.play_petersen_scale(
                        scale_entries, mode=mode, arrangement=style_or_arrangement
                    )
                elif mode == "comparison":
                    success = player.play_petersen_scale(
                        scale_entries, mode=mode, comparison_type=style_or_arrangement
                    )
                else:
                    success = player.play_petersen_scale(
                        scale_entries, mode=mode, style=style_or_arrangement
                    )
                
                if success:
                    print(f"   ✅ {description} 演示完成")
                else:
                    print(f"   ⚠️  {description} 演示部分失败")
                    
            except Exception as e:
                print(f"   ❌ {description} 演示失败: {e}")

def expression_showcase(phi: float = PHI, delta_theta: float = 4.8):
    """表现力展示（使用实际数据）"""
    print("\n🎨 === 表现力风格展示 ===")
    
    with create_player() as player:
        # 生成实际Petersen音阶数据（短旋律）
        melody_scale = generate_petersen_scale(phi=phi, delta_theta=delta_theta, max_entries=5)
        
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

def effects_showcase(phi: float = PHI, delta_theta: float = 4.8):
    """音效展示（使用实际数据）"""
    print("\n🎛️  === 音效空间展示 ===")
    
    with create_player() as player:
        # 生成实际Petersen音阶数据（和弦）
        chord_entries = generate_petersen_scale(phi=phi, delta_theta=delta_theta, max_entries=4)
        
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

def educational_mode_demo(phi: float = PHI, delta_theta: float = 4.8):
    """教育模式演示（使用实际数据）"""
    print("\n📚 === 教育模式演示 ===")
    
    with create_player() as player:
        educational_lessons = [
            ("basic_theory", "基础理论"),
            ("frequency_analysis", "频率分析"),
            ("harmonic_series", "谐波系列")
        ]
        
        # 生成实际Petersen音阶数据
        demo_scale = generate_petersen_scale(phi=phi, delta_theta=delta_theta, max_entries=6)
        scale_entries = [
            {'freq': entry.freq, 'key_name': entry.key_name, 'cents_deviation': entry.cents_deviation}
            for entry in demo_scale
        ]
        
        for lesson_type, description in educational_lessons:
            print(f"\n📖 {description}课程:")
            
            success = player.play_petersen_scale(
                scale_entries,
                mode="educational",
                lesson_type=lesson_type
            )
            
            if success:
                print(f"   ✅ {description}课程完成")

def complete_system_showcase(phi: float = PHI, delta_theta: float = 4.8):
    """完整系统展示（使用实际数据）"""
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
        
        # 生成实际Petersen音阶数据
        full_scale = generate_petersen_scale(phi=phi, delta_theta=delta_theta, max_entries=15)
        scale_entries = [
            {'freq': entry.freq, 'key_name': entry.key_name, 'cents_deviation': entry.cents_deviation}
            for entry in full_scale
        ]
        
        # 演示完整Petersen音阶
        print(f"\n🎵 完整Petersen音阶演示 ({len(scale_entries)} 个音符):")
        success = player.play_petersen_scale(
            scale_entries,
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
    
    # 配置参数（可以根据需要调整）
    PHI_VALUE = PHI  # 黄金比例
    DELTA_THETA_VALUE = 4.8  # 原始Petersen系统
    
    try:
        petersen_analysis_demo(phi=PHI_VALUE, delta_theta=DELTA_THETA_VALUE)
        frequency_accuracy_demo(phi=PHI_VALUE, delta_theta=DELTA_THETA_VALUE)
        multi_mode_comparison_demo(phi=PHI_VALUE, delta_theta=DELTA_THETA_VALUE)
        expression_showcase(phi=PHI_VALUE, delta_theta=DELTA_THETA_VALUE)
        effects_showcase(phi=PHI_VALUE, delta_theta=DELTA_THETA_VALUE)
        educational_mode_demo(phi=PHI_VALUE, delta_theta=DELTA_THETA_VALUE)
        complete_system_showcase(phi=PHI_VALUE, delta_theta=DELTA_THETA_VALUE)
        
        print("\n🎉 Petersen音阶演示完成!")
        print("🎵 感谢您体验Enhanced Petersen Music System!")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        pass