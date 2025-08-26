"""
演奏模式模块
提供不同类型的演奏模式：钢琴独奏、管弦乐、对比演示等
"""
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .frequency_accurate import FrequencyAccuratePlayback
from .audio_effects import AdvancedAudioEffects
from .expression_control import ExpressionController
from .soundfont_manager import SoundFontManager

class PerformanceMode(Enum):
    """演奏模式枚举"""
    SOLO_PIANO = "solo_piano"
    ORCHESTRAL = "orchestral"
    COMPARISON_DEMO = "comparison_demo"
    FREQUENCY_ANALYSIS = "frequency_analysis"
    EDUCATIONAL = "educational"
    CREATIVE_EXPLORATION = "creative_exploration"

@dataclass
class PerformancePlan:
    """演奏计划"""
    mode: PerformanceMode
    soundfont_name: str
    instrument_program: int
    effect_preset: str
    expression_preset: str
    frequencies: List[float]
    key_names: List[str]
    description: str
    estimated_duration: float

class PerformanceModes:
    """演奏模式控制器"""
    
    def __init__(self, 
                 frequency_player: FrequencyAccuratePlayback,
                 effects_controller: AdvancedAudioEffects,
                 expression_controller: ExpressionController,
                 soundfont_manager: SoundFontManager):
        """
        初始化演奏模式控制器
        
        Args:
            frequency_player: 精确频率播放器
            effects_controller: 音效控制器
            expression_controller: 表现力控制器
            soundfont_manager: SoundFont管理器
        """
        self.freq_player = frequency_player
        self.effects = effects_controller
        self.expression = expression_controller
        self.sf_manager = soundfont_manager
        
        # 演奏历史
        self.performance_history: List[Dict] = []
        
        print("✓ 演奏模式控制器已初始化")
    
    def execute_solo_piano_mode(self, 
                               frequencies: List[float],
                               key_names: Optional[List[str]] = None,
                               style: str = "romantic") -> bool:
        """
        执行钢琴独奏模式
        
        Args:
            frequencies: 频率列表
            key_names: 音名列表
            style: 演奏风格 ("classical", "romantic", "jazz", "study")
            
        Returns:
            执行成功返回True
        """
        print(f"\n🎹 === 钢琴独奏模式: {style}风格 ===")
        
        # 选择最佳钢琴SoundFont
        best_sf = self.sf_manager.get_best_soundfont_for_task("piano")
        if not best_sf:
            print("❌ 未找到适合的钢琴SoundFont")
            return False
        
        # 加载SoundFont
        if not self.sf_manager.load_soundfont(best_sf):
            return False
        
        # 选择最佳钢琴乐器
        best_piano = self.sf_manager.find_best_piano_instrument()
        if not best_piano:
            print("❌ 未找到钢琴乐器")
            return False
        
        # 切换到钢琴音色
        result = self.freq_player.fluidsynth.fluid_synth_program_change(
            self.freq_player.synth, self.freq_player.current_channel, best_piano.program
        )
        if result != 0:
            print(f"⚠️  乐器切换警告: {result}")
        
        print(f"🎵 使用乐器: {best_piano.name} (程序 {best_piano.program})")
        
        # 应用音效设置
        if best_sf.lower().find('steinway') >= 0:
            effect_preset = "steinway_concert"
        else:
            effect_preset = "hall"
        
        self.effects.apply_effect_preset(effect_preset)
        
        # 应用表现力设置
        expression_preset = self._map_style_to_expression(style)
        self.expression.apply_expression_preset(expression_preset)
        
        # 计算表现力序列
        expression_data = self.expression.calculate_expression_sequence(
            len(frequencies), frequencies, key_names
        )
        
        print(f"🎼 准备演奏 {len(frequencies)} 个音符，预计时长 {expression_data['total_duration']:.1f}秒")
        
        # 执行演奏
        success = self._execute_expressive_sequence(
            frequencies, key_names, expression_data
        )
        
        # 记录演奏
        self._record_performance({
            'mode': PerformanceMode.SOLO_PIANO,
            'style': style,
            'soundfont': best_sf,
            'instrument': best_piano.name,
            'note_count': len(frequencies),
            'duration': expression_data['total_duration'],
            'success': success
        })
        
        return success
    
    def execute_orchestral_mode(self,
                               frequencies: List[float],
                               key_names: Optional[List[str]] = None,
                               arrangement: str = "chamber") -> bool:
        """
        执行管弦乐模式
        
        Args:
            frequencies: 频率列表
            key_names: 音名列表
            arrangement: 编制类型 ("chamber", "symphonic", "mixed")
            
        Returns:
            执行成功返回True
        """
        print(f"\n🎺 === 管弦乐模式: {arrangement}编制 ===")
        
        # 选择管弦乐SoundFont
        best_sf = self.sf_manager.get_best_soundfont_for_task("orchestral")
        if not best_sf:
            print("❌ 未找到适合的管弦乐SoundFont")
            return False
        
        if not self.sf_manager.load_soundfont(best_sf):
            return False
        
        # 选择乐器组合
        instruments = self._select_orchestral_instruments(arrangement)
        if not instruments:
            print("❌ 未找到适合的管弦乐器")
            return False
        
        # 应用管弦乐音效
        self.effects.apply_effect_preset("orchestral")
        self.expression.apply_expression_preset("classical")
        
        # 分配频率到不同乐器
        instrument_assignments = self._assign_frequencies_to_instruments(
            frequencies, key_names, instruments
        )
        
        print(f"🎼 管弦乐演奏计划:")
        for inst_name, (program, freqs, names) in instrument_assignments.items():
            print(f"  - {inst_name}: {len(freqs)} 个音符")
        
        # 逐乐器演奏
        total_success = True
        for inst_name, (program, freqs, names) in instrument_assignments.items():
            print(f"\n🎵 演奏 {inst_name}...")
            
            # 切换乐器
            result = self.freq_player.fluidsynth.fluid_synth_program_change(
                self.freq_player.synth, self.freq_player.current_channel, program
            )
            if result != 0:
                print(f"⚠️  乐器切换警告: {result}")
            
            # 计算表现力
            expression_data = self.expression.calculate_expression_sequence(
                len(freqs), freqs, names
            )
            
            # 演奏这个乐器的部分
            success = self._execute_expressive_sequence(freqs, names, expression_data)
            if not success:
                total_success = False
            
            # 乐器间暂停
            time.sleep(1.0)
        
        # 记录演奏
        self._record_performance({
            'mode': PerformanceMode.ORCHESTRAL,
            'arrangement': arrangement,
            'soundfont': best_sf,
            'instruments': list(instrument_assignments.keys()),
            'note_count': len(frequencies),
            'success': total_success
        })
        
        return total_success
    
    def execute_comparison_demo(self,
                               frequencies: List[float],
                               key_names: Optional[List[str]] = None,
                               comparison_type: str = "12tet_vs_petersen") -> bool:
        """
        执行对比演示模式
        
        Args:
            frequencies: 频率列表
            key_names: 音名列表
            comparison_type: 对比类型
            
        Returns:
            执行成功返回True
        """
        print(f"\n🔄 === 对比演示模式: {comparison_type} ===")
        
        if comparison_type == "12tet_vs_petersen":
            return self._demo_12tet_vs_petersen(frequencies, key_names)
        elif comparison_type == "soundfont_quality":
            return self._demo_soundfont_quality(frequencies, key_names)
        elif comparison_type == "expression_styles":
            return self._demo_expression_styles(frequencies, key_names)
        else:
            print(f"❌ 未知对比类型: {comparison_type}")
            return False
    
    def execute_educational_mode(self,
                                frequencies: List[float],
                                key_names: Optional[List[str]] = None,
                                lesson_type: str = "basic_theory") -> bool:
        """
        执行教育模式
        
        Args:
            frequencies: 频率列表
            key_names: 音名列表
            lesson_type: 课程类型
            
        Returns:
            执行成功返回True
        """
        print(f"\n📚 === 教育模式: {lesson_type} ===")
        
        if lesson_type == "basic_theory":
            return self._lesson_basic_theory(frequencies, key_names)
        elif lesson_type == "frequency_analysis":
            return self._lesson_frequency_analysis(frequencies, key_names)
        elif lesson_type == "harmonic_series":
            return self._lesson_harmonic_series(frequencies, key_names)
        else:
            print(f"❌ 未知课程类型: {lesson_type}")
            return False
    
    def _map_style_to_expression(self, style: str) -> str:
        """将演奏风格映射到表现力预设"""
        style_mapping = {
            'classical': 'classical',
            'romantic': 'romantic',
            'jazz': 'jazz',
            'study': 'study',
            'gentle': 'gentle',
            'dramatic': 'dramatic',
            'mechanical': 'mechanical'
        }
        return style_mapping.get(style, 'expressive')
    
    def _select_orchestral_instruments(self, arrangement: str) -> List[Tuple[str, int]]:
        """选择管弦乐器组合"""
        available_instruments = self.sf_manager.get_available_instruments()
        
        if arrangement == "chamber":
            # 室内乐编制
            desired = ["violin", "cello", "flute", "acoustic_grand"]
        elif arrangement == "symphonic":
            # 交响乐编制
            desired = ["violin", "viola", "cello", "flute", "oboe", "trumpet", "french_horn"]
        else:  # mixed
            # 混合编制
            desired = ["violin", "cello", "flute", "trumpet", "acoustic_grand"]
        
        selected = []
        for instrument in available_instruments:
            if any(d in instrument.name.lower() or d in instrument.category for d in desired):
                selected.append((instrument.name, instrument.program))
                if len(selected) >= len(desired):
                    break
        
        return selected
    
    def _assign_frequencies_to_instruments(self, 
                                         frequencies: List[float],
                                         key_names: Optional[List[str]],
                                         instruments: List[Tuple[str, int]]) -> Dict[str, Tuple[int, List[float], List[str]]]:
        """将频率分配给不同乐器"""
        if not instruments:
            return {}
        
        assignments = {}
        
        # 按频率范围分配
        sorted_freq_indices = sorted(range(len(frequencies)), key=lambda i: frequencies[i])
        
        # 将频率分组
        group_size = max(1, len(frequencies) // len(instruments))
        
        for i, (inst_name, program) in enumerate(instruments):
            start_idx = i * group_size
            end_idx = min((i + 1) * group_size, len(frequencies))
            
            if i == len(instruments) - 1:  # 最后一个乐器承担剩余所有频率
                end_idx = len(frequencies)
            
            indices = sorted_freq_indices[start_idx:end_idx]
            inst_frequencies = [frequencies[idx] for idx in indices]
            inst_names = [key_names[idx] if key_names else f"F{idx}" for idx in indices]
            
            assignments[inst_name] = (program, inst_frequencies, inst_names)
        
        return assignments
    
    def _execute_expressive_sequence(self,
                                   frequencies: List[float],
                                   key_names: Optional[List[str]],
                                   expression_data: Dict) -> bool:
        """执行有表现力的序列演奏"""
        if not frequencies:
            return True
        
        velocities = expression_data['velocities']
        durations = expression_data['durations']
        gaps = expression_data['gaps']
        sustain_events = expression_data['sustain_events']
        soft_events = expression_data['soft_events']
        microtimings = expression_data['microtimings']
        
        names = key_names or [f"F{i+1}" for i in range(len(frequencies))]
        
        success_count = 0
        
        for i, (freq, name, vel, dur, gap, sustain, soft, microtiming) in enumerate(zip(
            frequencies, names, velocities, durations, gaps, sustain_events, soft_events, microtimings
        )):
            # 应用踏板控制
            self.expression.apply_pedal_control(sustain, soft)
            
            # 微调时间
            if microtiming != 0:
                time.sleep(abs(microtiming))
            
            # 播放音符
            print(f"[{i+1:3d}/{len(frequencies)}] {name}: {freq:.2f}Hz, 力度:{vel}, 时长:{dur:.2f}s", 
                  end="")
            if sustain:
                print(" [延音]", end="")
            if soft:
                print(" [弱音]", end="")
            print()
            
            success = self.freq_player.play_accurate_note(freq, vel, dur, name)
            if success:
                success_count += 1
            
            # 间隔时间
            if gap > 0 and i < len(frequencies) - 1:
                time.sleep(gap)
        
        # 重置踏板
        self.expression.reset_pedals()
        
        return success_count == len(frequencies)
    
    def _demo_12tet_vs_petersen(self, frequencies: List[float], key_names: Optional[List[str]]) -> bool:
        """12平均律 vs Petersen对比演示"""
        print("🔄 播放对比: 12平均律 vs Petersen精确频率")
        
        # 设置简洁的表现力
        self.expression.apply_expression_preset("mechanical")
        self.effects.apply_effect_preset("dry")
        
        # 使用高质量钢琴
        best_sf = self.sf_manager.get_best_soundfont_for_task("piano")
        if best_sf and self.sf_manager.load_soundfont(best_sf):
            best_piano = self.sf_manager.find_best_piano_instrument()
            if best_piano:
                self.freq_player.fluidsynth.fluid_synth_program_change(
                    self.freq_player.synth, self.freq_player.current_channel, best_piano.program
                )
        
        # 执行对比演示
        self.freq_player.compare_frequencies_demo(frequencies, key_names, 1.5, 1.0)
        
        return True
    
    def _demo_soundfont_quality(self, frequencies: List[float], key_names: Optional[List[str]]) -> bool:
        """SoundFont质量对比演示"""
        print("🔄 SoundFont质量对比演示")
        
        # 获取所有可用的SoundFont，按质量排序
        sf_summary = self.sf_manager.get_soundfont_summary()
        sorted_soundfonts = sorted(
            sf_summary['soundfont_details'].items(),
            key=lambda x: x[1]['quality_score'],
            reverse=True
        )
        
        demo_count = 0
        for sf_name, sf_info in sorted_soundfonts:
            if demo_count >= 3:  # 最多演示3个
                break
            
            print(f"\n🎵 演示 SoundFont: {sf_name} (质量: {sf_info['quality_score']:.2f})")
            
            if self.sf_manager.load_soundfont(sf_name):
                # 播放前几个音符作为演示
                demo_frequencies = frequencies[:min(5, len(frequencies))]
                demo_names = key_names[:len(demo_frequencies)] if key_names else None
                
                self.freq_player.play_accurate_sequence(demo_frequencies, show_progress=False)
                
                demo_count += 1
                time.sleep(2.0)  # 演示间暂停
        
        return True
    
    def _demo_expression_styles(self, frequencies: List[float], key_names: Optional[List[str]]) -> bool:
        """表现力风格对比演示"""
        print("🔄 表现力风格对比演示")
        
        styles = ['mechanical', 'romantic', 'jazz', 'classical']
        
        for style in styles:
            print(f"\n🎵 演示风格: {style}")
            
            self.expression.apply_expression_preset(style)
            expression_data = self.expression.calculate_expression_sequence(
                len(frequencies), frequencies, key_names
            )
            
            # 播放前几个音符作为演示
            demo_count = min(8, len(frequencies))
            demo_frequencies = frequencies[:demo_count]
            demo_names = key_names[:demo_count] if key_names else None
            
            # 提取对应的表现力数据
            demo_expression = {
                'velocities': expression_data['velocities'][:demo_count],
                'durations': expression_data['durations'][:demo_count],
                'gaps': expression_data['gaps'][:demo_count],
                'sustain_events': expression_data['sustain_events'][:demo_count],
                'soft_events': expression_data['soft_events'][:demo_count],
                'microtimings': expression_data['microtimings'][:demo_count]
            }
            
            self._execute_expressive_sequence(demo_frequencies, demo_names, demo_expression)
            time.sleep(2.0)  # 风格间暂停
        
        return True
    
    def _lesson_basic_theory(self, frequencies: List[float], key_names: Optional[List[str]]) -> bool:
        """基础理论课程"""
        print("📚 Petersen音阶基础理论")
        print("本课程将演示Petersen音阶的基本特征...")
        
        # 设置教学用的清晰音效
        self.effects.apply_effect_preset("intimate")
        self.expression.apply_expression_preset("study")
        
        # 逐个播放并解释
        for i, freq in enumerate(frequencies[:10]):  # 限制前10个音符
            name = key_names[i] if key_names and i < len(key_names) else f"音符{i+1}"
            
            print(f"\n📖 {name}: {freq:.3f} Hz")
            
            # 分析这个频率
            analysis = self.freq_player.analyze_frequency_accuracy([freq])
            if analysis['needs_compensation_count'] > 0:
                print(f"   ⚡ 需要频率补偿: {analysis['cents_deviations'][0]:.1f} 音分")
            else:
                print(f"   ✓ 接近12平均律标准")
            
            # 播放音符
            self.freq_player.play_accurate_note(freq, 80, 1.0, name)
            time.sleep(0.5)
        
        return True
    
    def _lesson_frequency_analysis(self, frequencies: List[float], key_names: Optional[List[str]]) -> bool:
        """频率分析课程"""
        print("📚 Petersen音阶频率分析")
        
        # 完整分析
        analysis = self.freq_player.analyze_frequency_accuracy(frequencies)
        
        print(f"\n📊 分析结果:")
        print(f"   总音符数: {len(frequencies)}")
        print(f"   频率范围: {analysis['frequency_range'][0]:.1f} - {analysis['frequency_range'][1]:.1f} Hz")
        print(f"   需要补偿: {analysis['needs_compensation_count']} ({analysis['compensation_percentage']:.1f}%)")
        print(f"   最大偏差: {analysis['max_deviation']:.1f} 音分")
        print(f"   平均偏差: {analysis['avg_deviation']:.1f} 音分")
        
        return True
    
    def _lesson_harmonic_series(self, frequencies: List[float], key_names: Optional[List[str]]) -> bool:
        """谐波系列课程"""
        print("📚 Petersen音阶与谐波系列")
        
        # 选择基频并计算谐波
        if frequencies:
            base_freq = min(frequencies)
            harmonics = [base_freq * i for i in range(1, 9)]  # 前8个谐波
            
            print(f"基频: {base_freq:.3f} Hz")
            print("谐波系列:")
            
            for i, harmonic in enumerate(harmonics, 1):
                print(f"   第{i}谐波: {harmonic:.3f} Hz")
                self.freq_player.play_accurate_note(harmonic, 70, 0.8)
                time.sleep(0.3)
        
        return True
    
    def _record_performance(self, performance_data: Dict) -> None:
        """记录演奏信息"""
        performance_data['timestamp'] = time.time()
        self.performance_history.append(performance_data)
        
        # 保持历史记录在合理范围内
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-50:]
    
    def get_performance_history(self) -> List[Dict]:
        """获取演奏历史"""
        return self.performance_history.copy()
    
    def get_available_modes(self) -> Dict[str, List[str]]:
        """获取可用的演奏模式"""
        return {
            'solo_piano': ['classical', 'romantic', 'jazz', 'study', 'gentle', 'dramatic'],
            'orchestral': ['chamber', 'symphonic', 'mixed'],
            'comparison_demo': ['12tet_vs_petersen', 'soundfont_quality', 'expression_styles'],
            'educational': ['basic_theory', 'frequency_analysis', 'harmonic_series']
        }