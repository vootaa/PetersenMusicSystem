from enhanced_petersen_player import create_player

def initialize_player_with_check():
    """统一初始化播放器"""
    try:
        player = create_player()
        if not player:
            raise Exception("播放器创建失败")
        print("✅ 播放器初始化成功")
        return player
    except Exception as e:
        print(f"❌ 播放器初始化失败: {e}")
        return None

def play_test_sequence(player, frequencies, names, **kwargs):
    """通用播放测试函数"""
    return player.play_frequencies(frequencies, names, **kwargs)