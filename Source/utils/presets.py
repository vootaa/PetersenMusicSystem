"""
预设配置文件
包含各种预定义的音效、表现力和演奏设置组合
"""
from typing import Dict, Any, List
from dataclasses import dataclass

import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from constants import REVERB_PARAMS, CHORUS_PARAMS

@dataclass
class CompletePreset:
    """完整预设（包含音效+表现力+乐器选择）"""
    name: str
    description: str
    effect_preset: str
    expression_preset: str
    recommended_instruments: List[int]
    soundfont_preferences: List[str]
    use_cases: List[str]

# ========== 音效预设库 ==========

EFFECT_PRESET_LIBRARY = {
    # 古典音乐厅系列
    'vienna_musikverein': {
        'description': '维也纳音乐厅的声学特性',
        'reverb': {'room_size': 0.85, 'damping': 0.12, 'width': 0.95, 'level': 0.75},
        'chorus': {'voices': 2, 'level': 0.8, 'speed': 0.25, 'depth': 6.0},
        'brightness': 72, 'resonance': 58, 'expression': 120
    },
    
    'carnegie_hall': {
        'description': '卡内基音乐厅的温暖音色',
        'reverb': {'room_size': 0.78, 'damping': 0.18, 'width': 0.88, 'level': 0.68},
        'chorus': {'voices': 3, 'level': 1.2, 'speed': 0.28, 'depth': 7.5},
        'brightness': 68, 'resonance': 62, 'expression': 115
    },
    
    'berlin_philharmonie': {
        'description': '柏林爱乐音乐厅的现代声学',
        'reverb': {'room_size': 0.72, 'damping': 0.15, 'width': 0.92, 'level': 0.7},
        'chorus': {'voices': 2, 'level': 1.0, 'speed': 0.3, 'depth': 8.0},
        'brightness': 75, 'resonance': 55, 'expression': 118
    },
    
    # 室内乐空间系列
    'intimate_salon': {
        'description': '19世纪沙龙的亲密氛围',
        'reverb': {'room_size': 0.25, 'damping': 0.3, 'width': 0.5, 'level': 0.4},
        'chorus': {'voices': 4, 'level': 1.8, 'speed': 0.35, 'depth': 9.0},
        'brightness': 62, 'resonance': 68, 'expression': 110
    },
    
    'chamber_recital': {
        'description': '室内乐演奏厅',
        'reverb': {'room_size': 0.45, 'damping': 0.22, 'width': 0.65, 'level': 0.55},
        'chorus': {'voices': 3, 'level': 1.3, 'speed': 0.32, 'depth': 7.8},
        'brightness': 65, 'resonance': 63, 'expression': 112
    },
    
    # 教堂和大教堂系列
    'gothic_cathedral': {
        'description': '哥特式大教堂的宏伟混响',
        'reverb': {'room_size': 0.95, 'damping': 0.05, 'width': 1.0, 'level': 0.85},
        'chorus': {'voices': 1, 'level': 0.3, 'speed': 0.2, 'depth': 4.0},
        'brightness': 78, 'resonance': 45, 'expression': 125
    },
    
    'baroque_church': {
        'description': '巴洛克教堂的清澈回响',
        'reverb': {'room_size': 0.68, 'damping': 0.08, 'width': 0.85, 'level': 0.72},
        'chorus': {'voices': 2, 'level': 0.6, 'speed': 0.22, 'depth': 5.5},
        'brightness': 82, 'resonance': 48, 'expression': 122
    },
    
    # 现代录音室系列
    'studio_close_mic': {
        'description': '录音室近距离拾音',
        'reverb': {'room_size': 0.15, 'damping': 0.4, 'width': 0.3, 'level': 0.2},
        'chorus': {'voices': 0, 'level': 0.0, 'speed': 0.0, 'depth': 0.0},
        'brightness': 58, 'resonance': 45, 'expression': 105
    },
    
    'studio_ambient': {
        'description': '录音室环境拾音',
        'reverb': {'room_size': 0.35, 'damping': 0.25, 'width': 0.6, 'level': 0.45},
        'chorus': {'voices': 2, 'level': 0.8, 'speed': 0.28, 'depth': 6.0},
        'brightness': 65, 'resonance': 52, 'expression': 108
    },
    
    # 特殊环境系列
    'jazz_club': {
        'description': '爵士俱乐部的温馨氛围',
        'reverb': {'room_size': 0.3, 'damping': 0.35, 'width': 0.45, 'level': 0.35},
        'chorus': {'voices': 4, 'level': 2.2, 'speed': 0.4, 'depth': 10.0},
        'brightness': 58, 'resonance': 72, 'expression': 95
    },
    
    'concert_stage': {
        'description': '露天音乐会舞台',
        'reverb': {'room_size': 0.5, 'damping': 0.4, 'width': 0.8, 'level': 0.3},
        'chorus': {'voices': 3, 'level': 1.5, 'speed': 0.33, 'depth': 8.5},
        'brightness': 75, 'resonance': 50, 'expression': 118
    }
}

