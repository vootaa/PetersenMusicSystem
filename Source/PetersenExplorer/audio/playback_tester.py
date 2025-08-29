"""
Petersen音律音频播放测试器
使用Enhanced Petersen Player进行实际音频验证
"""
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
import sys
from pathlib import Path

# 添加父级路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent.parent))

try:
    from enhanced_petersen_player import create_player, PlayerConfiguration
except ImportError:
    print("⚠️ 无法导入enhanced_petersen_player，音频测试功能将不可用")
    create_player = None
    PlayerConfiguration = None

from ..core.parameter_explorer import ExplorationResult

class PlaybackTestType(Enum):
    """播放测试类型"""
    SCALE_ASCENDING = "scale_ascending"
    SCALE_DESCENDING = "scale_descending"
    INTERVAL_JUMPS = "interval_jumps"
    SIMPLE_MELODY = "simple_melody"
    CHORD_PROGRESSION = "chord_progression"
    HARMONIC_SERIES = "harmonic_series"
    FREQUENCY_SWEEP = "frequency_sweep"

@dataclass
class PlaybackTestResult:
    """播放测试结果"""
    test_type: PlaybackTestType
    success: bool
    notes_played: int
    notes_failed: int
    avg_play_duration: float
    timing_accuracy: float
    frequency_accuracy: float
    subjective_quality: str  # "excellent", "good", "acceptable", "poor"
    error_messages: List[str]
    detailed_log: List[Dict[str, Any]]

@dataclass
class SystemPlaybackAssessment:
    """系统播放评估"""
    system_info: Dict[str, Any]
    test_results: List[PlaybackTestResult]
    overall_playability: float  # 0-1
    technical_score: float      # 技术播放质量
    musical_score: float        # 音乐表现质量
    recommended_for_audio: bool
    optimization_suggestions: List[str]

