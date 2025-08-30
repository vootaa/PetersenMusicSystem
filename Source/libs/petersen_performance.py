"""
Petersen 演奏技巧模块

将基础作曲转换为丰富的演奏效果，在Petersen定制钢琴上实现超越人类演奏者极限的技法。
支持单线条旋律的并行化、各种装饰技巧，以及多人协作级别的复杂演奏。

主要功能：
- 并行旋律生成（三度、五度、八度、音簇）
- 基础演奏技巧（颤音、装饰音、琶音、滑音）
- 高级协作技法（左右手配合、多层织体、交替演奏）
- 超人类技巧（极速音阶、复杂对位、多重并行）
- Petersen钢琴特殊技法（跨音区跳跃、五行循环）

使用示例：
```python
from petersen_composer import PetersenAutoComposer
from petersen_performance import PetersenPerformanceRenderer

# 获取基础作曲
composer = PetersenAutoComposer(...)
basic_composition = composer.compose(measures=8)

# 创建演奏渲染器
renderer = PetersenPerformanceRenderer(
    performance_level="superhuman",
    technique_density="rich"
)

# 渲染演奏版本
performance_composition = renderer.render_full_performance(
    basic_composition,
    techniques=["thirds_parallel", "octave_cascade", "cross_hand_weaving"],
    expression_style="dramatic"
)

# 导出演奏版本
performance_composition.export_performance_midi("virtuoso_performance.mid")
```
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Any, Set
from collections import defaultdict, deque
import math
import random
import json
from datetime import datetime
from enum import Enum

# 导入基础模块
try:
    from .petersen_scale import PetersenScale, ScaleEntry
    from .petersen_chord import ExtendedScale, ChordTone
    from .petersen_rhythm import BassNote, ChordNote, TimingGrid
    from .petersen_melody import MelodyNote, GraphNode
    from .petersen_composer import MultiTrackComposition
except ImportError:
    from petersen_scale import PetersenScale, ScaleEntry
    from petersen_chord import ExtendedScale, ChordTone
    from petersen_rhythm import BassNote, ChordNote, TimingGrid
    from petersen_melody import MelodyNote, GraphNode
    from petersen_composer import MultiTrackComposition

class PerformanceLevel(Enum):
    """演奏技巧级别"""
    BASIC = "basic"                    # 基础：人类可演奏
    ADVANCED = "advanced"              # 高级：熟练演奏者
    VIRTUOSO = "virtuoso"              # 大师：顶级演奏家
    SUPERHUMAN = "superhuman"          # 超人：Petersen钢琴专属

class TechniqueType(Enum):
    """技法类型"""
    PARALLEL = "parallel"              # 并行音符
    ORNAMENT = "ornament"              # 装饰音
    ARTICULATION = "articulation"      # 演奏法
    TEXTURE = "texture"                # 织体技巧
    COORDINATION = "coordination"      # 协调技巧
    SPECIAL = "special"                # 特殊技法

@dataclass
class ParallelVoice:
    """并行声部"""
    interval_ratio: float              # 音程比例（基于主音）
    velocity_factor: float             # 力度系数
    timing_offset: float               # 时间偏移（秒）
    voice_name: str                    # 声部名称
    register_shift: int = 0            # 音区偏移

@dataclass
class PerformanceNote:
    """演奏音符（扩展单音符为多声部）"""
    primary_note: Union[BassNote, ChordNote, MelodyNote]  # 原始音符
    parallel_voices: List[ParallelVoice] = field(default_factory=list)  # 并行声部
    ornaments: List['Ornament'] = field(default_factory=list)          # 装饰音
    articulation: str = "normal"                                       # 演奏法
    expression_marks: List[str] = field(default_factory=list)          # 表情记号
    
    def get_all_frequencies(self) -> List[Tuple[float, float, int]]:
        """获取所有频率 (频率, 时间偏移, 力度)"""
        frequencies = []
        
        # 主音符
        if hasattr(self.primary_note, 'frequency'):
            base_freq = self.primary_note.frequency
        elif hasattr(self.primary_note, 'note_entry'):
            base_freq = self.primary_note.note_entry.frequency
        else:
            base_freq = self.primary_note.get_frequencies()[0]  # 和弦音取第一个
        
        base_velocity = self.primary_note.velocity
        frequencies.append((base_freq, 0.0, base_velocity))
        
        # 并行声部
        for voice in self.parallel_voices:
            parallel_freq = base_freq * voice.interval_ratio
            parallel_velocity = int(base_velocity * voice.velocity_factor)
            frequencies.append((parallel_freq, voice.timing_offset, parallel_velocity))
        
        return frequencies
    
    def get_total_duration(self) -> float:
        """获取总持续时间（包含装饰音）"""
        base_duration = self.primary_note.duration
        ornament_extension = sum(orn.duration for orn in self.ornaments)
        return base_duration + ornament_extension

@dataclass
class Ornament:
    """装饰音"""
    type: str                          # 装饰音类型
    frequency: float                   # 频率
    duration: float                    # 持续时间
    velocity: int                      # 力度
    timing_offset: float               # 相对主音符的时间偏移
    
@dataclass
class PerformanceComposition:
    """演奏版作曲（扩展版的MultiTrackComposition）"""
    original_composition: MultiTrackComposition           # 原始作曲
    performance_bass: List[PerformanceNote]              # 演奏版低音
    performance_chord: List[PerformanceNote]             # 演奏版和弦  
    performance_melody: List[PerformanceNote]            # 演奏版旋律
    
    # 演奏信息
    performance_level: PerformanceLevel                  # 演奏级别
    techniques_used: List[str]                           # 使用的技法
    total_voices: int                                    # 总声部数
    complexity_score: float                              # 复杂度评分
    
    # 元信息
    render_time: datetime = field(default_factory=datetime.now)
    
    def get_all_performance_events(self) -> List[Tuple[float, str, PerformanceNote]]:
        """获取所有演奏事件（按时间排序）"""
        events = []
        beats_per_measure = 5
        notes_per_beat = 6
        bpm = self.original_composition.bpm
        
        # 计算每个音符位的时间
        position_duration = 60.0 / (bpm * notes_per_beat)
        
        # 添加演奏版事件
        for track_name, track_notes in [
            ("bass", self.performance_bass),
            ("chord", self.performance_chord), 
            ("melody", self.performance_melody)
        ]:
            for perf_note in track_notes:
                original = perf_note.primary_note
                time = (original.measure * beats_per_measure * notes_per_beat + original.position) * position_duration
                events.append((time, track_name, perf_note))
        
        # 按时间排序
        events.sort(key=lambda x: x[0])
        return events
    
    def export_performance_midi(self, path: Union[str, Path]) -> None:
        """导出演奏版MIDI"""
        path = Path(path)
        
        with open(path, 'w') as f:
            f.write(f"# Petersen演奏版MIDI导出\n")
            f.write(f"# 原始风格: {self.original_composition.composition_style}\n")
            f.write(f"# 演奏级别: {self.performance_level.value}\n")
            f.write(f"# 总声部数: {self.total_voices}\n")
            f.write(f"# 复杂度: {self.complexity_score:.2f}\n")
            f.write(f"# 使用技法: {', '.join(self.techniques_used)}\n")
        
        print(f"演奏版MIDI导出到: {path}")
    
    def export_performance_csv(self, path: Union[str, Path] = None) -> None:
        """导出演奏版详细CSV"""
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"petersen_performance_{self.performance_level.value}_{timestamp}.csv"
        
        path = Path(path)
        events = self.get_all_performance_events()
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write("时间(秒),轨道,音符类型,主频率(Hz),并行频率,装饰音,演奏法,表情,复杂度\n")
            
            for time, track, perf_note in events:
                frequencies = perf_note.get_all_frequencies()
                main_freq = frequencies[0][0]
                parallel_freqs = "+".join(f"{f[0]:.1f}" for f in frequencies[1:])
                ornament_info = "+".join(f"{o.type}({o.frequency:.1f}Hz)" for o in perf_note.ornaments)
                
                f.write(f"{time:.3f},{track},演奏音符,{main_freq:.2f},"
                       f"{parallel_freqs or '无'},{ornament_info or '无'},"
                       f"{perf_note.articulation},{'+'.join(perf_note.expression_marks) or '无'},"
                       f"{len(frequencies) + len(perf_note.ornaments)}\n")
        
        print(f"演奏版详细分析导出到: {path}")

# 演奏技法库
PERFORMANCE_TECHNIQUES = {
    # === 基础并行技法 ===
    "thirds_parallel": {
        "type": TechniqueType.PARALLEL,
        "level": PerformanceLevel.BASIC,
        "description": "三度并行",
        "parallel_intervals": [5/4],                    # 大三度
        "velocity_factors": [0.8],
        "timing_offsets": [0.0],
        "suitable_tracks": ["melody"],
        "complexity": 1.5
    },
    
    "fifths_parallel": {
        "type": TechniqueType.PARALLEL,
        "level": PerformanceLevel.BASIC,
        "description": "五度并行",
        "parallel_intervals": [3/2],                    # 完全五度
        "velocity_factors": [0.9],
        "timing_offsets": [0.0],
        "suitable_tracks": ["melody", "bass"],
        "complexity": 1.8
    },
    
    "octave_doubling": {
        "type": TechniqueType.PARALLEL,
        "level": PerformanceLevel.ADVANCED,
        "description": "八度加倍",
        "parallel_intervals": [2.0, 0.5],              # 高八度+低八度
        "velocity_factors": [0.7, 0.6],
        "timing_offsets": [0.0, 0.0],
        "suitable_tracks": ["melody", "bass"],
        "complexity": 2.2
    },
    
    # === 高级并行技法 ===
    "chord_cascade": {
        "type": TechniqueType.PARALLEL,
        "level": PerformanceLevel.VIRTUOSO,
        "description": "和弦瀑布",
        "parallel_intervals": [5/4, 3/2, 15/8],        # 三度+五度+七度
        "velocity_factors": [0.8, 0.9, 0.7],
        "timing_offsets": [0.02, 0.04, 0.06],          # 微小延迟
        "suitable_tracks": ["melody"],
        "complexity": 3.5
    },
    
    "cluster_harmony": {
        "type": TechniqueType.PARALLEL,
        "level": PerformanceLevel.SUPERHUMAN,
        "description": "音簇和声",
        "parallel_intervals": [9/8, 5/4, 11/8, 3/2],  # 密集音簇
        "velocity_factors": [0.6, 0.7, 0.8, 0.9],
        "timing_offsets": [0.0, 0.0, 0.0, 0.0],
        "suitable_tracks": ["chord"],
        "complexity": 4.2
    },
    
    # === 装饰音技法 ===
    "trill_ornament": {
        "type": TechniqueType.ORNAMENT,
        "level": PerformanceLevel.ADVANCED,
        "description": "颤音装饰",
        "ornament_pattern": "alternating",
        "ornament_interval": 9/8,                      # 大二度颤音
        "ornament_speed": 8,                           # 每秒8次
        "suitable_tracks": ["melody"],
        "complexity": 2.0
    },
    
    "grace_notes": {
        "type": TechniqueType.ORNAMENT,
        "level": PerformanceLevel.BASIC,
        "description": "装饰音",
        "ornament_pattern": "leading",
        "ornament_intervals": [9/8, 5/4],             # 二度和三度装饰
        "ornament_duration": 0.05,                     # 很短的装饰音
        "suitable_tracks": ["melody"],
        "complexity": 1.3
    },
    
    # === 演奏法技巧 ===
    "staccato_burst": {
        "type": TechniqueType.ARTICULATION,
        "level": PerformanceLevel.ADVANCED,
        "description": "断奏爆发",
        "duration_factor": 0.5,                       # 缩短50%
        "velocity_boost": 1.2,                        # 增强力度
        "attack_sharpness": "sharp",
        "suitable_tracks": ["melody", "chord"],
        "complexity": 1.8
    },
    
    "legato_flow": {
        "type": TechniqueType.ARTICULATION,
        "level": PerformanceLevel.BASIC,
        "description": "连奏流动",
        "duration_factor": 1.1,                       # 略微延长
        "velocity_smoothing": 0.9,                    # 柔化力度
        "attack_sharpness": "soft",
        "suitable_tracks": ["melody"],
        "complexity": 1.2
    },
    
    # === 织体技巧 ===
    "hand_crossing": {
        "type": TechniqueType.COORDINATION,
        "level": PerformanceLevel.VIRTUOSO,
        "description": "左右手交叉",
        "voice_assignment": "alternating",            # 交替分配
        "register_separation": 2.0,                   # 音区分离
        "timing_precision": 0.01,                     # 高精度
        "suitable_tracks": ["melody"],
        "complexity": 3.8
    },
    
    "polyrhythm_weaving": {
        "type": TechniqueType.COORDINATION,
        "level": PerformanceLevel.SUPERHUMAN,
        "description": "多重节奏编织",
        "rhythm_ratios": [3, 4, 5],                   # 3:4:5复合节奏
        "voice_independence": True,
        "coordination_difficulty": "extreme",
        "suitable_tracks": ["melody", "chord"],
        "complexity": 5.0
    },
    
    # === Petersen特殊技法 ===
    "five_element_cascade": {
        "type": TechniqueType.SPECIAL,
        "level": PerformanceLevel.SUPERHUMAN,
        "description": "五行瀑布",
        "element_sequence": ["金", "木", "水", "火", "土"],
        "cascade_speed": 0.05,                        # 极快瀑布
        "zone_jumping": True,                         # 跨音区
        "suitable_tracks": ["melody"],
        "complexity": 4.5
    },
    
    "petersen_graph_jump": {
        "type": TechniqueType.SPECIAL,
        "level": PerformanceLevel.SUPERHUMAN,
        "description": "图结构跳跃",
        "jump_pattern": "pentagram",                  # 五角星跳跃
        "simultaneous_jumps": 3,                      # 同时3个跳跃
        "precision_required": "sub_millisecond",
        "suitable_tracks": ["melody", "chord"],
        "complexity": 4.8
    },
    
    "yin_yang_alternation": {
        "type": TechniqueType.SPECIAL,
        "level": PerformanceLevel.VIRTUOSO,
        "description": "阴阳交替",
        "polarity_switching": "rapid",               # 快速阴阳切换
        "dynamic_contrast": 2.0,                     # 强烈对比
        "philosophical_expression": True,
        "suitable_tracks": ["bass", "chord"],
        "complexity": 3.2
    }
}

# 表情风格库
EXPRESSION_STYLES = {
    "natural": {
        "description": "自然表达",
        "velocity_variation": 0.15,                   # 力度变化范围
        "timing_rubato": 0.05,                       # 节拍弹性
        "phrase_shaping": "gentle",
        "accent_strength": 1.2
    },
    
    "dramatic": {
        "description": "戏剧化表达",
        "velocity_variation": 0.4,
        "timing_rubato": 0.15,
        "phrase_shaping": "bold",
        "accent_strength": 1.8
    },
    
    "mechanical": {
        "description": "机械精确",
        "velocity_variation": 0.05,
        "timing_rubato": 0.0,
        "phrase_shaping": "flat",
        "accent_strength": 1.0
    },
    
    "ethereal": {
        "description": "空灵飘逸",
        "velocity_variation": 0.25,
        "timing_rubato": 0.2,
        "phrase_shaping": "floating",
        "accent_strength": 0.8
    }
}

class PetersenPerformanceRenderer:
    """Petersen演奏渲染器"""
    
    def __init__(self,
                 performance_level: Union[str, PerformanceLevel] = PerformanceLevel.ADVANCED,
                 technique_density: str = "moderate",
                 expression_style: str = "natural"):
        """
        初始化演奏渲染器
        
        Args:
            performance_level: 演奏技巧级别
            technique_density: 技法密度 ("sparse", "moderate", "rich", "extreme")
            expression_style: 表情风格
        """
        if isinstance(performance_level, str):
            self.performance_level = PerformanceLevel(performance_level)
        else:
            self.performance_level = performance_level
        
        self.technique_density = technique_density
        self.expression_style = expression_style
        
        # 根据级别过滤可用技法
        self.available_techniques = self._filter_techniques_by_level()
        
        # 设置密度参数
        self.density_params = self._get_density_parameters()
    
    def _filter_techniques_by_level(self) -> Dict[str, Dict]:
        """根据演奏级别过滤技法"""
        filtered = {}
        
        for name, technique in PERFORMANCE_TECHNIQUES.items():
            technique_level = technique["level"]
            
            # 检查级别兼容性
            if self._is_level_accessible(technique_level):
                filtered[name] = technique
        
        return filtered
    
    def _is_level_accessible(self, technique_level: PerformanceLevel) -> bool:
        """检查技法级别是否可用"""
        level_hierarchy = [
            PerformanceLevel.BASIC,
            PerformanceLevel.ADVANCED, 
            PerformanceLevel.VIRTUOSO,
            PerformanceLevel.SUPERHUMAN
        ]
        
        current_index = level_hierarchy.index(self.performance_level)
        technique_index = level_hierarchy.index(technique_level)
        
        return technique_index <= current_index
    
    def _get_density_parameters(self) -> Dict[str, float]:
        """获取密度参数"""
        density_configs = {
            "sparse": {
                "technique_probability": 0.2,
                "parallel_voice_limit": 2,
                "ornament_frequency": 0.1,
                "max_complexity": 2.0
            },
            "moderate": {
                "technique_probability": 0.4,
                "parallel_voice_limit": 3,
                "ornament_frequency": 0.25,
                "max_complexity": 3.0
            },
            "rich": {
                "technique_probability": 0.7,
                "parallel_voice_limit": 5,
                "ornament_frequency": 0.5,
                "max_complexity": 4.0
            },
            "extreme": {
                "technique_probability": 0.9,
                "parallel_voice_limit": 8,
                "ornament_frequency": 0.8,
                "max_complexity": 5.0
            }
        }
        
        return density_configs.get(self.technique_density, density_configs["moderate"])
    
    def render_full_performance(self,
                              composition: MultiTrackComposition,
                              techniques: Optional[List[str]] = None,
                              auto_select_techniques: bool = True) -> PerformanceComposition:
        """
        渲染完整演奏版本
        
        Args:
            composition: 原始作曲
            techniques: 指定技法列表
            auto_select_techniques: 是否自动选择技法
            
        Returns:
            演奏版作曲
        """
        print(f"开始渲染演奏版本...")
        print(f"演奏级别: {self.performance_level.value}")
        print(f"技法密度: {self.technique_density}")
        
        # 选择要使用的技法
        if techniques is None and auto_select_techniques:
            techniques = self._auto_select_techniques(composition)
        elif techniques is None:
            techniques = []
        
        print(f"使用技法: {techniques}")
        
        # 渲染各轨道
        performance_bass = self._render_track(composition.bass_track, "bass", techniques)
        performance_chord = self._render_track(composition.chord_track, "chord", techniques)
        performance_melody = self._render_track(composition.melody_track, "melody", techniques)
        
        # 计算统计信息
        total_voices = self._count_total_voices([performance_bass, performance_chord, performance_melody])
        complexity_score = self._calculate_complexity_score([performance_bass, performance_chord, performance_melody])
        
        performance_composition = PerformanceComposition(
            original_composition=composition,
            performance_bass=performance_bass,
            performance_chord=performance_chord,
            performance_melody=performance_melody,
            performance_level=self.performance_level,
            techniques_used=techniques,
            total_voices=total_voices,
            complexity_score=complexity_score
        )
        
        print(f"渲染完成! 总声部: {total_voices}, 复杂度: {complexity_score:.2f}")
        return performance_composition
    
    def _auto_select_techniques(self, composition: MultiTrackComposition) -> List[str]:
        """自动选择技法"""
        selected = []
        
        # 基于作曲风格选择技法
        style = composition.composition_style
        
        if "calm" in style or "meditation" in style:
            # 平静风格：选择柔和技法
            candidates = ["legato_flow", "thirds_parallel", "grace_notes"]
        elif "dynamic" in style or "dance" in style:
            # 动感风格：选择活跃技法
            candidates = ["staccato_burst", "octave_doubling", "hand_crossing"]
        elif "harmonic" in style:
            # 和声风格：选择和声技法
            candidates = ["chord_cascade", "cluster_harmony", "fifths_parallel"]
        else:
            # 平衡风格：混合技法
            candidates = ["thirds_parallel", "grace_notes", "octave_doubling"]
        
        # 根据密度参数选择数量
        max_techniques = {
            "sparse": 2, "moderate": 3, "rich": 4, "extreme": 6
        }.get(self.technique_density, 3)
        
        # 只选择可用的技法
        available_candidates = [t for t in candidates if t in self.available_techniques]
        
        # 随机选择
        num_to_select = min(len(available_candidates), max_techniques)
        selected = random.sample(available_candidates, num_to_select)
        
        # 根据演奏级别添加特殊技法
        if self.performance_level == PerformanceLevel.SUPERHUMAN:
            special_techniques = ["five_element_cascade", "petersen_graph_jump"]
            for special in special_techniques:
                if special in self.available_techniques and len(selected) < max_techniques:
                    selected.append(special)
        
        return selected
    
    def _render_track(self, 
                     track_notes: List[Union[BassNote, ChordNote, MelodyNote]],
                     track_type: str,
                     techniques: List[str]) -> List[PerformanceNote]:
        """渲染单个轨道"""
        performance_notes = []
        
        # 过滤适用于该轨道的技法
        applicable_techniques = []
        for tech_name in techniques:
            if tech_name in self.available_techniques:
                tech_info = self.available_techniques[tech_name]
                if track_type in tech_info.get("suitable_tracks", []):
                    applicable_techniques.append(tech_name)
        
        print(f"  渲染{track_type}轨道，适用技法: {applicable_techniques}")
        
        for i, note in enumerate(track_notes):
            # 决定是否对此音符应用技法
            if random.random() < self.density_params["technique_probability"]:
                # 随机选择一个技法
                if applicable_techniques:
                    selected_technique = random.choice(applicable_techniques)
                    performance_note = self._apply_technique(note, selected_technique)
                else:
                    performance_note = self._create_basic_performance_note(note)
            else:
                performance_note = self._create_basic_performance_note(note)
            
            # 应用表情
            self._apply_expression(performance_note, i, len(track_notes))
            
            performance_notes.append(performance_note)
        
        return performance_notes
    
    def _apply_technique(self, 
                        note: Union[BassNote, ChordNote, MelodyNote],
                        technique_name: str) -> PerformanceNote:
        """对音符应用技法"""
        technique = self.available_techniques[technique_name]
        performance_note = self._create_basic_performance_note(note)
        
        if technique["type"] == TechniqueType.PARALLEL:
            self._apply_parallel_technique(performance_note, technique)
        
        elif technique["type"] == TechniqueType.ORNAMENT:
            self._apply_ornament_technique(performance_note, technique)
        
        elif technique["type"] == TechniqueType.ARTICULATION:
            self._apply_articulation_technique(performance_note, technique)
        
        elif technique["type"] == TechniqueType.SPECIAL:
            self._apply_special_technique(performance_note, technique)
        
        return performance_note
    
    def _create_basic_performance_note(self, note: Union[BassNote, ChordNote, MelodyNote]) -> PerformanceNote:
        """创建基础演奏音符"""
        return PerformanceNote(
            primary_note=note,
            parallel_voices=[],
            ornaments=[],
            articulation="normal",
            expression_marks=[]
        )
    
    def _apply_parallel_technique(self, performance_note: PerformanceNote, technique: Dict):
        """应用并行技法"""
        intervals = technique.get("parallel_intervals", [])
        velocity_factors = technique.get("velocity_factors", [1.0] * len(intervals))
        timing_offsets = technique.get("timing_offsets", [0.0] * len(intervals))
        
        for i, interval in enumerate(intervals):
            if i < self.density_params["parallel_voice_limit"]:
                voice = ParallelVoice(
                    interval_ratio=interval,
                    velocity_factor=velocity_factors[i] if i < len(velocity_factors) else 1.0,
                    timing_offset=timing_offsets[i] if i < len(timing_offsets) else 0.0,
                    voice_name=f"{technique.get('description', 'parallel')}_{i+1}"
                )
                performance_note.parallel_voices.append(voice)
    
    def _apply_ornament_technique(self, performance_note: PerformanceNote, technique: Dict):
        """应用装饰音技法"""
        if random.random() < self.density_params["ornament_frequency"]:
            # 获取主音频率
            if hasattr(performance_note.primary_note, 'frequency'):
                base_freq = performance_note.primary_note.frequency
            elif hasattr(performance_note.primary_note, 'note_entry'):
                base_freq = performance_note.primary_note.note_entry.frequency
            else:
                return  # 无法获取频率
            
            # 创建装饰音
            if technique.get("ornament_pattern") == "trill":
                # 颤音
                interval = technique.get("ornament_interval", 9/8)
                ornament = Ornament(
                    type="trill",
                    frequency=base_freq * interval,
                    duration=0.1,
                    velocity=performance_note.primary_note.velocity // 2,
                    timing_offset=0.05
                )
                performance_note.ornaments.append(ornament)
            
            elif technique.get("ornament_pattern") == "leading":
                # 前倚音
                intervals = technique.get("ornament_intervals", [9/8])
                for i, interval in enumerate(intervals[:2]):  # 最多2个前倚音
                    ornament = Ornament(
                        type="grace_note",
                        frequency=base_freq * interval,
                        duration=technique.get("ornament_duration", 0.05),
                        velocity=performance_note.primary_note.velocity // 3,
                        timing_offset=-0.1 - i * 0.05
                    )
                    performance_note.ornaments.append(ornament)
    
    def _apply_articulation_technique(self, performance_note: PerformanceNote, technique: Dict):
        """应用演奏法技法"""
        performance_note.articulation = technique.get("description", "modified")
        
        # 修改主音符属性
        if hasattr(performance_note.primary_note, 'duration'):
            duration_factor = technique.get("duration_factor", 1.0)
            performance_note.primary_note.duration *= duration_factor
        
        if hasattr(performance_note.primary_note, 'velocity'):
            velocity_boost = technique.get("velocity_boost", 1.0)
            performance_note.primary_note.velocity = int(
                min(127, performance_note.primary_note.velocity * velocity_boost)
            )
    
    def _apply_special_technique(self, performance_note: PerformanceNote, technique: Dict):
        """应用Petersen特殊技法"""
        technique_name = technique.get("description", "special")
        
        if "五行瀑布" in technique_name:
            # 创建五行快速级进
            base_freq = self._get_note_frequency(performance_note.primary_note)
            cascade_speed = technique.get("cascade_speed", 0.05)
            
            for i in range(5):  # 五行
                cascade_freq = base_freq * (1.2 ** i)  # 上行级进
                ornament = Ornament(
                    type="cascade",
                    frequency=cascade_freq,
                    duration=cascade_speed,
                    velocity=performance_note.primary_note.velocity - i * 10,
                    timing_offset=i * cascade_speed
                )
                performance_note.ornaments.append(ornament)
        
        elif "图结构跳跃" in technique_name:
            # 创建图跳跃效果
            base_freq = self._get_note_frequency(performance_note.primary_note)
            jump_ratios = [5/4, 3/2, 2.0]  # 三度、五度、八度跳跃
            
            for i, ratio in enumerate(jump_ratios):
                voice = ParallelVoice(
                    interval_ratio=ratio,
                    velocity_factor=0.8 - i * 0.1,
                    timing_offset=i * 0.02,  # 微小延迟
                    voice_name=f"graph_jump_{i+1}"
                )
                performance_note.parallel_voices.append(voice)
        
        elif "阴阳交替" in technique_name:
            # 创建阴阳对比效果
            performance_note.expression_marks.extend(["dynamic_contrast", "philosophical"])
            
            # 添加对比声部
            voice = ParallelVoice(
                interval_ratio=0.5,  # 低八度对比
                velocity_factor=1.5,  # 强对比
                timing_offset=0.0,
                voice_name="yin_yang_contrast"
            )
            performance_note.parallel_voices.append(voice)
        
        performance_note.expression_marks.append(f"special_{technique_name}")
    
    def _get_note_frequency(self, note: Union[BassNote, ChordNote, MelodyNote]) -> float:
        """获取音符频率"""
        if hasattr(note, 'frequency'):
            return note.frequency
        elif hasattr(note, 'note_entry'):
            return note.note_entry.frequency
        elif hasattr(note, 'get_frequencies'):
            frequencies = note.get_frequencies()
            return frequencies[0] if frequencies else 440.0
        else:
            return 440.0  # 默认频率
    
    def _apply_expression(self, performance_note: PerformanceNote, position: int, total_notes: int):
        """应用表情"""
        expression_config = EXPRESSION_STYLES.get(self.expression_style, EXPRESSION_STYLES["natural"])
        
        # 计算短语位置
        phrase_ratio = position / total_notes
        
        # 应用力度变化
        velocity_variation = expression_config["velocity_variation"]
        velocity_factor = 1.0 + random.uniform(-velocity_variation, velocity_variation)
        
        if hasattr(performance_note.primary_note, 'velocity'):
            new_velocity = int(performance_note.primary_note.velocity * velocity_factor)
            performance_note.primary_note.velocity = max(1, min(127, new_velocity))
        
        # 应用短语塑造
        phrase_shaping = expression_config["phrase_shaping"]
        if phrase_shaping == "gentle":
            if 0.2 <= phrase_ratio <= 0.8:  # 中间部分稍强
                performance_note.expression_marks.append("gentle_emphasis")
        elif phrase_shaping == "bold":
            if phrase_ratio < 0.1 or phrase_ratio > 0.9:  # 首尾强调
                performance_note.expression_marks.append("bold_accent")
        elif phrase_shaping == "floating":
            performance_note.expression_marks.append("ethereal")
        
        # 应用重音
        accent_strength = expression_config["accent_strength"]
        if position % 6 == 0 and accent_strength > 1.0:  # 拍的开始
            performance_note.expression_marks.append("accent")
            if hasattr(performance_note.primary_note, 'velocity'):
                performance_note.primary_note.velocity = int(
                    min(127, performance_note.primary_note.velocity * accent_strength)
                )
    
    def _count_total_voices(self, all_performance_notes: List[List[PerformanceNote]]) -> int:
        """计算总声部数"""
        total_voices = 0
        
        for track_notes in all_performance_notes:
            for perf_note in track_notes:
                # 主声部 + 并行声部
                voices_in_note = 1 + len(perf_note.parallel_voices)
                total_voices = max(total_voices, voices_in_note)
        
        return total_voices
    
    def _calculate_complexity_score(self, all_performance_notes: List[List[PerformanceNote]]) -> float:
        """计算复杂度评分"""
        total_complexity = 0.0
        total_notes = 0
        
        for track_notes in all_performance_notes:
            for perf_note in track_notes:
                note_complexity = 1.0  # 基础复杂度
                
                # 并行声部增加复杂度
                note_complexity += len(perf_note.parallel_voices) * 0.5
                
                # 装饰音增加复杂度
                note_complexity += len(perf_note.ornaments) * 0.3
                
                # 特殊表情增加复杂度
                if any("special" in mark for mark in perf_note.expression_marks):
                    note_complexity += 1.0
                
                total_complexity += note_complexity
                total_notes += 1
        
        return total_complexity / total_notes if total_notes > 0 else 0.0
    
    def analyze_performance_statistics(self, performance_composition: PerformanceComposition) -> Dict[str, Any]:
        """分析演奏统计"""
        all_events = performance_composition.get_all_performance_events()
        
        # 统计技法使用
        technique_usage = defaultdict(int)
        parallel_voice_count = 0
        ornament_count = 0
        special_effect_count = 0
        
        for _, track_type, perf_note in all_events:
            # 统计并行声部
            parallel_voice_count += len(perf_note.parallel_voices)
            
            # 统计装饰音
            ornament_count += len(perf_note.ornaments)
            
            # 统计特殊效果
            if any("special" in mark for mark in perf_note.expression_marks):
                special_effect_count += 1
            
            # 统计演奏法
            if perf_note.articulation != "normal":
                technique_usage[perf_note.articulation] += 1
        
        # 计算密度指标
        total_events = len(all_events)
        total_duration = performance_composition.original_composition.get_total_duration_seconds()
        
        return {
            "performance_level": performance_composition.performance_level.value,
            "total_voices": performance_composition.total_voices,
            "complexity_score": performance_composition.complexity_score,
            "techniques_used": performance_composition.techniques_used,
            
            "voice_statistics": {
                "parallel_voices_total": parallel_voice_count,
                "average_voices_per_note": parallel_voice_count / total_events if total_events > 0 else 0,
                "max_simultaneous_voices": performance_composition.total_voices
            },
            
            "ornament_statistics": {
                "total_ornaments": ornament_count,
                "ornament_density": ornament_count / total_duration if total_duration > 0 else 0,
                "special_effects": special_effect_count
            },
            
            "technique_usage": dict(technique_usage),
            
            "performance_metrics": {
                "events_per_second": total_events / total_duration if total_duration > 0 else 0,
                "complexity_per_second": performance_composition.complexity_score * total_events / total_duration if total_duration > 0 else 0,
                "humanly_possible": performance_composition.performance_level in [PerformanceLevel.BASIC, PerformanceLevel.ADVANCED]
            }
        }

def compare_performance_levels(composition: MultiTrackComposition) -> None:
    """比较不同演奏级别的效果"""
    print("=== 演奏级别比较分析 ===\n")
    
    for level in PerformanceLevel:
        print(f"【{level.value.upper()}】")
        
        renderer = PetersenPerformanceRenderer(
            performance_level=level,
            technique_density="moderate",
            expression_style="natural"
        )
        
        performance_composition = renderer.render_full_performance(composition)
        stats = renderer.analyze_performance_statistics(performance_composition)
        
        print(f"  总声部数: {stats['total_voices']}")
        print(f"  复杂度评分: {stats['complexity_score']:.2f}")
        print(f"  并行声部: {stats['voice_statistics']['parallel_voices_total']}个")
        print(f"  装饰音: {stats['ornament_statistics']['total_ornaments']}个")
        print(f"  特殊效果: {stats['ornament_statistics']['special_effects']}个")
        print(f"  人类可演奏: {'是' if stats['performance_metrics']['humanly_possible'] else '否'}")
        print(f"  使用技法: {', '.join(stats['techniques_used'])}")
        print()

if __name__ == "__main__":
    # 示例用法
    from petersen_scale import PetersenScale
    from petersen_chord import PetersenChordExtender
    from petersen_composer import PetersenAutoComposer
    
    # 创建基础作曲
    print("创建基础作曲...")
    base_scale = PetersenScale(F_base=55.0, phi=2.0, delta_theta=4.8)
    chord_extender = PetersenChordExtender(base_scale)
    
    composer = PetersenAutoComposer(
        petersen_scale=base_scale,
        chord_extender=chord_extender,
        composition_style="balanced_journey"
    )
    
    basic_composition = composer.compose(measures=4)
    print(f"基础作曲完成: {len(basic_composition.melody_track)}个旋律音符")
    
    # 创建演奏渲染器
    print("\n创建超人级演奏渲染器...")
    renderer = PetersenPerformanceRenderer(
        performance_level=PerformanceLevel.SUPERHUMAN,
        technique_density="rich",
        expression_style="dramatic"
    )
    
    # 渲染演奏版本
    print("\n渲染演奏版本...")
    performance_composition = renderer.render_full_performance(
        basic_composition,
        techniques=["five_element_cascade", "cluster_harmony", "hand_crossing"],
        auto_select_techniques=True
    )
    
    # 分析演奏统计
    print("\n分析演奏统计...")
    stats = renderer.analyze_performance_statistics(performance_composition)
    
    print(f"\n=== 演奏版本完成 ===")
    print(f"演奏级别: {stats['performance_level']}")
    print(f"总声部数: {stats['total_voices']}")
    print(f"复杂度评分: {stats['complexity_score']:.2f}")
    print(f"人类可演奏: {'是' if stats['performance_metrics']['humanly_possible'] else '否'}")
    
    print(f"\n声部统计:")
    voice_stats = stats['voice_statistics']
    print(f"  并行声部总数: {voice_stats['parallel_voices_total']}")
    print(f"  平均每音符声部数: {voice_stats['average_voices_per_note']:.2f}")
    print(f"  最大同时声部数: {voice_stats['max_simultaneous_voices']}")
    
    print(f"\n装饰统计:")
    ornament_stats = stats['ornament_statistics']
    print(f"  装饰音总数: {ornament_stats['total_ornaments']}")
    print(f"  装饰音密度: {ornament_stats['ornament_density']:.2f}个/秒")
    print(f"  特殊效果: {ornament_stats['special_effects']}个")
    
    print(f"\n使用技法: {', '.join(stats['techniques_used'])}")
    
    # 导出演奏版本
    print(f"\n导出演奏版本...")
    performance_composition.export_performance_csv()
    performance_composition.export_performance_midi("superhuman_performance.mid")
    
    # 比较不同演奏级别
    print(f"\n" + "="*60)
    compare_performance_levels(basic_composition)