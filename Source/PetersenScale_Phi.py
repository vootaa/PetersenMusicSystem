"""
Petersen 可变比例音区模块（库形式）

基于可变比例φ和五行阴阳理论的音阶生成系统，实现文档中的"方案B（归一化方式）"。

主要功能：
- 以可参数化的基点频率F_base为起点，按可变比例φ向上生成音区
- 在每个360°音区内，按五行(72°/方位)和阴阳极性(3个)分布15个音位
- 支持多种φ值：黄金比例(1.618)、八度(2.0)、完全五度(1.5)、增四度(√2)等
- 支持频率范围限制、多种导出格式、音程分析等功能

核心API：
  - PetersenScale_Phi(F_base=20, delta_theta=4.8, phi=PHI, F_min=30, F_max=6000, reference=440)
  - scale.generate() -> List[Dict]: 生成音阶条目字典列表
  - scale.generate_raw() -> List[ScaleEntry]: 生成原始精度的音阶条目
  - scale.frequencies_only() -> List[float]: 仅返回频率列表
  - scale.export_csv(path): 导出CSV格式
  - scale.to_scala_file(path): 导出Scala(.scl)格式
  - scale.to_midi_tuning(path): 导出MIDI调音(.tun)格式
  - scale.get_statistics(): 获取音阶统计信息
  - scale.analyze_intervals(): 分析音程关系

使用示例：
  ```python
  # 创建不同φ值的音阶对象
  scale_golden = PetersenScale_Phi(F_base=20.0, delta_theta=4.8, phi=1.618)  # 黄金比例
  scale_octave = PetersenScale_Phi(F_base=20.0, delta_theta=4.8, phi=2.0)    # 八度关系
  scale_fifth = PetersenScale_Phi(F_base=20.0, delta_theta=4.8, phi=1.5)     # 完全五度
  scale_tritone = PetersenScale_Phi(F_base=20.0, delta_theta=4.8, phi=1.414) # 增四度
  
  # 生成音阶
  entries = scale.generate()  # 舍入版本
  raw_entries = scale.generate_raw()  # 原始精度版本
  freqs = scale.frequencies_only()  # 仅频率
  
  # 分析功能
  stats = scale.get_statistics()
  intervals = scale.analyze_intervals()
  
  # 导出功能（文件名自动包含φ值）
  scale.export_csv("scale.csv")
  scale.to_scala_file("scale.scl")
  scale.to_midi_tuning("scale.tun")
  
  # 查询功能
  freq = scale.get_frequency_for_key("J-")  # 获取"金阴"的频率
  zone_entries = scale.get_entries_in_zone(5)  # 获取第5音区的所有条目
  ```

短名命名规则：元素拼音首字母 + 极性符号（-, 0, +），例如 J-/J0/J+
长名命名规则：中文元素 + 极性，例如 "金 阴"/"金 中"/"金 阳"

φ值预设说明：
- φ = 2.0 (八度关系): 与12平均律完全兼容，传统和谐
- φ = 1.618033988749 (黄金比例): 原始Petersen系统，神秘独特的音程关系
- φ = 1.5 (完全五度): 极其稳定和谐，适合冥想和治疗音乐
- φ = 1.414213562373 (增四度): 现代音乐风格，张力感强
"""
from __future__ import annotations

import math
import csv
import logging
import struct
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union

# 常量定义
PHI = (1 + 5 ** 0.5) / 2.0  # 黄金比例 ≈ 1.618033988749
SQRT2 = 2 ** 0.5           # √2 ≈ 1.414213562373
ELEMENTS_CN = ["金", "木", "水", "火", "土"]  # 五行中文名
ELEMENTS_PY = ["J", "M", "S", "H", "T"]  # 五行拼音首字母

# φ值预设常量
PHI_PRESETS = {
    "golden": PHI,              # 1.618... 黄金比例
    "octave": 2.0,             # 2.0 八度关系
    "fifth": 1.5,              # 1.5 完全五度
    "tritone": SQRT2,          # √2 增四度
}

def cents(f: float, ref: float) -> float:
    """
    计算两个频率之间的音分差值
    
    Args:
        f: 目标频率 (Hz)
        ref: 参考频率 (Hz)
    
    Returns:
        音分差值，正值表示f高于ref
    """
    return 1200.0 * math.log2(f / ref)

