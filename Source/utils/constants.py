"""
Enhanced Petersen Player 常量定义
"""

# MIDI 相关常量
MIDI_NOTE_COUNT = 128
PITCH_BEND_NEUTRAL = 8192
PITCH_BEND_RANGE = 8192
CENTS_PER_SEMITONE = 100
CENTS_PER_OCTAVE = 1200

# 频率补偿阈值
FREQUENCY_TOLERANCE_CENTS = 5.0  # 超过5音分才使用弯音轮补偿
MAX_PITCH_BEND_CENTS = 200.0     # 弯音轮最大补偿范围

# SoundFont 路径配置
DEFAULT_SOUNDFONTS = {
    'steinway_d274_ii': '[GD] Steinway Model D274 II.sf2',
    'steinway_d274': '[GD] Steinway Model D274.sf2', 
    'sonatina_orchestra': 'Sonatina_Symphonic_Orchestra.sf2',
    'fluidr3_gm': 'FluidR3_GM.sf2'
}

# 音效参数范围
REVERB_PARAMS = {
    'room_size': (0.0, 1.0, 0.2),    # (min, max, default)
    'damping': (0.0, 1.0, 0.0),
    'width': (0.0, 100.0, 0.5),
    'level': (0.0, 1.0, 0.9)
}

CHORUS_PARAMS = {
    'voices': (0, 99, 3),
    'level': (0.0, 10.0, 2.0),
    'speed': (0.29, 5.0, 0.3),
    'depth': (0.0, 21.0, 8.0),
    'type': (0, 1, 0)  # 0=sine, 1=triangle
}

# 表现力控制参数
VELOCITY_CURVES = {
    'linear': lambda x: x,
    'exponential': lambda x: x ** 2,
    'logarithmic': lambda x: x ** 0.5,
    'sigmoid': lambda x: 1 / (1 + pow(2.718, -6 * (x - 0.5)))
}

DYNAMIC_PATTERNS = {
    'crescendo': 'gradually_increase',
    'diminuendo': 'gradually_decrease', 
    'arch': 'increase_then_decrease',
    'wave': 'oscillate',
    'accent': 'emphasize_beats'
}

# CC 控制器映射
CC_CONTROLLERS = {
    'volume': 7,
    'expression': 11,
    'sustain_pedal': 64,
    'sostenuto_pedal': 66,
    'soft_pedal': 67,
    'reverb_send': 91,
    'chorus_send': 93,
    'brightness': 74,
    'resonance': 71,
    'attack_time': 73,
    'release_time': 72
}

# 乐器分类
INSTRUMENT_CATEGORIES = {
    'piano': {
        'acoustic_grand': 0,
        'bright_acoustic': 1,
        'electric_grand': 2,
        'honky_tonk': 3,
        'electric_piano_1': 4,
        'electric_piano_2': 5,
        'harpsichord': 6,
        'clavinet': 7
    },
    'strings': {
        'violin': 40,
        'viola': 41,
        'cello': 42,
        'contrabass': 43,
        'tremolo_strings': 44,
        'pizzicato_strings': 45,
        'orchestral_harp': 46,
        'timpani': 47
    },
    'winds': {
        'flute': 73,
        'piccolo': 72,
        'oboe': 68,
        'clarinet': 71,
        'bassoon': 70,
        'french_horn': 60,
        'trumpet': 56,
        'trombone': 57,
        'tuba': 58
    }
}

# 默认演奏参数
DEFAULT_PLAY_PARAMS = {
    'velocity': 80,
    'duration': 0.5,
    'gap': 0.1,
    'use_accurate_frequency': True,
    'apply_expression': True,
    'enable_effects': True
}

# 音质评估阈值
QUALITY_THRESHOLDS = {
    'excellent': 0.9,
    'good': 0.7,
    'acceptable': 0.5,
    'poor': 0.3
}