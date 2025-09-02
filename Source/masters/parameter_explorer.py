"""
Petersen 参数空间探索引擎

这是Petersen音乐系统参数空间的系统化探索工具，能够智能地生成参数组合，
创建对比作品，并分析不同数学参数对音乐美学的影响。

核心功能：
- 智能参数组合生成：避免无效组合，优化探索效率
- 分层探索策略：从基础对比到深度分析
- 数学美学量化：建立参数与音乐效果的映射关系
- 对比分析报告：可视化参数影响并提供建议
- 批量作品生成：高效创建参数空间作品集

探索维度：
- φ值系统：16个预设值（黄金比例、八度、五度等）
- δθ值系统：21个预设值（不同几何分割角度）
- 和弦比率组合：8种扩展模式
- 作曲风格：多种预设组合
- 演奏技法：不同复杂度级别

使用场景：
- 数学音乐学研究：量化参数对和声的影响
- 作曲家工具：发现新的音响组合
- 音乐教育：展示数学与音乐的关系
- 系统验证：测试Petersen模型的表现力

技术特点：
- 智能剪枝：避免产生过于相似的组合
- 渐进式探索：支持快速概览和深度分析
- 并行处理：支持批量作品生成
- 结果缓存：避免重复计算
"""

import sys
import time
import json
import itertools
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Set
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

class ExplorationMode(Enum):
    """探索模式"""
    QUICK_SURVEY = "quick_survey"           # 快速概览（少量关键组合）
    SYSTEMATIC_GRID = "systematic_grid"     # 系统网格（所有组合）
    FOCUSED_ANALYSIS = "focused_analysis"   # 聚焦分析（特定维度）
    RANDOM_SAMPLING = "random_sampling"     # 随机采样（统计方法）
    ADAPTIVE_SEARCH = "adaptive_search"     # 自适应搜索（基于效果）

class ParameterDimension(Enum):
    """参数维度"""
    PHI_VALUES = "phi_values"
    DELTA_THETA_VALUES = "delta_theta_values"
    F_BASE_VALUES = "f_base_values"
    CHORD_RATIOS = "chord_ratios"
    RHYTHM_STYLES = "rhythm_styles"
    MELODY_PATTERNS = "melody_patterns"
    COMPOSITION_STYLES = "composition_styles"

@dataclass
class ParameterCombination:
    """参数组合"""
    # 基础数学参数
    phi_name: str
    phi_value: float
    delta_theta_name: str
    delta_theta_value: float
    f_base: float
    
    # 音乐结构参数
    chord_set: str
    chord_ratios: List[float]
    rhythm_style: str
    melody_pattern: str
    composition_style: str
    
    # 元数据
    combination_id: str = ""
    complexity_score: float = 0.0
    estimated_novelty: float = 0.0
    generation_timestamp: str = ""

@dataclass
class ExplorationResults:
    """探索结果"""
    exploration_id: str
    mode: ExplorationMode
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # 参数组合
    total_combinations: int = 0
    explored_combinations: List[ParameterCombination] = field(default_factory=list)
    successful_works: List[Dict[str, Any]] = field(default_factory=list)
    failed_combinations: List[Tuple[ParameterCombination, str]] = field(default_factory=list)
    
    # 分析结果
    parameter_effects: Dict[str, Any] = field(default_factory=dict)
    aesthetic_metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    # 统计信息
    success_rate: float = 0.0
    average_generation_time: float = 0.0
    quality_distribution: Dict[str, int] = field(default_factory=dict)

@dataclass
class ExplorationConfig:
    """探索配置"""
    mode: ExplorationMode = ExplorationMode.QUICK_SURVEY
    max_combinations: int = 20
    measures_per_work: int = 4
    timeout_per_work: float = 30.0
    
    # 参数范围限制
    phi_filter: Optional[List[str]] = None
    delta_theta_filter: Optional[List[str]] = None
    f_base_range: Tuple[float, float] = (40.0, 80.0)
    
    # 质量控制
    min_complexity_score: float = 0.1
    max_complexity_score: float = 0.9
    enable_novelty_filtering: bool = True
    novelty_threshold: float = 0.3
    
    # 输出设置
    save_intermediate_results: bool = True
    generate_analysis_reports: bool = True
    export_comparison_charts: bool = False

