"""
Petersen 自动作曲模块

整合节奏、旋律、和声生成器，实现完整的自动作曲功能。
支持预制模式组合、记忆重复、多轨道协调，生成完整的音乐作品。

主要功能：
- 多轨道作曲（低音+和弦+旋律）
- 预制模式库与自由游走结合
- 记忆感与重复机制
- 音乐情境与风格控制
- 多种导出格式（MIDI/MusicXML/CSV）

使用示例：
```python
from petersen_scale import PetersenScale
from petersen_chord import PetersenChordExtender
from petersen_composer import PetersenAutoComposer, COMPOSITION_STYLES

# 创建完整的作曲系统
base_scale = PetersenScale(F_base=55.0, phi=2.0)
chord_extender = PetersenChordExtender(base_scale)

composer = PetersenAutoComposer(
    petersen_scale=base_scale,
    chord_extender=chord_extender,
    composition_style=COMPOSITION_STYLES["balanced_journey"],
    bpm=120
)

# 生成作曲
composition = composer.compose(measures=8)

# 导出和播放
composition.export_midi("my_composition.mid")
composition.export_score_csv("composition_analysis.csv")
composition.play_preview()
```
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Any
from collections import defaultdict, deque
import math
import random
import json
from datetime import datetime
from enum import Enum

# 导入基础模块
try:
    from .petersen_scale import PetersenScale, ScaleEntry
    from .petersen_chord import PetersenChordExtender, ExtendedScale, ChordTone
    from .petersen_rhythm import PetersenRhythmGenerator, RhythmTrack, BassNote, ChordNote, RHYTHM_STYLES
    from .petersen_melody import PetersenMelodyGenerator, MelodyUnit, MelodyNote, MELODY_PATTERNS
except ImportError:
    from petersen_scale import PetersenScale, ScaleEntry
    from petersen_chord import PetersenChordExtender, ExtendedScale, ChordTone
    from petersen_rhythm import PetersenRhythmGenerator, RhythmTrack, BassNote, ChordNote, RHYTHM_STYLES
    from petersen_melody import PetersenMelodyGenerator, MelodyUnit, MelodyNote, MELODY_PATTERNS

@dataclass
class CompositionStyle:
    """作曲风格配置"""
    name: str                                    # 风格名称
    description: str                             # 描述
    rhythm_style: str                           # 节奏风格（来自RHYTHM_STYLES）
    movement_probabilities: List[float]         # 旋律移动概率 [环上, 跨环, 邻接]
    note_duration_style: str                    # 音符时长风格
    memory_pattern: str                         # 记忆模式
    tempo_preference: Tuple[int, int]           # BPM范围偏好
    harmony_complexity: str                     # 和声复杂度
    melody_patterns: List[str]                  # 偏好的旋律模式
    pattern_variation_rate: float               # 模式变化率
    cross_track_coordination: str               # 跨轨道协调方式
    
    def get_recommended_bpm(self) -> int:
        """获取推荐的BPM"""
        return random.randint(self.tempo_preference[0], self.tempo_preference[1])

# 预设作曲风格
COMPOSITION_STYLES = {
    "calm_meditation": CompositionStyle(
        name="calm_meditation",
        description="平静冥想 - 缓慢流动，注重内心平静",
        rhythm_style="meditative",
        movement_probabilities=[0.6, 0.2, 0.2],      # 更多环上移动
        note_duration_style="slow",
        memory_pattern="long_memory",
        tempo_preference=(60, 80),
        harmony_complexity="simple",
        melody_patterns=["ascending_scale", "descending_scale", "wave_motion"],
        pattern_variation_rate=0.3,
        cross_track_coordination="gentle"
    ),
    
    "dynamic_dance": CompositionStyle(
        name="dynamic_dance",
        description="动感舞蹈 - 活跃节奏，充满能量",
        rhythm_style="dynamic",
        movement_probabilities=[0.2, 0.4, 0.4],      # 更多跳跃和跨环
        note_duration_style="fast",
        memory_pattern="short_memory",
        tempo_preference=(120, 160),
        harmony_complexity="complex",
        melody_patterns=["pentagram_jump", "yin_yang_alternate", "cluster_exploration"],
        pattern_variation_rate=0.7,
        cross_track_coordination="syncopated"
    ),
    
    "balanced_journey": CompositionStyle(
        name="balanced_journey",
        description="平衡之旅 - 均衡发展，富有层次",
        rhythm_style="traditional",
        movement_probabilities=[0.4, 0.3, 0.3],      # 平衡分布
        note_duration_style="medium",
        memory_pattern="medium_memory",
        tempo_preference=(100, 130),
        harmony_complexity="moderate",
        melody_patterns=["ascending_scale", "pentagram_jump", "ring_spiral", "echo_return"],
        pattern_variation_rate=0.5,
        cross_track_coordination="balanced"
    ),
    
    "harmonic_exploration": CompositionStyle(
        name="harmonic_exploration",
        description="和声探索 - 注重音色变化和和声层次",
        rhythm_style="ceremonial",
        movement_probabilities=[0.3, 0.5, 0.2],      # 重点跨环
        note_duration_style="varied",
        memory_pattern="medium_memory",
        tempo_preference=(80, 110),
        harmony_complexity="rich",
        melody_patterns=["ring_spiral", "yin_yang_alternate", "cluster_exploration"],
        pattern_variation_rate=0.6,
        cross_track_coordination="harmonic"
    ),
    
    "rhythmic_pulse": CompositionStyle(
        name="rhythmic_pulse",
        description="节奏脉动 - 强调节拍感和律动",
        rhythm_style="flowing",
        movement_probabilities=[0.5, 0.2, 0.3],      # 强调节奏感
        note_duration_style="fast",
        memory_pattern="short_memory",
        tempo_preference=(110, 140),
        harmony_complexity="moderate",
        melody_patterns=["ascending_scale", "descending_scale", "wave_motion"],
        pattern_variation_rate=0.4,
        cross_track_coordination="rhythmic"
    )
}

@dataclass
class MemoryPattern:
    """记忆模式配置"""
    name: str
    interval_measures: List[int]                # 重复间隔（小节数）
    repeat_probability: float                   # 重复概率
    variation_level: str                        # 变化程度 ("low", "medium", "high")
    max_stored_patterns: int                    # 最大存储模式数

# 记忆模式预设
MEMORY_PATTERNS = {
    "short_memory": MemoryPattern(
        name="short_memory",
        interval_measures=[2, 3],
        repeat_probability=0.7,
        variation_level="low",
        max_stored_patterns=5
    ),
    
    "medium_memory": MemoryPattern(
        name="medium_memory", 
        interval_measures=[3, 4],
        repeat_probability=0.5,
        variation_level="medium",
        max_stored_patterns=8
    ),
    
    "long_memory": MemoryPattern(
        name="long_memory",
        interval_measures=[4, 6],
        repeat_probability=0.3,
        variation_level="high",
        max_stored_patterns=10
    )
}

class MemoryTracker:
    """记忆与重复管理"""
    
    def __init__(self, memory_style: str = "medium_memory"):
        """
        初始化记忆追踪器
        
        Args:
            memory_style: 记忆风格
        """
        if memory_style not in MEMORY_PATTERNS:
            memory_style = "medium_memory"
        
        self.memory_config = MEMORY_PATTERNS[memory_style]
        self.stored_patterns: deque = deque(maxlen=self.memory_config.max_stored_patterns)
        self.pattern_usage_history: List[Tuple[int, str]] = []  # (measure, pattern)
        self.last_repeat_measure = -1
    
    def should_repeat_pattern(self, current_measure: int) -> bool:
        """
        判断是否应该重复模式
        
        Args:
            current_measure: 当前小节号
            
        Returns:
            是否重复
        """
        if not self.stored_patterns:
            return False
        
        # 检查距离上次重复的间隔
        intervals = self.memory_config.interval_measures
        min_interval = min(intervals)
        
        if current_measure - self.last_repeat_measure < min_interval:
            return False
        
        # 根据概率决定
        return random.random() < self.memory_config.repeat_probability
    
    def get_repeat_pattern(self) -> str:
        """
        获取要重复的模式
        
        Returns:
            模式名称
        """
        if not self.stored_patterns:
            return random.choice(list(MELODY_PATTERNS.keys()))
        
        # 根据变化程度选择模式
        base_pattern = random.choice(self.stored_patterns)
        
        if self.memory_config.variation_level == "low":
            return base_pattern
        elif self.memory_config.variation_level == "medium":
            # 50%概率变化
            if random.random() < 0.5:
                return self._vary_pattern(base_pattern)
            return base_pattern
        else:  # high
            # 70%概率变化
            if random.random() < 0.7:
                return self._vary_pattern(base_pattern)
            return base_pattern
    
    def _vary_pattern(self, base_pattern: str) -> str:
        """对基础模式进行变化"""
        # 简单的变化策略：选择相似的模式
        pattern_groups = {
            "scale": ["ascending_scale", "descending_scale"],
            "jump": ["pentagram_jump", "cluster_exploration"],
            "alternate": ["yin_yang_alternate", "wave_motion"],
            "spatial": ["ring_spiral", "echo_return"]
        }
        
        # 找到基础模式所属的组
        for group_patterns in pattern_groups.values():
            if base_pattern in group_patterns:
                # 从同组中选择不同的模式
                alternatives = [p for p in group_patterns if p != base_pattern]
                if alternatives:
                    return random.choice(alternatives)
        
        # 如果找不到同组模式，随机选择
        return random.choice(list(MELODY_PATTERNS.keys()))
    
    def store_pattern(self, measure: int, pattern: str):
        """
        存储模式
        
        Args:
            measure: 小节号
            pattern: 模式名称
        """
        self.stored_patterns.append(pattern)
        self.pattern_usage_history.append((measure, pattern))
    
    def mark_repeat_used(self, measure: int):
        """标记重复已使用"""
        self.last_repeat_measure = measure

@dataclass
class MultiTrackComposition:
    """完整的多轨道作曲"""
    bass_track: List[BassNote]                  # 低音轨道
    chord_track: List[ChordNote]                # 和弦轨道
    melody_track: List[MelodyNote]              # 旋律轨道
    
    # 元信息
    bpm: int                                    # 每分钟拍数
    total_measures: int                         # 总小节数
    composition_style: str                      # 作曲风格
    creation_time: datetime = field(default_factory=datetime.now)
    
    # 生成参数
    petersen_scale_params: Dict = field(default_factory=dict)
    chord_extension_params: Dict = field(default_factory=dict)
    
    def get_total_duration_seconds(self) -> float:
        """获取总时长（秒）"""
        if not self.bass_track:
            return 0.0
        
        # 基于拍数和BPM计算
        beats_per_measure = 5
        total_beats = self.total_measures * beats_per_measure
        return (total_beats * 60.0) / self.bpm
    
    def get_all_events(self) -> List[Tuple[float, str, Union[BassNote, ChordNote, MelodyNote]]]:
        """获取所有事件（按时间排序）"""
        events = []
        beats_per_measure = 5
        notes_per_beat = 6
        
        # 计算每个音符位的时间
        position_duration = 60.0 / (self.bpm * notes_per_beat)
        
        # 添加低音事件
        for note in self.bass_track:
            time = (note.measure * beats_per_measure * notes_per_beat + note.position) * position_duration
            events.append((time, "bass", note))
        
        # 添加和弦事件
        for note in self.chord_track:
            time = (note.measure * beats_per_measure * notes_per_beat + note.position) * position_duration
            events.append((time, "chord", note))
        
        # 添加旋律事件
        for note in self.melody_track:
            time = (note.measure * beats_per_measure * notes_per_beat + note.position) * position_duration
            events.append((time, "melody", note))
        
        # 按时间排序
        events.sort(key=lambda x: x[0])
        return events
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取作曲统计信息"""
        stats = {
            "basic_info": {
                "total_measures": self.total_measures,
                "total_duration_seconds": self.get_total_duration_seconds(),
                "bpm": self.bpm,
                "composition_style": self.composition_style,
                "creation_time": self.creation_time.isoformat()
            },
            
            "track_info": {
                "bass_notes": len(self.bass_track),
                "chord_notes": len(self.chord_track),
                "melody_notes": len(self.melody_track),
                "total_notes": len(self.bass_track) + len(self.chord_track) + len(self.melody_track)
            },
            
            "frequency_analysis": self._analyze_frequencies(),
            "rhythm_analysis": self._analyze_rhythm(),
            "harmony_analysis": self._analyze_harmony()
        }
        
        return stats
    
    def _analyze_frequencies(self) -> Dict[str, float]:
        """分析频率分布"""
        all_frequencies = []
        
        for note in self.bass_track:
            all_frequencies.append(note.note_entry.freq)
        
        for note in self.chord_track:
            all_frequencies.extend(note.get_frequencies())
        
        for note in self.melody_track:
            all_frequencies.append(note.freq)
        
        if not all_frequencies:
            return {}
        
        return {
            "min_frequency": min(all_frequencies),
            "max_frequency": max(all_frequencies),
            "frequency_span_ratio": max(all_frequencies) / min(all_frequencies),
            "average_frequency": sum(all_frequencies) / len(all_frequencies)
        }
    
    def _analyze_rhythm(self) -> Dict[str, float]:
        """分析节奏特征"""
        if not self.bass_track:
            return {}
        
        strong_beats = sum(1 for note in self.bass_track if note.is_strong_beat)
        strong_beat_ratio = strong_beats / len(self.bass_track)
        
        # 分析和弦密度
        chord_density = len(self.chord_track) / self.total_measures if self.total_measures > 0 else 0
        
        return {
            "strong_beat_ratio": strong_beat_ratio,
            "chord_density_per_measure": chord_density,
            "average_bass_velocity": sum(note.velocity for note in self.bass_track) / len(self.bass_track),
            "rhythm_variety_score": len(set(note.position % 6 for note in self.bass_track)) / 6
        }
    
    def _analyze_harmony(self) -> Dict[str, Any]:
        """分析和声特征"""
        if not self.chord_track:
            return {}
        
        chord_types = defaultdict(int)
        for note in self.chord_track:
            chord_types[note.chord_type] += 1
        
        total_chord_tones = sum(len(note.chord_tones) for note in self.chord_track)
        avg_chord_size = total_chord_tones / len(self.chord_track) if self.chord_track else 0
        
        return {
            "chord_type_distribution": dict(chord_types),
            "average_chord_size": avg_chord_size,
            "harmony_complexity_score": len(chord_types) / len(self.chord_track) if self.chord_track else 0
        }
    
    def export_midi(self, filename: str = None):
        """导出为MIDI文件"""
        if not filename:
            filename = f"../data/petersen_composition_{int(time.time())}.mid"
        
        try:
            # 创建真实的MIDI文件而不是占位符
            mid = mido.MidiFile()
            track = mido.MidiTrack()
            mid.tracks.append(track)
            
            # 设置tempo
            tempo = mido.bpm2tempo(self.bpm)
            track.append(mido.MetaMessage('set_tempo', tempo=tempo))
            
            # 转换时间戳为MIDI时间
            current_time = 0
            
            # 合并所有音符事件
            all_events = []
            
            # 添加旋律轨道
            for note in self.melody_track:
                start_time = note['timestamp']
                end_time = start_time + note['duration']
                
                # MIDI音符号（简化映射）
                midi_note = self._frequency_to_midi_note(note['freq'])
                velocity = note['velocity']
                
                all_events.append({
                    'time': start_time,
                    'type': 'note_on',
                    'note': midi_note,
                    'velocity': velocity
                })
                all_events.append({
                    'time': end_time,
                    'type': 'note_off',
                    'note': midi_note,
                    'velocity': 0
                })
            
            # 添加和弦轨道
            for chord in self.chord_track:
                start_time = chord['timestamp']
                end_time = start_time + chord['duration']
                
                for freq in chord['frequencies']:
                    midi_note = self._frequency_to_midi_note(freq)
                    velocity = chord['velocity']
                    
                    all_events.append({
                        'time': start_time,
                        'type': 'note_on',
                        'note': midi_note,
                        'velocity': velocity
                    })
                    all_events.append({
                        'time': end_time,
                        'type': 'note_off',
                        'note': midi_note,
                        'velocity': 0
                    })
            
            # 排序事件
            all_events.sort(key=lambda x: x['time'])
            
            # 转换为MIDI消息
            for event in all_events:
                delta_time = int((event['time'] - current_time) * 480)  # 480 ticks per beat
                current_time = event['time']
                
                if event['type'] == 'note_on':
                    track.append(mido.Message('note_on', 
                                            channel=0, 
                                            note=event['note'], 
                                            velocity=event['velocity'], 
                                            time=delta_time))
                else:
                    track.append(mido.Message('note_off', 
                                            channel=0, 
                                            note=event['note'], 
                                            velocity=0, 
                                            time=delta_time))
            
            # 保存文件
            mid.save(filename)
            print(f"MIDI文件已保存: {filename}")
            
        except Exception as e:
            print(f"MIDI导出失败: {e}")
            # 如果MIDI导出失败，创建占位符
            self._create_midi_placeholder(filename)

    def _frequency_to_midi_note(self, frequency: float) -> int:
        """将频率转换为MIDI音符号"""
        import math
        if frequency <= 0:
            return 60  # 默认中央C
        
        # 使用标准公式: MIDI = 12 * log2(f/440) + 69
        midi_note = int(12 * math.log2(frequency / 440) + 69)
        return max(0, min(127, midi_note))  # 限制在有效范围内
    
    def export_musicxml(self, path: Union[str, Path]) -> None:
        """
        导出到MusicXML文件
        
        Args:
            path: 输出路径
        """
        path = Path(path)
        
        # MusicXML导出占位符（实际实现需要music21库）
        with open(path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n')
            f.write('<score-partwise version="3.1">\n')
            f.write(f'  <!-- Petersen自动作曲系统生成 -->\n')
            f.write(f'  <!-- 风格: {self.composition_style} -->\n')
            f.write(f'  <!-- BPM: {self.bpm} -->\n')
            f.write('</score-partwise>\n')
        
        print(f"MusicXML文件导出到: {path} (占位符)")
    
    def export_score_csv(self, path: Union[str, Path] = None) -> None:
        """
        导出完整乐谱到CSV文件
        
        Args:
            path: 输出路径
        """
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"../data/petersen_composition_{self.composition_style}_{timestamp}.csv"
        
        path = Path(path)
        
        # 获取所有事件
        all_events = self.get_all_events()
        
        with open(path, 'w', encoding='utf-8') as f:
            # CSV头部
            f.write("时间(秒),轨道,小节,拍,位置,音符/和弦,频率(Hz),持续时间,力度,备注\n")
            
            for time, track_type, note in all_events:
                if track_type == "bass":
                    f.write(f"{time:.3f},低音,{note.measure},{note.beat},{note.position},"
                           f"{note.note_entry.key_short},{note.note_entry.freq:.2f},"
                           f"{note.duration:.2f},{note.velocity},"
                           f"根音-{'强' if note.is_strong_beat else '弱'}拍\n")
                
                elif track_type == "chord":
                    chord_names = "+".join(tone.ratio_name for tone in note.chord_tones)
                    chord_freqs = "+".join(f"{tone.freq:.1f}" for tone in note.chord_tones)
                    f.write(f"{time:.3f},和弦,{note.measure},{note.beat},{note.position},"
                           f"{chord_names},{chord_freqs},"
                           f"{note.duration:.2f},{note.velocity},"
                           f"{note.chord_type}-{'强' if note.is_strong_beat else '弱'}拍\n")
                
                elif track_type == "melody":
                    f.write(f"{time:.3f},旋律,{note.measure},{note.beat},{note.position},"
                           f"{note.key_name},{note.freq:.2f},"
                           f"{note.duration:.2f},{note.velocity},"
                           f"{note.articulation}-{'装饰' if note.is_ornament else '主音'}\n")
        
        print(f"完整乐谱已导出到: {path}")
    
    def play_preview(self) -> None:
        """播放预览（占位符功能）"""
        print(f"播放预览: {self.composition_style}风格作曲")
        print(f"时长: {self.get_total_duration_seconds():.1f}秒")
        print(f"BPM: {self.bpm}")
        print(f"低音: {len(self.bass_track)}个音符")
        print(f"和弦: {len(self.chord_track)}个音符") 
        print(f"旋律: {len(self.melody_track)}个音符")
        print("（实际播放功能需要音频库支持）")

class PetersenAutoComposer:
    """Petersen自动作曲系统"""
    
    def __init__(self,
                 petersen_scale: PetersenScale,
                 chord_extender: PetersenChordExtender,
                 composition_style: Union[str, CompositionStyle],
                 bpm: Optional[int] = None):
        """
        初始化自动作曲器
        
        Args:
            petersen_scale: Petersen音阶
            chord_extender: 和弦扩展器
            composition_style: 作曲风格（名称或对象）
            bpm: 每分钟拍数（如果为None则使用风格推荐值）
        """
        self.petersen_scale = petersen_scale
        self.chord_extender = chord_extender
        
        # 处理作曲风格
        if isinstance(composition_style, str):
            if composition_style not in COMPOSITION_STYLES:
                raise ValueError(f"未知的作曲风格: {composition_style}")
            self.composition_style = COMPOSITION_STYLES[composition_style]
        else:
            self.composition_style = composition_style
        
        # 设置BPM
        if bpm is None:
            self.bpm = self.composition_style.get_recommended_bpm()
        else:
            self.bpm = bpm
        
        # 生成扩展音阶
        self.extended_scale = self.chord_extender.extend_scale_with_chords()
        
        # 初始化子系统
        self._init_subsystems()
    
    def _init_subsystems(self):
        """初始化子系统"""
        # 节奏生成器
        self.rhythm_generator = PetersenRhythmGenerator(
            extended_scale=self.extended_scale,
            bpm=self.bpm,
            rhythm_style=self.composition_style.rhythm_style
        )
        
        # 旋律生成器
        self.melody_generator = PetersenMelodyGenerator(
            extended_scale=self.extended_scale,
            movement_probabilities=self.composition_style.movement_probabilities,
            melody_style=self.composition_style.name
        )
        
        # 记忆追踪器
        self.memory_tracker = MemoryTracker(self.composition_style.memory_pattern)
    
    def compose(self, measures: int = 8) -> MultiTrackComposition:
        """
        生成完整作曲
        
        Args:
            measures: 小节数
            
        Returns:
            多轨道作曲
        """
        print(f"开始作曲: {self.composition_style.name}风格, {measures}小节, {self.bpm}BPM")
        
        # 第一步：生成节奏框架
        print("生成节奏框架...")
        rhythm_track = self.rhythm_generator.generate_rhythm_track(measures)
        
        # 第二步：生成旋律轨道
        print("生成旋律轨道...")
        melody_track = self._generate_coordinated_melody(rhythm_track)
        
        # 第三步：创建完整作曲
        composition = MultiTrackComposition(
            bass_track=rhythm_track.bass_notes,
            chord_track=rhythm_track.chord_notes,
            melody_track=melody_track,
            bpm=self.bpm,
            total_measures=measures,
            composition_style=self.composition_style.name,
            petersen_scale_params={
                "F_base": self.petersen_scale.F_base,
                "phi": self.petersen_scale.phi,
                "delta_theta": self.petersen_scale.delta_theta
            },
            chord_extension_params={
                "chord_ratios": self.chord_extender.chord_ratios,
                "tolerance_cents": self.chord_extender.tolerance_cents
            }
        )
        
        print(f"作曲完成! 总时长: {composition.get_total_duration_seconds():.1f}秒")
        return composition
    
    def _generate_coordinated_melody(self, rhythm_track: RhythmTrack) -> List[MelodyNote]:
        """
        生成与节奏协调的旋律
        
        Args:
            rhythm_track: 节奏轨道
            
        Returns:
            旋律音符列表
        """
        all_melody_notes = []
        
        for measure in range(rhythm_track.total_measures):
            
            # 决定是否重复之前的模式
            if self.memory_tracker.should_repeat_pattern(measure):
                pattern = self.memory_tracker.get_repeat_pattern()
                self.memory_tracker.mark_repeat_used(measure)
                print(f"  小节{measure}: 重复模式 {pattern}")
            else:
                pattern = self._select_new_pattern(measure)
                self.memory_tracker.store_pattern(measure, pattern)
                print(f"  小节{measure}: 新模式 {pattern}")
            
            # 确定起始元素（基于该小节的低音）
            measure_bass_notes = [n for n in rhythm_track.bass_notes if n.measure == measure]
            if measure_bass_notes:
                start_element = self._bass_note_to_element(measure_bass_notes[0])
            else:
                start_element = "金"  # 默认
            
            # 生成旋律单元
            melody_unit = self.melody_generator.generate_melody_unit(
                start_element=start_element,
                start_polarity=0,
                start_zone=0,
                pattern=pattern,
                length=30,  # 一小节30个位置
                measure_number=measure
            )
            
            # 协调旋律与节奏
            coordinated_notes = self._coordinate_melody_with_rhythm(
                melody_unit.melody_notes,
                measure_bass_notes,
                [n for n in rhythm_track.chord_notes if n.measure == measure]
            )
            
            all_melody_notes.extend(coordinated_notes)
        
        return all_melody_notes
    
    def _select_new_pattern(self, measure: int) -> str:
        """
        选择新的旋律模式
        
        Args:
            measure: 小节号
            
        Returns:
            模式名称
        """
        # 从风格偏好的模式中选择
        preferred_patterns = self.composition_style.melody_patterns
        
        # 基于变化率决定是否选择新模式
        if random.random() < self.composition_style.pattern_variation_rate:
            # 高变化率：从所有模式中选择
            return random.choice(list(MELODY_PATTERNS.keys()))
        else:
            # 低变化率：从偏好模式中选择
            return random.choice(preferred_patterns)
    
    def _bass_note_to_element(self, bass_note: BassNote) -> str:
        """将低音音符转换为五行元素"""
        # 基于音阶条目的e值确定元素
        element_map = {0: "金", 1: "木", 2: "水", 3: "火", 4: "土"}
        return element_map.get(bass_note.note_entry.e, "金")
    
    def _coordinate_melody_with_rhythm(self, 
                                     melody_notes: List[MelodyNote],
                                     bass_notes: List[BassNote],
                                     chord_notes: List[ChordNote]) -> List[MelodyNote]:
        """
        协调旋律与节奏
        
        Args:
            melody_notes: 原始旋律音符
            bass_notes: 该小节的低音音符
            chord_notes: 该小节的和弦音符
            
        Returns:
            协调后的旋律音符
        """
        coordination_style = self.composition_style.cross_track_coordination
        
        if coordination_style == "gentle":
            # 温和协调：降低冲突位置的旋律力度
            return self._gentle_coordination(melody_notes, bass_notes, chord_notes)
        
        elif coordination_style == "syncopated":
            # 切分协调：在空拍位置强调旋律
            return self._syncopated_coordination(melody_notes, bass_notes, chord_notes)
        
        elif coordination_style == "harmonic":
            # 和声协调：旋律优先选择和声音
            return self._harmonic_coordination(melody_notes, bass_notes, chord_notes)
        
        elif coordination_style == "rhythmic":
            # 节奏协调：旋律强化节奏感
            return self._rhythmic_coordination(melody_notes, bass_notes, chord_notes)
        
        else:  # balanced
            # 平衡协调：综合多种策略
            return self._balanced_coordination(melody_notes, bass_notes, chord_notes)
    
    def _gentle_coordination(self, melody_notes, bass_notes, chord_notes):
        """温和协调策略"""
        occupied_positions = set()
        for note in bass_notes + chord_notes:
            occupied_positions.add(note.position)
        
        for melody_note in melody_notes:
            if melody_note.position in occupied_positions:
                # 降低冲突位置的力度
                melody_note.velocity = max(20, melody_note.velocity - 20)
                melody_note.articulation = "soft"
        
        return melody_notes
    
    def _syncopated_coordination(self, melody_notes, bass_notes, chord_notes):
        """切分协调策略"""
        occupied_positions = set()
        for note in bass_notes + chord_notes:
            occupied_positions.add(note.position)
        
        for melody_note in melody_notes:
            if melody_note.position not in occupied_positions:
                # 在空拍位置强调旋律
                melody_note.velocity = min(127, melody_note.velocity + 15)
                melody_note.articulation = "accent"
        
        return melody_notes
    
    def _harmonic_coordination(self, melody_notes, bass_notes, chord_notes):
        """和声协调策略"""
        # 获取该小节的和声音高
        harmony_frequencies = set()
        for chord_note in chord_notes:
            harmony_frequencies.update(chord_note.get_frequencies())
        
        for melody_note in melody_notes:
            # 如果旋律音接近和声音，增强力度
            melody_freq = melody_note.freq
            for harmony_freq in harmony_frequencies:
                freq_ratio = melody_freq / harmony_freq
                if 0.95 <= freq_ratio <= 1.05:  # 接近同音
                    melody_note.velocity = min(127, melody_note.velocity + 10)
                    break
        
        return melody_notes
    
    def _rhythmic_coordination(self, melody_notes, bass_notes, chord_notes):
        """节奏协调策略"""
        for melody_note in melody_notes:
            beat_position = melody_note.position % 6
            
            if beat_position == 0:  # 拍的开始
                melody_note.velocity = min(127, melody_note.velocity + 15)
                melody_note.articulation = "accent"
            elif beat_position in [2, 4]:  # 中强位置
                melody_note.velocity = min(127, melody_note.velocity + 5)
        
        return melody_notes
    
    def _balanced_coordination(self, melody_notes, bass_notes, chord_notes):
        """平衡协调策略"""
        # 综合应用多种策略
        melody_notes = self._gentle_coordination(melody_notes, bass_notes, chord_notes)
        melody_notes = self._harmonic_coordination(melody_notes, bass_notes, chord_notes)
        
        # 适度的节奏强化
        for melody_note in melody_notes:
            if melody_note.position % 6 == 0:
                melody_note.velocity = min(127, melody_note.velocity + 8)
        
        return melody_notes
    
    def compose_with_variations(self, 
                              base_measures: int = 4, 
                              variations: int = 2) -> List[MultiTrackComposition]:
        """
        生成带变奏的作曲
        
        Args:
            base_measures: 基础主题小节数
            variations: 变奏数量
            
        Returns:
            作曲列表（主题+变奏）
        """
        compositions = []
        
        # 生成基础主题
        print("生成基础主题...")
        base_composition = self.compose(base_measures)
        compositions.append(base_composition)
        
        # 生成变奏
        for i in range(variations):
            print(f"生成变奏 {i+1}...")
            
            # 修改作曲参数以创建变奏
            variation_style = self._create_variation_style(i + 1)
            
            # 临时保存原始风格
            original_style = self.composition_style
            
            try:
                # 应用变奏风格
                self.composition_style = variation_style
                self._init_subsystems()  # 重新初始化子系统
                
                # 生成变奏
                variation_composition = self.compose(base_measures)
                compositions.append(variation_composition)
                
            finally:
                # 恢复原始风格
                self.composition_style = original_style
                self._init_subsystems()
        
        return compositions
    
    def _create_variation_style(self, variation_number: int) -> CompositionStyle:
        """创建变奏风格"""
        base_style = self.composition_style
        
        # 变奏策略
        variation_strategies = [
            self._tempo_variation,
            self._probability_variation,
            self._pattern_variation,
            self._rhythm_variation
        ]
        
        strategy = variation_strategies[variation_number % len(variation_strategies)]
        return strategy(base_style, variation_number)
    
    def _tempo_variation(self, base_style: CompositionStyle, variation_num: int) -> CompositionStyle:
        """速度变奏"""
        new_style = CompositionStyle(**base_style.__dict__.copy())
        new_style.name = f"{base_style.name}_tempo_var_{variation_num}"
        
        # 调整速度范围
        tempo_factor = 1.2 if variation_num % 2 == 1 else 0.8
        new_tempo = (
            int(base_style.tempo_preference[0] * tempo_factor),
            int(base_style.tempo_preference[1] * tempo_factor)
        )
        new_style.tempo_preference = new_tempo
        
        return new_style
    
    def _probability_variation(self, base_style: CompositionStyle, variation_num: int) -> CompositionStyle:
        """概率分布变奏"""
        new_style = CompositionStyle(**base_style.__dict__.copy())
        new_style.name = f"{base_style.name}_prob_var_{variation_num}"
        
        # 重新分配移动概率
        if variation_num == 1:
            # 更多跨环移动
            new_style.movement_probabilities = [0.2, 0.5, 0.3]
        elif variation_num == 2:
            # 更多同环跳跃
            new_style.movement_probabilities = [0.3, 0.2, 0.5]
        else:
            # 更多环上移动
            new_style.movement_probabilities = [0.6, 0.2, 0.2]
        
        return new_style
    
    def _pattern_variation(self, base_style: CompositionStyle, variation_num: int) -> CompositionStyle:
        """模式变奏"""
        new_style = CompositionStyle(**base_style.__dict__.copy())
        new_style.name = f"{base_style.name}_pattern_var_{variation_num}"
        
        # 使用不同的模式组合
        all_patterns = list(MELODY_PATTERNS.keys())
        excluded_patterns = set(base_style.melody_patterns)
        new_patterns = [p for p in all_patterns if p not in excluded_patterns]
        
        if new_patterns:
            new_style.melody_patterns = new_patterns[:4]  # 最多4个新模式
        
        # 增加变化率
        new_style.pattern_variation_rate = min(1.0, base_style.pattern_variation_rate + 0.3)
        
        return new_style
    
    def _rhythm_variation(self, base_style: CompositionStyle, variation_num: int) -> CompositionStyle:
        """节奏变奏"""
        new_style = CompositionStyle(**base_style.__dict__.copy())
        new_style.name = f"{base_style.name}_rhythm_var_{variation_num}"
        
        # 使用不同的节奏风格
        rhythm_styles = list(RHYTHM_STYLES.keys())
        excluded_style = base_style.rhythm_style
        new_rhythm_styles = [s for s in rhythm_styles if s != excluded_style]
        
        if new_rhythm_styles:
            new_style.rhythm_style = new_rhythm_styles[variation_num % len(new_rhythm_styles)]
        
        return new_style
    
    def analyze_composition(self, composition: MultiTrackComposition) -> Dict[str, Any]:
        """
        分析作曲特征
        
        Args:
            composition: 作曲对象
            
        Returns:
            分析结果
        """
        basic_stats = composition.get_statistics()
        
        # 添加风格相关分析
        style_analysis = {
            "style_adherence": self._analyze_style_adherence(composition),
            "complexity_metrics": self._analyze_complexity(composition),
            "musical_flow": self._analyze_musical_flow(composition),
            "harmony_richness": self._analyze_harmony_richness(composition)
        }
        
        return {**basic_stats, "style_analysis": style_analysis}
    
    def _analyze_style_adherence(self, composition: MultiTrackComposition) -> Dict[str, float]:
        """分析风格遵循度"""
        # 简化的风格分析
        target_style = self.composition_style
        
        # 分析BPM是否在目标范围内
        bpm_adherence = 1.0
        if not (target_style.tempo_preference[0] <= composition.bpm <= target_style.tempo_preference[1]):
            bpm_adherence = 0.8
        
        # 分析节奏特征
        rhythm_stats = composition._analyze_rhythm()
        rhythm_adherence = 0.9  # 简化评分
        
        return {
            "bpm_adherence": bpm_adherence,
            "rhythm_adherence": rhythm_adherence,
            "overall_adherence": (bpm_adherence + rhythm_adherence) / 2
        }
    
    def _analyze_complexity(self, composition: MultiTrackComposition) -> Dict[str, float]:
        """分析复杂度"""
        # 基于音符数量和分布的复杂度评估
        total_notes = len(composition.bass_track) + len(composition.chord_track) + len(composition.melody_track)
        notes_per_measure = total_notes / composition.total_measures if composition.total_measures > 0 else 0
        
        return {
            "notes_per_measure": notes_per_measure,
            "track_balance": len(composition.melody_track) / total_notes if total_notes > 0 else 0,
            "complexity_score": min(1.0, notes_per_measure / 50)  # 归一化到0-1
        }
    
    def _analyze_musical_flow(self, composition: MultiTrackComposition) -> Dict[str, float]:
        """分析音乐流动性"""
        # 简化的流动性分析
        if not composition.melody_track:
            return {"flow_score": 0.0}
        
        # 分析旋律音程跳跃
        large_jumps = 0
        for i in range(1, len(composition.melody_track)):
            prev_freq = composition.melody_track[i-1].freq
            curr_freq = composition.melody_track[i].freq
            ratio = max(curr_freq, prev_freq) / min(curr_freq, prev_freq)
            if ratio > 1.5:  # 超过完全五度的跳跃
                large_jumps += 1
        
        jump_ratio = large_jumps / len(composition.melody_track)
        flow_score = max(0.0, 1.0 - jump_ratio * 2)  # 跳跃越多流动性越差
        
        return {"flow_score": flow_score, "large_jump_ratio": jump_ratio}
    
    def _analyze_harmony_richness(self, composition: MultiTrackComposition) -> Dict[str, float]:
        """分析和声丰富度"""
        if not composition.chord_track:
            return {"richness_score": 0.0}
        
        # 统计不同和弦类型
        chord_types = set(note.chord_type for note in composition.chord_track)
        richness_score = len(chord_types) / 5  # 假设最多5种和弦类型
        
        return {
            "richness_score": min(1.0, richness_score),
            "unique_chord_types": len(chord_types)
        }

def compare_composition_styles(petersen_scale: PetersenScale, 
                             chord_extender: PetersenChordExtender,
                             measures: int = 4) -> None:
    """
    比较不同作曲风格的效果
    
    Args:
        petersen_scale: Petersen音阶
        chord_extender: 和弦扩展器
        measures: 测试小节数
    """
    print("=== 作曲风格比较分析 ===\n")
    
    for style_name, style_config in COMPOSITION_STYLES.items():
        print(f"【{style_name}】{style_config.description}")
        
        composer = PetersenAutoComposer(
            petersen_scale=petersen_scale,
            chord_extender=chord_extender,
            composition_style=style_name,
            bpm=style_config.get_recommended_bpm()
        )
        
        composition = composer.compose(measures)
        analysis = composer.analyze_composition(composition)
        
        print(f"  BPM: {composition.bpm}")
        print(f"  总时长: {composition.get_total_duration_seconds():.1f}秒")
        print(f"  音符密度: {analysis['style_analysis']['complexity_metrics']['notes_per_measure']:.1f}个/小节")
        print(f"  风格遵循度: {analysis['style_analysis']['style_adherence']['overall_adherence']:.1%}")
        print(f"  音乐流动性: {analysis['style_analysis']['musical_flow']['flow_score']:.1%}")
        print(f"  和声丰富度: {analysis['style_analysis']['harmony_richness']['richness_score']:.1%}")
        print()

if __name__ == "__main__":
    # 示例用法
    from petersen_scale import PetersenScale
    from petersen_chord import PetersenChordExtender
    
    # 创建基础系统
    print("初始化Petersen音乐系统...")
    base_scale = PetersenScale(F_base=55.0, phi=2.0, delta_theta=4.8)
    chord_extender = PetersenChordExtender(base_scale, chord_ratios="simple_ratios")
    
    # 创建自动作曲器
    composer = PetersenAutoComposer(
        petersen_scale=base_scale,
        chord_extender=chord_extender,
        composition_style="balanced_journey",
        bpm=120
    )
    
    # 生成作曲
    print("\n开始作曲...")
    composition = composer.compose(measures=8)
    
    # 分析作曲
    print("\n分析作曲...")
    analysis = composer.analyze_composition(composition)
    
    print(f"\n=== 作曲完成 ===")
    print(f"风格: {composition.composition_style}")
    print(f"时长: {composition.get_total_duration_seconds():.1f}秒")
    print(f"BPM: {composition.bpm}")
    print(f"小节数: {composition.total_measures}")
    
    print(f"\n音符统计:")
    track_info = analysis["track_info"]
    print(f"  低音: {track_info['bass_notes']}个")
    print(f"  和弦: {track_info['chord_notes']}个")
    print(f"  旋律: {track_info['melody_notes']}个")
    print(f"  总计: {track_info['total_notes']}个")
    
    print(f"\n质量评估:")
    style_analysis = analysis["style_analysis"]
    print(f"  风格遵循度: {style_analysis['style_adherence']['overall_adherence']:.1%}")
    print(f"  音乐流动性: {style_analysis['musical_flow']['flow_score']:.1%}")
    print(f"  和声丰富度: {style_analysis['harmony_richness']['richness_score']:.1%}")
    
    # 导出文件
    print(f"\n导出文件...")
    composition.export_score_csv()
    composition.export_midi("../data/petersen_composition.mid")
    composition.export_musicxml("../data/petersen_composition.xml")
    
    # 播放预览
    print(f"\n预览播放:")
    composition.play_preview()
    
    # 生成变奏版本
    print(f"\n生成变奏...")
    variations = composer.compose_with_variations(base_measures=4, variations=2)
    
    print(f"生成了 {len(variations)} 个版本:")
    for i, var_composition in enumerate(variations):
        print(f"  版本{i+1}: {var_composition.composition_style}")
    
    # 比较不同风格
    print(f"\n" + "="*60)
    compare_composition_styles(base_scale, chord_extender, measures=4)