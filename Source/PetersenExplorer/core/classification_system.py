"""
Petersen音律开放性分类系统
基于多维度评估结果进行灵活的音律分类和应用推荐
"""
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

# 添加父级路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from .evaluation_framework import ComprehensiveEvaluation, EvaluationDimension

class PrimaryCategory(Enum):
    """主要类别：表示音律系统的主分类，并提供简要语义说明与典型应用指引。
    
    每个枚举值的 .value 保持为短标识符字符串，使用 .description 属性可以获取更完整的中文说明。
    """
    TRADITIONAL_EXTENSION = "traditional_extension"         # 传统扩展型：在十二平均律或历史音律基础上进行扩展，兼容性强，适合古典和当代传统化编制
    MICROTONAL_EXPLORATION = "microtonal_exploration"       # 微分音探索型：强调微分音与细分音程，适合现代古典、实验室研究与精细调音的创作
    EXPERIMENTAL_AVANT_GARDE = "experimental_avant_garde"   # 实验前卫型：追求声音创新和非常规结构，常用于声音艺术与先锋音乐装置
    WORLD_MUSIC_FUSION = "world_music_fusion"               # 世界音乐融合型：融合多文化音阶与节奏，适合跨文化合作与民族音乐改编
    SOUND_ART_DESIGN = "sound_art_design"                   # 声音艺术型：面向装置、空间与多媒体互动，重视音响质感与创新表达
    THERAPEUTIC_FUNCTIONAL = "therapeutic_functional"       # 治疗功能型：注重听觉舒缓、频率与节律对情绪/生理的影响，适用于音乐治疗与冥想
    COMPREHENSIVE_HYBRID = "comprehensive_hybrid"           # 综合混合型：多维度平衡，无单一突出特征，适合需要通用性与多场景适配的项目
    RESEARCH_EXPLORATION = "research_exploration"           # 研究探索型：以理论验证与学术探索为主，可能尚未成熟以投入生产环境
    CHAMBER_MUSIC = "chamber_music"                         # 室内乐/小型合奏：适用于小编制演出，强调声部平衡与现场可演性
    FUSION_PROJECTS = "fusion_projects"                     # 跨界/融合项目：强调不同风格或文化的混合创新，适合项目式合作与试验性演出

    @property
    def description(self) -> str:
        """返回该类别的详细中文说明，包含典型特征与适用场景（用于展示或报告）。"""
        descriptions = {
            PrimaryCategory.TRADITIONAL_EXTENSION: (
                "在传统音律框架上做适度扩展，保留演奏者与受众的可接受性。"
                "典型特征：高传统兼容、可用于古典与室内乐场景。"
            ),
            PrimaryCategory.MICROTONAL_EXPLORATION: (
                "侧重微分音与精细音高处理，适合追求新音响语汇的作曲与研究。"
                "典型特征：高微分音潜力、需要精确调音工具。"
            ),
            PrimaryCategory.EXPERIMENTAL_AVANT_GARDE: (
                "强调前卫实验与非常规声响结构，适用于声音艺术与装置。"
                "典型特征：高创新性、低传统可演性。"
            ),
            PrimaryCategory.WORLD_MUSIC_FUSION: (
                "融合多民族音阶与演奏实践，适合文化交流与跨界合作。"
                "典型特征：文化兼容性强、节奏与音阶多样。"
            ),
            PrimaryCategory.SOUND_ART_DESIGN: (
                "面向空间与多媒体交互的声音设计，注重质感与体验感。"
                "典型特征：偏实验、适合装置与多通道呈现。"
            ),
            PrimaryCategory.THERAPEUTIC_FUNCTIONAL: (
                "以促进身心健康为目标，强调可控的频率与节律效果。"
                "典型特征：适用于音乐治疗、冥想与健康应用。"
            ),
            PrimaryCategory.COMPREHENSIVE_HYBRID: (
                "多维度均衡的混合型，既有可用性也具一定创新性，适用范围广。"
            ),
            PrimaryCategory.RESEARCH_EXPLORATION: (
                "以验证新理论和探索性研究为主，成果倾向于学术发表与原型开发。"
            ),
            PrimaryCategory.CHAMBER_MUSIC: (
                "适用于小编制演出，关注声部之间的和谐与可演性。"
            ),
            PrimaryCategory.FUSION_PROJECTS: (
                "强调风格或文化之间的融合创新，常见于跨界演出和试验性合作。"
            ),
        }
        return descriptions.get(self, "")