class PetersenPlaybackTester:
    """Petersen音律播放测试器"""
    
    def __init__(self, soundfont_path: str = None):
        """
        初始化播放测试器
        
        Args:
            soundfont_path: SoundFont文件路径，支持以下选项：
                           - "GD_Steinway_Model_D274.sf2" (默认)
                           - "GD_Steinway_Model_D274II.sf2" 
                           - 完整路径
        """
        # 默认使用指定的两个Steinway钢琴SoundFont之一
        if soundfont_path is None:
            self.soundfont_path = "../../Soundfonts/GD_Steinway_Model_D274.sf2"
        elif soundfont_path in ["GD_Steinway_Model_D274.sf2", "GD_Steinway_Model_D274II.sf2"]:
            self.soundfont_path = f"../../Soundfonts/{soundfont_path}"
        else:
            self.soundfont_path = soundfont_path
            
        self.player = None
        self.test_configuration = {
            'note_duration': 0.5,
            'chord_duration': 1.5,
            'rest_duration': 0.1,
            'velocity': 70,
            'test_timeout': 30.0
        }
    
    def __enter__(self):
        """上下文管理器进入"""
        if create_player is None:
            raise RuntimeError("Enhanced Petersen Player不可用")
        
        # 使用soundfont_dir参数，让enhanced_petersen_player自动管理SoundFont
        soundfont_dir = str(Path(self.soundfont_path).parent)
        self.player = create_player(soundfont_dir=soundfont_dir)
        self.player.__enter__()
        
        # 配置播放器 - 强制使用钢琴模式
        config = PlayerConfiguration(
            mode="solo_piano",
            style="classical",
            soundfont_name=Path(self.soundfont_path).name
        )
        self.player.configure(config)
        
        print(f"🎹 播放测试器已初始化，使用SoundFont: {Path(self.soundfont_path).name}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        if self.player:
            self.player.__exit__(exc_type, exc_val, exc_tb)
            self.player = None
    
    def test_system_playability(self, exploration_result: ExplorationResult,
                              test_types: List[PlaybackTestType] = None,
                              interactive: bool = False) -> SystemPlaybackAssessment:
        """
        测试音律系统的播放能力
        
        Args:
            exploration_result: 探索结果
            test_types: 要执行的测试类型列表
            interactive: 是否交互模式（等待用户确认）
            
        Returns:
            SystemPlaybackAssessment: 播放评估结果
        """
        if not exploration_result.success or not exploration_result.entries:
            return self._create_failed_assessment(exploration_result, "系统生成失败或无音符")
        
        test_types = test_types or [
            PlaybackTestType.SCALE_ASCENDING,
            PlaybackTestType.SCALE_DESCENDING,
            PlaybackTestType.INTERVAL_JUMPS,
            PlaybackTestType.SIMPLE_MELODY,
            PlaybackTestType.CHORD_PROGRESSION
        ]
        
        print(f"\n🎼 开始测试音律系统播放能力")
        print(f"   参数: {exploration_result.parameters}")
        print(f"   音符数量: {len(exploration_result.entries)}")
        print(f"   测试项目: {len(test_types)}个")
        
        test_results = []
        
        for test_type in test_types:
            if interactive:
                input(f"   按回车开始 {test_type.value} 测试...")
            
            print(f"   🎵 执行 {test_type.value} 测试...")
            
            try:
                result = self._execute_single_test(exploration_result, test_type)
                test_results.append(result)
                
                status = "✅ 成功" if result.success else "❌ 失败"
                print(f"      {status} - {result.notes_played}/{result.notes_played + result.notes_failed} 音符播放")
                
                if result.error_messages:
                    for error in result.error_messages:
                        print(f"      ⚠️ {error}")
            
            except Exception as e:
                error_result = PlaybackTestResult(
                    test_type=test_type,
                    success=False,
                    notes_played=0,
                    notes_failed=0,
                    avg_play_duration=0,
                    timing_accuracy=0,
                    frequency_accuracy=0,
                    subjective_quality="poor",
                    error_messages=[f"测试异常: {str(e)}"],
                    detailed_log=[]
                )
                test_results.append(error_result)
                print(f"      ❌ 测试异常: {str(e)}")
        
        # 计算综合评估
        assessment = self._calculate_system_assessment(exploration_result, test_results)
        
        print(f"\n📊 播放测试完成")
        print(f"   整体播放能力: {assessment.overall_playability:.1%}")
        print(f"   技术质量: {assessment.technical_score:.1%}")
        print(f"   音乐质量: {assessment.musical_score:.1%}")
        print(f"   推荐用于音频: {'是' if assessment.recommended_for_audio else '否'}")
        
        return assessment
    
    def _execute_single_test(self, exploration_result: ExplorationResult, 
                            test_type: PlaybackTestType) -> PlaybackTestResult:
        """执行单个播放测试"""
        
        entries = exploration_result.entries
        start_time = time.time()
        
        if test_type == PlaybackTestType.SCALE_ASCENDING:
            return self._test_scale_ascending(entries)
        elif test_type == PlaybackTestType.SCALE_DESCENDING:
            return self._test_scale_descending(entries)
        elif test_type == PlaybackTestType.INTERVAL_JUMPS:
            return self._test_interval_jumps(entries)
        elif test_type == PlaybackTestType.SIMPLE_MELODY:
            return self._test_simple_melody(entries)
        elif test_type == PlaybackTestType.CHORD_PROGRESSION:
            return self._test_chord_progression(entries)
        elif test_type == PlaybackTestType.HARMONIC_SERIES:
            return self._test_harmonic_series(entries)
        elif test_type == PlaybackTestType.FREQUENCY_SWEEP:
            return self._test_frequency_sweep(entries)
        else:
            raise ValueError(f"未知测试类型: {test_type}")
    
    def _test_scale_ascending(self, entries: List) -> PlaybackTestResult:
        """测试上行音阶"""
        played = 0
        failed = 0
        error_messages = []
        detailed_log = []
        
        # 限制测试音符数量以避免过长
        test_entries = entries[:min(20, len(entries))]
        
        start_time = time.time()
        
        for i, entry in enumerate(test_entries):
            note_start = time.time()
            
            try:
                scale_data = [{
                    'freq': entry.freq,
                    'key': entry.key_short,
                    'name': entry.key_long
                }]
                
                success = self.player.play_petersen_scale(
                    scale_data,
                    duration=self.test_configuration['note_duration'],
                    velocity=self.test_configuration['velocity']
                )
                
                if success:
                    played += 1
                    detailed_log.append({
                        'index': i,
                        'frequency': entry.freq,
                        'key': entry.key_short,
                        'success': True,
                        'duration': time.time() - note_start
                    })
                else:
                    failed += 1
                    error_messages.append(f"音符 {entry.key_short} ({entry.freq:.1f}Hz) 播放失败")
                    detailed_log.append({
                        'index': i,
                        'frequency': entry.freq,
                        'key': entry.key_short,
                        'success': False,
                        'error': '播放函数返回失败'
                    })
                
                # 音符间隔
                if i < len(test_entries) - 1:
                    time.sleep(self.test_configuration['rest_duration'])
            
            except Exception as e:
                failed += 1
                error_messages.append(f"音符 {entry.key_short} 播放异常: {str(e)}")
                detailed_log.append({
                    'index': i,
                    'frequency': entry.freq,
                    'key': entry.key_short,
                    'success': False,
                    'error': str(e)
                })
        
        total_time = time.time() - start_time
        avg_duration = total_time / len(test_entries) if test_entries else 0
        
        success_rate = played / (played + failed) if (played + failed) > 0 else 0
        
        return PlaybackTestResult(
            test_type=PlaybackTestType.SCALE_ASCENDING,
            success=success_rate >= 0.8,  # 80%以上成功率认为成功
            notes_played=played,
            notes_failed=failed,
            avg_play_duration=avg_duration,
            timing_accuracy=self._calculate_timing_accuracy(detailed_log),
            frequency_accuracy=1.0,  # 假设频率精确（由Player处理）
            subjective_quality=self._assess_subjective_quality(success_rate),
            error_messages=error_messages,
            detailed_log=detailed_log
        )
    
    def _test_scale_descending(self, entries: List) -> PlaybackTestResult:
        """测试下行音阶"""
        # 反转音符顺序
        reversed_entries = list(reversed(entries[:min(20, len(entries))]))
        
        # 复用上行音阶测试逻辑，但改变测试类型
        result = self._test_scale_ascending(reversed_entries)
        result.test_type = PlaybackTestType.SCALE_DESCENDING
        
        return result
    
    def _test_interval_jumps(self, entries: List) -> PlaybackTestResult:
        """测试音程跳跃"""
        played = 0
        failed = 0
        error_messages = []
        detailed_log = []
        
        if len(entries) < 3:
            return PlaybackTestResult(
                test_type=PlaybackTestType.INTERVAL_JUMPS,
                success=False,
                notes_played=0,
                notes_failed=0,
                avg_play_duration=0,
                timing_accuracy=0,
                frequency_accuracy=0,
                subjective_quality="poor",
                error_messages=["音符数量不足，无法进行跳跃测试"],
                detailed_log=[]
            )
        
        # 选择跳跃模式：1st, 3rd, 5th, 2nd, 4th...
        jump_pattern = []
        step = max(1, len(entries) // 6)  # 确保不超过6个音符
        
        for i in range(0, min(len(entries), 12), step):
            if i < len(entries):
                jump_pattern.append(entries[i])
        
        start_time = time.time()
        
        for i, entry in enumerate(jump_pattern):
            note_start = time.time()
            
            try:
                scale_data = [{
                    'freq': entry.freq,
                    'key': entry.key_short,
                    'name': entry.key_long
                }]
                
                success = self.player.play_petersen_scale(
                    scale_data,
                    duration=self.test_configuration['note_duration'],
                    velocity=self.test_configuration['velocity']
                )
                
                if success:
                    played += 1
                    detailed_log.append({
                        'index': i,
                        'frequency': entry.freq,
                        'key': entry.key_short,
                        'success': True,
                        'duration': time.time() - note_start,
                        'jump_type': 'interval_jump'
                    })
                else:
                    failed += 1
                    error_messages.append(f"跳跃音符 {entry.key_short} 播放失败")
                
                time.sleep(self.test_configuration['rest_duration'])
            
            except Exception as e:
                failed += 1
                error_messages.append(f"跳跃音符 {entry.key_short} 异常: {str(e)}")
        
        total_time = time.time() - start_time
        avg_duration = total_time / len(jump_pattern) if jump_pattern else 0
        success_rate = played / (played + failed) if (played + failed) > 0 else 0
        
        return PlaybackTestResult(
            test_type=PlaybackTestType.INTERVAL_JUMPS,
            success=success_rate >= 0.8,
            notes_played=played,
            notes_failed=failed,
            avg_play_duration=avg_duration,
            timing_accuracy=self._calculate_timing_accuracy(detailed_log),
            frequency_accuracy=1.0,
            subjective_quality=self._assess_subjective_quality(success_rate),
            error_messages=error_messages,
            detailed_log=detailed_log
        )
    
    def _test_simple_melody(self, entries: List) -> PlaybackTestResult:
        """测试简单旋律"""
        played = 0
        failed = 0
        error_messages = []
        detailed_log = []
        
        if len(entries) < 5:
            return PlaybackTestResult(
                test_type=PlaybackTestType.SIMPLE_MELODY,
                success=False,
                notes_played=0,
                notes_failed=0,
                avg_play_duration=0,
                timing_accuracy=0,
                frequency_accuracy=0,
                subjective_quality="poor",
                error_messages=["音符数量不足，无法构建旋律"],
                detailed_log=[]
            )
        
        # 构建简单旋律模式
        melody_length = min(8, len(entries))
        step = len(entries) // melody_length
        
        melody_notes = []
        for i in range(0, len(entries), step):
            if len(melody_notes) < melody_length:
                melody_notes.append(entries[i])
        
        # 旋律模式：上行-下行-跳跃
        melody_pattern = []
        if len(melody_notes) >= 4:
            melody_pattern = [
                melody_notes[0],  # 起始
                melody_notes[1],  # 上行
                melody_notes[2],  # 继续
                melody_notes[1],  # 回落
                melody_notes[3] if len(melody_notes) > 3 else melody_notes[0],  # 跳跃
                melody_notes[0]   # 结束
            ]
        
        start_time = time.time()
        
        for i, entry in enumerate(melody_pattern):
            note_start = time.time()
            
            try:
                scale_data = [{
                    'freq': entry.freq,
                    'key': entry.key_short,
                    'name': entry.key_long
                }]
                
                # 旋律中的音符稍长一些
                duration = self.test_configuration['note_duration'] * 1.2
                
                success = self.player.play_petersen_scale(
                    scale_data,
                    duration=duration,
                    velocity=self.test_configuration['velocity']
                )
                
                if success:
                    played += 1
                    detailed_log.append({
                        'index': i,
                        'frequency': entry.freq,
                        'key': entry.key_short,
                        'success': True,
                        'duration': time.time() - note_start,
                        'melody_position': i
                    })
                else:
                    failed += 1
                    error_messages.append(f"旋律音符 {entry.key_short} 播放失败")
                
                time.sleep(self.test_configuration['rest_duration'] * 0.8)  # 旋律间隔稍短
            
            except Exception as e:
                failed += 1
                error_messages.append(f"旋律音符 {entry.key_short} 异常: {str(e)}")
        
        total_time = time.time() - start_time
        avg_duration = total_time / len(melody_pattern) if melody_pattern else 0
        success_rate = played / (played + failed) if (played + failed) > 0 else 0
        
        return PlaybackTestResult(
            test_type=PlaybackTestType.SIMPLE_MELODY,
            success=success_rate >= 0.8,
            notes_played=played,
            notes_failed=failed,
            avg_play_duration=avg_duration,
            timing_accuracy=self._calculate_timing_accuracy(detailed_log),
            frequency_accuracy=1.0,
            subjective_quality=self._assess_subjective_quality(success_rate),
            error_messages=error_messages,
            detailed_log=detailed_log
        )
    
    def _test_chord_progression(self, entries: List) -> PlaybackTestResult:
        """测试和弦进行"""
        played = 0
        failed = 0
        error_messages = []
        detailed_log = []
        
        if len(entries) < 3:
            return PlaybackTestResult(
                test_type=PlaybackTestType.CHORD_PROGRESSION,
                success=False,
                notes_played=0,
                notes_failed=0,
                avg_play_duration=0,
                timing_accuracy=0,
                frequency_accuracy=0,
                subjective_quality="poor",
                error_messages=["音符数量不足，无法构建和弦"],
                detailed_log=[]
            )
        
        # 构建简单和弦进行：选择3-4个音符组成和弦
        chord_size = min(4, len(entries) // 2)
        step = len(entries) // chord_size
        
        chord_notes = []
        for i in range(0, len(entries), step):
            if len(chord_notes) < chord_size:
                chord_notes.append(entries[i])
        
        start_time = time.time()
        chord_start = time.time()
        
        try:
            # 准备和弦数据
            chord_data = []
            for entry in chord_notes:
                chord_data.append({
                    'freq': entry.freq,
                    'key': entry.key_short,
                    'name': entry.key_long
                })
            
            # 尝试同时播放和弦（如果Player支持）
            # 这里假设player支持和弦模式
            success = True
            
            # 如果不支持同时播放，则快速连续播放
            for i, entry in enumerate(chord_notes):
                note_data = [{
                    'freq': entry.freq,
                    'key': entry.key_short,
                    'name': entry.key_long
                }]
                
                note_success = self.player.play_petersen_scale(
                    note_data,
                    duration=self.test_configuration['chord_duration'],
                    velocity=self.test_configuration['velocity'] - 10  # 和弦音量稍低
                )
                
                if note_success:
                    played += 1
                    detailed_log.append({
                        'index': i,
                        'frequency': entry.freq,
                        'key': entry.key_short,
                        'success': True,
                        'chord_position': i,
                        'duration': time.time() - chord_start
                    })
                else:
                    failed += 1
                    success = False
                    error_messages.append(f"和弦音符 {entry.key_short} 播放失败")
                
                # 和弦音符之间的微小间隔
                if i < len(chord_notes) - 1:
                    time.sleep(0.05)
        
        except Exception as e:
            failed = len(chord_notes)
            played = 0
            success = False
            error_messages.append(f"和弦播放异常: {str(e)}")
        
        total_time = time.time() - start_time
        avg_duration = total_time
        success_rate = played / (played + failed) if (played + failed) > 0 else 0
        
        return PlaybackTestResult(
            test_type=PlaybackTestType.CHORD_PROGRESSION,
            success=success_rate >= 0.7,  # 和弦测试要求稍低
            notes_played=played,
            notes_failed=failed,
            avg_play_duration=avg_duration,
            timing_accuracy=self._calculate_timing_accuracy(detailed_log),
            frequency_accuracy=1.0,
            subjective_quality=self._assess_subjective_quality(success_rate),
            error_messages=error_messages,
            detailed_log=detailed_log
        )
    
    def _test_harmonic_series(self, entries: List) -> PlaybackTestResult:
        """测试泛音列相关性"""
        # 这是一个更复杂的测试，检查音符是否符合自然泛音关系
        # 暂时使用简化实现
        return self._test_scale_ascending(entries[:min(10, len(entries))])
    
    def _test_frequency_sweep(self, entries: List) -> PlaybackTestResult:
        """测试频率扫描"""
        # 按频率顺序播放所有音符
        sorted_entries = sorted(entries, key=lambda x: x.freq)
        result = self._test_scale_ascending(sorted_entries)
        result.test_type = PlaybackTestType.FREQUENCY_SWEEP
        return result
    
    def _calculate_timing_accuracy(self, detailed_log: List[Dict]) -> float:
        """计算时序准确性"""
        if not detailed_log:
            return 0.0
        
        successful_notes = [log for log in detailed_log if log.get('success', False)]
        if not successful_notes:
            return 0.0
        
        # 简化的时序评估：基于播放成功率
        return len(successful_notes) / len(detailed_log)
    
    def _assess_subjective_quality(self, success_rate: float) -> str:
        """评估主观质量"""
        if success_rate >= 0.9:
            return "excellent"
        elif success_rate >= 0.8:
            return "good"
        elif success_rate >= 0.6:
            return "acceptable"
        else:
            return "poor"
    
    def _calculate_system_assessment(self, exploration_result: ExplorationResult,
                                   test_results: List[PlaybackTestResult]) -> SystemPlaybackAssessment:
        """计算系统播放评估"""
        if not test_results:
            return self._create_failed_assessment(exploration_result, "无测试结果")
        
        # 计算综合成功率
        total_notes_played = sum(r.notes_played for r in test_results)
        total_notes_attempted = sum(r.notes_played + r.notes_failed for r in test_results)
        overall_success_rate = total_notes_played / total_notes_attempted if total_notes_attempted > 0 else 0
        
        # 技术评分（基于播放成功率和准确性）
        technical_scores = []
        for result in test_results:
            if result.notes_played + result.notes_failed > 0:
                test_success_rate = result.notes_played / (result.notes_played + result.notes_failed)
                technical_scores.append(test_success_rate * result.timing_accuracy)
        
        technical_score = sum(technical_scores) / len(technical_scores) if technical_scores else 0
        
        # 音乐评分（基于不同测试类型的重要性）
        musical_weights = {
            PlaybackTestType.SCALE_ASCENDING: 0.2,
            PlaybackTestType.SCALE_DESCENDING: 0.2,
            PlaybackTestType.SIMPLE_MELODY: 0.3,
            PlaybackTestType.CHORD_PROGRESSION: 0.2,
            PlaybackTestType.INTERVAL_JUMPS: 0.1
        }
        
        musical_score = 0
        total_weight = 0
        
        for result in test_results:
            weight = musical_weights.get(result.test_type, 0.1)
            if result.notes_played + result.notes_failed > 0:
                test_score = result.notes_played / (result.notes_played + result.notes_failed)
                musical_score += test_score * weight
                total_weight += weight
        
        musical_score = musical_score / total_weight if total_weight > 0 else 0
        
        # 整体播放能力
        overall_playability = (technical_score * 0.6 + musical_score * 0.4)
        
        # 推荐判断
        recommended_for_audio = (
            overall_playability >= 0.7 and
            technical_score >= 0.8 and
            overall_success_rate >= 0.8
        )
        
        # 优化建议
        optimization_suggestions = self._generate_optimization_suggestions(test_results, exploration_result)
        
        return SystemPlaybackAssessment(
            system_info={
                'parameters': str(exploration_result.parameters),
                'entry_count': len(exploration_result.entries),
                'frequency_range': (
                    min(e.freq for e in exploration_result.entries),
                    max(e.freq for e in exploration_result.entries)
                ) if exploration_result.entries else (0, 0)
            },
            test_results=test_results,
            overall_playability=overall_playability,
            technical_score=technical_score,
            musical_score=musical_score,
            recommended_for_audio=recommended_for_audio,
            optimization_suggestions=optimization_suggestions
        )
    
    def _generate_optimization_suggestions(self, test_results: List[PlaybackTestResult],
                                         exploration_result: ExplorationResult) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 分析失败模式
        chord_test = next((r for r in test_results if r.test_type == PlaybackTestType.CHORD_PROGRESSION), None)
        if chord_test and not chord_test.success:
            suggestions.append("和弦播放困难，建议专注于单音线条音乐")
        
        melody_test = next((r for r in test_results if r.test_type == PlaybackTestType.SIMPLE_MELODY), None)
        if melody_test and not melody_test.success:
            suggestions.append("旋律构建困难，建议用于音响实验而非传统音乐")
        
        # 分析音符数量
        if len(exploration_result.entries) > 30:
            suggestions.append("音符数量较多，建议选择性使用部分音符")
        elif len(exploration_result.entries) < 8:
            suggestions.append("音符数量较少，建议与其他音律系统结合使用")
        
        # 分析播放成功率
        avg_success_rate = sum(
            r.notes_played / (r.notes_played + r.notes_failed) 
            for r in test_results 
            if r.notes_played + r.notes_failed > 0
        ) / len([r for r in test_results if r.notes_played + r.notes_failed > 0])
        
        if avg_success_rate < 0.8:
            suggestions.append("播放成功率较低，建议检查频率范围和Player配置")
        
        return suggestions
    
    def _create_failed_assessment(self, exploration_result: ExplorationResult, 
                                reason: str) -> SystemPlaybackAssessment:
        """创建失败的评估结果"""
        return SystemPlaybackAssessment(
            system_info={
                'parameters': str(exploration_result.parameters) if exploration_result else "N/A",
                'entry_count': 0,
                'frequency_range': (0, 0)
            },
            test_results=[],
            overall_playability=0.0,
            technical_score=0.0,
            musical_score=0.0,
            recommended_for_audio=False,
            optimization_suggestions=[f"测试失败: {reason}"]
        )

def format_playback_assessment(assessment: SystemPlaybackAssessment) -> str:
    """格式化播放评估结果"""
    output = []
    
    output.append("🎼 === 播放能力评估 ===")
    output.append(f"📊 整体播放能力: {assessment.overall_playability:.1%}")
    output.append(f"⚙️  技术评分: {assessment.technical_score:.1%}")
    output.append(f"🎵 音乐评分: {assessment.musical_score:.1%}")
    output.append(f"✅ 音频推荐: {'是' if assessment.recommended_for_audio else '否'}")
    
    if assessment.test_results:
        output.append("\n📋 测试详情:")
        for result in assessment.test_results:
            status = "✅" if result.success else "❌"
            output.append(f"   {status} {result.test_type.value}: "
                         f"{result.notes_played}/{result.notes_played + result.notes_failed} 音符, "
                         f"质量: {result.subjective_quality}")
    
    if assessment.optimization_suggestions:
        output.append("\n💡 优化建议:")
        for suggestion in assessment.optimization_suggestions:
            output.append(f"   • {suggestion}")
    
    return "\n".join(output)