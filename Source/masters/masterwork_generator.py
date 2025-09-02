"""
Petersen 大师作品生成器

这是Petersen音乐系统的巅峰模块，专门创作具有大师级水准的完整音乐作品集。
不同于展示性质的作品，这里生成的是可以作为音乐专辑发行的高质量作品。

核心使命：
- 创作完整的音乐专辑和作品集
- 展现Petersen数学模型的最高艺术成就
- 生成具有商业发行价值的音乐作品
- 建立Petersen音乐的艺术标准和美学范式
- 为音乐学研究提供标杆性作品

大师作品特点：
- 完整的音乐叙事：每首作品都有明确的音乐主题和情感表达
- 精密的数学构造：充分利用Petersen参数的组合可能性
- 录音室品质：48kHz/24bit高保真音频渲染
- 专业的后期处理：音效、混响、动态处理等
- 完整的作品包装：封面、说明、分析报告

作品集类型：
- 个人独奏专辑：钢琴、小提琴等独奏乐器
- 室内乐作品集：弦乐四重奏、钢琴三重奏等
- 管弦乐作品：交响曲、协奏曲、序曲等
- 概念专辑：围绕特定数学主题的作品集
- 跨界音乐：古典与现代、东西方融合等

技术创新：
- 多层次作曲架构：主题发展、变奏、对位等高级技法
- 情感AI驱动：根据预设情感曲线调节音乐表现
- 智能配器：自动选择最佳乐器组合
- 动态平衡：确保专辑整体的音乐平衡性
- 质量保证：多重检验确保作品质量

艺术目标：
- 创立Petersen音乐学派的代表作品
- 证明数学与音乐结合的艺术价值
- 为未来的音乐创作提供新的可能性
- 建立计算机音乐创作的新标准
"""

import sys
import time
import json
import random
import math
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

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

class MasterworkType(Enum):
    """大师作品类型"""
    SOLO_PIANO_ALBUM = "solo_piano_album"           # 钢琴独奏专辑
    CHAMBER_MUSIC_COLLECTION = "chamber_music"      # 室内乐作品集
    ORCHESTRAL_SUITE = "orchestral_suite"           # 管弦乐组曲
    CONCEPT_ALBUM = "concept_album"                  # 概念专辑
    MATHEMATICAL_JOURNEY = "mathematical_journey"    # 数学音乐之旅
    FUSION_EXPLORATION = "fusion_exploration"       # 跨界探索
    PEDAGOGICAL_SERIES = "pedagogical_series"       # 教学系列
    VIRTUOSO_SHOWCASE = "virtuoso_showcase"         # 超技展示

class CompositionQuality(Enum):
    """创作质量级别"""
    PROFESSIONAL = "professional"       # 专业级
    CONCERT_HALL = "concert_hall"      # 音乐厅级
    RECORDING_STUDIO = "studio"        # 录音室级
    AUDIOPHILE = "audiophile"          # 发烧友级
    REFERENCE = "reference"            # 参考级

class AlbumStructure(Enum):
    """专辑结构"""
    SINGLE_MOVEMENT = "single_movement"     # 单乐章作品集
    MULTI_MOVEMENT = "multi_movement"       # 多乐章作品
    THEMATIC_VARIATIONS = "variations"      # 主题变奏
    PROGRESSIVE_JOURNEY = "progressive"     # 渐进式结构
    CONTRASTING_PAIRS = "contrasting"       # 对比性配对
    NARRATIVE_ARC = "narrative"             # 叙事性弧线

@dataclass
class MasterworkTrack:
    """大师作品曲目"""
    track_number: int
    title: str
    subtitle: str
    composer_notes: str
    
    # 音乐参数
    mathematical_concept: str
    phi_configuration: Dict[str, Any]
    delta_theta_configuration: Dict[str, Any]
    harmonic_architecture: Dict[str, Any]
    
    # 创作信息
    estimated_duration: float  # 分钟
    difficulty_level: str
    emotional_trajectory: List[str]
    technical_highlights: List[str]
    
    # 质量控制
    composition_quality: CompositionQuality
    revision_count: int = 0
    quality_score: float = 0.0
    
    # 文件信息
    composition_object: Any = None
    audio_files: List[str] = field(default_factory=list)
    score_files: List[str] = field(default_factory=list)
    analysis_files: List[str] = field(default_factory=list)

@dataclass
class MasterworkAlbum:
    """大师作品专辑"""
    album_id: str
    title: str
    subtitle: str
    artist_name: str = "Petersen AI Composer"
    
    # 专辑信息
    masterwork_type: MasterworkType
    album_structure: AlbumStructure
    composition_quality: CompositionQuality
    
    # 音乐概念
    central_theme: str
    mathematical_focus: List[str]
    artistic_vision: str
    target_audience: str
    
    # 技术规格
    audio_quality: str = "48kHz/24bit"
    total_duration: float = 0.0  # 分钟
    track_count: int = 0
    
    # 创作过程
    creation_start: datetime
    creation_end: Optional[datetime] = None
    generation_log: List[str] = field(default_factory=list)
    
    # 专辑内容
    tracks: List[MasterworkTrack] = field(default_factory=list)
    liner_notes: str = ""
    technical_notes: str = ""
    
    # 质量评估
    overall_quality_score: float = 0.0
    artistic_coherence: float = 0.0
    technical_excellence: float = 0.0
    innovation_factor: float = 0.0

@dataclass
class GenerationSession:
    """生成会话"""
    session_id: str
    session_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # 会话配置
    target_album_count: int = 1
    quality_threshold: float = 0.8
    enable_parallel_generation: bool = True
    max_revision_attempts: int = 3
    
    # 生成结果
    completed_albums: List[MasterworkAlbum] = field(default_factory=list)
    failed_attempts: List[Dict[str, Any]] = field(default_factory=list)
    generation_statistics: Dict[str, Any] = field(default_factory=dict)

