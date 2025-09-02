import pandas as pd
import time
from typing import List, Dict, Optional
from enhanced_petersen_player import EnhancedPetersenPlayer

class CSVMusicPlayer:
    """CSV音乐文件播放器"""
    
    def __init__(self, enhanced_player: EnhancedPetersenPlayer):
        self.player = enhanced_player
        self.is_playing = False
        self.current_position = 0
    
    def load_csv_composition(self, csv_path: str) -> bool:
        """加载CSV音乐文件"""
        try:
            self.composition_data = pd.read_csv(csv_path)
            print(f"✓ 加载CSV音乐文件: {csv_path}")
            print(f"  总音符数: {len(self.composition_data)}")
            return True
        except Exception as e:
            print(f"❌ CSV文件加载失败: {e}")
            return False
    
    def play_composition(self, start_time: float = 0, end_time: Optional[float] = None):
        """播放整个作曲"""
        if not hasattr(self, 'composition_data'):
            print("❌ 未加载音乐数据")
            return False
        
        try:
            print("🎵 开始播放Petersen作曲...")
            
            # 过滤时间范围
            df = self.composition_data
            if end_time:
                df = df[(df['时间(秒)'] >= start_time) & (df['时间(秒)'] <= end_time)]
            else:
                df = df[df['时间(秒)'] >= start_time]
            
            # 按时间排序
            df = df.sort_values('时间(秒)')
            
            self.is_playing = True
            start_real_time = time.time()
            last_music_time = start_time
            
            for _, row in df.iterrows():
                if not self.is_playing:
                    break
                
                music_time = row['时间(秒)']
                
                # 等待到正确的播放时间
                elapsed_real_time = time.time() - start_real_time
                target_real_time = music_time - start_time
                
                if target_real_time > elapsed_real_time:
                    time.sleep(target_real_time - elapsed_real_time)
                
                # 播放音符
                self._play_csv_note(row)
                last_music_time = music_time
            
            print("✓ 播放完成")
            return True
            
        except Exception as e:
            print(f"❌ 播放失败: {e}")
            return False
        finally:
            self.is_playing = False
    
    def _play_csv_note(self, row):
        """播放单个CSV音符"""
        try:
            frequency = row['频率(Hz)']
            duration = row['持续时间']
            velocity = row['力度']
            
            # 使用Enhanced Player播放精确频率
            self.player.play_single_frequency(
                frequency=frequency,
                duration=duration * 0.9,  # 稍微缩短避免重叠
                velocity=velocity,
                use_accurate_frequency=True
            )
            
        except Exception as e:
            print(f"⚠️ 音符播放警告: {e}")
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
        print("⏹️ 播放已停止")
    
    def get_composition_info(self) -> Dict:
        """获取作曲信息"""
        if not hasattr(self, 'composition_data'):
            return {}
        
        df = self.composition_data
        return {
            "total_notes": len(df),
            "duration": df['时间(秒)'].max(),
            "frequency_range": [df['频率(Hz)'].min(), df['频率(Hz)'].max()],
            "tracks": df['轨道'].unique().tolist() if '轨道' in df.columns else [],
            "tempo_info": f"BPM信息可从小节时间计算"
        }