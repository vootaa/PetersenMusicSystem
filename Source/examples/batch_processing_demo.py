"""
批处理和自动化演示程序
展示系统的批量处理、自动化和高级集成功能
"""
import time
import json
import csv
import math
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import sys

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from enhanced_petersen_player import create_player, PlayerConfiguration
from utils.presets import COMPLETE_PRESET_COMBINATIONS, recommend_preset_for_context
from utils.analysis import FrequencyAnalyzer

@dataclass
class BatchJob:
    """批处理任务"""
    id: str
    name: str
    frequencies: List[float]
    key_names: List[str]
    mode: str = "solo_piano"
    style: str = "romantic"
    preset: Optional[str] = None
    priority: int = 1
    estimated_duration: float = 0.0

@dataclass
class ProcessingResult:
    """处理结果"""
    job_id: str
    success: bool
    duration: float
    notes_played: int
    accuracy_info: Optional[Dict] = None
    error_message: Optional[str] = None

class BatchProcessor:
    """批处理器"""
    
    def __init__(self):
        self.player = None
        self.job_queue: List[BatchJob] = []
        self.results: List[ProcessingResult] = []
        self.stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'total_notes': 0,
            'total_duration': 0.0
        }
    
    def initialize(self):
        """初始化批处理器"""
        print("🔄 初始化批处理系统...")
        
        # 创建优化的批处理配置
        config = PlayerConfiguration(
            enable_accurate_frequency=True,
            enable_effects=True,
            enable_expression=True,
            auto_optimize_settings=True,
            sample_rate=44100,
            buffer_size=1024
        )
        
        self.player = create_player()
        print("✅ 批处理系统初始化完成")
    
    def add_job(self, job: BatchJob):
        """添加批处理任务"""
        # 估算任务持续时间
        job.estimated_duration = len(job.frequencies) * 0.8 + 2.0  # 粗略估算
        
        self.job_queue.append(job)
        self.stats['total_jobs'] += 1
        print(f"📝 添加任务: {job.name} ({len(job.frequencies)} 音符)")
    
    def process_all_jobs(self, max_workers: int = 1):
        """处理所有任务"""
        if not self.job_queue:
            print("⚠️  没有待处理任务")
            return
        
        print(f"\n🚀 开始批处理 ({len(self.job_queue)} 个任务)...")
        
        # 按优先级排序
        self.job_queue.sort(key=lambda x: x.priority, reverse=True)
        
        start_time = time.time()
        
        # 由于FluidSynth通常不支持多线程，这里使用单线程处理
        for i, job in enumerate(self.job_queue, 1):
            print(f"\n[{i}/{len(self.job_queue)}] 处理任务: {job.name}")
            result = self._process_single_job(job)
            self.results.append(result)
            
            if result.success:
                self.stats['completed_jobs'] += 1
                self.stats['total_notes'] += result.notes_played
            else:
                self.stats['failed_jobs'] += 1
            
            self.stats['total_duration'] += result.duration
        
        total_time = time.time() - start_time
        
        print(f"\n✅ 批处理完成!")
        print(f"   总时间: {total_time:.1f}秒")
        print(f"   成功任务: {self.stats['completed_jobs']}/{self.stats['total_jobs']}")
        print(f"   失败任务: {self.stats['failed_jobs']}")
        print(f"   总音符数: {self.stats['total_notes']}")
    
    def _process_single_job(self, job: BatchJob) -> ProcessingResult:
        """处理单个任务"""
        start_time = time.time()
        
        try:
            # 应用预设（如果指定）
            if job.preset and job.preset in COMPLETE_PRESET_COMBINATIONS:
                preset = COMPLETE_PRESET_COMBINATIONS[job.preset]
                self.player.apply_preset_combination(
                    preset.effect_preset, preset.expression_preset
                )
            
            # 执行播放
            if job.mode == "solo_piano":
                success = self.player.performance_modes.execute_solo_piano_mode(
                    job.frequencies, job.key_names, job.style
                )
            elif job.mode == "comparison":
                success = self.player.performance_modes.execute_comparison_demo(
                    job.frequencies, job.key_names, "12tet_vs_petersen"
                )
            elif job.mode == "educational":
                success = self.player.performance_modes.execute_educational_mode(
                    job.frequencies, job.key_names, "basic_theory"
                )
            else:
                success = self.player.play_frequencies(job.frequencies, job.key_names)
            
            # 分析精确度
            accuracy_info = self.player.freq_player.analyze_frequency_accuracy(job.frequencies)
            
            duration = time.time() - start_time
            
            return ProcessingResult(
                job_id=job.id,
                success=success,
                duration=duration,
                notes_played=len(job.frequencies),
                accuracy_info=accuracy_info
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return ProcessingResult(
                job_id=job.id,
                success=False,
                duration=duration,
                notes_played=0,
                error_message=str(e)
            )
    
    def export_results(self, format: str = "json", filename: Optional[str] = None):
        """导出处理结果"""
        if not filename:
            timestamp = int(time.time())
            filename = f"batch_results_{timestamp}.{format}"
        
        output_path = Path("output") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        if format == "json":
            self._export_json(output_path)
        elif format == "csv":
            self._export_csv(output_path)
        else:
            print(f"❌ 不支持的格式: {format}")
            return
        
        print(f"📄 结果已导出: {output_path}")
    
    def _export_json(self, output_path: Path):
        """导出JSON格式"""
        export_data = {
            'metadata': {
                'export_time': time.time(),
                'total_jobs': self.stats['total_jobs'],
                'completed_jobs': self.stats['completed_jobs'],
                'failed_jobs': self.stats['failed_jobs'],
                'total_notes': self.stats['total_notes'],
                'total_duration': self.stats['total_duration']
            },
            'results': [asdict(result) for result in self.results]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, output_path: Path):
        """导出CSV格式"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = ['Job ID', 'Success', 'Duration', 'Notes Played', 
                      'Compensation Needed', 'Max Deviation', 'Error']
            writer.writerow(headers)
            
            # 写入数据
            for result in self.results:
                row = [
                    result.job_id,
                    result.success,
                    f"{result.duration:.2f}",
                    result.notes_played,
                    result.accuracy_info.get('needs_compensation_count', 0) if result.accuracy_info else 0,
                    result.accuracy_info.get('max_deviation', 0) if result.accuracy_info else 0,
                    result.error_message or ""
                ]
                writer.writerow(row)

class AutomatedDemo:
    """自动化演示系统"""
    
    def __init__(self):
        self.processor = BatchProcessor()
        
    def run_comprehensive_automation(self):
        """运行综合自动化演示"""
        print("🤖 Enhanced Petersen Music System 自动化演示")
        print("="*60)
        
        # 初始化
        self.processor.initialize()
        
        # 生成各种测试任务
        self._generate_scale_jobs()
        self._generate_accuracy_jobs()
        self._generate_expression_jobs()
        self._generate_comparison_jobs()
        self._generate_educational_jobs()
        
        # 执行批处理
        self.processor.process_all_jobs()
        
        # 分析结果
        self._analyze_results()
        
        # 导出报告
        self._export_reports()
    
    def _generate_scale_jobs(self):
        """生成音阶测试任务"""
        print("\n📝 生成音阶测试任务...")
        
        scales = [
            ("C大调", [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]),
            ("A小调", [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00]),
            ("G大调", [196.00, 220.00, 246.94, 261.63, 293.66, 329.63, 369.99, 392.00]),
            ("D大调", [146.83, 164.81, 184.99, 196.00, 220.00, 246.94, 277.18, 293.66])
        ]
        
        styles = ["classical", "romantic", "jazz"]
        presets = ["steinway_concert_grand", "chamber_music_intimate", "jazz_club_session"]
        
        for i, (scale_name, frequencies) in enumerate(scales):
            for j, style in enumerate(styles):
                job = BatchJob(
                    id=f"scale_{i}_{j}",
                    name=f"{scale_name}音阶 - {style}风格",
                    frequencies=frequencies,
                    key_names=[f"{scale_name[0]}{k+1}" for k in range(len(frequencies))],
                    mode="solo_piano",
                    style=style,
                    preset=presets[j % len(presets)],
                    priority=3
                )
                self.processor.add_job(job)
    
    def _generate_accuracy_jobs(self):
        """生成精确度测试任务"""
        print("📝 生成精确度测试任务...")
        
        # 生成需要不同程度补偿的频率
        accuracy_tests = [
            ("标准频率", [440.0, 523.25, 659.25, 783.99]),
            ("微调频率", [441.2, 524.8, 660.1, 785.3]),
            ("大偏差频率", [438.5, 521.7, 657.2, 781.1]),
            ("复杂微分音", [440.5, 523.8, 659.7, 784.5])
        ]
        
        for i, (test_name, frequencies) in enumerate(accuracy_tests):
            job = BatchJob(
                id=f"accuracy_{i}",
                name=f"精确度测试 - {test_name}",
                frequencies=frequencies,
                key_names=[f"Test{k+1}" for k in range(len(frequencies))],
                mode="comparison",
                priority=5
            )
            self.processor.add_job(job)
    
    def _generate_expression_jobs(self):
        """生成表现力测试任务"""
        print("📝 生成表现力测试任务...")
        
        melody = [261.63, 293.66, 329.63, 392.00, 440.00, 392.00, 329.63, 261.63]
        melody_names = ["C", "D", "E", "G", "A", "G", "E", "C"]
        
        expression_styles = [
            ("机械式", "mechanical"),
            ("浪漫主义", "romantic"),
            ("爵士风格", "jazz"),
            ("古典风格", "classical")
        ]
        
        for i, (style_name, style) in enumerate(expression_styles):
            job = BatchJob(
                id=f"expression_{i}",
                name=f"表现力测试 - {style_name}",
                frequencies=melody,
                key_names=melody_names,
                mode="solo_piano",
                style=style,
                priority=4
            )
            self.processor.add_job(job)
