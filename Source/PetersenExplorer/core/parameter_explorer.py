"""
Petersen音律参数空间探索引擎
负责系统性遍历所有φ和δθ预设组合，生成完整的参数探索矩阵
"""
from typing import List, Dict, Tuple, Optional, Iterator
from dataclasses import dataclass
import itertools
import sys
from pathlib import Path

# 添加父级路径以导入PetersenScale_Phi
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS

@dataclass
class ExplorationParameters:
    """探索参数配置"""
    phi_name: str
    phi_value: float
    delta_theta_name: str 
    delta_theta_value: float
    f_base: float
    f_min: float = 110.0
    f_max: float = 880.0
    
    def __str__(self):
        return f"φ={self.phi_name}({self.phi_value:.6f}), δθ={self.delta_theta_name}({self.delta_theta_value}°), F_base={self.f_base}Hz"

@dataclass 
class ExplorationResult:
    """单个参数组合的探索结果"""
    parameters: ExplorationParameters
    scale: Optional[PetersenScale_Phi]
    entries: List
    success: bool
    error_message: Optional[str] = None
    basic_metrics: Optional[Dict] = None

class ParameterSpaceExplorer:
    """参数空间探索器"""
    
    def __init__(self, 
                 f_base_candidates: List[float] = None,
                 f_min: float = 110.0,
                 f_max: float = 880.0):
        """
        初始化探索器
        
        Args:
            f_base_candidates: F_base候选值列表
            f_min: 最小频率限制
            f_max: 最大频率限制
        """
        self.f_base_candidates = f_base_candidates or [
            110.0,   # A2
            146.83,  # D3
            220.0,   # A3  
            261.63,  # C4 (中央C)
            293.66,  # D4
        ]
        self.f_min = f_min
        self.f_max = f_max
        
        # 统计信息
        self.total_combinations = (
            len(PHI_PRESETS) * 
            len(DELTA_THETA_PRESETS) * 
            len(self.f_base_candidates)
        )
        
        self.exploration_results: List[ExplorationResult] = []
        
    def get_exploration_matrix(self) -> Iterator[ExplorationParameters]:
        """
        生成完整的参数探索矩阵
        
        Yields:
            ExplorationParameters: 每个参数组合
        """
        for phi_name, phi_value in PHI_PRESETS.items():
            for dth_name, dth_value in DELTA_THETA_PRESETS.items():
                for f_base in self.f_base_candidates:
                    yield ExplorationParameters(
                        phi_name=phi_name,
                        phi_value=phi_value,
                        delta_theta_name=dth_name,
                        delta_theta_value=dth_value,
                        f_base=f_base,
                        f_min=self.f_min,
                        f_max=self.f_max
                    )
    
    def explore_single_combination(self, params: ExplorationParameters) -> ExplorationResult:
        """
        探索单个参数组合
        
        Args:
            params: 探索参数
            
        Returns:
            ExplorationResult: 探索结果
        """
        try:
            # 创建音阶对象
            scale = PetersenScale_Phi(
                F_base=params.f_base,
                phi=params.phi_value,
                delta_theta=params.delta_theta_value,
                F_min=params.f_min,
                F_max=params.f_max
            )
            
            # 生成音阶条目
            entries = scale.generate_raw()
            
            # 计算基础指标
            basic_metrics = self._calculate_basic_metrics(scale, entries)
            
            return ExplorationResult(
                parameters=params,
                scale=scale,
                entries=entries,
                success=True,
                basic_metrics=basic_metrics
            )
            
        except Exception as e:
            return ExplorationResult(
                parameters=params,
                scale=None,
                entries=[],
                success=False,
                error_message=str(e)
            )
    
    def _calculate_basic_metrics(self, scale: PetersenScale_Phi, entries: List) -> Dict:
        """
        计算基础度量指标
        
        Args:
            scale: 音阶对象
            entries: 音阶条目列表
            
        Returns:
            Dict: 基础指标字典
        """
        if not entries:
            return {
                'entry_count': 0,
                'frequency_range': (0, 0),
                'valid': False
            }
        
        frequencies = [entry.freq for entry in entries]
        intervals = scale.analyze_intervals()
        
        metrics = {
            'entry_count': len(entries),
            'frequency_range': (min(frequencies), max(frequencies)),
            'frequency_span_octaves': 0,
            'average_frequency': sum(frequencies) / len(frequencies),
            'valid': True
        }
        
        # 计算频率跨度（八度数）
        if frequencies:
            metrics['frequency_span_octaves'] = \
                math.log2(max(frequencies) / min(frequencies))
        
        # 音程分析
        if intervals:
            interval_cents = [interval['cents'] for interval in intervals]
            metrics.update({
                'interval_count': len(intervals),
                'min_interval_cents': min(interval_cents),
                'max_interval_cents': max(interval_cents),
                'avg_interval_cents': sum(interval_cents) / len(interval_cents),
                'interval_std': self._calculate_std(interval_cents)
            })
            
            # 微分音和大音程统计
            micro_intervals = sum(1 for c in interval_cents if c < 50)
            large_intervals = sum(1 for c in interval_cents if c > 300)
            
            metrics.update({
                'micro_interval_count': micro_intervals,
                'large_interval_count': large_intervals,
                'micro_interval_ratio': micro_intervals / len(intervals),
                'large_interval_ratio': large_intervals / len(intervals)
            })
        else:
            metrics.update({
                'interval_count': 0,
                'min_interval_cents': 0,
                'max_interval_cents': 0,
                'avg_interval_cents': 0,
                'interval_std': 0,
                'micro_interval_count': 0,
                'large_interval_count': 0,
                'micro_interval_ratio': 0,
                'large_interval_ratio': 0
            })
        
        return metrics
    
    def _calculate_std(self, values: List[float]) -> float:
        """计算标准差"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def explore_all_combinations(self, 
                               progress_callback=None,
                               error_callback=None) -> List[ExplorationResult]:
        """
        探索所有参数组合
        
        Args:
            progress_callback: 进度回调函数 (current, total, result)
            error_callback: 错误回调函数 (params, error)
            
        Returns:
            List[ExplorationResult]: 所有探索结果
        """
        self.exploration_results.clear()
        
        for i, params in enumerate(self.get_exploration_matrix()):
            result = self.explore_single_combination(params)
            self.exploration_results.append(result)
            
            # 进度回调
            if progress_callback:
                progress_callback(i + 1, self.total_combinations, result)
            
            # 错误回调
            if not result.success and error_callback:
                error_callback(params, result.error_message)
        
        return self.exploration_results
    
    def get_successful_results(self) -> List[ExplorationResult]:
        """获取成功的探索结果"""
        return [r for r in self.exploration_results if r.success]
    
    def get_failed_results(self) -> List[ExplorationResult]:
        """获取失败的探索结果"""
        return [r for r in self.exploration_results if not r.success]
    
    def get_statistics_summary(self) -> Dict:
        """获取探索统计摘要"""
        successful = self.get_successful_results()
        failed = self.get_failed_results()
        
        return {
            'total_combinations': self.total_combinations,
            'successful_count': len(successful),
            'failed_count': len(failed),
            'success_rate': len(successful) / self.total_combinations if self.total_combinations > 0 else 0,
            'phi_preset_count': len(PHI_PRESETS),
            'delta_theta_preset_count': len(DELTA_THETA_PRESETS),
            'f_base_candidate_count': len(self.f_base_candidates)
        }
    
    def filter_by_criteria(self, 
                          min_entries: int = 5,
                          max_entries: int = 60,
                          min_interval_cents: float = 5.0,
                          max_interval_cents: float = 600.0) -> List[ExplorationResult]:
        """
        根据标准筛选结果
        
        Args:
            min_entries: 最少音符数
            max_entries: 最多音符数
            min_interval_cents: 最小音程（音分）
            max_interval_cents: 最大音程（音分）
            
        Returns:
            List[ExplorationResult]: 筛选后的结果
        """
        filtered = []
        
        for result in self.get_successful_results():
            metrics = result.basic_metrics
            
            if not metrics or not metrics['valid']:
                continue
            
            # 检查音符数量
            if not (min_entries <= metrics['entry_count'] <= max_entries):
                continue
            
            # 检查音程范围
            if metrics['interval_count'] > 0:
                if not (min_interval_cents <= metrics['min_interval_cents']):
                    continue
                if not (metrics['max_interval_cents'] <= max_interval_cents):
                    continue
            
            filtered.append(result)
        
        return filtered
    
    def group_by_phi_preset(self) -> Dict[str, List[ExplorationResult]]:
        """按φ预设分组结果"""
        groups = {}
        
        for result in self.get_successful_results():
            phi_name = result.parameters.phi_name
            if phi_name not in groups:
                groups[phi_name] = []
            groups[phi_name].append(result)
        
        return groups
    
    def group_by_delta_theta_preset(self) -> Dict[str, List[ExplorationResult]]:
        """按δθ预设分组结果"""
        groups = {}
        
        for result in self.get_successful_results():
            dth_name = result.parameters.delta_theta_name
            if dth_name not in groups:
                groups[dth_name] = []
            groups[dth_name].append(result)
        
        return groups

# 工具函数
import math

def format_exploration_result(result: ExplorationResult, detailed: bool = False) -> str:
    """
    格式化探索结果为可读字符串
    
    Args:
        result: 探索结果
        detailed: 是否显示详细信息
        
    Returns:
        str: 格式化字符串
    """
    if not result.success:
        return f"❌ {result.parameters} - 失败: {result.error_message}"
    
    metrics = result.basic_metrics
    basic_info = f"✅ {result.parameters}"
    
    if metrics and detailed:
        basic_info += f"\n   📊 {metrics['entry_count']}个音符, "
        basic_info += f"音程{metrics['min_interval_cents']:.1f}-{metrics['max_interval_cents']:.1f}分, "
        basic_info += f"微分音{metrics['micro_interval_ratio']:.1%}"
    
    return basic_info

if __name__ == "__main__":
    # 简单测试
    explorer = ParameterSpaceExplorer()
    
    print(f"🔍 Petersen参数空间探索器")
    print(f"📊 总计组合数: {explorer.total_combinations}")
    print(f"🎵 φ预设数: {len(PHI_PRESETS)}")
    print(f"📐 δθ预设数: {len(DELTA_THETA_PRESETS)}")
    print(f"🎼 F_base候选数: {len(explorer.f_base_candidates)}")
    
    # 测试单个组合
    test_params = ExplorationParameters(
        phi_name="golden",
        phi_value=1.618033988749,
        delta_theta_name="petersen_original", 
        delta_theta_value=4.8,
        f_base=220.0
    )
    
    print(f"\n🧪 测试参数组合: {test_params}")
    test_result = explorer.explore_single_combination(test_params)
    print(format_exploration_result(test_result, detailed=True))