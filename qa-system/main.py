from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests
import os
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from datetime import datetime

# 加载环境变量
load_dotenv()

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.post("/api/chat")
async def chat(chat_request: ChatRequest):
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": m.role, "content": m.content} for m in chat_request.messages],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True
        )
        
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        async def generate():
            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8') + '\n'
        
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        error_msg = f"Error type: {type(e).__name__}, Error details: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/health")
async def health_check():
    """
    健康检查端点
    用途：
    1. 监控服务是否正常运行
    2. 用于负载均衡器检查服务状态
    3. 提供基本的服务可用性验证
    
    Returns:
        dict: 包含服务状态的响应
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "qa-system",
        "version": "1.0.0"
    } 