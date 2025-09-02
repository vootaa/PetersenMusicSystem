"""
Petersen Master Studio - 大师级音乐创作工作室

这是整个Petersen音乐系统的灵魂模块，展示从数学参数到完整音乐作品的全部威力。
不同于其他技术导向的模块，这里完全以作品级别输出为目标，每次运行都产生完整的音乐体验。

核心使命：
- 展示Petersen数学模型的音乐创作潜力
- 提供参数空间的全面探索
- 生成高质量的音乐作品
- 建立数学美学评估体系
- 为音乐家提供创新的探索工具

主要功能模块：
- 参数空间探索：生成不同数学参数组合的作品集
- 数学美学对比：同一音乐想法在不同框架下的表现
- 完整作曲展示：从参数到成品的全链条演示
- 交互式工作室：实时参数调节与音乐预览
- 批量作品生成：展示系统全部能力的作品集

使用示例：
```bash
# 探索数学参数空间
python3 petersen_master_studio.py --explore-mathematics \
  --phi-values golden,octave,fifth \
  --delta-theta-values 4.8,15.0,24.0 \
  --measures 16 --output-dir "mathematical_exploration/"

# 数学美学对比
python3 petersen_master_studio.py --compare-aesthetics \
  --base-theme romantic_melody \
  --parameter-variations 5 \
  --comparison-report detailed

# 展示大师级技艺
python3 petersen_master_studio.py --showcase-virtuosity \
  --composition-length 32 \
  --technique-levels all \
  --quality studio

# 交互式工作室
python3 petersen_master_studio.py --interactive-workshop \
  --realtime-preview \
  --parameter-studio

# 生成大师作品集
python3 petersen_master_studio.py --generate-masterworks \
  --collection-theme mathematical_beauty \
  --works-count 10 \
  --export-formats wav,midi,analysis
```
"""

import argparse
import json
import time
import random
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import sys
from pathlib import Path

# 添加父目录到路径
current_dir = Path(__file__).parent
libs_dir = current_dir.parent / "libs"
if str(libs_dir) not in sys.path:
    sys.path.insert(0, str(libs_dir))

# 导入基础模块
try:
    from petersen_scale import PetersenScale, PHI_PRESETS, DELTA_THETA_PRESETS
    from petersen_chord import PetersenChordExtender, CHORD_RATIOS
    from petersen_rhythm import PetersenRhythmGenerator, RHYTHM_STYLES
    from petersen_melody import PetersenMelodyGenerator, MELODY_PATTERNS
    from petersen_composer import PetersenAutoComposer, COMPOSITION_STYLES
    from petersen_performance import PetersenPerformanceRenderer, PERFORMANCE_TECHNIQUES
    from petersen_player import EnhancedPetersenPlayer, PlayerConfiguration
except ImportError as e:
    print(f"❌ 导入基础模块失败: {e}")
    print("请确保基础库模块位于正确路径")
    sys.exit(1)

# 导入大师级模块
try:
    from parameter_explorer import ParameterSpaceExplorer, ExplorationMode
    from aesthetic_comparator import AestheticComparator, ComparisonDimension
    from composition_showcase import CompositionShowcase, ShowcaseType
    from interactive_workshop import InteractiveWorkshop, WorkshopMode
    from masterwork_generator import MasterworkGenerator, MasterworkType, CompositionQuality
    from soundfont_renderer import HighQualitySoundFontRenderer, RenderQuality
    from analysis_reporter import AnalysisReporter
except ImportError as e:
    # 如果大师级模块不存在，创建占位符
    print(f"⚠️ 大师级模块导入警告: {e}")
    print("将使用基础功能模式")
    
    # 创建简单的占位符类
    class ParameterSpaceExplorer:
        def __init__(self, master_studio): pass
        def run_exploration(self): return {"mode": "basic", "works": []}
    
    class AestheticComparator:
        def __init__(self, master_studio): pass
        def run_comparison(self): return {"comparisons": []}
    
    class CompositionShowcase:
        def __init__(self, master_studio): pass
        def run_showcase(self): return {"showcase_works": []}
    
    class InteractiveWorkshop:
        def __init__(self, master_studio): pass
        def run_session(self): return {"interactions": []}
    
    class MasterworkGenerator:
        def __init__(self, master_studio): pass
        def generate_masterwork_album(self): return {"album": "basic"}
    
    class HighQualitySoundFontRenderer:
        def __init__(self, master_studio): pass
        def render_composition(self, composition, output_path): return output_path
    
    class AnalysisReporter:
        def __init__(self, master_studio): pass
        def generate_comprehensive_report(self): return {"report": "basic"}
    
    # 简化的枚举类
    class ExplorationMode:
        QUICK_SURVEY = "quick_survey"
        SYSTEMATIC_GRID = "systematic_grid"
    
    class ComparisonDimension:
        PHI_VALUES = "phi_values"
        COMPREHENSIVE = "comprehensive"
    
    class ShowcaseType:
        MATHEMATICAL_BEAUTY = "mathematical_beauty"
        VIRTUOSO_PERFORMANCE = "virtuoso_performance"
    
    class WorkshopMode:
        FREE_EXPLORATION = "free_exploration"
        GUIDED_TUTORIAL = "guided_tutorial"
    
    class MasterworkType:
        SOLO_PIANO_ALBUM = "solo_piano_album"
        CONCEPT_ALBUM = "concept_album"
    
    class CompositionQuality:
        STANDARD = "standard"
        HIGH = "high"
        STUDIO = "studio"
    
    class RenderQuality:
        STANDARD = "standard"
        HIGH = "high"
        STUDIO = "studio"

class WorkMode(Enum):
    """工作模式"""
    EXPLORE_MATHEMATICS = "explore_mathematics"         # 探索数学参数空间
    COMPARE_AESTHETICS = "compare_aesthetics"           # 数学美学对比
    SHOWCASE_VIRTUOSITY = "showcase_virtuosity"         # 展示大师级技艺
    INTERACTIVE_WORKSHOP = "interactive_workshop"       # 交互式工作室
    GENERATE_MASTERWORKS = "generate_masterworks"       # 生成大师作品集
    QUICK_PREVIEW = "quick_preview"                     # 快速预览
    ANALYZE_SYSTEM = "analyze_system"                   # 系统分析

