"""
批处理和自动化演示程序
展示大规模音阶处理、自动优化设置、批量对比等功能
"""
import time
import json
import csv
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from enhanced_petersen_player import create_player, PlayerConfiguration
from utils.presets import COMPLETE_PRESET_COMBINATIONS, recommend_preset_for_context
from utils.analysis import analyze_petersen_scale_characteristics

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

class BatchAutomationDemo:
    """批处理自动化演示类"""
    
    def __init__(self):
        self.processor = BatchProcessor()
        self.player = None
        self.results = []
        self.start_time = time.time()
        
    def initialize(self):
        """初始化系统"""
        print("🤖 === 批处理自动化演示系统 ===")
        print("🔧 正在初始化...")
        
        config = PlayerConfiguration(
            auto_optimize_settings=True,
            enable_accurate_frequency=True,
            enable_effects=True,
            enable_expression=True
        )
        
        self.player = create_player(config=config)
        if not self.player:
            raise Exception("播放器初始化失败")
        
        # 初始化处理器
        self.processor.initialize()
        self.processor.player = self.player  # 共享播放器实例

        print("✅ 系统初始化完成\n")
    
    def run_complete_automation_suite(self):
        """运行完整的自动化测试套件"""
        print("🚀 开始批处理自动化演示...")
        
        # 1. SoundFont自动分析和优化
        self._demo_soundfont_automation()
        
        # 2. 多音阶批量处理
        self._demo_multi_scale_processing()
        
        # 3. 预设自动选择和应用
        self._demo_preset_automation()
        
        # 4. 性能基准测试
        self._demo_performance_benchmarks()
        
        # 5. 质量评估自动化
        self._demo_quality_assessment()
        
        # 6. 报告生成
        self._generate_automation_report()
    
    def _demo_soundfont_automation(self):
        """SoundFont自动化演示"""
        print("\n📁 === SoundFont自动化分析 ===")
        
        sf_manager = self.player.sf_manager
        sf_summary = sf_manager.get_soundfont_summary()
        
        print(f"🔍 分析 {sf_summary['total_soundfonts']} 个SoundFont...")
        
        # 自动质量排序和推荐
        soundfonts = []
        for sf_name, details in sf_summary['soundfont_details'].items():
            soundfonts.append({
                'name': sf_name,
                'quality': details['quality_score'],
                'size': details['size_mb'],
                'type': details['type'],
                'instruments': details['instrument_count']
            })
        
        # 按质量排序
        soundfonts.sort(key=lambda x: x['quality'], reverse=True)
        
        print("\n📊 SoundFont质量排序:")
        for i, sf in enumerate(soundfonts[:5], 1):  # 显示前5个
            print(f"   {i}. {sf['name']}")
            print(f"      质量: {sf['quality']:.3f}, 类型: {sf['type']}, 大小: {sf['size']:.1f}MB")
            print(f"      乐器数: {sf['instruments']}, 推荐用途: {sf['type']}")
        
        # 自动选择最佳SoundFont并加载
        if soundfonts:
            best_sf = soundfonts[0]
            print(f"\n🎯 自动选择最佳SoundFont: {best_sf['name']}")
            success = sf_manager.load_soundfont(best_sf['name'])
            if success:
                print("✅ 自动加载成功")
                
                # 自动优化设置
                optimization = sf_manager.optimize_for_petersen_scale(best_sf['name'])
                print(f"⚙️  自动优化建议: {len(optimization.get('recommended_instruments', []))} 个推荐乐器")
            else:
                print("❌ 自动加载失败")
    
    def _demo_multi_scale_processing(self):
        """多音阶批量处理演示"""
        print("\n🎼 === 多音阶批量处理 ===")
        
        # 生成多个测试音阶
        test_scales = self._generate_test_scales()
        
        print(f"🔄 准备处理 {len(test_scales)} 个音阶...")
        
        # 使用BatchProcessor添加任务
        for scale_data in test_scales:
            job = BatchJob(
                id=f"scale_{scale_data['name']}",
                name=scale_data['name'],
                frequencies=scale_data['frequencies'],
                key_names=scale_data['names'],
                mode="solo_piano",
                style="romantic"
            )
            self.processor.add_job(job)
        
        # 批量处理
        self.processor.process_all_jobs()

        # 批量结果统计
        batch_results = self.processor.results
        total_processed = len(batch_results)
        successful = sum(1 for r in batch_results if r.success)
        avg_time = sum(r.duration for r in batch_results) / total_processed if total_processed > 0 else 0
        
        print(f"\n📈 批量处理结果:")
        print(f"   总数: {total_processed}")
        print(f"   成功: {successful} ({successful/total_processed*100:.1f}%)")
        print(f"   平均处理时间: {avg_time:.3f}秒")
        
        self.results.extend(batch_results)
    
    def _demo_preset_automation(self):
        """预设自动化演示"""
        print("\n🎨 === 预设自动化选择 ===")
        
        # 测试不同场景的自动预设选择
        scenarios = [
            {'context': 'concert', 'description': '音乐会演出'},
            {'context': 'study', 'description': '学习研究'},
            {'context': 'recording', 'description': '录音制作'},
            {'context': 'demo', 'description': '演示展示'},
            {'context': 'jazz', 'description': '爵士表演'}
        ]
        
        available_soundfonts = list(self.player.sf_manager.soundfonts.keys())
        
        for scenario in scenarios:
            print(f"\n🎯 场景: {scenario['description']}")
            
            # 自动推荐预设
            recommended = recommend_preset_for_context(
                scenario['context'], 
                available_soundfonts=available_soundfonts
            )
            
            if recommended in COMPLETE_PRESET_COMBINATIONS:
                preset = COMPLETE_PRESET_COMBINATIONS[recommended]
                print(f"   推荐预设: {preset.name}")
                print(f"   描述: {preset.description}")
                print(f"   音效: {preset.effect_preset}")
                print(f"   表现力: {preset.expression_preset}")
                
                # 自动应用并测试
                success = self.player.apply_preset_combination(
                    preset.effect_preset, 
                    preset.expression_preset
                )
                
                if success:
                    # 用测试音符验证
                    test_freq = [440.0, 493.88, 523.25]  # A4, B4, C5
                    test_names = ["A4", "B4", "C5"]
                    
                    self.player.play_frequencies(test_freq, test_names, duration=0.5)
                    print(f"   ✅ 预设应用并测试成功")
                else:
                    print(f"   ❌ 预设应用失败")
            else:
                print(f"   ⚠️  未找到合适预设")
    
    def _demo_performance_benchmarks(self):
        """性能基准测试"""
        print("\n⚡ === 性能基准测试 ===")
        
        benchmark_tests = [
            {'name': '短序列播放 (5音符)', 'count': 5, 'iterations': 10},
            {'name': '中等序列播放 (20音符)', 'count': 20, 'iterations': 5},
            {'name': '长序列播放 (50音符)', 'count': 50, 'iterations': 3},
            {'name': '超长序列播放 (100音符)', 'count': 100, 'iterations': 1}
        ]
        
        benchmark_results = []
        
        for test in benchmark_tests:
            print(f"\n🔬 测试: {test['name']}")
            
            # 生成测试数据
            test_frequencies = self._generate_test_frequencies(test['count'])
            test_names = [f"T{i+1}" for i in range(test['count'])]
            
            times = []
            success_count = 0
            
            for iteration in range(test['iterations']):
                start_time = time.time()
                
                success = self.player.play_frequencies(
                    test_frequencies, test_names,
                    duration=0.1,  # 快速播放
                    gap=0.01,
                    show_progress=False
                )
                
                end_time = time.time()
                elapsed = end_time - start_time
                times.append(elapsed)
                
                if success:
                    success_count += 1
                
                print(f"   迭代 {iteration+1}: {elapsed:.3f}秒 {'✅' if success else '❌'}")
            
            # 统计结果
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            success_rate = success_count / test['iterations']
            
            result = {
                'test_name': test['name'],
                'note_count': test['count'],
                'iterations': test['iterations'],
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'success_rate': success_rate,
                'notes_per_second': test['count'] / avg_time if avg_time > 0 else 0
            }
            
            benchmark_results.append(result)
            
            print(f"   📊 平均时间: {avg_time:.3f}秒")
            print(f"   📊 成功率: {success_rate*100:.1f}%")
            print(f"   📊 播放速度: {result['notes_per_second']:.1f} 音符/秒")
        
        # 性能摘要
        print(f"\n📈 性能基准摘要:")
        for result in benchmark_results:
            print(f"   {result['test_name']}: {result['notes_per_second']:.1f} 音符/秒")
        
        self.results.extend(benchmark_results)
    
    def _demo_quality_assessment(self):
        """质量评估自动化"""
        print("\n🔍 === 质量评估自动化 ===")
        
        # 生成不同精度要求的测试频率
        test_cases = [
            {
                'name': '标准12平均律频率',
                'frequencies': [261.63, 293.66, 329.63, 349.23, 392.00],
                'expected_accuracy': 'high'
            },
            {
                'name': '微调频率（偏差<10音分）',
                'frequencies': [261.63 * 1.006, 293.66 * 0.994, 329.63 * 1.008],  # 轻微偏差
                'expected_accuracy': 'medium'
            },
            {
                'name': '大偏差频率（偏差>20音分）',
                'frequencies': [261.63 * 1.02, 293.66 * 0.98, 329.63 * 1.025],  # 较大偏差
                'expected_accuracy': 'low'
            }
        ]
        
        quality_results = []
        
        for test_case in test_cases:
            print(f"\n🧪 测试: {test_case['name']}")
            
            # 频率精度分析
            analysis = self.player.freq_player.analyze_frequency_accuracy(test_case['frequencies'])
            
            print(f"   📊 需要补偿: {analysis.get('needs_compensation_count', 0)} 个音符")
            print(f"   📊 补偿比例: {analysis.get('compensation_percentage', 0):.1f}%")
            print(f"   📊 最大偏差: {analysis.get('max_deviation', 0):.1f} 音分")
            print(f"   📊 平均偏差: {analysis.get('avg_deviation', 0):.1f} 音分")
            
            # 播放测试
            success = self.player.play_frequencies(
                test_case['frequencies'],
                duration=0.5,
                show_progress=False
            )
            
            # 质量评分
            quality_score = self._calculate_quality_score(analysis, success)
            
            result = {
                'test_name': test_case['name'],
                'expected_accuracy': test_case['expected_accuracy'],
                'analysis': analysis,
                'success': success,
                'quality_score': quality_score
            }
            
            quality_results.append(result)
            
            print(f"   ⭐ 质量评分: {quality_score:.2f}/1.0 {'✅' if success else '❌'}")
        
        # 整体质量评估
        avg_quality = sum(r['quality_score'] for r in quality_results) / len(quality_results)
        print(f"\n📊 整体质量评分: {avg_quality:.3f}/1.0")
        
        self.results.extend(quality_results)
    
    def _generate_automation_report(self):
        """生成自动化测试报告"""
        print("\n📋 === 自动化测试报告 ===")
        
        total_runtime = time.time() - self.start_time
        
        # 系统状态
        status = self.player.get_system_status()
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_runtime': total_runtime,
            'system_status': status,
            'test_results': self.results,
            'summary': {
                'total_tests': len(self.results),
                'successful_tests': sum(1 for r in self.results if r.get('success', False)),
                'average_quality': sum(r.get('quality_score', 0) for r in self.results 
                                     if 'quality_score' in r) / max(1, sum(1 for r in self.results if 'quality_score' in r))
            }
        }
        
        # 保存报告
        report_file = Path(__file__).parent / f"automation_report_{int(time.time())}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            print(f"📄 报告已保存: {report_file}")
        except Exception as e:
            print(f"⚠️  报告保存失败: {e}")
        
        # 打印摘要
        print(f"\n📈 测试摘要:")
        print(f"   总运行时间: {total_runtime:.1f}秒")
        print(f"   总测试数: {report['summary']['total_tests']}")
        print(f"   成功测试: {report['summary']['successful_tests']}")
        print(f"   成功率: {report['summary']['successful_tests']/max(1,report['summary']['total_tests'])*100:.1f}%")
        print(f"   平均质量: {report['summary']['average_quality']:.3f}/1.0")
        
        # 播放统计
        session_stats = status['session_stats']
        print(f"\n🎵 播放统计:")
        print(f"   播放音符数: {session_stats['notes_played']}")
        print(f"   播放序列数: {session_stats['sequences_played']}")
        print(f"   总播放时长: {session_stats['total_play_time']:.1f}秒")
        print(f"   平均音符时长: {session_stats['total_play_time']/max(1,session_stats['notes_played']):.3f}秒")
    
    def _generate_test_scales(self) -> List[Dict]:
        """生成测试音阶"""
        scales = []
        
        # C大调音阶
        scales.append({
            'name': 'C大调音阶',
            'frequencies': [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25],
            'names': ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
        })
        
        # A小调音阶
        scales.append({
            'name': 'A小调音阶',
            'frequencies': [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00],
            'names': ['A3', 'B3', 'C4', 'D4', 'E4', 'F4', 'G4', 'A4']
        })
        
        # 五声音阶
        scales.append({
            'name': '中国五声音阶',
            'frequencies': [261.63, 293.66, 329.63, 392.00, 440.00],
            'names': ['宫', '商', '角', '徵', '羽']
        })
        
        # 半音阶（部分）
        scales.append({
            'name': '半音阶片段',
            'frequencies': [261.63, 277.18, 293.66, 311.13, 329.63, 349.23],
            'names': ['C4', 'C#4', 'D4', 'D#4', 'E4', 'F4']
        })
        
        # 高频测试
        scales.append({
            'name': '高频区域测试',
            'frequencies': [1046.50, 1174.66, 1318.51, 1396.91, 1567.98],
            'names': ['C6', 'D6', 'E6', 'F6', 'G6']
        })
        
        return scales
    
    def _generate_test_frequencies(self, count: int) -> List[float]:
        """生成指定数量的测试频率"""
        base_freq = 261.63  # C4
        frequencies = []
        
        for i in range(count):
            # 生成一个八度内的频率
            semitone = i % 12
            octave = i // 12
            freq = base_freq * (2 ** octave) * (2 ** (semitone / 12))
            frequencies.append(freq)
        
        return frequencies
    
    def _analyze_scale_characteristics(self, frequencies: List[float], names: List[str]) -> Dict:
        """分析音阶特性"""
        if not frequencies:
            return {}
        
        return {
            'note_count': len(frequencies),
            'frequency_range': (min(frequencies), max(frequencies)),
            'frequency_span': max(frequencies) - min(frequencies),
            'avg_frequency': sum(frequencies) / len(frequencies),
            'has_high_frequencies': any(f > 1000 for f in frequencies),
            'has_low_frequencies': any(f < 200 for f in frequencies),
            'wide_range': max(frequencies) / min(frequencies) > 2.0
        }
    
    def _auto_select_mode(self, characteristics: Dict) -> str:
        """自动选择演奏模式"""
        note_count = characteristics.get('note_count', 0)
        wide_range = characteristics.get('wide_range', False)
        
        if note_count <= 5:
            return 'demo'
        elif note_count <= 15 and not wide_range:
            return 'study'
        elif wide_range or note_count > 30:
            return 'orchestral'
        else:
            return 'piano'
    
    def _calculate_quality_score(self, analysis: Dict, success: bool) -> float:
        """计算质量评分"""
        if not success:
            return 0.0
        
        score = 1.0
        
        # 根据补偿需求减分
        compensation_ratio = analysis.get('compensation_percentage', 0) / 100
        score -= compensation_ratio * 0.3  # 最多减30%
        
        # 根据偏差减分
        max_deviation = analysis.get('max_deviation', 0)
        if max_deviation > 50:  # 大于50音分
            score -= 0.4
        elif max_deviation > 20:  # 大于20音分
            score -= 0.2
        elif max_deviation > 10:  # 大于10音分
            score -= 0.1
        
        return max(0.0, score)
    
    def cleanup(self):
        """清理资源"""
        if self.player:
            self.player.cleanup()
        if self.processor:
            self.processor.export_results() # 可选：导出批处理结果

if __name__ == "__main__":
    """主函数"""
    demo = BatchAutomationDemo()
    
    try:
        demo.initialize()
        demo.run_complete_automation_suite()
        
        print("\n🎉 批处理自动化演示完成!")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        demo.cleanup()