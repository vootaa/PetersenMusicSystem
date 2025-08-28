"""
高级音效处理模块
提供混响、合唱、均衡等音效控制，支持内置音效和CC控制器备用方案
"""
import ctypes
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.constants import REVERB_PARAMS, CHORUS_PARAMS, CC_CONTROLLERS

class EffectType(Enum):
    """音效类型枚举"""
    REVERB = "reverb"
    CHORUS = "chorus"
    BRIGHTNESS = "brightness"
    RESONANCE = "resonance"
    EXPRESSION = "expression"

@dataclass
class EffectSettings:
    """音效设置数据类"""
    reverb_room_size: float = 0.2
    reverb_damping: float = 0.0
    reverb_width: float = 0.5
    reverb_level: float = 0.9
    
    chorus_voices: int = 3
    chorus_level: float = 2.0
    chorus_speed: float = 0.3
    chorus_depth: float = 8.0
    chorus_type: int = 0
    
    brightness: int = 64
    resonance: int = 64
    expression: int = 127
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'reverb': {
                'room_size': self.reverb_room_size,
                'damping': self.reverb_damping,
                'width': self.reverb_width,
                'level': self.reverb_level
            },
            'chorus': {
                'voices': self.chorus_voices,
                'level': self.chorus_level,
                'speed': self.chorus_speed,
                'depth': self.chorus_depth,
                'type': self.chorus_type
            },
            'controls': {
                'brightness': self.brightness,
                'resonance': self.resonance,
                'expression': self.expression
            }
        }

