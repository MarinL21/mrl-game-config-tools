"""
快速测试可用的 Gemini 模型
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key 未配置")
    exit(1)

genai.configure(api_key=api_key)

print("="*70)
print("🧪 测试 Gemini 可用模型")
print("="*70)
print()

# 尝试的模型列表
model_names = [
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash',
    'gemini-1.5-pro-latest',
    'gemini-1.5-pro',
    'gemini-pro',
    'models/gemini-1.5-flash-latest',
    'models/gemini-1.5-flash',
    'models/gemini-pro',
]

working_models = []

for model_name in model_names:
    try:
        print(f"测试 {model_name:40s} ", end="")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello")
        print(f"✅ 工作正常 - 响应: {response.text[:20]}")
        working_models.append(model_name)
    except Exception as e:
        error_msg = str(e)[:50]
        print(f"❌ 失败 - {error_msg}")

print()
print("="*70)
if working_models:
    print(f"✅ 找到 {len(working_models)} 个可用模型:")
    for m in working_models:
        print(f"   - {m}")
    print()
    print(f"🎯 推荐使用: {working_models[0]}")
else:
    print("❌ 没有找到可用的模型")
    print()
    print("可能的原因:")
    print("1. API Key 权限不足")
    print("2. 需要在 Google Cloud Console 启用 API")
    print("3. 账号或地区限制")

print("="*70)
