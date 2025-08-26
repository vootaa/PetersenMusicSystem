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

δθ值预设说明：
- δθ = 24.0° : 15等分（完美分布）→ 15平均律（φ=2.0时）
- δθ = 36.0° : 10等分（相邻重叠）→ 10平均律（φ=2.0时） 
- δθ = 72.0° : 完美五角星（最简洁）→ 5平均律（φ=2.0时）
- δθ = 180.0°: 对称双五角星（平衡）→ 10平均律（φ=2.0时）
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
SQRT3 = 3 ** 0.5           # √3 ≈ 1.732050807569
SQRT5 = 5 ** 0.5           # √5 ≈ 2.236067977500
SQRT6 = 6 ** 0.5           # √6 ≈ 2.449489742783
SQRT7 = 7 ** 0.5           # √7 ≈ 2.645751311065
SQRT8 = 8 ** 0.5           # √8 = 2√2 ≈ 2.828427124746

# 双重开方值（四次方根）
SQRT_SQRT2 = 2 ** 0.25     # √√2 = 2^(1/4) ≈ 1.189207115003
SQRT_SQRT3 = 3 ** 0.25     # √√3 = 3^(1/4) ≈ 1.316074012952
SQRT_SQRT5 = 5 ** 0.25     # √√5 = 5^(1/4) ≈ 1.495348781476
SQRT_SQRT6 = 6 ** 0.25     # √√6 = 6^(1/4) ≈ 1.565085288688
SQRT_SQRT7 = 7 ** 0.25     # √√7 = 7^(1/4) ≈ 1.627498164557
SQRT_SQRT8 = 8 ** 0.25     # √√8 = 2^(3/4) ≈ 1.681792830507

ELEMENTS_CN = ["金", "木", "水", "火", "土"]  # 五行中文名
ELEMENTS_PY = ["J", "M", "S", "H", "T"]  # 五行拼音首字母

# φ值预设常量（完整扩展版）
PHI_PRESETS = {
    # 小间隔值（微分音效果）
    "sqrt_sqrt2": SQRT_SQRT2,   # √√2 ≈ 1.189 微分音
    "sqrt_sqrt3": SQRT_SQRT3,   # √√3 ≈ 1.316 中性二度
    "tritone": SQRT2,           # √2 ≈ 1.414 增四度
    "sqrt_sqrt5": SQRT_SQRT5,   # √√5 ≈ 1.495 中性三度
    "fifth": 1.5,               # 1.5 完全五度
    "sqrt_sqrt6": SQRT_SQRT6,   # √√6 ≈ 1.565 增强三度
    "golden": PHI,              # φ ≈ 1.618 黄金比例
    "sqrt_sqrt7": SQRT_SQRT7,   # √√7 ≈ 1.627 小七度近似
    "sqrt_sqrt8": SQRT_SQRT8,   # √√8 ≈ 1.682 大六度近似
    "sqrt3": SQRT3,             # √3 ≈ 1.732 大六度
    
    # 传统音程值
    "octave": 2.0,              # 2.0 八度关系
    "sqrt5": SQRT5,             # √5 ≈ 2.236 九度
    "sqrt6": SQRT6,             # √6 ≈ 2.449 超八度
    "sqrt7": SQRT7,             # √7 ≈ 2.646 大十度
    "sqrt8": SQRT8,             # √8 ≈ 2.828 双增四度
    "ninth": 3.0,               # 3.0 纯九度
}

