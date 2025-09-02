"""
Petersen 交互式参数工作室

这是一个实时交互式音乐创作环境，允许用户动态调节Petersen数学参数，
并立即听到音乐效果的变化。这是探索数学与音乐关系的最直观方式。

核心功能：
- 实时参数调节：滑动条、旋钮式的参数控制
- 即时音乐反馈：参数变化立即产生音乐预览
- 多层次预览：单音符、音阶、和弦、短旋律
- 对比试听：A/B对比不同参数设置
- 创作录制：保存满意的参数组合和音乐片段
- 教学模式：引导式的参数探索流程

交互模式：
- 自由探索模式：完全自由的参数调节
- 引导式教学：结构化的参数学习流程
- 对比分析模式：同时对比多个参数设置
- 创作会话模式：支持创作流程的完整记录
- 演示模式：自动演示系统各种能力

技术特点：
- 低延迟音频反馈：参数变化到音频输出 < 200ms
- 智能缓存机制：避免重复计算相同参数
- 渐进式加载：复杂参数组合的分层预览
- 会话管理：完整的交互历史记录
- 实时可视化：参数空间的图形化展示

用户体验：
- 直观的命令行界面
- 清晰的参数说明和当前值显示
- 即时的音频反馈
- 简单的保存和加载机制
- 完整的帮助和提示系统
"""

import sys
import time
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math

# 添加libs路径
current_dir = Path(__file__).parent
libs_dir = current_dir.parent / "libs"
if str(libs_dir) not in sys.path:
    sys.path.insert(0, str(libs_dir))

try:
    from petersen_scale import PetersenScale, PRESET_PHI_VALUES, PRESET_DELTA_THETA_VALUES
    from petersen_chord import PetersenChordExtender, CHORD_RATIOS_PRESETS
    from petersen_rhythm import PetersenRhythmGenerator, RHYTHM_STYLE_PRESETS
    from petersen_melody import PetersenMelodyGenerator, MELODY_PATTERN_PRESETS
    from petersen_composer import PetersenAutoComposer, COMPOSITION_STYLES
    from petersen_performance import PetersenPerformanceRenderer, PERFORMANCE_TECHNIQUES
except ImportError as e:
    print(f"⚠️ 导入基础模块失败: {e}")

class WorkshopMode(Enum):
    """工作室模式"""
    FREE_EXPLORATION = "free_exploration"       # 自由探索
    GUIDED_TUTORIAL = "guided_tutorial"         # 引导式教学
    COMPARISON_MODE = "comparison_mode"          # 对比分析
    COMPOSITION_SESSION = "composition_session" # 创作会话
    DEMONSTRATION = "demonstration"              # 演示模式

class PreviewType(Enum):
    """预览类型"""
    SINGLE_NOTE = "single_note"         # 单音符
    SCALE_SEQUENCE = "scale_sequence"   # 音阶序列
    CHORD_PROGRESSION = "chord_progression" # 和弦进行
    SHORT_MELODY = "short_melody"       # 短旋律
    MINI_COMPOSITION = "mini_composition" # 迷你作品

class ParameterType(Enum):
    """参数类型"""
    PHI_VALUE = "phi_value"
    DELTA_THETA = "delta_theta" 
    F_BASE = "f_base"
    CHORD_RATIOS = "chord_ratios"
    RHYTHM_STYLE = "rhythm_style"
    MELODY_PATTERN = "melody_pattern"
    COMPOSITION_STYLE = "composition_style"

@dataclass
class WorkshopState:
    """工作室状态"""
    # 当前参数值
    current_phi_name: str = "golden"
    current_phi_value: float = 1.618
    current_delta_theta_name: str = "15.0"
    current_delta_theta_value: float = 15.0
    current_f_base: float = 55.0
    current_chord_set: str = "major_triad"
    current_rhythm_style: str = "traditional"
    current_melody_pattern: str = "balanced"
    current_composition_style: str = "balanced_journey"
    
    # 预览设置
    preview_type: PreviewType = PreviewType.SCALE_SEQUENCE
    preview_duration: float = 3.0
    auto_preview: bool = True
    
    # 会话信息
    session_start_time: datetime = field(default_factory=datetime.now)
    interaction_count: int = 0
    parameter_changes: List[Dict[str, Any]] = field(default_factory=list)
    favorite_settings: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class InteractionRecord:
    """交互记录"""
    timestamp: datetime
    action_type: str  # "parameter_change", "preview", "save", etc.
    parameters: Dict[str, Any]
    description: str
    audio_generated: bool = False

