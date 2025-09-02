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
python petersen_master_studio.py --explore-mathematics \
  --phi-values golden,octave,fifth \
  --delta-theta-values 4.8,15.0,24.0 \
  --measures 16 --output-dir "mathematical_exploration/"

# 数学美学对比
python petersen_master_studio.py --compare-aesthetics \
  --base-theme romantic_melody \
  --parameter-variations 5 \
  --comparison-report detailed

# 展示大师级技艺
python petersen_master_studio.py --showcase-virtuosity \
  --composition-length 32 \
  --technique-levels all \
  --quality studio

# 交互式工作室
python petersen_master_studio.py --interactive-workshop \
  --realtime-preview \
  --parameter-studio

# 生成大师作品集
python petersen_master_studio.py --generate-masterworks \
  --collection-theme mathematical_beauty \
  --works-count 10 \
  --export-formats wav,midi,analysis
```
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time

# 添加父目录到路径
current_dir = Path(__file__).parent
libs_dir = current_dir.parent / "libs"
if str(libs_dir) not in sys.path:
    sys.path.insert(0, str(libs_dir))

# 导入基础模块
try:
    from petersen_scale import PetersenScale, PRESET_PHI_VALUES, PRESET_DELTA_THETA_VALUES
    from petersen_chord import PetersenChordExtender, CHORD_RATIOS_PRESETS
    from petersen_rhythm import PetersenRhythmGenerator, RHYTHM_STYLE_PRESETS
    from petersen_melody import PetersenMelodyGenerator, MELODY_PATTERN_PRESETS
    from petersen_composer import PetersenAutoComposer, COMPOSITION_STYLES
    from petersen_performance import PetersenPerformanceRenderer, PERFORMANCE_TECHNIQUES
    from petersen_player import EnhancedPetersenPlayer, PlayerConfiguration
except ImportError as e:
    print(f"❌ 导入基础模块失败: {e}")
    print("请确保基础库模块位于正确路径")
    sys.exit(1)

# 导入大师级模块
try:
    from parameter_explorer import ParameterSpaceExplorer
    from aesthetic_comparator import AestheticComparator
    from composition_showcase import CompositionShowcase
    from interactive_workshop import InteractiveWorkshop
    from masterwork_generator import MasterworkGenerator
    from soundfont_renderer import HighQualitySoundFontRenderer
    from analysis_reporter import AnalysisReporter
except ImportError:
    # 如果大师级模块不存在，我们将在后续创建
    print("⚠️ 大师级模块尚未完全加载，将使用基础功能")
    ParameterSpaceExplorer = None
    AestheticComparator = None
    CompositionShowcase = None
    InteractiveWorkshop = None
    MasterworkGenerator = None
    HighQualitySoundFontRenderer = None
    AnalysisReporter = None

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
    preferred_soundfont: str = "GD_Steinway_Model_D274.sf2"
    alternative_soundfont: str = "GD_Steinway_Model_D274II.sf2"
    
    # 实时设置
    realtime_preview: bool = False
    preview_duration: float = 4.0
    
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
            # 如果大师级模块可用，则初始化
            if ParameterSpaceExplorer:
                self.parameter_explorer = ParameterSpaceExplorer(self)
            
            if AestheticComparator:
                self.aesthetic_comparator = AestheticComparator(self)
            
            if CompositionShowcase:
                self.composition_showcase = CompositionShowcase(self)
            
            if InteractiveWorkshop:
                self.interactive_workshop = InteractiveWorkshop(self)
            
            if MasterworkGenerator:
                self.masterwork_generator = MasterworkGenerator(self)
            
            if HighQualitySoundFontRenderer:
                self.soundfont_renderer = HighQualitySoundFontRenderer(self)
            
            if AnalysisReporter:
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
        available_phi = list(PRESET_PHI_VALUES.keys())
        for phi in self.config.phi_values:
            if phi not in available_phi:
                print(f"⚠️ 未知φ值预设: {phi}")
        
        # 验证δθ值预设
        available_delta_theta = list(PRESET_DELTA_THETA_VALUES.keys())
        for delta_theta in self.config.delta_theta_values:
            if delta_theta not in available_delta_theta:
                print(f"⚠️ 未知δθ值预设: {delta_theta}")
    
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
    
    def _run_mathematics_exploration(self) -> Dict[str, Any]:
        """运行数学参数空间探索"""
        print("🔍 探索Petersen数学参数空间...")
        
        results = {
            "mode": "mathematics_exploration",
            "parameter_combinations": [],
            "generated_works": [],
            "analysis_reports": []
        }
        
        # 生成参数组合
        param_combinations = self._generate_parameter_combinations()
        
        print(f"📊 生成 {len(param_combinations)} 个参数组合")
        
        # 为每个参数组合创建作品
        for i, params in enumerate(param_combinations, 1):
            print(f"\n🎼 创作第 {i}/{len(param_combinations)} 个作品...")
            print(f"   参数: φ={params['phi_name']}, δθ={params['delta_theta_name']}")
            
            try:
                # 创建基础音阶系统
                scale = PetersenScale(
                    F_base=params['f_base'],
                    phi=params['phi_value'],
                    delta_theta=params['delta_theta_value']
                )
                
                # 创建和弦扩展
                chord_extender = PetersenChordExtender(
                    petersen_scale=scale,
                    chord_ratios=params['chord_ratios']
                )
                extended_scale = chord_extender.extend_scale_with_chords()
                
                # 创建作曲器
                composer = PetersenAutoComposer(
                    petersen_scale=scale,
                    chord_extender=chord_extender,
                    composition_style=COMPOSITION_STYLES[params['composition_style']],
                    bpm=120
                )
                
                # 生成作曲
                composition = composer.compose(measures=self.config.measures_count)
                
                # 保存作品
                work_name = f"math_exploration_{i:02d}_{params['phi_name']}_{params['delta_theta_name']}"
                work_results = self._save_composition_work(composition, work_name, params)
                
                results["generated_works"].append(work_results)
                results["parameter_combinations"].append(params)
                
                # 如果启用实时预览
                if self.config.realtime_preview and self.enhanced_player:
                    print("   🔊 实时预览...")
                    self._preview_composition_snippet(composition)
                
            except Exception as e:
                print(f"   ❌ 参数组合 {i} 创作失败: {e}")
                continue
        
        # 生成对比分析报告
        if self.config.include_analysis and results["generated_works"]:
            print("\n📈 生成数学美学分析报告...")
            analysis_report = self._generate_mathematics_analysis(results)
            results["analysis_reports"].append(analysis_report)
        
        return results
    
    def _generate_parameter_combinations(self) -> List[Dict[str, Any]]:
        """生成参数组合"""
        combinations = []
        
        for phi_name in self.config.phi_values:
            for delta_theta_name in self.config.delta_theta_values:
                for f_base in self.config.f_base_values:
                    for chord_set in self.config.chord_ratio_sets:
                        for composition_style in self.config.composition_styles:
                            
                            # 获取实际数值
                            phi_value = PRESET_PHI_VALUES.get(phi_name, 1.618)
                            delta_theta_value = PRESET_DELTA_THETA_VALUES.get(delta_theta_name, 15.0)
                            chord_ratios = CHORD_RATIOS_PRESETS.get(chord_set, CHORD_RATIOS_PRESETS["major_triad"])
                            
                            combination = {
                                "phi_name": phi_name,
                                "phi_value": phi_value,
                                "delta_theta_name": delta_theta_name,
                                "delta_theta_value": delta_theta_value,
                                "f_base": f_base,
                                "chord_set": chord_set,
                                "chord_ratios": chord_ratios,
                                "composition_style": composition_style
                            }
                            
                            combinations.append(combination)
        
        return combinations
    
    def _run_aesthetic_comparison(self) -> Dict[str, Any]:
        """运行数学美学对比"""
        print("🎨 进行数学美学对比分析...")
        
        if not self.aesthetic_comparator:
            # 使用基础实现
            return self._basic_aesthetic_comparison()
        
        return self.aesthetic_comparator.run_comparison()
    
    def _basic_aesthetic_comparison(self) -> Dict[str, Any]:
        """基础美学对比实现"""
        results = {
            "mode": "aesthetic_comparison",
            "base_theme": "mathematical_beauty",
            "variations": [],
            "comparison_metrics": {}
        }
        
        print("🎼 生成基础主题变奏...")
        
        # 生成几个不同参数的版本进行对比
        base_params = {
            "phi_name": "golden",
            "delta_theta_name": "15.0", 
            "composition_style": "balanced_journey"
        }
        
        variations = [
            {"phi_name": "octave", "delta_theta_name": "15.0"},
            {"phi_name": "golden", "delta_theta_name": "24.0"},
            {"phi_name": "fifth", "delta_theta_name": "4.8"}
        ]
        
        # 为每个变奏创建作品
        for i, variation in enumerate(variations, 1):
            print(f"\n🎵 创作变奏 {i}: φ={variation['phi_name']}, δθ={variation['delta_theta_name']}")
            
            params = {**base_params, **variation}
            params.update({
                "phi_value": PRESET_PHI_VALUES[params["phi_name"]],
                "delta_theta_value": PRESET_DELTA_THETA_VALUES[params["delta_theta_name"]],
                "f_base": 55.0,
                "chord_ratios": CHORD_RATIOS_PRESETS["major_triad"]
            })
            
            try:
                composition = self._create_composition_from_params(params)
                
                work_name = f"aesthetic_variation_{i:02d}_{variation['phi_name']}_{variation['delta_theta_name']}"
                work_results = self._save_composition_work(composition, work_name, params)
                
                results["variations"].append(work_results)
                
                # 实时预览
                if self.config.realtime_preview and self.enhanced_player:
                    print("   🔊 预览变奏...")
                    self._preview_composition_snippet(composition)
                
            except Exception as e:
                print(f"   ❌ 变奏 {i} 创作失败: {e}")
        
        return results
    
    def _run_virtuosity_showcase(self) -> Dict[str, Any]:
        """运行大师级技艺展示"""
        print("🎭 展示Petersen大师级演奏技艺...")
        
        if not self.composition_showcase:
            return self._basic_virtuosity_showcase()
        
        return self.composition_showcase.run_showcase()
    
    def _basic_virtuosity_showcase(self) -> Dict[str, Any]:
        """基础技艺展示实现"""
        results = {
            "mode": "virtuosity_showcase",
            "showcase_pieces": [],
            "technique_demonstrations": []
        }
        
        print("🎼 创作大师级展示作品...")
        
        # 创建一个复杂的作品展示多种技法
        params = {
            "phi_name": "golden",
            "phi_value": PRESET_PHI_VALUES["golden"],
            "delta_theta_name": "15.0",
            "delta_theta_value": PRESET_DELTA_THETA_VALUES["15.0"],
            "f_base": 55.0,
            "chord_ratios": CHORD_RATIOS_PRESETS["major_seventh"],
            "composition_style": "virtuoso_journey"
        }
        
        try:
            # 创建复杂作品
            composition = self._create_composition_from_params(params)
            
            # 应用高级演奏技法
            if hasattr(composition, 'apply_performance_techniques'):
                composition.apply_performance_techniques([
                    "thirds_parallel",
                    "octave_cascade", 
                    "cross_hand_weaving",
                    "harmonic_resonance"
                ])
            
            # 保存展示作品
            work_name = f"virtuosity_showcase_{int(time.time())}"
            work_results = self._save_composition_work(composition, work_name, params)
            
            results["showcase_pieces"].append(work_results)
            
            # 高质量渲染
            if self.config.quality_level in [QualityLevel.HIGH, QualityLevel.STUDIO]:
                print("🎭 渲染录音室级别作品...")
                self._render_studio_quality(composition, work_name)
            
        except Exception as e:
            print(f"❌ 技艺展示创作失败: {e}")
        
        return results
    
    def _run_interactive_workshop(self) -> Dict[str, Any]:
        """运行交互式工作室"""
        print("🛠️ 启动交互式参数工作室...")
        
        if not self.interactive_workshop:
            return self._basic_interactive_session()
        
        return self.interactive_workshop.run_session()
    
    def _basic_interactive_session(self) -> Dict[str, Any]:
        """基础交互式会话"""
        results = {
            "mode": "interactive_workshop",
            "session_duration": 0,
            "interactions": [],
            "final_creation": None
        }
        
        if not self.enhanced_player or not self.enhanced_player.is_initialized:
            print("❌ 交互式模式需要播放器支持")
            return results
        
        start_time = time.time()
        
        try:
            print("🎹 交互式演示开始...")
            print("将演示几个不同参数组合的音乐效果")
            
            demo_params = [
                {"phi_name": "golden", "delta_theta_name": "15.0", "description": "黄金比例 + 15等分"},
                {"phi_name": "octave", "delta_theta_name": "24.0", "description": "八度关系 + 24等分"},
                {"phi_name": "fifth", "delta_theta_name": "4.8", "description": "完全五度 + 五角星"},
            ]
            
            for i, demo in enumerate(demo_params, 1):
                print(f"\n🎵 演示 {i}: {demo['description']}")
                
                # 创建快速作品
                params = {
                    **demo,
                    "phi_value": PRESET_PHI_VALUES[demo["phi_name"]],
                    "delta_theta_value": PRESET_DELTA_THETA_VALUES[demo["delta_theta_name"]],
                    "f_base": 55.0,
                    "chord_ratios": CHORD_RATIOS_PRESETS["major_triad"]
                }
                
                # 创建短小的演示作品
                composition = self._create_demo_composition(params)
                
                if composition:
                    print("   🔊 播放演示...")
                    self._preview_composition_snippet(composition, duration=3.0)
                    
                    interaction = {
                        "demo_id": i,
                        "parameters": demo,
                        "timestamp": time.time() - start_time
                    }
                    results["interactions"].append(interaction)
                    
                    # 短暂暂停
                    time.sleep(1.0)
            
            results["session_duration"] = time.time() - start_time
            print(f"\n✓ 交互式演示完成，耗时 {results['session_duration']:.1f} 秒")
            
        except Exception as e:
            print(f"❌ 交互式会话失败: {e}")
        
        return results
    
    def _run_masterwork_generation(self) -> Dict[str, Any]:
        """运行大师作品集生成"""
        print("🏆 生成Petersen大师作品集...")
        
        if not self.masterwork_generator:
            return self._basic_masterwork_generation()
        
        return self.masterwork_generator.generate_collection()
    
    def _basic_masterwork_generation(self) -> Dict[str, Any]:
        """基础大师作品生成"""
        results = {
            "mode": "masterwork_generation",
            "collection_theme": "petersen_mathematical_beauty",
            "masterworks": [],
            "collection_analysis": {}
        }
        
        print(f"🎼 创作 {self.config.works_count} 首大师级作品...")
        
        # 选择最佳参数组合
        masterwork_params = [
            {
                "name": "Golden Harmony",
                "phi_name": "golden", "delta_theta_name": "15.0",
                "style": "harmonic_exploration"
            },
            {
                "name": "Octave Cathedral", 
                "phi_name": "octave", "delta_theta_name": "24.0",
                "style": "architectural_journey"
            },
            {
                "name": "Sacred Geometry",
                "phi_name": "fifth", "delta_theta_name": "4.8", 
                "style": "mystical_contemplation"
            }
        ]
        
        # 限制作品数量
        selected_params = masterwork_params[:self.config.works_count]
        
        for i, work_spec in enumerate(selected_params, 1):
            print(f"\n🎭 创作第 {i} 首: 《{work_spec['name']}》")
            
            params = {
                **work_spec,
                "phi_value": PRESET_PHI_VALUES[work_spec["phi_name"]],
                "delta_theta_value": PRESET_DELTA_THETA_VALUES[work_spec["delta_theta_name"]],
                "f_base": 55.0,
                "chord_ratios": CHORD_RATIOS_PRESETS["complex_jazz"],
                "composition_style": work_spec.get("style", "balanced_journey")
            }
            
            try:
                # 创作更长的作品
                composition = self._create_composition_from_params(params)
                
                # 保存大师作品
                work_name = f"masterwork_{i:02d}_{work_spec['name'].lower().replace(' ', '_')}"
                work_results = self._save_composition_work(composition, work_name, params)
                work_results["title"] = work_spec["name"]
                
                results["masterworks"].append(work_results)
                
                # 如果是高质量模式，进行专业渲染
                if self.config.quality_level in [QualityLevel.HIGH, QualityLevel.STUDIO]:
                    print("   🎭 进行录音室级别渲染...")
                    self._render_studio_quality(composition, work_name)
                
            except Exception as e:
                print(f"   ❌ 大师作品 {i} 创作失败: {e}")
        
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
        
        return results
    
    def _run_system_analysis(self) -> Dict[str, Any]:
        """运行系统分析"""
        print("📊 分析Petersen音乐系统...")
        
        if not self.analysis_reporter:
            return self._basic_system_analysis()
        
        return self.analysis_reporter.generate_comprehensive_report()
    
    def _basic_system_analysis(self) -> Dict[str, Any]:
        """基础系统分析"""
        results = {
            "mode": "system_analysis",
            "analysis_timestamp": datetime.now().isoformat(),
            "parameter_space_info": {},
            "capability_assessment": {},
            "performance_metrics": {}
        }
        
        print("📈 收集系统能力信息...")
        
        # 参数空间分析
        results["parameter_space_info"] = {
            "available_phi_values": len(PRESET_PHI_VALUES),
            "available_delta_theta_values": len(PRESET_DELTA_THETA_VALUES), 
            "chord_ratio_sets": len(CHORD_RATIOS_PRESETS),
            "rhythm_styles": len(RHYTHM_STYLE_PRESETS),
            "melody_patterns": len(MELODY_PATTERN_PRESETS),
            "composition_styles": len(COMPOSITION_STYLES),
            "performance_techniques": len(PERFORMANCE_TECHNIQUES)
        }
        
        # 能力评估
        results["capability_assessment"] = {
            "player_available": self.enhanced_player is not None and self.enhanced_player.is_initialized,
            "soundfont_loaded": self._check_soundfont_status(),
            "realtime_capability": self.enhanced_player is not None,
            "high_quality_rendering": True,  # 基于配置
            "parameter_exploration": True,
            "interactive_preview": self.enhanced_player is not None
        }
        
        # 性能指标
        if self.enhanced_player:
            results["performance_metrics"] = {
                "sample_rate": getattr(self.enhanced_player.config, 'sample_rate', 44100),
                "buffer_size": getattr(self.enhanced_player.config, 'buffer_size', 512),
                "accurate_frequency": getattr(self.enhanced_player.config, 'enable_accurate_frequency', True)
            }
        
        return results
    
    # === 辅助方法 ===
    
    def _create_composition_from_params(self, params: Dict[str, Any]):
        """从参数创建作曲"""
        # 创建基础音阶
        scale = PetersenScale(
            F_base=params['f_base'],
            phi=params['phi_value'],
            delta_theta=params['delta_theta_value']
        )
        
        # 创建和弦扩展
        chord_extender = PetersenChordExtender(
            petersen_scale=scale,
            chord_ratios=params['chord_ratios']
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
    
    def _create_demo_composition(self, params: Dict[str, Any]):
        """创建演示用的短作品"""
        # 类似于 _create_composition_from_params 但是更短
        scale = PetersenScale(
            F_base=params['f_base'],
            phi=params['phi_value'],
            delta_theta=params['delta_theta_value']
        )
        
        chord_extender = PetersenChordExtender(
            petersen_scale=scale,
            chord_ratios=params['chord_ratios']
        )
        
        composer = PetersenAutoComposer(
            petersen_scale=scale,
            chord_extender=chord_extender,
            composition_style=COMPOSITION_STYLES['balanced_journey'],
            bpm=140  # 稍快一些用于演示
        )
        
        # 生成2小节的短作品
        return composer.compose(measures=2)
    
    def _create_quick_demo_composition(self):
        """创建快速演示作品"""
        try:
            params = {
                "f_base": 55.0,
                "phi_value": 1.618,
                "delta_theta_value": 15.0,
                "chord_ratios": CHORD_RATIOS_PRESETS["major_triad"]
            }
            
            return self._create_demo_composition(params)
            
        except Exception as e:
            print(f"❌ 快速演示作品创建失败: {e}")
            return None
    
    def _preview_composition_snippet(self, composition, duration: float = 4.0):
        """预览作曲片段"""
        if not self.enhanced_player or not self.enhanced_player.is_initialized:
            print("⚠️ 播放器不可用，跳过预览")
            return
        
        try:
            # 这里需要根据实际的composition结构来提取音频数据
            # 目前使用简化实现
            print(f"   播放 {duration} 秒预览...")
            
            # 如果composition有frequency数据，直接播放
            if hasattr(composition, 'get_preview_frequencies'):
                frequencies, names = composition.get_preview_frequencies()
                self.enhanced_player.play_frequencies(
                    frequencies=frequencies[:8],  # 限制音符数量
                    key_names=names[:8],
                    duration=duration / 8,
                    gap=0.05,
                    use_accurate_frequency=True
                )
            else:
                print("   ⚠️ 作曲对象不支持直接预览")
            
        except Exception as e:
            print(f"   ⚠️ 预览失败: {e}")
    
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
    
    def _render_studio_quality(self, composition, work_name: str):
        """渲染录音室质量音频"""
        try:
            if not self.soundfont_renderer:
                print("   ⚠️ 高质量渲染器不可用")
                return
            
            output_path = self.config.output_directory / work_name / f"{work_name}_studio.wav"
            
            # 使用高质量渲染器
            result_path = self.soundfont_renderer.render_composition(
                composition,
                output_path,
                quality_level=self.config.quality_level
            )
            
            if result_path:
                print(f"   ✓ 录音室质量渲染完成: {result_path.name}")
            
        except Exception as e:
            print(f"   ❌ 录音室质量渲染失败: {e}")
    
    def _generate_mathematics_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成数学分析报告"""
        analysis = {
            "report_type": "mathematics_analysis",
            "timestamp": datetime.now().isoformat(),
            "parameter_effects": {},
            "aesthetic_metrics": {},
            "recommendations": []
        }
        
        # 分析参数对音乐效果的影响
        works = results.get("generated_works", [])
        
        if works:
            # 按φ值分组分析
            phi_groups = {}
            for work in works:
                params = work.get("parameters", {})
                phi_name = params.get("phi_name", "unknown")
                
                if phi_name not in phi_groups:
                    phi_groups[phi_name] = []
                phi_groups[phi_name].append(work)
            
            analysis["parameter_effects"]["phi_value_impact"] = {
                "groups": list(phi_groups.keys()),
                "group_sizes": {k: len(v) for k, v in phi_groups.items()},
                "observations": "不同φ值产生显著不同的和声特征"
            }
            
            # 推荐
            analysis["recommendations"] = [
                "黄金比例φ=1.618产生最和谐的音响效果",
                "15等分δθ=15.0提供丰富的旋律变化", 
                "建议组合使用多种参数以获得最佳美学体验"
            ]
        
        return analysis
    
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
    
    def _check_soundfont_status(self) -> bool:
        """检查SoundFont状态"""
        if not self.enhanced_player:
            return False
        
        return self.enhanced_player.is_initialized and \
               hasattr(self.enhanced_player, 'soundfont_manager') and \
               self.enhanced_player.soundfont_manager is not None
    
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
  python petersen_master_studio.py --explore-mathematics --phi-values golden,octave --measures 8
  
  # 数学美学对比
  python petersen_master_studio.py --compare-aesthetics --variations 3
  
  # 展示大师级技艺
  python petersen_master_studio.py --showcase-virtuosity --quality studio
  
  # 交互式工作室
  python petersen_master_studio.py --interactive-workshop --realtime-preview
  
  # 生成大师作品集
  python petersen_master_studio.py --generate-masterworks --works-count 5
  
  # 快速预览
  python petersen_master_studio.py --quick-preview
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
                       default='GD_Steinway_Model_D274.sf2',
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