class QualityLevel(Enum):
    """质量级别"""
    DRAFT = "draft"                # 草稿质量（快速预览）
    STANDARD = "standard"          # 标准质量
    HIGH = "high"                  # 高质量
    STUDIO = "studio"              # 录音室质量

@dataclass
class MasterStudioConfig:
    """大师工作室配置"""
    # 基础设置
    work_mode: WorkMode = WorkMode.QUICK_PREVIEW
    quality_level: QualityLevel = QualityLevel.STANDARD
    output_directory: Path = Path("../output")
    soundfont_directory: Path = Path("../../Soundfonts")
    
    # 数学参数设置
    phi_values: List[str] = field(default_factory=lambda: ["golden", "octave"])
    delta_theta_values: List[str] = field(default_factory=lambda: ["15.0", "24.0"])
    f_base_values: List[float] = field(default_factory=lambda: [55.0])
    chord_ratio_sets: List[str] = field(default_factory=lambda: ["major_triad"])
    
    # 作曲参数设置
    rhythm_styles: List[str] = field(default_factory=lambda: ["traditional"])
    melody_patterns: List[str] = field(default_factory=lambda: ["balanced"])
    composition_styles: List[str] = field(default_factory=lambda: ["balanced_journey"])
    
    # 演奏技法设置
    technique_levels: List[str] = field(default_factory=lambda: ["basic", "advanced"])
    technique_density: str = "moderate"
    expression_styles: List[str] = field(default_factory=lambda: ["natural"])
    
    # 输出设置
    measures_count: int = 8
    works_count: int = 1
    export_formats: List[str] = field(default_factory=lambda: ["wav"])
    include_analysis: bool = True
    include_midi: bool = True
    
    # SoundFont设置
    preferred_soundfont: str = "GD_Steinway_Model_D274II.sf2"
    alternative_soundfont: str = "GD_Steinway_Model_D274.sf2"
    
    # 实时设置
    realtime_preview: bool = False
    preview_duration: float = 4.0
    
    # 并行处理设置
    enable_parallel_generation: bool = True

def create_default_config() -> MasterStudioConfig:
    """创建默认配置"""
    return MasterStudioConfig()

