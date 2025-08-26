"""
交互式演示程序
提供命令行交互界面，让用户自由探索所有功能
"""
import cmd
import sys
import time
import math
from pathlib import Path
from typing import List, Optional

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from enhanced_petersen_player import create_player, PlayerConfiguration
from utils.presets import COMPLETE_PRESET_COMBINATIONS

class PetersenPlayerCLI(cmd.Cmd):
    """Enhanced Petersen Player 交互式命令行界面"""
    
    intro = '''
🎵 欢迎使用 Enhanced Petersen Music System 交互式演示!
📖 输入 'help' 查看可用命令，输入 'quit' 退出程序
🎹 祝您音乐探索愉快!
'''
    prompt = '🎵 Petersen Player > '
    
    def __init__(self):
        super().__init__()
        self.player = None
        self.current_frequencies = []
        self.current_names = []
        self._initialize_player()
    
    def _initialize_player(self):
        """初始化播放器"""
        try:
            print("🔄 正在初始化播放器...")
            self.player = create_player()
            print("✅ 播放器初始化成功!")
        except Exception as e:
            print(f"❌ 播放器初始化失败: {e}")
            self.player = None
    
    def do_status(self, arg):
        """显示系统状态"""
        if not self.player:
            print("❌ 播放器未初始化")
            return
        
        status = self.player.get_system_status()
        print("\n📊 系统状态:")
        print(f"   状态: {status['status']}")
        print(f"   运行时间: {status['runtime_seconds']:.1f}秒")
        
        stats = status['session_stats']
        print(f"\n📈 播放统计:")
        print(f"   已播放音符: {stats['notes_played']}")
        print(f"   播放序列数: {stats['sequences_played']}")
        print(f"   总播放时长: {stats['total_play_time']:.1f}秒")
        print(f"   已加载SoundFont: {stats['soundfonts_loaded']}")
        
        sf_summary = status['soundfont_summary']
        print(f"\n📁 SoundFont信息:")
        print(f"   总数: {sf_summary['total_soundfonts']}")
        print(f"   当前: {sf_summary.get('current_soundfont', '无')}")
    
    def do_soundfonts(self, arg):
        """显示可用SoundFont列表"""
        if not self.player:
            print("❌ 播放器未初始化")
            return
        
        sf_summary = self.player.sf_manager.get_soundfont_summary()
        soundfonts = sf_summary['soundfont_details']
        
        print(f"\n📁 可用SoundFont ({len(soundfonts)} 个):")
        for i, (name, details) in enumerate(soundfonts.items(), 1):
            current = "⭐" if name == sf_summary.get('current_soundfont') else "  "
            print(f"{current}{i:2d}. {name}")
            print(f"      类型: {details['type']}, 大小: {details['size_mb']:.1f}MB")
            print(f"      质量: {details['quality_score']:.2f}, 乐器: {details['instrument_count']}")
            print(f"      推荐: {details['recommended_use']}")
    
    def do_load_sf(self, arg):
        """加载SoundFont: load_sf <文件名或编号>"""
        if not self.player:
            print("❌ 播放器未初始化")
            return
        
        if not arg:
            print("请指定SoundFont文件名或编号")
            return
        
        # 获取SoundFont列表
        sf_summary = self.player.sf_manager.get_soundfont_summary()
        soundfonts = list(sf_summary['soundfont_details'].keys())
        
        # 尝试按编号解析
        try:
            index = int(arg) - 1
            if 0 <= index < len(soundfonts):
                sf_name = soundfonts[index]
            else:
                print(f"编号超出范围 (1-{len(soundfonts)})")
                return
        except ValueError:
            sf_name = arg
        
        print(f"🔄 正在加载: {sf_name}")
        success = self.player.switch_soundfont(sf_name)
        
        if success:
            print(f"✅ SoundFont加载成功: {sf_name}")
        else:
            print(f"❌ SoundFont加载失败: {sf_name}")
    
    def do_instruments(self, arg):
        """显示当前SoundFont的乐器列表"""
        if not self.player:
            print("❌ 播放器未初始化")
            return
        
        instruments = self.player.sf_manager.get_available_instruments()
        if not instruments:
            print("❌ 未找到可用乐器，请先加载SoundFont")
            return
        
        print(f"\n🎼 可用乐器 ({len(instruments)} 个):")
        
        # 按类别分组显示
        categories = {}
        for inst in instruments:
            if inst.category not in categories:
                categories[inst.category] = []
            categories[inst.category].append(inst)
        
        for category, insts in sorted(categories.items()):
            print(f"\n📂 {category}:")
            for inst in insts[:5]:  # 每类最多显示5个
                print(f"   {inst.program:3d}. {inst.name} (质量: {inst.sample_quality})")
    
    def do_switch_inst(self, arg):
        """切换乐器: switch_inst <程序号>"""
        if not self.player:
            print("❌ 播放器未初始化")
            return
        
        if not arg:
            print("请指定MIDI程序号 (0-127)")
            return
        
        try:
            program = int(arg)
            success = self.player.switch_instrument(program)
            if success:
                print(f"✅ 乐器切换成功: 程序 {program}")
            else:
                print(f"❌ 乐器切换失败: 程序 {program}")
        except ValueError:
            print("请输入有效的程序号")
    
    def do_presets(self, arg):
        """显示可用预设列表"""
        print("\n🎨 可用完整预设:")
        for i, (name, preset) in enumerate(COMPLETE_PRESET_COMBINATIONS.items(), 1):
            print(f"{i:2d}. {preset.name}")
            print(f"     {preset.description}")
            print(f"     用途: {', '.join(preset.use_cases)}")
    
    def do_apply_preset(self, arg):
        """应用预设: apply_preset <预设名或编号>"""
        if not self.player:
            print("❌ 播放器未初始化")
            return
        
        if not arg:
            print("请指定预设名称或编号")
            return
        
        presets = list(COMPLETE_PRESET_COMBINATIONS.keys())
        
        # 尝试按编号解析
        try:
            index = int(arg) - 1
            if 0 <= index < len(presets):
                preset_name = presets[index]
            else:
                print(f"编号超出范围 (1-{len(presets)})")
                return
        except ValueError:
            preset_name = arg
        
        preset = COMPLETE_PRESET_COMBINATIONS[preset_name]
        print(f"🎨 正在应用预设: {preset.name}")
        
        success = self.player.apply_preset_combination(
            preset.effect_preset,
            preset.expression_preset
        )
        
        if success:
            print(f"✅ 预设应用成功")
        else:
            print(f"❌ 预设应用失败")
    
    def do_play_scale(self, arg):
        """播放音阶: play_scale [c|d|e|f|g|a|b] [major|minor]"""
        if not self.player:
            print("❌ 播放器未初始化")
            return
        
        # 解析参数
        parts = arg.split() if arg else ['c', 'major']
        root = parts[0].lower() if len(parts) > 0 else 'c'
        scale_type = parts[1].lower() if len(parts) > 1 else 'major'
        
        # 生成音阶
        frequencies, names = self._generate_scale(root, scale_type)
        
        if not frequencies:
            print("❌ 音阶生成失败")
            return
        
        print(f"🎵 播放 {root.upper()} {scale_type} 音阶:")
        for freq, name in zip(frequencies, names):
            print(f"   {name}: {freq:.2f}Hz")
        
        self.current_frequencies = frequencies
        self.current_names = names
        
        success = self.player.play_frequencies(frequencies, names)
        if success:
            print("✅ 音阶播放完成")
        else:
            print("❌ 音阶播放失败")
    
    def do_play_chord(self, arg):
        """播放和弦: play_chord [c|d|e|f|g|a|b] [major|minor|dim|aug]"""
        if not self.player:
            print("❌ 播放器未初始化")
            return
        
        # 解析参数
        parts = arg.split() if arg else ['c', 'major']
        root = parts[0].lower() if len(parts) > 0 else 'c'
        chord_type = parts[1].lower() if len(parts) > 1 else 'major'
        
        # 生成和弦
        frequencies, names = self._generate_chord(root, chord_type)
        
        if not frequencies:
            print("❌ 和弦生成失败")
            return
        
        print(f"🎵 播放 {root.upper()} {chord_type} 和弦:")
        for freq, name in zip(frequencies, names):
            print(f"   {name}: {freq:.2f}Hz")
        
        # 同时播放所有音符（和弦效果）
        success = self.player.play_frequencies(frequencies, names, gap=0.0)
        if success:
            print("✅ 和弦播放完成")
        else:
            print("❌ 和弦播放失败")
    
    def do_demo(self, arg):
        """运行演示: demo [basic|advanced|comparison|educational]"""
        if not self.player:
            print("❌ 播放器未初始化")
            return
        
        demo_type = arg.lower() if arg else 'basic'
        
        if demo_type == 'basic':
            self._demo_basic()
        elif demo_type == 'advanced':
            self._demo_advanced()
        elif demo_type == 'comparison':
            self._demo_comparison()
        elif demo_type == 'educational':
            self._demo_educational()
        else:
            print("可用演示类型: basic, advanced, comparison, educational")
    
    def do_quit(self, arg):
        """退出程序"""
        print("👋 感谢使用 Enhanced Petersen Music System!")
        if self.player:
            self.player.cleanup()
        return True
    
    def _generate_scale(self, root, scale_type):
        """生成音阶"""
        # 基础频率映射
        note_frequencies = {
            'c': 261.63, 'd': 293.66, 'e': 329.63, 'f': 349.23,
            'g': 392.00, 'a': 440.00, 'b': 493.88
        }
        
        if root not in note_frequencies:
            return [], []
        
        base_freq = note_frequencies[root]
        
        # 音阶间隔（半音）
        if scale_type == 'major':
            intervals = [0, 2, 4, 5, 7, 9, 11, 12]  # 大调
        elif scale_type == 'minor':
            intervals = [0, 2, 3, 5, 7, 8, 10, 12]  # 小调
        else:
            return [], []
        
        frequencies = []
        names = []
        
        for i, interval in enumerate(intervals):
            freq = base_freq * (2 ** (interval / 12))
            frequencies.append(freq)
            names.append(f"{root.upper()}{scale_type[0].upper()}{i+1}")
        
        return frequencies, names
    
    def _generate_chord(self, root, chord_type):
        """生成和弦"""
        note_frequencies = {
            'c': 261.63, 'd': 293.66, 'e': 329.63, 'f': 349.23,
            'g': 392.00, 'a': 440.00, 'b': 493.88
        }
        
        if root not in note_frequencies:
            return [], []
        
        base_freq = note_frequencies[root]
        
        # 和弦间隔（半音）
        if chord_type == 'major':
            intervals = [0, 4, 7]  # 大三和弦
        elif chord_type == 'minor':
            intervals = [0, 3, 7]  # 小三和弦
        elif chord_type == 'dim':
            intervals = [0, 3, 6]  # 减三和弦
        elif chord_type == 'aug':
            intervals = [0, 4, 8]  # 增三和弦
        else:
            return [], []
        
        frequencies = []
        names = []
        
        for i, interval in enumerate(intervals):
            freq = base_freq * (2 ** (interval / 12))
            frequencies.append(freq)
            names.append(f"{root.upper()}{chord_type}{i+1}")
        
        return frequencies, names
    
    def _demo_basic(self):
        """基础演示"""
        print("\n🎵 基础功能演示:")
        
        # C大调音阶
        frequencies, names = self._generate_scale('c', 'major')
        print("播放C大调音阶...")
        self.player.play_frequencies(frequencies, names)
        
        time.sleep(1)
        
        # C大三和弦
        frequencies, names = self._generate_chord('c', 'major')
        print("播放C大三和弦...")
        self.player.play_frequencies(frequencies, names, gap=0.0)
    
    def _demo_advanced(self):
        """高级功能演示"""
        print("\n🎛️  高级功能演示:")
        
        # 应用不同预设
        presets = list(COMPLETE_PRESET_COMBINATIONS.keys())[:3]
        frequencies, names = self._generate_scale('c', 'major')
        
        for preset_name in presets:
            preset = COMPLETE_PRESET_COMBINATIONS[preset_name]
            print(f"\n应用预设: {preset.name}")
            
            self.player.apply_preset_combination(
                preset.effect_preset, preset.expression_preset
            )
            
            self.player.play_frequencies(frequencies[:5], names[:5])
            time.sleep(1)
    
    def _demo_comparison(self):
        """对比演示"""
        print("\n🔄 对比演示:")
        
        frequencies, names = self._generate_scale('c', 'major')
        success = self.player.demonstrate_frequency_accuracy(frequencies, names)
        
        if success:
            print("✅ 频率精确度对比完成")
        else:
            print("❌ 对比演示失败")
    
    def _demo_educational(self):
        """教育演示"""
        print("\n📚 教育功能演示:")
        
        frequencies, names = self._generate_scale('c', 'major')
        
        # 教育模式演示
        success = self.player.performance_modes.execute_educational_mode(
            frequencies, names, "basic_theory"
        )
        
        if success:
            print("✅ 教育演示完成")
        else:
            print("❌ 教育演示失败")

def main():
    """主函数"""
    try:
        cli = PetersenPlayerCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")

if __name__ == "__main__":
    main()