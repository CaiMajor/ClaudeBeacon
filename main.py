"""
Claude Code Hook Notification Service
用于接收 Claude Code hooks 事件并播放声音提醒的 FastAPI 服务
"""
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any, Optional

import uvicorn
from dynaconf import Dynaconf
from fastapi import FastAPI, HTTPException, BackgroundTasks
from loguru import logger
from pydantic import BaseModel, Field

from audio_player import AudioPlayer, get_sound_type_for_hook


# Pydantic 模型定义
class HookEventRequest(BaseModel):
    """Claude Hook 事件请求模型"""
    event_type: str = Field(..., description="Hook 事件类型")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="事件载荷数据")
    timestamp: Optional[str] = Field(default=None, description="事件时间戳")
    source: Optional[str] = Field(default="claude-code", description="事件来源")


class NotificationResponse(BaseModel):
    """通知响应模型"""
    success: bool = Field(..., description="处理是否成功")
    message: str = Field(..., description="响应消息")
    event_type: str = Field(..., description="事件类型")
    sound_played: bool = Field(..., description="是否播放了声音")


# 全局变量
config: Dynaconf = None
audio_player: AudioPlayer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理"""
    global config, audio_player
    
    # 启动时初始化
    logger.info("Claude Hook Notification Service 启动中...")
    
    # 加载配置
    config = Dynaconf(
        envvar_prefix="CLAUDE",
        settings_files=["config.toml"],
        load_dotenv=True
    )
    
    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        level=config.logging.level,
        format=config.logging.format
    )
    
    # 初始化音频播放器
    audio_player = AudioPlayer(config)
    
    logger.info(f"服务启动在 {config.server.host}:{config.server.port}")
    
    yield
    
    # 关闭时清理
    logger.info("Claude Hook Notification Service 关闭中...")
    if audio_player:
        await audio_player.cleanup()


# 创建 FastAPI 应用
app = FastAPI(
    title="Claude Hook Notification Service",
    description="接收 Claude Code hooks 事件并播放声音提醒的通知服务",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """根路径 - 服务状态检查"""
    return {
        "service": "Claude Hook Notification Service",
        "status": "running",
        "version": "1.0.0",
        "description": "Ready to receive Claude Code hook events"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "audio_available": audio_player is not None
    }


@app.post("/notify/hook", response_model=NotificationResponse)
async def handle_hook_notification(
    request: HookEventRequest,
    background_tasks: BackgroundTasks
):
    """
    处理 Claude Hook 事件通知
    这是主要的接收 Claude Code hooks 事件的端点
    """
    logger.info(f"收到 Hook 事件: {request.event_type}")
    logger.debug(f"事件详情: {request.model_dump()}")
    
    if not audio_player:
        logger.error("音频播放器未初始化")
        raise HTTPException(status_code=500, detail="音频播放器未初始化")
    
    # 获取对应的音频类型
    sound_type = get_sound_type_for_hook(request.event_type)
    
    try:
        # 在后台任务中播放音频，避免阻塞响应
        background_tasks.add_task(audio_player.play_sound_async, sound_type)
        
        response = NotificationResponse(
            success=True,
            message=f"Hook 事件 '{request.event_type}' 处理成功",
            event_type=request.event_type,
            sound_played=True
        )
        
        logger.info(f"Hook 事件处理完成: {request.event_type} -> {sound_type}")
        return response
        
    except Exception as e:
        logger.error(f"处理 Hook 事件失败: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"处理 Hook 事件失败: {str(e)}"
        )


@app.post("/notify/custom")
async def handle_custom_notification(
    event_type: str,
    message: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    处理自定义通知
    允许直接指定音频类型进行测试
    """
    logger.info(f"收到自定义通知: {event_type}")
    
    if not audio_player:
        raise HTTPException(status_code=500, detail="音频播放器未初始化")
    
    try:
        # 在后台任务中播放音频
        background_tasks.add_task(audio_player.play_sound_async, event_type)
        
        return NotificationResponse(
            success=True,
            message=message or f"自定义通知 '{event_type}' 处理成功",
            event_type=event_type,
            sound_played=True
        )
        
    except Exception as e:
        logger.error(f"处理自定义通知失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"处理自定义通知失败: {str(e)}"
        )


@app.post("/test/sound/{sound_type}")
async def test_sound(sound_type: str, background_tasks: BackgroundTasks):
    """
    测试指定类型的音频播放
    用于调试和验证音频文件
    """
    logger.info(f"测试音频播放: {sound_type}")
    
    if not audio_player:
        raise HTTPException(status_code=500, detail="音频播放器未初始化")
    
    try:
        # 在后台任务中播放音频
        background_tasks.add_task(audio_player.play_sound_async, sound_type)
        
        return {
            "success": True,
            "message": f"测试音频 '{sound_type}' 播放中",
            "sound_type": sound_type
        }
        
    except Exception as e:
        logger.error(f"测试音频播放失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"测试音频播放失败: {str(e)}"
        )


@app.get("/sounds/list")
async def list_available_sounds():
    """列出所有可用的音频类型"""
    if not config:
        raise HTTPException(status_code=500, detail="配置未初始化")
    
    return {
        "available_sounds": dict(config.sounds.files),
        "base_path": str(config.sounds.base_path)
    }


def main():
    """主程序入口"""
    # 临时加载配置以获取服务器设置
    temp_config = Dynaconf(
        envvar_prefix="CLAUDE",
        settings_files=["config.toml"],
        load_dotenv=True
    )
    
    print(f"启动服务器: {temp_config.server.host}:{temp_config.server.port}")
    print("确保防火墙允许此端口的入站连接!")
    
    # 启动 FastAPI 服务器
    uvicorn.run(
        app,  # 直接传递 app 对象而不是字符串
        host=temp_config.server.host,
        port=temp_config.server.port,
        reload=temp_config.server.get("debug", False),
        log_level="info",
        access_log=True  # 启用访问日志以便调试
    )


if __name__ == "__main__":
    main()
