"""
Petersen 和弦扩展模块

基于Petersen音阶系统，实现根音提取和和弦扩展功能。
从五行"中"极性音符中提取根音，然后基于传统和弦比率扩展出完整的和弦音阶。

主要功能：
- 提取五行"中"极性的最低3个音区作为根音（15个）
- 基于传统和弦比率（3/2、5/4、6/5等）生成和弦音
- 智能匹配现有音阶或创建新的和弦音
- 生成扩展音阶（原音阶 + 和弦音）
- 提供根音到和弦的映射关系

使用示例：
```python
from petersen_scale import PetersenScale
from petersen_chord import PetersenChordExtender

# 创建基础音阶
base_scale = PetersenScale(F_base=55.0, phi=2.0)  # A1基频，八度关系

# 创建和弦扩展器
extender = PetersenChordExtender(
    petersen_scale=base_scale,
    chord_ratios=[3/2, 5/4, 6/5],  # 完全五度、大三度、小三度
    tolerance_cents=50  # 50音分容差
)

# 生成扩展音阶
extended_scale = extender.extend_scale_with_chords()

# 获取根音列表
root_notes = extender.extract_root_notes()

# 获取特定根音的和弦
chord = extender.get_chord_for_root("J0")  # 金中的和弦
```
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union, Set
from collections import defaultdict

# 导入基础模块
try:
    from .petersen_scale import PetersenScale, ScaleEntry, cents
except ImportError:
    from petersen_scale import PetersenScale, ScaleEntry, cents

# 常用和弦比率预设
CHORD_RATIOS = {
    "major_triad": [5/4, 3/2],           # 大三和弦：大三度 + 完全五度
    "minor_triad": [6/5, 3/2],           # 小三和弦：小三度 + 完全五度
    "perfect_fourth_fifth": [4/3, 3/2],   # 四五度：完全四度 + 完全五度
    "extended_harmony": [5/4, 3/2, 9/5], # 扩展和声：大三度 + 完全五度 + 大九度
    "just_intonation": [9/8, 5/4, 4/3, 3/2, 5/3, 15/8],  # 纯律音阶比率
    "chinese_pentatonic": [9/8, 5/4, 3/2, 27/16],         # 中国五声音阶近似
    "golden_ratios": [1.618, 1.618**2],  # 基于黄金比例的比率
    "simple_ratios": [3/2, 5/4, 6/5],    # 默认简单比率
}

@dataclass
class ChordTone:
    """和弦音条目"""
    freq: float
    ratio_from_root: float
    ratio_name: str
    root_key: str
    source_type: str  # "existing" 或 "generated"
    petersen_entry: Optional[ScaleEntry] = None
    cents_from_ideal: float = 0.0

@dataclass 
class ExtendedScale:
    """扩展音阶结果"""
    root_notes: List[ScaleEntry]
    original_entries: List[ScaleEntry] 
    chord_tones: List[ChordTone]
    all_entries: List[Union[ScaleEntry, ChordTone]]
    chord_mapping: Dict[str, List[ChordTone]]
    
    def get_frequencies(self) -> List[float]:
        """获取所有频率（排序去重）"""
        freqs = []
        for entry in self.all_entries:
            if isinstance(entry, ScaleEntry):
                freqs.append(entry.freq)
            else:  # ChordTone
                freqs.append(entry.freq)
        return sorted(list(set(freqs)))
    
    def get_statistics(self) -> Dict[str, Union[int, float]]:
        """获取扩展音阶统计信息"""
        return {
            "total_notes": len(self.all_entries),
            "root_notes": len(self.root_notes),
            "original_petersen_notes": len(self.original_entries),
            "generated_chord_tones": len([ct for ct in self.chord_tones if ct.source_type == "generated"]),
            "matched_chord_tones": len([ct for ct in self.chord_tones if ct.source_type == "existing"]),
            "frequency_range_hz": (min(self.get_frequencies()), max(self.get_frequencies())),
            "total_chords": len(self.chord_mapping)
        }

class PetersenChordExtender:
    """
    Petersen音阶和弦扩展器
    
    基于五行"中"极性音符作为根音，使用传统和弦比率扩展出完整的和弦音阶。
    """
    
    def __init__(self,
                 petersen_scale: PetersenScale,
                 chord_ratios: Union[str, List[float]] = "simple_ratios",
                 tolerance_cents: float = 50.0,
                 max_zones: int = 3,
                 min_frequency: float = 30.0,
                 max_frequency: float = 2000.0):
        """
        初始化和弦扩展器
        
        Args:
            petersen_scale: 基础Petersen音阶对象
            chord_ratios: 和弦比率列表或预设名称
            tolerance_cents: 频率匹配容差（音分）
            max_zones: 考虑的最大音区数
            min_frequency: 最小频率限制
            max_frequency: 最大频率限制
        """
        self.petersen_scale = petersen_scale
        self.tolerance_cents = tolerance_cents
        self.max_zones = max_zones
        self.min_frequency = min_frequency
        self.max_frequency = max_frequency
        
        # 处理和弦比率
        if isinstance(chord_ratios, str):
            if chord_ratios in CHORD_RATIOS:
                self.chord_ratios = CHORD_RATIOS[chord_ratios]
            else:
                raise ValueError(f"未知的和弦比率预设: {chord_ratios}")
        else:
            self.chord_ratios = chord_ratios
        
        # 缓存生成的音阶
        self._original_entries = None
        self._root_notes = None
    
    def _get_original_entries(self) -> List[ScaleEntry]:
        """获取原始Petersen音阶条目（缓存）"""
        if self._original_entries is None:
            self._original_entries = self.petersen_scale.generate_raw()
        return self._original_entries
    
    def extract_root_notes(self) -> List[ScaleEntry]:
        """
        提取根音：五行"中"极性的最低3个音区
        
        Returns:
            15个根音条目列表（5个五行 × 3个音区）
        """
        if self._root_notes is not None:
            return self._root_notes
        
        entries = self._get_original_entries()
        
        # 筛选"中"极性音符（p=0）
        neutral_entries = [entry for entry in entries if entry.p == 0]
        
        # 按音区分组
        zone_groups = defaultdict(list)
        for entry in neutral_entries:
            zone_groups[entry.n].append(entry)
        
        # 选择最低的3个音区
        sorted_zones = sorted(zone_groups.keys())
        selected_zones = sorted_zones[:self.max_zones]
        
        root_notes = []
        for zone in selected_zones:
            # 每个音区内按五行顺序排序（e: 0=金, 1=木, 2=水, 3=火, 4=土）
            zone_entries = sorted(zone_groups[zone], key=lambda x: x.e)
            root_notes.extend(zone_entries)
        
        self._root_notes = root_notes
        return root_notes
    
    def generate_chord_tones(self, root_freq: float, ratios: List[float]) -> List[Tuple[float, float, str]]:
        """
        基于根音频率和比率生成和弦音频率
        
        Args:
            root_freq: 根音频率
            ratios: 和弦比率列表
        
        Returns:
            (和弦音频率, 比率, 比率描述) 的列表
        """
        chord_freqs = []
        
        for ratio in ratios:
            chord_freq = root_freq * ratio
            
            # 频率范围检查
            if self.min_frequency <= chord_freq <= self.max_frequency:
                # 生成比率描述
                ratio_name = self._ratio_to_name(ratio)
                chord_freqs.append((chord_freq, ratio, ratio_name))
        
        return chord_freqs
    
    def _ratio_to_name(self, ratio: float) -> str:
        """将数值比率转换为音程名称"""
        ratio_names = {
            1.0: "同度",
            9/8: "大二度", 
            10/9: "小二度",
            5/4: "大三度",
            6/5: "小三度", 
            4/3: "完全四度",
            7/5: "增四度",
            3/2: "完全五度",
            8/5: "小六度",
            5/3: "大六度",
            9/5: "小七度", 
            15/8: "大七度",
            2.0: "八度",
            9/4: "大九度",
            5/2: "大十度"
        }
        
        # 查找最接近的已知比率
        for known_ratio, name in ratio_names.items():
            if abs(ratio - known_ratio) < 0.01:
                return name
        
        return f"比率{ratio:.3f}"
    
    def find_matching_note(self, target_freq: float) -> Optional[ScaleEntry]:
        """
        在现有音阶中查找匹配的音符
        
        Args:
            target_freq: 目标频率
        
        Returns:
            匹配的音阶条目，如果没有找到则返回None
        """
        entries = self._get_original_entries()
        
        for entry in entries:
            cents_diff = abs(cents(target_freq, entry.freq))
            if cents_diff <= self.tolerance_cents:
                return entry
        
        return None
    
    def extend_scale_with_chords(self) -> ExtendedScale:
        """
        生成扩展音阶（原音阶 + 和弦音）
        
        Returns:
            扩展音阶对象
        """
        root_notes = self.extract_root_notes()
        original_entries = self._get_original_entries()
        chord_tones = []
        chord_mapping = {}
        
        for root in root_notes:
            root_key = root.key_short
            root_chord_tones = []
            
            # 为每个根音生成和弦音
            chord_freqs = self.generate_chord_tones(root.freq, self.chord_ratios)
            
            for chord_freq, ratio, ratio_name in chord_freqs:
                # 尝试在现有音阶中匹配
                matching_entry = self.find_matching_note(chord_freq)
                
                if matching_entry:
                    # 使用现有音符
                    chord_tone = ChordTone(
                        freq=matching_entry.freq,
                        ratio_from_root=ratio,
                        ratio_name=ratio_name,
                        root_key=root_key,
                        source_type="existing",
                        petersen_entry=matching_entry,
                        cents_from_ideal=cents(matching_entry.freq, chord_freq)
                    )
                else:
                    # 创建新的和弦音
                    chord_tone = ChordTone(
                        freq=chord_freq,
                        ratio_from_root=ratio,
                        ratio_name=ratio_name,
                        root_key=root_key,
                        source_type="generated",
                        petersen_entry=None,
                        cents_from_ideal=0.0
                    )
                
                chord_tones.append(chord_tone)
                root_chord_tones.append(chord_tone)
            
            chord_mapping[root_key] = root_chord_tones
        
        # 合并所有条目
        all_entries = original_entries.copy()
        all_entries.extend(chord_tones)
        
        return ExtendedScale(
            root_notes=root_notes,
            original_entries=original_entries,
            chord_tones=chord_tones,
            all_entries=all_entries,
            chord_mapping=chord_mapping
        )
    
    def get_chord_for_root(self, root_key: str) -> List[ChordTone]:
        """
        获取特定根音的和弦音列表
        
        Args:
            root_key: 根音短名（如"J0"）
        
        Returns:
            和弦音列表
        """
        extended_scale = self.extend_scale_with_chords()
        return extended_scale.chord_mapping.get(root_key, [])
    
    def analyze_chord_coverage(self) -> Dict[str, Union[int, float, List]]:
        """
        分析和弦覆盖情况
        
        Returns:
            和弦覆盖分析结果
        """
        extended_scale = self.extend_scale_with_chords()
        
        total_chord_tones = len(extended_scale.chord_tones)
        existing_matches = len([ct for ct in extended_scale.chord_tones if ct.source_type == "existing"])
        generated_new = len([ct for ct in extended_scale.chord_tones if ct.source_type == "generated"])
        
        # 计算匹配率
        match_rate = existing_matches / total_chord_tones if total_chord_tones > 0 else 0
        
        # 分析音程分布
        interval_distribution = defaultdict(int)
        for chord_tone in extended_scale.chord_tones:
            interval_distribution[chord_tone.ratio_name] += 1
        
        return {
            "total_chord_tones": total_chord_tones,
            "existing_matches": existing_matches,
            "generated_new": generated_new,
            "match_rate": match_rate,
            "interval_distribution": dict(interval_distribution),
            "average_cents_deviation": sum(abs(ct.cents_from_ideal) for ct in extended_scale.chord_tones) / total_chord_tones if total_chord_tones > 0 else 0
        }
    
    def export_extended_scale_csv(self, path: Union[str, Path] = None) -> None:
        """
        导出扩展音阶到CSV文件
        
        Args:
            path: 输出路径，如果为None则自动生成
        """
        extended_scale = self.extend_scale_with_chords()
        
        if path is None:
            base_name = self.petersen_scale._generate_filename_base()
            ratios_str = "_".join([f"{r:.3f}".replace(".", "p") for r in self.chord_ratios])
            path = f"../data/petersen_extended_scale_{base_name}_ratios_{ratios_str}.csv"
        
        path = Path(path)
        
        with open(path, 'w', encoding='utf-8') as f:
            # CSV头部
            f.write("类型,频率,键名短,键名长,音区,五行,极性,根音键名,比率,音程名,音分偏差,来源\n")
            
            # 根音
            for root in extended_scale.root_notes:
                f.write(f"根音,{root.freq:.6f},{root.key_short},{root.key_long},{root.n},{root.e},{root.p},,,,0.0,Petersen原音阶\n")
            
            # 和弦音
            for chord_tone in extended_scale.chord_tones:
                f.write(f"和弦音,{chord_tone.freq:.6f},,,,,,"
                       f"{chord_tone.root_key},{chord_tone.ratio_from_root:.6f},"
                       f"{chord_tone.ratio_name},{chord_tone.cents_from_ideal:.2f},"
                       f"{chord_tone.source_type}\n")
        
        print(f"扩展音阶已导出到: {path}")
    
    def export_chord_mapping_csv(self, path: Union[str, Path] = None) -> None:
        """
        导出和弦映射关系到CSV文件
        
        Args:
            path: 输出路径，如果为None则自动生成
        """
        extended_scale = self.extend_scale_with_chords()
        
        if path is None:
            base_name = self.petersen_scale._generate_filename_base()
            ratios_str = "_".join([f"{r:.3f}".replace(".", "p") for r in self.chord_ratios])
            path = f"../data/petersen_chord_mapping_{base_name}_ratios_{ratios_str}.csv"
        
        path = Path(path)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write("根音键名,根音频率,和弦音频率,比率,音程名,音分偏差,来源\n")
            
            for root_key, chord_tones in extended_scale.chord_mapping.items():
                root_note = next(r for r in extended_scale.root_notes if r.key_short == root_key)
                
                for chord_tone in chord_tones:
                    f.write(f"{root_key},{root_note.freq:.6f},"
                           f"{chord_tone.freq:.6f},{chord_tone.ratio_from_root:.6f},"
                           f"{chord_tone.ratio_name},{chord_tone.cents_from_ideal:.2f},"
                           f"{chord_tone.source_type}\n")
        
        print(f"和弦映射已导出到: {path}")

def compare_chord_ratio_presets(petersen_scale: PetersenScale) -> None:
    """
    比较不同和弦比率预设的效果
    
    Args:
        petersen_scale: 基础Petersen音阶
    """
    print("=== 和弦比率预设比较分析 ===\n")
    
    for preset_name, ratios in CHORD_RATIOS.items():
        print(f"【{preset_name}】比率: {ratios}")
        
        extender = PetersenChordExtender(
            petersen_scale=petersen_scale,
            chord_ratios=ratios,
            tolerance_cents=50
        )
        
        analysis = extender.analyze_chord_coverage()
        
        print(f"  总和弦音: {analysis['total_chord_tones']}")
        print(f"  匹配现有音阶: {analysis['existing_matches']}")
        print(f"  新生成: {analysis['generated_new']}")
        print(f"  匹配率: {analysis['match_rate']:.1%}")
        print(f"  平均音分偏差: {analysis['average_cents_deviation']:.1f}")
        print(f"  音程分布: {analysis['interval_distribution']}")
        print()

if __name__ == "__main__":
    # 示例用法
    from petersen_scale import PetersenScale, PHI
    
    # 创建基础音阶（八度关系，兼容性更好）
    base_scale = PetersenScale(F_base=55.0, phi=2.0, delta_theta=4.8)
    
    # 创建和弦扩展器
    extender = PetersenChordExtender(
        petersen_scale=base_scale,
        chord_ratios="simple_ratios",  # 使用简单比率预设
        tolerance_cents=50
    )
    
    # 提取根音
    root_notes = extender.extract_root_notes()
    print(f"提取到 {len(root_notes)} 个根音:")
    for root in root_notes:
        print(f"  {root.key_short} ({root.key_long}): {root.freq:.2f} Hz")
    
    # 生成扩展音阶
    extended_scale = extender.extend_scale_with_chords()
    stats = extended_scale.get_statistics()
    
    print(f"\n扩展音阶统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 分析和弦覆盖
    analysis = extender.analyze_chord_coverage()
    print(f"\n和弦覆盖分析:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    
    # 导出文件
    extender.export_extended_scale_csv()
    extender.export_chord_mapping_csv()
    
    # 比较不同预设
    print("\n" + "="*50)
    compare_chord_ratio_presets(base_scale)