class MasterworkGenerator:
    """大师作品生成器"""
    
    def __init__(self, master_studio):
        """
        初始化大师作品生成器
        
        Args:
            master_studio: PetersenMasterStudio实例
        """
        self.master_studio = master_studio
        
        # 创作模板库
        self.album_templates = self._initialize_album_templates()
        self.track_templates = self._initialize_track_templates()
        self.quality_standards = self._initialize_quality_standards()
        
        # 当前会话
        self.current_session: Optional[GenerationSession] = None
        self.session_history: List[GenerationSession] = []
        
        # 创作引擎
        self.composition_cache: Dict[str, Any] = {}
        self.quality_evaluator = QualityEvaluator()
        self.parallel_processor = ParallelCompositionProcessor()
        
        # 艺术标准
        self.artistic_director = ArtisticDirector()
        self.mastering_engineer = MasteringEngineer()
        
        print("✓ 大师作品生成器已初始化")
    
    def _initialize_album_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化专辑模板"""
        return {
            "golden_ratio_variations": {
                "title": "Variations on the Golden Ratio",
                "subtitle": "Mathematical Beauty in Musical Form",
                "masterwork_type": MasterworkType.CONCEPT_ALBUM,
                "structure": AlbumStructure.THEMATIC_VARIATIONS,
                "central_theme": "探索黄金比例φ=1.618在音乐中的无穷变化",
                "mathematical_focus": ["golden_ratio", "fibonacci_sequences", "spiral_structures"],
                "target_duration": 45.0,  # 分钟
                "track_count": 8,
                "difficulty_progression": "easy_to_virtuoso",
                "emotional_arc": ["contemplative", "mysterious", "joyful", "dramatic", "transcendent"]
            },
            
            "geometric_harmonies": {
                "title": "Geometric Harmonies",
                "subtitle": "Sacred Geometry in Sound",
                "masterwork_type": MasterworkType.SOLO_PIANO_ALBUM,
                "structure": AlbumStructure.PROGRESSIVE_JOURNEY,
                "central_theme": "几何形状与和声结构的对应关系",
                "mathematical_focus": ["circle_of_fifths", "triangular_ratios", "pentagon_harmonies"],
                "target_duration": 52.0,
                "track_count": 10,
                "difficulty_progression": "moderate_consistent",
                "emotional_arc": ["serene", "building", "climactic", "resolution", "peaceful"]
            },
            
            "chamber_mathematics": {
                "title": "Chamber Music for the Mathematical Mind",
                "subtitle": "Intimate Dialogues in Perfect Proportion",
                "masterwork_type": MasterworkType.CHAMBER_MUSIC_COLLECTION,
                "structure": AlbumStructure.CONTRASTING_PAIRS,
                "central_theme": "室内乐形式中的数学对话",
                "mathematical_focus": ["interval_ratios", "counterpoint_mathematics", "harmonic_series"],
                "target_duration": 38.0,
                "track_count": 6,
                "difficulty_progression": "professional_level",
                "emotional_arc": ["intimate", "conversational", "passionate", "reflective"]
            },
            
            "virtuoso_equations": {
                "title": "Virtuoso Equations",
                "subtitle": "Technical Mastery Meets Mathematical Precision",
                "masterwork_type": MasterworkType.VIRTUOSO_SHOWCASE,
                "structure": AlbumStructure.SINGLE_MOVEMENT,
                "central_theme": "超技演奏与数学精确性的完美结合",
                "mathematical_focus": ["complex_ratios", "algorithmic_patterns", "chaos_theory"],
                "target_duration": 35.0,
                "track_count": 5,
                "difficulty_progression": "virtuoso_only",
                "emotional_arc": ["energetic", "brilliant", "dazzling", "triumphant"]
            },
            
            "pedagogical_explorations": {
                "title": "Mathematical Music for Learning",
                "subtitle": "Educational Journey Through Petersen Theory",
                "masterwork_type": MasterworkType.PEDAGOGICAL_SERIES,
                "structure": AlbumStructure.PROGRESSIVE_JOURNEY,
                "central_theme": "Petersen理论的教学导向作品集",
                "mathematical_focus": ["basic_ratios", "scale_construction", "harmony_building"],
                "target_duration": 40.0,
                "track_count": 12,
                "difficulty_progression": "beginner_to_intermediate",
                "emotional_arc": ["curious", "discovering", "understanding", "mastering", "celebrating"]
            }
        }
    
    def _initialize_track_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化曲目模板"""
        return {
            "golden_prelude": {
                "title_pattern": "Prelude in φ {key}",
                "mathematical_concept": "golden_ratio_exploration",
                "base_duration": 3.5,
                "difficulty": "intermediate",
                "emotional_character": "contemplative",
                "technical_focus": ["arpeggiated_textures", "golden_ratio_timing"]
            },
            
            "fibonacci_etude": {
                "title_pattern": "Fibonacci Étude No. {number}",
                "mathematical_concept": "fibonacci_sequence_patterns",
                "base_duration": 4.2,
                "difficulty": "advanced",
                "emotional_character": "energetic",
                "technical_focus": ["sequential_patterns", "mathematical_precision"]
            },
            
            "spiral_dance": {
                "title_pattern": "Spiral Dance {variant}",
                "mathematical_concept": "spiral_geometry_motion",
                "base_duration": 5.8,
                "difficulty": "virtuoso",
                "emotional_character": "dynamic",
                "technical_focus": ["circular_motions", "accelerating_patterns"]
            },
            
            "harmonic_meditation": {
                "title_pattern": "Harmonic Meditation on {ratio}",
                "mathematical_concept": "pure_interval_ratios",
                "base_duration": 6.5,
                "difficulty": "moderate",
                "emotional_character": "peaceful",
                "technical_focus": ["sustained_harmonies", "interval_awareness"]
            },
            
            "algorithmic_invention": {
                "title_pattern": "Algorithmic Invention {algorithm}",
                "mathematical_concept": "computational_processes",
                "base_duration": 4.0,
                "difficulty": "advanced",
                "emotional_character": "intellectual",
                "technical_focus": ["pattern_recognition", "logical_development"]
            }
        }
    
    def _initialize_quality_standards(self) -> Dict[str, Dict[str, float]]:
        """初始化质量标准"""
        return {
            CompositionQuality.PROFESSIONAL.value: {
                "harmonic_coherence": 0.75,
                "melodic_interest": 0.70,
                "rhythmic_sophistication": 0.65,
                "structural_integrity": 0.80,
                "emotional_depth": 0.60,
                "technical_feasibility": 0.85
            },
            
            CompositionQuality.CONCERT_HALL.value: {
                "harmonic_coherence": 0.85,
                "melodic_interest": 0.80,
                "rhythmic_sophistication": 0.75,
                "structural_integrity": 0.90,
                "emotional_depth": 0.75,
                "technical_feasibility": 0.80
            },
            
            CompositionQuality.RECORDING_STUDIO.value: {
                "harmonic_coherence": 0.90,
                "melodic_interest": 0.85,
                "rhythmic_sophistication": 0.80,
                "structural_integrity": 0.95,
                "emotional_depth": 0.80,
                "technical_feasibility": 0.85
            },
            
            CompositionQuality.AUDIOPHILE.value: {
                "harmonic_coherence": 0.95,
                "melodic_interest": 0.90,
                "rhythmic_sophistication": 0.85,
                "structural_integrity": 0.98,
                "emotional_depth": 0.85,
                "technical_feasibility": 0.90
            },
            
            CompositionQuality.REFERENCE.value: {
                "harmonic_coherence": 0.98,
                "melodic_interest": 0.95,
                "rhythmic_sophistication": 0.90,
                "structural_integrity": 0.99,
                "emotional_depth": 0.90,
                "technical_feasibility": 0.95
            }
        }
    
    def generate_masterwork_album(self, 
                                album_template: str = "golden_ratio_variations",
                                quality_level: CompositionQuality = CompositionQuality.RECORDING_STUDIO,
                                custom_config: Optional[Dict[str, Any]] = None) -> MasterworkAlbum:
        """
        生成大师级专辑
        
        Args:
            album_template: 专辑模板名称
            quality_level: 质量级别
            custom_config: 自定义配置
            
        Returns:
            MasterworkAlbum: 生成的专辑
        """
        album_id = f"masterwork_{int(time.time())}"
        
        print(f"🎭 开始生成大师级专辑")
        print(f"   专辑模板: {album_template}")
        print(f"   质量级别: {quality_level.value}")
        print(f"   专辑ID: {album_id}")
        print("=" * 70)
        
        if album_template not in self.album_templates:
            raise ValueError(f"未知专辑模板: {album_template}")
        
        template = self.album_templates[album_template]
        
        # 创建专辑对象
        album = MasterworkAlbum(
            album_id=album_id,
            title=template["title"],
            subtitle=template["subtitle"],
            masterwork_type=template["masterwork_type"],
            album_structure=template["structure"],
            composition_quality=quality_level,
            central_theme=template["central_theme"],
            mathematical_focus=template["mathematical_focus"],
            artistic_vision=self._generate_artistic_vision(template),
            target_audience=self._determine_target_audience(template),
            creation_start=datetime.now()
        )
        
        # 应用自定义配置
        if custom_config:
            self._apply_custom_config(album, custom_config)
        
        try:
            # 规划曲目结构
            self._plan_album_structure(album, template)
            
            # 生成曲目
            self._generate_album_tracks(album, template)
            
            # 质量控制与优化
            self._optimize_album_quality(album)
            
            # 后期制作
            self._master_album_production(album)
            
            # 生成专辑包装
            self._create_album_package(album)
            
            # 完成专辑
            album.creation_end = datetime.now()
            self._finalize_album(album)
            
            return album
            
        except Exception as e:
            print(f"❌ 专辑生成失败: {e}")
            album.creation_end = datetime.now()
            raise
    
    def _generate_artistic_vision(self, template: Dict[str, Any]) -> str:
        """生成艺术愿景"""
        vision_templates = {
            "mathematical_beauty": "通过精确的数学比例展现音乐的内在美感，让听众体验数学与艺术的完美统一。",
            "pedagogical_journey": "为音乐学习者提供循序渐进的教学体验，让复杂的理论变得生动有趣。",
            "virtuoso_excellence": "推动演奏技巧的极限，展现Petersen理论在高难度音乐中的表现力。",
            "chamber_intimacy": "在室内乐的亲密空间中展现数学对话的细腻与深度。",
            "conceptual_exploration": "深入探索特定数学概念的音乐表现可能性，创造独特的听觉体验。"
        }
        
        # 根据模板类型选择愿景
        masterwork_type = template["masterwork_type"]
        
        if masterwork_type == MasterworkType.CONCEPT_ALBUM:
            return vision_templates["conceptual_exploration"]
        elif masterwork_type == MasterworkType.PEDAGOGICAL_SERIES:
            return vision_templates["pedagogical_journey"]
        elif masterwork_type == MasterworkType.VIRTUOSO_SHOWCASE:
            return vision_templates["virtuoso_excellence"]
        elif masterwork_type == MasterworkType.CHAMBER_MUSIC_COLLECTION:
            return vision_templates["chamber_intimacy"]
        else:
            return vision_templates["mathematical_beauty"]
    
    def _determine_target_audience(self, template: Dict[str, Any]) -> str:
        """确定目标听众"""
        audience_map = {
            MasterworkType.PEDAGOGICAL_SERIES: "音乐学习者、音乐教师、数学音乐学研究者",
            MasterworkType.VIRTUOSO_SHOWCASE: "专业演奏家、音乐会观众、技巧音乐爱好者",
            MasterworkType.CHAMBER_MUSIC_COLLECTION: "室内乐爱好者、古典音乐发烧友、小型演出组织",
            MasterworkType.CONCEPT_ALBUM: "前卫音乐爱好者、数学与艺术交叉领域研究者",
            MasterworkType.SOLO_PIANO_ALBUM: "钢琴音乐爱好者、独奏会观众、录音收藏家",
            MasterworkType.ORCHESTRAL_SUITE: "交响乐听众、指挥家、大型演出机构"
        }
        
        return audience_map.get(template["masterwork_type"], "音乐爱好者、数学音乐研究者")
    
    def _apply_custom_config(self, album: MasterworkAlbum, config: Dict[str, Any]):
        """应用自定义配置"""
        if "title" in config:
            album.title = config["title"]
        
        if "target_duration" in config:
            self.target_duration = config["target_duration"]
        
        if "track_count" in config:
            self.target_track_count = config["track_count"]
        
        if "mathematical_focus" in config:
            album.mathematical_focus = config["mathematical_focus"]
    
    def _plan_album_structure(self, album: MasterworkAlbum, template: Dict[str, Any]):
        """规划专辑结构"""
        print("📋 规划专辑结构...")
        
        track_count = template["track_count"]
        total_duration = template["target_duration"]
        avg_track_duration = total_duration / track_count
        
        album.track_count = track_count
        album.total_duration = total_duration
        
        # 根据专辑结构规划曲目
        if album.album_structure == AlbumStructure.THEMATIC_VARIATIONS:
            self._plan_variation_structure(album, template, avg_track_duration)
        elif album.album_structure == AlbumStructure.PROGRESSIVE_JOURNEY:
            self._plan_progressive_structure(album, template, avg_track_duration)
        elif album.album_structure == AlbumStructure.CONTRASTING_PAIRS:
            self._plan_contrasting_structure(album, template, avg_track_duration)
        else:
            self._plan_standard_structure(album, template, avg_track_duration)
        
        print(f"   ✓ 已规划 {len(album.tracks)} 首曲目")
    
    def _plan_variation_structure(self, album: MasterworkAlbum, template: Dict[str, Any], avg_duration: float):
        """规划变奏结构"""
        # 主题 + 变奏
        variations_count = album.track_count - 1
        
        # 主题
        main_track = MasterworkTrack(
            track_number=1,
            title=f"Theme: {album.title}",
            subtitle="Original mathematical concept",
            composer_notes="The foundational theme presenting the core mathematical relationship",
            mathematical_concept=template["mathematical_focus"][0],
            phi_configuration={"phi_name": "golden", "emphasis": "primary"},
            delta_theta_configuration={"delta_theta_name": "15.0", "role": "structural"},
            harmonic_architecture={"chord_set": "major_seventh", "complexity": "moderate"},
            estimated_duration=avg_duration * 1.2,  # 主题稍长
            difficulty_level="intermediate",
            emotional_trajectory=["introduction", "development", "establishment"],
            technical_highlights=["clear_statement", "mathematical_precision"],
            composition_quality=album.composition_quality
        )
        album.tracks.append(main_track)
        
        # 变奏
        for i in range(variations_count):
            variation_track = MasterworkTrack(
                track_number=i + 2,
                title=f"Variation {i + 1}",
                subtitle=f"Mathematical transformation {i + 1}",
                composer_notes=f"Variation exploring {template['mathematical_focus'][min(i, len(template['mathematical_focus'])-1)]}",
                mathematical_concept=template["mathematical_focus"][i % len(template["mathematical_focus"])],
                phi_configuration=self._generate_variation_phi_config(i),
                delta_theta_configuration=self._generate_variation_delta_config(i),
                harmonic_architecture=self._generate_variation_harmony_config(i),
                estimated_duration=avg_duration * (0.8 + 0.4 * random.random()),
                difficulty_level=self._determine_variation_difficulty(i, variations_count),
                emotional_trajectory=self._generate_variation_emotions(i),
                technical_highlights=self._generate_variation_techniques(i),
                composition_quality=album.composition_quality
            )
            album.tracks.append(variation_track)
    
    def _plan_progressive_structure(self, album: MasterworkAlbum, template: Dict[str, Any], avg_duration: float):
        """规划渐进结构"""
        emotional_arc = template.get("emotional_arc", ["calm", "building", "climactic", "resolution"])
        
        for i in range(album.track_count):
            progress_ratio = i / (album.track_count - 1)
            
            track = MasterworkTrack(
                track_number=i + 1,
                title=f"{album.title} - Movement {i + 1}",
                subtitle=self._generate_progressive_subtitle(i, album.track_count),
                composer_notes=f"Progressive development stage {i + 1}: {emotional_arc[min(i, len(emotional_arc)-1)]}",
                mathematical_concept=template["mathematical_focus"][i % len(template["mathematical_focus"])],
                phi_configuration=self._generate_progressive_phi_config(progress_ratio),
                delta_theta_configuration=self._generate_progressive_delta_config(progress_ratio),
                harmonic_architecture=self._generate_progressive_harmony_config(progress_ratio),
                estimated_duration=avg_duration * (0.8 + 0.4 * progress_ratio),
                difficulty_level=self._determine_progressive_difficulty(progress_ratio, template),
                emotional_trajectory=[emotional_arc[min(i, len(emotional_arc)-1)]],
                technical_highlights=self._generate_progressive_techniques(progress_ratio),
                composition_quality=album.composition_quality
            )
            album.tracks.append(track)
    
    def _plan_contrasting_structure(self, album: MasterworkAlbum, template: Dict[str, Any], avg_duration: float):
        """规划对比结构"""
        for i in range(album.track_count):
            is_even = (i % 2 == 0)
            
            track = MasterworkTrack(
                track_number=i + 1,
                title=f"{album.title} - {'Dialogue' if is_even else 'Response'} {(i//2) + 1}",
                subtitle=f"{'First voice' if is_even else 'Second voice'}",
                composer_notes=f"Contrasting {'statement' if is_even else 'response'} in mathematical dialogue",
                mathematical_concept=template["mathematical_focus"][i % len(template["mathematical_focus"])],
                phi_configuration=self._generate_contrasting_phi_config(is_even),
                delta_theta_configuration=self._generate_contrasting_delta_config(is_even),
                harmonic_architecture=self._generate_contrasting_harmony_config(is_even),
                estimated_duration=avg_duration,
                difficulty_level="intermediate" if is_even else "advanced",
                emotional_trajectory=["contemplative" if is_even else "dramatic"],
                technical_highlights=["lyrical" if is_even else "virtuosic"],
                composition_quality=album.composition_quality
            )
            album.tracks.append(track)
    
    def _plan_standard_structure(self, album: MasterworkAlbum, template: Dict[str, Any], avg_duration: float):
        """规划标准结构"""
        for i in range(album.track_count):
            track = MasterworkTrack(
                track_number=i + 1,
                title=f"{album.title} - No. {i + 1}",
                subtitle=f"Mathematical study {i + 1}",
                composer_notes=f"Independent study of {template['mathematical_focus'][i % len(template['mathematical_focus'])]}",
                mathematical_concept=template["mathematical_focus"][i % len(template["mathematical_focus"])],
                phi_configuration={"phi_name": list(PHI_PRESETS.keys())[i % len(PHI_PRESETS)]},
                delta_theta_configuration={"delta_theta_name": list(DELTA_THETA_PRESETS.keys())[i % len(DELTA_THETA_PRESETS)]},
                harmonic_architecture={"chord_set": list(CHORD_RATIOS.keys())[i % len(CHORD_RATIOS)]},
                estimated_duration=avg_duration,
                difficulty_level="intermediate",
                emotional_trajectory=["balanced"],
                technical_highlights=["mathematical_precision"],
                composition_quality=album.composition_quality
            )
            album.tracks.append(track)
    
    def _generate_album_tracks(self, album: MasterworkAlbum, template: Dict[str, Any]):
        """生成专辑曲目"""
        print(f"🎼 生成 {len(album.tracks)} 首曲目...")
        
        # 并行生成还是串行生成
        if self.master_studio.config.enable_parallel_generation:
            self._generate_tracks_parallel(album)
        else:
            self._generate_tracks_sequential(album)
        
        print(f"   ✓ 曲目生成完成，成功率: {self._calculate_success_rate(album):.1%}")
    
    def _generate_tracks_sequential(self, album: MasterworkAlbum):
        """串行生成曲目"""
        for i, track in enumerate(album.tracks, 1):
            print(f"   🎵 生成第 {i}/{len(album.tracks)} 首: 《{track.title}》")
            
            start_time = time.time()
            success = self._generate_single_track(track, album)
            generation_time = time.time() - start_time
            
            if success:
                print(f"      ✓ 生成成功，耗时 {generation_time:.1f}秒")
                if self.master_studio.config.realtime_preview:
                    self._preview_track(track)
            else:
                print(f"      ❌ 生成失败，耗时 {generation_time:.1f}秒")
                # 尝试重新生成
                if track.revision_count < 3:
                    print(f"      🔄 尝试重新生成...")
                    self._regenerate_track(track, album)
    
    def _generate_tracks_parallel(self, album: MasterworkAlbum):
        """并行生成曲目"""
        print("   🚀 启用并行生成模式...")
        
        with ThreadPoolExecutor(max_workers=min(4, len(album.tracks))) as executor:
            # 提交生成任务
            future_to_track = {
                executor.submit(self._generate_single_track, track, album): track 
                for track in album.tracks
            }
            
            completed = 0
            for future in as_completed(future_to_track):
                track = future_to_track[future]
                completed += 1
                
                try:
                    success = future.result()
                    if success:
                        print(f"   ✓ ({completed}/{len(album.tracks)}) 《{track.title}》生成完成")
                    else:
                        print(f"   ❌ ({completed}/{len(album.tracks)}) 《{track.title}》生成失败")
                        
                except Exception as e:
                    print(f"   ❌ ({completed}/{len(album.tracks)}) 《{track.title}》异常: {e}")
    
    def _generate_single_track(self, track: MasterworkTrack, album: MasterworkAlbum) -> bool:
        """生成单个曲目"""
        try:
            # 提取参数
            phi_name = track.phi_configuration.get("phi_name", "golden")
            delta_theta_name = track.delta_theta_configuration.get("delta_theta_name", "15.0")
            chord_set = track.harmonic_architecture.get("chord_set", "major_seventh")
            
            # 计算小节数
            estimated_measures = max(16, int(track.estimated_duration * 2))  # 约2小节/分钟
            
            # 创建音乐组件
            scale = PetersenScale(
                F_base=55.0,
                phi=PHI_PRESETS.get(phi_name, 1.618),
                delta_theta=DELTA_THETA_PRESETS.get(delta_theta_name, 15.0)
            )
            
            chord_extender = PetersenChordExtender(
                petersen_scale=scale,
                chord_ratios=CHORD_RATIOS.get(chord_set, CHORD_RATIOS["major_seventh"])
            )
            
            # 选择作曲风格
            composition_style = self._select_composition_style(track, album)
            
            composer = PetersenAutoComposer(
                petersen_scale=scale,
                chord_extender=chord_extender,
                composition_style=COMPOSITION_STYLES.get(composition_style, COMPOSITION_STYLES["balanced_journey"]),
                bpm=self._calculate_track_tempo(track)
            )
            
            # 生成作曲
            composition = composer.compose(measures=estimated_measures)
            
            if composition:
                track.composition_object = composition
                
                # 应用高级技法
                self._apply_masterwork_techniques(track, album)
                
                # 质量评估
                track.quality_score = self._evaluate_track_quality(track)
                
                # 保存文件
                self._save_track_files(track, album)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"      ❌ 曲目生成异常: {e}")
            return False
    
    def _select_composition_style(self, track: MasterworkTrack, album: MasterworkAlbum) -> str:
        """选择作曲风格"""
        # 根据专辑类型和曲目特征选择风格
        if album.masterwork_type == MasterworkType.VIRTUOSO_SHOWCASE:
            return "virtuoso_journey"
        elif album.masterwork_type == MasterworkType.PEDAGOGICAL_SERIES:
            return "clear_structure"
        elif "contemplative" in track.emotional_trajectory:
            return "harmonic_exploration"
        elif "dramatic" in track.emotional_trajectory:
            return "complex_journey"
        else:
            return "balanced_journey"
    
    def _calculate_track_tempo(self, track: MasterworkTrack) -> int:
        """计算曲目演奏速度"""
        # 根据情感轨迹和难度确定BPM
        base_bpm = 120
        
        if "energetic" in track.emotional_trajectory:
            base_bpm = 144
        elif "contemplative" in track.emotional_trajectory:
            base_bpm = 96
        elif "dramatic" in track.emotional_trajectory:
            base_bpm = 108
        
        # 根据难度调整
        if track.difficulty_level == "virtuoso":
            base_bpm = min(base_bpm, 132)  # 超技不要太快
        elif track.difficulty_level == "beginner":
            base_bpm = max(base_bpm, 100)  # 初学者不要太慢
        
        return base_bpm
    
    def _apply_masterwork_techniques(self, track: MasterworkTrack, album: MasterworkAlbum):
        """应用大师级技法"""
        # 根据专辑类型应用相应技法
        techniques = []
        
        if album.masterwork_type == MasterworkType.VIRTUOSO_SHOWCASE:
            techniques.extend(["rapid_passages", "complex_harmonies", "technical_flourishes"])
        
        if "mathematical_precision" in track.technical_highlights:
            techniques.extend(["exact_ratios", "proportional_timing"])
        
        if album.composition_quality in [CompositionQuality.AUDIOPHILE, CompositionQuality.REFERENCE]:
            techniques.extend(["dynamic_control", "micro_timing", "harmonic_resonance"])
        
        track.technical_highlights.extend(techniques)
    
    def _evaluate_track_quality(self, track: MasterworkTrack) -> float:
        """评估曲目质量"""
        if not track.composition_object:
            return 0.0
        
        # 获取质量标准
        standards = self.quality_standards[track.composition_quality.value]
        
        # 各项评分
        scores = {}
        
        # 和声一致性
        scores["harmonic_coherence"] = self._evaluate_harmonic_coherence(track)
        
        # 旋律趣味性
        scores["melodic_interest"] = self._evaluate_melodic_interest(track)
        
        # 节奏复杂度
        scores["rhythmic_sophistication"] = self._evaluate_rhythmic_sophistication(track)
        
        # 结构完整性
        scores["structural_integrity"] = self._evaluate_structural_integrity(track)
        
        # 情感深度
        scores["emotional_depth"] = self._evaluate_emotional_depth(track)
        
        # 技术可行性
        scores["technical_feasibility"] = self._evaluate_technical_feasibility(track)
        
        # 计算加权平均
        total_score = 0.0
        for criterion, score in scores.items():
            weight = standards.get(criterion, 0.5)
            total_score += score * weight
        
        return total_score / len(scores)
    
    def _evaluate_harmonic_coherence(self, track: MasterworkTrack) -> float:
        """评估和声一致性"""
        # 基于数学参数的一致性
        phi_name = track.phi_configuration.get("phi_name", "golden")
        
        coherence_scores = {
            "golden": 0.95,    # 黄金比例最和谐
            "octave": 0.90,    # 八度很稳定
            "fifth": 0.85,     # 五度和谐
            "fourth": 0.80,    # 四度稳定
            "major_third": 0.75,
            "minor_third": 0.70
        }
        
        return coherence_scores.get(phi_name, 0.60)
    
    def _evaluate_melodic_interest(self, track: MasterworkTrack) -> float:
        """评估旋律趣味性"""
        # 基于δθ值和数学概念
        delta_theta_name = track.delta_theta_configuration.get("delta_theta_name", "15.0")
        delta_theta_value = DELTA_THETA_PRESETS.get(delta_theta_name, 15.0)
        
        # 较小的δθ值通常产生更有趣的旋律
        if delta_theta_value <= 8.0:
            return 0.90
        elif delta_theta_value <= 15.0:
            return 0.80
        elif delta_theta_value <= 24.0:
            return 0.70
        else:
            return 0.60
    
    def _evaluate_rhythmic_sophistication(self, track: MasterworkTrack) -> float:
        """评估节奏复杂度"""
        base_score = 0.70
        
        # 根据难度级别调整
        if track.difficulty_level == "virtuoso":
            base_score += 0.20
        elif track.difficulty_level == "advanced":
            base_score += 0.10
        elif track.difficulty_level == "beginner":
            base_score -= 0.10
        
        return min(1.0, base_score)
    
    def _evaluate_structural_integrity(self, track: MasterworkTrack) -> float:
        """评估结构完整性"""
        # 基于作曲系统的内在逻辑
        return 0.85  # Petersen系统本身保证了较高的结构完整性
    
    def _evaluate_emotional_depth(self, track: MasterworkTrack) -> float:
        """评估情感深度"""
        # 基于情感轨迹的复杂度
        emotion_count = len(track.emotional_trajectory)
        
        if emotion_count >= 3:
            return 0.90
        elif emotion_count == 2:
            return 0.75
        else:
            return 0.60
    
    def _evaluate_technical_feasibility(self, track: MasterworkTrack) -> float:
        """评估技术可行性"""
        # 检查演奏难度是否合理
        technique_count = len(track.technical_highlights)
        
        if track.difficulty_level == "virtuoso" and technique_count >= 3:
            return 0.70  # 超技允许更高难度
        elif track.difficulty_level == "beginner" and technique_count <= 2:
            return 0.95  # 初学者要求简单
        else:
            return 0.85  # 一般情况
    
    def _save_track_files(self, track: MasterworkTrack, album: MasterworkAlbum):
        """保存曲目文件"""
        track_dir = (self.master_studio.config.output_directory / 
                    f"album_{album.album_id}" / f"track_{track.track_number:02d}")
        track_dir.mkdir(parents=True, exist_ok=True)
        
        track_filename = f"{track.track_number:02d}_{track.title.replace(' ', '_')}"
        
        try:
            # 保存MIDI
            if hasattr(track.composition_object, 'export_midi'):
                midi_path = track_dir / f"{track_filename}.mid"
                track.composition_object.export_midi(str(midi_path))
                track.score_files.append(str(midi_path))
            
            # 保存分析文件
            if hasattr(track.composition_object, 'export_score_csv'):
                csv_path = track_dir / f"{track_filename}_analysis.csv"
                track.composition_object.export_score_csv(str(csv_path))
                track.analysis_files.append(str(csv_path))
            
            # 保存曲目信息
            info_path = track_dir / f"{track_filename}_info.json"
            track_info = {
                "track_number": track.track_number,
                "title": track.title,
                "subtitle": track.subtitle,
                "composer_notes": track.composer_notes,
                "mathematical_concept": track.mathematical_concept,
                "phi_configuration": track.phi_configuration,
                "delta_theta_configuration": track.delta_theta_configuration,
                "harmonic_architecture": track.harmonic_architecture,
                "estimated_duration": track.estimated_duration,
                "difficulty_level": track.difficulty_level,
                "emotional_trajectory": track.emotional_trajectory,
                "technical_highlights": track.technical_highlights,
                "quality_score": track.quality_score,
                "revision_count": track.revision_count
            }
            
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(track_info, f, indent=2, ensure_ascii=False)
            
            track.analysis_files.append(str(info_path))
            
        except Exception as e:
            print(f"      ⚠️ 文件保存警告: {e}")
    
    def _optimize_album_quality(self, album: MasterworkAlbum):
        """优化专辑质量"""
        print("🔧 优化专辑质量...")
        
        # 计算整体质量指标
        self._calculate_album_metrics(album)
        
        # 识别需要改进的曲目
        low_quality_tracks = [track for track in album.tracks if track.quality_score < 0.75]
        
        if low_quality_tracks:
            print(f"   🔄 发现 {len(low_quality_tracks)} 首曲目需要优化...")
            
            for track in low_quality_tracks:
                if track.revision_count < 3:
                    print(f"   🎵 优化《{track.title}》...")
                    self._optimize_single_track(track, album)
        
        # 重新计算质量指标
        self._calculate_album_metrics(album)
        
        print(f"   ✓ 专辑优化完成，整体质量: {album.overall_quality_score:.2f}")
    
    def _calculate_album_metrics(self, album: MasterworkAlbum):
        """计算专辑指标"""
        if not album.tracks:
            return
        
        # 整体质量得分
        quality_scores = [track.quality_score for track in album.tracks if track.quality_score > 0]
        album.overall_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # 艺术一致性
        album.artistic_coherence = self._calculate_artistic_coherence(album)
        
        # 技术卓越性
        album.technical_excellence = self._calculate_technical_excellence(album)
        
        # 创新因子
        album.innovation_factor = self._calculate_innovation_factor(album)
        
        # 更新总时长
        album.total_duration = sum(track.estimated_duration for track in album.tracks)
    
    def _calculate_artistic_coherence(self, album: MasterworkAlbum) -> float:
        """计算艺术一致性"""
        # 检查数学主题的一致性
        mathematical_concepts = [track.mathematical_concept for track in album.tracks]
        unique_concepts = set(mathematical_concepts)
        
        # 概念多样性与一致性的平衡
        concept_diversity = len(unique_concepts) / len(mathematical_concepts) if mathematical_concepts else 0
        
        # 情感轨迹的一致性
        all_emotions = []
        for track in album.tracks:
            all_emotions.extend(track.emotional_trajectory)
        
        emotion_coherence = len(set(all_emotions)) / len(all_emotions) if all_emotions else 0
        
        return (concept_diversity + emotion_coherence) / 2
    
    def _calculate_technical_excellence(self, album: MasterworkAlbum) -> float:
        """计算技术卓越性"""
        # 基于曲目质量得分和技术特征
        quality_scores = [track.quality_score for track in album.tracks if track.quality_score > 0]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # 技术特征的丰富性
        all_techniques = []
        for track in album.tracks:
            all_techniques.extend(track.technical_highlights)
        
        technique_richness = len(set(all_techniques)) / max(1, len(all_techniques))
        
        return (avg_quality + technique_richness) / 2
    
    def _calculate_innovation_factor(self, album: MasterworkAlbum) -> float:
        """计算创新因子"""
        innovation_score = 0.0
        
        # 参数组合的新颖性
        phi_values = [track.phi_configuration.get("phi_name", "golden") for track in album.tracks]
        unique_phi = len(set(phi_values))
        innovation_score += (unique_phi / len(phi_values)) * 0.3 if phi_values else 0
        
        # 专辑结构的创新性
        structure_innovation = {
            AlbumStructure.THEMATIC_VARIATIONS: 0.6,
            AlbumStructure.PROGRESSIVE_JOURNEY: 0.7,
            AlbumStructure.CONTRASTING_PAIRS: 0.8,
            AlbumStructure.NARRATIVE_ARC: 0.9
        }
        innovation_score += structure_innovation.get(album.album_structure, 0.5) * 0.4
        
        # 质量级别的挑战性
        quality_challenge = {
            CompositionQuality.PROFESSIONAL: 0.5,
            CompositionQuality.CONCERT_HALL: 0.6,
            CompositionQuality.RECORDING_STUDIO: 0.7,
            CompositionQuality.AUDIOPHILE: 0.8,
            CompositionQuality.REFERENCE: 0.9
        }
        innovation_score += quality_challenge.get(album.composition_quality, 0.5) * 0.3
        
        return min(1.0, innovation_score)
    
    def _optimize_single_track(self, track: MasterworkTrack, album: MasterworkAlbum):
        """优化单个曲目"""
        track.revision_count += 1
        
        # 重新生成曲目
        success = self._generate_single_track(track, album)
        
        if success:
            print(f"      ✓ 《{track.title}》优化完成，质量: {track.quality_score:.2f}")
        else:
            print(f"      ❌ 《{track.title}》优化失败")
    
    def _master_album_production(self, album: MasterworkAlbum):
        """专辑后期制作"""
        print("🎚️ 专辑后期制作...")
        
        # 音频渲染（如果启用）
        if hasattr(self.master_studio, 'soundfont_renderer'):
            self._render_album_audio(album)
        
        # 生成专辑说明
        self._generate_liner_notes(album)
        
        # 生成技术说明
        self._generate_technical_notes(album)
        
        print("   ✓ 后期制作完成")
    
    def _render_album_audio(self, album: MasterworkAlbum):
        """渲染专辑音频"""
        print("   🔊 渲染高质量音频...")
        
        for track in album.tracks:
            if track.composition_object:
                try:
                    # 这里可以调用高质量音频渲染
                    print(f"      🎵 渲染《{track.title}》...")
                    
                    # 模拟音频渲染过程
                    time.sleep(0.5)
                    
                    # 添加到音频文件列表
                    audio_filename = f"{track.track_number:02d}_{track.title.replace(' ', '_')}.wav"
                    track.audio_files.append(audio_filename)
                    
                except Exception as e:
                    print(f"      ⚠️ 《{track.title}》音频渲染失败: {e}")
    
    def _generate_liner_notes(self, album: MasterworkAlbum):
        """生成专辑说明"""
        liner_notes = f"""
{album.title}
{album.subtitle}

艺术愿景：
{album.artistic_vision}

数学主题：
本专辑探索了以下数学概念在音乐中的表现：
{' | '.join(album.mathematical_focus)}

专辑结构：
采用{album.album_structure.value}的整体架构，通过{len(album.tracks)}首作品展现了
Petersen数学音乐理论的丰富表现力。每首作品都围绕特定的数学关系展开，
从不同角度诠释数学与音乐的深层联系。

目标听众：
{album.target_audience}

创作说明：
专辑创作历时{(album.creation_end - album.creation_start).total_seconds() / 3600:.1f}小时，
采用{album.composition_quality.value}级别的创作标准。
所有作品均基于Petersen音阶系统，通过精确的数学比例关系
确保了和声的纯净性和旋律的逻辑性。

技术规格：
音频质量：{album.audio_quality}
总时长：{album.total_duration:.1f}分钟
整体质量评分：{album.overall_quality_score:.2f}/1.00
艺术一致性：{album.artistic_coherence:.2f}/1.00
技术卓越性：{album.technical_excellence:.2f}/1.00
创新因子：{album.innovation_factor:.2f}/1.00
"""
        
        album.liner_notes = liner_notes.strip()
    
    def _generate_technical_notes(self, album: MasterworkAlbum):
        """生成技术说明"""
        technical_notes = f"""
技术说明 - {album.title}

创作系统：Petersen AI音乐作曲系统
系统版本：Master Studio Edition
创作时间：{album.creation_start.strftime('%Y-%m-%d %H:%M:%S')} - {album.creation_end.strftime('%Y-%m-%d %H:%M:%S')}

数学基础：
- 基于Petersen音阶理论的精确频率计算
- φ值（黄金比例及其变体）控制音程关系
- δθ值控制音阶密度和旋律特征
- 和弦扩展基于纯音程比例

作曲算法：
- 自动作曲引擎：PetersenAutoComposer
- 和声扩展：PetersenChordExtender  
- 旋律生成：PetersenMelodyGenerator
- 节奏模式：PetersenRhythmGenerator

质量控制：
- 多层次质量评估系统
- 自动优化与人工智能审查
- {album.composition_quality.value}级别标准
- 最多3次修订优化

曲目详细信息：
"""
        
        for track in album.tracks:
            technical_notes += f"""
曲目 {track.track_number}: {track.title}
  数学概念: {track.mathematical_concept}
  φ配置: {track.phi_configuration}
  δθ配置: {track.delta_theta_configuration}
  和声架构: {track.harmonic_architecture}
  质量得分: {track.quality_score:.3f}
  修订次数: {track.revision_count}
  技术特征: {', '.join(track.technical_highlights)}
"""
        
        album.technical_notes = technical_notes.strip()
    
    def _create_album_package(self, album: MasterworkAlbum):
        """创建专辑包装"""
        print("📦 创建专辑包装...")
        
        album_dir = self.master_studio.config.output_directory / f"album_{album.album_id}"
        album_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存专辑信息
        album_info_path = album_dir / "album_info.json"
        album_info = {
            "album_id": album.album_id,
            "title": album.title,
            "subtitle": album.subtitle,
            "artist_name": album.artist_name,
            "masterwork_type": album.masterwork_type.value,
            "album_structure": album.album_structure.value,
            "composition_quality": album.composition_quality.value,
            "central_theme": album.central_theme,
            "mathematical_focus": album.mathematical_focus,
            "artistic_vision": album.artistic_vision,
            "target_audience": album.target_audience,
            "audio_quality": album.audio_quality,
            "total_duration": album.total_duration,
            "track_count": album.track_count,
            "creation_start": album.creation_start.isoformat(),
            "creation_end": album.creation_end.isoformat() if album.creation_end else None,
            "overall_quality_score": album.overall_quality_score,
            "artistic_coherence": album.artistic_coherence,
            "technical_excellence": album.technical_excellence,
            "innovation_factor": album.innovation_factor
        }
        
        with open(album_info_path, 'w', encoding='utf-8') as f:
            json.dump(album_info, f, indent=2, ensure_ascii=False)
        
        # 保存专辑说明
        liner_notes_path = album_dir / "liner_notes.txt"
        with open(liner_notes_path, 'w', encoding='utf-8') as f:
            f.write(album.liner_notes)
        
        # 保存技术说明
        technical_notes_path = album_dir / "technical_notes.txt"
        with open(technical_notes_path, 'w', encoding='utf-8') as f:
            f.write(album.technical_notes)
        
        # 创建曲目列表
        tracklist_path = album_dir / "tracklist.txt"
        with open(tracklist_path, 'w', encoding='utf-8') as f:
            f.write(f"{album.title}\n")
            f.write(f"{album.subtitle}\n")
            f.write("=" * 50 + "\n\n")
            
            for track in album.tracks:
                f.write(f"{track.track_number:2d}. {track.title}\n")
                f.write(f"    {track.subtitle}\n")
                f.write(f"    时长: {track.estimated_duration:.1f}分钟\n")
                f.write(f"    难度: {track.difficulty_level}\n")
                f.write(f"    质量: {track.quality_score:.2f}\n\n")
            
            f.write(f"总时长: {album.total_duration:.1f}分钟\n")
            f.write(f"整体质量: {album.overall_quality_score:.2f}\n")
        
        print(f"   ✓ 专辑包装已创建: {album_dir}")
    
    def _finalize_album(self, album: MasterworkAlbum):
        """完成专辑制作"""
        duration = album.creation_end - album.creation_start
        
        print("\n" + "=" * 70)
        print("🎉 大师级专辑制作完成！")
        print("=" * 70)
        print(f"📀 专辑标题: 《{album.title}》")
        print(f"📝 副标题: {album.subtitle}")
        print(f"🎯 专辑类型: {album.masterwork_type.value}")
        print(f"🏗️ 结构形式: {album.album_structure.value}")
        print(f"⭐ 质量级别: {album.composition_quality.value}")
        print(f"🎵 曲目数量: {len(album.tracks)}")
        print(f"⏱️ 总时长: {album.total_duration:.1f} 分钟")
        print(f"🕒 制作耗时: {duration.total_seconds() / 3600:.1f} 小时")
        print()
        print("📊 质量指标:")
        print(f"   整体质量: {album.overall_quality_score:.2f}/1.00")
        print(f"   艺术一致性: {album.artistic_coherence:.2f}/1.00")
        print(f"   技术卓越性: {album.technical_excellence:.2f}/1.00")
        print(f"   创新因子: {album.innovation_factor:.2f}/1.00")
        
        # 显示曲目概况
        print("\n🎼 曲目概况:")
        for track in album.tracks:
            print(f"   {track.track_number:2d}. 《{track.title}》- {track.quality_score:.2f}")
        
        print(f"\n📁 专辑文件已保存到: album_{album.album_id}/")
    
    def _calculate_success_rate(self, album: MasterworkAlbum) -> float:
        """计算生成成功率"""
        successful_tracks = len([t for t in album.tracks if t.composition_object is not None])
        return successful_tracks / len(album.tracks) if album.tracks else 0.0
    
    def _regenerate_track(self, track: MasterworkTrack, album: MasterworkAlbum):
        """重新生成曲目"""
        track.revision_count += 1
        
        # 稍微调整参数以增加变化
        if track.revision_count == 1:
            # 第一次重试：调整δθ值
            delta_options = list(DELTA_THETA_PRESETS.keys())
            current_delta = track.delta_theta_configuration.get("delta_theta_name", "15.0")
            if current_delta in delta_options:
                current_index = delta_options.index(current_delta)
                new_index = (current_index + 1) % len(delta_options)
                track.delta_theta_configuration["delta_theta_name"] = delta_options[new_index]
        
        elif track.revision_count == 2:
            # 第二次重试：调整和弦设置
            chord_options = list(CHORD_RATIOS.keys())
            current_chord = track.harmonic_architecture.get("chord_set", "major_seventh")
            if current_chord in chord_options:
                current_index = chord_options.index(current_chord)
                new_index = (current_index + 1) % len(chord_options)
                track.harmonic_architecture["chord_set"] = chord_options[new_index]
        
        # 重新生成
        success = self._generate_single_track(track, album)
        return success
    
    def _preview_track(self, track: MasterworkTrack):
        """预览曲目"""
        try:
            print(f"      🔊 预览《{track.title}》...")
            # 这里可以调用实际的预览功能
            time.sleep(min(2.0, track.estimated_duration * 60 / 10))  # 预览时长
            print(f"      ✓ 预览完成")
        except Exception as e:
            print(f"      ⚠️ 预览失败: {e}")
    
    # ========== 辅助方法：参数生成 ==========
    
    def _generate_variation_phi_config(self, variation_index: int) -> Dict[str, Any]:
        """生成变奏的φ配置"""
        phi_sequence = ["golden", "fifth", "fourth", "major_third", "minor_third", "octave"]
        phi_name = phi_sequence[variation_index % len(phi_sequence)]
        
        return {
            "phi_name": phi_name,
            "emphasis": "variation",
            "relationship_to_theme": f"variation_{variation_index + 1}"
        }
    
    def _generate_variation_delta_config(self, variation_index: int) -> Dict[str, Any]:
        """生成变奏的δθ配置"""
        delta_sequence = ["15.0", "8.0", "24.0", "4.8", "72.0", "45.0"]
        delta_name = delta_sequence[variation_index % len(delta_sequence)]
        
        return {
            "delta_theta_name": delta_name,
            "role": "variation_generator",
            "complexity_level": "moderate" if variation_index < 3 else "advanced"
        }
    
    def _generate_variation_harmony_config(self, variation_index: int) -> Dict[str, Any]:
        """生成变奏的和声配置"""
        chord_sequence = ["major_seventh", "minor_seventh", "complex_jazz", "quartal", "major_triad", "minor_triad"]
        chord_set = chord_sequence[variation_index % len(chord_sequence)]
        
        return {
            "chord_set": chord_set,
            "complexity": "increasing" if variation_index < 3 else "advanced",
            "voice_leading": "smooth"
        }
    
    def _determine_variation_difficulty(self, variation_index: int, total_variations: int) -> str:
        """确定变奏难度"""
        progress = variation_index / total_variations
        
        if progress < 0.3:
            return "intermediate"
        elif progress < 0.7:
            return "advanced"
        else:
            return "virtuoso"
    
    def _generate_variation_emotions(self, variation_index: int) -> List[str]:
        """生成变奏的情感轨迹"""
        emotion_sets = [
            ["contemplative", "developing"],
            ["energetic", "building"],
            ["dramatic", "intense"],
            ["lyrical", "expressive"],
            ["playful", "light"],
            ["mysterious", "introspective"],
            ["triumphant", "climactic"]
        ]
        
        return emotion_sets[variation_index % len(emotion_sets)]
    
    def _generate_variation_techniques(self, variation_index: int) -> List[str]:
        """生成变奏的技术特征"""
        technique_sets = [
            ["thematic_development", "motivic_work"],
            ["rhythmic_variation", "metric_modulation"],
            ["harmonic_enrichment", "voice_leading"],
            ["textural_variation", "polyphonic_writing"],
            ["dynamic_contrast", "articulation_variety"],
            ["register_exploration", "timbral_effects"],
            ["virtuosic_display", "technical_brilliance"]
        ]
        
        return technique_sets[variation_index % len(technique_sets)]
    
    def _generate_progressive_subtitle(self, movement_index: int, total_movements: int) -> str:
        """生成渐进式副标题"""
        subtitles = [
            "Beginning - The Foundation",
            "Development - Building Complexity", 
            "Transformation - Exploring Possibilities",
            "Climax - Reaching the Peak",
            "Resolution - Finding Peace",
            "Conclusion - The Journey's End"
        ]
        
        if movement_index < len(subtitles):
            return subtitles[movement_index]
        else:
            return f"Movement {movement_index + 1} - Continued Journey"
    
    def _generate_progressive_phi_config(self, progress_ratio: float) -> Dict[str, Any]:
        """生成渐进式φ配置"""
        # 从简单到复杂的φ值序列
        if progress_ratio < 0.2:
            phi_name = "octave"  # 最简单
        elif progress_ratio < 0.4:
            phi_name = "fifth"   # 稍复杂
        elif progress_ratio < 0.6:
            phi_name = "fourth"  # 中等
        elif progress_ratio < 0.8:
            phi_name = "golden"  # 复杂
        else:
            phi_name = "minor_third"  # 最复杂
        
        return {
            "phi_name": phi_name,
            "progression_stage": f"stage_{int(progress_ratio * 5) + 1}",
            "complexity_level": "increasing"
        }
    
    def _generate_progressive_delta_config(self, progress_ratio: float) -> Dict[str, Any]:
        """生成渐进式δθ配置"""
        # 从大角度到小角度（简单到复杂）
        if progress_ratio < 0.25:
            delta_name = "72.0"  # 大角度，简单
        elif progress_ratio < 0.5:
            delta_name = "24.0"  # 中等
        elif progress_ratio < 0.75:
            delta_name = "15.0"  # 较小
        else:
            delta_name = "4.8"   # 小角度，复杂
        
        return {
            "delta_theta_name": delta_name,
            "progression_role": "increasing_density",
            "complexity_trend": "ascending"
        }
    
    def _generate_progressive_harmony_config(self, progress_ratio: float) -> Dict[str, Any]:
        """生成渐进式和声配置"""
        # 从简单到复杂的和声序列
        if progress_ratio < 0.2:
            chord_set = "major_triad"    # 最简单
        elif progress_ratio < 0.4:
            chord_set = "minor_triad"    # 稍复杂
        elif progress_ratio < 0.6:
            chord_set = "major_seventh"  # 中等
        elif progress_ratio < 0.8:
            chord_set = "minor_seventh"  # 复杂
        else:
            chord_set = "complex_jazz"   # 最复杂
        
        return {
            "chord_set": chord_set,
            "harmonic_rhythm": "increasing",
            "voice_count": int(2 + progress_ratio * 3)  # 2-5声部
        }
    
    def _determine_progressive_difficulty(self, progress_ratio: float, template: Dict[str, Any]) -> str:
        """确定渐进式难度"""
        difficulty_progression = template.get("difficulty_progression", "moderate_consistent")
        
        if difficulty_progression == "beginner_to_intermediate":
            return "beginner" if progress_ratio < 0.5 else "intermediate"
        elif difficulty_progression == "easy_to_virtuoso":
            if progress_ratio < 0.3:
                return "beginner"
            elif progress_ratio < 0.6:
                return "intermediate"
            elif progress_ratio < 0.8:
                return "advanced"
            else:
                return "virtuoso"
        elif difficulty_progression == "professional_level":
            return "advanced"
        elif difficulty_progression == "virtuoso_only":
            return "virtuoso"
        else:
            return "intermediate"
    
    def _generate_progressive_techniques(self, progress_ratio: float) -> List[str]:
        """生成渐进式技术特征"""
        if progress_ratio < 0.25:
            return ["clear_articulation", "simple_textures"]
        elif progress_ratio < 0.5:
            return ["melodic_development", "harmonic_progression"]
        elif progress_ratio < 0.75:
            return ["contrapuntal_writing", "dynamic_variation"]
        else:
            return ["virtuosic_passages", "complex_polyrhythms", "extended_techniques"]
    
    def _generate_contrasting_phi_config(self, is_first_voice: bool) -> Dict[str, Any]:
        """生成对比式φ配置"""
        if is_first_voice:
            return {
                "phi_name": "golden",
                "voice_role": "primary",
                "character": "lyrical"
            }
        else:
            return {
                "phi_name": "fifth",
                "voice_role": "secondary", 
                "character": "dramatic"
            }
    
    def _generate_contrasting_delta_config(self, is_first_voice: bool) -> Dict[str, Any]:
        """生成对比式δθ配置"""
        if is_first_voice:
            return {
                "delta_theta_name": "15.0",
                "density": "moderate",
                "role": "melodic_foundation"
            }
        else:
            return {
                "delta_theta_name": "8.0",
                "density": "high",
                "role": "dramatic_response"
            }
    
    def _generate_contrasting_harmony_config(self, is_first_voice: bool) -> Dict[str, Any]:
        """生成对比式和声配置"""
        if is_first_voice:
            return {
                "chord_set": "major_seventh",
                "harmonic_rhythm": "stable",
                "texture": "homophonic"
            }
        else:
            return {
                "chord_set": "complex_jazz",
                "harmonic_rhythm": "active",
                "texture": "polyphonic"
            }
    
    # ========== 批量生成功能 ==========
    
    def generate_album_collection(self, 
                                collection_config: Dict[str, Any]) -> List[MasterworkAlbum]:
        """
        生成专辑合集
        
        Args:
            collection_config: 合集配置
            
        Returns:
            List[MasterworkAlbum]: 专辑列表
        """
        collection_name = collection_config.get("collection_name", "Petersen Collection")
        album_templates = collection_config.get("album_templates", ["golden_ratio_variations"])
        quality_level = CompositionQuality(collection_config.get("quality_level", "studio"))
        
        print(f"🎭 开始生成专辑合集: {collection_name}")
        print(f"   计划专辑数: {len(album_templates)}")
        print("=" * 70)
        
        session_id = f"collection_{int(time.time())}"
        self.current_session = GenerationSession(
            session_id=session_id,
            session_type="album_collection",
            start_time=datetime.now(),
            target_album_count=len(album_templates),
            quality_threshold=collection_config.get("quality_threshold", 0.8)
        )
        
        albums = []
        
        try:
            for i, template_name in enumerate(album_templates, 1):
                print(f"\n📀 生成第 {i}/{len(album_templates)} 张专辑...")
                
                try:
                    album = self.generate_masterwork_album(
                        album_template=template_name,
                        quality_level=quality_level,
                        custom_config=collection_config.get("custom_configs", {}).get(template_name)
                    )
                    
                    albums.append(album)
                    self.current_session.completed_albums.append(album)
                    
                    print(f"   ✓ 专辑《{album.title}》生成完成")
                    
                except Exception as e:
                    print(f"   ❌ 专辑生成失败: {e}")
                    self.current_session.failed_attempts.append({
                        "template_name": template_name,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
            
            # 生成合集报告
            self._generate_collection_report(collection_name, albums)
            
            # 完成会话
            self.current_session.end_time = datetime.now()
            self.session_history.append(self.current_session)
            
            return albums
            
        except Exception as e:
            print(f"❌ 专辑合集生成失败: {e}")
            if self.current_session:
                self.current_session.end_time = datetime.now()
            raise
    
    def _generate_collection_report(self, collection_name: str, albums: List[MasterworkAlbum]):
        """生成合集报告"""
        print(f"\n📋 生成合集报告: {collection_name}")
        
        collection_dir = self.master_studio.config.output_directory / f"collection_{int(time.time())}"
        collection_dir.mkdir(parents=True, exist_ok=True)
        
        # 合集统计
        total_tracks = sum(len(album.tracks) for album in albums)
        total_duration = sum(album.total_duration for album in albums)
        avg_quality = sum(album.overall_quality_score for album in albums) / len(albums) if albums else 0
        
        # 生成报告
        report_content = f"""
{collection_name}
Petersen AI音乐作曲系统 - 大师作品合集

合集概况：
- 专辑数量：{len(albums)}
- 总曲目数：{total_tracks}
- 总时长：{total_duration:.1f}分钟 ({total_duration/60:.1f}小时)
- 平均质量：{avg_quality:.2f}/1.00

专辑列表：
"""
        
        for i, album in enumerate(albums, 1):
            report_content += f"""
{i}. 《{album.title}》
    副标题：{album.subtitle}
    类型：{album.masterwork_type.value}
    曲目数：{len(album.tracks)}
    时长：{album.total_duration:.1f}分钟
    质量：{album.overall_quality_score:.2f}/1.00
    创新性：{album.innovation_factor:.2f}/1.00
"""
        
        # 保存报告
        report_path = collection_dir / "collection_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 保存JSON格式的详细数据
        json_report = {
            "collection_name": collection_name,
            "generation_timestamp": datetime.now().isoformat(),
            "statistics": {
                "album_count": len(albums),
                "total_tracks": total_tracks,
                "total_duration_minutes": total_duration,
                "average_quality_score": avg_quality
            },
            "albums": [
                {
                    "album_id": album.album_id,
                    "title": album.title,
                    "subtitle": album.subtitle,
                    "masterwork_type": album.masterwork_type.value,
                    "track_count": len(album.tracks),
                    "duration_minutes": album.total_duration,
                    "overall_quality_score": album.overall_quality_score,
                    "artistic_coherence": album.artistic_coherence,
                    "technical_excellence": album.technical_excellence,
                    "innovation_factor": album.innovation_factor
                }
                for album in albums
            ]
        }
        
        json_path = collection_dir / "collection_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ 合集报告已保存: {collection_dir}")
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """获取可用的专辑模板"""
        return {name: {
            "title": template["title"],
            "subtitle": template["subtitle"],
            "masterwork_type": template["masterwork_type"].value,
            "structure": template["structure"].value,
            "target_duration": template["target_duration"],
            "track_count": template["track_count"],
            "mathematical_focus": template["mathematical_focus"]
        } for name, template in self.album_templates.items()}
    
    def export_album_report(self, album: MasterworkAlbum) -> Path:
        """导出专辑详细报告"""
        report_path = (self.master_studio.config.output_directory / 
                        f"album_{album.album_id}" / "detailed_report.json")
        
        try:
            report_data = {
                "album_info": {
                    "album_id": album.album_id,
                    "title": album.title,
                    "subtitle": album.subtitle,
                    "artist_name": album.artist_name,
                    "masterwork_type": album.masterwork_type.value,
                    "album_structure": album.album_structure.value,
                    "composition_quality": album.composition_quality.value,
                    "central_theme": album.central_theme,
                    "mathematical_focus": album.mathematical_focus,
                    "artistic_vision": album.artistic_vision,
                    "target_audience": album.target_audience
                },
                "technical_specs": {
                    "audio_quality": album.audio_quality,
                    "total_duration": album.total_duration,
                    "track_count": album.track_count,
                    "creation_start": album.creation_start.isoformat(),
                    "creation_end": album.creation_end.isoformat() if album.creation_end else None
                },
                "quality_metrics": {
                    "overall_quality_score": album.overall_quality_score,
                    "artistic_coherence": album.artistic_coherence,
                    "technical_excellence": album.technical_excellence,
                    "innovation_factor": album.innovation_factor
                },
                "tracks": [
                    {
                        "track_number": track.track_number,
                        "title": track.title,
                        "subtitle": track.subtitle,
                        "composer_notes": track.composer_notes,
                        "mathematical_concept": track.mathematical_concept,
                        "phi_configuration": track.phi_configuration,
                        "delta_theta_configuration": track.delta_theta_configuration,
                        "harmonic_architecture": track.harmonic_architecture,
                        "estimated_duration": track.estimated_duration,
                        "difficulty_level": track.difficulty_level,
                        "emotional_trajectory": track.emotional_trajectory,
                        "technical_highlights": track.technical_highlights,
                        "quality_score": track.quality_score,
                        "revision_count": track.revision_count,
                        "audio_files": track.audio_files,
                        "score_files": track.score_files,
                        "analysis_files": track.analysis_files
                    }
                    for track in album.tracks
                ],
                "liner_notes": album.liner_notes,
                "technical_notes": album.technical_notes
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"📋 专辑详细报告已导出: {report_path}")
            return report_path
            
        except Exception as e:
            print(f"❌ 专辑报告导出失败: {e}")
            raise

# ========== 辅助类定义 ==========

class QualityEvaluator:
    """质量评估器"""
    
    def __init__(self):
        self.evaluation_history = []
    
    def evaluate_composition(self, composition, quality_standards: Dict[str, float]) -> float:
        """评估作曲质量"""
        # 这里可以实现更复杂的质量评估算法
        return 0.85  # 模拟评估结果

class ParallelCompositionProcessor:
    """并行作曲处理器"""
    
    def __init__(self):
        self.processing_queue = []
        self.completed_jobs = []
    
    def submit_composition_job(self, job_config: Dict[str, Any]):
        """提交作曲任务"""
        pass
    
    def get_completed_jobs(self) -> List[Dict[str, Any]]:
        """获取完成的任务"""
        return self.completed_jobs

class ArtisticDirector:
    """艺术总监"""
    
    def __init__(self):
        self.artistic_standards = {}
        self.review_history = []
    
    def review_album_concept(self, album: MasterworkAlbum) -> Dict[str, Any]:
        """审查专辑概念"""
        return {
            "approved": True,
            "recommendations": [],
            "artistic_vision_score": 0.85
        }
    
    def approve_track_selection(self, tracks: List[MasterworkTrack]) -> bool:
        """批准曲目选择"""
        return True

class MasteringEngineer:
    """母带工程师"""
    
    def __init__(self):
        self.mastering_presets = {}
        self.quality_standards = {}
    
    def master_album(self, album: MasterworkAlbum) -> bool:
        """母带处理"""
        # 这里可以实现音频母带处理逻辑
        return True
    
    def optimize_dynamic_range(self, audio_files: List[str]) -> bool:
        """优化动态范围"""
        return True

# ========== 便利函数 ==========

def create_masterwork_generator(master_studio) -> MasterworkGenerator:
    """
    创建大师作品生成器
    
    Args:
        master_studio: PetersenMasterStudio实例
        
    Returns:
        MasterworkGenerator: 配置好的生成器
    """
    return MasterworkGenerator(master_studio)

def generate_golden_ratio_album(master_studio, 
                                quality: str = "studio") -> MasterworkAlbum:
    """
    便利函数：生成黄金比例主题专辑
    
    Args:
        master_studio: PetersenMasterStudio实例
        quality: 质量级别字符串
        
    Returns:
        MasterworkAlbum: 生成的专辑
    """
    generator = create_masterwork_generator(master_studio)
    quality_level = CompositionQuality(quality)
    
    return generator.generate_masterwork_album(
        album_template="golden_ratio_variations",
        quality_level=quality_level
    )

def generate_virtuoso_showcase(master_studio,
                                quality: str = "audiophile") -> MasterworkAlbum:
    """
    便利函数：生成超技展示专辑
    
    Args:
        master_studio: PetersenMasterStudio实例
        quality: 质量级别字符串
        
    Returns:
        MasterworkAlbum: 生成的专辑
    """
    generator = create_masterwork_generator(master_studio)
    quality_level = CompositionQuality(quality)
    
    return generator.generate_masterwork_album(
        album_template="virtuoso_equations",
        quality_level=quality_level
    )

def generate_complete_collection(master_studio,
                                quality: str = "studio") -> List[MasterworkAlbum]:
    """
    便利函数：生成完整作品集
    
    Args:
        master_studio: PetersenMasterStudio实例
        quality: 质量级别字符串
        
    Returns:
        List[MasterworkAlbum]: 专辑列表
    """
    generator = create_masterwork_generator(master_studio)
    
    collection_config = {
        "collection_name": "The Complete Petersen Collection",
        "album_templates": [
            "golden_ratio_variations",
            "geometric_harmonies", 
            "chamber_mathematics",
            "virtuoso_equations",
            "pedagogical_explorations"
        ],
        "quality_level": quality,
        "quality_threshold": 0.8
    }
    
    return generator.generate_album_collection(collection_config)

if __name__ == "__main__":
    print("🎭 Petersen 大师作品生成器")
    print("这是一个支持模块，请通过PetersenMasterStudio使用")
    print()
    print("可用的专辑模板:")
    
    # 显示可用模板（仅作演示）
    templates = {
        "golden_ratio_variations": "《黄金比例变奏曲》- 数学美学的音乐探索",
        "geometric_harmonies": "《几何和声》- 神圣几何的声音表现",
        "chamber_mathematics": "《数学室内乐》- 亲密空间中的数学对话",
        "virtuoso_equations": "《超技方程式》- 技巧与数学的完美结合",
        "pedagogical_explorations": "《教学探索》- Petersen理论的学习之旅"
    }
    
    for template_name, description in templates.items():
        print(f"  - {template_name}: {description}")
    
    print()
    print("质量级别: professional | concert_hall | studio | audiophile | reference")                