class SecondaryTrait(Enum):
    """次要特征"""
    HIGH_HARMONIC_COMPLEXITY = "high_harmonic"          # 高和声复杂度
    MELODIC_FLUIDITY = "melodic_fluid"                  # 旋律流畅性
    DENSE_SCALE = "dense_scale"                         # 密集音阶
    SPARSE_SCALE = "sparse_scale"                       # 稀疏音阶
    WIDE_INTERVALS = "wide_intervals"                   # 宽音程
    MICRO_INTERVALS = "micro_intervals"                 # 微分音
    CONSONANT_BIAS = "consonant_bias"                   # 协和倾向
    DISSONANT_TENSION = "dissonant_tension"             # 不协和张力
    FREQUENCY_BALANCE = "frequency_balance"             # 频率平衡
    INNOVATIVE_STRUCTURE = "innovative_structure"        # 创新结构

@dataclass
class ApplicationDomain:
    """应用领域"""
    name: str
    description: str
    suitability_score: float  # 0-1
    specific_uses: List[str]
    technical_requirements: List[str]
    target_audience: List[str]

@dataclass
class ClassificationResult:
    """分类结果"""
    primary_category: PrimaryCategory
    secondary_traits: List[SecondaryTrait]
    confidence_score: float  # 分类置信度
    
    # 应用推荐
    recommended_domains: List[ApplicationDomain]
    priority_applications: List[str]
    
    # 发展建议
    strengths_to_leverage: List[str]
    areas_for_improvement: List[str]
    complementary_systems: List[str]
    
    # 实用性评估
    immediate_usability: str     # "high", "medium", "low", "research"
    learning_curve: str          # "easy", "moderate", "challenging", "expert"
    production_readiness: str    # "ready", "needs_development", "experimental"

