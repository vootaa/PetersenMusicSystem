"""
Petersen音阶与中国五行阴阳理论结合演示
展示东西方音乐理论的融合应用
"""
import time
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from enhanced_petersen_player import create_player
from utils.analysis import FrequencyAnalyzer

class WuXingElement(Enum):
    """五行元素"""
    WOOD = "木"    # Wood - 生长、升发
    FIRE = "火"    # Fire - 温热、上炎
    EARTH = "土"   # Earth - 承载、化生
    METAL = "金"   # Metal - 收敛、肃杀
    WATER = "水"   # Water - 寒凉、下行

class YinYangPolarity(Enum):
    """阴阳极性"""
    YIN = "阴"     # 阴性 - 柔、静、降、内
    YANG = "阳"    # 阳性 - 刚、动、升、外

@dataclass
class WuXingNote:
    """五行音符"""
    element: WuXingElement
    polarity: YinYangPolarity
    frequency: float
    traditional_name: str  # 传统音名（宫商角徵羽）
    petersen_frequency: float  # Petersen精确频率
    harmonic_ratio: float  # 谐波比例
    energy_level: int  # 能量级别 (1-10)

class PetersenWuXingSystem:
    """Petersen五行音阶系统"""
    
    def __init__(self, base_frequency: float = 261.63):  # C4
        self.base_frequency = base_frequency
        self.player = None
        
        # 五行生克关系
        self.generation_cycle = {  # 相生关系
            WuXingElement.WOOD: WuXingElement.FIRE,    # 木生火
            WuXingElement.FIRE: WuXingElement.EARTH,   # 火生土
            WuXingElement.EARTH: WuXingElement.METAL,  # 土生金
            WuXingElement.METAL: WuXingElement.WATER,  # 金生水
            WuXingElement.WATER: WuXingElement.WOOD    # 水生木
        }
        
        self.destruction_cycle = {  # 相克关系
            WuXingElement.WOOD: WuXingElement.EARTH,   # 木克土
            WuXingElement.FIRE: WuXingElement.METAL,   # 火克金
            WuXingElement.EARTH: WuXingElement.WATER,  # 土克水
            WuXingElement.METAL: WuXingElement.WOOD,   # 金克木
            WuXingElement.WATER: WuXingElement.FIRE    # 水克火
        }
        
        # 生成五行音阶
        self.wuxing_scale = self._generate_wuxing_scale()
        
    def initialize_player(self):
        """初始化播放器"""
        print("🎵 初始化Petersen五行音阶系统...")
        self.player = create_player()
        
        # 应用适合东方音乐的预设
        self.player.apply_preset_combination("intimate_salon", "debussy_impressionist")
        print("✅ 播放器初始化完成")
    
    def _generate_wuxing_scale(self) -> List[WuXingNote]:
        """生成五行音阶"""
        
        # 五行对应的传统音名和谐波比例
        element_data = {
            WuXingElement.WOOD: {
                'name': '角',  # 角音
                'ratio': 5/4,  # 大三度
                'energy': 8,   # 生发之气
                'polarity': YinYangPolarity.YANG
            },
            WuXingElement.FIRE: {
                'name': '徵',  # 徵音  
                'ratio': 3/2,  # 纯五度
                'energy': 10,  # 最强阳气
                'polarity': YinYangPolarity.YANG
            },
            WuXingElement.EARTH: {
                'name': '宫',  # 宫音
                'ratio': 1/1,  # 基音
                'energy': 5,   # 中和之气
                'polarity': YinYangPolarity.YIN
            },
            WuXingElement.METAL: {
                'name': '商',  # 商音
                'ratio': 9/8,  # 大二度
                'energy': 3,   # 收敛之气
                'polarity': YinYangPolarity.YIN
            },
            WuXingElement.WATER: {
                'name': '羽',  # 羽音
                'ratio': 27/16, # 小六度
                'energy': 1,   # 最弱阴气
                'polarity': YinYangPolarity.YIN
            }
        }
        
        wuxing_notes = []
        
        for element in WuXingElement:
            data = element_data[element]
            
            # 计算基础频率
            base_freq = self.base_frequency * data['ratio']
            
            # 应用Petersen音阶的微调
            petersen_freq = self._apply_petersen_tuning(base_freq, element)
            
            note = WuXingNote(
                element=element,
                polarity=data['polarity'],
                frequency=base_freq,
                traditional_name=data['name'],
                petersen_frequency=petersen_freq,
                harmonic_ratio=data['ratio'],
                energy_level=data['energy']
            )
            
            wuxing_notes.append(note)
        
        return wuxing_notes
    
    def _apply_petersen_tuning(self, base_freq: float, element: WuXingElement) -> float:
        """应用Petersen音阶微调"""
        
        # 为不同五行元素应用不同的微调策略
        adjustment_factors = {
            WuXingElement.WOOD: 1.002,    # 木：轻微升高，象征生长
            WuXingElement.FIRE: 1.004,    # 火：明显升高，象征炎上
            WuXingElement.EARTH: 1.000,   # 土：保持不变，象征稳定
            WuXingElement.METAL: 0.998,   # 金：轻微降低，象征收敛
            WuXingElement.WATER: 0.996    # 水：明显降低，象征下行
        }
        
        factor = adjustment_factors.get(element, 1.0)
        return base_freq * factor
    
    def demonstrate_wuxing_system(self):
        """演示五行音阶系统"""
        print("\n🌿 === Petersen五行音阶系统演示 ===")
        
        # 1. 介绍五行理论
        self._introduce_wuxing_theory()
        
        # 2. 演示基础五行音阶
        self._demo_basic_wuxing_scale()
        
        # 3. 演示相生关系
        self._demo_generation_relationships()
        
        # 4. 演示相克关系  
        self._demo_destruction_relationships()
        
        # 5. 阴阳平衡演示
        self._demo_yinyang_balance()
        
        # 6. 四季变化演示
        self._demo_seasonal_variations()
        
        # 7. 情绪表达演示
        self._demo_emotional_expressions()
    
    def _introduce_wuxing_theory(self):
        """介绍五行理论"""
        print("\n📚 五行理论基础:")
        print("   木 (角音) - 生长、升发、春天、肝")
        print("   火 (徵音) - 温热、炎上、夏天、心") 
        print("   土 (宫音) - 承载、化生、长夏、脾")
        print("   金 (商音) - 收敛、肃杀、秋天、肺")
        print("   水 (羽音) - 寒凉、下行、冬天、肾")
        print("\n🎼 五行音阶特点:")
        
        for note in self.wuxing_scale:
            freq_diff = note.petersen_frequency - note.frequency
            cents = FrequencyAnalyzer.frequency_to_cents(note.petersen_frequency / note.frequency)
            
            print(f"   {note.element.value} ({note.traditional_name}): {note.frequency:.2f}Hz → {note.petersen_frequency:.2f}Hz")
            print(f"      Petersen调整: {cents:.1f}音分, 能量级: {note.energy_level}, 极性: {note.polarity.value}")
    
    def _demo_basic_wuxing_scale(self):
        """演示基础五行音阶"""
        print("\n🎵 演示基础五行音阶 (宫商角徵羽):")
        
        # 按传统顺序排列：宫商角徵羽
        ordered_elements = [
            WuXingElement.EARTH,  # 宫
            WuXingElement.METAL,  # 商  
            WuXingElement.WOOD,   # 角
            WuXingElement.FIRE,   # 徵
            WuXingElement.WATER   # 羽
        ]
        
        frequencies = []
        names = []
        
        for element in ordered_elements:
            note = next(n for n in self.wuxing_scale if n.element == element)
            frequencies.append(note.petersen_frequency)
            names.append(f"{note.traditional_name}({note.element.value})")
            
            print(f"   🎵 {note.traditional_name} ({note.element.value}): {note.petersen_frequency:.2f}Hz")
        
        # 播放完整音阶
        self.player.play_frequencies(frequencies, names, duration=1.0, gap=0.5)
        
        print("✅ 基础五行音阶演示完成")
    
    def _demo_generation_relationships(self):
        """演示相生关系"""
        print("\n🔄 演示五行相生关系:")
        
        for element, generated in self.generation_cycle.items():
            print(f"\n   {element.value} 生 {generated.value}")
            
            # 找到对应音符
            source_note = next(n for n in self.wuxing_scale if n.element == element)
            target_note = next(n for n in self.wuxing_scale if n.element == generated)
            
            print(f"   {source_note.traditional_name}({source_note.petersen_frequency:.2f}Hz) → "
                  f"{target_note.traditional_name}({target_note.petersen_frequency:.2f}Hz)")
            
            # 播放相生音程
            frequencies = [source_note.petersen_frequency, target_note.petersen_frequency]
            names = [f"{source_note.traditional_name}({element.value})", 
                    f"{target_note.traditional_name}({generated.value})"]
            
            self.player.play_frequencies(frequencies, names, duration=1.5, gap=0.3)
            time.sleep(0.5)
        
        print("✅ 五行相生关系演示完成")
    
    def _demo_destruction_relationships(self):
        """演示相克关系"""
        print("\n⚔️  演示五行相克关系:")
        
        # 应用更尖锐的音效来表现相克关系
        self.player.effects.apply_effect_preset("dry")
        self.player.expression.apply_expression_preset("mechanical")
        
        for element, destroyed in self.destruction_cycle.items():
            print(f"\n   {element.value} 克 {destroyed.value}")
            
            source_note = next(n for n in self.wuxing_scale if n.element == element)
            target_note = next(n for n in self.wuxing_scale if n.element == destroyed)
            
            print(f"   {source_note.traditional_name} 克制 {target_note.traditional_name}")
            
            # 播放相克音程（使用不和谐的效果）
            frequencies = [source_note.petersen_frequency, target_note.petersen_frequency]
            names = [f"{source_note.traditional_name}(克)", 
                    f"{target_note.traditional_name}(被克)"]
            
            # 同时播放产生紧张感
            self.player.play_frequencies(frequencies, names, duration=1.0, gap=0.0)
            time.sleep(0.8)
        
        # 恢复柔和音效
        self.player.apply_preset_combination("intimate_salon", "debussy_impressionist")
        print("✅ 五行相克关系演示完成")
    
    def _demo_yinyang_balance(self):
        """演示阴阳平衡"""
        print("\n☯️  演示阴阳平衡:")
        
        # 分离阴阳音符
        yang_notes = [n for n in self.wuxing_scale if n.polarity == YinYangPolarity.YANG]
        yin_notes = [n for n in self.wuxing_scale if n.polarity == YinYangPolarity.YIN]
        
        print(f"\n🌟 阳性音符 ({len(yang_notes)}个):")
        yang_frequencies = []
        yang_names = []
        for note in yang_notes:
            print(f"   {note.traditional_name} ({note.element.value}): 能量级{note.energy_level}")
            yang_frequencies.append(note.petersen_frequency)
            yang_names.append(f"{note.traditional_name}(阳)")
        
        print(f"\n🌙 阴性音符 ({len(yin_notes)}个):")
        yin_frequencies = []
        yin_names = []
        for note in yin_notes:
            print(f"   {note.traditional_name} ({note.element.value}): 能量级{note.energy_level}")
            yin_frequencies.append(note.petersen_frequency)
            yin_names.append(f"{note.traditional_name}(阴)")
        
        # 先播放阳性音符（升调）
        print("\n🎵 播放阳性音符序列:")
        self.player.expression.apply_expression_preset("liszt_virtuosity")  # 强劲风格
        self.player.play_frequencies(yang_frequencies, yang_names, duration=1.0)
        
        time.sleep(1.0)
        
        # 再播放阴性音符（降调）
        print("\n🎵 播放阴性音符序列:")
        self.player.expression.apply_expression_preset("schumann_dreamy")  # 梦幻风格
        self.player.play_frequencies(yin_frequencies, yin_names, duration=1.5)
        
        time.sleep(1.0)
        
        # 最后播放平衡序列
        print("\n🎵 播放阴阳平衡序列:")
        balanced_freq = []
        balanced_names = []
        
        # 交替排列阴阳音符
        all_notes = sorted(self.wuxing_scale, key=lambda x: x.energy_level)
        for note in all_notes:
            balanced_freq.append(note.petersen_frequency)
            balanced_names.append(f"{note.traditional_name}({note.polarity.value})")
        
        self.player.expression.apply_expression_preset("ravel_crystalline")  # 平衡风格
        self.player.play_frequencies(balanced_freq, balanced_names, duration=1.2)
        
        print("✅ 阴阳平衡演示完成")
    
    def _demo_seasonal_variations(self):
        """演示四季变化"""
        print("\n🌸🌞🍂❄️  演示四季五行变化:")
        
        seasons = {
            '春': {'element': WuXingElement.WOOD, 'description': '生机勃勃，万物复苏'},
            '夏': {'element': WuXingElement.FIRE, 'description': '热情奔放，阳气极盛'},
            '长夏': {'element': WuXingElement.EARTH, 'description': '稳重厚实，化生万物'}, 
            '秋': {'element': WuXingElement.METAL, 'description': '收敛肃杀，万物归藏'},
            '冬': {'element': WuXingElement.WATER, 'description': '潜藏蛰伏，阴气极盛'}
        }
        
        for season, info in seasons.items():
            print(f"\n🌿 {season}季 - {info['element'].value}行:")
            print(f"   特点: {info['description']}")
            
            # 找到主导音符
            main_note = next(n for n in self.wuxing_scale if n.element == info['element'])
            
            # 生成季节性音阶（主音+相生关系）
            generated_element = self.generation_cycle[info['element']]
            generated_note = next(n for n in self.wuxing_scale if n.element == generated_element)
            
            seasonal_frequencies = [main_note.petersen_frequency, generated_note.petersen_frequency]
            seasonal_names = [f"{main_note.traditional_name}({season}主)", 
                            f"{generated_note.traditional_name}({season}辅)"]
            
            # 应用季节性表现力
            if season in ['春', '夏']:
                self.player.expression.apply_expression_preset("chopin_poetry")  # 明亮
            else:
                self.player.expression.apply_expression_preset("schumann_dreamy")  # 内敛
            
            print(f"   🎵 {main_note.traditional_name} + {generated_note.traditional_name}")
            self.player.play_frequencies(seasonal_frequencies, seasonal_names, duration=2.0)
            
            time.sleep(0.5)
        
        print("✅ 四季变化演示完成")
    
    def _demo_emotional_expressions(self):
        """演示情绪表达"""
        print("\n😊😢😡😌😨 演示五行情绪表达:")
        
        emotions = {
            '喜悦': {
                'elements': [WuXingElement.FIRE, WuXingElement.WOOD], 
                'description': '心火旺盛，肝木疏泄',
                'preset': 'jazz_swing'
            },
            '忧思': {
                'elements': [WuXingElement.EARTH, WuXingElement.METAL],
                'description': '脾土困顿，肺金悲伤', 
                'preset': 'schumann_dreamy'
            },
            '恐惧': {
                'elements': [WuXingElement.WATER],
                'description': '肾水不足，精神恐惧',
                'preset': 'minimalist_reich'
            },
            '愤怒': {
                'elements': [WuXingElement.WOOD, WuXingElement.FIRE],
                'description': '肝火上炎，怒发冲冠',
                'preset': 'liszt_virtuosity'
            },
            '平静': {
                'elements': [WuXingElement.EARTH],
                'description': '脾土和顺，心神安宁',
                'preset': 'ravel_crystalline'
            }
        }
        
        for emotion, info in emotions.items():
            print(f"\n💭 {emotion} - {info['description']}")
            
            # 应用情绪对应的表现力
            self.player.expression.apply_expression_preset(info['preset'])
            
            # 收集对应元素的音符
            emotion_frequencies = []
            emotion_names = []
            
            for element in info['elements']:
                note = next(n for n in self.wuxing_scale if n.element == element)
                emotion_frequencies.append(note.petersen_frequency)
                emotion_names.append(f"{note.traditional_name}({emotion})")
            
            # 根据情绪调整播放方式
            if emotion == '愤怒':
                duration = 0.8
                gap = 0.1
            elif emotion == '恐惧':
                duration = 2.0
                gap = 1.0
            elif emotion == '平静':
                duration = 3.0
                gap = 0.5
            else:
                duration = 1.5
                gap = 0.3
            
            print(f"   🎵 播放{len(emotion_frequencies)}个相关音符")
            self.player.play_frequencies(emotion_frequencies, emotion_names, 
                                       duration=duration, gap=gap)
            
            time.sleep(0.8)
        
        print("✅ 情绪表达演示完成")
    
    def generate_custom_wuxing_melody(self, pattern: str = "generation") -> List[float]:
        """生成自定义五行旋律"""
        print(f"\n🎼 生成五行{pattern}旋律:")
        
        frequencies = []
        names = []
        
        if pattern == "generation":
            # 按相生顺序
            element_order = [WuXingElement.WOOD, WuXingElement.FIRE, WuXingElement.EARTH, 
                           WuXingElement.METAL, WuXingElement.WATER, WuXingElement.WOOD]
        elif pattern == "destruction":
            # 按相克顺序
            element_order = [WuXingElement.WOOD, WuXingElement.EARTH, WuXingElement.WATER,
                           WuXingElement.FIRE, WuXingElement.METAL, WuXingElement.WOOD]
        else:
            # 能量级顺序
            sorted_notes = sorted(self.wuxing_scale, key=lambda x: x.energy_level)
            element_order = [note.element for note in sorted_notes]
        
        for element in element_order:
            note = next(n for n in self.wuxing_scale if n.element == element)
            frequencies.append(note.petersen_frequency)
            names.append(f"{note.traditional_name}({note.element.value})")
        
        print(f"🎵 播放{pattern}序列旋律:")
        for name in names:
            print(f"   {name}")
        
        self.player.play_frequencies(frequencies, names, duration=1.0, gap=0.2)
        
        return frequencies
    
    def analyze_frequency_wuxing_mapping(self, frequencies: List[float]) -> Dict:
        """分析频率的五行映射"""
        print("\n🔍 分析频率五行映射:")
        
        mappings = []
        
        for freq in frequencies:
            # 找到最接近的五行音符
            closest_note = None
            min_distance = float('inf')
            
            for note in self.wuxing_scale:
                distance = abs(freq - note.petersen_frequency)
                if distance < min_distance:
                    min_distance = distance
                    closest_note = note
            
            if closest_note:
                cents_diff = FrequencyAnalyzer.frequency_to_cents(freq / closest_note.petersen_frequency)
                mappings.append({
                    'frequency': freq,
                    'closest_element': closest_note.element,
                    'traditional_name': closest_note.traditional_name,
                    'distance_hz': min_distance,
                    'distance_cents': cents_diff,
                    'polarity': closest_note.polarity,
                    'energy_level': closest_note.energy_level
                })
        
        # 分析五行分布
        element_counts = {}
        for mapping in mappings:
            element = mapping['closest_element']
            element_counts[element] = element_counts.get(element, 0) + 1
        
        analysis = {
            'frequency_count': len(frequencies),
            'mappings': mappings,
            'element_distribution': element_counts,
            'dominant_element': max(element_counts.items(), key=lambda x: x[1])[0] if element_counts else None,
            'yin_yang_balance': self._calculate_yinyang_balance(mappings)
        }
        
        print(f"📊 分析结果:")
        print(f"   频率总数: {analysis['frequency_count']}")
        print(f"   主导元素: {analysis['dominant_element'].value if analysis['dominant_element'] else '无'}")
        print(f"   阴阳平衡: {analysis['yin_yang_balance']['ratio']:.2f} (阳/阴)")
        
        return analysis
    
    def _calculate_yinyang_balance(self, mappings: List[Dict]) -> Dict:
        """计算阴阳平衡"""
        yin_count = sum(1 for m in mappings if m['polarity'] == YinYangPolarity.YIN)
        yang_count = sum(1 for m in mappings if m['polarity'] == YinYangPolarity.YANG)
        
        total = yin_count + yang_count
        ratio = yang_count / max(1, yin_count)
        
        return {
            'yin_count': yin_count,
            'yang_count': yang_count,
            'total': total,
            'ratio': ratio,
            'balance_type': 'balanced' if 0.8 <= ratio <= 1.2 else 'yang_dominant' if ratio > 1.2 else 'yin_dominant'
        }
    
    def cleanup(self):
        """清理资源"""
        if self.player:
            self.player.cleanup()

if __name__ == "__main__":
    """主函数"""
    system = PetersenWuXingSystem()
    
    try:
        system.initialize_player()
        system.demonstrate_wuxing_system()
        
        print("\n🎨 自定义旋律生成:")
        system.generate_custom_wuxing_melody("generation")
        time.sleep(1)
        system.generate_custom_wuxing_melody("destruction") 
        
        # 测试频率分析
        test_frequencies = [261.63, 329.63, 392.00, 523.25]
        analysis = system.analyze_frequency_wuxing_mapping(test_frequencies)
        
        print("\n🎉 Petersen五行音阶系统演示完成!")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        system.cleanup()