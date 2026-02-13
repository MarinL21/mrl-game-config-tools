"""
游戏运营策划工具 - 翻译服务后端 API

使用 FastAPI 框架提供翻译服务
支持 Google Gemini API 批量翻译到 17 种语言
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="游戏运营策划工具 - 翻译 API",
    description="基于 Google Gemini AI 的多语言翻译服务",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量获取 API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEY 未设置！请在 .env 文件中配置")
else:
    # 配置 Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini API 已配置")

# 支持的语言配置
LANGUAGE_CODES = ['en', 'fr', 'de', 'po', 'zh', 'id', 'th', 'sp', 'ru', 'tr', 'vi', 'it', 'pl', 'ar', 'jp', 'kr', 'cns']

LANGUAGE_FULL_NAMES = {
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'po': 'Portuguese',
    'zh': 'Simplified Chinese',
    'id': 'Indonesian',
    'th': 'Thai',
    'sp': 'Spanish',
    'ru': 'Russian',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'it': 'Italian',
    'pl': 'Polish',
    'ar': 'Arabic',
    'jp': 'Japanese',
    'kr': 'Korean',
    'cns': 'Traditional Chinese'
}

# 请求模型
class TranslationRequest(BaseModel):
    """翻译请求模型"""
    texts: List[str]  # 要翻译的中文文本列表
    model: str = "models/gemini-2.5-flash"  # 使用的模型，默认最新最快版本

class TranslationResponse(BaseModel):
    """翻译响应模型"""
    success: bool
    data: List[Dict[str, str]]  # 翻译结果，每行是一个字典
    message: str = ""

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    api_configured: bool
    supported_languages: int


# API 路由
@app.get("/", response_model=Dict[str, str])
async def root():
    """根路径，返回 API 信息"""
    return {
        "message": "游戏运营策划工具 - 翻译 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "api_configured": bool(GEMINI_API_KEY),
        "supported_languages": len(LANGUAGE_CODES)
    }


@app.post("/api/translate", response_model=TranslationResponse)
async def translate_texts(request: TranslationRequest):
    """
    翻译接口
    
    接收中文文本列表，翻译到 17 种语言
    返回格式：[{语言代码: 翻译结果}, ...]
    """
    
    # 验证 API Key
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="服务器未配置 GEMINI_API_KEY，请联系管理员"
        )
    
    # 验证输入
    if not request.texts:
        raise HTTPException(
            status_code=400,
            detail="请提供要翻译的文本"
        )
    
    if len(request.texts) > 100:
        raise HTTPException(
            status_code=400,
            detail="单次翻译文本数量不能超过 100 条"
        )
    
    logger.info(f"📝 收到翻译请求：{len(request.texts)} 条文本")
    
    try:
        # 创建 Gemini 模型（使用 v1 API）
        model = genai.GenerativeModel(model_name=request.model)
        
        results = []
        
        # 逐行翻译
        for idx, text in enumerate(request.texts):
            logger.info(f"⚡ 正在翻译第 {idx + 1}/{len(request.texts)} 行: {text[:50]}...")
            
            # 构建提示词
            prompt = f"""Translate the following Chinese text into these languages. Return ONLY a tab-separated line with translations in this exact order:
{', '.join([LANGUAGE_FULL_NAMES[code] for code in LANGUAGE_CODES])}

Chinese text: {text}

Format: Return one line with {len(LANGUAGE_CODES)} translations separated by tabs (\\t).
For Simplified Chinese (zh), return the original text: {text}
Do not include any explanations, markdown formatting, or code blocks - just the translations separated by tabs."""

            # 调用 Gemini API
            response = model.generate_content(prompt)
            translated_line = response.text.strip()
            
            # 清理可能的 markdown 标记
            translated_line = translated_line.replace('```', '').strip()
            
            # 解析翻译结果
            translations = translated_line.split('\t')
            
            # 构建结果字典
            row_data = {}
            for i, code in enumerate(LANGUAGE_CODES):
                if i < len(translations):
                    row_data[code] = translations[i].strip()
                else:
                    # 如果翻译结果不完整，使用原文
                    row_data[code] = text if code == 'zh' else f"[翻译不完整]"
            
            results.append(row_data)
            
            # 避免请求过快，延迟 1 秒
            if idx < len(request.texts) - 1:
                await asyncio.sleep(1)
        
        logger.info(f"✅ 翻译完成：{len(results)} 条")
        
        return {
            "success": True,
            "data": results,
            "message": f"成功翻译 {len(results)} 条文本"
        }
    
    except Exception as e:
        logger.error(f"❌ 翻译失败：{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"翻译失败：{str(e)}"
        )


@app.get("/api/languages")
async def get_supported_languages():
    """获取支持的语言列表"""
    return {
        "codes": LANGUAGE_CODES,
        "names": LANGUAGE_FULL_NAMES,
        "count": len(LANGUAGE_CODES)
    }


# 开发环境运行
if __name__ == "__main__":
    import uvicorn
    
    # 检查 API Key
    if not GEMINI_API_KEY:
        print("\n" + "="*60)
        print("⚠️  警告：GEMINI_API_KEY 未设置！")
        print("="*60)
        print("\n请按照以下步骤配置：")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 中设置 GEMINI_API_KEY=your_api_key")
        print("3. 重新运行服务")
        print("\n获取 API Key：https://aistudio.google.com/app/apikey\n")
    else:
        print("\n" + "="*60)
        print("✅ 游戏运营策划工具 - 翻译服务")
        print("="*60)
        print(f"\n📡 服务地址：http://localhost:8000")
        print(f"📖 API 文档：http://localhost:8000/docs")
        print(f"🔍 健康检查：http://localhost:8000/health")
        print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
