"""
音频播放模块 - 支持不同事件类型的音频提醒
"""
import asyncio
import os
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from dynaconf import Dynaconf

# Windows 音频播放支持
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False
    logger.warning("winsound not available, fallback to pygame")

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("pygame not available")


class AudioPlayer:
    """音频播放器类"""
    
    def __init__(self, config: Dynaconf):
        self.config = config
        self.sounds_base_path = Path(config.sounds.base_path)
        self.sound_files = config.sounds.files
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="audio")
        
        # 确保音频目录存在
        self.sounds_base_path.mkdir(exist_ok=True)
        
        logger.info(f"音频播放器初始化完成，基础路径: {self.sounds_base_path}")
    
    def _get_sound_file_path(self, event_type: str) -> Optional[Path]:
        """获取指定事件类型的音频文件路径"""
        if event_type not in self.sound_files:
            logger.warning(f"未知的事件类型: {event_type}")
            # 使用通用通知音效作为默认
            event_type = "general_notification"
        
        sound_file = self.sound_files.get(event_type, "happy-message-ping-351298.mp3")
        sound_path = self.sounds_base_path / sound_file
        
        if not sound_path.exists():
            logger.warning(f"音频文件不存在: {sound_path}")
            return None
            
        return sound_path
    
    def _play_sound_sync(self, sound_path: Path) -> bool:
        """同步播放音频文件"""
        try:
            if PYGAME_AVAILABLE:
                # 使用 pygame 播放音频
                pygame.mixer.music.load(str(sound_path))
                pygame.mixer.music.play()
                # 等待播放完成
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                logger.debug(f"使用 pygame 播放音频: {sound_path}")
                return True
            else:
                logger.error("pygame 不可用，无法播放音频")
                return False
        except Exception as e:
            logger.error(f"播放音频失败: {sound_path}, 错误: {e}")
            return False
    
    async def play_sound_async(self, event_type: str) -> bool:
        """异步播放指定事件类型的音频"""
        sound_path = self._get_sound_file_path(event_type)
        if not sound_path:
            return False
        
        try:
            # 在线程池中执行音频播放
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self.executor, 
                self._play_sound_sync, 
                sound_path
            )
            
            if success:
                logger.info(f"音频播放成功: {event_type} -> {sound_path.name}")
            else:
                logger.error(f"音频播放失败: {event_type}")
                
            return success
        except Exception as e:
            logger.error(f"异步播放音频失败: {event_type}, 错误: {e}")
            return False
    
    def play_sound(self, event_type: str) -> bool:
        """同步播放指定事件类型的音频"""
        sound_path = self._get_sound_file_path(event_type)
        if not sound_path:
            return False
        
        return self._play_sound_sync(sound_path)
    
    def play_system_beep(self, beep_type: str = "default") -> bool:
        """播放系统提示音"""
        if not WINSOUND_AVAILABLE:
            logger.warning("winsound 不可用，无法播放系统提示音")
            return False
        
        try:
            beep_map = {
                "default": winsound.MB_OK,
                "error": winsound.MB_ICONHAND,
                "warning": winsound.MB_ICONEXCLAMATION,
                "info": winsound.MB_ICONASTERISK,
                "question": winsound.MB_ICONQUESTION
            }
            
            beep_flag = beep_map.get(beep_type, winsound.MB_OK)
            winsound.MessageBeep(beep_flag)
            logger.debug(f"播放系统提示音: {beep_type}")
            return True
        except Exception as e:
            logger.error(f"播放系统提示音失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
            logger.info("音频播放器资源清理完成")


# 事件类型到音频文件的映射
HOOK_EVENT_SOUND_MAP = {
    # Tool 相关事件
    "tool-call": "tool_start",
    "tool-result": "tool_complete", 
    "tool-error": "tool_error",
    
    # 对话相关事件
    "conversation-start": "conversation_start",
    "conversation-end": "conversation_end",
    
    # 用户交互事件
    "user-prompt-submit": "user_prompt_submit",
    "assistant-response": "assistant_response",
    
    # 通用事件
    "notification": "general_notification",
    "error": "system_error"
}


def get_sound_type_for_hook(hook_event: str) -> str:
    """根据 Claude Hook 事件类型获取对应的音频类型"""
    return HOOK_EVENT_SOUND_MAP.get(hook_event, "general_notification")