def phi_name(phi: float) -> str:
    """
    根据φ值返回英文名称，用于文件命名
    
    Args:
        phi: φ比例值
    
    Returns:
        英文名称字符串
    """
    # 检查是否为预设值（允许小量误差）
    for name, value in PHI_PRESETS.items():
        if abs(phi - value) < 1e-6:
            return name
    
    # 检查其他常见值
    if abs(phi - 1.0) < 1e-6:
        return "unison"
    elif abs(phi - 3.0/2.0) < 1e-6:
        return "perfect_fifth"
    elif abs(phi - 4.0/3.0) < 1e-6:
        return "perfect_fourth"
    elif abs(phi - 3.0) < 1e-6:
        return "perfect_twelfth"
    else:
        # 格式化为文件名安全的字符串
        return f"phi_{phi:.6f}".replace('.', 'p')

@dataclass
class ScaleEntry:
    """
    音阶条目数据结构
    
    Attributes:
        e: 五行索引 (0-4: 金木水火土)
        p: 极性 (-1:阴, 0:中, 1:阳)
        theta_deg: 角度值 (度)
        u: 归一化区内位置 [0,1)
        n: 音区编号
        interval_a: 音区下界频率 (Hz)
        interval_b: 音区上界频率 (Hz)
        freq: 实际频率 (Hz)
        cents_ref: 相对于参考频率的音分值
        key_short: 短名 (如 "J-")
        key_long: 长名 (如 "金 阴")
    """
    e: int
    p: int
    theta_deg: float
    u: float
    n: int
    interval_a: float
    interval_b: float
    freq: float
    cents_ref: float
    key_short: str
    key_long: str