# ========== 表现力预设库 ==========

EXPRESSION_PRESET_LIBRARY = {
    # 古典时期风格
    'mozart_elegance': {
        'description': '莫扎特式的优雅和精确',
        'dynamic_pattern': 'terraced',
        'timing_style': 'mechanical',
        'velocity_base': 85, 'velocity_range': (70, 100),
        'duration_variance': 0.02, 'gap_variance': 0.01,
        'use_sustain_pedal': True, 'sustain_probability': 0.15,
        'phrase_shaping': True, 'microtiming_deviation': 0.005
    },
    
    'haydn_wit': {
        'description': '海顿式的机智和幽默',
        'dynamic_pattern': 'accent',
        'timing_style': 'mechanical',
        'velocity_base': 88, 'velocity_range': (75, 110),
        'duration_variance': 0.05, 'gap_variance': 0.03,
        'use_sustain_pedal': True, 'sustain_probability': 0.2,
        'accent_beats': [0, 2], 'phrase_shaping': True
    },
    
    # 浪漫主义风格
    'chopin_poetry': {
        'description': '肖邦式的诗意和细腻',
        'dynamic_pattern': 'wave',
        'timing_style': 'rubato',
        'velocity_base': 72, 'velocity_range': (35, 115),
        'duration_variance': 0.25, 'gap_variance': 0.12,
        'use_sustain_pedal': True, 'sustain_probability': 0.7,
        'phrase_shaping': True, 'microtiming_deviation': 0.08
    },
    
    'liszt_virtuosity': {
        'description': '李斯特式的炫技和激情',
        'dynamic_pattern': 'arch',
        'timing_style': 'rubato',
        'velocity_base': 105, 'velocity_range': (60, 127),
        'duration_variance': 0.2, 'gap_variance': 0.08,
        'use_sustain_pedal': True, 'sustain_probability': 0.8,
        'phrase_shaping': True, 'microtiming_deviation': 0.06
    },
    
    'schumann_dreamy': {
        'description': '舒曼式的梦幻和内省',
        'dynamic_pattern': 'wave',
        'timing_style': 'rubato',
        'velocity_base': 68, 'velocity_range': (45, 90),
        'duration_variance': 0.18, 'gap_variance': 0.1,
        'use_sustain_pedal': True, 'sustain_probability': 0.6,
        'use_soft_pedal': True, 'phrase_shaping': True
    },
    
    # 印象主义风格
    'debussy_impressionist': {
        'description': '德彪西式的印象主义色彩',
        'dynamic_pattern': 'wave',
        'timing_style': 'rubato',
        'velocity_base': 65, 'velocity_range': (40, 85),
        'duration_variance': 0.22, 'gap_variance': 0.15,
        'use_sustain_pedal': True, 'sustain_probability': 0.9,
        'phrase_shaping': True, 'microtiming_deviation': 0.1
    },
    
    'ravel_crystalline': {
        'description': '拉威尔式的晶莹剔透',
        'dynamic_pattern': 'arch',
        'timing_style': 'mechanical',
        'velocity_base': 78, 'velocity_range': (55, 95),
        'duration_variance': 0.08, 'gap_variance': 0.04,
        'use_sustain_pedal': True, 'sustain_probability': 0.4,
        'phrase_shaping': True, 'microtiming_deviation': 0.02
    },
    
    # 现代风格
    'minimalist_reich': {
        'description': '史蒂夫·赖希式的极简主义',
        'dynamic_pattern': 'linear',
        'timing_style': 'mechanical',
        'velocity_base': 82, 'velocity_range': (78, 86),
        'duration_variance': 0.0, 'gap_variance': 0.0,
        'phrase_shaping': False, 'microtiming_deviation': 0.0
    },
    
    'jazz_swing': {
        'description': '爵士摇摆风格',
        'dynamic_pattern': 'accent',
        'timing_style': 'swing',
        'velocity_base': 92, 'velocity_range': (70, 120),
        'duration_variance': 0.3, 'gap_variance': 0.2,
        'accent_beats': [0, 2], 'microtiming_deviation': 0.12
    }
}

