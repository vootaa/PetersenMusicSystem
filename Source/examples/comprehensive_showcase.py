"""
综合功能展示程序
展示Enhanced Petersen Music System的所有核心功能
"""
import time
import math
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from enhanced_petersen_player import create_player, PlayerConfiguration
from utils.presets import COMPLETE_PRESET_COMBINATIONS, EFFECT_PRESET_LIBRARY
from utils.analysis import FrequencyAnalyzer

class ComprehensiveShowcase:
    """综合功能展示类"""
    
    def __init__(self):
        self.player = None
        self.demo_results = {}
        
    def initialize(self):
        """初始化系统"""
        print("🚀 Enhanced Petersen Music System 综合展示")
        print("="*60)
        
        try:
            # 创建高性能配置
            config = PlayerConfiguration(
                enable_accurate_frequency=True,
                enable_effects=True,
                enable_expression=True,
                auto_optimize_settings=True,
                sample_rate=48000,
                buffer_size=512
            )
            
            print("🔄 正在初始化高性能播放器...")
            self.player = create_player()
            
            print("✅ 系统初始化完成!")
            self._print_system_info()
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            raise
    
    def _print_system_info(self):
        """打印系统信息"""
        status = self.player.get_system_status()
        sf_summary = status['soundfont_summary']
        
        print(f"\n📊 系统信息:")
        print(f"   SoundFont数量: {sf_summary['total_soundfonts']}")
        print(f"   当前SoundFont: {sf_summary.get('current_soundfont', '自动选择中...')}")
        print(f"   可用演奏模式: {len(status['available_modes'])}")
        print(f"   精确频率播放: ✅ 启用")
        print(f"   高级音效: ✅ 启用")
        print(f"   表现力控制: ✅ 启用")
    
    def run_comprehensive_demo(self):
        """运行综合演示"""
        demos = [
            ("基础功能验证", self.demo_basic_functionality),
            ("SoundFont管理展示", self.demo_soundfont_management),
            ("精确频率播放", self.demo_frequency_accuracy),
            ("音效处理系统", self.demo_audio_effects),
            ("表现力控制", self.demo_expression_control),
            ("演奏模式展示", self.demo_performance_modes),
            ("预设系统演示", self.demo_preset_system),
            ("高级功能集成", self.demo_advanced_features),
            ("性能压力测试", self.demo_performance_test),
            ("教育功能展示", self.demo_educational_features)
        ]
        
        print(f"\n🎯 开始综合演示 ({len(demos)} 个模块):")
        
        for i, (name, demo_func) in enumerate(demos, 1):
            print(f"\n{'='*60}")
            print(f"📍 演示 {i}/{len(demos)}: {name}")
            print('='*60)
            
            try:
                start_time = time.time()
                result = demo_func()
                duration = time.time() - start_time
                
                self.demo_results[name] = {
                    'success': result.get('success', True) if isinstance(result, dict) else result,
                    'duration': duration,
                    'details': result if isinstance(result, dict) else {}
                }
                
                status = "✅ 成功" if self.demo_results[name]['success'] else "❌ 失败"
                print(f"\n{status} - 用时 {duration:.1f}秒")
                
                # 模块间暂停
                if i < len(demos):
                    time.sleep(2)
                    
            except Exception as e:
                print(f"\n❌ 演示异常: {e}")
                self.demo_results[name] = {
                    'success': False,
                    'duration': 0,
                    'error': str(e)
                }
        
        self._print_demo_summary()
    
    def demo_basic_functionality(self) -> Dict:
        """基础功能验证"""
        print("🔧 测试基础播放功能...")
        
        # 测试基础音符播放
        test_frequencies = [261.63, 293.66, 329.63, 349.23, 392.00]
        test_names = ["C4", "D4", "E4", "F4", "G4"]
        
        print("🎵 播放测试音符序列:")
        for freq, name in zip(test_frequencies, test_names):
            print(f"   {name}: {freq}Hz")
        
        success = self.player.play_frequencies(test_frequencies, test_names, duration=0.5, gap=0.2)
        
        # 测试系统状态
        status = self.player.get_system_status()
        notes_played = status['session_stats']['notes_played']
        
        return {
            'success': success,
            'notes_played': notes_played,
            'system_ready': status['status'] == 'ready'
        }
    
    def demo_soundfont_management(self) -> Dict:
        """SoundFont管理展示"""
        print("📁 SoundFont管理系统展示...")
        
        sf_manager = self.player.sf_manager
        sf_summary = sf_manager.get_soundfont_summary()
        
        print(f"发现 {sf_summary['total_soundfonts']} 个SoundFont文件")
        
        # 展示SoundFont详情
        for sf_name, details in list(sf_summary['soundfont_details'].items())[:3]:
            print(f"\n📂 {sf_name}:")
            print(f"   类型: {details['type']}")
            print(f"   大小: {details['size_mb']:.1f}MB")
            print(f"   质量分数: {details['quality_score']:.2f}")
            print(f"   乐器数量: {details['instrument_count']}")
            print(f"   推荐用途: {details['recommended_use']}")
        
        # 测试SoundFont切换
        available_soundfonts = list(sf_summary['soundfont_details'].keys())
        switch_success = True
        
        if len(available_soundfonts) > 1:
            print(f"\n🔄 测试SoundFont切换...")
            for sf_name in available_soundfonts[:2]:
                print(f"   切换到: {sf_name}")
                result = sf_manager.load_soundfont(sf_name)
                if not result:
                    switch_success = False
                    break
                time.sleep(1)
        
        # 测试乐器检测
        instruments = sf_manager.get_available_instruments()
        piano_instrument = sf_manager.find_best_piano_instrument()
        
        return {
            'success': True,
            'soundfont_count': sf_summary['total_soundfonts'],
            'switch_success': switch_success,
            'instrument_count': len(instruments),
            'piano_found': piano_instrument is not None
        }
    
    def demo_frequency_accuracy(self) -> Dict:
        """精确频率播放演示"""
        print("🎯 精确频率播放系统展示...")
        
        # 生成需要频率补偿的音符
        test_frequencies = [
            440.0,      # A4 - 标准
            442.5,      # 略高于A4
            438.2,      # 略低于A4
            523.77,     # 接近C5但不完全
            659.44      # 接近E5但需要微调
        ]
        
        print("🔍 分析频率精确度需求:")
        analysis = self.player.freq_player.analyze_frequency_accuracy(test_frequencies)
        
        print(f"   需要补偿的音符: {analysis['needs_compensation_count']}/{len(test_frequencies)}")
        print(f"   补偿百分比: {analysis['compensation_percentage']:.1f}%")
        print(f"   最大偏差: {analysis['max_deviation']:.1f} 音分")
        print(f"   平均偏差: {analysis['avg_deviation']:.1f} 音分")
        
        # 演示对比播放
        print("\n🔄 执行精确度对比演示:")
        comparison_success = self.player.demonstrate_frequency_accuracy(
            test_frequencies, ["Test1", "Test2", "Test3", "Test4", "Test5"]
        )
        
        return {
            'success': comparison_success,
            'compensation_needed': analysis['needs_compensation_count'],
            'max_deviation': analysis['max_deviation'],
            'compensation_effectiveness': analysis.get('compensation_effectiveness', 0)
        }
    
    def demo_audio_effects(self) -> Dict:
        """音效处理系统演示"""
        print("🎛️  音效处理系统展示...")
        
        # 测试频率（简单旋律）
        melody_frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 349.23, 329.63, 261.63]
        melody_names = ["C", "D", "E", "F", "G", "F", "E", "C"]
        
        # 测试不同音效预设
        test_presets = [
            ("dry", "干燥直接"),
            ("hall", "音乐厅"),
            ("cathedral", "大教堂"),
            ("intimate_salon", "私人沙龙")
        ]
        
        effects_success = True
        
        for preset_name, description in test_presets:
            if preset_name in EFFECT_PRESET_LIBRARY:
                print(f"\n🎵 应用音效: {description}")
                
                success = self.player.effects.apply_effect_preset(preset_name)
                if success:
                    print(f"   播放测试旋律...")
                    self.player.play_frequencies(
                        melody_frequencies[:4], melody_names[:4], 
                        duration=0.8, gap=0.1
                    )
                    time.sleep(0.5)
                else:
                    effects_success = False
        
        # 测试自定义音效
        print(f"\n🔧 测试自定义音效参数...")
        custom_settings = {
            'reverb': {'room_size': 0.6, 'damping': 0.2, 'width': 0.8, 'level': 0.5},
            'chorus': {'voices': 3, 'level': 1.0, 'speed': 0.3, 'depth': 7.0},
            'brightness': 70,
            'resonance': 60
        }
        
        custom_success = self.player.effects.apply_custom_settings(custom_settings)
        if custom_success:
            print("   自定义音效应用成功")
            self.player.play_frequencies(
                melody_frequencies[:3], melody_names[:3], 
                duration=1.0
            )
        
        return {
            'success': effects_success and custom_success,
            'presets_tested': len(test_presets),
            'custom_effects': custom_success
        }
    
    def demo_expression_control(self) -> Dict:
        """表现力控制演示"""
        print("🎭 表现力控制系统展示...")
        
        # 测试旋律
        phrase_frequencies = [261.63, 293.66, 329.63, 392.00, 440.00, 392.00, 329.63, 261.63]
        phrase_names = ["C", "D", "E", "G", "A", "G", "E", "C"]
        
        # 测试不同表现力风格
        expression_styles = [
            ("mechanical", "机械式"),
            ("romantic", "浪漫主义"),
            ("jazz", "爵士风格"),
            ("classical", "古典风格")
        ]
        
        expression_success = True
        
        for style, description in expression_styles:
            print(f"\n🎨 表现力风格: {description}")
            
            success = self.player.expression.apply_expression_preset(style)
            if success:
                # 计算表现力数据
                expression_data = self.player.expression.calculate_expression_sequence(
                    len(phrase_frequencies), phrase_frequencies, phrase_names
                )
                
                print(f"   力度范围: {min(expression_data['velocities'])}-{max(expression_data['velocities'])}")
                print(f"   时长变化: {min(expression_data['durations']):.2f}-{max(expression_data['durations']):.2f}s")
                print(f"   使用踏板: {any(expression_data['sustain_events'])}")
                
                # 播放表现力序列（只播放前4个音符）
                self.player.performance_modes._execute_expressive_sequence(
                    phrase_frequencies[:4], phrase_names[:4], 
                    {k: v[:4] for k, v in expression_data.items() if isinstance(v, list)}
                )
                time.sleep(0.5)
            else:
                expression_success = False
        
        # 测试踏板控制
        print(f"\n🦶 测试踏板控制...")
        self.player.expression.apply_pedal_control(True, False)  # 延音踏板
        time.sleep(0.5)
        self.player.expression.reset_pedals()
        
        return {
            'success': expression_success,
            'styles_tested': len(expression_styles),
            'pedal_control': True
        }
    
    def demo_performance_modes(self) -> Dict:
        """演奏模式展示"""
        print("🎯 演奏模式系统展示...")
        
        # 测试序列
        demo_frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
        demo_names = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
        
        # 测试不同演奏模式
        modes_tested = 0
        modes_success = 0
        
        # 1. 钢琴独奏模式
        print(f"\n🎹 测试钢琴独奏模式...")
        try:
            success = self.player.performance_modes.execute_solo_piano_mode(
                demo_frequencies[:5], demo_names[:5], "classical"
            )
            modes_tested += 1
            if success:
                modes_success += 1
        except Exception as e:
            print(f"   钢琴模式异常: {e}")
        
        time.sleep(1)
        
        # 2. 对比演示模式
        print(f"\n🔄 测试对比演示模式...")
        try:
            success = self.player.performance_modes.execute_comparison_demo(
                demo_frequencies[:4], demo_names[:4], "12tet_vs_petersen"
            )
            modes_tested += 1
            if success:
                modes_success += 1
        except Exception as e:
            print(f"   对比模式异常: {e}")
        
        time.sleep(1)
        
        # 3. 教育模式
        print(f"\n📚 测试教育模式...")
        try:
            success = self.player.performance_modes.execute_educational_mode(
                demo_frequencies[:3], demo_names[:3], "basic_theory"
            )
            modes_tested += 1
            if success:
                modes_success += 1
        except Exception as e:
            print(f"   教育模式异常: {e}")
        
        # 获取可用模式
        available_modes = self.player.performance_modes.get_available_modes()
        
        return {
            'success': modes_success == modes_tested and modes_tested > 0,
            'modes_tested': modes_tested,
            'modes_successful': modes_success,
            'available_modes': len(available_modes)
        }
    
    def demo_preset_system(self) -> Dict:
        """预设系统演示"""
        print("🎨 预设系统展示...")
        
        # 测试旋律
        preset_test_freq = [261.63, 329.63, 392.00, 523.25]
        preset_test_names = ["C", "E", "G", "C"]
        
        # 测试几个完整预设
        test_presets = list(COMPLETE_PRESET_COMBINATIONS.keys())[:3]
        presets_success = 0
        
        for preset_name in test_presets:
            preset = COMPLETE_PRESET_COMBINATIONS[preset_name]
            print(f"\n🎼 测试预设: {preset.name}")
            print(f"   {preset.description}")
            
            success = self.player.apply_preset_combination(
                preset.effect_preset, preset.expression_preset
            )
            
            if success:
                print(f"   播放测试序列...")
                self.player.play_frequencies(
                    preset_test_freq, preset_test_names, 
                    duration=0.8, gap=0.2
                )
                presets_success += 1
                time.sleep(0.5)
        
        # 测试预设推荐系统
        print(f"\n🤖 测试智能预设推荐...")
        available_soundfonts = list(self.player.sf_manager.soundfonts.keys())
        
        from utils.presets import recommend_preset_for_context
        recommended = recommend_preset_for_context("concert", None, available_soundfonts)
        print(f"   推荐预设: {recommended}")
        
        return {
            'success': presets_success == len(test_presets),
            'presets_tested': len(test_presets),
            'presets_successful': presets_success,
            'recommendation_system': bool(recommended)
        }
    
    def demo_advanced_features(self) -> Dict:
        """高级功能集成演示"""
        print("🚀 高级功能集成展示...")
        
        # 复杂音阶测试
        complex_frequencies = []
        complex_names = []
        
        # 生成微分音阶（Petersen风格）
        base_freq = 261.63  # C4
        for i in range(12):
            # 使用非平均律间隔
            ratio = 2 ** ((i + random.uniform(-0.1, 0.1)) / 12)
            freq = base_freq * ratio
            complex_frequencies.append(freq)
            complex_names.append(f"M{i+1}")
        
        print(f"🎼 测试复杂微分音阶 ({len(complex_frequencies)} 音符):")
        
        # 分析频率特性
        analysis = self.player.freq_player.analyze_frequency_accuracy(complex_frequencies)
        print(f"   需要补偿: {analysis['needs_compensation_count']} 音符")
        print(f"   最大偏差: {analysis['max_deviation']:.1f} 音分")
        
        # 应用最佳预设
        best_preset = "steinway_concert_grand"
        preset = COMPLETE_PRESET_COMBINATIONS[best_preset]
        self.player.apply_preset_combination(preset.effect_preset, preset.expression_preset)
        
        # 智能演奏
        print(f"🎵 执行智能演奏...")
        performance_success = self.player.play_petersen_scale(
            [type('Entry', (), {'freq': f, 'key_name': n})() 
             for f, n in zip(complex_frequencies, complex_names)],
            mode="solo_piano",
            style="romantic"
        )
        
        # 获取播放统计
        status = self.player.get_system_status()
        session_stats = status['session_stats']
        
        return {
            'success': performance_success,
            'complex_notes': len(complex_frequencies),
            'compensation_rate': analysis['compensation_percentage'],
            'total_notes_played': session_stats['notes_played'],
            'total_sequences': session_stats['sequences_played']
        }
    
    def demo_performance_test(self) -> Dict:
        """性能压力测试"""
        print("⚡ 性能压力测试...")
        
        # 生成大量音符
        stress_frequencies = []
        stress_names = []
        
        base_freq = 220.0  # A3
        for i in range(50):  # 50个音符的压力测试
            freq = base_freq * (2 ** (i / 12))
            stress_frequencies.append(freq)
            stress_names.append(f"S{i+1}")
        
        print(f"🏃‍♂️ 压力测试: {len(stress_frequencies)} 音符快速播放")
        
        # 记录开始时间
        start_time = time.time()
        
        # 快速播放
        success = self.player.play_frequencies(
            stress_frequencies, stress_names, 
            duration=0.1, gap=0.05, show_progress=False
        )
        
        # 计算性能指标
        end_time = time.time()
        total_time = end_time - start_time
        notes_per_second = len(stress_frequencies) / total_time if total_time > 0 else 0
        
        print(f"   总时间: {total_time:.2f}秒")
        print(f"   播放速率: {notes_per_second:.1f} 音符/秒")
        
        # 内存和资源测试
        status = self.player.get_system_status()
        
        return {
            'success': success,
            'notes_count': len(stress_frequencies),
            'total_time': total_time,
            'notes_per_second': notes_per_second,
            'performance_rating': 'excellent' if notes_per_second > 20 else 'good' if notes_per_second > 10 else 'acceptable'
        }
    
    def demo_educational_features(self) -> Dict:
        """教育功能展示"""
        print("📚 教育功能展示...")
        
        # 教学序列
        educational_frequencies = [261.63, 293.66, 329.63, 349.23, 392.00]
        educational_names = ["C (宫)", "D (商)", "E (角)", "F (变徵)", "G (徵)"]
        
        # 理论分析演示
        print(f"🔍 音乐理论分析:")
        for freq, name in zip(educational_frequencies, educational_names):
            midi_note, cents_off, note_name = FrequencyAnalyzer.find_closest_midi_note(freq)
            print(f"   {name}: {freq:.2f}Hz → MIDI {midi_note} ({note_name}, {cents_off:+.1f}音分)")
        
        # 执行教育模式
        print(f"\n📖 基础理论课程:")
        theory_success = self.player.performance_modes.execute_educational_mode(
            educational_frequencies, educational_names, "basic_theory"
        )
        
        time.sleep(1)
        
        print(f"\n🔬 频率分析课程:")
        analysis_success = self.player.performance_modes.execute_educational_mode(
            educational_frequencies, educational_names, "frequency_analysis"
        )
        
        # 生成学习报告
        learning_report = {
            'frequencies_analyzed': len(educational_frequencies),
            'theory_concepts': ['宫商角徵羽', '十二平均律', 'MIDI音符映射', '音分计算'],
            'practical_exercises': ['音阶播放', '频率对比', '精确度分析']
        }
        
        print(f"\n📊 学习报告生成:")
        for concept in learning_report['theory_concepts']:
            print(f"   ✓ {concept}")
        
        return {
            'success': theory_success and analysis_success,
            'concepts_covered': len(learning_report['theory_concepts']),
            'exercises_completed': len(learning_report['practical_exercises']),
            'learning_report': learning_report
        }
    
    def _print_demo_summary(self):
        """打印演示总结"""
        print("\n" + "="*60)
        print("📊 综合演示总结报告")
        print("="*60)
        
        total_demos = len(self.demo_results)
        successful_demos = sum(1 for result in self.demo_results.values() if result['success'])
        total_time = sum(result['duration'] for result in self.demo_results.values())
        
        print(f"📈 总体统计:")
        print(f"   演示模块总数: {total_demos}")
        print(f"   成功模块数: {successful_demos}")
        print(f"   成功率: {successful_demos/total_demos*100:.1f}%")
        print(f"   总演示时间: {total_time:.1f}秒")
        
        print(f"\n📋 详细结果:")
        for name, result in self.demo_results.items():
            status = "✅" if result['success'] else "❌"
            duration = result['duration']
            print(f"   {status} {name}: {duration:.1f}秒")
            
            if not result['success'] and 'error' in result:
                print(f"      错误: {result['error']}")
        
        # 系统最终状态
        if self.player:
            final_status = self.player.get_system_status()
            final_stats = final_status['session_stats']
            
            print(f"\n📊 会话统计:")
            print(f"   总播放音符: {final_stats['notes_played']}")
            print(f"   播放序列数: {final_stats['sequences_played']}")
            print(f"   总播放时长: {final_stats['total_play_time']:.1f}秒")
            print(f"   加载SoundFont: {final_stats['soundfonts_loaded']}")
        
        # 功能评级
        if successful_demos == total_demos:
            rating = "🏆 卓越"
        elif successful_demos >= total_demos * 0.8:
            rating = "🥇 优秀"
        elif successful_demos >= total_demos * 0.6:
            rating = "🥈 良好"
        else:
            rating = "🥉 需要改进"
        
        print(f"\n🎯 系统评级: {rating}")
        print("="*60)
    
    def cleanup(self):
        """清理资源"""
        if self.player:
            self.player.cleanup()

def main():
    """主函数"""
    showcase = ComprehensiveShowcase()
    
    try:
        # 初始化系统
        showcase.initialize()
        
        # 运行综合演示
        showcase.run_comprehensive_demo()
        
        print("\n🎉 Enhanced Petersen Music System 综合展示完成!")
        print("感谢您的耐心观看，希望您对系统功能有了全面了解。")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        showcase.cleanup()

if __name__ == "__main__":
    main()