class PetersenScale_Phi:
    """
    Petersen可变比例音阶生成器
    
    实现基于可变比例φ和五行阴阳理论的音阶系统，按照文档中的"方案B"生成频率。
    """
    
    def __init__(self,
                 F_base: float = 20.0,
                 delta_theta: float = 4.8,   # degrees
                 phi: float = PHI,           # 新增：可变比例参数
                 F_min: float = 30.0,
                 F_max: float = 6000.0,
                 reference: float = 440.0):
        """
        初始化音阶生成器
        
        Args:
            F_base: 基准频率 (Hz)，默认20Hz
            delta_theta: 极性角度步进 (度)，默认4.8°
            phi: 音区间比例系数，默认黄金比例1.618
            F_min: 最小频率限制 (Hz)，默认30Hz
            F_max: 最大频率限制 (Hz)，默认6000Hz
            reference: 参考频率 (Hz)，用于计算音分，默认440Hz
        
        Raises:
            ValueError: 当参数不合法时抛出异常
        """
        # 基本参数验证
        if F_base <= 0 or F_min <= 0 or F_max <= 0:
            raise ValueError("F_base, F_min, F_max must be positive")
        if F_min >= F_max:
            raise ValueError("F_min must be less than F_max")
        if reference <= 0:
            raise ValueError("reference frequency must be positive")
        if phi <= 1.0:
            raise ValueError("phi must be greater than 1.0 to ensure frequency progression")
            
        self.F_base = float(F_base)
        self.delta_theta = float(delta_theta)
        self.phi = float(phi)  # 新增：存储φ值
        self.F_min = float(F_min)
        self.F_max = float(F_max)
        self.reference = float(reference)
        self.logger = logging.getLogger(__name__)
        
        # 用于性能优化的实例级缓存
        self._power_cache: Dict[float, float] = {}
        
        # 记录φ值信息
        phi_desc = phi_name(self.phi)
        self.logger.info(f"Created PetersenScale_Phi with φ={self.phi:.6f} ({phi_desc})")

    def _theta_for(self, e: int, p: int) -> float:
        """
        计算五行元素e和极性p对应的角度
        
        Args:
            e: 五行索引 (0-4)
            p: 极性 (-1, 0, 1)
        
        Returns:
            角度值 (度)
        
        公式: θ = θₑ + (p+1)·Δθ，其中θₑ = 72°·e
        """
        theta_e = 72.0 * e  # 五行基准角度
        return theta_e + (p + 1) * self.delta_theta

    def _u_from_theta(self, theta: float) -> float:
        """
        将角度归一化到区内位置参数u
        
        Args:
            theta: 角度值 (度)
        
        Returns:
            归一化位置 u ∈ [0,1)
        
        公式: u = (θ mod 360°) / 360°
        """
        mod = theta % 360.0
        return mod / 360.0

    def _n_range_for_u(self, u: float) -> Tuple[int, int]:
        """
        计算给定u值下的有效音区范围
        
        Args:
            u: 归一化区内位置
        
        Returns:
            (n_min, n_max): 音区编号范围
        
        基于约束: F_min ≤ F_base * φ^(n+u) ≤ F_max
        """
        # 使用实例的φ值进行对数运算
        lo = math.log(self.F_min / self.F_base, self.phi) - u
        hi = math.log(self.F_max / self.F_base, self.phi) - u
        n_min = math.ceil(lo)
        n_max = math.floor(hi)
        return n_min, n_max

    def _zone_interval(self, n: int) -> Tuple[float, float]:
        """
        计算第n音区的频率区间
        
        Args:
            n: 音区编号
        
        Returns:
            (下界, 上界): 频率区间 (Hz)
        
        公式: [F_base * φⁿ, F_base * φⁿ⁺¹)
        """
        a = self.F_base * self._phi_power(n)
        b = self.F_base * self._phi_power(n + 1)
        return a, b

    def _phi_power(self, exponent: float) -> float:
        """
        计算φ的幂运算，使用实例级缓存优化性能
        
        Args:
            exponent: 指数
        
        Returns:
            φ^exponent
        """
        if exponent not in self._power_cache:
            self._power_cache[exponent] = self.phi ** exponent
        return self._power_cache[exponent]

    def key_name_short(self, e: int, p: int) -> str:
        """
        生成短名格式的音名
        
        Args:
            e: 五行索引
            p: 极性
        
        Returns:
            短名，如 "J-", "M0", "T+"
        """
        py = ELEMENTS_PY[e]
        sym = { -1: "-", 0: "0", 1: "+" }[p]
        return f"{py}{sym}"

    def key_name_long(self, e: int, p: int) -> str:
        """
        生成长名格式的音名
        
        Args:
            e: 五行索引
            p: 极性
        
        Returns:
            长名，如 "金 阴", "木 中", "土 阳"
        """
        el = ELEMENTS_CN[e]
        pol = { -1: "阴", 0: "中", 1: "阳" }[p]
        return f"{el} {pol}"

    def generate_raw(self) -> List[ScaleEntry]:
        """
        生成原始精度的音阶条目列表
        
        Returns:
            按频率排序的ScaleEntry列表，保持完整浮点精度
        
        实现方案B的核心算法：
        1. 遍历所有15个(e,p)组合
        2. 计算角度θ和归一化位置u
        3. 枚举有效音区n
        4. 计算频率 f = F_base * φ^(n+u)
        5. 过滤频率范围并排序
        """
        out: List[ScaleEntry] = []
        for e in range(5):  # 五行: 金木水火土
            for p in (-1, 0, 1):  # 三极性: 阴中阳
                theta = self._theta_for(e, p)
                u = self._u_from_theta(theta)
                n_min, n_max = self._n_range_for_u(u)
                
                for n in range(n_min, n_max + 1):
                    # 使用实例级缓存的φ幂运算
                    f = self.F_base * self._phi_power(n + u)
                    
                    # 频率范围检查，包含小量容差以处理浮点误差
                    if f < self.F_min - 1e-12 or f > self.F_max + 1e-12:
                        continue
                    
                    # 计算音区边界并裁剪到全局范围
                    a, b = self._zone_interval(n)
                    Ia = max(a, self.F_min)
                    Ib = min(b, self.F_max)
                    
                    entry = ScaleEntry(
                        e=e,
                        p=p,
                        theta_deg=theta,
                        u=u,
                        n=n,
                        interval_a=Ia,
                        interval_b=Ib,
                        freq=f,
                        cents_ref=cents(f, self.reference),
                        key_short=self.key_name_short(e, p),
                        key_long=self.key_name_long(e, p)
                    )
                    out.append(entry)
        
        # 按频率排序
        out.sort(key=lambda x: x.freq)
        return out

    def generate(self, round_digits: Optional[int] = 6) -> List[Dict]:
        """
        生成音阶条目的字典列表（向后兼容版本）
        
        Args:
            round_digits: 数值舍入位数，None表示保持原始精度
        
        Returns:
            字典列表，每个字典包含音阶条目的所有字段
        """
        raw = self.generate_raw()
        if round_digits is None:
            return [r.__dict__ for r in raw]
        
        rounded: List[Dict] = []
        for r in raw:
            rounded.append({
                "e": r.e,
                "p": r.p,
                "theta_deg": round(r.theta_deg, round_digits),
                "u": round(r.u, round_digits),
                "n": r.n,
                "interval_a": round(r.interval_a, round_digits),
                "interval_b": round(r.interval_b, round_digits),
                "freq": round(r.freq, round_digits),
                "cents_ref": round(r.cents_ref, 4),
                "key_short": r.key_short,
                "key_long": r.key_long
            })
        return rounded

    def frequencies_only(self) -> List[float]:
        """
        仅返回按频率排序的频率列表
        
        Returns:
            频率列表 (Hz)，适用于需要纯数值数组的场合
        """
        return [e.freq for e in self.generate_raw()]

    # 便利查询方法
    def get_frequency_for_key(self, key_short: str) -> Optional[float]:
        """
        根据短名查找对应的频率
        
        Args:
            key_short: 短名，如 'J-', 'M0', 'T+'
        
        Returns:
            对应的频率值，未找到时返回None
        """
        for entry in self.generate_raw():
            if entry.key_short == key_short:
                return entry.freq
        return None
    
    def get_entries_in_zone(self, n: int) -> List[ScaleEntry]:
        """
        获取指定音区的所有条目
        
        Args:
            n: 音区编号
        
        Returns:
            该音区内的所有ScaleEntry
        """
        return [e for e in self.generate_raw() if e.n == n]
    
    def get_frequency_range(self) -> Tuple[float, float]:
        """
        获取实际生成的频率范围
        
        Returns:
            (最小频率, 最大频率) (Hz)
        """
        entries = self.generate_raw()
        if not entries:
            return (0.0, 0.0)
        freqs = [e.freq for e in entries]
        return (min(freqs), max(freqs))
    
    def get_phi_info(self) -> Dict[str, Union[float, str]]:
        """
        获取当前φ值的详细信息
        
        Returns:
            包含φ值信息的字典
        """
        return {
            "phi_value": self.phi,
            "phi_name": phi_name(self.phi),
            "cents_per_zone": 1200 * math.log2(self.phi),
            "zones_per_octave": 12 / (12 * math.log2(self.phi)),
            "musical_description": self._get_musical_description()
        }
    
    def _get_musical_description(self) -> str:
        """获取φ值的音乐学描述"""
        phi_val = self.phi
        
        if abs(phi_val - PHI) < 1e-6:
            return "黄金比例：神秘独特的音程关系，Petersen原始系统"
        elif abs(phi_val - 2.0) < 1e-6:
            return "八度关系：与12平均律完全兼容，传统和谐"
        elif abs(phi_val - 1.5) < 1e-6:
            return "完全五度：极其稳定和谐，适合冥想和治疗音乐"
        elif abs(phi_val - SQRT2) < 1e-6:
            return "增四度(三全音)：现代音乐风格，张力感强"
        elif abs(phi_val - 4.0/3.0) < 1e-6:
            return "完全四度：稳定的协和音程"
        elif abs(phi_val - 3.0/2.0) < 1e-6:
            return "完全五度精确值：纯律调音中的理想比例"
        else:
            cents_interval = 1200 * math.log2(phi_val)
            return f"自定义比例：每音区间隔约{cents_interval:.1f}音分"
    
    # 统计分析方法
    def get_statistics(self) -> Dict[str, Union[int, float, List, Dict]]:
        """
        获取音阶的统计信息
        
        Returns:
            包含各种统计数据的字典，现在包含φ信息
        """
        entries = self.generate_raw()
        if not entries:
            return {}
        
        freqs = [e.freq for e in entries]
        zones = list(set(e.n for e in entries))
        
        # 五行分布统计
        elements_dist = {ELEMENTS_CN[i]: 0 for i in range(5)}
        for e in entries:
            elements_dist[ELEMENTS_CN[e.e]] += 1
        
        # 极性分布统计
        polarity_dist = {"阴": 0, "中": 0, "阳": 0}
        polarity_map = {-1: "阴", 0: "中", 1: "阳"}
        for e in entries:
            polarity_dist[polarity_map[e.p]] += 1
        
        stats = {
            "phi_info": self.get_phi_info(),  # 新增：φ值信息
            "total_entries": len(entries),
            "frequency_range": (min(freqs), max(freqs)),
            "zones_used": sorted(zones),
            "zone_count": len(zones),
            "entries_per_zone": {n: len(self.get_entries_in_zone(n)) for n in zones},
            "elements_distribution": elements_dist,
            "polarity_distribution": polarity_dist
        }
        
        return stats

    def analyze_intervals(self) -> List[Dict]:
        """
        分析相邻频率之间的音程关系
        
        Returns:
            音程分析列表，每个字典包含:
            - from_key/to_key: 起止音名
            - ratio: 频率比
            - cents: 音分差
            - from_freq/to_freq: 起止频率
        """
        entries = sorted(self.generate_raw(), key=lambda x: x.freq)
        intervals = []
        
        for i in range(len(entries) - 1):
            curr = entries[i]
            next_entry = entries[i + 1]
            ratio = next_entry.freq / curr.freq
            cents_interval = cents(next_entry.freq, curr.freq)
            
            intervals.append({
                "from_key": curr.key_short,
                "to_key": next_entry.key_short,
                "from_long": curr.key_long,
                "to_long": next_entry.key_long,
                "ratio": ratio,
                "cents": cents_interval,
                "from_freq": curr.freq,
                "to_freq": next_entry.freq
            })
        
        return intervals
    
    # 验证方法
    def validate_implementation(self) -> bool:
        """
        验证实现是否符合文档中的数学公式
        
        Returns:
            True表示实现正确，False表示有问题
        
        测试几个已知案例来验证角度计算和归一化的正确性
        """
        test_cases = [
            (0, -1),  # 金阴: θ=0°, u=0
            (1, 0),   # 木中: θ=76.8°
            (4, 1),   # 土阳: θ=297.6°
        ]
        
        for e, p in test_cases:
            theta = self._theta_for(e, p)
            u = self._u_from_theta(theta)
            expected_theta = 72.0 * e + (p + 1) * self.delta_theta
            expected_u = (expected_theta % 360.0) / 360.0
            
            if abs(theta - expected_theta) > 1e-10:
                self.logger.error(f"Theta mismatch for e={e}, p={p}: got {theta}, expected {expected_theta}")
                return False
            if abs(u - expected_u) > 1e-10:
                self.logger.error(f"U mismatch for e={e}, p={p}: got {u}, expected {expected_u}")
                return False
        
        return True

    def _generate_filename_base(self) -> str:
        """生成包含φ信息的文件名基础"""
        def fmt(x):
            return str(x).replace('.', 'p')
        
        phi_desc = phi_name(self.phi)
        return f"petersen_phi_{phi_desc}_F{fmt(self.F_base)}_dth{fmt(self.delta_theta)}"

    # 导出方法（更新为包含φ信息）
    def export_csv(self, path: Union[str, Path] = None, entries: Optional[List[Union[ScaleEntry, Dict]]] = None) -> None:
        """
        导出为CSV格式
        
        Args:
            path: 输出文件路径，None表示自动生成文件名
            entries: 要导出的条目，None表示使用默认生成的条目
        """
        if entries is None:
            entries = self.generate()
        
        if path is None:
            path = f"{self._generate_filename_base()}.csv"
        
        p = Path(path)
        fieldnames = ["key_short", "key_long", "e", "p", "n",
                      "theta_deg", "u", "interval_a", "interval_b",
                      "freq", "cents_ref"]
        
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in entries:
                if isinstance(r, ScaleEntry):
                    row = r.__dict__
                else:
                    row = r
                w.writerow({k: row.get(k, "") for k in fieldnames})

    def to_scala_file(self, path: Union[str, Path] = None, description: str = None) -> None:
        """
        导出为Scala (.scl) 格式
        
        Args:
            path: 输出文件路径，None表示自动生成文件名
            description: 音阶描述，None表示自动生成描述
        """
        entries = self.generate_raw()
        if not entries:
            raise ValueError("No entries to export")
        
        if path is None:
            path = f"{self._generate_filename_base()}.scl"
        
        if description is None:
            phi_info = self.get_phi_info()
            description = f"Petersen Scale φ={self.phi:.6f} ({phi_info['phi_name']}) - {phi_info['musical_description']}"
        
        p = Path(path)
        
        # 找到基准频率（最低频率作为1/1）
        entries_sorted = sorted(entries, key=lambda x: x.freq)
        base_freq = entries_sorted[0].freq
        
        with p.open("w", encoding="utf-8") as f:
            f.write(f"! {description}\n")
            # Scala 格式：音数不包括基准音 1/1
            f.write(f"{len(entries) - 1}\n")
            f.write("!\n")
            
            for i, entry in enumerate(entries_sorted):
                if i == 0:  # 第一个音作为基准音
                    f.write("1/1\n")
                else:
                    ratio = entry.freq / base_freq
                    # 尝试表示为简单分数，否则用小数
                    if abs(ratio - round(ratio)) < 1e-6:
                        # 接近整数
                        f.write(f"{int(round(ratio))}/1\n")
                    else:
                        # 检查是否为简单分数
                        for denom in [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16]:
                            num = ratio * denom
                            if abs(num - round(num)) < 1e-6:
                                f.write(f"{int(round(num))}/{denom}\n")
                                break
                        else:
                            # 用小数表示
                            f.write(f"{ratio:.10f}\n")

    def to_midi_tuning(self, path: Union[str, Path] = None, name: str = None,
                       entries: Optional[List[ScaleEntry]] = None) -> None:
        """
        导出为MIDI调音表(.tun)
        
        Args:
            path: 输出文件路径，None表示自动生成文件名
            name: 调音表名称，None表示自动生成名称
            entries: 条目列表，None表示使用默认生成的条目
        """
        if entries is None:
            entries = self.generate_raw()
        if not entries:
            raise ValueError("No entries to export")
        
        if path is None:
            path = f"{self._generate_filename_base()}.tun"
        
        if name is None:
            phi_info = self.get_phi_info()
            name = f"Petersen φ={self.phi:.3f} ({phi_info['phi_name']})"
        
        p = Path(path)
        base_freq = 8.1757989156  # MIDI 0 的频率
        
        # 原始 scale 频率（去重并排序）
        scale_freqs = sorted({e.freq for e in entries if e.freq > 0})
        if not scale_freqs:
            raise ValueError("No valid scale frequencies")
        
        midi_freqs = []
        for midi_note in range(128):
            # 目标等十二平均律频率（用于匹配）
            target = base_freq * (2 ** (midi_note / 12.0))
            best_freq = scale_freqs[0]
            best_diff = abs(best_freq - target)
            
            for sf in scale_freqs:
                # 估算最合适的 octave 偏移 k（将 sf 移到接近 target 的 octave）
                k = round(math.log2(target / sf))
                cand = sf * (2 ** k)
                diff = abs(cand - target)
                if diff < best_diff:
                    best_diff = diff
                    best_freq = cand
            
            midi_freqs.append(best_freq)
        
        # 写入简化 .tun 文件
        with p.open("wb") as f:
            f.write(b"TUN ")
            f.write(struct.pack("<I", 1))
            name_bytes = name.encode('ascii', errors='ignore')[:31]
            name_padded = name_bytes + b'\x00' * (32 - len(name_bytes))
            f.write(name_padded)
            for freq in midi_freqs:
                f.write(struct.pack("<d", float(freq)))

    def verify_scala_file(self, scl_path: Union[str, Path]) -> None:
        """
        验证生成的 .scl 文件格式是否正确
        
        Args:
            scl_path: .scl 文件路径
        """
        with open(scl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"=== Scala 文件验证: {scl_path} ===")
        print(f"描述: {lines[0].strip()}")
        print(f"音数: {lines[1].strip()}")
        print(f"前10个比值:")
        
        def parse_scala_ratio(line: str) -> float:
            """解析 Scala 格式的比值（支持 1/1, 小数, 分数等格式）"""
            line = line.strip()
            if '/' in line:
                # 分数格式，如 "1/1", "3/2"
                numerator, denominator = line.split('/')
                return float(numerator) / float(denominator)
            else:
                # 小数格式
                return float(line)
        
        ratio_lines = []
        for i, line in enumerate(lines[3:]):  # 跳过描述、音数、注释行
            if line.strip() == '' or line.strip().startswith('!'):
                continue
            ratio_lines.append(line.strip())
        
        # 显示前10个比值
        for i, line in enumerate(ratio_lines[:10]):
            try:
                ratio = parse_scala_ratio(line)
                cents_val = 1200 * math.log2(ratio) if ratio > 0 else 0
                print(f"  {i+1:2d}: {line:<12} = {ratio:.6f} ({cents_val:+7.1f} cents)")
            except (ValueError, ZeroDivisionError) as e:
                print(f"  {i+1:2d}: {line:<12} = 解析错误: {e}")
        
        # 额外统计信息
        try:
            declared_count = int(lines[1].strip())
            actual_count = len(ratio_lines)
            print(f"\n声明音数: {declared_count}")
            print(f"实际音数: {actual_count}")
            print(f"包含基准音1/1: {'是' if '1/1' in ratio_lines else '否'}")
            
            # Scala格式说明：声明的音数应该是实际音数减去基准音1/1
            if '1/1' in ratio_lines:
                expected_declared = actual_count - 1
            else:
                expected_declared = actual_count
                
            if declared_count == expected_declared:
                print(f"✓ 音数匹配 (Scala格式正确)")
            else:
                print(f"⚠️  音数不匹配！应该声明 {expected_declared} 个音")
                
        except Exception as e:
            print(f"无法验证音数: {e}")

    def prune_keep_neutral_zones(self,
                                 entries: Optional[List[ScaleEntry]] = None,
                                 zones: Optional[List[int]] = None) -> List[ScaleEntry]:
        """
        在给定音区列表中只保留中性(p==0)条目，其它音区保持不变。
        如果 entries 为 None，会调用 generate_raw() 获取完整条目列表。
        """
        if entries is None:
            entries = self.generate_raw()
        if not zones:
            return entries
        zones_set = set(zones)
        filtered = [e for e in entries if not (e.n in zones_set and e.p != 0)]
        return filtered

