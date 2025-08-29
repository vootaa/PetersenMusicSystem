#!/usr/bin/env python3
"""
Petersen音阶交互式演示程序
增强版本，支持基于五行相生相克关系的旋律构建
"""
import sys
import time
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from enum import Enum

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(current_dir))

from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS, ELEMENTS_CN, ELEMENTS_PY
from enhanced_petersen_player import create_player, PlayerConfiguration
from utils.presets import COMPLETE_PRESET_COMBINATIONS

class WuXingElement(Enum):
    """五行元素"""
    J = "金"  # 金
    M = "木"  # 木  
    S = "水"  # 水
    H = "火"  # 火
    T = "土"  # 土

class MelodyPattern(Enum):
    """旋律模式"""
    GENERATION = "相生"      # 五行相生关系
    DESTRUCTION = "相克"     # 五行相克关系
    BALANCE = "平衡"         # 阴阳平衡
    ASCENDING = "上行"       # 频率递增
    DESCENDING = "下行"      # 频率递减
    RANDOM = "随机"          # 随机排列
    PENTATONIC = "五声"      # 传统五声音阶

class PetersenScaleDemo:
    """Petersen音阶演示类"""
    
    def __init__(self):
        self.player = None
        self.current_scale = None
        self.steinway_files = [
            'GD_Steinway_Model_D274.sf2',
            'GD_Steinway_Model_D274II.sf2'
        ]
        
        # 五行相生关系 (生成循环)
        self.generation_cycle = {
            'M': 'H',  # 木生火
            'H': 'T',  # 火生土
            'T': 'J',  # 土生金
            'J': 'S',  # 金生水
            'S': 'M'   # 水生木
        }
        
        # 五行相克关系 (破坏循环)
        self.destruction_cycle = {
            'M': 'T',  # 木克土
            'H': 'J',  # 火克金
            'T': 'S',  # 土克水
            'J': 'M',  # 金克木
            'S': 'H'   # 水克火
        }
        
        # 五行对应传统音名
        self.traditional_names = {
            'T': '宫',  # 土 -> 宫
            'J': '商',  # 金 -> 商
            'M': '角',  # 木 -> 角
            'H': '徵',  # 火 -> 徵
            'S': '羽'   # 水 -> 羽
        }
        
    def initialize_player(self):
        """初始化播放器"""
        try:
            print("🔧 初始化播放器...")
            config = PlayerConfiguration(
                default_soundfont="GD_Steinway_Model_D274.sf2",
                soundfont_directory="../../Soundfonts"
            )
            self.player = create_player(config=config)
            print("✅ 播放器初始化成功!")
            current_sf = getattr(self.player.sf_manager, 'current_soundfont', None)
            if current_sf:
                print(f"🎹 已加载默认SoundFont: {current_sf}")
            return True
        except Exception as e:
            print(f"❌ 播放器初始化失败: {e}")
            return False
    
    def check_soundfont_switch(self):
        """检查是否需要切换SoundFont"""
        available_sf = self.list_available_soundfonts()
        if len(available_sf) <= 1:
            print("📝 只有一个SoundFont可用，跳过切换")
            return True
        
        current_sf = getattr(self.player.sf_manager, 'current_soundfont', None)
        print(f"\n📁 当前SoundFont: {current_sf}")
        print("可用SoundFont:")
        for i, sf in enumerate(available_sf, 1):
            mark = " (当前)" if sf == current_sf else ""
            print(f"   {i}. {sf}{mark}")
        
        switch_choice = input("\n是否切换SoundFont? (y/n, 默认n): ").strip().lower()
        if switch_choice == 'y':
            while True:
                try:
                    choice = input(f"选择SoundFont (1-{len(available_sf)}): ").strip()
                    index = int(choice) - 1
                    if 0 <= index < len(available_sf):
                        return self.load_steinway_soundfont(available_sf[index])
                    else:
                        print(f"❌ 请输入 1-{len(available_sf)}")
                except ValueError:
                    print("❌ 请输入有效数字")
        
        return True
    
    def list_available_soundfonts(self):
        """列出可用的Steinway SoundFont"""
        if not self.player:
            return []
        
        sf_summary = self.player.sf_manager.get_soundfont_summary()
        available_steinway = []
        
        for sf_name in self.steinway_files:
            if sf_name in sf_summary['soundfont_details']:
                available_steinway.append(sf_name)
        
        return available_steinway
    
    def load_steinway_soundfont(self, sf_name: str):
        """加载Steinway SoundFont"""
        print(f"🎹 加载 {sf_name}...")
        success = self.player.switch_soundfont(sf_name)
        
        if success:
            self.player.switch_instrument(0)
            print(f"✅ 成功加载 {sf_name} 并切换到钢琴音色")
            return True
        else:
            print(f"❌ 加载失败: {sf_name}")
            return False
    
    def show_presets(self):
        """显示预设值"""
        print("\n📋 PHI 预设值:")
        for name, value in PHI_PRESETS.items():
            print(f"   {name:<18}: {value:.6f}")
        
        print("\n📋 DELTA_THETA 预设值:")
        for name, value in DELTA_THETA_PRESETS.items():
            eq_div = round(360.0 / value) if value > 0 else 0
            print(f"   {name:<20}: {value:5.1f}° ({eq_div:3d}等分)")
    
    def get_phi_preset(self, input_str: str):
        """根据输入获取PHI值"""
        if not input_str:
            return None
        
        # 尝试作为数字解析
        try:
            value = float(input_str)
            if 1.0 <= value <= 5.0:  # 合理范围检查
                print(f"📝 使用PHI值: {value:.6f}")
                return value
            else:
                print(f"❌ PHI值应在1.0-5.0范围内")
                return None
        except ValueError:
            pass
        
        # 尝试作为名称解析
        if input_str in PHI_PRESETS:
            value = PHI_PRESETS[input_str]
            print(f"📝 选择PHI预设: {input_str} = {value:.6f}")
            return value
        
        print(f"❌ 无效的PHI值: {input_str}")
        print("请输入预设名称或1.0-5.0之间的数值")
        return None
    
    def get_delta_theta_preset(self, input_str: str):
        """根据输入获取DELTA_THETA值"""
        if not input_str:
            return None
        
        # 尝试作为数字解析
        try:
            value = float(input_str)
            if 0.1 <= value <= 360.0:  # 合理范围检查
                print(f"📝 使用DELTA_THETA值: {value}°")
                return value
            else:
                print(f"❌ DELTA_THETA值应在0.1-360.0度范围内")
                return None
        except ValueError:
            pass
        
        # 尝试作为名称解析
        if input_str in DELTA_THETA_PRESETS:
            value = DELTA_THETA_PRESETS[input_str]
            print(f"📝 选择DELTA_THETA预设: {input_str} = {value}°")
            return value
        
        print(f"❌ 无效的DELTA_THETA值: {input_str}")
        print("请输入预设名称或0.1-360.0之间的数值")
        return None
    
    def create_petersen_scale(self, f0, phi, delta_theta, f_min, f_max):
        """创建Petersen音阶"""
        try:
            print(f"\n🎵 创建Petersen音阶...")
            print(f"   F0: {f0} Hz")
            print(f"   PHI: {phi}")
            print(f"   DELTA_THETA: {delta_theta}°")
            print(f"   频率范围: {f_min} - {f_max} Hz")
            
            self.current_scale = PetersenScale_Phi(
                F_base=f0,
                delta_theta=delta_theta,
                phi=phi,
                F_min=f_min,
                F_max=f_max,
                reference=440.0
            )
            
            # 生成音阶数据
            entries = self.current_scale.generate()
            
            print(f"✅ 音阶创建成功!")
            
            # 显示统计信息
            self.show_scale_statistics()
            
            return True
            
        except Exception as e:
            print(f"❌ 音阶创建失败: {e}")
            return False
    
    def show_scale_statistics(self):
        """显示音阶统计信息"""
        if not self.current_scale:
            print("❌ 无当前音阶")
            return
        
        stats = self.current_scale.get_statistics()
        
        print(f"\n📊 音阶统计信息:")
        print(f"   总条目数: {stats['total_entries']}")
        print(f"   唯一频率数: {stats['unique_frequencies']}")
        print(f"   重叠频率数: {stats['frequency_overlaps']}")
        print(f"   频率范围: {stats['frequency_range'][0]:.1f} - {stats['frequency_range'][1]:.1f} Hz")
        print(f"   使用音区数: {stats['zone_count']}")
        print(f"   五行分布: {stats['elements_distribution']}")
        print(f"   极性分布: {stats['polarity_distribution']}")
        
        # 显示音区分布
        entries = self.current_scale.generate()
        zones = {}
        for entry in entries:
            zone = entry['n']
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(entry)
        
        print(f"\n🎼 音区分布:")
        for zone in sorted(zones.keys()):
            print(f"   音区{zone}: {len(zones[zone])}个音符 "
                  f"({zones[zone][0]['freq']:.1f}-{zones[zone][-1]['freq']:.1f}Hz)")
    
    def get_filter_options(self):
        """获取播放过滤选项"""
        if not self.current_scale:
            return None, None
        
        entries = self.current_scale.generate()
        
        print("\n🎵 播放选项:")
        print("1. 播放全部音符")
        print("2. 按音区过滤")
        print("3. 按五行过滤")
        print("4. 按极性过滤")
        print("5. 自定义数量限制")
        
        choice = input("选择播放方式 (1-5, 默认1): ").strip()
        
        filtered_entries = entries
        filter_desc = "全部音符"
        
        if choice == "2":
            # 按音区过滤
            zones = sorted(set(entry['n'] for entry in entries))
            print(f"可用音区: {zones}")
            zone_input = input("输入音区编号 (用逗号分隔多个): ").strip()
            if zone_input:
                try:
                    selected_zones = [int(z.strip()) for z in zone_input.split(',')]
                    filtered_entries = [e for e in entries if e['n'] in selected_zones]
                    filter_desc = f"音区{selected_zones}"
                except ValueError:
                    print("❌ 音区输入格式错误")
                    
        elif choice == "3":
            # 按五行过滤
            print(f"五行元素: {', '.join([f'{py}({cn})' for py, cn in zip(ELEMENTS_PY, ELEMENTS_CN)])}")
            element_input = input("输入五行代码 (如J,M或金,木): ").strip()
            if element_input:
                elements = [e.strip() for e in element_input.split(',')]
                # 转换中文到拼音
                converted_elements = []
                for elem in elements:
                    if elem in ELEMENTS_CN:
                        converted_elements.append(ELEMENTS_PY[ELEMENTS_CN.index(elem)])
                    elif elem in ELEMENTS_PY:
                        converted_elements.append(elem)
                
                filtered_entries = [e for e in entries if e['key_short'][0] in converted_elements]
                filter_desc = f"五行{elements}"
                
        elif choice == "4":
            # 按极性过滤
            print("极性选项: - (阴), 0 (中), + (阳)")
            polarity_input = input("输入极性 (如-,+): ").strip()
            if polarity_input:
                polarities = [p.strip() for p in polarity_input.split(',')]
                filtered_entries = [e for e in entries if e['key_short'][-1] in polarities]
                filter_desc = f"极性{polarities}"
                
        elif choice == "5":
            # 自定义数量限制
            count_input = input("输入播放音符数量: ").strip()
            if count_input:
                try:
                    count = int(count_input)
                    filtered_entries = entries[:count]
                    filter_desc = f"前{count}个音符"
                except ValueError:
                    print("❌ 数量输入错误")
        
        print(f"📝 将播放: {filter_desc} (共{len(filtered_entries)}个音符)")
        return filtered_entries, filter_desc
    
    def select_melody_pattern(self):
        """选择旋律模式"""
        print("\n🎼 旋律构建模式:")
        patterns = list(MelodyPattern)
        for i, pattern in enumerate(patterns, 1):
            print(f"   {i}. {pattern.value} - {self._get_pattern_description(pattern)}")
        
        choice = input(f"\n选择旋律模式 (1-{len(patterns)}, 默认1): ").strip()
        
        try:
            if not choice:
                choice = "1"
            index = int(choice) - 1
            if 0 <= index < len(patterns):
                return patterns[index]
            else:
                print(f"❌ 请输入 1-{len(patterns)}")
                return MelodyPattern.GENERATION
        except ValueError:
            print("❌ 请输入有效数字")
            return MelodyPattern.GENERATION
    
    def _get_pattern_description(self, pattern: MelodyPattern) -> str:
        """获取模式描述"""
        descriptions = {
            MelodyPattern.GENERATION: "五行相生关系排列 (木→火→土→金→水)",
            MelodyPattern.DESTRUCTION: "五行相克关系排列 (木→土→水→火→金)",
            MelodyPattern.BALANCE: "阴阳平衡交替排列",
            MelodyPattern.ASCENDING: "按频率从低到高排列",
            MelodyPattern.DESCENDING: "按频率从高到低排列",
            MelodyPattern.RANDOM: "随机打乱排列",
            MelodyPattern.PENTATONIC: "传统五声音阶排列 (宫商角徵羽)"
        }
        return descriptions.get(pattern, "未知模式")
    
    def build_wuxing_melody(self, entries: List[Dict], pattern: MelodyPattern) -> Tuple[List[float], List[str], List[Dict]]:
        """根据五行关系构建旋律"""
        print(f"\n🎶 构建{pattern.value}旋律...")
        
        # 按五行分组
        wuxing_groups = {'J': [], 'M': [], 'S': [], 'H': [], 'T': []}
        for entry in entries:
            element = entry['key_short'][0]
            if element in wuxing_groups:
                wuxing_groups[element].append(entry)
        
        # 显示五行分布
        print("🌿 五行音符分布:")
        for element, group in wuxing_groups.items():
            if group:
                traditional = self.traditional_names.get(element, element)
                print(f"   {element}({traditional}): {len(group)}个音符")
        
        ordered_entries = []
        
        if pattern == MelodyPattern.GENERATION:
            # 相生关系: 木→火→土→金→水
            order = ['M', 'H', 'T', 'J', 'S']
            ordered_entries = self._build_cycle_melody(wuxing_groups, order, "相生")
            
        elif pattern == MelodyPattern.DESTRUCTION:
            # 相克关系: 木→土→水→火→金
            order = ['M', 'T', 'S', 'H', 'J']
            ordered_entries = self._build_cycle_melody(wuxing_groups, order, "相克")
            
        elif pattern == MelodyPattern.BALANCE:
            # 阴阳平衡
            ordered_entries = self._build_balance_melody(entries)
            
        elif pattern == MelodyPattern.ASCENDING:
            # 频率升序
            ordered_entries = sorted(entries, key=lambda x: x['freq'])
            
        elif pattern == MelodyPattern.DESCENDING:
            # 频率降序
            ordered_entries = sorted(entries, key=lambda x: x['freq'], reverse=True)
            
        elif pattern == MelodyPattern.RANDOM:
            # 随机排列
            ordered_entries = entries.copy()
            random.shuffle(ordered_entries)
            
        elif pattern == MelodyPattern.PENTATONIC:
            # 传统五声: 宫商角徵羽
            order = ['T', 'J', 'M', 'H', 'S']  # 宫商角徵羽
            ordered_entries = self._build_cycle_melody(wuxing_groups, order, "五声")
        
        # 提取频率和名称
        frequencies = [entry['freq'] for entry in ordered_entries]
        key_names = []
        
        for entry in ordered_entries:
            element = entry['key_short'][0]
            traditional = self.traditional_names.get(element, element)
            key_names.append(f"{entry['key_short']}({traditional})")
        
        print(f"🎵 {pattern.value}旋律构建完成，共{len(frequencies)}个音符")
        
        return frequencies, key_names, ordered_entries
    
    def _build_cycle_melody(self, wuxing_groups: Dict, order: List[str], cycle_type: str) -> List[Dict]:
        """构建循环旋律"""
        print(f"🔄 按{cycle_type}关系排列: {' → '.join([f'{e}({self.traditional_names.get(e, e)})' for e in order])}")
        
        ordered_entries = []
        max_cycles = 5  # 最多循环5次
        
        for cycle in range(max_cycles):
            added_in_cycle = False
            
            for element in order:
                if element in wuxing_groups and wuxing_groups[element]:
                    # 每个元素按频率排序，每次循环取下一个
                    group = sorted(wuxing_groups[element], key=lambda x: x['freq'])
                    if cycle < len(group):
                        ordered_entries.append(group[cycle])
                        added_in_cycle = True
            
            if not added_in_cycle:
                break
        
        return ordered_entries
    
    def _build_balance_melody(self, entries: List[Dict]) -> List[Dict]:
        """构建阴阳平衡旋律"""
        print("☯️  按阴阳平衡排列")
        
        # 分离阴阳音符
        yang_notes = [e for e in entries if e['key_short'][-1] == '+']
        yin_notes = [e for e in entries if e['key_short'][-1] == '-']
        neutral_notes = [e for e in entries if e['key_short'][-1] == '0']
        
        # 按频率排序
        yang_notes = sorted(yang_notes, key=lambda x: x['freq'])
        yin_notes = sorted(yin_notes, key=lambda x: x['freq'])
        neutral_notes = sorted(neutral_notes, key=lambda x: x['freq'])
        
        print(f"   阳性音符: {len(yang_notes)}个")
        print(f"   阴性音符: {len(yin_notes)}个")
        print(f"   中性音符: {len(neutral_notes)}个")
        
        # 交替排列阴阳音符
        ordered_entries = []
        max_length = max(len(yang_notes), len(yin_notes))
        
        for i in range(max_length):
            if i < len(yang_notes):
                ordered_entries.append(yang_notes[i])
            if i < len(yin_notes):
                ordered_entries.append(yin_notes[i])
        
        # 添加中性音符
        ordered_entries.extend(neutral_notes)
        
        return ordered_entries
    
    def select_performance_style(self):
        """选择演奏风格"""
        print("\n🎨 演奏风格选项:")
        presets = list(COMPLETE_PRESET_COMBINATIONS.keys())
        for i, preset_name in enumerate(presets, 1):
            preset = COMPLETE_PRESET_COMBINATIONS[preset_name]
            print(f"   {i}. {preset.name}")
            print(f"      音效: {preset.effect_preset}, 表现力: {preset.expression_preset}")
        
        choice = input(f"\n选择演奏风格 (1-{len(presets)}, 默认1): ").strip()
        
        try:
            if not choice:
                choice = "1"
            index = int(choice) - 1
            if 0 <= index < len(presets):
                preset_name = presets[index]
                preset = COMPLETE_PRESET_COMBINATIONS[preset_name]
                
                print(f"🎨 应用演奏风格: {preset.name}")
                success = self.player.apply_preset_combination(
                    preset.effect_preset,
                    preset.expression_preset
                )
                
                if success:
                    print(f"✅ 演奏风格应用成功")
                    return True
                else:
                    print(f"❌ 演奏风格应用失败")
                    return False
            else:
                print(f"❌ 请输入 1-{len(presets)}")
                return False
        except ValueError:
            print("❌ 请输入有效数字")
            return False
    
    def get_rhythm_settings(self):
        """获取节奏设置"""
        print("\n🥁 节奏设置:")
        
        # 音符时长
        duration_input = input("基础音符时长 (秒, 默认1.0): ").strip()
        base_duration = float(duration_input) if duration_input else 1.0
        
        # 音符间隔
        gap_input = input("音符间隔 (秒, 默认0.3): ").strip()
        gap = float(gap_input) if gap_input else 0.3
        
        # 节奏变化
        print("\n节奏变化模式:")
        print("1. 均匀节拍")
        print("2. 渐快 (Accelerando)")
        print("3. 渐慢 (Ritardando)")
        print("4. 强弱交替")
        print("5. 随机变化")
        
        rhythm_choice = input("选择节奏模式 (1-5, 默认1): ").strip()
        
        return {
            'base_duration': base_duration,
            'gap': gap,
            'rhythm_mode': rhythm_choice or "1"
        }
    
    def apply_rhythm_variations(self, frequencies: List[float], rhythm_settings: Dict) -> List[Tuple[float, float]]:
        """应用节奏变化"""
        base_duration = rhythm_settings['base_duration']
        rhythm_mode = rhythm_settings['rhythm_mode']
        
        durations = []
        
        if rhythm_mode == "1":  # 均匀节拍
            durations = [base_duration] * len(frequencies)
            
        elif rhythm_mode == "2":  # 渐快
            for i in range(len(frequencies)):
                factor = 1.0 - (i / len(frequencies)) * 0.5  # 减少到50%
                durations.append(base_duration * factor)
                
        elif rhythm_mode == "3":  # 渐慢
            for i in range(len(frequencies)):
                factor = 1.0 + (i / len(frequencies)) * 0.8  # 增加到180%
                durations.append(base_duration * factor)
                
        elif rhythm_mode == "4":  # 强弱交替
            for i in range(len(frequencies)):
                factor = 1.3 if i % 2 == 0 else 0.7  # 强弱交替
                durations.append(base_duration * factor)
                
        elif rhythm_mode == "5":  # 随机变化
            for i in range(len(frequencies)):
                factor = random.uniform(0.6, 1.4)  # 随机60%-140%
                durations.append(base_duration * factor)
        
        else:
            durations = [base_duration] * len(frequencies)
        
        return list(zip(frequencies, durations))
    
    def play_melody(self):
        """播放旋律"""
        if not self.current_scale:
            print("❌ 无当前音阶")
            return False
        
        if not self.player:
            print("❌ 播放器未初始化")
            return False
        
        try:
            # 获取过滤选项
            filtered_entries, filter_desc = self.get_filter_options()
            if not filtered_entries:
                print("❌ 没有符合条件的音符")
                return False
            
            # 选择旋律模式
            melody_pattern = self.select_melody_pattern()
            
            # 构建五行旋律
            frequencies, key_names, ordered_entries = self.build_wuxing_melody(filtered_entries, melody_pattern)
            
            # 选择演奏风格
            if not self.select_performance_style():
                print("📝 使用默认演奏风格")
            
            # 获取节奏设置
            rhythm_settings = self.get_rhythm_settings()
            
            print(f"\n🎵 播放Petersen五行旋律: {filter_desc}")
            print(f"🎼 旋律模式: {melody_pattern.value}")
            print(f"🥁 节奏模式: {['均匀', '渐快', '渐慢', '强弱', '随机'][int(rhythm_settings['rhythm_mode'])-1]}")
            
            # 显示旋律序列
            print(f"\n🎶 旋律序列 ({len(frequencies)} 个音符):")
            for i, (freq, name, entry) in enumerate(zip(frequencies, key_names, ordered_entries), 1):
                element = entry['key_short'][0]
                traditional = self.traditional_names.get(element, element)
                print(f"   {i:2d}. {name} {freq:8.2f}Hz (音区{entry['n']}) - {traditional}")
            
            # 应用节奏变化
            freq_duration_pairs = self.apply_rhythm_variations(frequencies, rhythm_settings)
            
            # 播放旋律
            print(f"\n🎵 开始播放旋律...")
            
            for i, (freq, duration) in enumerate(freq_duration_pairs):
                name = key_names[i]
                
                print(f"🎵 {i+1}/{len(freq_duration_pairs)}: {name} ({freq:.1f}Hz, {duration:.2f}s)")
                
                # 播放单个音符
                success = self.player.play_frequencies(
                    [freq], 
                    [name],
                    duration=duration,
                    gap=rhythm_settings['gap'],
                    use_accurate_frequency=True
                )
                
                if not success:
                    print(f"❌ 播放音符 {name} 失败")
                    return False
                
                # 短暂停顿以便听清每个音符
                time.sleep(rhythm_settings['gap'])
            
            print("✅ 五行旋律播放完成")
            
            # 询问是否重复播放或尝试其他模式
            repeat_choice = input("\n是否尝试其他旋律模式? (y/n, 默认n): ").strip().lower()
            if repeat_choice == 'y':
                return self.play_melody()
            
            return True
                
        except Exception as e:
            print(f"❌ 播放失败: {e}")
            return False
    
    def run(self):
        """运行主程序"""
        print("🎵 Petersen音阶五行旋律构建系统")
        print("=" * 50)
        
        # 初始化播放器
        if not self.initialize_player():
            return
        
        # 检查是否需要切换SoundFont
        if not self.check_soundfont_switch():
            return
        
        # 主循环
        while True:
            print("\n" + "=" * 50)
            print("🎵 Petersen音阶参数设置")
            
            try:
                # 输入基础频率F0 (必填)
                while True:
                    f0_input = input("输入基础频率F0 (Hz): ").strip()
                    if f0_input:
                        try:
                            f0 = float(f0_input)
                            if 10.0 <= f0 <= 1000.0:  # 合理范围
                                break
                            else:
                                print("❌ F0应在10-1000Hz范围内")
                        except ValueError:
                            print("❌ 请输入有效的数字")
                    else:
                        print("❌ F0是必填项")
                
                # 显示预设并选择PHI (必填)
                self.show_presets()
                while True:
                    phi_input = input("\n输入PHI值 (预设名称或数值): ").strip()
                    if phi_input:
                        phi = self.get_phi_preset(phi_input)
                        if phi is not None:
                            break
                    else:
                        print("❌ PHI是必填项")
                
                # 选择DELTA_THETA (必填)
                while True:
                    delta_theta_input = input("输入DELTA_THETA值 (预设名称或数值): ").strip()
                    if delta_theta_input:
                        delta_theta = self.get_delta_theta_preset(delta_theta_input)
                        if delta_theta is not None:
                            break
                    else:
                        print("❌ DELTA_THETA是必填项")
                
                # 输入频率范围
                f_min_input = input("输入最小频率 (Hz, 默认30): ").strip()
                f_min = float(f_min_input) if f_min_input else 30.0
                
                f_max_input = input("输入最大频率 (Hz, 默认6000): ").strip()
                f_max = float(f_max_input) if f_max_input else 6000.0
                
                # 创建音阶
                if self.create_petersen_scale(f0, phi, delta_theta, f_min, f_max):
                    # 询问是否播放
                    play_choice = input("\n是否播放五行旋律? (y/n, 默认y): ").strip().lower()
                    if play_choice != 'n':
                        self.play_melody()
                
                # 询问是否继续
                continue_choice = input("\n是否继续测试其他参数? (y/n, 默认y): ").strip().lower()
                if continue_choice == 'n':
                    break
                    
            except ValueError as e:
                print(f"❌ 输入错误: {e}")
            except KeyboardInterrupt:
                print("\n👋 程序被中断")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
        
        # 清理
        if self.player:
            self.player.cleanup()
        
        print("👋 谢谢使用!")

if __name__ == "__main__":
    demo = PetersenScaleDemo()
    demo.run()