# ========== 完整预设组合 ==========

COMPLETE_PRESET_COMBINATIONS = {
    'steinway_concert_grand': CompletePreset(
        name='Steinway音乐会三角钢琴',
        description='专业音乐会演出设置，适合古典和浪漫主义作品',
        effect_preset='vienna_musikverein',
        expression_preset='chopin_poetry',
        recommended_instruments=[0, 1],  # Acoustic Grand, Bright Acoustic
        soundfont_preferences=['steinway', 'piano'],
        use_cases=['古典音乐会', '浪漫主义作品', '专业演出']
    ),
    
    'chamber_music_intimate': CompletePreset(
        name='室内乐亲密演奏',
        description='小型室内乐空间的精致演奏',
        effect_preset='intimate_salon',
        expression_preset='mozart_elegance',
        recommended_instruments=[0, 40, 73],  # Piano, Violin, Flute
        soundfont_preferences=['orchestral', 'chamber'],
        use_cases=['室内乐', '沙龙音乐会', '小型演出']
    ),
    
    'orchestral_symphonic': CompletePreset(
        name='交响乐团演奏',
        description='大型交响乐团的宏伟演出',
        effect_preset='berlin_philharmonie',
        expression_preset='liszt_virtuosity',
        recommended_instruments=[40, 41, 42, 73, 56, 60],  # Strings, Winds, Brass
        soundfont_preferences=['orchestral', 'symphonic'],
        use_cases=['交响音乐会', '大型作品', '管弦乐']
    ),
    
    'jazz_club_session': CompletePreset(
        name='爵士俱乐部演出',
        description='爵士俱乐部的轻松演奏',
        effect_preset='jazz_club',
        expression_preset='jazz_swing',
        recommended_instruments=[4, 32, 56],  # Electric Piano, Bass, Trumpet
        soundfont_preferences=['jazz', 'electric'],
        use_cases=['爵士演出', '即兴演奏', '轻松娱乐']
    ),
    
    'cathedral_sacred': CompletePreset(
        name='教堂圣乐演奏',
        description='教堂圣乐的庄严演出',
        effect_preset='gothic_cathedral',
        expression_preset='debussy_impressionist',
        recommended_instruments=[19, 73, 52],  # Church Organ, Flute, Choir
        soundfont_preferences=['organ', 'choir'],
        use_cases=['宗教音乐', '教堂演出', '圣乐']
    ),
    
    'studio_recording': CompletePreset(
        name='录音室录制',
        description='专业录音室的精确录制',
        effect_preset='studio_close_mic',
        expression_preset='ravel_crystalline',
        recommended_instruments=[0, 1],  # High-quality piano
        soundfont_preferences=['studio', 'high_quality'],
        use_cases=['录音制作', '精确演奏', '音频制作']
    ),
    
    'educational_demo': CompletePreset(
        name='教学演示',
        description='教育用途的清晰演示',
        effect_preset='chamber_recital',
        expression_preset='haydn_wit',
        recommended_instruments=[0],  # Simple piano
        soundfont_preferences=['general', 'clear'],
        use_cases=['音乐教学', '理论演示', '学习辅助']
    ),
    
    'experimental_modern': CompletePreset(
        name='现代实验音乐',
        description='现代音乐的实验性演奏',
        effect_preset='concert_stage',
        expression_preset='minimalist_reich',
        recommended_instruments=[80, 81, 88],  # Synth leads and pads
        soundfont_preferences=['synth', 'modern'],
        use_cases=['现代音乐', '实验音乐', '电子音乐']
    )
}

# ========== 预设推荐系统 ==========