class PetersenMasterStudio:
    """Petersen大师级音乐创作工作室"""
    
    def __init__(self, config: Optional[MasterStudioConfig] = None):
        """
        初始化大师工作室
        
        Args:
            config: 工作室配置
        """
        self.config = config or create_default_config()
        
        # 核心组件
        self.enhanced_player: Optional[EnhancedPetersenPlayer] = None
        self.current_scale: Optional[PetersenScale] = None
        self.current_composition = None
        
        # 大师级组件
        self.parameter_explorer: Optional[ParameterSpaceExplorer] = None
        self.aesthetic_comparator: Optional[AestheticComparator] = None
        self.composition_showcase: Optional[CompositionShowcase] = None
        self.interactive_workshop: Optional[InteractiveWorkshop] = None
        self.masterwork_generator: Optional[MasterworkGenerator] = None
        self.soundfont_renderer: Optional[HighQualitySoundFontRenderer] = None
        self.analysis_reporter: Optional[AnalysisReporter] = None
        
        # 状态变量
        self.is_initialized = False
        self.session_results = {}
        self.session_start_time = datetime.now()
        
        # 初始化工作室
        self._initialize_studio()
    
    def _initialize_studio(self):
        """初始化工作室"""
        print("=" * 60)
        print("🎹 Petersen Master Studio 正在初始化...")
        print("=" * 60)
        
        try:
            # 创建输出目录
            self.config.output_directory.mkdir(parents=True, exist_ok=True)
            
            # 初始化核心播放器
            self._init_core_player()
            
            # 初始化大师级组件
            self._init_master_components()
            
            # 验证资源
            self._verify_resources()
            
            self.is_initialized = True
            
            print("✓ Petersen Master Studio 初始化完成")
            print(f"✓ 工作模式: {self.config.work_mode.value}")
            print(f"✓ 质量级别: {self.config.quality_level.value}")
            print(f"✓ 输出目录: {self.config.output_directory}")
            print()
            
        except Exception as e:
            print(f"❌ 工作室初始化失败: {e}")
            raise
    
    def _init_core_player(self):
        """初始化核心播放器"""
        try:
            player_config = PlayerConfiguration(
                soundfont_directory=str(self.config.soundfont_directory),
                sample_rate=44100 if self.config.quality_level in [QualityLevel.DRAFT, QualityLevel.STANDARD] else 48000,
                buffer_size=512 if self.config.quality_level != QualityLevel.STUDIO else 256,
                enable_accurate_frequency=True,
                enable_effects=True,
                enable_expression=True
            )
            
            self.enhanced_player = EnhancedPetersenPlayer(player_config)
            
            # 尝试加载首选SoundFont
            if self.enhanced_player.is_initialized:
                success = self.enhanced_player.switch_soundfont(
                    self.config.preferred_soundfont, 
                    quiet_mode=True
                )
                if not success:
                    print(f"⚠️ 首选SoundFont {self.config.preferred_soundfont} 不可用")
                    success = self.enhanced_player.switch_soundfont(
                        self.config.alternative_soundfont,
                        quiet_mode=True
                    )
                    if success:
                        print(f"✓ 使用备选SoundFont: {self.config.alternative_soundfont}")
                    else:
                        print("⚠️ 使用默认SoundFont")
                else:
                    print(f"✓ 使用首选SoundFont: {self.config.preferred_soundfont}")
            
        except Exception as e:
            print(f"⚠️ 核心播放器初始化警告: {e}")
    
    def _init_master_components(self):
        """初始化大师级组件"""
        try:
            # 初始化大师级组件
            self.parameter_explorer = ParameterSpaceExplorer(self)
            self.aesthetic_comparator = AestheticComparator(self)
            self.composition_showcase = CompositionShowcase(self)
            self.interactive_workshop = InteractiveWorkshop(self)
            self.masterwork_generator = MasterworkGenerator(self)

            # 确保播放器可用后再初始化渲染器
            if self.enhanced_player and self.enhanced_player.is_initialized:
                # 为了兼容性，添加player属性指向enhanced_player
                self.player = self.enhanced_player
                self.soundfont_renderer = HighQualitySoundFontRenderer(self)
            else:
                print("⚠️ 播放器不可用，跳过SoundFont渲染器初始化")
                self.soundfont_renderer = None
            
            self.analysis_reporter = AnalysisReporter(self)
            
            print("✓ 大师级组件初始化完成")
            
        except Exception as e:
            print(f"⚠️ 大师级组件初始化警告: {e}")
    
    def _verify_resources(self):
        """验证资源可用性"""
        # 验证SoundFont目录
        if not self.config.soundfont_directory.exists():
            print(f"⚠️ SoundFont目录不存在: {self.config.soundfont_directory}")
        
        # 验证预设参数
        self._verify_parameter_presets()
    
    def _verify_parameter_presets(self):
        """验证参数预设"""
        # 验证φ值预设
        available_phi = list(PHI_PRESETS.keys())
        for phi in self.config.phi_values:
            if phi not in available_phi:
                print(f"⚠️ 未知φ值预设: {phi}")
        
        # 验证δθ值预设 - 修复：支持数值字符串
        available_delta_theta = list(DELTA_THETA_PRESETS.keys())
        for delta_theta in self.config.delta_theta_values:
            if delta_theta not in available_delta_theta:
                # 尝试解析为数值
                try:
                    float(delta_theta)
                    print(f"✓ 自定义δθ值: {delta_theta}")
                except ValueError:
                    print(f"⚠️ 无效δθ值: {delta_theta}")
    
    def run_session(self) -> Dict[str, Any]:
        """运行工作会话"""
        if not self.is_initialized:
            raise RuntimeError("工作室未初始化")
        
        print(f"🎵 开始 {self.config.work_mode.value} 会话...")
        print("-" * 40)
        
        try:
            # 根据工作模式执行相应功能
            if self.config.work_mode == WorkMode.EXPLORE_MATHEMATICS:
                results = self._run_mathematics_exploration()
            
            elif self.config.work_mode == WorkMode.COMPARE_AESTHETICS:
                results = self._run_aesthetic_comparison()
            
            elif self.config.work_mode == WorkMode.SHOWCASE_VIRTUOSITY:
                results = self._run_virtuosity_showcase()
            
            elif self.config.work_mode == WorkMode.INTERACTIVE_WORKSHOP:
                results = self._run_interactive_workshop()
            
            elif self.config.work_mode == WorkMode.GENERATE_MASTERWORKS:
                results = self._run_masterwork_generation()
            
            elif self.config.work_mode == WorkMode.QUICK_PREVIEW:
                results = self._run_quick_preview()
            
            elif self.config.work_mode == WorkMode.ANALYZE_SYSTEM:
                results = self._run_system_analysis()
            
            else:
                raise ValueError(f"未知工作模式: {self.config.work_mode}")
            
            # 保存会话结果
            self.session_results = results
            self._save_session_summary()
            
            print("-" * 40)
            print(f"✓ {self.config.work_mode.value} 会话完成")
            
            return results
            
        except Exception as e:
            print(f"❌ 会话执行失败: {e}")
            raise
    
    def play_generated_work(self, work_path: str, 
                           play_mode: str = "enhanced", 
                           preview_duration: Optional[float] = None) -> bool:
        """
        播放生成的作品
        
        Args:
            work_path: 作品文件路径
            play_mode: 播放模式 ("enhanced", "csv", "realtime")
            preview_duration: 预览时长（秒），None表示播放全部
            
        Returns:
            播放成功返回True
        """
        if not self.is_initialized:
            print("❌ 工作室未初始化")
            return False
        
        work_path = Path(work_path)
        
        try:
            if play_mode == "enhanced" and self.enhanced_player:
                return self._play_with_enhanced_player(work_path, preview_duration)
            
            elif play_mode == "csv":
                return self._play_with_csv_player(work_path, preview_duration)
            
            elif play_mode == "realtime":
                return self._play_with_realtime_renderer(work_path, preview_duration)
            
            else:
                print(f"❌ 未知播放模式: {play_mode}")
                return False
                
        except Exception as e:
            print(f"❌ 播放失败: {e}")
            return False
    
    def _play_with_enhanced_player(self, work_path: Path, preview_duration: Optional[float]) -> bool:
        """使用EnhancedPetersenPlayer播放"""
        print(f"🎵 使用增强播放器播放: {work_path.name}")
        
        # 检查是否有对应的CSV分析文件
        csv_path = work_path.parent / f"{work_path.stem}_analysis.csv"
        
        if csv_path.exists():
            # 导入CSV播放器
            try:
                from csv_player import CSVMusicPlayer
                
                csv_player = CSVMusicPlayer(self.enhanced_player)
                
                if csv_player.load_csv_composition(str(csv_path)):
                    print(f"✓ 加载CSV作曲文件: {csv_path.name}")
                    
                    # 获取作曲信息
                    info = csv_player.get_composition_info()
                    total_duration = info.get("duration", 0)
                    
                    print(f"📊 作曲信息:")
                    print(f"   总音符: {info.get('total_notes', 0)}")
                    print(f"   总时长: {total_duration:.1f}秒")
                    
                    # 确定播放时长
                    if preview_duration and preview_duration < total_duration:
                        print(f"⏯️  预览播放 {preview_duration:.1f}秒")
                        csv_player.play_composition(0, preview_duration)
                    else:
                        print("⏯️  完整播放")
                        csv_player.play_composition()
                    
                    return True
                else:
                    print(f"❌ CSV文件加载失败")
                    return False
                    
            except ImportError as e:
                print(f"⚠️ CSV播放器导入失败: {e}")
                return False
        
        else:
            # 没有CSV文件，尝试其他方式
            print("⚠️ 未找到对应的CSV分析文件，尝试其他播放方式")
            return self._play_with_generic_method(work_path, preview_duration)
    
    def _play_with_csv_player(self, work_path: Path, preview_duration: Optional[float]) -> bool:
        """使用CSV播放器播放（改进版，支持无pandas）"""
        # 查找CSV文件
        if work_path.suffix.lower() == '.csv':
            csv_path = work_path
        else:
            csv_path = work_path.parent / f"{work_path.stem}_analysis.csv"
        
        if not csv_path.exists():
            print(f"❌ CSV文件不存在: {csv_path}")
            return False
        
        try:
            # 首先尝试使用pandas版本的CSV播放器
            try:
                import pandas as pd
                from csv_player import CSVMusicPlayer
                
                csv_player = CSVMusicPlayer(self.enhanced_player)
                
                if csv_player.load_csv_composition(str(csv_path)):
                    print(f"🎵 CSV播放（pandas）: {csv_path.name}")
                    
                    if preview_duration:
                        csv_player.play_composition(0, preview_duration)
                    else:
                        csv_player.play_composition()
                    
                    return True
                else:
                    return False
                    
            except ImportError:
                # pandas不可用，使用内置CSV解析器
                print("⚠️ pandas库未安装，使用内置CSV播放器")
                return self._play_csv_with_builtin_parser(csv_path, preview_duration)
                
        except Exception as e:
            print(f"❌ CSV播放失败: {e}")
            # 最后尝试参数演示播放
            return self._play_parameter_demo_fallback(work_path)
    
    def _play_csv_with_builtin_parser(self, csv_path: Path, preview_duration: Optional[float]) -> bool:
        """使用内置CSV解析器播放（不依赖pandas）"""
        try:
            import csv
            
            print(f"🎵 内置CSV播放: {csv_path.name}")
            
            notes = []
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        note = {
                            'time': float(row.get('时间(秒)', row.get('time', 0))),
                            'frequency': float(row.get('频率(Hz)', row.get('frequency', 440))),
                            'duration': float(row.get('持续时间', row.get('duration', 0.5))),
                            'velocity': int(row.get('力度', row.get('velocity', 80)))
                        }
                        notes.append(note)
                    except (ValueError, KeyError):
                        continue  # 跳过无效行
            
            if not notes:
                print("❌ 未找到有效音符数据")
                return False
            
            print(f"📊 加载了 {len(notes)} 个音符")
            
            # 排序并限制预览
            notes.sort(key=lambda x: x['time'])
            
            if preview_duration:
                notes = [n for n in notes if n['time'] <= preview_duration]
                preview_notes = notes[:30]  # 限制预览音符数量
            else:
                preview_notes = notes[:50]  # 限制总音符数量
            
            # 播放音符
            import time as time_module
            start_time = time_module.time()
            
            for i, note in enumerate(preview_notes):
                # 等待到正确时间
                target_time = note['time']
                elapsed = time_module.time() - start_time
                
                if target_time > elapsed:
                    time_module.sleep(target_time - elapsed)
                
                # 播放音符
                self.enhanced_player.play_single_frequency(
                    frequency=note['frequency'],
                    duration=min(note['duration'] * 0.8, 0.4),  # 限制最大时长
                    velocity=note['velocity'],
                    use_accurate_frequency=True
                )
                
                # 显示进度
                if (i + 1) % 10 == 0:
                    progress = (i + 1) / len(preview_notes) * 100
                    print(f"   播放进度: {progress:.0f}%")
                
                # 预览模式下限制时长
                if preview_duration and target_time >= preview_duration:
                    break
            
            print("✓ 内置CSV播放完成")
            return True
            
        except Exception as e:
            print(f"❌ 内置CSV播放失败: {e}")
            return False
    
    def _play_parameter_demo_fallback(self, work_path: Path) -> bool:
        """参数演示回退播放"""
        try:
            print("🎵 使用参数演示播放")
            
            # 从配置获取参数
            phi_value = PHI_PRESETS.get(self.config.phi_values[0], 1.618)
            delta_theta_value = float(self.config.delta_theta_values[0])
            
            scale = PetersenScale(F_base=55.0, phi=phi_value, delta_theta=delta_theta_value)
            scale_entries = scale.get_scale_entries()[:8]
            
            frequencies = [entry.freq for entry in scale_entries]
            key_names = [entry.key_short for entry in scale_entries]
            
            return self.enhanced_player.play_frequencies(
                frequencies=frequencies,
                key_names=key_names,
                duration=0.4,
                gap=0.1,
                show_progress=True
            )
            
        except Exception as e:
            print(f"❌ 参数演示播放失败: {e}")
            return False
    
    def _play_with_realtime_renderer(self, work_path: Path, preview_duration: Optional[float]) -> bool:
        """使用实时渲染器播放"""
        if not self.soundfont_renderer:
            print("❌ SoundFont渲染器不可用")
            return False
        
        try:
            # 需要从文件重新加载作曲对象
            composition = self._load_composition_from_file(work_path)
            
            if composition:
                duration = preview_duration or 10.0  # 默认预览10秒
                return self.soundfont_renderer.render_composition_realtime(composition, duration)
            else:
                print("❌ 无法从文件加载作曲")
                return False
                
        except Exception as e:
            print(f"❌ 实时渲染播放失败: {e}")
            return False
    
    def _play_with_generic_method(self, work_path: Path, preview_duration: Optional[float]) -> bool:
        """通用播放方法"""
        if not self.enhanced_player:
            return False
        
        # 生成演示音阶
        from petersen_scale import PetersenScale
        
        # 从配置获取参数
        phi_value = PHI_PRESETS.get(self.config.phi_values[0], 1.618)
        delta_theta_value = float(self.config.delta_theta_values[0])
        
        scale = PetersenScale(F_base=55.0, phi=phi_value, delta_theta=delta_theta_value)
        scale_entries = scale.get_scale_entries()[:8]
        
        print(f"🎵 演示音阶播放 (φ={phi_value:.3f}, δθ={delta_theta_value:.1f}°)")
        
        frequencies = [entry.freq for entry in scale_entries]
        key_names = [entry.key_short for entry in scale_entries]
        
        # 调整播放时长
        duration = min(preview_duration or 4.0, 0.6)
        
        return self.enhanced_player.play_frequencies(
            frequencies=frequencies,
            key_names=key_names,
            duration=duration,
            gap=0.1,
            show_progress=True
        )
    
    def _load_composition_from_file(self, work_path: Path):
        """从文件加载作曲对象（占位符方法）"""
        # 这个方法需要根据实际的文件格式实现
        # 目前返回None，表示不支持从文件重新加载
        print("⚠️ 暂不支持从文件重新加载作曲对象")
        return None
    
    def play_all_generated_works(self, mode: str = "enhanced", preview_only: bool = True) -> int:
        """
        播放所有生成的作品
        
        Args:
            mode: 播放模式
            preview_only: 是否只播放预览
            
        Returns:
            成功播放的作品数量
        """
        if not self.session_results or "generated_works" not in self.session_results:
            print("❌ 没有找到生成的作品")
            return 0
        
        works = self.session_results["generated_works"]
        success_count = 0
        
        print(f"🎵 播放 {len(works)} 个生成的作品...")
        
        for i, work in enumerate(works):
            print(f"\n🎼 播放作品 {i+1}/{len(works)}: {work['work_name']}")
            
            # 查找文件
            work_files = work.get("files", [])
            play_file = None
            
            # 优先选择CSV文件
            for file_path in work_files:
                if file_path.endswith("_analysis.csv"):
                    play_file = file_path
                    break
            
            # 如果没有CSV，选择第一个文件
            if not play_file and work_files:
                play_file = work_files[0]
            
            if play_file:
                preview_duration = 6.0 if preview_only else None
                
                success = self.play_generated_work(play_file, mode, preview_duration)
                if success:
                    success_count += 1
                    print(f"   ✓ 播放成功")
                else:
                    print(f"   ❌ 播放失败")
                
                # 作品间暂停
                if i < len(works) - 1:
                    print("   ⏸️  间隔暂停...")
                    time.sleep(2.0)
            else:
                print(f"   ⚠️ 未找到可播放文件")
        
        print(f"\n✓ 播放完成，成功: {success_count}/{len(works)}")
        return success_count

    def _run_mathematics_exploration(self) -> Dict[str, Any]:
        """运行数学参数空间探索"""
        print("🔍 探索Petersen数学参数空间...")
        
        results = {
            "mode": "mathematics_exploration",
            "parameter_combinations": [],
            "generated_works": [],
            "analysis_reports": []
        }
        
        try:
            # 生成参数组合
            parameter_combinations = self._generate_parameter_combinations()
            
            print(f"📊 生成了 {len(parameter_combinations)} 个参数组合")
            
            # 为每个参数组合生成作品
            for i, params in enumerate(parameter_combinations):
                try:
                    print(f"\n🎵 生成作品 {i+1}/{len(parameter_combinations)}")
                    print(f"   参数: φ={params['phi_value']:.3f}, δθ={params['delta_theta_value']:.1f}°")
                    
                    # 创建作曲
                    composition = self._create_composition_from_params(params)
                    
                    if composition:
                        # 保存作品
                        work_name = f"exploration_{i+1:02d}_phi{params['phi_value']:.3f}_dt{params['delta_theta_value']:.1f}"
                        work_result = self._save_composition_work(composition, work_name, params)
                        
                        # 添加到结果
                        results["parameter_combinations"].append(params)
                        results["generated_works"].append(work_result)
                        
                        print(f"   ✓ 作品生成成功: {work_name}")
                    else:
                        print(f"   ❌ 作品生成失败")
                        
                except Exception as e:
                    print(f"   ❌ 参数组合 {i+1} 失败: {e}")
                    continue
            
            # 生成探索报告
            if results["generated_works"]:
                analysis_report = self._generate_exploration_analysis(results)
                results["analysis_reports"].append(analysis_report)
            
            # 添加播放选项
            if results["generated_works"] and self.enhanced_player and self.enhanced_player.is_initialized:
                print(f"\n🎵 是否播放生成的作品预览？")
                print(f"   生成了 {len(results['generated_works'])} 个作品")
                
                # 自动播放前几个作品的预览
                preview_count = min(4, len(results["generated_works"]))
                print(f"🎼 自动播放前 {preview_count} 个作品预览...")
                
                for i in range(preview_count):
                    work = results["generated_works"][i]
                    print(f"\n🎵 预览作品 {i+1}: {work['work_name']}")
                    
                    # 查找CSV文件
                    csv_file = None
                    for file_path in work.get("files", []):
                        if file_path.endswith("_analysis.csv"):
                            csv_file = file_path
                            break
                    
                    if csv_file:
                        success = self.play_generated_work(csv_file, "csv", 4.0)  # 4秒预览
                        if success:
                            print(f"   ✓ 预览播放完成")
                        else:
                            print(f"   ⚠️ 预览播放失败")
                    
                    # 预览间暂停
                    if i < preview_count - 1:
                        time.sleep(1.5)
            
        except Exception as e:
            print(f"❌ 数学探索失败: {e}")
            results["error"] = str(e)
        
        return results
    
    def _generate_parameter_combinations(self) -> List[Dict[str, Any]]:
        """生成参数组合"""
        combinations = []
        
        # 解析φ值
        phi_values = []
        for phi_str in self.config.phi_values:
            if phi_str in PHI_PRESETS:
                phi_values.append(PHI_PRESETS[phi_str])
            else:
                try:
                    phi_values.append(float(phi_str))
                except ValueError:
                    print(f"⚠️ 跳过无效φ值: {phi_str}")
                    continue
        
        # 解析δθ值
        delta_theta_values = []
        for dt_str in self.config.delta_theta_values:
            if dt_str in DELTA_THETA_PRESETS:
                delta_theta_values.append(DELTA_THETA_PRESETS[dt_str])
            else:
                try:
                    delta_theta_values.append(float(dt_str))
                except ValueError:
                    print(f"⚠️ 跳过无效δθ值: {dt_str}")
                    continue
        
        # 生成组合
        for phi in phi_values:
            for delta_theta in delta_theta_values:
                for f_base in self.config.f_base_values:
                    combinations.append({
                        "phi_value": phi,
                        "delta_theta_value": delta_theta,
                        "f_base": f_base,
                        "chord_ratios": CHORD_RATIOS.get(
                            self.config.chord_ratio_sets[0], 
                            CHORD_RATIOS["major_triad"]
                        ),
                        "composition_style": self.config.composition_styles[0]
                    })
        
        return combinations
    
    def _generate_exploration_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成探索分析报告"""
        analysis = {
            "exploration_summary": {
                "total_combinations": len(results["parameter_combinations"]),
                "successful_works": len(results["generated_works"]),
                "success_rate": len(results["generated_works"]) / max(1, len(results["parameter_combinations"]))
            },
            "parameter_analysis": {
                "phi_range": [],
                "delta_theta_range": [],
                "most_successful_params": None
            },
            "musical_analysis": {
                "complexity_scores": [],
                "harmonic_richness": [],
                "rhythmic_variety": []
            }
        }
        
        if results["parameter_combinations"]:
            # 分析φ值范围
            phi_values = [p["phi_value"] for p in results["parameter_combinations"]]
            analysis["parameter_analysis"]["phi_range"] = [min(phi_values), max(phi_values)]
            
            # 分析δθ值范围
            dt_values = [p["delta_theta_value"] for p in results["parameter_combinations"]]
            analysis["parameter_analysis"]["delta_theta_range"] = [min(dt_values), max(dt_values)]
            
            # 最成功的参数组合（简化版）
            if results["generated_works"]:
                analysis["parameter_analysis"]["most_successful_params"] = results["parameter_combinations"][0]
        
        return analysis
    
    def _run_aesthetic_comparison(self) -> Dict[str, Any]:
        """运行数学美学对比"""
        print("🎨 进行数学美学对比分析...")
        
        results = {
            "mode": "aesthetic_comparison",
            "base_theme": "mathematical_beauty",
            "variations": [],
            "comparison_metrics": {}
        }
        
        try:
            # 运行美学对比
            comparison_result = self.aesthetic_comparator.run_comparison(
                dimension=ComparisonDimension.PHI_VALUES if len(self.config.phi_values) > 1 else ComparisonDimension.COMPREHENSIVE
            )
            
            # 整合结果
            results["variations"] = [
                {
                    "parameters": params,
                    "aesthetic_score": score.__dict__ if hasattr(score, '__dict__') else score
                }
                for params, score in zip(comparison_result.parameter_sets, comparison_result.aesthetic_scores)
            ]
            results["comparison_metrics"] = {
                "ranking": comparison_result.ranking,
                "insights": comparison_result.insights,
                "recommendations": comparison_result.recommendations
            }
            
        except Exception as e:
            print(f"❌ 美学对比失败: {e}")
            results["error"] = str(e)
        
        return results
    
    def _run_virtuosity_showcase(self) -> Dict[str, Any]:
        """运行大师级技艺展示"""
        print("🎭 展示Petersen大师级演奏技艺...")
        
        results = {
            "mode": "virtuosity_showcase",
            "showcase_pieces": [],
            "technique_demonstrations": []
        }
        
        try:
            # 运行作曲展示
            showcase_session = self.composition_showcase.run_showcase("virtuoso_recital")
            
            # 整合结果
            results["showcase_pieces"] = [
                {
                    "title": work.title,
                    "showcase_type": work.showcase_type.value if hasattr(work.showcase_type, 'value') else str(work.showcase_type),
                    "complexity_score": work.structural_analysis.get("complexity_score", 0),
                    "files": work.generated_files
                }
                for work in showcase_session.showcase_works
            ]
            
        except Exception as e:
            print(f"❌ 技艺展示失败: {e}")
            results["error"] = str(e)
        
        return results
    
    def _run_interactive_workshop(self) -> Dict[str, Any]:
        """运行交互式工作室"""
        print("🛠️ 启动交互式参数工作室...")
        
        results = {
            "mode": "interactive_workshop",
            "session_duration": 0,
            "interactions": [],
            "final_creation": None
        }
        
        try:
            # 运行交互式会话
            workshop_results = self.interactive_workshop.run_session(WorkshopMode.FREE_EXPLORATION)
            
            # 整合结果
            results.update(workshop_results)
            
        except Exception as e:
            print(f"❌ 交互式工作室失败: {e}")
            results["error"] = str(e)
        
        return results
    
    def _run_masterwork_generation(self) -> Dict[str, Any]:
        """运行大师作品集生成"""
        print("🏆 生成Petersen大师作品集...")
        
        results = {
            "mode": "masterwork_generation",
            "collection_theme": "petersen_mathematical_beauty",
            "masterworks": [],
            "collection_analysis": {}
        }
        
        try:
            # 生成大师作品
            album = self.masterwork_generator.generate_masterwork_album(
                album_template="golden_ratio_variations",
                quality_level=CompositionQuality.STUDIO if self.config.quality_level == QualityLevel.STUDIO else CompositionQuality.HIGH
            )
            
            # 整合结果
            results["masterworks"] = [{
                "album_id": album.album_id,
                "title": album.title,
                "track_count": len(album.tracks),
                "quality_score": album.overall_quality_score
            }]
            
        except Exception as e:
            print(f"❌ 大师作品生成失败: {e}")
            results["error"] = str(e)
        
        return results
    
    def _run_quick_preview(self) -> Dict[str, Any]:
        """运行快速预览"""
        print("⚡ 快速预览Petersen音乐系统...")
        
        results = {
            "mode": "quick_preview",
            "preview_items": [],
            "system_info": {}
        }
        
        try:
            # 展示基础音阶
            print("🎵 预览基础音阶...")
            scale = PetersenScale(F_base=55.0, phi=1.618, delta_theta=15.0)
            scale_entries = scale.get_scale_entries()[:8]
            
            if self.enhanced_player and self.enhanced_player.is_initialized:
                frequencies = [entry.freq for entry in scale_entries]
                key_names = [entry.key_short for entry in scale_entries]
                
                success = self.enhanced_player.play_frequencies(
                    frequencies=frequencies,
                    key_names=key_names,
                    duration=0.4,
                    gap=0.1,
                    use_accurate_frequency=True,
                    show_progress=True
                )
                
                if success:
                    results["preview_items"].append({
                        "type": "scale_preview",
                        "description": "Petersen基础音阶（黄金比例）",
                        "success": True
                    })
            
            # 快速创作演示
            print("\n🎼 快速作曲演示...")
            quick_composition = self._create_quick_demo_composition()
            
            if quick_composition:
                results["preview_items"].append({
                    "type": "composition_demo",
                    "description": "Petersen自动作曲演示",
                    "success": True
                })
                
                # 保存演示作品
                demo_name = f"quick_preview_{int(time.time())}"
                self._save_composition_work(quick_composition, demo_name, {})
            
            # 系统信息
            results["system_info"] = self._collect_system_info()
            
        except Exception as e:
            print(f"❌ 快速预览失败: {e}")
            results["error"] = str(e)
        
        return results
    
    def _run_system_analysis(self) -> Dict[str, Any]:
        """运行系统分析"""
        print("📊 分析Petersen音乐系统...")
        
        try:
            analysis_report = self.analysis_reporter.generate_comprehensive_report()
            return {
                "mode": "system_analysis",
                "report": analysis_report.__dict__ if hasattr(analysis_report, '__dict__') else analysis_report
            }
        except Exception as e:
            print(f"❌ 系统分析失败: {e}")
            return {
                "mode": "system_analysis",
                "error": str(e)
            }
    
    # === 辅助方法 ===
    
    def _create_composition_from_params(self, params: Dict[str, Any]):
        """从参数创建作曲"""
        # 创建基础音阶
        scale = PetersenScale(
            F_base=params.get('f_base', 55.0),
            phi=params.get('phi_value', 1.618),
            delta_theta=params.get('delta_theta_value', 15.0)
        )
        
        # 创建和弦扩展
        chord_extender = PetersenChordExtender(
            petersen_scale=scale,
            chord_ratios=params.get('chord_ratios', CHORD_RATIOS['major_triad'])
        )
        
        # 创建作曲器
        style_name = params.get('composition_style', 'balanced_journey')
        composition_style = COMPOSITION_STYLES.get(style_name, COMPOSITION_STYLES['balanced_journey'])
        
        composer = PetersenAutoComposer(
            petersen_scale=scale,
            chord_extender=chord_extender,
            composition_style=composition_style,
            bpm=120
        )
        
        # 生成作曲
        return composer.compose(measures=self.config.measures_count)
    
    def _create_quick_demo_composition(self):
        """创建快速演示作品"""
        try:
            params = {
                "f_base": 55.0,
                "phi_value": 1.618,
                "delta_theta_value": 15.0,
                "chord_ratios": CHORD_RATIOS["major_triad"]
            }
            
            return self._create_composition_from_params(params)
            
        except Exception as e:
            print(f"❌ 快速演示作品创建失败: {e}")
            return None
    
    def _save_composition_work(self, composition, work_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """保存作曲作品"""
        work_results = {
            "work_name": work_name,
            "timestamp": datetime.now().isoformat(),
            "parameters": params,
            "files": []
        }
        
        try:
            # 创建作品目录
            work_dir = self.config.output_directory / work_name
            work_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存MIDI文件
            if self.config.include_midi and hasattr(composition, 'export_midi'):
                midi_path = work_dir / f"{work_name}.mid"
                composition.export_midi(str(midi_path))
                work_results["files"].append(str(midi_path))
                print(f"   ✓ MIDI已保存: {midi_path.name}")
            
            # 保存CSV分析文件
            if self.config.include_analysis and hasattr(composition, 'export_score_csv'):
                csv_path = work_dir / f"{work_name}_analysis.csv"
                composition.export_score_csv(str(csv_path))
                work_results["files"].append(str(csv_path))
                print(f"   ✓ 分析已保存: {csv_path.name}")
            
            # 保存参数文件
            params_path = work_dir / f"{work_name}_parameters.json"
            with open(params_path, 'w', encoding='utf-8') as f:
                json.dump(params, f, indent=2, ensure_ascii=False)
            work_results["files"].append(str(params_path))
            
            print(f"   ✓ 作品已保存到: {work_dir}")
            
        except Exception as e:
            print(f"   ❌ 作品保存失败: {e}")
        
        return work_results
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """收集系统信息"""
        info = {
            "petersen_studio_version": "1.0.0",
            "initialization_status": self.is_initialized,
            "session_start_time": self.session_start_time.isoformat(),
            "configuration": {
                "output_directory": str(self.config.output_directory),
                "quality_level": self.config.quality_level.value,
                "soundfont_directory": str(self.config.soundfont_directory)
            }
        }
        
        if self.enhanced_player:
            info["player_status"] = {
                "initialized": self.enhanced_player.is_initialized,
                "current_soundfont": getattr(self.enhanced_player, 'current_soundfont', 'unknown')
            }
        
        return info
    
    def _save_session_summary(self):
        """保存会话摘要"""
        try:
            summary = {
                "session_info": {
                    "mode": self.config.work_mode.value,
                    "start_time": self.session_start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "quality_level": self.config.quality_level.value
                },
                "configuration": {
                    "measures_count": self.config.measures_count,
                    "works_count": self.config.works_count,
                    "export_formats": self.config.export_formats,
                    "phi_values": self.config.phi_values,
                    "delta_theta_values": self.config.delta_theta_values
                },
                "results": self.session_results
            }
            
            summary_path = self.config.output_directory / f"session_summary_{int(time.time())}.json"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"📋 会话摘要已保存: {summary_path}")
            
        except Exception as e:
            print(f"⚠️ 会话摘要保存失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        if self.enhanced_player:
            self.enhanced_player.cleanup()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

def parse_command_line_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Petersen Master Studio - 大师级音乐创作工作室",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 探索数学参数空间
  python3 petersen_master_studio.py --explore-mathematics --phi-values golden,octave --measures 8
  
  # 数学美学对比
  python3 petersen_master_studio.py --compare-aesthetics --variations 3
  
  # 展示大师级技艺
  python3 petersen_master_studio.py --showcase-virtuosity --quality studio
  
  # 交互式工作室
  python3 petersen_master_studio.py --interactive-workshop --realtime-preview
  
  # 生成大师作品集
  python3 petersen_master_studio.py --generate-masterworks --works-count 5
  
  # 快速预览
  python3 petersen_master_studio.py --quick-preview
        """
    )
    
    # 工作模式选择（互斥）
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--explore-mathematics', action='store_true',
                           help='探索数学参数空间')
    mode_group.add_argument('--compare-aesthetics', action='store_true',
                           help='进行数学美学对比')
    mode_group.add_argument('--showcase-virtuosity', action='store_true',
                           help='展示大师级演奏技艺')
    mode_group.add_argument('--interactive-workshop', action='store_true',
                           help='启动交互式参数工作室')
    mode_group.add_argument('--generate-masterworks', action='store_true',
                           help='生成大师作品集')
    mode_group.add_argument('--quick-preview', action='store_true',
                           help='快速预览系统功能')
    mode_group.add_argument('--analyze-system', action='store_true',
                           help='分析系统能力')
    
    # 数学参数设置
    parser.add_argument('--phi-values', type=str, default='golden,octave',
                       help='φ值预设，逗号分隔 (默认: golden,octave)')
    parser.add_argument('--delta-theta-values', type=str, default='15.0,24.0',
                       help='δθ值预设，逗号分隔 (默认: 15.0,24.0)')
    parser.add_argument('--f-base', type=float, default=55.0,
                       help='基础频率 (默认: 55.0)')
    parser.add_argument('--chord-sets', type=str, default='major_triad',
                       help='和弦比率集合 (默认: major_triad)')
    
    # 作曲设置
    parser.add_argument('--measures', type=int, default=8,
                       help='作品小节数 (默认: 8)')
    parser.add_argument('--works-count', type=int, default=1,
                       help='生成作品数量 (默认: 1)')
    parser.add_argument('--composition-styles', type=str, default='balanced_journey',
                       help='作曲风格 (默认: balanced_journey)')
    
    # 质量与输出设置
    parser.add_argument('--quality', choices=['draft', 'standard', 'high', 'studio'],
                       default='standard', help='质量级别 (默认: standard)')
    parser.add_argument('--output-dir', type=str, default='../output',
                       help='输出目录 (默认: ../output)')
    parser.add_argument('--export-formats', type=str, default='wav,midi',
                       help='导出格式，逗号分隔 (默认: wav,midi)')
    
    # 实时与交互设置
    parser.add_argument('--realtime-preview', action='store_true',
                       help='启用实时预览')
    parser.add_argument('--preview-duration', type=float, default=4.0,
                       help='预览时长(秒) (默认: 4.0)')
    
    # SoundFont设置
    parser.add_argument('--soundfont-dir', type=str, default='../../Soundfonts',
                       help='SoundFont目录 (默认: ../../Soundfonts)')
    parser.add_argument('--preferred-soundfont', type=str, 
                       default='GD_Steinway_Model_D274II.sf2',
                       help='首选SoundFont文件')
    
    # 分析设置
    parser.add_argument('--include-analysis', action='store_true', default=True,
                       help='包含分析报告')
    parser.add_argument('--include-midi', action='store_true', default=True,
                       help='包含MIDI导出')
    
    # 技法设置
    parser.add_argument('--technique-levels', type=str, default='basic,advanced',
                       help='演奏技法级别 (默认: basic,advanced)')
    parser.add_argument('--technique-density', choices=['sparse', 'moderate', 'rich', 'extreme'],
                       default='moderate', help='技法密度 (默认: moderate)')
    
    return parser.parse_args()

