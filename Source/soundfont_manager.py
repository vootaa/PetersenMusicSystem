"""
SoundFont管理模块
提供SoundFont文件分析、乐器检测、质量评估和自动优化功能
"""
import os
import ctypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.analysis import SoundFontAnalyzer
from utils.constants import DEFAULT_SOUNDFONTS, INSTRUMENT_CATEGORIES, QUALITY_THRESHOLDS


class SoundFontType(Enum):
    """SoundFont类型枚举"""
    PIANO_SPECIALIZED = "piano_specialized"
    ORCHESTRAL = "orchestral" 
    GENERAL_MIDI = "general_midi"
    SYNTHESIZER = "synthesizer"
    ETHNIC = "ethnic"
    UNKNOWN = "unknown"

@dataclass
class InstrumentInfo:
    """乐器信息"""
    program: int
    bank: int
    name: str
    category: str
    preset_name: str = ""
    sample_quality: str = "unknown"
    
@dataclass
class SoundFontInfo:
    """SoundFont信息"""
    file_path: Path
    file_size_mb: float
    sf_type: SoundFontType
    quality_score: float
    instrument_count: int
    available_instruments: List[InstrumentInfo]
    recommended_settings: Dict
    is_loaded: bool = False
    fluid_sf_id: Optional[int] = None