class OpenClassificationSystem:
    """开放性分类系统"""
    
    def __init__(self):
        # 分类阈值配置
        self.category_thresholds = {
            PrimaryCategory.TRADITIONAL_EXTENSION: {
                EvaluationDimension.TRADITIONAL_COMPATIBILITY: 0.7,
                EvaluationDimension.TECHNICAL_FEASIBILITY: 0.6
            },
            PrimaryCategory.MICROTONAL_EXPLORATION: {
                EvaluationDimension.MICROTONAL_POTENTIAL: 0.7,
                EvaluationDimension.EXPERIMENTAL_INNOVATION: 0.5
            },
            PrimaryCategory.EXPERIMENTAL_AVANT_GARDE: {
                EvaluationDimension.EXPERIMENTAL_INNOVATION: 0.8,
                EvaluationDimension.TRADITIONAL_COMPATIBILITY: 0.3  # 低传统性
            },
            PrimaryCategory.WORLD_MUSIC_FUSION: {
                EvaluationDimension.WORLD_MUSIC_AFFINITY: 0.6,
                EvaluationDimension.TRADITIONAL_COMPATIBILITY: 0.4
            },
            PrimaryCategory.THERAPEUTIC_FUNCTIONAL: {
                EvaluationDimension.THERAPEUTIC_VALUE: 0.7,
                EvaluationDimension.HARMONIC_RICHNESS: 0.5
            },
            PrimaryCategory.SOUND_ART_DESIGN: {
                EvaluationDimension.EXPERIMENTAL_INNOVATION: 0.6,
                EvaluationDimension.TRADITIONAL_COMPATIBILITY: 0.2  # 非传统
            }
        }
        
        # 应用领域定义
        self.application_domains = self._initialize_application_domains()
    
    def classify_system(self, evaluation_result: ComprehensiveEvaluation) -> ClassificationResult:
        """对系统进行分类"""
        try:
            # 获取评估维度分数
            dimension_scores = evaluation_result.dimension_scores
            
            # 计算分类得分
            traditional_score = self._get_dimension_score(dimension_scores, 'traditional_compatibility')
            microtonal_score = self._get_dimension_score(dimension_scores, 'microtonal_potential')
            experimental_score = self._get_dimension_score(dimension_scores, 'experimental_innovation')
            therapeutic_score = self._get_dimension_score(dimension_scores, 'therapeutic_value')
            
            # 确定主要类别 - 返回枚举对象而非字符串
            if traditional_score >= 0.7:
                primary_category = PrimaryCategory.TRADITIONAL_EXTENSION
                confidence = 0.8
            elif microtonal_score >= 0.7:
                primary_category = PrimaryCategory.MICROTONAL_EXPLORATION
                confidence = 0.85
            elif experimental_score >= 0.7:
                primary_category = PrimaryCategory.EXPERIMENTAL_AVANT_GARDE
                confidence = 0.8
            elif therapeutic_score >= 0.7:
                primary_category = PrimaryCategory.THERAPEUTIC_FUNCTIONAL
                confidence = 0.75
            else:
                primary_category = PrimaryCategory.RESEARCH_EXPLORATION
                confidence = 0.6
            
            return ClassificationResult(
                primary_category=primary_category,  # 确保这是枚举对象
                confidence_score=confidence,
                secondary_categories=[],
                classification_reasoning=f"基于评估分数的自动分类",
                application_domains=[],
                target_audiences=[],
                performance_contexts=[],
                technical_requirements=[],
                creative_potential_assessment={},
                usage_recommendations=[]
            )
            
        except Exception as e:
            print(f"分类过程出错: {e}")
            # 返回默认分类
            return ClassificationResult(
                primary_category=PrimaryCategory.RESEARCH_EXPLORATION,
                confidence_score=0.3,
                secondary_categories=[],
                classification_reasoning=f"分类失败，使用默认分类: {e}",
                application_domains=[],
                target_audiences=[],
                performance_contexts=[],
                technical_requirements=[],
                creative_potential_assessment={},
                usage_recommendations=[]
            )
    
    def _get_dimension_score(self, dimension_scores: Dict, dimension_name: str) -> float:
        """安全获取维度分数"""
        if dimension_name in dimension_scores:
            score_obj = dimension_scores[dimension_name]
            if hasattr(score_obj, 'score'):
                return score_obj.score
            elif isinstance(score_obj, (int, float)):
                return float(score_obj)
        return 0.5  # 默认分数

    def _determine_primary_category(self, evaluation: ComprehensiveEvaluation) -> Tuple[PrimaryCategory, float]:
        """确定主要类别"""
        scores = evaluation.dimension_scores
        category_scores = {}
        
        # 计算每个类别的匹配度
        for category, thresholds in self.category_thresholds.items():
            match_score = 1.0
            requirement_count = len(thresholds)
            
            for dimension, threshold in thresholds.items():
                actual_score = scores[dimension].score
                if actual_score >= threshold:
                    match_score *= 1.0  # 满足要求
                else:
                    # 部分满足，按比例计算
                    partial_match = actual_score / threshold
                    match_score *= partial_match
            
            category_scores[category] = match_score
        
        # 特殊类别判断
        
        # 综合混合型：多个维度都不错但没有突出优势
        if evaluation.weighted_total_score >= 0.6:
            high_scores = sum(1 for score in scores.values() if score.score >= 0.6)
            if high_scores >= 4:  # 多个维度表现良好
                category_scores[PrimaryCategory.COMPREHENSIVE_HYBRID] = 0.8
        
        # 声音艺术型：高创新性但低传统性和实用性
        innovation_score = scores[EvaluationDimension.EXPERIMENTAL_INNOVATION].score
        traditional_score = scores[EvaluationDimension.TRADITIONAL_COMPATIBILITY].score
        if innovation_score >= 0.7 and traditional_score <= 0.3:
            category_scores[PrimaryCategory.SOUND_ART_DESIGN] = 0.9
        
        # 研究探索型：作为默认类别
        if not category_scores or max(category_scores.values()) < 0.4:
            category_scores[PrimaryCategory.RESEARCH_EXPLORATION] = 0.5
        
        # 选择最高得分的类别
        best_category = max(category_scores.items(), key=lambda x: x[1])
        return best_category[0], best_category[1]
    
    def _identify_secondary_traits(self, evaluation: ComprehensiveEvaluation) -> List[SecondaryTrait]:
        """识别次要特征"""
        traits = []
        scores = evaluation.dimension_scores
        
        # 和声复杂度
        if scores[EvaluationDimension.HARMONIC_RICHNESS].score >= 0.8:
            traits.append(SecondaryTrait.HIGH_HARMONIC_COMPLEXITY)
        
        # 旋律流畅性
        if scores[EvaluationDimension.MELODIC_EXPRESSIVENESS].score >= 0.8:
            traits.append(SecondaryTrait.MELODIC_FLUIDITY)
        
        # 微分音特征
        if scores[EvaluationDimension.MICROTONAL_POTENTIAL].score >= 0.7:
            traits.append(SecondaryTrait.MICRO_INTERVALS)
        
        # 协和倾向
        harmonic_details = scores[EvaluationDimension.HARMONIC_RICHNESS].details
        if harmonic_details and harmonic_details.get('consonant_ratio', 0) >= 0.7:
            traits.append(SecondaryTrait.CONSONANT_BIAS)
        elif harmonic_details and harmonic_details.get('consonant_ratio', 0) <= 0.3:
            traits.append(SecondaryTrait.DISSONANT_TENSION)
        
        # 创新结构
        if scores[EvaluationDimension.EXPERIMENTAL_INNOVATION].score >= 0.8:
            traits.append(SecondaryTrait.INNOVATIVE_STRUCTURE)
        
        # 根据评估细节判断音阶密度（这里需要从evaluation中获取更多信息）
        # 这部分可能需要在实际实现时根据具体的evaluation结构调整
        
        return traits
    
    def _recommend_application_domains(self, evaluation: ComprehensiveEvaluation, 
                                     primary_category: PrimaryCategory) -> List[ApplicationDomain]:
        """推荐应用领域"""
        recommended = []
        scores = evaluation.dimension_scores
        
        # 根据主要类别推荐相应领域
        if primary_category == PrimaryCategory.TRADITIONAL_EXTENSION:
            recommended.extend([
                self.application_domains['classical_music'],
                self.application_domains['chamber_music'],
                self.application_domains['educational_tools']
            ])
        
        elif primary_category == PrimaryCategory.MICROTONAL_EXPLORATION:
            recommended.extend([
                self.application_domains['contemporary_classical'],
                self.application_domains['electronic_music'],
                self.application_domains['computer_music']
            ])
        
        elif primary_category == PrimaryCategory.EXPERIMENTAL_AVANT_GARDE:
            recommended.extend([
                self.application_domains['sound_art'],
                self.application_domains['experimental_music'],
                self.application_domains['research_projects']
            ])
        
        elif primary_category == PrimaryCategory.WORLD_MUSIC_FUSION:
            recommended.extend([
                self.application_domains['world_music'],
                self.application_domains['fusion_projects'],
                self.application_domains['cultural_exchange']
            ])
        
        elif primary_category == PrimaryCategory.THERAPEUTIC_FUNCTIONAL:
            recommended.extend([
                self.application_domains['music_therapy'],
                self.application_domains['meditation_music'],
                self.application_domains['wellness_applications']
            ])
        
        elif primary_category == PrimaryCategory.SOUND_ART_DESIGN:
            recommended.extend([
                self.application_domains['sound_design'],
                self.application_domains['installation_art'],
                self.application_domains['multimedia_projects']
            ])
        
        # 根据具体得分调整推荐度
        for domain in recommended:
            domain.suitability_score = self._calculate_domain_suitability(domain, evaluation)
        
        # 按适用性排序
        recommended.sort(key=lambda x: x.suitability_score, reverse=True)
        
        return recommended[:5]  # 返回前5个最适合的领域
    
    def _initialize_application_domains(self) -> Dict[str, ApplicationDomain]:
        """初始化应用领域定义"""
        return {
            'classical_music': ApplicationDomain(
                name="古典音乐",
                description="传统古典音乐创作和演奏",
                suitability_score=0.0,  # 将在运行时计算
                specific_uses=["室内乐编曲", "管弦乐作品", "独奏曲目"],
                technical_requirements=["传统乐器适配", "音律转换工具", "记谱软件支持"],
                target_audience=["古典音乐家", "作曲家", "音乐学者"]
            ),
            
            'contemporary_classical': ApplicationDomain(
                name="现代古典音乐",
                description="当代古典音乐和微分音作品",
                suitability_score=0.0,
                specific_uses=["微分音作品", "实验性室内乐", "新音响探索"],
                technical_requirements=["微分音乐器", "特殊记谱法", "精确调音设备"],
                target_audience=["现代作曲家", "新音乐演奏家", "音乐研究者"]
            ),
            
            'electronic_music': ApplicationDomain(
                name="电子音乐",
                description="电子音乐制作和声音设计",
                suitability_score=0.0,
                specific_uses=["合成器编程", "采样设计", "音序制作"],
                technical_requirements=["DAW软件", "合成器", "MIDI控制器"],
                target_audience=["电子音乐制作人", "声音设计师", "DJ"]
            ),
            
            'music_therapy': ApplicationDomain(
                name="音乐治疗",
                description="治疗性音乐应用和健康促进",
                suitability_score=0.0,
                specific_uses=["冥想音乐", "放松治疗", "情绪调节"],
                technical_requirements=["治疗环境", "播放设备", "个性化调整"],
                target_audience=["音乐治疗师", "健康从业者", "个人用户"]
            ),
            
            'world_music': ApplicationDomain(
                name="世界音乐",
                description="跨文化音乐融合和民族音乐",
                suitability_score=0.0,
                specific_uses=["文化融合项目", "民族音乐研究", "国际合作"],
                technical_requirements=["多文化乐器", "录音设备", "文化研究"],
                target_audience=["世界音乐家", "民族音乐学者", "文化工作者"]
            ),
            
            'sound_art': ApplicationDomain(
                name="声音艺术",
                description="声音装置和实验性音响艺术",
                suitability_score=0.0,
                specific_uses=["声音装置", "环境音响", "互动艺术"],
                technical_requirements=["空间音响系统", "传感器技术", "编程能力"],
                target_audience=["声音艺术家", "装置艺术家", "新媒体艺术家"]
            ),
            
            'research_projects': ApplicationDomain(
                name="研究项目",
                description="音乐理论研究和学术项目",
                suitability_score=0.0,
                specific_uses=["理论验证", "教学演示", "学术发表"],
                technical_requirements=["研究设备", "数据分析软件", "文献资源"],
                target_audience=["音乐学者", "研究生", "理论家"]
            ),
            
            'educational_tools': ApplicationDomain(
                name="教育工具",
                description="音乐教育和听力训练",
                suitability_score=0.0,
                specific_uses=["听力训练", "音律教学", "理论演示"],
                technical_requirements=["教学软件", "播放设备", "互动界面"],
                target_audience=["音乐教师", "学生", "自学者"]
            )
        }
    
    def _calculate_domain_suitability(self, domain: ApplicationDomain, 
                                    evaluation: ComprehensiveEvaluation) -> float:
        """计算领域适用性得分"""
        scores = evaluation.dimension_scores
        
        # 简化的适用性计算，实际应用中可以更复杂
        if domain.name == "古典音乐":
            return scores[EvaluationDimension.TRADITIONAL_COMPATIBILITY].score * 0.8 + \
                   scores[EvaluationDimension.HARMONIC_RICHNESS].score * 0.2
        
        elif domain.name == "现代古典音乐":
            return scores[EvaluationDimension.MICROTONAL_POTENTIAL].score * 0.6 + \
                   scores[EvaluationDimension.EXPERIMENTAL_INNOVATION].score * 0.4
        
        elif domain.name == "音乐治疗":
            return scores[EvaluationDimension.THERAPEUTIC_VALUE].score
        
        elif domain.name == "声音艺术":
            return scores[EvaluationDimension.EXPERIMENTAL_INNOVATION].score * 0.7 + \
                   (1.0 - scores[EvaluationDimension.TRADITIONAL_COMPATIBILITY].score) * 0.3
        
        # 默认计算
        return evaluation.weighted_total_score
    
    def _generate_priority_applications(self, evaluation: ComprehensiveEvaluation, 
                                      primary_category: PrimaryCategory) -> List[str]:
        """生成优先应用建议"""
        # 这里返回具体的应用建议
        return evaluation.application_suggestions
    
    def _identify_strengths_to_leverage(self, evaluation: ComprehensiveEvaluation) -> List[str]:
        """识别可利用的优势"""
        return evaluation.strengths
    
    def _identify_improvement_areas(self, evaluation: ComprehensiveEvaluation) -> List[str]:
        """识别改进领域"""
        return evaluation.limitations
    
    def _suggest_complementary_systems(self, evaluation: ComprehensiveEvaluation, 
                                     primary_category: PrimaryCategory) -> List[str]:
        """建议互补系统"""
        complementary = []
        
        scores = evaluation.dimension_scores
        
        # 根据弱点建议互补系统
        if scores[EvaluationDimension.TRADITIONAL_COMPATIBILITY].score < 0.3:
            complementary.append("12平均律系统 - 提供传统和声支持")
        
        if scores[EvaluationDimension.HARMONIC_RICHNESS].score < 0.4:
            complementary.append("纯律系统 - 增强和声协和度")
        
        if scores[EvaluationDimension.MICROTONAL_POTENTIAL].score < 0.3:
            complementary.append("四分音系统 - 补充微分音表达")
        
        # 根据类别建议相关系统
        if primary_category == PrimaryCategory.TRADITIONAL_EXTENSION:
            complementary.append("中古调式 - 提供历史音响参考")
        
        elif primary_category == PrimaryCategory.WORLD_MUSIC_FUSION:
            complementary.append("各民族音阶 - 扩展文化表达范围")
        
        return complementary
    
    def _assess_practical_usability(self, evaluation: ComprehensiveEvaluation) -> Dict[str, str]:
        """评估实用性"""
        scores = evaluation.dimension_scores
        
        feasibility = scores[EvaluationDimension.TECHNICAL_FEASIBILITY].score
        total_score = evaluation.weighted_total_score
        
        # 即时可用性
        if total_score >= 0.7 and feasibility >= 0.8:
            usability = "high"
        elif total_score >= 0.5 and feasibility >= 0.6:
            usability = "medium"
        elif feasibility >= 0.5:
            usability = "low"
        else:
            usability = "research"
        
        # 学习曲线
        traditional = scores[EvaluationDimension.TRADITIONAL_COMPATIBILITY].score
        if traditional >= 0.7:
            learning_curve = "easy"
        elif traditional >= 0.4:
            learning_curve = "moderate"
        elif feasibility >= 0.6:
            learning_curve = "challenging"
        else:
            learning_curve = "expert"
        
        # 生产就绪性
        if usability == "high" and learning_curve in ["easy", "moderate"]:
            production_readiness = "ready"
        elif usability in ["medium", "low"]:
            production_readiness = "needs_development"
        else:
            production_readiness = "experimental"
        
        return {
            'usability': usability,
            'learning_curve': learning_curve,
            'production_readiness': production_readiness
        }

