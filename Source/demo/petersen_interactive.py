#!/usr/bin/env python3
"""
Petersen音阶交互式演示程序
增强版本，支持音阶过滤、表现力和音效控制
"""
import sys
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(current_dir))

from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS, ELEMENTS_CN, ELEMENTS_PY
from enhanced_petersen_player import create_player, PlayerConfiguration
from utils.presets import COMPLETE_PRESET_COMBINATIONS

class PetersenScaleDemo:
    """Petersen音阶演示类"""
    
    def __init__(self):
        self.player = None
        self.current_scale = None
        self.steinway_files = [
            'GD_Steinway_Model_D274.sf2',
            'GD_Steinway_Model_D274II.sf2'
        ]
        
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
    
    def play_scale(self):
        """播放当前音阶"""
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
            
            # 选择演奏风格
            if not self.select_performance_style():
                print("📝 使用默认演奏风格")
            
            print(f"\n🎵 播放Petersen音阶: {filter_desc}")
            
            # 提取频率和音名
            frequencies = [entry['freq'] for entry in filtered_entries]
            key_names = [entry['key_short'] for entry in filtered_entries]
            
            print(f"播放 {len(frequencies)} 个音符:")
            for i, (freq, name, entry) in enumerate(zip(frequencies, key_names, filtered_entries), 1):
                print(f"   {i:2d}. {name:<4} {entry['key_long']:<8} {freq:8.2f}Hz (音区{entry['n']})")
            
            # 询问播放参数
            duration_input = input("\n音符时长 (秒, 默认0.8): ").strip()
            duration = float(duration_input) if duration_input else 0.8
            
            gap_input = input("音符间隔 (秒, 默认0.2): ").strip()
            gap = float(gap_input) if gap_input else 0.2
            
            # 播放音阶
            success = self.player.play_frequencies(
                frequencies, 
                key_names,
                duration=duration,
                gap=gap
            )
            
            if success:
                print("✅ 音阶播放完成")
                return True
            else:
                print("❌ 音阶播放失败")
                return False
                
        except Exception as e:
            print(f"❌ 播放失败: {e}")
            return False
    
    def run(self):
        """运行主程序"""
        print("🎵 Petersen音阶交互式演示程序 (增强版)")
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
                    play_choice = input("\n是否播放音阶? (y/n, 默认y): ").strip().lower()
                    if play_choice != 'n':
                        self.play_scale()
                
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