def create_config_from_args(args) -> MasterStudioConfig:
    """从命令行参数创建配置"""
    
    # 确定工作模式
    if args.explore_mathematics:
        work_mode = WorkMode.EXPLORE_MATHEMATICS
    elif args.compare_aesthetics:
        work_mode = WorkMode.COMPARE_AESTHETICS
    elif args.showcase_virtuosity:
        work_mode = WorkMode.SHOWCASE_VIRTUOSITY
    elif args.interactive_workshop:
        work_mode = WorkMode.INTERACTIVE_WORKSHOP
    elif args.generate_masterworks:
        work_mode = WorkMode.GENERATE_MASTERWORKS
    elif args.quick_preview:
        work_mode = WorkMode.QUICK_PREVIEW
    elif args.analyze_system:
        work_mode = WorkMode.ANALYZE_SYSTEM
    else:
        work_mode = WorkMode.QUICK_PREVIEW  # 默认
    
    # 创建配置
    config = MasterStudioConfig(
        work_mode=work_mode,
        quality_level=QualityLevel(args.quality),
        output_directory=Path(args.output_dir),
        soundfont_directory=Path(args.soundfont_dir),
        
        # 数学参数
        phi_values=args.phi_values.split(','),
        delta_theta_values=args.delta_theta_values.split(','),
        f_base_values=[args.f_base],
        chord_ratio_sets=args.chord_sets.split(','),
        
        # 作曲设置
        composition_styles=args.composition_styles.split(','),
        measures_count=args.measures,
        works_count=args.works_count,
        
        # 输出设置
        export_formats=args.export_formats.split(','),
        include_analysis=args.include_analysis,
        include_midi=args.include_midi,
        
        # 实时设置
        realtime_preview=args.realtime_preview,
        preview_duration=args.preview_duration,
        
        # SoundFont设置
        preferred_soundfont=args.preferred_soundfont,
        
        # 技法设置
        technique_levels=args.technique_levels.split(','),
        technique_density=args.technique_density
    )
    
    return config

def main():
    """主函数"""
    print("🎹 Petersen Master Studio 启动中...")
    print("=" * 60)
    
    try:
        # 解析命令行参数
        args = parse_command_line_args()
        
        # 创建配置
        config = create_config_from_args(args)
        
        # 创建并运行工作室
        with PetersenMasterStudio(config) as studio:
            results = studio.run_session()
            
            # 显示结果摘要
            print("\n" + "=" * 60)
            print("🎉 会话完成！结果摘要:")
            print("=" * 60)
            
            if results:
                print(f"📊 模式: {results.get('mode', 'unknown')}")
                
                if 'generated_works' in results:
                    print(f"🎼 生成作品: {len(results['generated_works'])} 首")
                
                if 'variations' in results:
                    print(f"🎨 美学变奏: {len(results['variations'])} 个")
                
                if 'masterworks' in results:
                    print(f"🏆 大师作品: {len(results['masterworks'])} 首")
                
                if 'preview_items' in results:
                    print(f"⚡ 预览项目: {len(results['preview_items'])} 个")
            
            print(f"📁 输出目录: {config.output_directory}")
            print("\n✨ 感谢使用 Petersen Master Studio！")
        
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🎹 Petersen Master Studio 已退出")

if __name__ == "__main__":
    main()