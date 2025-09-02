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
    preferred_soundfont: str = "GD_Steinway_Model_D274.sf2"
    alternative_soundfont: str = "GD_Steinway_Model_D274II.sf2"
    
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
            self.soundfont_renderer = HighQualitySoundFontRenderer(self)
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
        
        # 验证δθ值预设
        available_delta_theta = list(DELTA_THETA_PRESETS.keys())
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
        
        try:
            # 配置探索参数
            config = self.parameter_explorer.configure_exploration(
                mode=ExplorationMode.QUICK_SURVEY if len(self.config.phi_values) <= 3 else ExplorationMode.SYSTEMATIC_GRID,
                max_combinations=min(20, len(self.config.phi_values) * len(self.config.delta_theta_values)),
                phi_filter=self.config.phi_values,
                delta_theta_filter=self.config.delta_theta_values,
                measures_per_work=self.config.measures_count
            )
            
            # 运行探索
            exploration_results = self.parameter_explorer.run_exploration(config)
            
            # 整合结果
            results["parameter_combinations"] = [combo.__dict__ for combo in exploration_results.explored_combinations]
            results["generated_works"] = exploration_results.successful_works
            results["analysis_reports"] = [exploration_results.parameter_effects]
            
        except Exception as e:
            print(f"❌ 数学探索失败: {e}")
            results["error"] = str(e)
        
        return results
    
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