def recommend_preset_for_context(context_type: str, 
                                 scale_characteristics: Dict = None,
                                 available_soundfonts: List[str] = None) -> str:
    """
    根据上下文推荐预设
    
    Args:
        context_type: 上下文类型 ('concert', 'study', 'demo', 'recording', etc.)
        scale_characteristics: 音阶特性分析结果
        available_soundfonts: 可用的SoundFont列表
        
    Returns:
        推荐的预设名称
    """
    
    # 基于上下文的基础推荐
    context_mapping = {
        'concert': 'steinway_concert_grand',
        'recital': 'chamber_music_intimate',
        'study': 'educational_demo',
        'demo': 'educational_demo',
        'recording': 'studio_recording',
        'orchestral': 'orchestral_symphonic',
        'jazz': 'jazz_club_session',
        'sacred': 'cathedral_sacred',
        'modern': 'experimental_modern'
    }
    
    base_recommendation = context_mapping.get(context_type, 'educational_demo')
    
    # 根据可用SoundFont调整推荐
    if available_soundfonts:
        preset = COMPLETE_PRESET_COMBINATIONS[base_recommendation]
        
        # 检查SoundFont兼容性
        sf_names_lower = [sf.lower() for sf in available_soundfonts]
        
        for pref in preset.soundfont_preferences:
            if any(pref in sf_name for sf_name in sf_names_lower):
                return base_recommendation
        
        # 如果没有匹配的，寻找备选方案
        for preset_name, preset_info in COMPLETE_PRESET_COMBINATIONS.items():
            for pref in preset_info.soundfont_preferences:
                if any(pref in sf_name for sf_name in sf_names_lower):
                    return preset_name
    
    return base_recommendation

def get_preset_variations(base_preset_name: str) -> List[Dict]:
    """
    获取预设的变体
    
    Args:
        base_preset_name: 基础预设名称
        
    Returns:
        预设变体列表
    """
    if base_preset_name not in COMPLETE_PRESET_COMBINATIONS:
        return []
    
    base_preset = COMPLETE_PRESET_COMBINATIONS[base_preset_name]
    variations = []
    
    # 创建音效变体
    for effect_name in EFFECT_PRESET_LIBRARY:
        if effect_name != base_preset.effect_preset:
            variations.append({
                'name': f"{base_preset.name} + {effect_name}",
                'type': 'effect_variation',
                'effect_preset': effect_name,
                'expression_preset': base_preset.expression_preset,
                'description': f"{base_preset.description} 配合 {EFFECT_PRESET_LIBRARY[effect_name]['description']}"
            })
    
    # 创建表现力变体
    for expr_name in EXPRESSION_PRESET_LIBRARY:
        if expr_name != base_preset.expression_preset:
            variations.append({
                'name': f"{base_preset.name} + {expr_name}",
                'type': 'expression_variation',
                'effect_preset': base_preset.effect_preset,
                'expression_preset': expr_name,
                'description': f"{base_preset.description} 配合 {EXPRESSION_PRESET_LIBRARY[expr_name]['description']}"
            })
    
    return variations

def analyze_preset_suitability(preset_name: str, 
                              frequency_range: Tuple[float, float],
                              note_count: int) -> Dict:
    """
    分析预设对特定音乐内容的适用性
    
    Args:
        preset_name: 预设名称
        frequency_range: 频率范围
        note_count: 音符数量
        
    Returns:
        适用性分析结果
    """
    if preset_name not in COMPLETE_PRESET_COMBINATIONS:
        return {'suitable': False, 'reason': '预设不存在'}
    
    preset = COMPLETE_PRESET_COMBINATIONS[preset_name]
    analysis = {'suitable': True, 'score': 1.0, 'recommendations': []}
    
    min_freq, max_freq = frequency_range
    
    # 频率范围分析
    if min_freq < 80:  # 极低频
        if 'intimate' in preset.effect_preset or 'close' in preset.effect_preset:
            analysis['score'] *= 0.8
            analysis['recommendations'].append('低频内容建议使用大空间混响')
    
    if max_freq > 4000:  # 极高频
        if 'cathedral' in preset.effect_preset:
            analysis['score'] *= 0.7
            analysis['recommendations'].append('高频内容在大空间可能过于刺耳')
    
    # 音符数量分析
    if note_count > 50:  # 长序列
        expr_preset = EXPRESSION_PRESET_LIBRARY.get(preset.expression_preset, {})
        if expr_preset.get('microtiming_deviation', 0) > 0.05:
            analysis['score'] *= 0.9
            analysis['recommendations'].append('长序列建议减少微调时间变化')
    
    if note_count < 10:  # 短序列
        if 'mechanical' in preset.expression_preset:
            analysis['score'] *= 0.8
            analysis['recommendations'].append('短序列建议增加表现力变化')
    
    # 设置适用性等级
    if analysis['score'] >= 0.9:
        analysis['suitability'] = 'excellent'
    elif analysis['score'] >= 0.7:
        analysis['suitability'] = 'good'
    elif analysis['score'] >= 0.5:
        analysis['suitability'] = 'acceptable'
    else:
        analysis['suitability'] = 'poor'
    
    return analysis