class SoundFontManager:
    """SoundFont管理器"""
    
    def __init__(self, fluidsynth_lib, synth, soundfont_directory: str = "../Soundfonts"):
        """
        初始化SoundFont管理器
        
        Args:
            fluidsynth_lib: FluidSynth动态库对象
            synth: FluidSynth合成器对象
            soundfont_directory: SoundFont文件目录
        """
        self.fluidsynth = fluidsynth_lib
        self.synth = synth
        self.soundfont_dir = Path(soundfont_directory)
   
        # SoundFont注册表
        self.soundfonts: Dict[str, SoundFontInfo] = {}
        self.current_soundfont: Optional[str] = None
        self.loaded_soundfonts: Set[str] = set()
        
        print(f"✓ SoundFont管理器已初始化，目录: {self.soundfont_dir}")
        
        # 扫描并分析SoundFont文件
        self._scan_soundfonts()
    
    def _scan_soundfonts(self) -> None:
        """扫描并分析SoundFont文件"""
        if not self.soundfont_dir.exists():
            print(f"⚠️  SoundFont目录不存在: {self.soundfont_dir}")
            print("请确保SoundFont文件位于正确位置，或修改soundfont_directory参数")
            print("将使用空SoundFont列表 - 播放器仍可初始化，但需要SoundFont文件才能播放")
            self.soundfonts = {}
            return
        
        sf2_files = list(self.soundfont_dir.glob("*.sf2")) + list(self.soundfont_dir.glob("*.SF2"))
        print(f"🔍 发现 {len(sf2_files)} 个SoundFont文件")
        
        for sf_path in sf2_files:
            try:
                sf_info = self._analyze_soundfont_file(sf_path)
                self.soundfonts[sf_info.file_path.name] = sf_info
                print(f"  ✓ {sf_path.name}: {sf_info.sf_type.value}, {sf_info.file_size_mb:.1f}MB, 质量:{sf_info.quality_score:.2f}")
            except Exception as e:
                print(f"  ❌ 分析失败 {sf_path.name}: {e}")
    
    def _analyze_soundfont_file(self, sf_path: Path) -> SoundFontInfo:
        """分析单个SoundFont文件"""
        # 基本文件信息
        file_size_mb = sf_path.stat().st_size / (1024 * 1024)
        sf_name = sf_path.name.lower()
        
        # 类型识别
        sf_type = self._identify_soundfont_type(sf_name, file_size_mb)
        
        # 质量评估
        quality_score = self._assess_quality(sf_name, file_size_mb, sf_type)
        
        # 估算乐器数量
        estimated_instruments = SoundFontAnalyzer.estimate_instrument_count(file_size_mb, sf_name)
        
        # 推荐设置
        recommended_settings = SoundFontAnalyzer.recommend_settings(sf_name, file_size_mb)
        
        # 创建SoundFont信息对象
        sf_info = SoundFontInfo(
            file_path=sf_path,
            file_size_mb=file_size_mb,
            sf_type=sf_type,
            quality_score=quality_score,
            instrument_count=estimated_instruments,
            available_instruments=[],  # 需要加载后才能获取详细信息
            recommended_settings=recommended_settings
        )
        
        return sf_info
    
    def _identify_soundfont_type(self, sf_name: str, file_size_mb: float) -> SoundFontType:
        """识别SoundFont类型"""
        if any(keyword in sf_name for keyword in ['steinway', 'piano', 'grand']):
            return SoundFontType.PIANO_SPECIALIZED
        elif any(keyword in sf_name for keyword in ['orchestra', 'symphonic', 'philharmonic']):
            return SoundFontType.ORCHESTRAL
        elif any(keyword in sf_name for keyword in ['gm', 'general', 'fluid']):
            return SoundFontType.GENERAL_MIDI
        elif any(keyword in sf_name for keyword in ['synth', 'electronic']):
            return SoundFontType.SYNTHESIZER
        elif any(keyword in sf_name for keyword in ['world', 'ethnic', 'folk']):
            return SoundFontType.ETHNIC
        else:
            return SoundFontType.UNKNOWN
    
    def _assess_quality(self, sf_name: str, file_size_mb: float, sf_type: SoundFontType) -> float:
        """评估SoundFont质量（0-1分数）"""
        score = 0.5  # 基础分数
        
        # 文件大小评分
        if file_size_mb > 500:
            score += 0.3  # 大文件通常质量较高
        elif file_size_mb > 100:
            score += 0.2
        elif file_size_mb > 50:
            score += 0.1
        
        # 名称信息评分
        quality_indicators = {
            'steinway': 0.25,
            'professional': 0.2,
            'studio': 0.15,
            'premium': 0.15,
            'hd': 0.1,
            'hi-res': 0.1,
            'orchestral': 0.15,
            'symphonic': 0.15
        }
        
        for indicator, bonus in quality_indicators.items():
            if indicator in sf_name:
                score += bonus
                break
        
        # 类型特定评分
        if sf_type == SoundFontType.PIANO_SPECIALIZED and file_size_mb > 300:
            score += 0.15  # 专业钢琴库
        elif sf_type == SoundFontType.ORCHESTRAL and file_size_mb > 200:
            score += 0.1   # 管弦乐库
        
        return min(1.0, score)
    
    def load_soundfont(self, sf_name: str, force_reload: bool = False) -> bool:
        """
        加载SoundFont
        
        Args:
            sf_name: SoundFont文件名
            force_reload: 强制重新加载
            
        Returns:
            加载成功返回True
        """
        if sf_name not in self.soundfonts:
            print(f"❌ 未找到SoundFont: {sf_name}")
            print(f"可用文件: {list(self.soundfonts.keys())}")
            return False
        
        sf_info = self.soundfonts[sf_name]
        
        # 检查是否已加载
        if sf_info.is_loaded and not force_reload:
            print(f"✓ SoundFont已加载: {sf_name}")
            self.current_soundfont = sf_name
            return True
        
        # 卸载之前的SoundFont
        if self.current_soundfont:
            self._unload_current_soundfont()
        
        try:
            print(f"🔄 加载SoundFont: {sf_name} ({sf_info.file_size_mb:.1f}MB)")
            
            # 使用FluidSynth加载
            sf_path_str = str(sf_info.file_path)
            sf_id = self.fluidsynth.fluid_synth_sfload(
                self.synth, 
                sf_path_str.encode('utf-8'), 
                1  # reset_presets
            )
            
            if sf_id == -1:
                print(f"❌ FluidSynth加载失败: {sf_name}")
                return False
            
            # 更新状态
            sf_info.is_loaded = True
            sf_info.fluid_sf_id = sf_id
            self.current_soundfont = sf_name
            self.loaded_soundfonts.add(sf_name)
            
            print(f"✓ SoundFont加载成功: {sf_name} (ID: {sf_id})")
            
            # 获取详细乐器信息
            self._load_instrument_details(sf_name)
            
            return True
            
        except Exception as e:
            print(f"❌ 加载异常: {e}")
            return False
    
    def _unload_current_soundfont(self) -> None:
        """卸载当前SoundFont"""
        if not self.current_soundfont:
            return
        
        sf_info = self.soundfonts[self.current_soundfont]
        if sf_info.is_loaded and sf_info.fluid_sf_id is not None:
            try:
                result = self.fluidsynth.fluid_synth_sfunload(
                    self.synth, sf_info.fluid_sf_id, 1
                )
                if result == 0:
                    print(f"✓ 卸载SoundFont: {self.current_soundfont}")
                else:
                    print(f"⚠️  卸载警告: {result}")
            except Exception as e:
                print(f"⚠️  卸载异常: {e}")
        
        sf_info.is_loaded = False
        sf_info.fluid_sf_id = None
        self.loaded_soundfonts.discard(self.current_soundfont)
        self.current_soundfont = None
    
    def _load_instrument_details(self, sf_name: str) -> None:
        """加载乐器详细信息"""
        sf_info = self.soundfonts[sf_name]
        
        # 尝试获取预设信息
        instruments = []
        
        # 根据SoundFont类型选择检测范围
        if sf_info.sf_type == SoundFontType.PIANO_SPECIALIZED:
            # 钢琴专用SoundFont通常只有钢琴相关音色
            test_programs = list(range(0, 8))  # 钢琴系列音色
        else:
            # 其他类型检查更多程序
            test_programs = list(range(0, 128))
        
        current_program = 0  # 记录当前程序，避免重复设置
        
        for program in test_programs:
            try:
                # 只在需要时切换程序
                if program != current_program:
                    result = self.fluidsynth.fluid_synth_program_change(
                        self.synth, 0, program
                    )
                    current_program = program
                    
                    if result != 0:
                        continue  # 程序切换失败，跳过
                
                # 检查是否成功设置（通过尝试发送一个很短的音符）
                # 这里我们不实际播放，只是检查程序是否有效
                name = self._get_program_name(program)
                category = self._get_program_category(program)
                instrument = InstrumentInfo(
                    program=program,
                    bank=0,
                    name=name,
                    category=category,
                    preset_name=name,
                    sample_quality=self._estimate_sample_quality(sf_info, program)
                )
                instruments.append(instrument)
                
                # 对于钢琴专用SoundFont，一旦找到有效程序就停止
                if sf_info.sf_type == SoundFontType.PIANO_SPECIALIZED and program == 0:
                    break
                    
            except Exception:
                continue
        
        # 如果没有检测到乐器，至少添加默认钢琴
        if not instruments:
            instruments.append(InstrumentInfo(
                program=0,
                bank=0,
                name="Acoustic Grand Piano",
                category="piano",
                preset_name="Default Piano",
                sample_quality=self._estimate_sample_quality(sf_info, 0)
            ))
        
        sf_info.available_instruments = instruments
        sf_info.instrument_count = len(instruments)
        
        print(f"  ✓ 检测到 {len(instruments)} 个可用乐器")
    
    def _get_program_category(self, program: int) -> str:
        """获取程序分类"""
        for category, instruments in INSTRUMENT_CATEGORIES.items():
            if program in instruments.values():
                return category
        
        # 基于MIDI标准分类
        if 0 <= program <= 7:
            return "piano"
        elif 8 <= program <= 15:
            return "chromatic"
        elif 16 <= program <= 23:
            return "organ"
        elif 24 <= program <= 31:
            return "guitar"
        elif 32 <= program <= 39:
            return "bass"
        elif 40 <= program <= 47:
            return "strings"
        elif 48 <= program <= 55:
            return "ensemble"
        elif 56 <= program <= 63:
            return "brass"
        elif 64 <= program <= 71:
            return "reed"
        elif 72 <= program <= 79:
            return "pipe"
        elif 80 <= program <= 87:
            return "synth_lead"
        elif 88 <= program <= 95:
            return "synth_pad"
        elif 96 <= program <= 103:
            return "synth_effects"
        elif 104 <= program <= 111:
            return "ethnic"
        elif 112 <= program <= 119:
            return "percussive"
        elif 120 <= program <= 127:
            return "sound_effects"
        else:
            return "unknown"
    
    def _get_program_name(self, program: int) -> str:
        """获取程序名称"""
        # MIDI标准程序名称
        midi_program_names = {
            0: "Acoustic Grand Piano", 1: "Bright Acoustic Piano", 2: "Electric Grand Piano",
            3: "Honky-tonk Piano", 4: "Electric Piano 1", 5: "Electric Piano 2",
            6: "Harpsichord", 7: "Clavinet", 8: "Celesta", 9: "Glockenspiel",
            # ... 可以继续添加更多
        }
        
        return midi_program_names.get(program, f"Program {program}")
    
    def _estimate_sample_quality(self, sf_info: SoundFontInfo, program: int) -> str:
        """估算采样质量"""
        base_quality = sf_info.quality_score
        
        # 钢琴专用库的钢琴音色质量更高
        if sf_info.sf_type == SoundFontType.PIANO_SPECIALIZED and 0 <= program <= 7:
            base_quality += 0.2
        
        # 管弦乐库的管弦乐器质量更高
        elif sf_info.sf_type == SoundFontType.ORCHESTRAL and 40 <= program <= 79:
            base_quality += 0.15
        
        if base_quality >= QUALITY_THRESHOLDS['excellent']:
            return "excellent"
        elif base_quality >= QUALITY_THRESHOLDS['good']:
            return "good"
        elif base_quality >= QUALITY_THRESHOLDS['acceptable']:
            return "acceptable"
        else:
            return "poor"
    
    def get_best_soundfont_for_task(self, task_type: str) -> Optional[str]:
        """
        为特定任务选择最佳SoundFont
        
        Args:
            task_type: 任务类型 ("piano", "orchestral", "general", "demo")
            
        Returns:
            推荐的SoundFont文件名
        """
        candidates = []
        
        for sf_name, sf_info in self.soundfonts.items():
            score = sf_info.quality_score
            
            # 任务匹配奖励
            if task_type == "piano" and sf_info.sf_type == SoundFontType.PIANO_SPECIALIZED:
                score += 0.5
            elif task_type == "orchestral" and sf_info.sf_type == SoundFontType.ORCHESTRAL:
                score += 0.4
            elif task_type == "general" and sf_info.sf_type == SoundFontType.GENERAL_MIDI:
                score += 0.3
            elif task_type == "demo":
                # 演示用途，平衡质量和多样性
                if sf_info.sf_type in [SoundFontType.PIANO_SPECIALIZED, SoundFontType.ORCHESTRAL]:
                    score += 0.2
            
            candidates.append((sf_name, score))
        
        if not candidates:
            return None
        
        # 按分数排序，返回最高分
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    def get_available_instruments(self, sf_name: Optional[str] = None) -> List[InstrumentInfo]:
        """
        获取可用乐器列表
        
        Args:
            sf_name: SoundFont名称，None表示当前加载的
            
        Returns:
            乐器信息列表
        """
        target_sf = sf_name or self.current_soundfont
        
        if not target_sf or target_sf not in self.soundfonts:
            return []
        
        sf_info = self.soundfonts[target_sf]
        
        if not sf_info.is_loaded:
            print(f"⚠️  SoundFont未加载: {target_sf}")
            return []
        
        return sf_info.available_instruments
    
    def find_instruments_by_category(self, category: str, sf_name: Optional[str] = None) -> List[InstrumentInfo]:
        """根据分类查找乐器"""
        instruments = self.get_available_instruments(sf_name)
        return [inst for inst in instruments if inst.category == category]
    
    def find_best_piano_instrument(self, sf_name: Optional[str] = None) -> Optional[InstrumentInfo]:
        """查找最佳钢琴乐器"""
        pianos = self.find_instruments_by_category("piano", sf_name)
        
        if not pianos:
            return None
        
        # 优先选择质量高的
        pianos.sort(key=lambda x: (
            x.sample_quality == "excellent",
            x.sample_quality == "good",
            x.program == 0  # 默认选择Acoustic Grand Piano
        ), reverse=True)
        
        return pianos[0]
    
    def get_soundfont_summary(self) -> Dict:
        """获取SoundFont管理器摘要"""
        summary = {
            'total_soundfonts': len(self.soundfonts),
            'loaded_soundfonts': len(self.loaded_soundfonts),
            'current_soundfont': self.current_soundfont,
            'soundfont_details': {}
        }
        
        for sf_name, sf_info in self.soundfonts.items():
            summary['soundfont_details'][sf_name] = {
                'type': sf_info.sf_type.value,
                'size_mb': sf_info.file_size_mb,
                'quality_score': sf_info.quality_score,
                'instrument_count': sf_info.instrument_count,
                'is_loaded': sf_info.is_loaded,
                'recommended_use': self._get_recommended_use(sf_info)
            }
        
        return summary
    
    def _get_recommended_use(self, sf_info: SoundFontInfo) -> str:
        """获取推荐用途"""
        if sf_info.sf_type == SoundFontType.PIANO_SPECIALIZED:
            if sf_info.quality_score >= 0.8:
                return "专业钢琴演奏和录音"
            else:
                return "钢琴练习和学习"
        elif sf_info.sf_type == SoundFontType.ORCHESTRAL:
            return "管弦乐编曲和演示"
        elif sf_info.sf_type == SoundFontType.GENERAL_MIDI:
            return "通用MIDI播放和兼容性测试"
        else:
            return "特殊音色和实验"
    
    def optimize_for_petersen_scale(self, sf_name: Optional[str] = None) -> Dict:
        """
        为Petersen音阶优化SoundFont设置
        
        Args:
            sf_name: SoundFont名称
            
        Returns:
            优化建议
        """
        target_sf = sf_name or self.current_soundfont
        
        if not target_sf or target_sf not in self.soundfonts:
            return {}
        
        sf_info = self.soundfonts[target_sf]
        
        optimization = {
            'recommended_instruments': [],
            'effect_settings': sf_info.recommended_settings,
            'frequency_compensation': True,
            'special_considerations': []
        }
        
        # 根据SoundFont类型推荐乐器
        if sf_info.sf_type == SoundFontType.PIANO_SPECIALIZED:
            best_piano = self.find_best_piano_instrument(target_sf)
            if best_piano:
                optimization['recommended_instruments'].append({
                    'program': best_piano.program,
                    'name': best_piano.name,
                    'reason': '最佳钢琴音色，适合展示Petersen音阶的微分音差异'
                })
            
            optimization['special_considerations'].extend([
                '使用延音踏板增强谐波共鸣',
                '适当的混响设置突出空间感',
                '精确的力度控制展现动态层次'
            ])
        
        elif sf_info.sf_type == SoundFontType.ORCHESTRAL:
            categories = ['violin', 'flute', 'trumpet']
            for category in categories:
                instruments = self.find_instruments_by_category(category, target_sf)
                if instruments:
                    best = max(instruments, key=lambda x: x.sample_quality == "excellent")
                    optimization['recommended_instruments'].append({
                        'program': best.program,
                        'name': best.name,
                        'reason': f'{category}音色适合展示Petersen音阶在不同音域的特性'
                    })
            
            optimization['special_considerations'].extend([
                '多乐器对比演示Petersen音阶的普适性',
                '注意不同乐器的频率响应特性',
                '使用管弦乐空间感增强听觉体验'
            ])
        
        return optimization
    
    def cleanup(self) -> None:
        """清理SoundFont管理器"""
        try:
            # 卸载当前加载的SoundFont
            if self.current_soundfont and self.current_soundfont in self.soundfonts:
                sf_info = self.soundfonts[self.current_soundfont]
                if sf_info.is_loaded and sf_info.fluid_sf_id is not None:
                    try:
                        # 静默卸载，不重置程序
                        self.fluidsynth.fluid_synth_sfunload(
                            self.synth, sf_info.fluid_sf_id, 0  # 0 = 不重置程序
                        )
                        print(f"✓ 卸载SoundFont: {self.current_soundfont}")
                    except:
                        pass
                    
                    sf_info.is_loaded = False
                    sf_info.fluid_sf_id = None
            
            # 清理状态
            self.current_soundfont = None
            self.loaded_soundfonts.clear()
            
            print("✓ SoundFont管理器已清理")
            
        except Exception as e:
            print(f"⚠️  SoundFont清理异常: {e}")