# delta_theta预设常量
DELTA_THETA_PRESETS = {
    # Petersen系统原始值
    "petersen_quarter": 2.4,       # 1/4原始值
    "petersen_original": 4.8,      # 原始Petersen系统
    "petersen_triple": 8.0,        # 72/9 = 8°
    "petersen_ninth": 9.0,         # 72/8 = 9°
    "petersen_double": 9.6,        # 2倍原始值
    
    # 72°的整数分割
    "72_div_4": 18.0,              # 72°/4 = 18°
    "72_div_3": 24.0,              # 72°/3 = 24° (15等分角度)
    "72_div_2": 36.0,              # 72°/2 = 36° (10等分重叠)
    "72_original": 72.0,           # 72° (完美五角星)
    
    # 特殊几何角度
    "right_angle": 90.0,           # 直角 (不等分15角星)
    "complement_108": 108.0,       # 五角星补角
    "special_96": 96.0,            # 特殊角度 (24°×4)
    "triple_symmetry": 120.0,      # 三重对称 (120°)
    "golden_twist": 144.0,         # 黄金扭曲 (144°=360°×(φ-1)²)
    "straight_angle": 180.0,       # 平角 (对称双五角星)
    "special_192": 192.0,          # 特殊角度 (24°×8)
    "super_pentagon": 216.0,       # 超级五角星 (72°×3)
    "dual_spiral": 240.0,          # 双重螺旋 (2/3圆周)
    "special_288": 288.0,          # 特殊角度 (72°×4)
    "convergent_spiral": 300.0,    # 收束螺旋
    
    # 微小角度值（密集分布）
    "dense_1": 1.0,                # 极密集分布
    "dense_2": 2.0,                # 密集分布
    "dense_3": 3.0,                # 密集分布
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
    else:
        # 格式化为文件名安全的字符串
        return f"phi_{phi:.6f}".replace('.', 'p')

def delta_theta_name(delta_theta: float) -> str:
    """
    根据delta_theta值返回英文名称，用于文件命名
    
    Args:
        delta_theta: δθ角度值
    
    Returns:
        英文名称字符串
    """
    # 检查是否为预设值（允许小量误差）
    for name, value in DELTA_THETA_PRESETS.items():
        if abs(delta_theta - value) < 1e-6:
            return name
    
    # 检查是否为特殊角度值
    special_angles = {
        24.0: "uniform_15",
        36.0: "overlap_10", 
        72.0: "pentagon_5",
        90.0: "mixed_15",
        108.0: "complement_15",
        120.0: "triple_15",
        144.0: "golden_15",
        180.0: "symmetric_10",
        216.0: "super_15",
        240.0: "spiral_15",
        300.0: "convergent_15"
    }
    
    for angle, name in special_angles.items():
        if abs(delta_theta - angle) < 1e-6:
            return name
    
    # 格式化为安全文件名
    return f"dth_{delta_theta:.1f}".replace('.', 'p')

def get_phi_info(phi: float) -> Dict[str, Union[float, str]]:
    """
    获取φ值的详细信息
    
    Args:
        phi: φ比例值
    
    Returns:
        包含φ值信息的字典
    """
    cents_per_zone = 1200 * math.log2(phi)
    zones_per_octave = 1200 / cents_per_zone if cents_per_zone > 0 else 0
    
    info = {
        "phi_value": phi,
        "phi_name": phi_name(phi),
        "cents_per_zone": cents_per_zone,
        "zones_per_octave": zones_per_octave,
        "musical_description": get_musical_description(phi)
    }
    
    return info

def get_musical_description(phi: float) -> str:
    """获取φ值的音乐学描述"""
    if abs(phi - PHI) < 1e-6:
        return "黄金比例：神秘独特的音程关系，Petersen原始系统"
    elif abs(phi - 2.0) < 1e-6:
        return "八度关系：与12平均律完全兼容，传统和谐"
    elif abs(phi - 1.5) < 1e-6:
        return "完全五度：极其稳定和谐，适合冥想和治疗音乐"
    elif abs(phi - SQRT2) < 1e-6:
        return "增四度(三全音)：现代音乐风格，张力感强"
    elif abs(phi - SQRT3) < 1e-6:
        return "大六度：浪漫温暖的音程"
    elif abs(phi - SQRT5) < 1e-6:
        return "大九度：开阔明亮的音程"
    elif abs(phi - 3.0) < 1e-6:
        return "纯九度：空灵神圣的音程"
    elif abs(phi - SQRT_SQRT2) < 1e-6:
        return "微分音间隔：极细腻的音程变化"
    else:
        cents_interval = 1200 * math.log2(phi)
        return f"自定义比例：每音区间隔约{cents_interval:.1f}音分"

def get_delta_theta_info(delta_theta: float, phi: float = 2.0) -> Dict[str, Union[float, str, bool]]:
    """
    获取delta_theta对应的详细信息
    
    Args:
        delta_theta: δθ角度值
        phi: φ比例值（用于计算音区大小）
    
    Returns:
        包含δθ信息的字典
    """
    divisions_per_zone = 360.0 / delta_theta
    zone_cents = 1200 * math.log2(phi)
    cents_per_step = zone_cents / divisions_per_zone
    
    # 检查是否为Petersen系统中的特殊角度模式
    is_special_pattern = False
    pattern_positions = 15  # 默认理论位置数
    
    if abs(delta_theta - 24.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 15
        pattern_mechanism = "完美15等分（无重叠）"
    elif abs(delta_theta - 36.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 10
        pattern_mechanism = "相邻重叠机制（5个阴阳重叠对）"
    elif abs(delta_theta - 72.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 5
        pattern_mechanism = "完美五角星（每个角度3重重叠）"
    elif abs(delta_theta - 90.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 15
        pattern_mechanism = "特殊不等分（9×18° + 6×36°间隔）"
    elif abs(delta_theta - 108.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 15
        pattern_mechanism = "五角星补角效应（反转几何）"
    elif abs(delta_theta - 120.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 15
        pattern_mechanism = "三重旋转对称（120°间隔）"
    elif abs(delta_theta - 144.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 15
        pattern_mechanism = "黄金扭曲（与φ相关的几何）"
    elif abs(delta_theta - 180.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 10
        pattern_mechanism = "对称双五角星（同元素阴阳重叠）"
    elif abs(delta_theta - 216.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 15
        pattern_mechanism = "超级五角星（3倍72°扩展）"
    elif abs(delta_theta - 240.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 15
        pattern_mechanism = "双重螺旋交错（2/3圆周）"
    elif abs(delta_theta - 300.0) < 1e-6:
        is_special_pattern = True
        pattern_positions = 15
        pattern_mechanism = "收束螺旋（接近完整旋转）"
    else:
        pattern_mechanism = "非特殊模式（复杂分布）"
    
    info = {
        "delta_theta": delta_theta,
        "name": delta_theta_name(delta_theta),
        "theoretical_divisions_per_zone": divisions_per_zone,
        "zone_size_cents": zone_cents,
        "theoretical_cents_per_step": cents_per_step,
        "is_special_pattern": is_special_pattern,
        "pattern_positions": pattern_positions if is_special_pattern else None,
        "pattern_mechanism": pattern_mechanism,
        "geometric_beauty": get_geometric_beauty_description(delta_theta),
    }
    
    # 描述信息
    if is_special_pattern:
        if abs(phi - 2.0) < 1e-6:
            if pattern_positions in [5, 10]:
                info["description"] = f"Petersen系统{pattern_positions}等分 = {pattern_positions}平均律（φ=2.0时）"
            else:
                info["description"] = f"Petersen系统{pattern_positions}位置特殊模式（φ=2.0时为非传统调律）"
        else:
            info["description"] = f"Petersen系统{pattern_positions}位置模式，φ={phi:.3f}基础（非传统调律）"
    else:
        info["description"] = f"复杂分布：理论{divisions_per_zone:.1f}等分但实际非特殊模式"
    
    return info

def get_geometric_beauty_description(delta_theta: float) -> str:
    """
    获取delta_theta值的几何美学描述
    
    Args:
        delta_theta: δθ角度值
    
    Returns:
        几何美学描述字符串
    """
    if abs(delta_theta - 24.0) < 1e-6:
        return "单一15角星：完美均匀分布，几何纯净"
    elif abs(delta_theta - 36.0) < 1e-6:
        return "重叠10角星：相邻重叠，和谐统一"
    elif abs(delta_theta - 72.0) < 1e-6:
        return "完美五角星：最简洁优雅，数学之美"
    elif abs(delta_theta - 90.0) < 1e-6:
        return "不等分15角星：规律中的变化，节奏感强"
    elif abs(delta_theta - 108.0) < 1e-6:
        return "反转五角星：五角星的镜像，对偶之美"
    elif abs(delta_theta - 120.0) < 1e-6:
        return "三重对称星：三重旋转对称，东方美学"
    elif abs(delta_theta - 144.0) < 1e-6:
        return "黄金扭曲星：与φ共鸣，神秘几何"
    elif abs(delta_theta - 180.0) < 1e-6:
        return "对称双五角星：两星相对，平衡之美"
    elif abs(delta_theta - 216.0) < 1e-6:
        return "超级五角星：五角星的升华，宏伟磅礴"
    elif abs(delta_theta - 240.0) < 1e-6:
        return "双重螺旋：交错盘旋，动态之美"
    elif abs(delta_theta - 300.0) < 1e-6:
        return "收束螺旋：向心聚合，张力与释放"
    else:
        return f"复杂几何：{360.0/delta_theta:.1f}等分理论的实际变形"

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
                 delta_theta: float = 4.8,
                 phi: float = PHI,
                 F_min: float = 30.0,
                 F_max: float = 6000.0,
                 reference: float = 440.0):
        """
        初始化音阶生成器
        
        Args:
            F_base: 基准频率 (Hz)，默认20Hz
            delta_theta: 极性角度步进 (度)，默认4.8°
                        预设值：72_div_3(24°), 72_div_2(36°), 72_original(72°)等
            phi: 音区间比例系数，默认黄金比例1.618
                 预设值：golden(1.618), octave(2.0), fifth(1.5), tritone(√2)等
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
        self.phi = float(phi)
        self.F_min = float(F_min)
        self.F_max = float(F_max)
        self.reference = float(reference)
        self.logger = logging.getLogger(__name__)
        
        # 用于性能优化的实例级缓存
        self._power_cache: Dict[float, float] = {}
        
        # 记录φ和δθ的组合信息
        phi_info = get_phi_info(phi)
        dth_info = get_delta_theta_info(delta_theta, phi)
        
        self.logger.info(f"Created PetersenScale_Phi with φ={phi:.6f} ({phi_info['phi_name']}), δθ={delta_theta}° ({dth_info['name']})")
        self.logger.info(f"   φ效果: {phi_info['musical_description']}")
        self.logger.info(f"   δθ效果: {dth_info['description']}")

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
        return get_phi_info(self.phi)
    
    def get_delta_theta_info(self) -> Dict[str, Union[float, str]]:
        """
        获取当前delta_theta的详细信息
        
        Returns:
            包含δθ信息的字典
        """
        return get_delta_theta_info(self.delta_theta, self.phi)
    
    # 统计分析方法
    def get_statistics(self) -> Dict[str, Union[int, float, List, Dict]]:
        """
        获取音阶的统计信息
        
        Returns:
            包含各种统计数据的字典，现在包含φ和δθ信息
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
            "phi_info": self.get_phi_info(),
            "delta_theta_info": self.get_delta_theta_info(),
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
        """生成包含φ和δθ信息的文件名基础"""
        def fmt(x):
            return str(x).replace('.', 'p')
        
        phi_desc = phi_name(self.phi)
        dth_desc = delta_theta_name(self.delta_theta)
        return f"petersen_phi_{phi_desc}_dth_{dth_desc}_F{fmt(self.F_base)}"

    # 导出方法（更新为包含φ和δθ信息）
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
            dth_info = self.get_delta_theta_info()
            description = f"Petersen Scale φ={self.phi:.6f} ({phi_info['phi_name']}) δθ={self.delta_theta}° ({dth_info['name']})"
        
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
            dth_info = self.get_delta_theta_info()
            name = f"Petersen φ={self.phi:.3f} δθ={self.delta_theta}°"
        
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

def compare_delta_theta_values(dth_values: List[float], phi: float = 2.0, F_base: float = 55.0) -> None:
    """
    比较不同delta_theta值的效果（固定φ值）
    
    Args:
        dth_values: 要比较的δθ值列表
        phi: 固定的φ值
        F_base: 基础频率
    """
    print(f"=== δθ值比较分析 (φ={phi}) ===")
    print(f"基础参数: φ={phi}, F_base={F_base} Hz\n")
    
    for dth in dth_values:
        try:
            scale = PetersenScale_Phi(F_base=F_base, delta_theta=dth, phi=phi)
            dth_info = scale.get_delta_theta_info()
            stats = scale.get_statistics()
            
            print(f"δθ = {dth}° ({dth_info['name']})")
            print(f"   描述: {dth_info['description']}")
            print(f"   几何美学: {dth_info['geometric_beauty']}")
            print(f"   每音区细分数: {dth_info['theoretical_divisions_per_zone']:.1f}")
            print(f"   每步长音分: {dth_info['theoretical_cents_per_step']:.1f}")
            print(f"   总条目数: {stats['total_entries']}")
            print()
            
        except Exception as e:
            print(f"δθ = {dth}°: 错误 - {e}\n")

def list_all_presets():
    """
    列出所有预设值
    """
    print("=== φ值预设 (漂亮的数学递进) ===")
    phi_items = list(PHI_PRESETS.items())
    for name, value in phi_items:
        cents_per_zone = 1200 * math.log2(value)
        print(f"  {name:<12}: {value:.6f} ({cents_per_zone:6.1f} cents/zone)")
    
    print(f"\n=== δθ值预设 (特殊几何结构) ===")
    dth_items = list(DELTA_THETA_PRESETS.items())
    for name, value in dth_items:
        eq_div = round(360.0 / value) if value > 0 else 0
        beauty_desc = get_geometric_beauty_description(value)
        print(f"  {name:<20}: {value:5.1f}° ({eq_div:3d}等分) - {beauty_desc}")

def parse_args():
    p = argparse.ArgumentParser(description="Petersen可变比例音阶生成器")
    p.add_argument('--F_base', type=float, default=20.0, help='基础频率 (默认: 20.0)')
    p.add_argument('--delta_theta', type=float, default=4.8, help='极性偏移角度 (默认: 4.8°)')
    p.add_argument('--dth_preset', choices=list(DELTA_THETA_PRESETS.keys()), 
                   help='使用δθ预设值: 72_div_2(36°), 72_div_3(24°), 72_original(72°)等')
    p.add_argument('--phi', type=float, default=PHI, help=f'比例系数 (默认: {PHI:.6f} 黄金比例)')
    p.add_argument('--preset', choices=list(PHI_PRESETS.keys()), 
                   help='使用φ预设值: golden(1.618), octave(2.0), fifth(1.5), tritone(√2)等')
    p.add_argument('--compare', action='store_true', help='比较所有预设φ值')
    p.add_argument('--compare_dth', action='store_true', help='比较常见δθ值（φ=2.0）')
    p.add_argument('--list_presets', action='store_true', help='列出所有预设值')
    return p.parse_args()

if __name__ == "__main__":
    """
    测试和演示代码
    
    运行方式：
    python PetersenScale_Phi.py                                         # 使用默认黄金比例
    python PetersenScale_Phi.py --preset octave                         # 使用八度关系
    python PetersenScale_Phi.py --preset sqrt3 --dth_preset 72_div_2    # φ=√3, δθ=36°
    python PetersenScale_Phi.py --phi 1.25 --delta_theta 60             # 使用自定义值
    python PetersenScale_Phi.py --compare                               # 比较所有φ预设值
    python PetersenScale_Phi.py --compare_dth                           # 比较所有dth预设值