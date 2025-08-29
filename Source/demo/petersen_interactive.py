#!/usr/bin/env python3
"""
Petersen音阶交互式演示程序
简化版本，专注于音阶生成和播放测试
"""
import sys
from pathlib import Path

# 添加路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(current_dir))

from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
from enhanced_petersen_player import create_player, PlayerConfiguration

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
    
    def list_available_soundfonts(self):
        """列出可用的Steinway SoundFont"""
        if not self.player:
            print("❌ 播放器未初始化")
            return []
        
        sf_summary = self.player.sf_manager.get_soundfont_summary()
        available_steinway = []
        
        for sf_name in self.steinway_files:
            if sf_name in sf_summary['soundfont_details']:
                available_steinway.append(sf_name)
        
        return available_steinway
    
    def load_steinway_soundfont(self, sf_name: str = None):
        """加载Steinway SoundFont"""
        if not self.player:
            print("❌ 播放器未初始化")
            return False
        
        available = self.list_available_soundfonts()
        if not available:
            print("❌ 未找到Steinway SoundFont文件")
            return False
        
        if sf_name is None:
            sf_name = available[0]  # 使用第一个可用的
        
        if sf_name not in available:
            print(f"❌ SoundFont {sf_name} 不可用")
            print(f"可用文件: {available}")
            return False
        
        print(f"🎹 加载 {sf_name}...")
        success = self.player.switch_soundfont(sf_name)
        
        if success:
            # 切换到钢琴音色 (程序0)
            self.player.switch_instrument(0)
            print(f"✅ 成功加载 {sf_name} 并切换到钢琴音色")
            return True
        else:
            print(f"❌ 加载失败: {sf_name}")
            return False
    
    def show_presets(self):
        """显示预设值"""
        print("\n📋 PHI 预设值:")
        for i, (name, value) in enumerate(PHI_PRESETS.items(), 1):
            cents_per_zone = 1200 * (value ** (1/12) - 1) * 12  # 近似音分
            print(f"  {i:2d}. {name:<15}: {value:.6f} ({cents_per_zone:6.1f} cents/zone)")
        
        print("\n📋 DELTA_THETA 预设值:")
        for i, (name, value) in enumerate(DELTA_THETA_PRESETS.items(), 1):
            eq_div = round(360.0 / value) if value > 0 else 0
            print(f"  {i:2d}. {name:<20}: {value:5.1f}° ({eq_div:3d}等分)")
    
    def get_phi_preset(self, input_str: str):
        """根据输入获取PHI值"""
        try:
            # 尝试作为数字解析
            return float(input_str)
        except ValueError:
            pass
        
        # 尝试作为编号解析
        try:
            index = int(input_str) - 1
            presets = list(PHI_PRESETS.items())
            if 0 <= index < len(presets):
                name, value = presets[index]
                print(f"📝 选择PHI预设: {name} = {value:.6f}")
                return value
        except ValueError:
            pass
        
        # 尝试作为名称解析
        if input_str in PHI_PRESETS:
            value = PHI_PRESETS[input_str]
            print(f"📝 选择PHI预设: {input_str} = {value:.6f}")
            return value
        
        print(f"❌ 无效的PHI值: {input_str}")
        return None
    
    def get_delta_theta_preset(self, input_str: str):
        """根据输入获取DELTA_THETA值"""
        try:
            # 尝试作为数字解析
            return float(input_str)
        except ValueError:
            pass
        
        # 尝试作为编号解析
        try:
            index = int(input_str) - 1
            presets = list(DELTA_THETA_PRESETS.items())
            if 0 <= index < len(presets):
                name, value = presets[index]
                print(f"📝 选择DELTA_THETA预设: {name} = {value}°")
                return value
        except ValueError:
            pass
        
        # 尝试作为名称解析
        if input_str in DELTA_THETA_PRESETS:
            value = DELTA_THETA_PRESETS[input_str]
            print(f"📝 选择DELTA_THETA预设: {input_str} = {value}°")
            return value
        
        print(f"❌ 无效的DELTA_THETA值: {input_str}")
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
        
        # 显示前几个频率
        entries = self.current_scale.generate()
        print(f"\n🎼 前10个音符:")
        for i, entry in enumerate(entries[:10]):
            print(f"   {i+1:2d}. {entry['key_short']:<4} {entry['key_long']:<6} "
                  f"{entry['freq']:8.2f}Hz (音区{entry['n']})")
    
    def play_scale(self):
        """播放当前音阶"""
        if not self.current_scale:
            print("❌ 无当前音阶")
            return False
        
        if not self.player:
            print("❌ 播放器未初始化")
            return False
        
        try:
            print(f"\n🎵 播放Petersen音阶...")
            
            # 获取频率列表
            frequencies = self.current_scale.frequencies_only()
            
            # 限制播放数量（避免太长）
            max_notes = 24
            if len(frequencies) > max_notes:
                frequencies = frequencies[:max_notes]
                print(f"📝 限制播放前{max_notes}个音符")
            
            # 生成音名
            entries = self.current_scale.generate()
            key_names = [entry['key_short'] for entry in entries[:len(frequencies)]]
            
            print(f"播放 {len(frequencies)} 个音符:")
            for freq, name in zip(frequencies, key_names):
                print(f"   {name}: {freq:.1f}Hz")
            
            # 播放音阶
            success = self.player.play_frequencies(
                frequencies, 
                key_names,
                duration=0.8,
                gap=0.2
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
        print("🎵 Petersen音阶交互式演示程序")
        print("=" * 50)
        
        # 初始化播放器
        if not self.initialize_player():
            return
        
        # 加载SoundFont
        available_sf = self.list_available_soundfonts()
        if not available_sf:
            print("❌ 未找到Steinway SoundFont文件")
            return
        
        print(f"\n📁 可用SoundFont:")
        for i, sf in enumerate(available_sf, 1):
            print(f"   {i}. {sf}")
        
        # 选择SoundFont
        while True:
            try:
                choice = input(f"\n选择SoundFont (1-{len(available_sf)}, 默认1): ").strip()
                if not choice:
                    choice = "1"
                
                index = int(choice) - 1
                if 0 <= index < len(available_sf):
                    if self.load_steinway_soundfont(available_sf[index]):
                        break
                else:
                    print(f"❌ 请输入 1-{len(available_sf)}")
            except ValueError:
                print("❌ 请输入有效数字")
        
        # 主循环
        while True:
            print("\n" + "=" * 50)
            print("🎵 Petersen音阶参数设置")
            
            try:
                # 输入基础频率F0
                f0_input = input("输入基础频率F0 (Hz, 默认55): ").strip()
                f0 = float(f0_input) if f0_input else 55.0
                
                # 显示预设并选择PHI
                self.show_presets()
                phi_input = input("\n输入PHI值 (数字/编号/名称, 默认golden): ").strip()
                phi = self.get_phi_preset(phi_input if phi_input else "golden")
                if phi is None:
                    continue
                
                # 选择DELTA_THETA
                delta_theta_input = input("输入DELTA_THETA值 (数字/编号/名称, 默认petersen_original): ").strip()
                delta_theta = self.get_delta_theta_preset(delta_theta_input if delta_theta_input else "petersen_original")
                if delta_theta is None:
                    continue
                
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