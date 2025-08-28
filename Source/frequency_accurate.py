"""
精确频率播放模块
实现真正的Petersen音阶频率播放，而非12平均律近似
"""
import time
import math
import ctypes
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass

import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.analysis import FrequencyAnalyzer
from utils.constants import (
    FREQUENCY_TOLERANCE_CENTS, MAX_PITCH_BEND_CENTS, 
    PITCH_BEND_NEUTRAL, DEFAULT_PLAY_PARAMS
)

@dataclass
class AccurateNote:
    """精确音符数据"""
    target_frequency: float
    midi_note: int
    standard_frequency: float
    cents_deviation: float
    pitch_bend_value: int
    needs_compensation: bool
    key_name: str = ""
    
class FrequencyAccuratePlayback:
    """精确频率播放控制器"""
    
    def __init__(self, fluidsynth_lib, synth, current_channel: int = 0):
        """
        初始化精确频率播放器
        
        Args:
            fluidsynth_lib: FluidSynth动态库对象
            synth: FluidSynth合成器对象  
            current_channel: 当前MIDI通道
        """
        self.fluidsynth = fluidsynth_lib
        self.synth = synth
        self.current_channel = current_channel
        self.a4_frequency = 440.0
        self.pitch_bend_range_cents = 200.0  # 默认弯音轮范围
        
        # 统计信息
        self.accuracy_stats = {
            'total_notes_played': 0,
            'compensated_notes': 0,
            'max_deviation_played': 0.0,
            'avg_deviation': 0.0
        }
        
        # 设置弯音轮范围
        self._setup_pitch_bend_range()
    
    def _setup_pitch_bend_range(self):
        """设置弯音轮范围"""
        try:
            # 尝试设置弯音轮范围为200音分（2个半音）
            # 这是大多数合成器的标准设置
            if hasattr(self.fluidsynth, 'fluid_synth_set_pitch_bend_range'):
                result = self.fluidsynth.fluid_synth_set_pitch_bend_range(
                    self.synth, self.current_channel, 200
                )
                if result == 0:
                    print(f"✓ 弯音轮范围设置为 {self.pitch_bend_range_cents} 音分")
                else:
                    print(f"⚠️  弯音轮范围设置可能失败")
        except AttributeError:
            print("⚠️  FluidSynth版本不支持弯音轮范围设置，使用默认值")
    
    def prepare_accurate_note(self, target_frequency: float, key_name: str = "") -> AccurateNote:
        """
        准备精确音符数据
        
        Args:
            target_frequency: 目标频率
            key_name: 音名（可选）
            
        Returns:
            AccurateNote对象
        """
        # 找到最接近的MIDI音符
        midi_note, standard_freq, cents_deviation = FrequencyAnalyzer.find_closest_midi_note(
            target_frequency, self.a4_frequency
        )
        
        # 计算弯音轮值
        pitch_bend_value = FrequencyAnalyzer.calculate_pitch_bend(
            target_frequency, midi_note, self.a4_frequency, self.pitch_bend_range_cents
        )
        
        # 判断是否需要补偿
        needs_compensation = abs(cents_deviation) > FREQUENCY_TOLERANCE_CENTS
        
        return AccurateNote(
            target_frequency=target_frequency,
            midi_note=midi_note,
            standard_frequency=standard_freq,
            cents_deviation=cents_deviation,
            pitch_bend_value=pitch_bend_value,
            needs_compensation=needs_compensation,
            key_name=key_name
        )
    
    def play_accurate_note(self, 
                          target_frequency: float,
                          velocity: int = 80,
                          duration: float = 0.5,
                          key_name: Optional[str] = None,
                          force_compensation: bool = False) -> bool:
        """
        播放精确频率音符
        
        Args:
            target_frequency: 目标频率
            velocity: 力度 (1-127)
            duration: 持续时间(秒)
            key_name: 音名(用于显示)
            force_compensation: 强制使用频率补偿
            
        Returns:
            播放成功返回True
        """
        try:
            # 准备音符数据
            note = self.prepare_accurate_note(target_frequency, key_name)
            
            # 显示信息
            compensation_info = ""
            if note.needs_compensation or force_compensation:
                compensation_info = f" [补偿: {note.cents_deviation:+.1f}¢]"
            
            print(f"播放: {note.key_name} {target_frequency:.3f}Hz → MIDI{note.midi_note}" + compensation_info)
            
            # 应用弯音轮补偿
            if (note.needs_compensation or force_compensation) and abs(note.cents_deviation) <= MAX_PITCH_BEND_CENTS:
                result = self.fluidsynth.fluid_synth_pitch_bend(
                    self.synth, self.current_channel, note.pitch_bend_value
                )
                if result != 0:
                    print(f"⚠️  弯音轮设置警告: 返回码 {result}")
                
                self.accuracy_stats['compensated_notes'] += 1
            
            # 播放音符
            try:
                result_on = self.fluidsynth.fluid_synth_noteon(
                    self.synth, self.current_channel, note.midi_note, velocity
                )
                if result_on != 0:
                    print(f"⚠️  noteon警告: 返回码 {result_on}")
            except Exception as e:
                print(f"❌ FluidSynth调用异常: {e}")
                return False
                
            # 持续时间
            time.sleep(duration)
            
            # 停止音符
            result_off = self.fluidsynth.fluid_synth_noteoff(
                self.synth, self.current_channel, note.midi_note
            )
            if result_off != 0:
                print(f"⚠️  noteoff警告: 返回码 {result_off}")
            
            # 重置弯音轮
            if note.needs_compensation or force_compensation:
                self.fluidsynth.fluid_synth_pitch_bend(
                    self.synth, self.current_channel, PITCH_BEND_NEUTRAL
                )
            
            # 更新统计
            self._update_accuracy_stats(note)
            
            return True
            
        except Exception as e:
            print(f"❌ 播放失败: {e}")
            return False
    
    def play_accurate_sequence(self,
                            frequencies: List[float],
                            velocities: Optional[List[int]] = None,
                            durations: Optional[List[float]] = None,
                            gaps: Optional[List[float]] = None,
                            key_names: Optional[List[str]] = None,
                            show_progress: bool = True) -> int:
        """
        播放精确频率序列
        
        Args:
            frequencies: 频率列表
            velocities: 力度列表(可选)
            durations: 持续时间列表(可选) 
            gaps: 间隔时间列表(可选)
            key_names: 音名列表(可选)
            show_progress: 显示进度
            
        Returns:
            成功播放的音符数
        """
        if not frequencies:
            print("❌ 空的频率列表")
            return 0
        
        count = len(frequencies)
        
        # 填充默认参数
        if velocities is None:
            velocities = [DEFAULT_PLAY_PARAMS['velocity']] * count
        if durations is None:
            durations = [DEFAULT_PLAY_PARAMS['duration']] * count
        if gaps is None:
            gaps = [DEFAULT_PLAY_PARAMS['gap']] * count
        if key_names is None:
            key_names = [""] * count
        
        # 确保列表长度一致
        velocities = (velocities * count)[:count]
        durations = (durations * count)[:count]
        gaps = (gaps * count)[:count]
        key_names = (key_names * count)[:count]
        
        if show_progress:
            print(f"=== 精确频率序列播放: {count} 个音符 ===")
        
        played_count = 0
        
        for i, (freq, vel, dur, gap, name) in enumerate(zip(
            frequencies, velocities, durations, gaps, key_names
        )):
            if show_progress:
                print(f"[{i+1:3d}/{count}] ", end="")
            
            if self.play_accurate_note(freq, vel, dur, name):
                played_count += 1
            
            # 间隔时间
            if gap > 0 and i < count - 1:
                time.sleep(gap)
        
        if show_progress:
            print(f"✓ 序列播放完成: {played_count}/{count}")
            self._print_accuracy_summary()
        
        return played_count
    
    def compare_frequencies_demo(self, 
                               frequencies: List[float],
                               key_names: Optional[List[str]] = None,
                               comparison_duration: float = 1.0,
                               pause_between: float = 0.5) -> None:
        """
        频率对比演示：先播放12平均律近似，再播放精确频率
        
        Args:
            frequencies: 要对比的频率列表
            key_names: 音名列表
            comparison_duration: 每个音符的持续时间
            pause_between: 对比之间的暂停时间
        """
        if not frequencies:
            return
        
        if key_names is None:
            key_names = [f"F{i+1}" for i in range(len(frequencies))]
        
        print(f"\n=== 频率对比演示 ===")
        print("先播放12平均律近似音高，再播放Petersen精确频率")
        
        for i, (freq, name) in enumerate(zip(frequencies, key_names)):
            note = self.prepare_accurate_note(freq, name)
            
            print(f"\n[{i+1}] {name}: {freq:.3f} Hz (偏差: {note.cents_deviation:+.1f}¢)")
            
            # 播放12平均律版本
            print("  → 12平均律近似:", end=" ")
            self.play_accurate_note(note.standard_frequency, 80, comparison_duration, force_compensation=False)
            time.sleep(pause_between)
            
            # 播放精确频率版本
            print("  → Petersen精确:", end=" ")
            self.play_accurate_note(freq, 80, comparison_duration, force_compensation=True)
            time.sleep(pause_between * 2)
    
    def analyze_frequency_accuracy(self, frequencies: List[float]) -> Dict:
        """
        分析频率精确度需求
        
        Args:
            frequencies: 频率列表
            
        Returns:
            精确度分析结果
        """
        analysis = FrequencyAnalyzer.analyze_frequency_deviation(frequencies, self.a4_frequency)
        
        # 添加播放相关的分析
        notes = [self.prepare_accurate_note(f) for f in frequencies]
        
        extreme_deviations = [n for n in notes if abs(n.cents_deviation) > MAX_PITCH_BEND_CENTS]
        
        analysis.update({
            'pitch_bend_compensation_needed': sum(1 for n in notes if n.needs_compensation),
            'extreme_deviations': len(extreme_deviations),
            'extreme_deviation_frequencies': [n.target_frequency for n in extreme_deviations],
            'playable_with_compensation': len(notes) - len(extreme_deviations),
            'compensation_effectiveness': (len(notes) - len(extreme_deviations)) / len(notes) * 100 if notes else 0
        })
        
        return analysis
    
    def _update_accuracy_stats(self, note: AccurateNote):
        """更新精确度统计"""
        self.accuracy_stats['total_notes_played'] += 1
        
        deviation = abs(note.cents_deviation)
        if deviation > self.accuracy_stats['max_deviation_played']:
            self.accuracy_stats['max_deviation_played'] = deviation
        
        # 更新平均偏差
        total = self.accuracy_stats['total_notes_played']
        current_avg = self.accuracy_stats['avg_deviation']
        self.accuracy_stats['avg_deviation'] = (current_avg * (total - 1) + deviation) / total
    
    def _print_accuracy_summary(self):
        """打印精确度统计摘要"""
        stats = self.accuracy_stats
        if stats['total_notes_played'] == 0:
            return
        
        compensation_rate = stats['compensated_notes'] / stats['total_notes_played'] * 100
        
        print(f"\n--- 精确度统计 ---")
        print(f"总播放音符: {stats['total_notes_played']}")
        print(f"使用补偿: {stats['compensated_notes']} ({compensation_rate:.1f}%)")
        print(f"最大偏差: {stats['max_deviation_played']:.1f}¢")
        print(f"平均偏差: {stats['avg_deviation']:.1f}¢")
    
    def reset_stats(self):
        """重置统计信息"""
        self.accuracy_stats = {
            'total_notes_played': 0,
            'compensated_notes': 0,
            'max_deviation_played': 0.0,
            'avg_deviation': 0.0
        }
    
    def get_accuracy_report(self) -> Dict:
        """获取完整的精确度报告"""
        return {
            'stats': self.accuracy_stats.copy(),
            'settings': {
                'a4_frequency': self.a4_frequency,
                'pitch_bend_range_cents': self.pitch_bend_range_cents,
                'frequency_tolerance_cents': FREQUENCY_TOLERANCE_CENTS,
                'current_channel': self.current_channel
            }
        }