def format_classification_result(result: ClassificationResult) -> str:
    """格式化分类结果为可读字符串"""
    output = []
    
    output.append(f"🎵 主要类别: {result.primary_category.value}")
    output.append(f"📊 分类置信度: {result.confidence_score:.1%}")
    
    if result.secondary_traits:
        traits_str = ", ".join([trait.value for trait in result.secondary_traits])
        output.append(f"🏷️  次要特征: {traits_str}")
    
    output.append(f"🚀 即时可用性: {result.immediate_usability}")
    output.append(f"📈 学习曲线: {result.learning_curve}")
    output.append(f"🏭 生产就绪: {result.production_readiness}")
    
    if result.priority_applications:
        apps_str = ", ".join(result.priority_applications[:3])
        output.append(f"💡 优先应用: {apps_str}")
    
    return "\n".join(output)

# 工具函数
def create_classification_report(result: ClassificationResult) -> Dict[str, Any]:
    """创建详细的分类报告"""
    return {
        'classification': {
            'primary_category': result.primary_category.value,
            'secondary_traits': [trait.value for trait in result.secondary_traits],
            'confidence_score': result.confidence_score
        },
        'applications': {
            'recommended_domains': [
                {
                    'name': domain.name,
                    'suitability': domain.suitability_score,
                    'uses': domain.specific_uses
                } for domain in result.recommended_domains
            ],
            'priority_applications': result.priority_applications
        },
        'assessment': {
            'immediate_usability': result.immediate_usability,
            'learning_curve': result.learning_curve,
            'production_readiness': result.production_readiness
        },
        'recommendations': {
            'strengths_to_leverage': result.strengths_to_leverage,
            'areas_for_improvement': result.areas_for_improvement,
            'complementary_systems': result.complementary_systems
        }
    }