"""
Petersen 节奏与和声模块

基于Petersen音阶系统，实现节奏框架和和声结构。
提供低音轨道和和弦轨道的生成，作为自动作曲的基础支撑。

主要功能：
- 5拍小节的节奏框架（30个时间位）
- 低音轨道生成（根音 + 节拍锚点）
- 和弦轨道生成（基于和弦扩展器）
- 阴阳强弱拍映射
- BPM时间计算

使用示例：
```python
from petersen_scale import PetersenScale
from petersen_chord import PetersenChordExtender
from petersen_rhythm import PetersenRhythmGenerator

# 创建基础音阶和和弦扩展
base_scale = PetersenScale(F_base=55.0, phi=2.0)
chord_extender = PetersenChordExtender(base_scale)
extended_scale = chord_extender.extend_scale_with_chords()

# 创建节奏生成器
rhythm_gen = PetersenRhythmGenerator(
    extended_scale=extended_scale,
    bpm=120,
    rhythm_style="traditional"
)

# 生成节奏轨道
bass_track = rhythm_gen.generate_bass_track(measures=4)
chord_track = rhythm_gen.generate_chord_track(bass_track)

# 导出节奏结构
rhythm_gen.export_rhythm_csv("rhythm_structure.csv")
```
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from collections import defaultdict
import math
import random
from datetime import datetime

# 导入基础模块
try:
    from .petersen_scale import PetersenScale, ScaleEntry
    from .petersen_chord import PetersenChordExtender, ExtendedScale, ChordTone
except ImportError:
    from petersen_scale import PetersenScale, ScaleEntry
    from petersen_chord import PetersenChordExtender, ExtendedScale, ChordTone

# 节奏风格预设
RHYTHM_STYLES = {
    "traditional": {
        "description": "传统五行节奏",
        "bass_pattern": "root_emphasis",      # 强调根音
        "chord_density": "medium",            # 中等和弦密度
        "syncopation": False,                 # 无切分音
        "velocity_contrast": 0.3              # 强弱对比度
    },
    
    "meditative": {
        "description": "冥想静心节奏",
        "bass_pattern": "sustained",          # 持续低音
        "chord_density": "sparse",            # 稀疏和弦
        "syncopation": False,
        "velocity_contrast": 0.2              # 较小强弱对比
    },
    
    "dynamic": {
        "description": "动感活跃节奏",
        "bass_pattern": "walking",            # 行进低音
        "chord_density": "dense",             # 密集和弦
        "syncopation": True,                  # 有切分音
        "velocity_contrast": 0.5              # 较大强弱对比
    },
    
    "ceremonial": {
        "description": "仪式庄重节奏",
        "bass_pattern": "pedal_tone",         # 持续音
        "chord_density": "medium",
        "syncopation": False,
        "velocity_contrast": 0.4
    },
    
    "flowing": {
        "description": "流动自然节奏",
        "bass_pattern": "gentle_walk",        # 柔和行进
        "chord_density": "varied",            # 变化密度
        "syncopation": True,
        "velocity_contrast": 0.35
    }
}

@dataclass
class RhythmPattern:
    """节拍模式定义"""
    beats_per_measure: int = 5               # 每小节拍数
    notes_per_beat: int = 6                  # 每拍音符位数
    total_positions: int = 30                # 总音符位数
    
    def get_beat_positions(self, beat: int) -> List[int]:
        """获取指定拍的音符位置"""
        start_pos = beat * self.notes_per_beat
        return list(range(start_pos, start_pos + self.notes_per_beat))
    
    def get_position_timing(self, beat: int, position: int) -> Tuple[int, int]:
        """获取位置在拍内的相对时间"""
        beat_start = beat * self.notes_per_beat
        relative_pos = position - beat_start
        return beat, relative_pos

@dataclass
class TimingGrid:
    """时间网格系统"""
    bpm: int                                 # 每分钟拍数
    rhythm_pattern: RhythmPattern
    
    def position_to_seconds(self, measure: int, beat: int, position: int) -> float:
        """将音符位置转换为绝对时间（秒）"""
        # 计算总拍数
        total_beats = measure * self.rhythm_pattern.beats_per_measure + beat
        
        # 计算拍内相对时间
        beat_relative_pos = position % self.rhythm_pattern.notes_per_beat
        relative_time = beat_relative_pos / self.rhythm_pattern.notes_per_beat
        
        # 转换为秒
        seconds_per_beat = 60.0 / self.bpm
        return (total_beats + relative_time) * seconds_per_beat
    
    def get_beat_duration(self) -> float:
        """获取一拍的时长（秒）"""
        return 60.0 / self.bpm
    
    def get_position_duration(self) -> float:
        """获取一个音符位的时长（秒）"""
        return self.get_beat_duration() / self.rhythm_pattern.notes_per_beat

@dataclass
class BassNote:
    """低音轨道音符"""
    measure: int                             # 小节号（从0开始）
    beat: int                               # 拍号（0-4）
    position: int                           # 音符位置（0-29）
    note_entry: ScaleEntry                  # 对应的音阶条目
    duration: float                         # 持续时间（以拍为单位）
    velocity: int                           # 力度（0-127）
    is_strong_beat: bool                    # 是否为强拍（基于阴阳）
    is_root: bool                          # 是否为根音
    
    def get_absolute_time(self, timing_grid: TimingGrid) -> float:
        """获取绝对时间（秒）"""
        return timing_grid.position_to_seconds(self.measure, self.beat, self.position)
    
    def get_end_time(self, timing_grid: TimingGrid) -> float:
        """获取结束时间（秒）"""
        start_time = self.get_absolute_time(timing_grid)
        duration_seconds = self.duration * timing_grid.get_beat_duration()
        return start_time + duration_seconds

@dataclass
class ChordNote:
    """和弦轨道音符"""
    measure: int
    beat: int
    position: int
    chord_tones: List[ChordTone]            # 和弦音组合
    root_note: ScaleEntry                   # 对应的根音
    duration: float                         # 持续时间（以拍为单位）
    velocity: int                           # 力度（0-127）
    chord_type: str                         # 和弦类型描述
    is_strong_beat: bool                    # 是否为强拍
    
    def get_frequencies(self) -> List[float]:
        """获取所有和弦音频率"""
        return [tone.freq for tone in self.chord_tones]
    
    def get_absolute_time(self, timing_grid: TimingGrid) -> float:
        """获取绝对时间（秒）"""
        return timing_grid.position_to_seconds(self.measure, self.beat, self.position)

@dataclass
class RhythmTrack:
    """节奏轨道（低音+和弦的组合）"""
    bass_notes: List[BassNote]
    chord_notes: List[ChordNote]
    timing_grid: TimingGrid
    rhythm_style: str
    total_measures: int
    
    def get_all_events(self) -> List[Union[BassNote, ChordNote]]:
        """获取所有事件（按时间排序）"""
        all_events = []
        all_events.extend(self.bass_notes)
        all_events.extend(self.chord_notes)
        
        # 按时间排序
        all_events.sort(key=lambda x: x.get_absolute_time(self.timing_grid))
        return all_events
    
    def get_events_in_measure(self, measure: int) -> List[Union[BassNote, ChordNote]]:
        """获取指定小节的所有事件"""
        events = []
        for note in self.bass_notes:
            if note.measure == measure:
                events.append(note)
        for note in self.chord_notes:
            if note.measure == measure:
                events.append(note)
        
        return sorted(events, key=lambda x: x.position)

class PetersenRhythmGenerator:
    """
    Petersen节奏生成器
    
    基于扩展音阶生成低音和和弦轨道，提供完整的节奏框架。
    """
    
    def __init__(self,
                 extended_scale: ExtendedScale,
                 bpm: int = 120,
                 rhythm_style: str = "traditional"):
        """
        初始化节奏生成器
        
        Args:
            extended_scale: 扩展音阶对象
            bpm: 每分钟拍数
            rhythm_style: 节奏风格（预设名称）
        """
        self.extended_scale = extended_scale
        self.bpm = bpm
        
        if rhythm_style in RHYTHM_STYLES:
            self.rhythm_style = rhythm_style
            self.style_config = RHYTHM_STYLES[rhythm_style]
        else:
            raise ValueError(f"未知的节奏风格: {rhythm_style}")
        
        self.rhythm_pattern = RhythmPattern()
        self.timing_grid = TimingGrid(bpm, self.rhythm_pattern)
        
        # 缓存根音序列
        self._root_sequence = None
    
    def _get_root_sequence(self) -> List[ScaleEntry]:
        """获取根音序列（五行顺序循环）"""
        if self._root_sequence is None:
            # 按五行顺序排列根音
            root_notes = self.extended_scale.root_notes
            
            # 按五行顺序（e值）和音区（n值）排序
            sorted_roots = sorted(root_notes, key=lambda x: (x.n, x.e))
            
            # 提取最低音区的五行序列作为基础
            if sorted_roots:
                base_zone = sorted_roots[0].n
                base_sequence = [r for r in sorted_roots if r.n == base_zone]
                self._root_sequence = base_sequence[:5]  # 确保只有5个
            else:
                self._root_sequence = []
        
        return self._root_sequence
    
    def _get_root_for_beat(self, measure: int, beat: int) -> ScaleEntry:
        """获取指定拍的根音"""
        root_sequence = self._get_root_sequence()
        if not root_sequence:
            raise ValueError("没有可用的根音序列")
        
        # 五行循环
        root_index = beat % len(root_sequence)
        return root_sequence[root_index]
    
    def _is_strong_beat(self, note_entry: ScaleEntry) -> bool:
        """判断是否为强拍（基于阴阳极性）"""
        # 阳位（p=1）为强拍，阴位（p=-1）为弱拍，中位（p=0）为中强拍
        if note_entry.p == 1:  # 阳位
            return True
        elif note_entry.p == -1:  # 阴位
            return False
        else:  # 中位（p=0）
            return True  # 根音通常为强拍
    
    def _calculate_velocity(self, is_strong_beat: bool, is_root: bool = False) -> int:
        """计算音符力度"""
        base_velocity = 80
        contrast = self.style_config["velocity_contrast"]
        
        if is_root:
            # 根音稍强
            return min(127, int(base_velocity + 20))
        elif is_strong_beat:
            # 强拍
            return min(127, int(base_velocity + contrast * 40))
        else:
            # 弱拍
            return max(1, int(base_velocity - contrast * 30))
    
    def generate_bass_track(self, measures: int) -> List[BassNote]:
        """
        生成低音轨道
        
        Args:
            measures: 小节数
            
        Returns:
            低音音符列表
        """
        bass_notes = []
        
        for measure in range(measures):
            for beat in range(self.rhythm_pattern.beats_per_measure):
                
                # 获取该拍的根音
                root_note = self._get_root_for_beat(measure, beat)
                
                # 计算音符位置（每拍第一个位置）
                position = beat * self.rhythm_pattern.notes_per_beat
                
                # 判断强弱拍
                is_strong = self._is_strong_beat(root_note)
                
                # 计算持续时间（基于风格）
                duration = self._calculate_bass_duration(beat)
                
                # 计算力度
                velocity = self._calculate_velocity(is_strong, is_root=True)
                
                bass_note = BassNote(
                    measure=measure,
                    beat=beat,
                    position=position,
                    note_entry=root_note,
                    duration=duration,
                    velocity=velocity,
                    is_strong_beat=is_strong,
                    is_root=True
                )
                
                bass_notes.append(bass_note)
        
        return bass_notes
    
    def _calculate_bass_duration(self, beat: int) -> float:
        """计算低音持续时间"""
        bass_pattern = self.style_config["bass_pattern"]
        
        if bass_pattern == "sustained":
            # 持续音模式：每个音持续整拍
            return 1.0
        elif bass_pattern == "walking":
            # 行进模式：较短持续时间
            return 0.8
        elif bass_pattern == "pedal_tone":
            # 持续音：长时间保持
            return 1.2
        elif bass_pattern == "gentle_walk":
            # 柔和行进：中等持续时间
            return 0.9
        else:  # root_emphasis
            # 根音强调：标准持续时间
            return 1.0
    
    def generate_chord_track(self, bass_track: List[BassNote]) -> List[ChordNote]:
        """
        基于低音轨道生成和弦轨道
        
        Args:
            bass_track: 低音轨道
            
        Returns:
            和弦音符列表
        """
        chord_notes = []
        chord_density = self.style_config["chord_density"]
        
        for bass_note in bass_track:
            
            # 根据密度设置决定和弦位置
            chord_positions = self._get_chord_positions(
                bass_note.beat, chord_density
            )
            
            # 获取该根音的和弦
            root_key = bass_note.note_entry.key_short
            chord_tones = self.extended_scale.chord_mapping.get(root_key, [])
            
            if not chord_tones:
                continue  # 如果没有和弦音则跳过
            
            # 在指定位置生成和弦音符
            for rel_pos in chord_positions:
                chord_position = bass_note.beat * self.rhythm_pattern.notes_per_beat + rel_pos
                
                # 选择和弦音（可能是部分和弦）
                selected_tones = self._select_chord_tones(chord_tones, chord_density)
                
                # 计算和弦持续时间
                chord_duration = self._calculate_chord_duration(rel_pos)
                
                # 判断强弱拍（基于位置）
                is_strong = rel_pos in [0, 3]  # 第1和第4位置为强位
                
                # 计算力度
                velocity = self._calculate_velocity(is_strong, is_root=False)
                
                chord_note = ChordNote(
                    measure=bass_note.measure,
                    beat=bass_note.beat,
                    position=chord_position,
                    chord_tones=selected_tones,
                    root_note=bass_note.note_entry,
                    duration=chord_duration,
                    velocity=velocity,
                    chord_type=self._describe_chord_type(selected_tones),
                    is_strong_beat=is_strong
                )
                
                chord_notes.append(chord_note)
        
        return chord_notes
    
    def _get_chord_positions(self, beat: int, density: str) -> List[int]:
        """获取和弦在拍内的位置"""
        if density == "sparse":
            # 稀疏：只在第4位置（弱拍）
            return [3]
        elif density == "medium":
            # 中等：第2、4位置
            return [1, 3]
        elif density == "dense":
            # 密集：第2、4、6位置
            return [1, 3, 5]
        elif density == "varied":
            # 变化：随机选择
            all_positions = [1, 2, 3, 4, 5]
            num_chords = random.choice([1, 2, 3])
            return sorted(random.sample(all_positions, num_chords))
        else:
            # 默认：第2、4位置
            return [1, 3]
    
    def _select_chord_tones(self, chord_tones: List[ChordTone], density: str) -> List[ChordTone]:
        """选择要演奏的和弦音"""
        if not chord_tones:
            return []
        
        if density in ["sparse", "meditative"]:
            # 稀疏：只选择1-2个和弦音
            return chord_tones[:min(2, len(chord_tones))]
        elif density == "dense":
            # 密集：使用所有和弦音
            return chord_tones
        else:
            # 中等：使用大部分和弦音
            return chord_tones[:min(3, len(chord_tones))]
    
    def _calculate_chord_duration(self, position: int) -> float:
        """计算和弦持续时间"""
        # 基于位置的不同持续时间
        if position in [1, 5]:  # 弱位置
            return 0.4
        elif position in [3]:    # 中强位置
            return 0.6
        else:                   # 其他位置
            return 0.5
    
    def _describe_chord_type(self, chord_tones: List[ChordTone]) -> str:
        """描述和弦类型"""
        if not chord_tones:
            return "无和弦"
        
        # 简单的和弦类型识别
        ratios = [tone.ratio_from_root for tone in chord_tones]
        
        if 5/4 in ratios and 3/2 in ratios:
            return "大三和弦"
        elif 6/5 in ratios and 3/2 in ratios:
            return "小三和弦"
        elif 3/2 in ratios:
            return "五度和声"
        else:
            return f"复合和弦({len(chord_tones)}音)"
    
    def generate_rhythm_track(self, measures: int) -> RhythmTrack:
        """
        生成完整的节奏轨道（低音+和弦）
        
        Args:
            measures: 小节数
            
        Returns:
            完整的节奏轨道
        """
        bass_track = self.generate_bass_track(measures)
        chord_track = self.generate_chord_track(bass_track)
        
        return RhythmTrack(
            bass_notes=bass_track,
            chord_notes=chord_track,
            timing_grid=self.timing_grid,
            rhythm_style=self.rhythm_style,
            total_measures=measures
        )
    
    def analyze_rhythm_structure(self, rhythm_track: RhythmTrack) -> Dict:
        """
        分析节奏结构
        
        Args:
            rhythm_track: 节奏轨道
            
        Returns:
            节奏分析结果
        """
        analysis = {
            "total_measures": rhythm_track.total_measures,
            "total_bass_notes": len(rhythm_track.bass_notes),
            "total_chord_notes": len(rhythm_track.chord_notes),
            "bpm": self.bpm,
            "rhythm_style": self.rhythm_style,
            "total_duration_seconds": 0,
            "strong_beat_ratio": 0,
            "chord_density_per_measure": 0,
            "root_note_distribution": defaultdict(int)
        }
        
        # 计算总时长
        if rhythm_track.bass_notes:
            last_note = max(rhythm_track.bass_notes, 
                          key=lambda x: x.get_end_time(rhythm_track.timing_grid))
            analysis["total_duration_seconds"] = last_note.get_end_time(rhythm_track.timing_grid)
        
        # 计算强拍比例
        strong_beats = sum(1 for note in rhythm_track.bass_notes if note.is_strong_beat)
        analysis["strong_beat_ratio"] = strong_beats / len(rhythm_track.bass_notes) if rhythm_track.bass_notes else 0
        
        # 计算和弦密度
        analysis["chord_density_per_measure"] = len(rhythm_track.chord_notes) / rhythm_track.total_measures if rhythm_track.total_measures > 0 else 0
        
        # 根音分布
        for note in rhythm_track.bass_notes:
            key = f"{note.note_entry.key_short}({note.note_entry.freq:.1f}Hz)"
            analysis["root_note_distribution"][key] += 1
        
        return analysis
    
    def export_rhythm_csv(self, rhythm_track: RhythmTrack, path: Union[str, Path] = None) -> None:
        """
        导出节奏轨道到CSV文件
        
        Args:
            rhythm_track: 节奏轨道
            path: 输出路径
        """
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"../data/petersen_rhythm_{self.rhythm_style}_{timestamp}.csv"
        
        path = Path(path)
        
        with open(path, 'w', encoding='utf-8') as f:
            # CSV头部
            f.write("轨道类型,小节,拍,位置,绝对时间(秒),音符/和弦,频率(Hz),持续时间(拍),力度,强弱拍,备注\n")
            
            # 获取所有事件并排序
            all_events = rhythm_track.get_all_events()
            
            for event in all_events:
                abs_time = event.get_absolute_time(rhythm_track.timing_grid)
                
                if isinstance(event, BassNote):
                    f.write(f"低音,{event.measure},{event.beat},{event.position},"
                           f"{abs_time:.3f},{event.note_entry.key_short},"
                           f"{event.note_entry.freq:.2f},{event.duration:.2f},"
                           f"{event.velocity},{'强' if event.is_strong_beat else '弱'},"
                           f"根音\n")
                
                elif isinstance(event, ChordNote):
                    chord_freqs = [f"{tone.freq:.1f}" for tone in event.chord_tones]
                    chord_names = [tone.ratio_name for tone in event.chord_tones]
                    
                    f.write(f"和弦,{event.measure},{event.beat},{event.position},"
                           f"{abs_time:.3f},{'+'.join(chord_names)},"
                           f"{'+'.join(chord_freqs)},{event.duration:.2f},"
                           f"{event.velocity},{'强' if event.is_strong_beat else '弱'},"
                           f"{event.chord_type}\n")
        
        print(f"节奏轨道已导出到: {path}")
    
    def export_rhythm_analysis_csv(self, rhythm_track: RhythmTrack, path: Union[str, Path] = None) -> None:
        """
        导出节奏分析到CSV文件
        
        Args:
            rhythm_track: 节奏轨道
            path: 输出路径
        """
        analysis = self.analyze_rhythm_structure(rhythm_track)
        
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"../data/petersen_rhythm_analysis_{self.rhythm_style}_{timestamp}.csv"
        
        path = Path(path)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write("分析项目,数值,单位\n")
            
            for key, value in analysis.items():
                if key == "root_note_distribution":
                    f.write("根音分布统计:\n")
                    for note, count in value.items():
                        f.write(f"  {note},{count},次\n")
                else:
                    f.write(f"{key},{value},\n")
        
        print(f"节奏分析已导出到: {path}")

def compare_rhythm_styles(extended_scale: ExtendedScale, measures: int = 4) -> None:
    """
    比较不同节奏风格的效果
    
    Args:
        extended_scale: 扩展音阶
        measures: 测试小节数
    """
    print("=== 节奏风格比较分析 ===\n")
    
    for style_name, style_config in RHYTHM_STYLES.items():
        print(f"【{style_name}】{style_config['description']}")
        
        generator = PetersenRhythmGenerator(
            extended_scale=extended_scale,
            bpm=120,
            rhythm_style=style_name
        )
        
        rhythm_track = generator.generate_rhythm_track(measures)
        analysis = generator.analyze_rhythm_structure(rhythm_track)
        
        print(f"  总时长: {analysis['total_duration_seconds']:.1f}秒")
        print(f"  低音音符: {analysis['total_bass_notes']}个")
        print(f"  和弦音符: {analysis['total_chord_notes']}个")
        print(f"  强拍比例: {analysis['strong_beat_ratio']:.1%}")
        print(f"  和弦密度: {analysis['chord_density_per_measure']:.1f}个/小节")
        print()

if __name__ == "__main__":
    # 示例用法
    from petersen_scale import PetersenScale
    from petersen_chord import PetersenChordExtender
    
    # 创建基础音阶和扩展
    base_scale = PetersenScale(F_base=55.0, phi=2.0, delta_theta=4.8)
    chord_extender = PetersenChordExtender(base_scale, chord_ratios="simple_ratios")
    extended_scale = chord_extender.extend_scale_with_chords()
    
    # 创建节奏生成器
    rhythm_gen = PetersenRhythmGenerator(
        extended_scale=extended_scale,
        bpm=120,
        rhythm_style="traditional"
    )
    
    # 生成节奏轨道
    print("生成节奏轨道...")
    rhythm_track = rhythm_gen.generate_rhythm_track(measures=4)
    
    # 分析节奏结构
    analysis = rhythm_gen.analyze_rhythm_structure(rhythm_track)
    print("\n节奏结构分析:")
    for key, value in analysis.items():
        if key != "root_note_distribution":
            print(f"  {key}: {value}")
    
    print("\n根音分布:")
    for note, count in analysis["root_note_distribution"].items():
        print(f"  {note}: {count}次")
    
    # 导出文件
    rhythm_gen.export_rhythm_csv(rhythm_track)
    rhythm_gen.export_rhythm_analysis_csv(rhythm_track)
    
    # 比较不同风格
    print("\n" + "="*50)
    compare_rhythm_styles(extended_scale, measures=2)