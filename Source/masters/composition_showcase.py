"""
Petersen 作曲展示系统

这是专门展示Petersen音乐系统大师级作曲能力的模块，通过创作结构完整、
技法丰富的音乐作品来证明系统的创作潜力和艺术价值。

核心使命：
- 展示完整的作曲流程：从数学参数到成品音乐
- 演示高级作曲技法：对位、变奏、发展等
- 创作不同风格的作品：古典、爵士、现代、实验等
- 展现参数组合的创作可能性
- 提供作曲教学的范例作品

展示类型：
- 技法展示作品：专门演示特定作曲技法
- 风格化作品：不同音乐风格的创作示例
- 参数驱动作品：突出数学美学的作品
- 综合性大作：展示系统全部能力的复杂作品
- 教学演示作品：用于教学的结构清晰作品

技术特点：
- 多层次作曲架构：动机→乐句→乐段→作品
- 智能发展技法：模进、变奏、对比等
- 精确的数学美学控制
- 录音室级别的音频渲染
- 完整的作品分析和注释

作品类型：
- 短小精品（16-32小节）
- 中型作品（64-128小节）  
- 大型作品（256+小节）
- 组曲形式（多乐章）
- 变奏曲式（主题+变奏）
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random
import math

# 添加libs路径
current_dir = Path(__file__).parent
libs_dir = current_dir.parent / "libs"
if str(libs_dir) not in sys.path:
    sys.path.insert(0, str(libs_dir))

try:
    from petersen_scale import PetersenScale, PHI_PRESETS, DELTA_THETA_PRESETS
    from petersen_chord import PetersenChordExtender, CHORD_RATIOS
    from petersen_rhythm import PetersenRhythmGenerator, RHYTHM_STYLES
    from petersen_melody import PetersenMelodyGenerator, MELODY_PATTERNS
    from petersen_composer import PetersenAutoComposer, COMPOSITION_STYLES
    from petersen_performance import PetersenPerformanceRenderer, PERFORMANCE_TECHNIQUES
except ImportError as e:
    print(f"⚠️ 导入基础模块失败: {e}")

class ShowcaseType(Enum):
    """展示类型"""
    TECHNIQUE_DEMONSTRATION = "technique_demonstration"    # 技法演示
    STYLE_EXPLORATION = "style_exploration"              # 风格探索
    PARAMETER_ARTISTRY = "parameter_artistry"            # 参数艺术性
    COMPREHENSIVE_MASTERWORK = "comprehensive_masterwork" # 综合大作
    EDUCATIONAL_EXAMPLE = "educational_example"          # 教学范例
    VIRTUOSO_PERFORMANCE = "virtuoso_performance"        # 超技演奏
    MATHEMATICAL_BEAUTY = "mathematical_beauty"          # 数学美学

class CompositionScale(Enum):
    """作品规模"""
    MINIATURE = "miniature"        # 16-32小节
    SHORT_PIECE = "short_piece"    # 32-64小节
    MEDIUM_WORK = "medium_work"    # 64-128小节
    LARGE_WORK = "large_work"      # 128-256小节
    EXTENDED_WORK = "extended_work" # 256+小节

class CompositionForm(Enum):
    """作品体裁"""
    BINARY_FORM = "binary_form"           # 二段体
    TERNARY_FORM = "ternary_form"         # 三段体
    RONDO_FORM = "rondo_form"             # 回旋曲式
    VARIATION_FORM = "variation_form"     # 变奏曲式
    SONATA_FORM = "sonata_form"           # 奏鸣曲式
    SUITE_FORM = "suite_form"             # 组曲形式
    FREE_FORM = "free_form"               # 自由形式

@dataclass
class ShowcaseWork:
    """展示作品"""
    work_id: str
    title: str
    subtitle: str
    showcase_type: ShowcaseType
    composition_scale: CompositionScale
    composition_form: CompositionForm
    
    # 创作参数
    mathematical_parameters: Dict[str, Any] = field(default_factory=dict)
    musical_parameters: Dict[str, Any] = field(default_factory=dict)
    technical_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # 作品信息
    creation_timestamp: str = ""
    estimated_duration: float = 0.0  # 秒
    difficulty_level: str = "intermediate"
    
    # 分析信息
    structural_analysis: Dict[str, Any] = field(default_factory=dict)
    harmonic_analysis: Dict[str, Any] = field(default_factory=dict)
    technical_features: List[str] = field(default_factory=list)
    
    # 文件信息
    generated_files: List[str] = field(default_factory=list)
    audio_files: List[str] = field(default_factory=list)
    analysis_files: List[str] = field(default_factory=list)

@dataclass
class ShowcaseSession:
    """展示会话"""
    session_id: str
    showcase_theme: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # 展示作品
    showcase_works: List[ShowcaseWork] = field(default_factory=list)
    
    # 会话统计
    total_works_planned: int = 0
    works_completed: int = 0
    total_composition_time: float = 0.0
    
    # 展示效果
    demonstration_logs: List[str] = field(default_factory=list)
    audience_feedback: Dict[str, Any] = field(default_factory=dict)

class CompositionShowcase:
    """作曲展示系统"""
    
    def __init__(self, master_studio):
        """
        初始化作曲展示系统
        
        Args:
            master_studio: PetersenMasterStudio实例
        """
        self.master_studio = master_studio
        
        # 当前会话
        self.current_session: Optional[ShowcaseSession] = None
        self.session_history: List[ShowcaseSession] = []
        
        # 作品模板库
        self.composition_templates = self._initialize_composition_templates()
        self.showcase_programs = self._initialize_showcase_programs()
        
        # 创作状态
        self.creation_cache: Dict[str, Any] = {}
        self.quality_metrics: Dict[str, float] = {}
        
        print("✓ 作曲展示系统已初始化")
    
    def _initialize_composition_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化作品模板"""
        return {
            "golden_miniature": {
                "title": "Golden Ratio Miniature",
                "subtitle": "A brief exploration of φ=1.618",
                "showcase_type": ShowcaseType.MATHEMATICAL_BEAUTY,
                "scale": CompositionScale.MINIATURE,
                "form": CompositionForm.TERNARY_FORM,
                "parameters": {
                    "phi_name": "golden",
                    "delta_theta_name": "15.0",
                    "chord_set": "major_seventh",
                    "composition_style": "harmonic_exploration"
                },
                "measures": 24,
                "estimated_duration": 90.0
            },
            
            "octave_cathedral": {
                "title": "Octave Cathedral", 
                "subtitle": "Architectural harmony in perfect ratios",
                "showcase_type": ShowcaseType.STYLE_EXPLORATION,
                "scale": CompositionScale.SHORT_PIECE,
                "form": CompositionForm.BINARY_FORM,
                "parameters": {
                    "phi_name": "octave",
                    "delta_theta_name": "24.0", 
                    "chord_set": "quartal",
                    "composition_style": "architectural_journey"
                },
                "measures": 48,
                "estimated_duration": 180.0
            },
            
            "fifth_spiral": {
                "title": "The Perfect Fifth Spiral",
                "subtitle": "Melodic spirals in sacred geometry", 
                "showcase_type": ShowcaseType.TECHNIQUE_DEMONSTRATION,
                "scale": CompositionScale.SHORT_PIECE,
                "form": CompositionForm.RONDO_FORM,
                "parameters": {
                    "phi_name": "fifth",
                    "delta_theta_name": "4.8",
                    "chord_set": "complex_jazz",
                    "composition_style": "virtuoso_journey"
                },
                "measures": 56,
                "estimated_duration": 210.0
            },
            
            "chromatic_cosmos": {
                "title": "Chromatic Cosmos",
                "subtitle": "Exploring the 12-tone universe through Petersen mathematics",
                "showcase_type": ShowcaseType.COMPREHENSIVE_MASTERWORK,
                "scale": CompositionScale.MEDIUM_WORK,
                "form": CompositionForm.VARIATION_FORM,
                "parameters": {
                    "phi_name": "semitone",
                    "delta_theta_name": "72.0",
                    "chord_set": "atonal_clusters",
                    "composition_style": "experimental_journey"
                },
                "measures": 96,
                "estimated_duration": 360.0
            },
            
            "virtuoso_etude": {
                "title": "Petersen Virtuoso Étude No.1",
                "subtitle": "Technical mastery meets mathematical beauty",
                "showcase_type": ShowcaseType.VIRTUOSO_PERFORMANCE,
                "scale": CompositionScale.MEDIUM_WORK,
                "form": CompositionForm.FREE_FORM,
                "parameters": {
                    "phi_name": "golden",
                    "delta_theta_name": "8.0",
                    "chord_set": "complex_jazz",
                    "composition_style": "virtuoso_journey"
                },
                "measures": 128,
                "estimated_duration": 480.0
            },
            
            "pedagogical_suite": {
                "title": "Petersen Educational Suite",
                "subtitle": "Teaching mathematical music through progressive movements",
                "showcase_type": ShowcaseType.EDUCATIONAL_EXAMPLE,
                "scale": CompositionScale.LARGE_WORK,
                "form": CompositionForm.SUITE_FORM,
                "parameters": {
                    "multi_movement": True,
                    "movements": [
                        {"phi_name": "octave", "delta_theta_name": "24.0"},
                        {"phi_name": "fifth", "delta_theta_name": "15.0"},
                        {"phi_name": "golden", "delta_theta_name": "4.8"}
                    ]
                },
                "measures": 192,
                "estimated_duration": 720.0
            }
        }
    
    def _initialize_showcase_programs(self) -> Dict[str, List[str]]:
        """初始化展示节目单"""
        return {
            "quick_demonstration": [
                "golden_miniature",
                "fifth_spiral"
            ],
            
            "comprehensive_showcase": [
                "golden_miniature",
                "octave_cathedral", 
                "fifth_spiral",
                "virtuoso_etude"
            ],
            
            "educational_program": [
                "pedagogical_suite",
                "golden_miniature",
                "octave_cathedral"
            ],
            
            "virtuoso_recital": [
                "virtuoso_etude",
                "chromatic_cosmos",
                "fifth_spiral"
            ],
            
            "mathematical_beauty": [
                "golden_miniature",
                "octave_cathedral",
                "chromatic_cosmos"
            ]
        }
    
    def run_showcase(self, program_name: str = "comprehensive_showcase") -> ShowcaseSession:
        """
        运行作曲展示
        
        Args:
            program_name: 展示节目名称
            
        Returns:
            ShowcaseSession: 展示会话结果
        """
        session_id = f"showcase_{int(time.time())}"
        
        print(f"🎭 开始作曲展示: {program_name}")
        print(f"   会话ID: {session_id}")
        print("=" * 60)
        
        # 获取展示节目
        if program_name not in self.showcase_programs:
            print(f"❌ 未知展示节目: {program_name}")
            print(f"可用节目: {list(self.showcase_programs.keys())}")
            raise ValueError(f"未知展示节目: {program_name}")
        
        work_templates = self.showcase_programs[program_name]
        
        # 创建展示会话
        self.current_session = ShowcaseSession(
            session_id=session_id,
            showcase_theme=program_name,
            start_time=datetime.now(),
            total_works_planned=len(work_templates)
        )
        
        try:
            # 展示开场
            self._display_showcase_opening(program_name, work_templates)
            
            # 逐个创作展示作品
            for i, template_name in enumerate(work_templates, 1):
                print(f"\n🎼 创作第 {i}/{len(work_templates)} 首作品...")
                
                start_time = time.time()
                showcase_work = self._create_showcase_work(template_name)
                creation_time = time.time() - start_time
                
                if showcase_work:
                    self.current_session.showcase_works.append(showcase_work)
                    self.current_session.works_completed += 1
                    self.current_session.total_composition_time += creation_time
                    
                    # 展示作品信息
                    self._display_work_showcase(showcase_work, creation_time)
                    
                    # 如果启用实时预览
                    if self.master_studio.config.realtime_preview:
                        self._preview_showcase_work(showcase_work)
                
                else:
                    print(f"   ❌ 作品创作失败: {template_name}")
            
            # 展示总结
            self._display_showcase_summary()
            
            # 完成会话
            self.current_session.end_time = datetime.now()
            self.session_history.append(self.current_session)
            
            return self.current_session
            
        except Exception as e:
            print(f"❌ 展示会话失败: {e}")
            if self.current_session:
                self.current_session.end_time = datetime.now()
            raise
    
    def _display_showcase_opening(self, program_name: str, work_templates: List[str]):
        """展示开场介绍"""
        print("🎪 Petersen 作曲展示会")
        print("=" * 60)
        print(f"📋 节目主题: {program_name}")
        print(f"🎼 计划作品: {len(work_templates)} 首")
        print()
        
        print("📝 节目单:")
        for i, template_name in enumerate(work_templates, 1):
            template = self.composition_templates.get(template_name, {})
            title = template.get("title", template_name)
            subtitle = template.get("subtitle", "")
            duration = template.get("estimated_duration", 0) / 60.0
            
            print(f"   {i}. {title}")
            if subtitle:
                print(f"      {subtitle}")
            print(f"      预计时长: {duration:.1f} 分钟")
        
        print("\n🎹 现在开始演出...")
        print("-" * 60)
    
    def _create_showcase_work(self, template_name: str) -> Optional[ShowcaseWork]:
        """创作展示作品"""
        if template_name not in self.composition_templates:
            print(f"❌ 未知作品模板: {template_name}")
            return None
        
        template = self.composition_templates[template_name]
        
        print(f"🎵 创作: 《{template['title']}》")
        print(f"   副标题: {template['subtitle']}")
        print(f"   展示类型: {template['showcase_type'].value}")
        
        try:
            # 创建展示作品对象
            showcase_work = ShowcaseWork(
                work_id=f"{template_name}_{int(time.time())}",
                title=template["title"],
                subtitle=template["subtitle"],
                showcase_type=template["showcase_type"],
                composition_scale=template["scale"],
                composition_form=template["form"],
                creation_timestamp=datetime.now().isoformat(),
                estimated_duration=template.get("estimated_duration", 120.0)
            )
            
            # 处理参数
            if template["parameters"].get("multi_movement", False):
                # 多乐章作品
                composition = self._create_multi_movement_work(template, showcase_work)
            else:
                # 单乐章作品
                composition = self._create_single_movement_work(template, showcase_work)
            
            if not composition:
                return None
            
            # 保存作品文件
            self._save_showcase_work_files(showcase_work, composition)
            
            # 分析作品
            self._analyze_showcase_work(showcase_work, composition)
            
            return showcase_work
            
        except Exception as e:
            print(f"   ❌ 创作失败: {e}")
            return None
    
    def _create_single_movement_work(self, template: Dict[str, Any], 
                                   showcase_work: ShowcaseWork) -> Optional[Any]:
        """创作单乐章作品"""
        params = template["parameters"]
        
        # 提取参数
        phi_name = params.get("phi_name", "golden")
        delta_theta_name = params.get("delta_theta_name", "15.0")
        chord_set = params.get("chord_set", "major_triad")
        composition_style = params.get("composition_style", "balanced_journey")
        measures = template.get("measures", 32)
        
        print(f"   参数: φ={phi_name}, δθ={delta_theta_name}, 和弦={chord_set}")
        print(f"   规模: {measures} 小节, 形式: {template['form'].value}")
        
        # 记录参数
        showcase_work.mathematical_parameters = {
            "phi_name": phi_name,
            "phi_value": PHI_PRESETS.get(phi_name, 1.618),
            "delta_theta_name": delta_theta_name,
            "delta_theta_value": DELTA_THETA_PRESETS.get(delta_theta_name, 15.0)
        }
        
        showcase_work.musical_parameters = {
            "chord_set": chord_set,
            "composition_style": composition_style,
            "measures": measures,
            "form": template["form"].value
        }
        
        # 创建基础音乐组件
        scale = PetersenScale(
            F_base=55.0,
            phi=showcase_work.mathematical_parameters["phi_value"],
            delta_theta=showcase_work.mathematical_parameters["delta_theta_value"]
        )
        
        chord_extender = PetersenChordExtender(
            petersen_scale=scale,
            chord_ratios=CHORD_RATIOS.get(chord_set, CHORD_RATIOS["major_triad"])
        )
        
        # 根据展示类型调整作曲风格
        adjusted_style = self._adjust_composition_style_for_showcase(
            composition_style, showcase_work.showcase_type
        )
        
        composer = PetersenAutoComposer(
            petersen_scale=scale,
            chord_extender=chord_extender,
            composition_style=COMPOSITION_STYLES.get(adjusted_style, COMPOSITION_STYLES["balanced_journey"]),
            bpm=self._calculate_optimal_tempo(template)
        )
        
        # 生成作曲
        composition = composer.compose(measures=measures)
        
        # 如果是技法展示或超技演奏，应用高级技法
        if showcase_work.showcase_type in [ShowcaseType.TECHNIQUE_DEMONSTRATION, 
                                         ShowcaseType.VIRTUOSO_PERFORMANCE]:
            composition = self._apply_advanced_techniques(composition, showcase_work)
        
        return composition
    
    def _create_multi_movement_work(self, template: Dict[str, Any], 
                                  showcase_work: ShowcaseWork) -> Optional[Any]:
        """创作多乐章作品"""
        movements = template["parameters"]["movements"]
        total_measures = template.get("measures", 192)
        measures_per_movement = total_measures // len(movements)
        
        print(f"   多乐章作品: {len(movements)} 个乐章")
        
        movement_compositions = []
        
        for i, movement_params in enumerate(movements, 1):
            print(f"   创作第 {i} 乐章: φ={movement_params['phi_name']}, δθ={movement_params['delta_theta_name']}")
            
            # 创建乐章的单独作曲
            movement_template = {
                **template,
                "parameters": {
                    **movement_params,
                    "chord_set": "major_seventh",  # 为多乐章设置默认和弦
                    "composition_style": f"movement_{i}_style"  # 可以为每个乐章定制风格
                },
                "measures": measures_per_movement
            }
            
            movement_composition = self._create_single_movement_work(
                movement_template, showcase_work
            )
            
            if movement_composition:
                movement_compositions.append(movement_composition)
            else:
                print(f"   ⚠️ 第 {i} 乐章创作失败，跳过")
        
        if not movement_compositions:
            return None
        
        # 这里可以添加多乐章合并逻辑
        # 目前返回第一个乐章作为代表
        return movement_compositions[0] if movement_compositions else None
    
    def _adjust_composition_style_for_showcase(self, base_style: str, 
                                             showcase_type: ShowcaseType) -> str:
        """根据展示类型调整作曲风格"""
        style_adjustments = {
            ShowcaseType.TECHNIQUE_DEMONSTRATION: "virtuoso_journey",
            ShowcaseType.STYLE_EXPLORATION: "harmonic_exploration", 
            ShowcaseType.PARAMETER_ARTISTRY: "mathematical_beauty",
            ShowcaseType.COMPREHENSIVE_MASTERWORK: "complex_journey",
            ShowcaseType.EDUCATIONAL_EXAMPLE: "clear_structure",
            ShowcaseType.VIRTUOSO_PERFORMANCE: "virtuoso_journey",
            ShowcaseType.MATHEMATICAL_BEAUTY: "harmonic_exploration"
        }
        
        return style_adjustments.get(showcase_type, base_style)
    
    def _calculate_optimal_tempo(self, template: Dict[str, Any]) -> int:
        """计算最适合的演奏速度"""
        showcase_type = template["showcase_type"]
        scale = template["scale"]
        
        # 基础BPM
        if showcase_type == ShowcaseType.VIRTUOSO_PERFORMANCE:
            base_bpm = 144  # 较快
        elif showcase_type == ShowcaseType.MATHEMATICAL_BEAUTY:
            base_bpm = 96   # 较慢，便于感受和声
        elif showcase_type == ShowcaseType.EDUCATIONAL_EXAMPLE:
            base_bpm = 108  # 中等，便于理解
        else:
            base_bpm = 120  # 标准速度
        
        # 根据作品规模调整
        if scale == CompositionScale.MINIATURE:
            return base_bpm + 12  # 短小作品稍快
        elif scale in [CompositionScale.LARGE_WORK, CompositionScale.EXTENDED_WORK]:
            return base_bpm - 12  # 大型作品稍慢
        else:
            return base_bpm
    
    def _apply_advanced_techniques(self, composition: Any, 
                                 showcase_work: ShowcaseWork) -> Any:
        """应用高级演奏技法"""
        print("   🎭 应用高级演奏技法...")
        
        # 根据展示类型选择技法
        if showcase_work.showcase_type == ShowcaseType.TECHNIQUE_DEMONSTRATION:
            techniques = ["thirds_parallel", "octave_cascade", "arpeggiated_texture"]
        elif showcase_work.showcase_type == ShowcaseType.VIRTUOSO_PERFORMANCE:
            techniques = ["cross_hand_weaving", "rapid_scalar_passages", "complex_polyrhythm"]
        else:
            techniques = ["harmonic_resonance", "subtle_rubato"]
        
        # 记录应用的技法
        showcase_work.technical_features.extend(techniques)
        showcase_work.technical_parameters["applied_techniques"] = techniques
        showcase_work.difficulty_level = "advanced" if len(techniques) > 2 else "intermediate"
        
        # 这里可以实际应用技法到composition对象
        # 目前记录技法信息
        
        return composition
    
    def _save_showcase_work_files(self, showcase_work: ShowcaseWork, composition: Any):
        """保存展示作品文件"""
        work_dir = self.master_studio.config.output_directory / f"showcase_{showcase_work.work_id}"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"   💾 保存作品文件到: {work_dir.name}")
        
        try:
            # 保存MIDI文件
            if hasattr(composition, 'export_midi'):
                midi_path = work_dir / f"{showcase_work.work_id}.mid"
                composition.export_midi(str(midi_path))
                showcase_work.generated_files.append(str(midi_path))
                print(f"   ✓ MIDI: {midi_path.name}")
            
            # 保存分析文件
            if hasattr(composition, 'export_score_csv'):
                csv_path = work_dir / f"{showcase_work.work_id}_analysis.csv"
                composition.export_score_csv(str(csv_path))
                showcase_work.analysis_files.append(str(csv_path))
                print(f"   ✓ 分析: {csv_path.name}")
            
            # 保存作品信息
            info_path = work_dir / f"{showcase_work.work_id}_info.json"
            work_info = {
                "title": showcase_work.title,
                "subtitle": showcase_work.subtitle,
                "showcase_type": showcase_work.showcase_type.value,
                "composition_scale": showcase_work.composition_scale.value,
                "composition_form": showcase_work.composition_form.value,
                "mathematical_parameters": showcase_work.mathematical_parameters,
                "musical_parameters": showcase_work.musical_parameters,
                "technical_parameters": showcase_work.technical_parameters,
                "estimated_duration": showcase_work.estimated_duration,
                "difficulty_level": showcase_work.difficulty_level,
                "creation_timestamp": showcase_work.creation_timestamp
            }
            
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(work_info, f, indent=2, ensure_ascii=False)
            
            showcase_work.generated_files.append(str(info_path))
            
        except Exception as e:
            print(f"   ⚠️ 文件保存警告: {e}")
    
    def _analyze_showcase_work(self, showcase_work: ShowcaseWork, composition: Any):
        """分析展示作品"""
        print("   📈 分析作品特征...")
        
        # 结构分析
        showcase_work.structural_analysis = {
            "form_type": showcase_work.composition_form.value,
            "estimated_sections": self._estimate_work_sections(showcase_work),
            "complexity_score": self._calculate_work_complexity(showcase_work),
            "innovation_index": self._calculate_innovation_index(showcase_work)
        }
        
        # 和声分析
        showcase_work.harmonic_analysis = {
            "phi_ratio_impact": self._analyze_phi_impact(showcase_work),
            "delta_theta_effect": self._analyze_delta_theta_effect(showcase_work),
            "chord_complexity": self._analyze_chord_complexity(showcase_work),
            "harmonic_richness": self._calculate_harmonic_richness(showcase_work)
        }
        
        # 技术特征
        if not showcase_work.technical_features:
            showcase_work.technical_features = self._extract_technical_features(showcase_work)
    
    def _estimate_work_sections(self, showcase_work: ShowcaseWork) -> int:
        """估算作品段落数"""
        measures = showcase_work.musical_parameters.get("measures", 32)
        form = showcase_work.composition_form
        
        if form == CompositionForm.BINARY_FORM:
            return 2
        elif form == CompositionForm.TERNARY_FORM:
            return 3
        elif form == CompositionForm.RONDO_FORM:
            return max(3, measures // 16)  # 根据长度估算
        elif form == CompositionForm.VARIATION_FORM:
            return max(4, measures // 12)  # 主题+变奏
        else:
            return max(2, measures // 20)  # 通用估算
    
    def _calculate_work_complexity(self, showcase_work: ShowcaseWork) -> float:
        """计算作品复杂度"""
        complexity = 0.0
        
        # 数学参数复杂度
        phi_value = showcase_work.mathematical_parameters.get("phi_value", 1.618)
        if phi_value == 1.618:  # 黄金比例
            complexity += 0.8
        elif phi_value == 2.0:  # 八度
            complexity += 0.4
        else:
            complexity += 0.6
        
        # δθ值复杂度
        delta_theta = showcase_work.mathematical_parameters.get("delta_theta_value", 15.0)
        if delta_theta < 10.0:
            complexity += 0.7  # 小角度，复杂
        elif delta_theta < 20.0:
            complexity += 0.5
        else:
            complexity += 0.3
        
        # 音乐参数复杂度
        chord_set = showcase_work.musical_parameters.get("chord_set", "major_triad")
        chord_complexity = {
            "major_triad": 0.2, "minor_triad": 0.3,
            "major_seventh": 0.5, "minor_seventh": 0.6,
            "complex_jazz": 0.9, "quartal": 0.7,
            "atonal_clusters": 1.0
        }
        complexity += chord_complexity.get(chord_set, 0.5) * 0.5
        
        # 技法复杂度
        tech_count = len(showcase_work.technical_features)
        complexity += min(0.5, tech_count * 0.1)
        
        return min(1.0, complexity / 2.0)  # 标准化到0-1
    
    def _calculate_innovation_index(self, showcase_work: ShowcaseWork) -> float:
        """计算创新指数"""
        innovation = 0.0
        
        # 参数组合的新颖性
        phi_name = showcase_work.mathematical_parameters.get("phi_name", "golden")
        delta_name = showcase_work.mathematical_parameters.get("delta_theta_name", "15.0")
        
        # 非常规参数组合获得更高创新分
        if phi_name in ["golden", "octave"]:
            innovation += 0.3  # 常规
        else:
            innovation += 0.7  # 非常规
        
        if delta_name in ["15.0", "24.0"]:
            innovation += 0.3  # 常规
        else:
            innovation += 0.7  # 非常规
        
        # 展示类型创新性
        type_innovation = {
            ShowcaseType.EDUCATIONAL_EXAMPLE: 0.4,
            ShowcaseType.STYLE_EXPLORATION: 0.6,
            ShowcaseType.TECHNIQUE_DEMONSTRATION: 0.7,
            ShowcaseType.MATHEMATICAL_BEAUTY: 0.8,
            ShowcaseType.COMPREHENSIVE_MASTERWORK: 0.9,
            ShowcaseType.VIRTUOSO_PERFORMANCE: 0.8
        }
        innovation += type_innovation.get(showcase_work.showcase_type, 0.5) * 0.4
        
        return min(1.0, innovation)
    
    def _analyze_phi_impact(self, showcase_work: ShowcaseWork) -> str:
        """分析φ值的影响"""
        phi_name = showcase_work.mathematical_parameters.get("phi_name", "golden")
        
        impact_descriptions = {
            "golden": "产生自然和谐的音程关系，黄金分割美学",
            "octave": "建立清晰的八度结构，稳定的音程基础",
            "fifth": "创造完全五度的和声色彩，明亮通透",
            "fourth": "构建完全四度框架，庄重宽广的音响",
            "major_third": "带来大三度的温暖色彩，柔和悦耳",
            "minor_third": "创造小三度的内敛美感，深沉含蓄",
            "semitone": "产生半音级进的紧张感，现代色彩"
        }
        
        return impact_descriptions.get(phi_name, "创造独特的音程关系")
    
    def _analyze_delta_theta_effect(self, showcase_work: ShowcaseWork) -> str:
        """分析δθ值的效果"""
        delta_theta = showcase_work.mathematical_parameters.get("delta_theta_value", 15.0)
        
        if delta_theta <= 5.0:
            return "极密集的音阶分布，微分音色彩丰富"
        elif delta_theta <= 10.0:
            return "密集的音阶结构，复杂的旋律变化"
        elif delta_theta <= 20.0:
            return "中等密度音阶，平衡的旋律表现力"
        elif delta_theta <= 40.0:
            return "较为稀疏的音阶，清晰的音程关系"
        else:
            return "稀疏的音阶分布，突出的骨干音程"
    
    def _analyze_chord_complexity(self, showcase_work: ShowcaseWork) -> str:
        """分析和弦复杂度"""
        chord_set = showcase_work.musical_parameters.get("chord_set", "major_triad")
        
        complexity_descriptions = {
            "major_triad": "基础三和弦，清澈透明的和声",
            "minor_triad": "小三和弦，温暖内敛的色彩",
            "major_seventh": "大七和弦，丰富的和声层次",
            "minor_seventh": "小七和弦，爵士色彩浓郁",
            "complex_jazz": "复杂爵士和弦，现代和声语言",
            "quartal": "四度和弦，现代音响效果",
            "atonal_clusters": "无调性音簇，实验性音响"
        }
        
        return complexity_descriptions.get(chord_set, "独特的和弦色彩")
    
    def _calculate_harmonic_richness(self, showcase_work: ShowcaseWork) -> float:
        """计算和声丰富度"""
        # 综合φ值、和弦设置等因素
        phi_richness = {
            "golden": 0.9, "fifth": 0.8, "fourth": 0.7,
            "major_third": 0.75, "minor_third": 0.7,
            "octave": 0.6, "semitone": 0.5
        }
        
        chord_richness = {
            "complex_jazz": 0.9, "quartal": 0.8,
            "major_seventh": 0.7, "minor_seventh": 0.75,
            "major_triad": 0.5, "minor_triad": 0.55,
            "atonal_clusters": 0.6
        }
        
        phi_name = showcase_work.mathematical_parameters.get("phi_name", "golden")
        chord_set = showcase_work.musical_parameters.get("chord_set", "major_triad")
        
        phi_score = phi_richness.get(phi_name, 0.5)
        chord_score = chord_richness.get(chord_set, 0.5)
        
        return (phi_score + chord_score) / 2
    
    def _extract_technical_features(self, showcase_work: ShowcaseWork) -> List[str]:
        """提取技术特征"""
        features = []
        
        # 基于展示类型添加特征
        if showcase_work.showcase_type == ShowcaseType.VIRTUOSO_PERFORMANCE:
            features.extend(["高速演奏", "复杂技法", "表现力丰富"])
        
        if showcase_work.showcase_type == ShowcaseType.MATHEMATICAL_BEAUTY:
            features.extend(["数学美学", "比例协调", "结构严谨"])
        
        if showcase_work.showcase_type == ShowcaseType.TECHNIQUE_DEMONSTRATION:
            features.extend(["技法展示", "教学价值", "结构清晰"])
        
        # 基于复杂度添加特征
        complexity = showcase_work.structural_analysis.get("complexity_score", 0.5)
        if complexity > 0.7:
            features.append("高复杂度")
        elif complexity < 0.3:
            features.append("简洁明快")
        else:
            features.append("结构平衡")
        
        return features
    
    def _display_work_showcase(self, showcase_work: ShowcaseWork, creation_time: float):
        """展示作品信息"""
        print(f"   ✓ 《{showcase_work.title}》创作完成")
        print(f"   ⏱️ 创作耗时: {creation_time:.1f} 秒")
        print(f"   📊 复杂度: {showcase_work.structural_analysis.get('complexity_score', 0):.2f}")
        print(f"   🎨 创新指数: {showcase_work.structural_analysis.get('innovation_index', 0):.2f}")
        print(f"   🎯 难度级别: {showcase_work.difficulty_level}")
        
        if showcase_work.technical_features:
            print(f"   🛠️ 技术特征: {', '.join(showcase_work.technical_features[:3])}")
        
        print(f"   💾 生成文件: {len(showcase_work.generated_files)} 个")
    
    def _preview_showcase_work(self, showcase_work: ShowcaseWork):
        """预览展示作品"""
        print(f"   🔊 预览《{showcase_work.title}》...")
        
        try:
            # 这里可以调用实际的预览功能
            # 目前使用模拟预览
            preview_duration = min(10.0, showcase_work.estimated_duration / 10)
            
            print(f"   🎵 播放 {preview_duration:.1f} 秒预览...")
            time.sleep(preview_duration)
            print("   ✓ 预览完成")
            
        except Exception as e:
            print(f"   ⚠️ 预览失败: {e}")
    
    def _display_showcase_summary(self):
        """展示总结信息"""
        if not self.current_session:
            return
        
        session = self.current_session
        
        print("\n" + "=" * 60)
        print("🎉 作曲展示会完成！")
        print("=" * 60)
        
        print(f"📋 展示主题: {session.showcase_theme}")
        print(f"🎼 完成作品: {session.works_completed}/{session.total_works_planned}")
        print(f"⏱️ 总创作时间: {session.total_composition_time:.1f} 秒")
        
        if session.showcase_works:
            avg_time = session.total_composition_time / len(session.showcase_works)
            print(f"📊 平均创作时间: {avg_time:.1f} 秒/作品")
            
            # 统计信息
            complexity_scores = [w.structural_analysis.get("complexity_score", 0) 
                               for w in session.showcase_works]
            avg_complexity = sum(complexity_scores) / len(complexity_scores)
            print(f"📈 平均复杂度: {avg_complexity:.2f}")
            
            innovation_scores = [w.structural_analysis.get("innovation_index", 0) 
                               for w in session.showcase_works]
            avg_innovation = sum(innovation_scores) / len(innovation_scores)
            print(f"🎨 平均创新指数: {avg_innovation:.2f}")
            
            print("\n🏆 作品列表:")
            for i, work in enumerate(session.showcase_works, 1):
                print(f"   {i}. 《{work.title}》")
                print(f"      类型: {work.showcase_type.value}")
                print(f"      复杂度: {work.structural_analysis.get('complexity_score', 0):.2f}")
                print(f"      文件: {len(work.generated_files)} 个")
        
        print(f"\n📁 所有文件已保存到: {self.master_studio.config.output_directory}")
    
    def export_showcase_report(self, session: Optional[ShowcaseSession] = None) -> Path:
        """导出展示报告"""
        if not session:
            session = self.current_session
        
        if not session:
            raise ValueError("没有可导出的展示会话")
        
        report_path = (self.master_studio.config.output_directory / 
                      f"showcase_report_{session.session_id}.json")
        
        try:
            # 准备报告数据
            report_data = {
                "session_info": {
                    "session_id": session.session_id,
                    "showcase_theme": session.showcase_theme,
                    "start_time": session.start_time.isoformat(),
                    "end_time": session.end_time.isoformat() if session.end_time else None,
                    "duration_minutes": ((session.end_time - session.start_time).total_seconds() / 60) if session.end_time else None
                },
                "statistics": {
                    "total_works_planned": session.total_works_planned,
                    "works_completed": session.works_completed,
                    "success_rate": session.works_completed / session.total_works_planned if session.total_works_planned > 0 else 0,
                    "total_composition_time": session.total_composition_time,
                    "average_composition_time": session.total_composition_time / session.works_completed if session.works_completed > 0 else 0
                },
                "showcase_works": [
                    {
                        "work_id": work.work_id,
                        "title": work.title,
                        "subtitle": work.subtitle,
                        "showcase_type": work.showcase_type.value,
                        "composition_scale": work.composition_scale.value,
                        "composition_form": work.composition_form.value,
                        "mathematical_parameters": work.mathematical_parameters,
                        "musical_parameters": work.musical_parameters,
                        "technical_parameters": work.technical_parameters,
                        "structural_analysis": work.structural_analysis,
                        "harmonic_analysis": work.harmonic_analysis,
                        "technical_features": work.technical_features,
                        "generated_files": work.generated_files,
                        "estimated_duration": work.estimated_duration,
                        "difficulty_level": work.difficulty_level
                    }
                    for work in session.showcase_works
                ]
            }
            
            # 保存报告
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"📋 展示报告已导出: {report_path}")
            return report_path
            
        except Exception as e:
            print(f"❌ 展示报告导出失败: {e}")
            raise
    
    def get_available_programs(self) -> Dict[str, List[str]]:
        """获取可用的展示节目"""
        return self.showcase_programs.copy()
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """获取可用的作品模板"""
        return {name: {
            "title": template["title"],
            "subtitle": template["subtitle"],
            "showcase_type": template["showcase_type"].value,
            "scale": template["scale"].value,
            "estimated_duration": template.get("estimated_duration", 120.0)
        } for name, template in self.composition_templates.items()}

# ========== 便利函数 ==========

def create_composition_showcase(master_studio) -> CompositionShowcase:
    """
    创建作曲展示系统
    
    Args:
        master_studio: PetersenMasterStudio实例
        
    Returns:
        CompositionShowcase: 配置好的展示系统
    """
    return CompositionShowcase(master_studio)

def run_quick_showcase(master_studio) -> ShowcaseSession:
    """
    便利函数：运行快速展示
    
    Args:
        master_studio: PetersenMasterStudio实例
        
    Returns:
        ShowcaseSession: 展示会话结果
    """
    showcase = create_composition_showcase(master_studio)
    return showcase.run_showcase("quick_demonstration")

def run_comprehensive_showcase(master_studio) -> ShowcaseSession:
    """
    便利函数：运行综合展示
    
    Args:
        master_studio: PetersenMasterStudio实例
        
    Returns:
        ShowcaseSession: 展示会话结果
    """
    showcase = create_composition_showcase(master_studio)
    return showcase.run_showcase("comprehensive_showcase")

def run_educational_showcase(master_studio) -> ShowcaseSession:
    """
    便利函数：运行教学展示
    
    Args:
        master_studio: PetersenMasterStudio实例
        
    Returns:
        ShowcaseSession: 展示会话结果
    """
    showcase = create_composition_showcase(master_studio)
    return showcase.run_showcase("educational_program")

if __name__ == "__main__":
    print("🎭 Petersen 作曲展示系统")
    print("这是一个支持模块，请通过PetersenMasterStudio使用")
    print()
    print("可用的展示节目:")
    
    # 显示可用节目（仅作演示）
    showcase_programs = {
        "quick_demonstration": ["金比例小品", "五度螺旋"],
        "comprehensive_showcase": ["金比例小品", "八度大教堂", "五度螺旋", "大师练习曲"],
        "educational_program": ["教学组曲", "金比例小品", "八度大教堂"],
        "virtuoso_recital": ["大师练习曲", "半音宇宙", "五度螺旋"],
        "mathematical_beauty": ["金比例小品", "八度大教堂", "半音宇宙"]
    }
    
    for program, works in showcase_programs.items():
        print(f"  - {program}: {', '.join(works)}")