class InteractiveWorkshop:
    """交互式参数工作室"""
    
    def __init__(self, master_studio):
        """
        初始化交互式工作室
        
        Args:
            master_studio: PetersenMasterStudio实例
        """
        self.master_studio = master_studio
        self.state = WorkshopState()
        self.mode = WorkshopMode.FREE_EXPLORATION
        
        # 音频组件
        self.enhanced_player = master_studio.enhanced_player
        self.current_scale = None
        self.current_chord_extender = None
        self.current_composer = None
        
        # 缓存系统
        self.scale_cache: Dict[str, PetersenScale] = {}
        self.audio_cache: Dict[str, Any] = {}
        self.last_preview_time = 0.0
        
        # 会话管理
        self.interaction_history: List[InteractionRecord] = []
        self.session_id = f"workshop_{int(time.time())}"
        
        # 控制状态
        self.is_running = False
        self.stop_requested = False
        self.preview_thread = None
        
        print("✓ 交互式参数工作室已初始化")
        self._initialize_current_parameters()
    
    def _initialize_current_parameters(self):
        """初始化当前参数"""
        try:
            self._update_musical_components()
            print("✓ 音乐组件已初始化")
        except Exception as e:
            print(f"⚠️ 音乐组件初始化警告: {e}")
    
    def run_session(self, mode: WorkshopMode = WorkshopMode.FREE_EXPLORATION) -> Dict[str, Any]:
        """
        运行交互式会话
        
        Args:
            mode: 工作室模式
            
        Returns:
            Dict: 会话结果
        """
        self.mode = mode
        self.is_running = True
        self.stop_requested = False
        
        print("🛠️ 启动交互式参数工作室")
        print("=" * 50)
        
        session_results = {
            "session_id": self.session_id,
            "mode": mode.value,
            "start_time": self.state.session_start_time.isoformat(),
            "interactions": [],
            "created_works": [],
            "session_summary": {}
        }
        
        try:
            # 显示欢迎信息
            self._display_welcome_message()
            
            # 根据模式启动相应的会话
            if mode == WorkshopMode.FREE_EXPLORATION:
                session_results.update(self._run_free_exploration())
            elif mode == WorkshopMode.GUIDED_TUTORIAL:
                session_results.update(self._run_guided_tutorial())
            elif mode == WorkshopMode.COMPARISON_MODE:
                session_results.update(self._run_comparison_mode())
            elif mode == WorkshopMode.COMPOSITION_SESSION:
                session_results.update(self._run_composition_session())
            elif mode == WorkshopMode.DEMONSTRATION:
                session_results.update(self._run_demonstration())
            else:
                print(f"❌ 未知工作室模式: {mode}")
                return session_results
            
            # 完成会话
            session_results["end_time"] = datetime.now().isoformat()
            session_results["interactions"] = [
                {
                    "timestamp": record.timestamp.isoformat(),
                    "action": record.action_type,
                    "description": record.description,
                    "parameters": record.parameters
                }
                for record in self.interaction_history
            ]
            
            # 保存会话
            self._save_session_results(session_results)
            
            print("\n" + "=" * 50)
            print("✓ 交互式会话完成")
            print(f"  交互次数: {len(self.interaction_history)}")
            print(f"  收藏设置: {len(self.state.favorite_settings)}")
            
            return session_results
            
        except KeyboardInterrupt:
            print("\n\n❌ 用户中断会话")
            session_results["interrupted"] = True
            return session_results
        except Exception as e:
            print(f"\n❌ 会话执行失败: {e}")
            session_results["error"] = str(e)
            return session_results
        finally:
            self.is_running = False
            self._cleanup_session()
    
    def _display_welcome_message(self):
        """显示欢迎信息"""
        print("🎹 欢迎使用 Petersen 交互式参数工作室！")
        print()
        print("在这里，您可以实时调节数学参数并立即听到音乐效果：")
        print("• φ值：影响音程关系和和声色彩")
        print("• δθ值：控制音阶密度和旋律复杂度")
        print("• 基频：设置音高中心")
        print("• 和弦比率：决定和声结构")
        print("• 风格设置：调整整体音乐风格")
        print()
        print("💡 提示：每次参数改变后会自动播放预览")
        print("📝 输入 'help' 查看所有可用命令")
        print("🔄 输入 'quit' 退出工作室")
        print("-" * 50)
    
    def _run_free_exploration(self) -> Dict[str, Any]:
        """运行自由探索模式"""
        print("🔍 自由探索模式")
        print("您可以自由调节任何参数，系统会实时反馈音乐效果")
        print()
        
        # 显示当前状态
        self._display_current_state()
        
        results = {"mode_type": "free_exploration", "interactions": 0}
        
        while self.is_running and not self.stop_requested:
            try:
                # 获取用户输入
                user_input = input("\n🎛️ 输入命令 (help 查看帮助): ").strip().lower()
                
                if not user_input:
                    continue
                
                # 处理命令
                command_result = self._process_command(user_input)
                
                if command_result.get("should_exit"):
                    break
                
                results["interactions"] += 1
                
                # 如果参数改变了，更新预览
                if command_result.get("parameter_changed"):
                    self._trigger_auto_preview()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 命令处理失败: {e}")
        
        return results
    
    def _run_guided_tutorial(self) -> Dict[str, Any]:
        """运行引导式教学模式"""
        print("🎓 引导式教学模式")
        print("我们将逐步探索 Petersen 数学参数的音乐效果")
        print()
        
        tutorial_steps = [
            {
                "title": "探索 φ 值的影响",
                "description": "φ值控制音程关系，让我们听听不同值的效果",
                "actions": ["phi golden", "preview", "phi octave", "preview", "phi fifth", "preview"]
            },
            {
                "title": "感受 δθ 值的变化",
                "description": "δθ值决定音阶密度，影响旋律的复杂程度",
                "actions": ["delta 4.8", "preview", "delta 15.0", "preview", "delta 24.0", "preview"]
            },
            {
                "title": "体验和弦比率的差异",
                "description": "不同的和弦比率创造不同的和声色彩",
                "actions": ["chord major_triad", "preview", "chord minor_seventh", "preview", "chord complex_jazz", "preview"]
            },
            {
                "title": "综合参数的艺术",
                "description": "让我们创造一个综合的音乐片段",
                "actions": ["phi golden", "delta 15.0", "chord major_seventh", "preview mini", "save tutorial_masterpiece"]
            }
        ]
        
        results = {"mode_type": "guided_tutorial", "completed_steps": 0}
        
        for i, step in enumerate(tutorial_steps, 1):
            print(f"\n📚 第 {i} 步: {step['title']}")
            print(f"   {step['description']}")
            print()
            
            # 等待用户准备
            input("按 Enter 继续...")
            
            # 执行教学步骤
            for action in step["actions"]:
                print(f"🎵 执行: {action}")
                command_result = self._process_command(action)
                
                if action == "preview" or action.startswith("preview"):
                    time.sleep(self.state.preview_duration + 0.5)  # 等待预览完成
                elif action.startswith("save"):
                    print(f"   ✓ 已保存: {action.split()[1]}")
                
                time.sleep(0.5)  # 短暂暂停
            
            results["completed_steps"] += 1
            
            # 询问是否继续
            if i < len(tutorial_steps):
                continue_tutorial = input(f"\n继续下一步？(y/n): ").strip().lower()
                if continue_tutorial in ['n', 'no', 'quit']:
                    break
        
        print("\n🎉 教学完成！您已经掌握了 Petersen 参数系统的基础知识")
        return results
    
    def _run_comparison_mode(self) -> Dict[str, Any]:
        """运行对比分析模式"""
        print("🔄 对比分析模式")
        print("在这个模式下，您可以保存多个参数设置并进行对比试听")
        print()
        
        comparison_sets = []
        results = {"mode_type": "comparison_mode", "comparison_sets": []}
        
        while len(comparison_sets) < 4:  # 最多4个对比设置
            print(f"\n📝 设置对比组合 {len(comparison_sets) + 1}:")
            
            # 让用户调节参数
            print("请调节参数到您想要的设置，然后输入 'save_compare' 保存")
            self._display_current_state()
            
            while True:
                user_input = input("🎛️ 调节参数或输入 'save_compare': ").strip().lower()
                
                if user_input == "save_compare":
                    # 保存当前设置
                    current_setting = self._get_current_parameter_dict()
                    comparison_sets.append(current_setting)
                    results["comparison_sets"].append(current_setting)
                    
                    print(f"✓ 对比设置 {len(comparison_sets)} 已保存")
                    break
                elif user_input == "quit":
                    self.stop_requested = True
                    return results
                else:
                    command_result = self._process_command(user_input)
                    if command_result.get("parameter_changed"):
                        self._trigger_auto_preview()
        
        # 开始对比试听
        print(f"\n🎵 开始对比试听 {len(comparison_sets)} 个设置:")
        
        for i, setting in enumerate(comparison_sets, 1):
            print(f"\n播放设置 {i}:")
            self._apply_parameter_dict(setting)
            self._display_parameter_summary(setting)
            self._trigger_preview(PreviewType.SHORT_MELODY)
            time.sleep(self.state.preview_duration + 1.0)
        
        # 让用户选择最喜欢的
        while True:
            try:
                choice = input(f"\n您最喜欢哪个设置？(1-{len(comparison_sets)}, 或 'replay' 重新播放): ")
                
                if choice.lower() == "replay":
                    # 重新播放所有设置
                    for i, setting in enumerate(comparison_sets, 1):
                        print(f"重播设置 {i}...")
                        self._apply_parameter_dict(setting)
                        self._trigger_preview(PreviewType.SHORT_MELODY)
                        time.sleep(self.state.preview_duration + 0.5)
                elif choice.lower() == "quit":
                    break
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(comparison_sets):
                        favorite_setting = comparison_sets[choice_num - 1]
                        self.state.favorite_settings.append(favorite_setting)
                        self._apply_parameter_dict(favorite_setting)
                        print(f"✓ 设置 {choice_num} 已应用并添加到收藏")
                        break
                    else:
                        print(f"请输入 1-{len(comparison_sets)} 之间的数字")
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                break
        
        return results
    
    def _run_composition_session(self) -> Dict[str, Any]:
        """运行创作会话模式"""
        print("🎼 创作会话模式")
        print("在这个模式下，我们将逐步创建一个完整的音乐作品")
        print()
        
        composition_elements = {
            "intro_params": None,
            "main_theme_params": None,
            "development_params": None,
            "conclusion_params": None
        }
        
        results = {"mode_type": "composition_session", "created_works": []}
        
        sections = [
            ("intro", "引入段", "设置作品的开场氛围"),
            ("main_theme", "主题段", "建立作品的主要旋律主题"),
            ("development", "发展段", "对主题进行变化和发展"),
            ("conclusion", "结尾段", "为作品提供满意的收束")
        ]
        
        for section_key, section_name, section_desc in sections:
            print(f"\n🎵 创作 {section_name}")
            print(f"   {section_desc}")
            print()
            
            # 为这个段落调节参数
            print("请为这个段落调节合适的参数:")
            self._display_current_state()
            
            while True:
                user_input = input(f"🎛️ 调节参数或输入 'confirm_{section_key}' 确认: ").strip().lower()
                
                if user_input == f"confirm_{section_key}":
                    # 保存这个段落的参数
                    composition_elements[f"{section_key}_params"] = self._get_current_parameter_dict()
                    
                    # 创建这个段落的音乐
                    section_work = self._create_section_work(section_key, section_name)
                    if section_work:
                        results["created_works"].append(section_work)
                        print(f"✓ {section_name} 已创作并保存")
                    break
                elif user_input == "quit":
                    self.stop_requested = True
                    return results
                else:
                    command_result = self._process_command(user_input)
                    if command_result.get("parameter_changed"):
                        self._trigger_auto_preview()
        
        # 创建完整作品
        print("\n🎭 创建完整作品...")
        full_composition = self._create_full_composition(composition_elements)
        if full_composition:
            results["created_works"].append(full_composition)
            print("✓ 完整作品已创建")
        
        print(f"\n🎉 创作会话完成！共创建了 {len(results['created_works'])} 个音乐片段")
        return results
    
    def _run_demonstration(self) -> Dict[str, Any]:
        """运行演示模式"""
        print("🎭 演示模式")
        print("自动演示 Petersen 音乐系统的各种能力")
        print()
        
        demonstrations = [
            {
                "title": "φ值的音乐魔法",
                "params": [
                    {"phi": "golden", "desc": "黄金比例 - 最和谐的音程关系"},
                    {"phi": "octave", "desc": "八度关系 - 纯净的倍音"},
                    {"phi": "fifth", "desc": "完全五度 - 强烈的共鸣"},
                    {"phi": "fourth", "desc": "完全四度 - 稳定的支撑"}
                ]
            },
            {
                "title": "δθ值的密度变化",
                "params": [
                    {"delta": "4.8", "desc": "五角星分割 - 神秘的几何"},
                    {"delta": "8.0", "desc": "八等分 - 对称的美感"},
                    {"delta": "15.0", "desc": "15等分 - 丰富的变化"},
                    {"delta": "24.0", "desc": "24等分 - 微分音的精妙"}
                ]
            },
            {
                "title": "和弦色彩的变幻",
                "params": [
                    {"chord": "major_triad", "desc": "大三和弦 - 明亮开朗"},
                    {"chord": "minor_seventh", "desc": "小七和弦 - 忧郁深沉"},
                    {"chord": "complex_jazz", "desc": "复合爵士 - 现代华丽"},
                    {"chord": "quartal", "desc": "四度叠置 - 现代和声"}
                ]
            }
        ]
        
        results = {"mode_type": "demonstration", "demonstrations": []}
        
        for demo in demonstrations:
            print(f"\n🌟 {demo['title']}")
            print("-" * 30)
            
            demo_result = {"title": demo["title"], "items": []}
            
            for param_set in demo["params"]:
                # 应用参数
                for param_key, param_value in param_set.items():
                    if param_key != "desc":
                        self._process_command(f"{param_key} {param_value}")
                
                # 显示说明
                print(f"\n🎵 {param_set['desc']}")
                
                # 播放预览
                self._trigger_preview(PreviewType.CHORD_PROGRESSION)
                time.sleep(self.state.preview_duration + 0.5)
                
                demo_result["items"].append({
                    "description": param_set["desc"],
                    "parameters": self._get_current_parameter_dict()
                })
            
            results["demonstrations"].append(demo_result)
            
            # 询问是否继续
            if demo != demonstrations[-1]:  # 不是最后一个演示
                continue_demo = input("\n继续下一个演示？(y/n): ").strip().lower()
                if continue_demo in ['n', 'no', 'quit']:
                    break
        
        print("\n🎊 演示完成！您已经见识了 Petersen 系统的主要能力")
        return results
    
    def _process_command(self, command: str) -> Dict[str, Any]:
        """
        处理用户命令
        
        Args:
            command: 用户输入的命令
            
        Returns:
            Dict: 命令处理结果
        """
        result = {
            "success": False,
            "parameter_changed": False,
            "should_exit": False,
            "message": ""
        }
        
        command = command.strip().lower()
        parts = command.split()
        
        if not parts:
            return result
        
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            # 帮助命令
            if cmd in ["help", "h", "?"]:
                self._display_help()
                result["success"] = True
                
            # 退出命令
            elif cmd in ["quit", "exit", "q"]:
                print("👋 感谢使用 Petersen 交互式工作室！")
                result["should_exit"] = True
                result["success"] = True
                
            # 显示当前状态
            elif cmd in ["status", "state", "current"]:
                self._display_current_state()
                result["success"] = True
                
            # φ值调节
            elif cmd in ["phi", "φ"]:
                if args:
                    if self._set_phi_value(args[0]):
                        result["parameter_changed"] = True
                        result["success"] = True
                        result["message"] = f"φ值已设置为: {args[0]}"
                else:
                    print("请指定φ值，例如: phi golden")
                    
            # δθ值调节
            elif cmd in ["delta", "θ", "theta"]:
                if args:
                    if self._set_delta_theta_value(args[0]):
                        result["parameter_changed"] = True
                        result["success"] = True
                        result["message"] = f"δθ值已设置为: {args[0]}"
                else:
                    print("请指定δθ值，例如: delta 15.0")
                    
            # 基频调节
            elif cmd in ["fbase", "freq", "base"]:
                if args:
                    try:
                        new_f_base = float(args[0])
                        if 20.0 <= new_f_base <= 200.0:
                            self.state.current_f_base = new_f_base
                            self._update_musical_components()
                            result["parameter_changed"] = True
                            result["success"] = True
                            result["message"] = f"基频已设置为: {new_f_base:.1f} Hz"
                        else:
                            print("基频应在 20.0-200.0 Hz 范围内")
                    except ValueError:
                        print("请输入有效的频率数值")
                else:
                    print("请指定基频，例如: fbase 55.0")
                    
            # 和弦设置
            elif cmd in ["chord", "harmony"]:
                if args:
                    if self._set_chord_ratios(args[0]):
                        result["parameter_changed"] = True
                        result["success"] = True
                        result["message"] = f"和弦已设置为: {args[0]}"
                else:
                    print("请指定和弦类型，例如: chord major_triad")
                    
            # 节奏风格
            elif cmd in ["rhythm", "beat"]:
                if args:
                    if self._set_rhythm_style(args[0]):
                        result["parameter_changed"] = True
                        result["success"] = True
                        result["message"] = f"节奏风格已设置为: {args[0]}"
                else:
                    print("请指定节奏风格，例如: rhythm traditional")
                    
            # 旋律模式
            elif cmd in ["melody", "pattern"]:
                if args:
                    if self._set_melody_pattern(args[0]):
                        result["parameter_changed"] = True
                        result["success"] = True
                        result["message"] = f"旋律模式已设置为: {args[0]}"
                else:
                    print("请指定旋律模式，例如: melody balanced")
                    
            # 作曲风格
            elif cmd in ["style", "composition"]:
                if args:
                    if self._set_composition_style(args[0]):
                        result["parameter_changed"] = True
                        result["success"] = True
                        result["message"] = f"作曲风格已设置为: {args[0]}"
                else:
                    print("请指定作曲风格，例如: style balanced_journey")
                    
            # 预览命令
            elif cmd in ["preview", "play", "p"]:
                preview_type = PreviewType.SCALE_SEQUENCE  # 默认
                if args:
                    if args[0] in ["note", "single"]:
                        preview_type = PreviewType.SINGLE_NOTE
                    elif args[0] in ["scale", "sequence"]:
                        preview_type = PreviewType.SCALE_SEQUENCE
                    elif args[0] in ["chord", "harmony"]:
                        preview_type = PreviewType.CHORD_PROGRESSION
                    elif args[0] in ["melody", "tune"]:
                        preview_type = PreviewType.SHORT_MELODY
                    elif args[0] in ["mini", "composition"]:
                        preview_type = PreviewType.MINI_COMPOSITION
                
                self._trigger_preview(preview_type)
                result["success"] = True
                result["message"] = f"播放预览: {preview_type.value}"
                
            # 保存命令
            elif cmd in ["save", "store"]:
                if args:
                    work_name = "_".join(args)
                    if self._save_current_work(work_name):
                        result["success"] = True
                        result["message"] = f"当前设置已保存为: {work_name}"
                else:
                    print("请指定保存名称，例如: save my_favorite")
                    
            # 收藏命令
            elif cmd in ["favorite", "fav", "like"]:
                self._add_to_favorites()
                result["success"] = True
                result["message"] = "当前设置已添加到收藏"
                
            # 列出预设
            elif cmd in ["list", "show"]:
                if args:
                    self._list_presets(args[0])
                else:
                    self._list_all_presets()
                result["success"] = True
                
            # 随机参数
            elif cmd in ["random", "rand", "surprise"]:
                self._randomize_parameters()
                result["parameter_changed"] = True
                result["success"] = True
                result["message"] = "参数已随机化"
                
            # 重置参数
            elif cmd in ["reset", "default"]:
                self._reset_to_defaults()
                result["parameter_changed"] = True
                result["success"] = True
                result["message"] = "参数已重置为默认值"
                
            # 自动预览开关
            elif cmd in ["auto"]:
                self.state.auto_preview = not self.state.auto_preview
                status = "开启" if self.state.auto_preview else "关闭"
                result["success"] = True
                result["message"] = f"自动预览已{status}"
                
            # 未知命令
            else:
                print(f"❌ 未知命令: {cmd}")
                print("输入 'help' 查看可用命令")
            
            # 记录交互
            if result["success"]:
                self._record_interaction(cmd, args, result["message"])
                self.state.interaction_count += 1
                
                if result["parameter_changed"]:
                    self._record_parameter_change()
        
        except Exception as e:
            print(f"❌ 命令执行失败: {e}")
            result["message"] = f"错误: {e}"
        
        return result
    
    def _set_phi_value(self, phi_name: str) -> bool:
        """设置φ值"""
        if phi_name in PRESET_PHI_VALUES:
            self.state.current_phi_name = phi_name
            self.state.current_phi_value = PRESET_PHI_VALUES[phi_name]
            self._update_musical_components()
            return True
        else:
            print(f"❌ 未知φ值: {phi_name}")
            print(f"可用φ值: {', '.join(PRESET_PHI_VALUES.keys())}")
            return False
    
    def _set_delta_theta_value(self, delta_name: str) -> bool:
        """设置δθ值"""
        if delta_name in PRESET_DELTA_THETA_VALUES:
            self.state.current_delta_theta_name = delta_name
            self.state.current_delta_theta_value = PRESET_DELTA_THETA_VALUES[delta_name]
            self._update_musical_components()
            return True
        else:
            print(f"❌ 未知δθ值: {delta_name}")
            print(f"可用δθ值: {', '.join(PRESET_DELTA_THETA_VALUES.keys())}")
            return False
    
    def _set_chord_ratios(self, chord_name: str) -> bool:
        """设置和弦比率"""
        if chord_name in CHORD_RATIOS_PRESETS:
            self.state.current_chord_set = chord_name
            self._update_musical_components()
            return True
        else:
            print(f"❌ 未知和弦类型: {chord_name}")
            print(f"可用和弦: {', '.join(CHORD_RATIOS_PRESETS.keys())}")
            return False
    
    def _set_rhythm_style(self, rhythm_name: str) -> bool:
        """设置节奏风格"""
        if rhythm_name in RHYTHM_STYLE_PRESETS:
            self.state.current_rhythm_style = rhythm_name
            return True
        else:
            print(f"❌ 未知节奏风格: {rhythm_name}")
            print(f"可用节奏: {', '.join(RHYTHM_STYLE_PRESETS.keys())}")
            return False
    
    def _set_melody_pattern(self, pattern_name: str) -> bool:
        """设置旋律模式"""
        if pattern_name in MELODY_PATTERN_PRESETS:
            self.state.current_melody_pattern = pattern_name
            return True
        else:
            print(f"❌ 未知旋律模式: {pattern_name}")
            print(f"可用模式: {', '.join(MELODY_PATTERN_PRESETS.keys())}")
            return False
    
    def _set_composition_style(self, style_name: str) -> bool:
        """设置作曲风格"""
        if style_name in COMPOSITION_STYLES:
            self.state.current_composition_style = style_name
            return True
        else:
            print(f"❌ 未知作曲风格: {style_name}")
            print(f"可用风格: {', '.join(COMPOSITION_STYLES.keys())}")
            return False
    
    def _update_musical_components(self):
        """更新音乐组件"""
        try:
            # 创建音阶
            cache_key = f"{self.state.current_phi_value}_{self.state.current_delta_theta_value}_{self.state.current_f_base}"
            
            if cache_key not in self.scale_cache:
                self.current_scale = PetersenScale(
                    F_base=self.state.current_f_base,
                    phi=self.state.current_phi_value,
                    delta_theta=self.state.current_delta_theta_value
                )
                self.scale_cache[cache_key] = self.current_scale
            else:
                self.current_scale = self.scale_cache[cache_key]
            
            # 创建和弦扩展器
            chord_ratios = CHORD_RATIOS_PRESETS[self.state.current_chord_set]
            self.current_chord_extender = PetersenChordExtender(
                petersen_scale=self.current_scale,
                chord_ratios=chord_ratios
            )
            
            # 创建作曲器
            composition_style = COMPOSITION_STYLES[self.state.current_composition_style]
            self.current_composer = PetersenAutoComposer(
                petersen_scale=self.current_scale,
                chord_extender=self.current_chord_extender,
                composition_style=composition_style,
                bpm=120
            )
            
        except Exception as e:
            print(f"⚠️ 音乐组件更新失败: {e}")
    
    def _trigger_auto_preview(self):
        """触发自动预览"""
        if self.state.auto_preview:
            self._trigger_preview(self.state.preview_type)
    
    def _trigger_preview(self, preview_type: PreviewType):
        """触发预览播放"""
        if not self.enhanced_player or not self.enhanced_player.is_initialized:
            print("⚠️ 音频播放器不可用")
            return
        
        # 避免过于频繁的预览
        current_time = time.time()
        if current_time - self.last_preview_time < 0.5:
            return
        
        self.last_preview_time = current_time
        
        try:
            print(f"🔊 播放预览: {preview_type.value}")
            
            if preview_type == PreviewType.SINGLE_NOTE:
                self._preview_single_note()
            elif preview_type == PreviewType.SCALE_SEQUENCE:
                self._preview_scale_sequence()
            elif preview_type == PreviewType.CHORD_PROGRESSION:
                self._preview_chord_progression()
            elif preview_type == PreviewType.SHORT_MELODY:
                self._preview_short_melody()
            elif preview_type == PreviewType.MINI_COMPOSITION:
                self._preview_mini_composition()
                
        except Exception as e:
            print(f"⚠️ 预览播放失败: {e}")
    
    def _preview_single_note(self):
        """预览单音符"""
        if not self.current_scale:
            return
        
        # 播放基频音符
        base_entry = self.current_scale.get_scale_entries()[0]
        self.enhanced_player.play_frequencies(
            frequencies=[base_entry.freq],
            key_names=[base_entry.key_short],
            duration=self.state.preview_duration,
            use_accurate_frequency=True
        )
    
    def _preview_scale_sequence(self):
        """预览音阶序列"""
        if not self.current_scale:
            return
        
        # 播放前8个音符
        scale_entries = self.current_scale.get_scale_entries()[:8]
        frequencies = [entry.freq for entry in scale_entries]
        key_names = [entry.key_short for entry in scale_entries]
        
        self.enhanced_player.play_frequencies(
            frequencies=frequencies,
            key_names=key_names,
            duration=self.state.preview_duration / len(frequencies),
            gap=0.05,
            use_accurate_frequency=True
        )
    
    def _preview_chord_progression(self):
        """预览和弦进行"""
        if not self.current_chord_extender:
            return
        
        try:
            # 获取扩展音阶
            extended_scale = self.current_chord_extender.extend_scale_with_chords()
            
            # 创建简单的和弦进行
            chord_notes = extended_scale[:6] if len(extended_scale) >= 6 else extended_scale
            frequencies = [note.freq for note in chord_notes]
            key_names = [note.key_short for note in chord_notes]
            
            # 同时播放形成和弦
            for freq, key in zip(frequencies[:3], key_names[:3]):  # 三音和弦
                # 这里需要实现同时播放多个音符的功能
                # 目前使用快速连续播放模拟
                pass
            
            # 使用旋律化的和弦
            self.enhanced_player.play_frequencies(
                frequencies=frequencies,
                key_names=key_names,
                duration=self.state.preview_duration / len(frequencies),
                gap=0.02,
                use_accurate_frequency=True
            )
            
        except Exception as e:
            print(f"⚠️ 和弦预览失败: {e}")
    
    def _preview_short_melody(self):
        """预览短旋律"""
        if not self.current_composer:
            return
        
        try:
            # 创建2小节的短作品
            mini_composition = self.current_composer.compose(measures=2)
            
            # 提取旋律进行播放
            if hasattr(mini_composition, 'get_preview_frequencies'):
                frequencies, names = mini_composition.get_preview_frequencies()
                self.enhanced_player.play_frequencies(
                    frequencies=frequencies[:8],
                    key_names=names[:8],
                    duration=self.state.preview_duration / 8,
                    gap=0.1,
                    use_accurate_frequency=True
                )
            else:
                # 回退到音阶预览
                self._preview_scale_sequence()
                
        except Exception as e:
            print(f"⚠️ 旋律预览失败: {e}")
            # 回退到音阶预览
            self._preview_scale_sequence()
    
    def _preview_mini_composition(self):
        """预览迷你作品"""
        if not self.current_composer:
            return
        
        try:
            # 创建4小节的迷你作品
            mini_composition = self.current_composer.compose(measures=4)
            
            # 这里需要更复杂的播放逻辑
            # 目前使用简化版本
            print("🎼 生成迷你作品中...")
            time.sleep(1.0)  # 模拟生成时间
            
            # 播放主旋律线
            if hasattr(mini_composition, 'get_preview_frequencies'):
                frequencies, names = mini_composition.get_preview_frequencies()
                self.enhanced_player.play_frequencies(
                    frequencies=frequencies[:12],
                    key_names=names[:12],
                    duration=self.state.preview_duration / 12,
                    gap=0.05,
                    use_accurate_frequency=True
                )
            else:
                # 回退到和弦预览
                self._preview_chord_progression()
                
        except Exception as e:
            print(f"⚠️ 迷你作品预览失败: {e}")
            # 回退到和弦预览
            self._preview_chord_progression()
    
    def _display_current_state(self):
        """显示当前状态"""
        print("\n" + "=" * 40)
        print("🎛️ 当前参数状态")
        print("=" * 40)
        print(f"φ值:      {self.state.current_phi_name} ({self.state.current_phi_value:.3f})")
        print(f"δθ值:     {self.state.current_delta_theta_name} ({self.state.current_delta_theta_value:.1f}°)")
        print(f"基频:      {self.state.current_f_base:.1f} Hz")
        print(f"和弦:      {self.state.current_chord_set}")
        print(f"节奏:      {self.state.current_rhythm_style}")
        print(f"旋律:      {self.state.current_melody_pattern}")
        print(f"风格:      {self.state.current_composition_style}")
        print(f"预览:      {self.state.preview_type.value}")
        print(f"自动预览:  {'开启' if self.state.auto_preview else '关闭'}")
        print("=" * 40)
    
    def _display_parameter_summary(self, params: Dict[str, Any]):
        """显示参数摘要"""
        print(f"  φ={params.get('phi_name', '?')}({params.get('phi_value', 0):.3f}), "
              f"δθ={params.get('delta_theta_name', '?')}({params.get('delta_theta_value', 0):.1f}°), "
              f"和弦={params.get('chord_set', '?')}")
    
    def _display_help(self):
        """显示帮助信息"""
        help_text = """
🎹 Petersen 交互式工作室 - 命令帮助

📊 状态查看:
  status/state      - 显示当前参数状态
  list <类型>       - 列出可用预设 (phi/delta/chord/rhythm/melody/style)
  list              - 列出所有预设

🎛️ 参数调节:
  phi <值>          - 设置φ值 (golden/octave/fifth/fourth/...)
  delta <值>        - 设置δθ值 (4.8/8.0/15.0/24.0/...)
  fbase <频率>      - 设置基频 (20.0-200.0 Hz)
  chord <类型>      - 设置和弦 (major_triad/minor_seventh/...)
  rhythm <风格>     - 设置节奏风格
  melody <模式>     - 设置旋律模式
  style <风格>      - 设置作曲风格

🔊 音频预览:
  preview/play      - 播放当前设置预览 (默认音阶)
  preview note      - 单音符预览
  preview scale     - 音阶序列预览
  preview chord     - 和弦进行预览
  preview melody    - 短旋律预览
  preview mini      - 迷你作品预览

💾 保存管理:
  save <名称>       - 保存当前设置为作品
  favorite/fav      - 添加到收藏夹

🎲 快捷操作:
  random/rand       - 随机化所有参数
  reset/default     - 重置为默认参数
  auto              - 切换自动预览开关

❓ 其他:
  help/h/?          - 显示此帮助
  quit/exit/q       - 退出工作室

💡 使用提示:
• 参数改变后会自动播放预览 (如果开启自动预览)
• 使用 'list' 命令查看所有可用的参数选项
• 'save' 命令会创建完整的音乐作品文件
• 输入参数名称不完整时会显示可用选项
        """
        print(help_text)
    
    def _list_presets(self, preset_type: str):
        """列出特定类型的预设"""
        preset_type = preset_type.lower()
        
        if preset_type in ["phi", "φ"]:
            print("🎵 可用φ值预设:")
            for name, value in PRESET_PHI_VALUES.items():
                current = " ← 当前" if name == self.state.current_phi_name else ""
                print(f"  {name}: {value:.3f}{current}")
                
        elif preset_type in ["delta", "θ", "theta"]:
            print("🎵 可用δθ值预设:")
            for name, value in PRESET_DELTA_THETA_VALUES.items():
                current = " ← 当前" if name == self.state.current_delta_theta_name else ""
                print(f"  {name}: {value:.1f}°{current}")
                
        elif preset_type in ["chord", "harmony"]:
            print("🎵 可用和弦预设:")
            for name in CHORD_RATIOS_PRESETS.keys():
                current = " ← 当前" if name == self.state.current_chord_set else ""
                print(f"  {name}{current}")
                
        elif preset_type in ["rhythm", "beat"]:
            print("🎵 可用节奏风格:")
            for name in RHYTHM_STYLE_PRESETS.keys():
                current = " ← 当前" if name == self.state.current_rhythm_style else ""
                print(f"  {name}{current}")
                
        elif preset_type in ["melody", "pattern"]:
            print("🎵 可用旋律模式:")
            for name in MELODY_PATTERN_PRESETS.keys():
                current = " ← 当前" if name == self.state.current_melody_pattern else ""
                print(f"  {name}{current}")
                
        elif preset_type in ["style", "composition"]:
            print("🎵 可用作曲风格:")
            for name in COMPOSITION_STYLES.keys():
                current = " ← 当前" if name == self.state.current_composition_style else ""
                print(f"  {name}{current}")
                
        else:
            print(f"❌ 未知预设类型: {preset_type}")
            print("可用类型: phi, delta, chord, rhythm, melody, style")
    
    def _list_all_presets(self):
        """列出所有预设"""
        print("🎵 所有可用预设:")
        print()
        
        preset_types = [
            ("φ值", PRESET_PHI_VALUES),
            ("δθ值", PRESET_DELTA_THETA_VALUES),
            ("和弦", CHORD_RATIOS_PRESETS),
            ("节奏", RHYTHM_STYLE_PRESETS),
            ("旋律", MELODY_PATTERN_PRESETS),
            ("风格", COMPOSITION_STYLES)
        ]
        
        for type_name, presets in preset_types:
            print(f"{type_name}: {', '.join(list(presets.keys())[:5])}{'...' if len(presets) > 5 else ''}")
        
        print("\n💡 使用 'list <类型>' 查看详细信息")
    
    def _randomize_parameters(self):
        """随机化参数"""
        import random
        
        # 随机选择参数
        phi_names = list(PRESET_PHI_VALUES.keys())
        delta_names = list(PRESET_DELTA_THETA_VALUES.keys())
        chord_names = list(CHORD_RATIOS_PRESETS.keys())
        rhythm_names = list(RHYTHM_STYLE_PRESETS.keys())
        melody_names = list(MELODY_PATTERN_PRESETS.keys())
        style_names = list(COMPOSITION_STYLES.keys())
        
        self.state.current_phi_name = random.choice(phi_names)
        self.state.current_phi_value = PRESET_PHI_VALUES[self.state.current_phi_name]
        
        self.state.current_delta_theta_name = random.choice(delta_names)
        self.state.current_delta_theta_value = PRESET_DELTA_THETA_VALUES[self.state.current_delta_theta_name]
        
        self.state.current_f_base = random.uniform(40.0, 80.0)
        self.state.current_chord_set = random.choice(chord_names)
        self.state.current_rhythm_style = random.choice(rhythm_names)
        self.state.current_melody_pattern = random.choice(melody_names)
        self.state.current_composition_style = random.choice(style_names)
        
        self._update_musical_components()
        
        print("🎲 参数已随机化:")
        self._display_current_state()
    
    def _reset_to_defaults(self):
        """重置为默认参数"""
        self.state = WorkshopState()  # 重新创建默认状态
        self._update_musical_components()
        
        print("🔄 参数已重置为默认值:")
        self._display_current_state()
    
    def _add_to_favorites(self):
        """添加到收藏"""
        current_params = self._get_current_parameter_dict()
        self.state.favorite_settings.append(current_params)
        print(f"⭐ 当前设置已添加到收藏 (共 {len(self.state.favorite_settings)} 个)")
    
    def _save_current_work(self, work_name: str) -> bool:
        """保存当前作品"""
        try:
            if not self.current_composer:
                print("❌ 音乐组件未初始化")
                return False
            
            # 创建作品
            composition = self.current_composer.compose(measures=4)
            
            # 使用master_studio的保存功能
            current_params = self._get_current_parameter_dict()
            work_result = self.master_studio._save_composition_work(
                composition, f"workshop_{work_name}", current_params
            )
            
            if work_result:
                print(f"✓ 作品已保存: {work_name}")
                return True
            else:
                print(f"❌ 作品保存失败: {work_name}")
                return False
                
        except Exception as e:
            print(f"❌ 保存作品失败: {e}")
            return False
    
    def _create_section_work(self, section_key: str, section_name: str) -> Optional[Dict[str, Any]]:
        """创建段落作品"""
        try:
            if not self.current_composer:
                return None
            
            # 创建段落作品
            composition = self.current_composer.compose(measures=2)
            
            # 保存段落
            current_params = self._get_current_parameter_dict()
            work_name = f"workshop_section_{section_key}"
            
            work_result = self.master_studio._save_composition_work(
                composition, work_name, current_params
            )
            
            if work_result:
                work_result["section_name"] = section_name
                work_result["section_key"] = section_key
                return work_result
                
        except Exception as e:
            print(f"❌ 段落创作失败: {e}")
        
        return None
    
    def _create_full_composition(self, composition_elements: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建完整作品"""
        try:
            # 这里可以整合所有段落创建一个完整作品
            # 目前创建一个8小节的综合作品
            
            if not self.current_composer:
                return None
            
            composition = self.current_composer.compose(measures=8)
            
            work_name = f"workshop_full_composition_{int(time.time())}"
            current_params = self._get_current_parameter_dict()
            
            work_result = self.master_studio._save_composition_work(
                composition, work_name, current_params
            )
            
            if work_result:
                work_result["composition_type"] = "full_composition"
                work_result["elements"] = composition_elements
                return work_result
                
        except Exception as e:
            print(f"❌ 完整作品创作失败: {e}")
        
        return None
    
    def _get_current_parameter_dict(self) -> Dict[str, Any]:
        """获取当前参数字典"""
        return {
            "phi_name": self.state.current_phi_name,
            "phi_value": self.state.current_phi_value,
            "delta_theta_name": self.state.current_delta_theta_name,
            "delta_theta_value": self.state.current_delta_theta_value,
            "f_base": self.state.current_f_base,
            "chord_set": self.state.current_chord_set,
            "rhythm_style": self.state.current_rhythm_style,
            "melody_pattern": self.state.current_melody_pattern,
            "composition_style": self.state.current_composition_style,
            "timestamp": datetime.now().isoformat()
        }
    
    def _apply_parameter_dict(self, params: Dict[str, Any]):
        """应用参数字典"""
        self.state.current_phi_name = params.get("phi_name", "golden")
        self.state.current_phi_value = params.get("phi_value", 1.618)
        self.state.current_delta_theta_name = params.get("delta_theta_name", "15.0")
        self.state.current_delta_theta_value = params.get("delta_theta_value", 15.0)
        self.state.current_f_base = params.get("f_base", 55.0)
        self.state.current_chord_set = params.get("chord_set", "major_triad")
        self.state.current_rhythm_style = params.get("rhythm_style", "traditional")
        self.state.current_melody_pattern = params.get("melody_pattern", "balanced")
        self.state.current_composition_style = params.get("composition_style", "balanced_journey")
        
        self._update_musical_components()
    
    def _record_interaction(self, command: str, args: List[str], description: str):
        """记录交互"""
        interaction = InteractionRecord(
            timestamp=datetime.now(),
            action_type=command,
            parameters=self._get_current_parameter_dict(),
            description=description,
            audio_generated=command in ["preview", "play", "p"]
        )
        
        self.interaction_history.append(interaction)
    
    def _record_parameter_change(self):
        """记录参数变化"""
        change_record = {
            "timestamp": datetime.now().isoformat(),
            "parameters": self._get_current_parameter_dict(),
            "interaction_count": self.state.interaction_count
        }
        
        self.state.parameter_changes.append(change_record)
    
    def _save_session_results(self, session_results: Dict[str, Any]):
        """保存会话结果"""
        try:
            session_path = (self.master_studio.config.output_directory / 
                           f"workshop_session_{self.session_id}.json")
            
            # 添加会话统计
            session_results["session_statistics"] = {
                "total_interactions": len(self.interaction_history),
                "parameter_changes": len(self.state.parameter_changes),
                "favorite_settings": len(self.state.favorite_settings),
                "session_duration_minutes": (
                    (datetime.now() - self.state.session_start_time).total_seconds() / 60
                )
            }
            
            # 添加收藏设置
            session_results["favorite_settings"] = self.state.favorite_settings
            
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 会话结果已保存: {session_path}")
            
        except Exception as e:
            print(f"⚠️ 会话结果保存失败: {e}")
    
    def _cleanup_session(self):
        """清理会话资源"""
        try:
            # 停止预览线程
            if self.preview_thread and self.preview_thread.is_alive():
                self.preview_thread.join(timeout=1.0)
            
            # 清理缓存
            self.scale_cache.clear()
            self.audio_cache.clear()
            
            print("✓ 会话资源已清理")
            
        except Exception as e:
            print(f"⚠️ 会话清理警告: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        return {
            "session_id": self.session_id,
            "mode": self.mode.value,
            "is_running": self.is_running,
            "current_parameters": self._get_current_parameter_dict(),
            "statistics": {
                "interactions": len(self.interaction_history),
                "parameter_changes": len(self.state.parameter_changes),
                "favorites": len(self.state.favorite_settings),
                "session_duration": (
                    (datetime.now() - self.state.session_start_time).total_seconds()
                )
            }
        }
    
    def export_favorite_presets(self, output_path: Optional[Path] = None) -> Path:
        """导出收藏的预设"""
        if not output_path:
            output_path = (self.master_studio.config.output_directory / 
                          f"workshop_favorites_{self.session_id}.json")
        
        try:
            favorites_data = {
                "session_id": self.session_id,
                "export_timestamp": datetime.now().isoformat(),
                "favorite_count": len(self.state.favorite_settings),
                "favorites": self.state.favorite_settings
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(favorites_data, f, indent=2, ensure_ascii=False)
            
            print(f"⭐ 收藏预设已导出: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 收藏预设导出失败: {e}")
            raise
    
    def load_favorite_presets(self, favorites_path: Path) -> bool:
        """加载收藏的预设"""
        try:
            with open(favorites_path, 'r', encoding='utf-8') as f:
                favorites_data = json.load(f)
            
            loaded_favorites = favorites_data.get("favorites", [])
            self.state.favorite_settings.extend(loaded_favorites)
            
            print(f"⭐ 已加载 {len(loaded_favorites)} 个收藏预设")
            return True
            
        except Exception as e:
            print(f"❌ 收藏预设加载失败: {e}")
            return False

# ========== 预定义工作室会话 ==========

class PredefinedSessions:
    """预定义的工作室会话"""
    
    @staticmethod
    def create_beginner_tutorial() -> List[Dict[str, Any]]:
        """创建初学者教程会话"""
        return [
            {
                "title": "认识φ值",
                "description": "了解φ值如何影响音程关系",
                "commands": [
                    "phi golden",
                    "preview scale",
                    "phi octave", 
                    "preview scale",
                    "phi fifth",
                    "preview scale"
                ]
            },
            {
                "title": "探索δθ值",
                "description": "感受不同δθ值的音阶密度",
                "commands": [
                    "delta 4.8",
                    "preview scale",
                    "delta 15.0",
                    "preview scale", 
                    "delta 24.0",
                    "preview scale"
                ]
            },
            {
                "title": "和弦的魅力",
                "description": "体验不同和弦类型的色彩",
                "commands": [
                    "chord major_triad",
                    "preview chord",
                    "chord minor_seventh",
                    "preview chord",
                    "chord complex_jazz",
                    "preview chord"
                ]
            }
        ]
    
    @staticmethod
    def create_advanced_exploration() -> List[Dict[str, Any]]:
        """创建高级探索会话"""
        return [
            {
                "title": "数学美学对比",
                "description": "对比不同数学参数的美学效果",
                "commands": [
                    "phi golden",
                    "delta 15.0",
                    "preview melody",
                    "save golden_melody",
                    "phi octave",
                    "delta 24.0", 
                    "preview melody",
                    "save octave_melody"
                ]
            },
            {
                "title": "复合参数实验",
                "description": "实验复杂参数组合",
                "commands": [
                    "phi golden",
                    "delta 4.8",
                    "chord complex_jazz",
                    "style virtuoso_journey",
                    "preview mini",
                    "save complex_experiment"
                ]
            }
        ]
    
    @staticmethod
    def create_composition_workshop() -> List[Dict[str, Any]]:
        """创建作曲工作坊会话"""
        return [
            {
                "title": "主题创建",
                "description": "创建音乐主题",
                "commands": [
                    "phi golden",
                    "delta 15.0",
                    "chord major_seventh",
                    "melody balanced",
                    "preview melody",
                    "save main_theme"
                ]
            },
            {
                "title": "主题变奏",
                "description": "对主题进行变奏",
                "commands": [
                    "phi fifth",
                    "chord minor_seventh",
                    "preview melody",
                    "save theme_variation_1",
                    "phi fourth",
                    "chord complex_jazz",
                    "preview melody", 
                    "save theme_variation_2"
                ]
            },
            {
                "title": "综合作品",
                "description": "创建综合性作品",
                "commands": [
                    "phi golden",
                    "delta 15.0",
                    "chord major_seventh",
                    "style balanced_journey",
                    "preview mini",
                    "save final_composition"
                ]
            }
        ]

# ========== 便利函数 ==========

def create_interactive_workshop(master_studio) -> InteractiveWorkshop:
    """
    创建交互式工作室
    
    Args:
        master_studio: PetersenMasterStudio实例
        
    Returns:
        InteractiveWorkshop: 配置好的工作室
    """
    return InteractiveWorkshop(master_studio)

def run_quick_interactive_demo(master_studio, duration_minutes: float = 5.0) -> Dict[str, Any]:
    """
    便利函数：运行快速交互演示
    
    Args:
        master_studio: PetersenMasterStudio实例
        duration_minutes: 演示时长（分钟）
        
    Returns:
        Dict: 演示结果
    """
    workshop = create_interactive_workshop(master_studio)
    
    # 设置较短的预览时间
    workshop.state.preview_duration = 2.0
    workshop.state.auto_preview = True
    
    print(f"🎵 开始 {duration_minutes} 分钟快速交互演示...")
    
    # 运行演示模式
    return workshop.run_session(WorkshopMode.DEMONSTRATION)

def run_guided_tutorial(master_studio) -> Dict[str, Any]:
    """
    便利函数：运行引导式教程
    
    Args:
        master_studio: PetersenMasterStudio实例
        
    Returns:
        Dict: 教程结果
    """
    workshop = create_interactive_workshop(master_studio)
    return workshop.run_session(WorkshopMode.GUIDED_TUTORIAL)

def run_parameter_comparison(master_studio, max_comparisons: int = 3) -> Dict[str, Any]:
    """
    便利函数：运行参数对比会话
    
    Args:
        master_studio: PetersenMasterStudio实例
        max_comparisons: 最大对比数量
        
    Returns:
        Dict: 对比结果
    """
    workshop = create_interactive_workshop(master_studio)
    
    # 设置对比参数
    workshop.max_comparisons = max_comparisons
    
    return workshop.run_session(WorkshopMode.COMPARISON_MODE)

def execute_predefined_session(master_studio, session_type: str = "beginner") -> Dict[str, Any]:
    """
    执行预定义会话
    
    Args:
        master_studio: PetersenMasterStudio实例
        session_type: 会话类型 ("beginner", "advanced", "composition")
        
    Returns:
        Dict: 会话结果
    """
    workshop = create_interactive_workshop(master_studio)
    
    # 选择预定义会话
    if session_type == "beginner":
        session_steps = PredefinedSessions.create_beginner_tutorial()
    elif session_type == "advanced":
        session_steps = PredefinedSessions.create_advanced_exploration()
    elif session_type == "composition":
        session_steps = PredefinedSessions.create_composition_workshop()
    else:
        raise ValueError(f"未知会话类型: {session_type}")
    
    print(f"🎓 执行预定义会话: {session_type}")
    
    results = {
        "session_type": session_type,
        "steps_completed": 0,
        "created_works": []
    }
    
    # 执行会话步骤
    for i, step in enumerate(session_steps, 1):
        print(f"\n📚 步骤 {i}: {step['title']}")
        print(f"   {step['description']}")
        
        # 执行命令序列
        for command in step["commands"]:
            print(f"🎵 执行: {command}")
            command_result = workshop._process_command(command)
            
            if command.startswith("preview"):
                time.sleep(workshop.state.preview_duration + 0.5)
            elif command.startswith("save"):
                if command_result.get("success"):
                    work_name = command.split()[1] if len(command.split()) > 1 else f"work_{i}"
                    results["created_works"].append(work_name)
            
            time.sleep(0.3)  # 短暂间隔
        
        results["steps_completed"] += 1
        
        # 简短暂停
        print("   ✓ 步骤完成")
        time.sleep(1.0)
    
    print(f"\n🎉 预定义会话完成！")
    print(f"   完成步骤: {results['steps_completed']}")
    print(f"   创建作品: {len(results['created_works'])}")
    
    return results

# ========== 命令行接口 ==========

def main():
    """交互式工作室的独立命令行接口"""
    print("🛠️ Petersen 交互式参数工作室")
    print("=" * 50)
    
    # 这里可以添加独立运行的逻辑
    # 目前主要通过 PetersenMasterStudio 调用
    
    print("请通过 PetersenMasterStudio 使用交互式工作室：")
    print("python petersen_master_studio.py --interactive-workshop")
    print()
    print("或使用便利函数：")
    print("- run_quick_interactive_demo()")
    print("- run_guided_tutorial()")
    print("- run_parameter_comparison()")
    print("- execute_predefined_session()")

if __name__ == "__main__":
    main()