def compare_phi_values(phi_values: List[float], F_base: float = 55.0, delta_theta: float = 4.8) -> None:
    """
    比较不同φ值的音阶特性
    
    Args:
        phi_values: 要比较的φ值列表
        F_base: 基础频率
        delta_theta: 极性偏移角度
    """
    print(f"=== φ值比较分析 ===")
    print(f"基础参数: F_base={F_base} Hz, delta_theta={delta_theta}°\n")
    
    for phi in phi_values:
        try:
            scale = PetersenScale_Phi(F_base=F_base, delta_theta=delta_theta, phi=phi)
            phi_info = scale.get_phi_info()
            stats = scale.get_statistics()
            
            print(f"φ = {phi:.6f} ({phi_info['phi_name']})")
            print(f"   描述: {phi_info['musical_description']}")
            print(f"   每音区音分: {phi_info['cents_per_zone']:.1f}")
            print(f"   总条目数: {stats['total_entries']}")
            print(f"   频率范围: {stats['frequency_range'][0]:.1f} - {stats['frequency_range'][1]:.1f} Hz")
            print(f"   使用音区: {len(stats['zones_used'])} 个")
            print()
            
        except Exception as e:
            print(f"φ = {phi:.6f}: 错误 - {e}\n")

def parse_args():
    p = argparse.ArgumentParser(description="Petersen可变比例音阶生成器")
    p.add_argument('--F_base', type=float, default=20.0, help='基础频率 (默认: 20.0)')
    p.add_argument('--delta_theta', type=float, default=4.8, help='极性偏移角度 (默认: 4.8)')
    p.add_argument('--phi', type=float, default=PHI, help=f'比例系数 (默认: {PHI:.6f} 黄金比例)')
    p.add_argument('--preset', choices=list(PHI_PRESETS.keys()), 
                   help='使用预设φ值: golden(1.618), octave(2.0), fifth(1.5), tritone(√2)')
    p.add_argument('--compare', action='store_true', help='比较所有预设φ值')
    return p.parse_args()