class AdvancedAudioEffects:
    """高级音效处理控制器"""
    
    def __init__(self, fluidsynth_lib, synth, current_channel: int = 0):
        """
        初始化音效处理器
        
        Args:
            fluidsynth_lib: FluidSynth动态库对象
            synth: FluidSynth合成器对象
            current_channel: 当前MIDI通道
        """
        self.fluidsynth = fluidsynth_lib
        self.synth = synth
        self.current_channel = current_channel
        
        # 检测功能支持
        self.has_builtin_reverb = self._check_builtin_reverb()
        self.has_builtin_chorus = self._check_builtin_chorus()
        self.has_cc_support = True  # CC控制器通常都支持
        
        # 当前音效设置
        self.current_settings = EffectSettings()
        
        # 音效预设
        self.presets = self._create_effect_presets()
        
        print(f"✓ 音效支持检测:")
        print(f"  - 内置混响: {'✓' if self.has_builtin_reverb else '✗'}")
        print(f"  - 内置合唱: {'✓' if self.has_builtin_chorus else '✗'}")
        print(f"  - CC控制器: {'✓' if self.has_cc_support else '✗'}")
    
    def _check_builtin_reverb(self) -> bool:
        """检测内置混响支持"""
        try:
            if hasattr(self.fluidsynth, 'fluid_synth_set_reverb'):
                # 尝试设置默认混响参数
                result = self.fluidsynth.fluid_synth_set_reverb(
                    self.synth, 0.2, 0.0, 0.5, 0.9
                )
                return result == 0
        except (AttributeError, ctypes.ArgumentError):
            pass
        return False
    
    def _check_builtin_chorus(self) -> bool:
        """检测内置合唱支持"""
        try:
            if hasattr(self.fluidsynth, 'fluid_synth_set_chorus'):
                # 尝试设置默认合唱参数
                result = self.fluidsynth.fluid_synth_set_chorus(
                    self.synth, 3, 2.0, 0.3, 8.0, 0
                )
                return result == 0
        except (AttributeError, ctypes.ArgumentError):
            pass
        return False
    
    def _create_effect_presets(self) -> Dict[str, EffectSettings]:
        """创建音效预设"""
        presets = {
            'dry': EffectSettings(
                reverb_level=0.0, chorus_level=0.0,
                brightness=64, resonance=40
            ),
            
            'hall': EffectSettings(
                reverb_room_size=0.8, reverb_damping=0.1, 
                reverb_width=1.0, reverb_level=0.7,
                chorus_level=0.5, brightness=70, resonance=55
            ),
            
            'chamber': EffectSettings(
                reverb_room_size=0.4, reverb_damping=0.2,
                reverb_width=0.6, reverb_level=0.6,
                chorus_level=1.0, brightness=65, resonance=60
            ),
            
            'cathedral': EffectSettings(
                reverb_room_size=0.9, reverb_damping=0.05,
                reverb_width=1.0, reverb_level=0.8,
                chorus_level=0.3, brightness=75, resonance=50
            ),
            
            'intimate': EffectSettings(
                reverb_room_size=0.2, reverb_damping=0.3,
                reverb_width=0.4, reverb_level=0.4,
                chorus_level=1.5, brightness=60, resonance=65
            ),
            
            'bright': EffectSettings(
                reverb_room_size=0.3, reverb_damping=0.1,
                reverb_width=0.7, reverb_level=0.5,
                chorus_level=2.0, brightness=90, resonance=45
            ),
            
            'warm': EffectSettings(
                reverb_room_size=0.5, reverb_damping=0.4,
                reverb_width=0.8, reverb_level=0.6,
                chorus_level=1.0, brightness=45, resonance=70
            ),
            
            'steinway_concert': EffectSettings(
                reverb_room_size=0.6, reverb_damping=0.15,
                reverb_width=0.9, reverb_level=0.5,
                chorus_level=0.2, brightness=75, resonance=55
            ),
            
            'orchestral': EffectSettings(
                reverb_room_size=0.7, reverb_damping=0.2,
                reverb_width=1.0, reverb_level=0.8,
                chorus_level=1.5, brightness=68, resonance=58
            )
        }
        
        return presets
    
    def apply_effect_preset(self, preset_name: str) -> bool:
        """
        应用音效预设
        
        Args:
            preset_name: 预设名称
            
        Returns:
            应用成功返回True
        """
        if preset_name not in self.presets:
            print(f"❌ 未知预设: {preset_name}")
            print(f"可用预设: {list(self.presets.keys())}")
            return False
        
        settings = self.presets[preset_name]
        return self.apply_effect_settings(settings)
    
    def apply_effect_settings(self, settings: EffectSettings) -> bool:
        """
        应用音效设置
        
        Args:
            settings: 音效设置对象
            
        Returns:
            应用成功返回True
        """
        success = True
        
        # 应用混响
        if not self._apply_reverb(settings):
            success = False
        
        # 应用合唱
        if not self._apply_chorus(settings):
            success = False
        
        # 应用控制器参数
        if not self._apply_control_parameters(settings):
            success = False
        
        if success:
            self.current_settings = settings
            print(f"✓ 音效设置已应用")
        
        return success
    
    def _apply_reverb(self, settings: EffectSettings) -> bool:
        """应用混响设置"""
        try:
            if self.has_builtin_reverb:
                # 使用内置混响API
                result = self.fluidsynth.fluid_synth_set_reverb(
                    self.synth,
                    ctypes.c_double(settings.reverb_room_size),
                    ctypes.c_double(settings.reverb_damping),
                    ctypes.c_double(settings.reverb_width),
                    ctypes.c_double(settings.reverb_level)
                )
                
                if result == 0:
                    print(f"  ✓ 内置混响: 房间={settings.reverb_room_size:.1f}, "
                          f"阻尼={settings.reverb_damping:.1f}, 级别={settings.reverb_level:.1f}")
                    return True
                else:
                    print(f"  ⚠️  内置混响设置失败: {result}")
            
            # 备用方案：使用CC控制器
            if self.has_cc_support:
                reverb_cc_value = int(settings.reverb_level * 127)
                result = self.fluidsynth.fluid_synth_cc(
                    self.synth, self.current_channel, 
                    CC_CONTROLLERS['reverb_send'], reverb_cc_value
                )
                
                if result == 0:
                    print(f"  ✓ CC混响: 级别={reverb_cc_value}")
                    return True
                else:
                    print(f"  ⚠️  CC混响设置失败: {result}")
            
        except Exception as e:
            print(f"  ❌ 混响设置异常: {e}")
        
        return False
    
    def _apply_chorus(self, settings: EffectSettings) -> bool:
        """应用合唱设置"""
        try:
            if self.has_builtin_chorus:
                # 使用内置合唱API
                result = self.fluidsynth.fluid_synth_set_chorus(
                    self.synth,
                    ctypes.c_int(settings.chorus_voices),
                    ctypes.c_double(settings.chorus_level),
                    ctypes.c_double(settings.chorus_speed),
                    ctypes.c_double(settings.chorus_depth),
                    ctypes.c_int(settings.chorus_type)
                )
                
                if result == 0:
                    print(f"  ✓ 内置合唱: 声部={settings.chorus_voices}, "
                          f"级别={settings.chorus_level:.1f}, 深度={settings.chorus_depth:.1f}")
                    return True
                else:
                    print(f"  ⚠️  内置合唱设置失败: {result}")
            
            # 备用方案：使用CC控制器
            if self.has_cc_support:
                chorus_cc_value = int(min(settings.chorus_level / 10.0 * 127, 127))
                result = self.fluidsynth.fluid_synth_cc(
                    self.synth, self.current_channel,
                    CC_CONTROLLERS['chorus_send'], chorus_cc_value
                )
                
                if result == 0:
                    print(f"  ✓ CC合唱: 级别={chorus_cc_value}")
                    return True
                else:
                    print(f"  ⚠️  CC合唱设置失败: {result}")
            
        except Exception as e:
            print(f"  ❌ 合唱设置异常: {e}")
        
        return False
    
    def _apply_control_parameters(self, settings: EffectSettings) -> bool:
        """应用控制器参数"""
        if not self.has_cc_support:
            return False
        
        controls = [
            ('brightness', settings.brightness),
            ('resonance', settings.resonance),
            ('expression', settings.expression)
        ]
        
        success_count = 0
        
        for control_name, value in controls:
            try:
                cc_number = CC_CONTROLLERS[control_name]
                result = self.fluidsynth.fluid_synth_cc(
                    self.synth, self.current_channel, cc_number, value
                )
                
                if result == 0:
                    success_count += 1
                else:
                    print(f"  ⚠️  {control_name}设置失败: {result}")
                    
            except Exception as e:
                print(f"  ❌ {control_name}设置异常: {e}")
        
        if success_count > 0:
            print(f"  ✓ 控制参数: 亮度={settings.brightness}, "
                  f"共振={settings.resonance}, 表现力={settings.expression}")
        
        return success_count == len(controls)
    
    def set_sustain_pedal(self, pressed: bool) -> bool:
        """
        设置延音踏板
        
        Args:
            pressed: True为按下，False为释放
            
        Returns:
            设置成功返回True
        """
        try:
            value = 127 if pressed else 0
            result = self.fluidsynth.fluid_synth_cc(
                self.synth, self.current_channel, 
                CC_CONTROLLERS['sustain_pedal'], value
            )
            
            if result == 0:
                status = "按下" if pressed else "释放"
                print(f"  ✓ 延音踏板{status}")
                return True
            else:
                print(f"  ⚠️  延音踏板设置失败: {result}")
                
        except Exception as e:
            print(f"  ❌ 延音踏板异常: {e}")
        
        return False
    
    def set_soft_pedal(self, pressed: bool) -> bool:
        """设置弱音踏板"""
        try:
            value = 127 if pressed else 0
            result = self.fluidsynth.fluid_synth_cc(
                self.synth, self.current_channel,
                CC_CONTROLLERS['soft_pedal'], value
            )
            
            if result == 0:
                status = "按下" if pressed else "释放"
                print(f"  ✓ 弱音踏板{status}")
                return True
            else:
                print(f"  ⚠️  弱音踏板设置失败: {result}")
                
        except Exception as e:
            print(f"  ❌ 弱音踏板异常: {e}")
        
        return False
    
    def create_custom_preset(self, name: str, **kwargs) -> EffectSettings:
        """
        创建自定义音效预设
        
        Args:
            name: 预设名称
            **kwargs: 音效参数
            
        Returns:
            创建的EffectSettings对象
        """
        # 从当前设置开始
        settings = EffectSettings(
            reverb_room_size=self.current_settings.reverb_room_size,
            reverb_damping=self.current_settings.reverb_damping,
            reverb_width=self.current_settings.reverb_width,
            reverb_level=self.current_settings.reverb_level,
            chorus_voices=self.current_settings.chorus_voices,
            chorus_level=self.current_settings.chorus_level,
            chorus_speed=self.current_settings.chorus_speed,
            chorus_depth=self.current_settings.chorus_depth,
            chorus_type=self.current_settings.chorus_type,
            brightness=self.current_settings.brightness,
            resonance=self.current_settings.resonance,
            expression=self.current_settings.expression
        )
        
        # 应用自定义参数
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
            else:
                print(f"⚠️  未知参数: {key}")
        
        # 保存预设
        self.presets[name] = settings
        print(f"✓ 自定义预设 '{name}' 已创建")
        
        return settings
    
    def get_available_presets(self) -> List[str]:
        """获取可用预设列表"""
        return list(self.presets.keys())
    
    def get_current_settings(self) -> Dict:
        """获取当前音效设置"""
        return self.current_settings.to_dict()
    
    def optimize_for_soundfont(self, sf_name: str, sf_size_mb: float) -> bool:
        """
        根据SoundFont特性优化音效
        
        Args:
            sf_name: SoundFont文件名
            sf_size_mb: 文件大小(MB)
            
        Returns:
            优化成功返回True
        """
        preset_name = 'dry'  # 默认预设
        
        if 'steinway' in sf_name.lower():
            if sf_size_mb > 500:
                preset_name = 'steinway_concert'
            else:
                preset_name = 'hall'
        elif 'orchestra' in sf_name.lower() or 'symphonic' in sf_name.lower():
            preset_name = 'orchestral'
        elif sf_size_mb > 100:
            preset_name = 'chamber'
        else:
            preset_name = 'intimate'
        
        print(f"🎵 为 {sf_name} 选择音效预设: {preset_name}")
        return self.apply_effect_preset(preset_name)
    
    def analyze_effect_impact(self, frequencies: List[float]) -> Dict:
        """
        分析音效对频率响应的影响
        
        Args:
            frequencies: 频率列表
            
        Returns:
            影响分析结果
        """
        if not frequencies:
            return {}
        
        freq_range = (min(frequencies), max(frequencies))
        settings = self.current_settings
        
        # 分析混响影响
        reverb_impact = {
            'low_freq_enhancement': settings.reverb_room_size * 0.3,  # 低频增强
            'high_freq_damping': settings.reverb_damping * 0.4,      # 高频衰减
            'spatial_width': settings.reverb_width,                   # 空间感
            'overall_wetness': settings.reverb_level                  # 湿度
        }
        
        # 分析合唱影响
        chorus_impact = {
            'frequency_spreading': settings.chorus_depth * 0.01,      # 频率扩散
            'amplitude_modulation': settings.chorus_speed * 0.1,      # 幅度调制
            'stereo_enhancement': settings.chorus_level * 0.05,       # 立体声增强
            'harmonic_richness': settings.chorus_voices * 0.1         # 谐波丰富度
        }
        
        return {
            'frequency_range': freq_range,
            'current_preset': self._find_current_preset(),
            'reverb_impact': reverb_impact,
            'chorus_impact': chorus_impact,
            'brightness_adjustment': (settings.brightness - 64) / 64.0,
            'resonance_adjustment': (settings.resonance - 64) / 64.0,
            'recommended_adjustments': self._recommend_frequency_adjustments(frequencies)
        }
    
    def _find_current_preset(self) -> Optional[str]:
        """查找当前设置对应的预设名称"""
        current_dict = self.current_settings.to_dict()
        
        for preset_name, preset_settings in self.presets.items():
            preset_dict = preset_settings.to_dict()
            if self._settings_match(current_dict, preset_dict):
                return preset_name
        
        return "custom"
    
    def _settings_match(self, settings1: Dict, settings2: Dict, tolerance: float = 0.05) -> bool:
        """检查两个设置是否匹配"""
        for category in ['reverb', 'chorus', 'controls']:
            if category not in settings1 or category not in settings2:
                continue
            
            for param, value1 in settings1[category].items():
                value2 = settings2[category].get(param, 0)
                
                if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    if abs(value1 - value2) > tolerance * max(abs(value1), abs(value2), 1):
                        return False
        
        return True
    
    def _recommend_frequency_adjustments(self, frequencies: List[float]) -> Dict:
        """为特定频率范围推荐调整"""
        if not frequencies:
            return {}
        
        min_freq, max_freq = min(frequencies), max(frequencies)
        
        recommendations = {}
        
        # 低频建议
        if min_freq < 100:
            recommendations['low_frequency'] = {
                'suggestion': '增加混响房间大小以增强低频',
                'reverb_room_size': min(1.0, self.current_settings.reverb_room_size + 0.2)
            }
        
        # 高频建议
        if max_freq > 2000:
            recommendations['high_frequency'] = {
                'suggestion': '适当降低亮度以避免刺耳',
                'brightness': max(30, self.current_settings.brightness - 15)
            }
        
        # 中频建议
        if 200 <= min_freq <= 800 and 800 <= max_freq <= 1500:
            recommendations['mid_frequency'] = {
                'suggestion': '增加共振以增强中频表现力',
                'resonance': min(100, self.current_settings.resonance + 10)
            }
        
        return recommendations