class ParameterSpaceExplorer:
    """参数空间探索引擎"""
    
    def __init__(self, master_studio):
        """
        初始化参数探索器
        
        Args:
            master_studio: PetersenMasterStudio实例
        """
        self.master_studio = master_studio
        self.config = ExplorationConfig()
        
        # 探索状态
        self.current_exploration: Optional[ExplorationResults] = None
        self.parameter_cache: Dict[str, Any] = {}
        self.similarity_cache: Dict[Tuple[str, str], float] = {}
        
        # 统计数据
        self.exploration_history: List[ExplorationResults] = []
        self.parameter_performance: Dict[str, Dict[str, float]] = {}
        
        print("✓ 参数空间探索引擎已初始化")
    
    def configure_exploration(self, 
                            mode: ExplorationMode = ExplorationMode.QUICK_SURVEY,
                            max_combinations: int = 20,
                            **kwargs) -> ExplorationConfig:
        """
        配置探索参数
        
        Args:
            mode: 探索模式
            max_combinations: 最大组合数
            **kwargs: 其他配置参数
            
        Returns:
            ExplorationConfig: 配置对象
        """
        self.config = ExplorationConfig(
            mode=mode,
            max_combinations=max_combinations,
            **kwargs
        )
        
        print(f"✓ 探索配置已更新: {mode.value}, 最大组合数: {max_combinations}")
        return self.config
    
    def run_exploration(self, config: Optional[ExplorationConfig] = None) -> ExplorationResults:
        """
        运行参数空间探索
        
        Args:
            config: 探索配置（可选）
            
        Returns:
            ExplorationResults: 探索结果
        """
        if config:
            self.config = config
        
        exploration_id = f"exploration_{int(time.time())}"
        
        print(f"🔍 开始参数空间探索: {self.config.mode.value}")
        print(f"   探索ID: {exploration_id}")
        print(f"   最大组合数: {self.config.max_combinations}")
        
        # 初始化探索结果
        self.current_exploration = ExplorationResults(
            exploration_id=exploration_id,
            mode=self.config.mode,
            start_time=datetime.now()
        )
        
        try:
            # 根据模式执行不同的探索策略
            if self.config.mode == ExplorationMode.QUICK_SURVEY:
                combinations = self._generate_quick_survey_combinations()
            elif self.config.mode == ExplorationMode.SYSTEMATIC_GRID:
                combinations = self._generate_systematic_grid_combinations()
            elif self.config.mode == ExplorationMode.FOCUSED_ANALYSIS:
                combinations = self._generate_focused_analysis_combinations()
            elif self.config.mode == ExplorationMode.RANDOM_SAMPLING:
                combinations = self._generate_random_sampling_combinations()
            elif self.config.mode == ExplorationMode.ADAPTIVE_SEARCH:
                combinations = self._generate_adaptive_search_combinations()
            else:
                raise ValueError(f"未知探索模式: {self.config.mode}")
            
            # 执行探索
            self._execute_exploration(combinations)
            
            # 分析结果
            self._analyze_exploration_results()
            
            # 完成探索
            self.current_exploration.end_time = datetime.now()
            self.exploration_history.append(self.current_exploration)
            
            print(f"✓ 参数空间探索完成")
            print(f"   成功作品: {len(self.current_exploration.successful_works)}")
            print(f"   成功率: {self.current_exploration.success_rate:.1%}")
            
            return self.current_exploration
            
        except Exception as e:
            print(f"❌ 参数空间探索失败: {e}")
            if self.current_exploration:
                self.current_exploration.end_time = datetime.now()
            raise
    
    def _generate_quick_survey_combinations(self) -> List[ParameterCombination]:
        """生成快速概览组合"""
        print("📊 生成快速概览参数组合...")
        
        # 选择关键的φ值和δθ值组合
        key_phi_values = ["golden", "octave", "fifth", "fourth"]
        key_delta_theta_values = ["15.0", "24.0", "4.8", "8.0"]
        
        # 应用过滤器
        if self.config.phi_filter:
            key_phi_values = [p for p in key_phi_values if p in self.config.phi_filter]
        if self.config.delta_theta_filter:
            key_delta_theta_values = [d for d in key_delta_theta_values if d in self.config.delta_theta_filter]
        
        combinations = []
        
        # 生成核心组合
        for phi_name in key_phi_values[:3]:  # 限制数量
            for delta_theta_name in key_delta_theta_values[:3]:
                
                combination = ParameterCombination(
                    phi_name=phi_name,
                    phi_value=PRESET_PHI_VALUES[phi_name],
                    delta_theta_name=delta_theta_name,
                    delta_theta_value=PRESET_DELTA_THETA_VALUES[delta_theta_name],
                    f_base=55.0,  # 固定基频
                    chord_set="major_triad",
                    chord_ratios=CHORD_RATIOS_PRESETS["major_triad"],
                    rhythm_style="traditional",
                    melody_pattern="balanced",
                    composition_style="balanced_journey"
                )
                
                combination.combination_id = f"quick_{phi_name}_{delta_theta_name}"
                combination.complexity_score = self._calculate_complexity_score(combination)
                combination.generation_timestamp = datetime.now().isoformat()
                
                combinations.append(combination)
                
                if len(combinations) >= self.config.max_combinations:
                    break
            
            if len(combinations) >= self.config.max_combinations:
                break
        
        print(f"   生成了 {len(combinations)} 个快速概览组合")
        return combinations
    
    def _generate_systematic_grid_combinations(self) -> List[ParameterCombination]:
        """生成系统网格组合"""
        print("🗂️ 生成系统网格参数组合...")
        
        # 获取所有可用参数
        phi_values = list(PRESET_PHI_VALUES.keys())
        delta_theta_values = list(PRESET_DELTA_THETA_VALUES.keys())
        chord_sets = list(CHORD_RATIOS_PRESETS.keys())
        composition_styles = list(COMPOSITION_STYLES.keys())
        
        # 应用过滤器
        if self.config.phi_filter:
            phi_values = [p for p in phi_values if p in self.config.phi_filter]
        if self.config.delta_theta_filter:
            delta_theta_values = [d for d in delta_theta_values if d in self.config.delta_theta_filter]
        
        # 限制组合数量以避免爆炸
        max_per_dimension = int(math.ceil(self.config.max_combinations ** (1/4)))  # 4维度开方
        
        phi_values = phi_values[:max_per_dimension]
        delta_theta_values = delta_theta_values[:max_per_dimension]
        chord_sets = chord_sets[:max_per_dimension]
        composition_styles = composition_styles[:max_per_dimension]
        
        combinations = []
        
        # 生成笛卡尔积
        for phi_name, delta_theta_name, chord_set, comp_style in itertools.product(
            phi_values, delta_theta_values, chord_sets, composition_styles
        ):
            if len(combinations) >= self.config.max_combinations:
                break
            
            combination = ParameterCombination(
                phi_name=phi_name,
                phi_value=PRESET_PHI_VALUES[phi_name],
                delta_theta_name=delta_theta_name,
                delta_theta_value=PRESET_DELTA_THETA_VALUES[delta_theta_name],
                f_base=55.0,
                chord_set=chord_set,
                chord_ratios=CHORD_RATIOS_PRESETS[chord_set],
                rhythm_style="traditional",
                melody_pattern="balanced",
                composition_style=comp_style
            )
            
            combination.combination_id = f"grid_{len(combinations):03d}"
            combination.complexity_score = self._calculate_complexity_score(combination)
            combination.generation_timestamp = datetime.now().isoformat()
            
            # 复杂度过滤
            if (self.config.min_complexity_score <= combination.complexity_score <= 
                self.config.max_complexity_score):
                combinations.append(combination)
        
        print(f"   生成了 {len(combinations)} 个系统网格组合")
        return combinations
    
    def _generate_focused_analysis_combinations(self) -> List[ParameterCombination]:
        """生成聚焦分析组合"""
        print("🎯 生成聚焦分析参数组合...")
        
        combinations = []
        
        # 聚焦于φ值的影响（固定其他参数）
        base_params = {
            "delta_theta_name": "15.0",
            "f_base": 55.0,
            "chord_set": "major_triad",
            "rhythm_style": "traditional",
            "melody_pattern": "balanced",
            "composition_style": "balanced_journey"
        }
        
        # φ值变化分析
        phi_focus_values = ["golden", "octave", "fifth", "fourth", "minor_third"]
        for i, phi_name in enumerate(phi_focus_values[:5]):
            combination = self._create_combination_from_base(
                phi_name=phi_name,
                base_params=base_params,
                combination_id=f"phi_focus_{i+1:02d}"
            )
            combinations.append(combination)
        
        # δθ值变化分析（固定φ为黄金比例）
        delta_theta_focus_values = ["4.8", "8.0", "15.0", "24.0", "72.0"]
        base_params["phi_name"] = "golden"
        
        for i, delta_theta_name in enumerate(delta_theta_focus_values[:5]):
            combination = self._create_combination_from_base(
                delta_theta_name=delta_theta_name,
                base_params=base_params,
                combination_id=f"delta_focus_{i+1:02d}"
            )
            combinations.append(combination)
        
        # 和弦比率变化分析
        chord_focus_sets = ["major_triad", "minor_triad", "major_seventh", "minor_seventh", "complex_jazz"]
        base_params.update({"phi_name": "golden", "delta_theta_name": "15.0"})
        
        for i, chord_set in enumerate(chord_focus_sets[:5]):
            combination = self._create_combination_from_base(
                chord_set=chord_set,
                base_params=base_params,
                combination_id=f"chord_focus_{i+1:02d}"
            )
            combinations.append(combination)
        
        # 限制总数
        combinations = combinations[:self.config.max_combinations]
        
        print(f"   生成了 {len(combinations)} 个聚焦分析组合")
        return combinations
    
    def _generate_random_sampling_combinations(self) -> List[ParameterCombination]:
        """生成随机采样组合"""
        print("🎲 生成随机采样参数组合...")
        
        import random
        
        combinations = []
        
        # 获取所有可用参数
        phi_values = list(PRESET_PHI_VALUES.keys())
        delta_theta_values = list(PRESET_DELTA_THETA_VALUES.keys())
        chord_sets = list(CHORD_RATIOS_PRESETS.keys())
        composition_styles = list(COMPOSITION_STYLES.keys())
        
        # 应用过滤器
        if self.config.phi_filter:
            phi_values = [p for p in phi_values if p in self.config.phi_filter]
        if self.config.delta_theta_filter:
            delta_theta_values = [d for d in delta_theta_values if d in self.config.delta_theta_filter]
        
        # 生成随机组合
        attempts = 0
        max_attempts = self.config.max_combinations * 3
        
        while len(combinations) < self.config.max_combinations and attempts < max_attempts:
            attempts += 1
            
            # 随机选择参数
            phi_name = random.choice(phi_values)
            delta_theta_name = random.choice(delta_theta_values)
            chord_set = random.choice(chord_sets)
            comp_style = random.choice(composition_styles)
            
            # 随机基频（在范围内）
            f_base = random.uniform(self.config.f_base_range[0], self.config.f_base_range[1])
            
            combination = ParameterCombination(
                phi_name=phi_name,
                phi_value=PRESET_PHI_VALUES[phi_name],
                delta_theta_name=delta_theta_name,
                delta_theta_value=PRESET_DELTA_THETA_VALUES[delta_theta_name],
                f_base=f_base,
                chord_set=chord_set,
                chord_ratios=CHORD_RATIOS_PRESETS[chord_set],
                rhythm_style=random.choice(list(RHYTHM_STYLE_PRESETS.keys())),
                melody_pattern=random.choice(list(MELODY_PATTERN_PRESETS.keys())),
                composition_style=comp_style
            )
            
            combination.combination_id = f"random_{len(combinations)+1:03d}"
            combination.complexity_score = self._calculate_complexity_score(combination)
            combination.estimated_novelty = self._estimate_novelty(combination, combinations)
            combination.generation_timestamp = datetime.now().isoformat()
            
            # 复杂度和新颖性过滤
            if (self.config.min_complexity_score <= combination.complexity_score <= 
                self.config.max_complexity_score):
                
                if (not self.config.enable_novelty_filtering or 
                    combination.estimated_novelty >= self.config.novelty_threshold):
                    combinations.append(combination)
        
        print(f"   生成了 {len(combinations)} 个随机采样组合 (尝试 {attempts} 次)")
        return combinations
    
    def _generate_adaptive_search_combinations(self) -> List[ParameterCombination]:
        """生成自适应搜索组合"""
        print("🧠 生成自适应搜索参数组合...")
        
        # 如果没有历史数据，先生成基础组合
        if not self.exploration_history:
            print("   无历史数据，使用快速概览作为起点...")
            return self._generate_quick_survey_combinations()
        
        combinations = []
        
        # 分析历史最佳组合
        best_combinations = self._find_best_historical_combinations()
        
        # 基于最佳组合生成变异
        for base_combo in best_combinations[:5]:  # 取前5个最佳
            # 生成邻近变异
            variations = self._generate_parameter_variations(base_combo)
            combinations.extend(variations[:4])  # 每个基础组合生成4个变异
            
            if len(combinations) >= self.config.max_combinations:
                break
        
        # 如果组合不够，补充随机探索
        if len(combinations) < self.config.max_combinations:
            remaining = self.config.max_combinations - len(combinations)
            random_combos = self._generate_random_sampling_combinations()
            combinations.extend(random_combos[:remaining])
        
        print(f"   生成了 {len(combinations)} 个自适应搜索组合")
        return combinations
    
    def _create_combination_from_base(self, base_params: Dict[str, Any], 
                                    combination_id: str, **overrides) -> ParameterCombination:
        """从基础参数创建组合"""
        params = {**base_params, **overrides}
        
        phi_name = params.get("phi_name", "golden")
        delta_theta_name = params.get("delta_theta_name", "15.0")
        chord_set = params.get("chord_set", "major_triad")
        
        combination = ParameterCombination(
            phi_name=phi_name,
            phi_value=PRESET_PHI_VALUES[phi_name],
            delta_theta_name=delta_theta_name,
            delta_theta_value=PRESET_DELTA_THETA_VALUES[delta_theta_name],
            f_base=params.get("f_base", 55.0),
            chord_set=chord_set,
            chord_ratios=CHORD_RATIOS_PRESETS[chord_set],
            rhythm_style=params.get("rhythm_style", "traditional"),
            melody_pattern=params.get("melody_pattern", "balanced"),
            composition_style=params.get("composition_style", "balanced_journey")
        )
        
        combination.combination_id = combination_id
        combination.complexity_score = self._calculate_complexity_score(combination)
        combination.generation_timestamp = datetime.now().isoformat()
        
        return combination
    
    def _calculate_complexity_score(self, combination: ParameterCombination) -> float:
        """计算参数组合的复杂度得分"""
        score = 0.0
        
        # φ值复杂度（基于数值大小和特殊性）
        phi_complexity = {
            "golden": 0.8,    # 黄金比例，高复杂度
            "octave": 0.3,    # 八度，简单
            "fifth": 0.5,     # 五度，中等
            "fourth": 0.4,    # 四度，较简单
            "major_third": 0.6,
            "minor_third": 0.7,
            "tone": 0.4,
            "semitone": 0.2
        }
        score += phi_complexity.get(combination.phi_name, 0.5) * 0.3
        
        # δθ值复杂度（基于等分数）
        delta_theta_value = combination.delta_theta_value
        if delta_theta_value <= 5.0:
            delta_complexity = 0.9  # 小角度，高复杂度
        elif delta_theta_value <= 15.0:
            delta_complexity = 0.6  # 中等
        elif delta_theta_value <= 30.0:
            delta_complexity = 0.4  # 较简单
        else:
            delta_complexity = 0.2  # 大角度，简单
        score += delta_complexity * 0.3
        
        # 和弦复杂度
        chord_complexity = {
            "major_triad": 0.2,
            "minor_triad": 0.3,
            "diminished": 0.6,
            "augmented": 0.7,
            "major_seventh": 0.5,
            "minor_seventh": 0.6,
            "complex_jazz": 0.9,
            "quartal": 0.8
        }
        score += chord_complexity.get(combination.chord_set, 0.5) * 0.2
        
        # 作曲风格复杂度
        style_complexity = {
            "simple_journey": 0.2,
            "balanced_journey": 0.5,
            "complex_journey": 0.8,
            "virtuoso_journey": 0.9,
            "harmonic_exploration": 0.7,
            "rhythmic_adventure": 0.6
        }
        score += style_complexity.get(combination.composition_style, 0.5) * 0.2
        
        return min(1.0, max(0.0, score))
    
    def _estimate_novelty(self, combination: ParameterCombination, 
                         existing_combinations: List[ParameterCombination]) -> float:
        """估算组合的新颖性"""
        if not existing_combinations:
            return 1.0
        
        # 计算与现有组合的最小距离
        min_distance = float('inf')
        
        for existing in existing_combinations:
            distance = self._calculate_parameter_distance(combination, existing)
            min_distance = min(min_distance, distance)
        
        # 距离越大，新颖性越高
        novelty = min(1.0, min_distance / 2.0)  # 标准化到0-1
        return novelty
    
    def _calculate_parameter_distance(self, combo1: ParameterCombination, 
                                    combo2: ParameterCombination) -> float:
        """计算两个参数组合之间的距离"""
        distance = 0.0
        
        # φ值距离
        phi_diff = abs(combo1.phi_value - combo2.phi_value)
        distance += phi_diff * 0.3
        
        # δθ值距离
        delta_diff = abs(combo1.delta_theta_value - combo2.delta_theta_value)
        distance += (delta_diff / 180.0) * 0.3  # 标准化
        
        # 基频距离
        f_base_diff = abs(combo1.f_base - combo2.f_base)
        distance += (f_base_diff / 40.0) * 0.1  # 标准化
        
        # 离散参数距离
        if combo1.chord_set != combo2.chord_set:
            distance += 0.2
        
        if combo1.composition_style != combo2.composition_style:
            distance += 0.1
        
        return distance
    
    def _execute_exploration(self, combinations: List[ParameterCombination]):
        """执行参数探索"""
        print(f"\n🎼 开始创作 {len(combinations)} 个参数组合的作品...")
        
        self.current_exploration.total_combinations = len(combinations)
        self.current_exploration.explored_combinations = combinations
        
        successful_count = 0
        total_time = 0.0
        
        for i, combination in enumerate(combinations, 1):
            print(f"\n🎵 作品 {i}/{len(combinations)}: {combination.combination_id}")
            print(f"   参数: φ={combination.phi_name}({combination.phi_value:.3f}), "
                  f"δθ={combination.delta_theta_name}({combination.delta_theta_value:.1f}°)")
            
            start_time = time.time()
            
            try:
                # 创建作品
                work_result = self._create_work_from_combination(combination)
                
                if work_result:
                    self.current_exploration.successful_works.append(work_result)
                    successful_count += 1
                    
                    generation_time = time.time() - start_time
                    total_time += generation_time
                    
                    print(f"   ✓ 创作成功，耗时 {generation_time:.1f}秒")
                    
                    # 实时预览（如果启用）
                    if self.master_studio.config.realtime_preview:
                        self._preview_work(work_result)
                
                else:
                    error_msg = "作品创建失败"
                    self.current_exploration.failed_combinations.append((combination, error_msg))
                    print(f"   ❌ {error_msg}")
                
            except Exception as e:
                error_msg = f"创作异常: {str(e)}"
                self.current_exploration.failed_combinations.append((combination, error_msg))
                print(f"   ❌ {error_msg}")
                
                generation_time = time.time() - start_time
                total_time += generation_time
            
            # 中间结果保存
            if (self.config.save_intermediate_results and 
                i % 5 == 0 and successful_count > 0):
                self._save_intermediate_results(i, len(combinations))
        
        # 更新统计信息
        self.current_exploration.success_rate = successful_count / len(combinations)
        self.current_exploration.average_generation_time = total_time / len(combinations) if combinations else 0.0
        
        print(f"\n📊 探索完成统计:")
        print(f"   成功作品: {successful_count}/{len(combinations)} ({self.current_exploration.success_rate:.1%})")
        print(f"   平均耗时: {self.current_exploration.average_generation_time:.1f}秒/作品")
    
    def _create_work_from_combination(self, combination: ParameterCombination) -> Optional[Dict[str, Any]]:
        """从参数组合创建音乐作品"""
        try:
            # 创建基础音阶
            scale = PetersenScale(
                F_base=combination.f_base,
                phi=combination.phi_value,
                delta_theta=combination.delta_theta_value
            )
            
            # 创建和弦扩展
            chord_extender = PetersenChordExtender(
                petersen_scale=scale,
                chord_ratios=combination.chord_ratios
            )
            
            # 创建作曲器
            composition_style = COMPOSITION_STYLES.get(
                combination.composition_style, 
                COMPOSITION_STYLES["balanced_journey"]
            )
            
            composer = PetersenAutoComposer(
                petersen_scale=scale,
                chord_extender=chord_extender,
                composition_style=composition_style,
                bpm=120
            )
            
            # 生成作曲
            composition = composer.compose(measures=self.config.measures_per_work)
            
            # 保存作品
            work_name = f"param_explore_{combination.combination_id}"
            work_result = self.master_studio._save_composition_work(
                composition, work_name, combination.__dict__
            )
            
            # 添加探索特定信息
            work_result.update({
                "combination": combination,
                "parameter_summary": {
                    "phi": f"{combination.phi_name}({combination.phi_value:.3f})",
                    "delta_theta": f"{combination.delta_theta_name}({combination.delta_theta_value:.1f}°)",
                    "chord_set": combination.chord_set,
                    "composition_style": combination.composition_style
                },
                "complexity_score": combination.complexity_score,
                "estimated_novelty": combination.estimated_novelty
            })
            
            return work_result
            
        except Exception as e:
            print(f"   ❌ 作品创建失败: {e}")
            return None
    
    def _preview_work(self, work_result: Dict[str, Any]):
        """预览作品"""
        try:
            print("   🔊 播放预览...")
            
            # 这里可以调用master_studio的预览功能
            combination = work_result["combination"]
            
            # 创建简化的预览版本
            if hasattr(self.master_studio, '_preview_composition_snippet'):
                # 需要从work_result重建composition对象或使用保存的文件
                print("   🎵 预览播放中...")
                time.sleep(1.0)  # 模拟播放时间
                
        except Exception as e:
            print(f"   ⚠️ 预览失败: {e}")
    
    def _analyze_exploration_results(self):
        """分析探索结果"""
        print("\n📈 分析探索结果...")
        
        if not self.current_exploration.successful_works:
            print("   ⚠️ 没有成功作品可供分析")
            return
        
        # 参数效果分析
        self._analyze_parameter_effects()
        
        # 美学指标分析
        self._analyze_aesthetic_metrics()
        
        # 生成建议
        self._generate_recommendations()
        
        print("   ✓ 结果分析完成")
    
    def _analyze_parameter_effects(self):
        """分析参数效果"""
        parameter_effects = {
            "phi_value_analysis": {},
            "delta_theta_analysis": {},
            "chord_set_analysis": {},
            "complexity_distribution": {}
        }
        
        # 按φ值分组分析
        phi_groups = {}
        for work in self.current_exploration.successful_works:
            combination = work["combination"]
            phi_name = combination.phi_name
            
            if phi_name not in phi_groups:
                phi_groups[phi_name] = []
            phi_groups[phi_name].append(work)
        
        for phi_name, works in phi_groups.items():
            parameter_effects["phi_value_analysis"][phi_name] = {
                "count": len(works),
                "average_complexity": sum(w["complexity_score"] for w in works) / len(works),
                "phi_value": works[0]["combination"].phi_value
            }
        
        # 按δθ值分组分析
        delta_groups = {}
        for work in self.current_exploration.successful_works:
            combination = work["combination"]
            delta_name = combination.delta_theta_name
            
            if delta_name not in delta_groups:
                delta_groups[delta_name] = []
            delta_groups[delta_name].append(work)
        
        for delta_name, works in delta_groups.items():
            parameter_effects["delta_theta_analysis"][delta_name] = {
                "count": len(works),
                "average_complexity": sum(w["complexity_score"] for w in works) / len(works),
                "delta_theta_value": works[0]["combination"].delta_theta_value
            }
        
        # 复杂度分布
        complexity_scores = [w["complexity_score"] for w in self.current_exploration.successful_works]
        parameter_effects["complexity_distribution"] = {
            "min": min(complexity_scores),
            "max": max(complexity_scores),
            "average": sum(complexity_scores) / len(complexity_scores),
            "range_counts": {
                "low (0-0.3)": len([s for s in complexity_scores if s <= 0.3]),
                "medium (0.3-0.7)": len([s for s in complexity_scores if 0.3 < s <= 0.7]),
                "high (0.7-1.0)": len([s for s in complexity_scores if s > 0.7])
            }
        }
        
        self.current_exploration.parameter_effects = parameter_effects
    
    def _analyze_aesthetic_metrics(self):
        """分析美学指标"""
        aesthetic_metrics = {
            "harmonic_richness": {},
            "melodic_complexity": {},
            "overall_quality": {}
        }
        
        # 这里可以添加更复杂的美学分析
        # 目前使用基于参数的简化分析
        
        for work in self.current_exploration.successful_works:
            combination = work["combination"]
            
            # 和声丰富度（基于φ值和和弦设置）
            harmonic_score = self._calculate_harmonic_richness(combination)
            
            # 旋律复杂度（基于δθ值和旋律模式）
            melodic_score = self._calculate_melodic_complexity(combination)
            
            # 整体质量（复合指标）
            overall_score = (harmonic_score + melodic_score + combination.complexity_score) / 3
            
            work_id = work["work_name"]
            aesthetic_metrics["harmonic_richness"][work_id] = harmonic_score
            aesthetic_metrics["melodic_complexity"][work_id] = melodic_score
            aesthetic_metrics["overall_quality"][work_id] = overall_score
        
        self.current_exploration.aesthetic_metrics = aesthetic_metrics
    
    def _calculate_harmonic_richness(self, combination: ParameterCombination) -> float:
        """计算和声丰富度"""
        # 基于φ值的和声潜力
        phi_harmony = {
            "golden": 0.9,
            "octave": 0.6,
            "fifth": 0.8,
            "fourth": 0.7,
            "major_third": 0.75,
            "minor_third": 0.7
        }
        
        # 基于和弦设置的丰富度
        chord_richness = {
            "major_triad": 0.5,
            "minor_triad": 0.55,
            "major_seventh": 0.7,
            "minor_seventh": 0.75,
            "complex_jazz": 0.9,
            "quartal": 0.8
        }
        
        phi_score = phi_harmony.get(combination.phi_name, 0.5)
        chord_score = chord_richness.get(combination.chord_set, 0.5)
        
        return (phi_score + chord_score) / 2
    
    def _calculate_melodic_complexity(self, combination: ParameterCombination) -> float:
        """计算旋律复杂度"""
        # 基于δθ值的旋律变化潜力
        if combination.delta_theta_value <= 8.0:
            delta_complexity = 0.8  # 小角度，复杂旋律
        elif combination.delta_theta_value <= 20.0:
            delta_complexity = 0.6  # 中等
        else:
            delta_complexity = 0.4  # 大角度，简单旋律
        
        # 基于旋律模式
        pattern_complexity = {
            "simple": 0.3,
            "balanced": 0.6,
            "complex": 0.8,
            "experimental": 0.9
        }
        
        pattern_score = pattern_complexity.get(combination.melody_pattern, 0.5)
        
        return (delta_complexity + pattern_score) / 2
    
    def _generate_recommendations(self):
        """生成建议"""
        recommendations = []
        
        # 基于参数效果分析的建议
        phi_analysis = self.current_exploration.parameter_effects.get("phi_value_analysis", {})
        
        if phi_analysis:
            # 找出最佳φ值
            best_phi = max(phi_analysis.items(), 
                          key=lambda x: x[1]["average_complexity"])
            recommendations.append(
                f"推荐使用φ值: {best_phi[0]} (平均复杂度: {best_phi[1]['average_complexity']:.2f})"
            )
        
        # 基于复杂度分布的建议
        complexity_dist = self.current_exploration.parameter_effects.get("complexity_distribution", {})
        
        if complexity_dist:
            if complexity_dist["range_counts"]["high (0.7-1.0)"] > 0:
                recommendations.append("发现高复杂度组合，适合高级音乐创作")
            
            if complexity_dist["range_counts"]["low (0-0.3)"] > complexity_dist["range_counts"]["high (0.7-1.0)"]:
                recommendations.append("建议尝试更复杂的参数组合以增加表现力")
        
        # 基于成功率的建议
        if self.current_exploration.success_rate < 0.8:
            recommendations.append("部分参数组合失败，建议检查参数范围设置")
        elif self.current_exploration.success_rate > 0.95:
            recommendations.append("所有组合都成功，可以尝试更具挑战性的参数范围")
        
        # 通用建议
        recommendations.extend([
            "黄金比例φ=1.618通常产生最和谐的效果",
            "较小的δθ值(< 15°)提供更丰富的旋律变化",
            "复合和弦(七和弦、爵士和弦)增加和声深度",
            "建议结合不同复杂度的参数以获得平衡的表现"
        ])
        
        self.current_exploration.recommendations = recommendations
    
    def _find_best_historical_combinations(self) -> List[ParameterCombination]:
        """查找历史最佳组合"""
        best_combinations = []
        
        for exploration in self.exploration_history:
            for work in exploration.successful_works:
                if "combination" in work:
                    best_combinations.append(work["combination"])
        
        # 按复杂度和美学指标排序
        best_combinations.sort(
            key=lambda x: x.complexity_score + x.estimated_novelty,
            reverse=True
        )
        
        return best_combinations[:10]  # 返回前10个
    
    def _generate_parameter_variations(self, base_combination: ParameterCombination) -> List[ParameterCombination]:
        """生成参数变异"""
        variations = []
        
        # φ值变异
        phi_variants = ["golden", "octave", "fifth", "fourth"]
        for phi_name in phi_variants:
            if phi_name != base_combination.phi_name:
                variation = ParameterCombination(
                    phi_name=phi_name,
                    phi_value=PRESET_PHI_VALUES[phi_name],
                    delta_theta_name=base_combination.delta_theta_name,
                    delta_theta_value=base_combination.delta_theta_value,
                    f_base=base_combination.f_base,
                    chord_set=base_combination.chord_set,
                    chord_ratios=base_combination.chord_ratios,
                    rhythm_style=base_combination.rhythm_style,
                    melody_pattern=base_combination.melody_pattern,
                    composition_style=base_combination.composition_style
                )
                variation.combination_id = f"var_phi_{phi_name}_{len(variations)+1}"
                variation.complexity_score = self._calculate_complexity_score(variation)
                variations.append(variation)
        
        return variations[:4]  # 限制变异数量
    
    def _save_intermediate_results(self, current_index: int, total_count: int):
        """保存中间结果"""
        try:
            intermediate_path = (self.master_studio.config.output_directory / 
                               f"exploration_intermediate_{self.current_exploration.exploration_id}.json")
            
            intermediate_data = {
                "exploration_id": self.current_exploration.exploration_id,
                "progress": f"{current_index}/{total_count}",
                "success_count": len(self.current_exploration.successful_works),
                "failed_count": len(self.current_exploration.failed_combinations),
                "timestamp": datetime.now().isoformat()
            }
            
            with open(intermediate_path, 'w', encoding='utf-8') as f:
                json.dump(intermediate_data, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 中间结果已保存: {intermediate_path.name}")
            
        except Exception as e:
            print(f"   ⚠️ 中间结果保存失败: {e}")
    
    def export_exploration_report(self, exploration_results: Optional[ExplorationResults] = None) -> Path:
        """导出探索报告"""
        if not exploration_results:
            exploration_results = self.current_exploration
        
        if not exploration_results:
            raise ValueError("没有可导出的探索结果")
        
        report_path = (self.master_studio.config.output_directory / 
                      f"exploration_report_{exploration_results.exploration_id}.json")
        
        try:
            # 准备报告数据
            report_data = {
                "exploration_info": {
                    "id": exploration_results.exploration_id,
                    "mode": exploration_results.mode.value,
                    "start_time": exploration_results.start_time.isoformat(),
                    "end_time": exploration_results.end_time.isoformat() if exploration_results.end_time else None,
                    "duration_minutes": ((exploration_results.end_time - exploration_results.start_time).total_seconds() / 60) if exploration_results.end_time else None
                },
                "statistics": {
                    "total_combinations": exploration_results.total_combinations,
                    "successful_works": len(exploration_results.successful_works),
                    "failed_combinations": len(exploration_results.failed_combinations),
                    "success_rate": exploration_results.success_rate,
                    "average_generation_time": exploration_results.average_generation_time
                },
                "parameter_effects": exploration_results.parameter_effects,
                "aesthetic_metrics": exploration_results.aesthetic_metrics,
                "recommendations": exploration_results.recommendations,
                "successful_works_summary": [
                    {
                        "work_name": work["work_name"],
                        "parameters": work["parameter_summary"],
                        "complexity_score": work["complexity_score"],
                        "files": work["files"]
                    }
                    for work in exploration_results.successful_works
                ]
            }
            
            # 保存报告
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"📋 探索报告已导出: {report_path}")
            return report_path
            
        except Exception as e:
            print(f"❌ 探索报告导出失败: {e}")
            raise
    
    def get_exploration_summary(self) -> Dict[str, Any]:
        """获取探索摘要"""
        if not self.current_exploration:
            return {"status": "no_exploration"}
        
        return {
            "exploration_id": self.current_exploration.exploration_id,
            "mode": self.current_exploration.mode.value,
            "status": "completed" if self.current_exploration.end_time else "running",
            "progress": {
                "successful_works": len(self.current_exploration.successful_works),
                "total_combinations": self.current_exploration.total_combinations,
                "success_rate": self.current_exploration.success_rate
            },
            "best_works": [
                work["work_name"] for work in 
                sorted(self.current_exploration.successful_works, 
                      key=lambda x: x["complexity_score"], reverse=True)[:3]
            ],
            "top_recommendations": self.current_exploration.recommendations[:3]
        }

# ========== 便利函数 ==========

def create_parameter_explorer(master_studio) -> ParameterSpaceExplorer:
    """
    创建参数空间探索器
    
    Args:
        master_studio: PetersenMasterStudio实例
        
    Returns:
        ParameterSpaceExplorer: 配置好的探索器
    """
    return ParameterSpaceExplorer(master_studio)

def run_quick_parameter_survey(master_studio, max_combinations: int = 12) -> ExplorationResults:
    """
    便利函数：运行快速参数概览
    
    Args:
        master_studio: PetersenMasterStudio实例
        max_combinations: 最大组合数
        
    Returns:
        ExplorationResults: 探索结果
    """
    explorer = create_parameter_explorer(master_studio)
    
    config = explorer.configure_exploration(
        mode=ExplorationMode.QUICK_SURVEY,
        max_combinations=max_combinations,
        measures_per_work=4
    )
    
    return explorer.run_exploration(config)

if __name__ == "__main__":
    print("🔍 Petersen参数空间探索引擎")
    print("这是一个支持模块，请通过PetersenMasterStudio使用")