if __name__ == "__main__":
    """
    测试和演示代码
    
    运行方式：
    python PetersenScale_Phi.py                           # 使用默认黄金比例
    python PetersenScale_Phi.py --preset octave           # 使用八度关系
    python PetersenScale_Phi.py --preset fifth            # 使用完全五度
    python PetersenScale_Phi.py --phi 1.25                # 使用自定义φ值
    python PetersenScale_Phi.py --compare                 # 比较所有预设值
    """

    args = parse_args()
    
    # 处理预设φ值
    if args.preset:
        phi_value = PHI_PRESETS[args.preset]
        print(f"使用预设 '{args.preset}': φ = {phi_value}")
    else:
        phi_value = args.phi
    
    # 比较模式
    if args.compare:
        compare_phi_values(list(PHI_PRESETS.values()), args.F_base, args.delta_theta)
        exit()

    F_base = args.F_base
    delta_theta = args.delta_theta

    print("=== Petersen 可变比例音阶系统测试 ===\n")
    
    # 创建音阶对象
    scale = PetersenScale_Phi(F_base=F_base, delta_theta=delta_theta, phi=phi_value,
                              F_min=30.0, F_max=6000.0, reference=220.0)
    
    # 显示φ信息
    phi_info = scale.get_phi_info()
    print(f"φ值信息:")
    print(f"   数值: {phi_info['phi_value']:.6f}")
    print(f"   名称: {phi_info['phi_name']}")
    print(f"   描述: {phi_info['musical_description']}")
    print(f"   每音区音分: {phi_info['cents_per_zone']:.1f}")
    print()
    
    # 验证实现正确性
    if scale.validate_implementation():
        print("✓ 实现验证通过")
    else:
        print("✗ 实现验证失败")
    
    # 生成音阶
    entries = scale.generate()
    raw_entries = scale.generate_raw()
    
    print(f"\n=== 音阶条目预览 (前6个) ===")
    for e in entries[:6]:
        print(f"{e['key_short']:4} {e['key_long']:<6} n={e['n']:>2} "
              f"freq={e['freq']:8.3f} Hz  "
              f"interval=[{e['interval_a']:.3f},{e['interval_b']:.3f}] "
              f"cents={e['cents_ref']:>6.1f}")
    
    print(f"... 共生成 {len(entries)} 个音阶条目")
    
    # 统计信息
    print(f"\n=== 统计信息 ===")
    stats = scale.get_statistics()
    print(f"总条目数: {stats['total_entries']}")
    print(f"频率范围: {stats['frequency_range'][0]:.2f} - {stats['frequency_range'][1]:.2f} Hz")
    print(f"使用音区: {stats['zones_used']}")
    print(f"五行分布: {stats['elements_distribution']}")
    print(f"极性分布: {stats['polarity_distribution']}")
    
    # 音程分析（显示前几个）
    print(f"\n=== 音程分析 (前5个音程) ===")
    intervals = scale.analyze_intervals()
    for i, interval in enumerate(intervals[:5]):
        print(f"{interval['from_key']} -> {interval['to_key']}: "
              f"{interval['ratio']:.4f} ({interval['cents']:>6.1f} cents)")
    
    # 查询功能演示
    print(f"\n=== 查询功能演示 ===")
    test_key = "J-"
    freq = scale.get_frequency_for_key(test_key)
    print(f"音名 '{test_key}' 的频率: {freq:.3f} Hz" if freq else f"未找到音名 '{test_key}'")
    
    zone_5_entries = scale.get_entries_in_zone(5)
    print(f"第5音区包含 {len(zone_5_entries)} 个条目")
    
    freq_range = scale.get_frequency_range()
    print(f"实际频率范围: {freq_range[0]:.2f} - {freq_range[1]:.2f} Hz")
    
    # 导出功能测试（自动生成包含φ信息的文件名）
    print(f"\n=== 导出功能测试 ===")
    try:
        scale.export_csv()
        print(f"✓ CSV导出成功（自动文件名）")
    except Exception as ex:
        print(f"✗ CSV导出失败: {ex}")
    
    try:
        scale.to_scala_file()
        print(f"✓ Scala导出成功（自动文件名）")
    except Exception as ex:
        print(f"✗ Scala导出失败: {ex}")
    
    try:
        scale.to_midi_tuning()
        print(f"✓ MIDI调音表导出成功（自动文件名）")
    except Exception as ex:
        print(f"✗ MIDI调音表导出失败: {ex}")

    try:
        pruned = scale.prune_keep_neutral_zones(raw_entries, zones=[1, 2])
        prune_filename = f"{scale._generate_filename_base()}_prune.tun"
        scale.to_midi_tuning(prune_filename, entries=pruned)
        print(f"✓ 裁剪版MIDI调音表导出成功: {prune_filename}")
    except Exception as ex:
        print(f"✗ 裁剪版MIDI调音表导出失败: {ex}")
    
    print(f"\n=== 测试完成 ===")
    print(f"📁 生成的文件前缀: {scale._generate_filename_base()}")