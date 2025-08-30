"""
Petersen 旋律生成模块

基于Petersen图结构约束，实现单小节内的旋律单元生成。
提供图形游走算法和基础旋律模式，作为自动作曲的旋律素材。

主要功能：
- 三环平面图结构（内/中/外环）
- 图约束的音符游走算法
- 基本旋律模式（6-8种范式结构）
- 概率分布游走（环上/跨环/邻接）
- 单小节旋律单元生成

使用示例：
```python
from petersen_scale import PetersenScale
from petersen_chord import PetersenChordExtender
from petersen_melody import PetersenMelodyGenerator

# 创建基础系统
base_scale = PetersenScale(F_base=55.0, phi=2.0)
chord_extender = PetersenChordExtender(base_scale)
extended_scale = chord_extender.extend_scale_with_chords()

# 创建旋律生成器
melody_gen = PetersenMelodyGenerator(
    extended_scale=extended_scale,
    movement_probabilities=[0.4, 0.3, 0.3],  # 环上、跨环、邻接
    melody_style="balanced"
)

# 生成旋律单元
melody_unit = melody_gen.generate_melody_unit(
    start_element="金", start_polarity=0, start_zone=0,
    pattern="ascending_scale", length=30
)

# 分析和导出
melody_gen.export_melody_csv(melody_unit, "melody_output.csv")
```
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Set
from collections import defaultdict
import math
import random
from datetime import datetime
from enum import Enum

# 导入基础模块
try:
    from .petersen_scale import PetersenScale, ScaleEntry
    from .petersen_chord import ExtendedScale, ChordTone
except ImportError:
    from petersen_scale import PetersenScale, ScaleEntry
    from petersen_chord import ExtendedScale, ChordTone

# 五行元素映射
class Element(Enum):
    """五行元素枚举"""
    METAL = (0, "金")      # 金
    WOOD = (1, "木")       # 木  
    WATER = (2, "水")      # 水
    FIRE = (3, "火")       # 火
    EARTH = (4, "土")      # 土
    
    def __init__(self, value: int, chinese: str):
        self.value = value
        self.chinese = chinese
    
    @classmethod
    def from_value(cls, value: int):
        """从数值获取元素"""
        for element in cls:
            if element.value == value:
                return element
        raise ValueError(f"无效的元素值: {value}")
    
    def next_element(self) -> 'Element':
        """获取下一个元素（五行顺序）"""
        next_value = (self.value + 1) % 5
        return Element.from_value(next_value)
    
    def prev_element(self) -> 'Element':
        """获取前一个元素（五行逆序）"""
        prev_value = (self.value - 1) % 5
        return Element.from_value(prev_value)

@dataclass
class GraphNode:
    """图节点定义"""
    ring: str               # "inner", "middle", "outer"
    element: Element        # 五行元素
    polarity: int          # -1(阴), 0(中), 1(阳)
    zone: int              # 音区编号
    scale_entry: Optional[ScaleEntry] = None  # 对应的音阶条目
    chord_tone: Optional[ChordTone] = None    # 对应的和弦音（如果是扩展音）
    
    def __post_init__(self):
        """初始化后处理"""
        if self.scale_entry is None and self.chord_tone is None:
            raise ValueError("节点必须关联音阶条目或和弦音")
    
    @property
    def frequency(self) -> float:
        """获取频率"""
        if self.scale_entry:
            return self.scale_entry.frequency
        elif self.chord_tone:
            return self.chord_tone.frequency
        return 0.0
    
    @property
    def key_name(self) -> str:
        """获取键名"""
        if self.scale_entry:
            return self.scale_entry.key_short
        elif self.chord_tone:
            return f"和弦音{self.chord_tone.ratio_name}"
        return "未知"
    
    def __str__(self) -> str:
        polarity_str = {-1: "阴", 0: "中", 1: "阳"}[self.polarity]
        return f"{self.element.chinese}{polarity_str}({self.ring}环,{self.zone}区)"
    
    def __hash__(self) -> int:
        return hash((self.ring, self.element.value, self.polarity, self.zone))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, GraphNode):
            return False
        return (self.ring == other.ring and 
                self.element == other.element and 
                self.polarity == other.polarity and 
                self.zone == other.zone)

@dataclass
class MelodyNote:
    """旋律音符"""
    measure: int            # 小节号
    beat: int              # 拍号（0-4）
    position: int          # 音符位置（0-29）
    graph_node: GraphNode  # 对应的图节点
    duration: float        # 持续时间（以位置为单位）
    velocity: int          # 力度（0-127）
    is_ornament: bool = False      # 是否为装饰音
    articulation: str = "normal"   # 演奏技法
    
    @property
    def frequency(self) -> float:
        """获取频率"""
        return self.graph_node.frequency
    
    @property
    def key_name(self) -> str:
        """获取键名"""
        return self.graph_node.key_name

@dataclass
class MelodyUnit:
    """旋律单元（一小节）"""
    measure_number: int
    melody_notes: List[MelodyNote]
    pattern_used: str
    walking_path: List[GraphNode]
    start_node: GraphNode
    end_node: GraphNode
    
    def get_total_duration(self) -> float:
        """获取总持续时间"""
        return sum(note.duration for note in self.melody_notes)
    
    def get_frequency_range(self) -> Tuple[float, float]:
        """获取频率范围"""
        frequencies = [note.frequency for note in self.melody_notes]
        return min(frequencies), max(frequencies)
    
    def get_pattern_statistics(self) -> Dict[str, int]:
        """获取模式统计"""
        stats = {
            "total_notes": len(self.melody_notes),
            "unique_nodes": len(set(self.walking_path)),
            "ring_transitions": 0,
            "zone_transitions": 0,
            "element_transitions": 0
        }
        
        for i in range(1, len(self.walking_path)):
            prev_node = self.walking_path[i-1]
            curr_node = self.walking_path[i]
            
            if prev_node.ring != curr_node.ring:
                stats["ring_transitions"] += 1
            if prev_node.zone != curr_node.zone:
                stats["zone_transitions"] += 1
            if prev_node.element != curr_node.element:
                stats["element_transitions"] += 1
        
        return stats

# 旋律模式定义
MELODY_PATTERNS = {
    "ascending_scale": {
        "description": "五行顺序上行",
        "structure": "sequential_up",
        "preferred_moves": ["ring_rotation_up"],
        "avoid_moves": ["ring_rotation_down"],
        "repetition_allowed": False
    },
    
    "descending_scale": {
        "description": "五行顺序下行",
        "structure": "sequential_down", 
        "preferred_moves": ["ring_rotation_down"],
        "avoid_moves": ["ring_rotation_up"],
        "repetition_allowed": False
    },
    
    "pentagram_jump": {
        "description": "五角星跳跃",
        "structure": "pentagram",
        "preferred_moves": ["same_ring_jump"],
        "avoid_moves": ["ring_rotation"],
        "repetition_allowed": True
    },
    
    "yin_yang_alternate": {
        "description": "阴阳交替",
        "structure": "polarity_alternate",
        "preferred_moves": ["cross_ring"],
        "avoid_moves": ["same_ring_jump"],
        "repetition_allowed": True
    },
    
    "ring_spiral": {
        "description": "环间螺旋",
        "structure": "ring_progression",
        "preferred_moves": ["cross_ring", "ring_rotation_up"],
        "avoid_moves": [],
        "repetition_allowed": False
    },
    
    "echo_return": {
        "description": "回音返回",
        "structure": "return_pattern",
        "preferred_moves": ["same_ring_jump", "cross_ring"],
        "avoid_moves": [],
        "repetition_allowed": True
    },
    
    "wave_motion": {
        "description": "波浪起伏",
        "structure": "oscillating",
        "preferred_moves": ["ring_rotation_up", "ring_rotation_down"],
        "avoid_moves": ["same_ring_jump"],
        "repetition_allowed": True
    },
    
    "cluster_exploration": {
        "description": "局部探索",
        "structure": "localized",
        "preferred_moves": ["same_ring_jump", "cross_ring"],
        "avoid_moves": ["ring_rotation"],
        "repetition_allowed": True
    }
}

class PetersenGraph:
    """Petersen图结构管理"""
    
    def __init__(self, extended_scale: ExtendedScale, max_zones: int = 3):
        """
        初始化图结构
        
        Args:
            extended_scale: 扩展音阶
            max_zones: 最大音区数
        """
        self.extended_scale = extended_scale
        self.max_zones = max_zones
        self.nodes: Dict[Tuple, GraphNode] = {}
        self.adjacency: Dict[GraphNode, List[GraphNode]] = defaultdict(list)
        
        self._build_graph()
        self._build_adjacency()
    
    def _build_graph(self):
        """构建图节点"""
        # 从根音构建内环和中环节点
        for root in self.extended_scale.root_notes[:15]:  # 最多3个音区
            element = Element.from_value(root.e)
            zone = root.n
            
            if zone >= self.max_zones:
                continue
                
            # 内环节点（五行中位）
            inner_key = ("inner", element.value, 0, zone)
            if inner_key not in self.nodes:
                self.nodes[inner_key] = GraphNode(
                    ring="inner",
                    element=element,
                    polarity=0,
                    zone=zone,
                    scale_entry=root
                )
            
            # 中环节点（重复内环，用于连接）
            middle_key = ("middle", element.value, 0, zone)
            if middle_key not in self.nodes:
                self.nodes[middle_key] = GraphNode(
                    ring="middle",
                    element=element,
                    polarity=0,
                    zone=zone,
                    scale_entry=root
                )
        
        # 从扩展音阶构建外环节点（阴阳位）
        for entry in self.extended_scale.original_entries:
            if entry.p != 0:  # 只要阴阳位
                element = Element.from_value(entry.e)
                zone = entry.n
                
                if zone >= self.max_zones:
                    continue
                
                outer_key = ("outer", element.value, entry.p, zone)
                if outer_key not in self.nodes:
                    self.nodes[outer_key] = GraphNode(
                        ring="outer",
                        element=element,
                        polarity=entry.p,
                        zone=zone,
                        scale_entry=entry
                    )
        
        # 添加和弦音作为扩展节点
        for chord_tone in self.extended_scale.chord_tones:
            if chord_tone.source_type == "generated":
                # 为生成的和弦音创建虚拟节点
                # 根据频率和根音关系推断可能的位置
                estimated_element, estimated_polarity = self._estimate_position(chord_tone)
                estimated_zone = 0  # 简化：默认音区
                
                chord_key = ("chord", estimated_element.value, estimated_polarity, estimated_zone, chord_tone.frequency)
                if chord_key not in self.nodes:
                    self.nodes[chord_key] = GraphNode(
                        ring="chord",
                        element=estimated_element,
                        polarity=estimated_polarity,
                        zone=estimated_zone,
                        chord_tone=chord_tone
                    )
    
    def _estimate_position(self, chord_tone: ChordTone) -> Tuple[Element, int]:
        """估算和弦音的图位置"""
        # 基于根音键名推断元素
        root_key = chord_tone.root_key
        
        # 简化映射（需要根据实际键名格式调整）
        element_map = {"J": Element.METAL, "M": Element.WOOD, "S": Element.WATER, 
                      "H": Element.FIRE, "T": Element.EARTH}
        
        element = element_map.get(root_key[0], Element.METAL)
        
        # 基于比率推断极性（简化逻辑）
        if chord_tone.ratio_from_root > 1.2:
            polarity = 1  # 阳
        elif chord_tone.ratio_from_root < 0.9:
            polarity = -1  # 阴
        else:
            polarity = 0  # 中
        
        return element, polarity
    
    def _build_adjacency(self):
        """构建邻接关系"""
        for node in self.nodes.values():
            neighbors = []
            
            if node.ring == "inner":
                # 内环：五角星跳跃 + 中环连接
                neighbors.extend(self._get_pentagram_neighbors(node))
                neighbors.extend(self._get_middle_ring_connections(node))
                
            elif node.ring == "middle":
                # 中环：内环连接 + 外环连接
                neighbors.extend(self._get_inner_ring_connections(node))
                neighbors.extend(self._get_outer_ring_connections(node))
                
            elif node.ring == "outer":
                # 外环：特殊跳跃 + 中环连接
                neighbors.extend(self._get_outer_ring_jumps(node))
                neighbors.extend(self._get_middle_ring_connections_from_outer(node))
                
            elif node.ring == "chord":
                # 和弦音：与相近的图节点连接
                neighbors.extend(self._get_chord_connections(node))
            
            # 过滤有效邻居并限制数量
            valid_neighbors = [n for n in neighbors if n is not None and n != node]
            self.adjacency[node] = valid_neighbors[:3]  # 最多3个邻接
    
    def _get_pentagram_neighbors(self, node: GraphNode) -> List[GraphNode]:
        """获取五角星邻接节点"""
        neighbors = []
        
        # 五角星跳跃：跳2个位置
        for offset in [2, -2]:  # +2和-2的跳跃
            target_element_value = (node.element.value + offset) % 5
            target_element = Element.from_value(target_element_value)
            
            target_key = ("inner", target_element.value, 0, node.zone)
            if target_key in self.nodes:
                neighbors.append(self.nodes[target_key])
        
        return neighbors
    
    def _get_middle_ring_connections(self, node: GraphNode) -> List[GraphNode]:
        """获取中环连接"""
        middle_key = ("middle", node.element.value, 0, node.zone)
        if middle_key in self.nodes:
            return [self.nodes[middle_key]]
        return []
    
    def _get_inner_ring_connections(self, node: GraphNode) -> List[GraphNode]:
        """获取内环连接"""
        inner_key = ("inner", node.element.value, 0, node.zone)
        if inner_key in self.nodes:
            return [self.nodes[inner_key]]
        return []
    
    def _get_outer_ring_connections(self, node: GraphNode) -> List[GraphNode]:
        """获取外环连接"""
        connections = []
        
        # 连接到同元素的阴阳位
        for polarity in [-1, 1]:
            outer_key = ("outer", node.element.value, polarity, node.zone)
            if outer_key in self.nodes:
                connections.append(self.nodes[outer_key])
        
        return connections
    
    def _get_middle_ring_connections_from_outer(self, node: GraphNode) -> List[GraphNode]:
        """从外环到中环的连接"""
        middle_key = ("middle", node.element.value, 0, node.zone)
        if middle_key in self.nodes:
            return [self.nodes[middle_key]]
        return []
    
    def _get_outer_ring_jumps(self, node: GraphNode) -> List[GraphNode]:
        """获取外环特殊跳跃"""
        neighbors = []
        
        # 外环特殊跳跃模式：金阴→木阳→水阴→火阳→土阴→金阳→木阴→水阳→火阴→土阳→金阴
        jump_sequence = [
            (Element.METAL, -1), (Element.WOOD, 1), (Element.WATER, -1), 
            (Element.FIRE, 1), (Element.EARTH, -1), (Element.METAL, 1),
            (Element.WOOD, -1), (Element.WATER, 1), (Element.FIRE, -1), 
            (Element.EARTH, 1)
        ]
        
        # 找到当前节点在序列中的位置
        current_pos = None
        for i, (elem, pol) in enumerate(jump_sequence):
            if elem == node.element and pol == node.polarity:
                current_pos = i
                break
        
        if current_pos is not None:
            # 前一个和后一个节点
            for offset in [-1, 1]:
                target_pos = (current_pos + offset) % len(jump_sequence)
                target_elem, target_pol = jump_sequence[target_pos]
                
                target_key = ("outer", target_elem.value, target_pol, node.zone)
                if target_key in self.nodes:
                    neighbors.append(self.nodes[target_key])
        
        return neighbors
    
    def _get_chord_connections(self, node: GraphNode) -> List[GraphNode]:
        """获取和弦音连接"""
        # 简化：连接到相近频率的图节点
        connections = []
        target_freq = node.frequency
        
        for other_node in self.nodes.values():
            if other_node.ring != "chord" and other_node != node:
                freq_ratio = target_freq / other_node.frequency
                # 如果频率比例合理（半音到全音范围）
                if 0.9 <= freq_ratio <= 1.2:
                    connections.append(other_node)
                    if len(connections) >= 3:
                        break
        
        return connections
    
    def get_neighbors(self, node: GraphNode) -> List[GraphNode]:
        """获取节点的邻接节点（不含旋转）"""
        return self.adjacency.get(node, [])
    
    def get_rotation_options(self, node: GraphNode) -> List[GraphNode]:
        """获取旋转选项（上行/下行）"""
        options = []
        
        # 上行：下一个音区的相同位置
        up_zone = node.zone + 1
        up_key = (node.ring, node.element.value, node.polarity, up_zone)
        if up_key in self.nodes:
            options.append(self.nodes[up_key])
        
        # 下行：前一个音区的相同位置
        down_zone = node.zone - 1
        if down_zone >= 0:
            down_key = (node.ring, node.element.value, node.polarity, down_zone)
            if down_key in self.nodes:
                options.append(self.nodes[down_key])
        
        # 跨音区特殊连接
        if node.element == Element.EARTH and node.polarity == 0:  # 土中
            # 土中可以连接到金中（下一音区）
            if up_zone < self.max_zones:
                gold_key = ("inner", Element.METAL.value, 0, up_zone)
                if gold_key in self.nodes:
                    options.append(self.nodes[gold_key])
        
        elif node.element == Element.METAL and node.polarity == 0:  # 金中
            # 金中可以连接到土中（前一音区）
            if down_zone >= 0:
                earth_key = ("inner", Element.EARTH.value, 0, down_zone)
                if earth_key in self.nodes:
                    options.append(self.nodes[earth_key])
        
        # 外环的跨音区连接
        if node.ring == "outer":
            if node.element == Element.EARTH and node.polarity == 1:  # 土阳
                gold_yin_key = ("outer", Element.METAL.value, -1, up_zone)
                if gold_yin_key in self.nodes:
                    options.append(self.nodes[gold_yin_key])
            elif node.element == Element.METAL and node.polarity == -1:  # 金阴
                earth_yang_key = ("outer", Element.EARTH.value, 1, down_zone)
                if earth_yang_key in self.nodes:
                    options.append(self.nodes[earth_yang_key])
        
        return options
    
    def get_all_candidates(self, node: GraphNode) -> List[GraphNode]:
        """获取所有候选节点（邻接+旋转，最多5个）"""
        candidates = []
        candidates.extend(self.get_neighbors(node))
        candidates.extend(self.get_rotation_options(node))
        
        # 去重并限制数量
        unique_candidates = []
        seen = set()
        for candidate in candidates:
            if candidate not in seen:
                unique_candidates.append(candidate)
                seen.add(candidate)
                if len(unique_candidates) >= 5:
                    break
        
        return unique_candidates
    
    def find_node_by_entry(self, scale_entry: ScaleEntry) -> Optional[GraphNode]:
        """根据音阶条目查找节点"""
        for node in self.nodes.values():
            if node.scale_entry == scale_entry:
                return node
        return None
    
    def get_nodes_by_ring(self, ring: str) -> List[GraphNode]:
        """获取指定环的所有节点"""
        return [node for node in self.nodes.values() if node.ring == ring]
    
    def get_nodes_by_element(self, element: Element) -> List[GraphNode]:
        """获取指定元素的所有节点"""
        return [node for node in self.nodes.values() if node.element == element]

class MelodyWalker:
    """旋律游走算法"""
    
    def __init__(self, 
                 graph: PetersenGraph,
                 movement_probabilities: List[float] = [0.4, 0.3, 0.3],
                 melody_style: str = "balanced"):
        """
        初始化旋律游走器
        
        Args:
            graph: Petersen图对象
            movement_probabilities: [环上旋转, 跨环移动, 同环邻接] 的概率
            melody_style: 旋律风格
        """
        self.graph = graph
        self.movement_probabilities = movement_probabilities
        self.melody_style = melody_style
        
        # 验证概率和为1
        if abs(sum(movement_probabilities) - 1.0) > 0.01:
            raise ValueError("移动概率之和必须为1.0")
    
    def walk_step(self, current_node: GraphNode, pattern_constraints: Dict = None) -> GraphNode:
        """
        执行一步游走
        
        Args:
            current_node: 当前节点
            pattern_constraints: 模式约束
            
        Returns:
            下一个节点
        """
        # 获取所有候选节点
        neighbors = self.graph.get_neighbors(current_node)
        rotations = self.graph.get_rotation_options(current_node)
        
        # 分类候选节点
        ring_rotations = rotations
        cross_ring_moves = [n for n in neighbors if n.ring != current_node.ring]
        same_ring_jumps = [n for n in neighbors if n.ring == current_node.ring]
        
        # 应用模式约束
        if pattern_constraints:
            ring_rotations = self._apply_pattern_filter(ring_rotations, pattern_constraints, "ring_rotation")
            cross_ring_moves = self._apply_pattern_filter(cross_ring_moves, pattern_constraints, "cross_ring")
            same_ring_jumps = self._apply_pattern_filter(same_ring_jumps, pattern_constraints, "same_ring_jump")
        
        # 根据概率选择移动类型
        move_type = random.choices(
            ["ring_rotation", "cross_ring", "same_ring_jump"],
            weights=self.movement_probabilities
        )[0]
        
        # 选择具体节点
        if move_type == "ring_rotation" and ring_rotations:
            return random.choice(ring_rotations)
        elif move_type == "cross_ring" and cross_ring_moves:
            return random.choice(cross_ring_moves)
        elif move_type == "same_ring_jump" and same_ring_jumps:
            return random.choice(same_ring_jumps)
        else:
            # 备选方案：从所有候选中随机选择
            all_candidates = ring_rotations + cross_ring_moves + same_ring_jumps
            if all_candidates:
                return random.choice(all_candidates)
            else:
                # 最后备选：保持当前节点
                return current_node
    
    def _apply_pattern_filter(self, candidates: List[GraphNode], 
                            constraints: Dict, move_type: str) -> List[GraphNode]:
        """应用模式约束过滤候选节点"""
        if move_type in constraints.get("preferred_moves", []):
            # 偏好的移动类型：保留所有候选
            return candidates
        elif move_type in constraints.get("avoid_moves", []):
            # 避免的移动类型：清空候选
            return []
        else:
            # 中性移动类型：保留候选
            return candidates
    
    def generate_melody_unit(self, 
                           start_node: GraphNode,
                           pattern: str = "balanced",
                           length: int = 30,
                           measure_number: int = 0) -> MelodyUnit:
        """
        生成一个旋律单元
        
        Args:
            start_node: 起始节点
            pattern: 旋律模式名称
            length: 旋律长度（音符位数）
            measure_number: 小节号
            
        Returns:
            旋律单元
        """
        if pattern not in MELODY_PATTERNS:
            pattern = "balanced"
            pattern_constraints = {}
        else:
            pattern_constraints = MELODY_PATTERNS[pattern]
        
        walking_path = [start_node]
        current_node = start_node
        
        # 执行游走
        for step in range(length - 1):
            next_node = self.walk_step(current_node, pattern_constraints)
            walking_path.append(next_node)
            current_node = next_node
        
        # 转换为旋律音符
        melody_notes = self._convert_path_to_notes(
            walking_path, measure_number, pattern
        )
        
        return MelodyUnit(
            measure_number=measure_number,
            melody_notes=melody_notes,
            pattern_used=pattern,
            walking_path=walking_path,
            start_node=start_node,
            end_node=current_node
        )
    
    def _convert_path_to_notes(self, path: List[GraphNode], 
                             measure_number: int, pattern: str) -> List[MelodyNote]:
        """将游走路径转换为旋律音符"""
        melody_notes = []
        
        for i, node in enumerate(path):
            beat = i // 6
            position = i
            
            # 计算音符持续时间（基本为1个位置）
            duration = 1.0
            
            # 计算力度（基于位置和节点特征）
            velocity = self._calculate_melody_velocity(node, i, pattern)
            
            # 判断是否为装饰音
            is_ornament = self._is_ornament_note(node, i, pattern)
            
            # 选择演奏技法
            articulation = self._select_articulation(node, i, pattern)
            
            melody_note = MelodyNote(
                measure=measure_number,
                beat=beat,
                position=position,
                graph_node=node,
                duration=duration,
                velocity=velocity,
                is_ornament=is_ornament,
                articulation=articulation
            )
            
            melody_notes.append(melody_note)
        
        return melody_notes
    
    def _calculate_melody_velocity(self, node: GraphNode, position: int, pattern: str) -> int:
        """计算旋律音符力度"""
        base_velocity = 70
        
        # 基于节点极性调整
        if node.polarity == 1:  # 阳位
            base_velocity += 15
        elif node.polarity == -1:  # 阴位
            base_velocity -= 10
        
        # 基于位置调整（强拍位置）
        beat_position = position % 6
        if beat_position == 0:  # 拍的第一个位置
            base_velocity += 10
        elif beat_position in [2, 4]:  # 中强位置
            base_velocity += 5
        
        # 基于模式调整
        if pattern in ["dynamic", "rhythmic_pulse"]:
            base_velocity += 10
        elif pattern in ["meditative", "flowing"]:
            base_velocity -= 5
        
        return max(20, min(127, base_velocity))
    
    def _is_ornament_note(self, node: GraphNode, position: int, pattern: str) -> bool:
        """判断是否为装饰音"""
        # 简化逻辑：某些位置和模式倾向于装饰音
        if pattern == "cluster_exploration":
            return position % 6 in [1, 3, 5]  # 弱拍位置
        elif pattern == "echo_return":
            return position % 4 == 2  # 每4个音符的第3个
        else:
            return False
    
    def _select_articulation(self, node: GraphNode, position: int, pattern: str) -> str:
        """选择演奏技法"""
        if pattern == "flowing":
            return "legato"  # 连奏
        elif pattern == "rhythmic_pulse":
            return "staccato"  # 断奏
        elif pattern == "meditative":
            return "sostenuto"  # 持续
        else:
            return "normal"  # 正常

class PetersenMelodyGenerator:
    """Petersen旋律生成器（高级接口）"""
    
    def __init__(self,
                 extended_scale: ExtendedScale,
                 movement_probabilities: List[float] = [0.4, 0.3, 0.3],
                 melody_style: str = "balanced",
                 max_zones: int = 3):
        """
        初始化旋律生成器
        
        Args:
            extended_scale: 扩展音阶
            movement_probabilities: 移动概率分布
            melody_style: 旋律风格
            max_zones: 最大音区数
        """
        self.extended_scale = extended_scale
        self.melody_style = melody_style
        
        # 构建图和游走器
        self.graph = PetersenGraph(extended_scale, max_zones)
        self.walker = MelodyWalker(self.graph, movement_probabilities, melody_style)
    
    def generate_melody_unit(self,
                           start_element: Union[str, Element] = "金",
                           start_polarity: int = 0,
                           start_zone: int = 0,
                           pattern: str = "balanced",
                           length: int = 30,
                           measure_number: int = 0) -> MelodyUnit:
        """
        生成旋律单元（用户友好接口）
        
        Args:
            start_element: 起始五行元素
            start_polarity: 起始极性 (-1, 0, 1)
            start_zone: 起始音区
            pattern: 旋律模式
            length: 旋律长度
            measure_number: 小节号
            
        Returns:
            旋律单元
        """
        # 转换元素参数
        if isinstance(start_element, str):
            element_map = {"金": Element.METAL, "木": Element.WOOD, "水": Element.WATER,
                          "火": Element.FIRE, "土": Element.EARTH}
            element = element_map.get(start_element, Element.METAL)
        else:
            element = start_element
        
        # 查找起始节点
        start_node = self._find_start_node(element, start_polarity, start_zone)
        if not start_node:
            # 备选方案：使用第一个可用节点
            all_nodes = list(self.graph.nodes.values())
            if all_nodes:
                start_node = all_nodes[0]
            else:
                raise ValueError("没有可用的图节点")
        
        return self.walker.generate_melody_unit(
            start_node, pattern, length, measure_number
        )
    
    def _find_start_node(self, element: Element, polarity: int, zone: int) -> Optional[GraphNode]:
        """查找起始节点"""
        # 优先查找内环节点
        inner_key = ("inner", element.value, polarity, zone)
        if inner_key in self.graph.nodes:
            return self.graph.nodes[inner_key]
        
        # 其次查找中环节点
        middle_key = ("middle", element.value, polarity, zone)
        if middle_key in self.graph.nodes:
            return self.graph.nodes[middle_key]
        
        # 最后查找外环节点
        outer_key = ("outer", element.value, polarity, zone)
        if outer_key in self.graph.nodes:
            return self.graph.nodes[outer_key]
        
        return None
    
    def generate_multiple_units(self,
                              measures: int = 4,
                              patterns: List[str] = None,
                              start_elements: List[str] = None) -> List[MelodyUnit]:
        """
        生成多个旋律单元
        
        Args:
            measures: 小节数
            patterns: 模式列表（如果为None则随机选择）
            start_elements: 起始元素列表（如果为None则循环使用五行）
            
        Returns:
            旋律单元列表
        """
        if patterns is None:
            patterns = list(MELODY_PATTERNS.keys())
        
        if start_elements is None:
            start_elements = ["金", "木", "水", "火", "土"]
        
        melody_units = []
        
        for measure in range(measures):
            pattern = patterns[measure % len(patterns)]
            element = start_elements[measure % len(start_elements)]
            
            melody_unit = self.generate_melody_unit(
                start_element=element,
                pattern=pattern,
                measure_number=measure
            )
            
            melody_units.append(melody_unit)
        
        return melody_units
    
    def analyze_melody_complexity(self, melody_unit: MelodyUnit) -> Dict[str, Union[int, float]]:
        """分析旋律复杂度"""
        stats = melody_unit.get_pattern_statistics()
        freq_range = melody_unit.get_frequency_range()
        
        # 计算复杂度指标
        complexity_score = (
            stats["ring_transitions"] * 0.3 +
            stats["zone_transitions"] * 0.5 +
            stats["element_transitions"] * 0.2
        )
        
        frequency_span = freq_range[1] / freq_range[0] if freq_range[0] > 0 else 1.0
        
        return {
            "complexity_score": complexity_score,
            "frequency_span_ratio": frequency_span,
            "unique_node_ratio": stats["unique_nodes"] / stats["total_notes"],
            "transition_density": (stats["ring_transitions"] + stats["zone_transitions"]) / stats["total_notes"],
            **stats,
            "frequency_range_hz": freq_range
        }
    
    def export_melody_csv(self, melody_unit: MelodyUnit, path: Union[str, Path] = None) -> None:
        """
        导出旋律单元到CSV文件
        
        Args:
            melody_unit: 旋律单元
            path: 输出路径
        """
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"petersen_melody_{melody_unit.pattern_used}_{timestamp}.csv"
        
        path = Path(path)
        
        with open(path, 'w', encoding='utf-8') as f:
            # CSV头部
            f.write("小节,拍,位置,节点,频率(Hz),持续时间,力度,装饰音,演奏技法,环,元素,极性,音区\n")
            
            for note in melody_unit.melody_notes:
                node = note.graph_node
                polarity_str = {-1: "阴", 0: "中", 1: "阳"}[node.polarity]
                
                f.write(f"{note.measure},{note.beat},{note.position},"
                       f"{node},{note.frequency:.2f},{note.duration:.2f},"
                       f"{note.velocity},{'是' if note.is_ornament else '否'},"
                       f"{note.articulation},{node.ring},{node.element.chinese},"
                       f"{polarity_str},{node.zone}\n")
        
        print(f"旋律单元已导出到: {path}")
    
    def export_melody_analysis_csv(self, melody_unit: MelodyUnit, path: Union[str, Path] = None) -> None:
        """
        导出旋律分析到CSV文件
        
        Args:
            melody_unit: 旋律单元
            path: 输出路径
        """
        analysis = self.analyze_melody_complexity(melody_unit)
        
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"petersen_melody_analysis_{melody_unit.pattern_used}_{timestamp}.csv"
        
        path = Path(path)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write("分析项目,数值,单位/说明\n")
            
            for key, value in analysis.items():
                if key == "frequency_range_hz":
                    f.write(f"频率范围,{value[0]:.2f}-{value[1]:.2f},Hz\n")
                else:
                    f.write(f"{key},{value},\n")
        
        print(f"旋律分析已导出到: {path}")

def compare_melody_patterns(extended_scale: ExtendedScale, measures: int = 1) -> None:
    """
    比较不同旋律模式的效果
    
    Args:
        extended_scale: 扩展音阶
        measures: 测试小节数
    """
    print("=== 旋律模式比较分析 ===\n")
    
    generator = PetersenMelodyGenerator(extended_scale)
    
    for pattern_name, pattern_info in MELODY_PATTERNS.items():
        print(f"【{pattern_name}】{pattern_info['description']}")
        
        melody_unit = generator.generate_melody_unit(
            start_element="金",
            pattern=pattern_name,
            length=30
        )
        
        analysis = generator.analyze_melody_complexity(melody_unit)
        
        print(f"  复杂度评分: {analysis['complexity_score']:.2f}")
        print(f"  频率跨度: {analysis['frequency_span_ratio']:.2f}")
        print(f"  节点多样性: {analysis['unique_node_ratio']:.2%}")
        print(f"  转换密度: {analysis['transition_density']:.2%}")
        print(f"  环转换: {analysis['ring_transitions']}次")
        print(f"  音区转换: {analysis['zone_transitions']}次")
        print()

if __name__ == "__main__":
    # 示例用法
    from petersen_scale import PetersenScale
    from petersen_chord import PetersenChordExtender
    
    # 创建基础系统
    base_scale = PetersenScale(F_base=55.0, phi=2.0, delta_theta=4.8)
    chord_extender = PetersenChordExtender(base_scale, chord_ratios="simple_ratios")
    extended_scale = chord_extender.extend_scale_with_chords()
    
    # 创建旋律生成器
    melody_gen = PetersenMelodyGenerator(
        extended_scale=extended_scale,
        movement_probabilities=[0.4, 0.3, 0.3],
        melody_style="balanced"
    )
    
    # 生成旋律单元
    print("生成旋律单元...")
    melody_unit = melody_gen.generate_melody_unit(
        start_element="金",
        start_polarity=0,
        pattern="ascending_scale",
        length=30
    )
    
    # 分析旋律
    analysis = melody_gen.analyze_melody_complexity(melody_unit)
    print("\n旋律复杂度分析:")
    for key, value in analysis.items():
        if key != "frequency_range_hz":
            print(f"  {key}: {value}")
        else:
            print(f"  频率范围: {value[0]:.2f} - {value[1]:.2f} Hz")
    
    # 显示旋律路径
    print(f"\n旋律路径 ({len(melody_unit.walking_path)} 个节点):")
    for i, node in enumerate(melody_unit.walking_path[:10]):  # 显示前10个
        print(f"  {i+1}. {node}")
    if len(melody_unit.walking_path) > 10:
        print(f"  ... 还有 {len(melody_unit.walking_path)-10} 个节点")
    
    # 导出文件
    melody_gen.export_melody_csv(melody_unit)
    melody_gen.export_melody_analysis_csv(melody_unit)
    
    # 比较不同模式
    print("\n" + "="*50)
    compare_melody_patterns(extended_scale)