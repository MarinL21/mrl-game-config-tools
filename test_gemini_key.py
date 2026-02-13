"""
测试 Gemini API Key 是否有效
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("="*60)
print("🔑 Gemini API Key 测试")
print("="*60)
print()

if not api_key:
    print("❌ 错误：未找到 GEMINI_API_KEY")
    print("   请检查 .env 文件")
    exit(1)

print(f"✅ API Key 已加载")
print(f"   长度: {len(api_key)} 字符")
print(f"   开头: {api_key[:10]}...")
print(f"   结尾: ...{api_key[-4:]}")
print()

# 测试 API
print("🧪 测试 API 连接...")
print()

try:
    import google.generativeai as genai
    
    # 配置 API
    genai.configure(api_key=api_key)
    
    print("📡 尝试连接 Gemini API...")
    
    # 尝试不同的模型
    models_to_try = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro']
    
    for model_name in models_to_try:
        try:
            print(f"   尝试模型: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'Hello' in one word")
            print(f"   ✅ 模型 {model_name} 可用")
            break
        except Exception as model_error:
            print(f"   ⚠️ 模型 {model_name} 不可用: {str(model_error)[:50]}...")
            continue
    else:
        raise Exception("所有模型都不可用")
    
    print("✅ API 连接成功！")
    print(f"   响应: {response.text}")
    print()
    print("="*60)
    print("🎉 您的 API Key 完全正常！")
    print("="*60)
    
except Exception as e:
    print("❌ API 连接失败")
    print()
    print("错误类型:", type(e).__name__)
    print("错误信息:", str(e))
    print()
    print("="*60)
    print("🔍 可能的原因:")
    print("="*60)
    print()
    
    error_str = str(e).lower()
    
    if "400" in error_str or "invalid" in error_str:
        print("1. API Key 可能无效或格式错误")
        print("   - 检查 .env 文件中的 API Key 是否完整")
        print("   - 确保没有多余的空格或引号")
        print()
        print("2. API 可能未启用")
        print("   - 访问: https://console.cloud.google.com/")
        print("   - 搜索并启用 'Generative Language API'")
        print()
        print("3. 地区限制")
        print("   - Gemini API 在某些地区可能不可用")
        print("   - 尝试使用 VPN 连接美国节点")
        print()
    
    elif "403" in error_str or "permission" in error_str:
        print("1. API Key 权限不足")
        print("   - 在 Google AI Studio 重新创建 API Key")
        print("   - 确保项目已启用 Generative Language API")
        print()
    
    elif "429" in error_str or "quota" in error_str:
        print("1. 已超过免费配额限制")
        print("   - 每分钟限制: 60 次请求")
        print("   - 每天限制: 1,500 次请求")
        print("   - 等待一段时间后重试")
        print()
    
    elif "404" in error_str or "not found" in error_str:
        print("1. 模型名称错误或不可用")
        print("   - 尝试其他模型: gemini-pro")
        print()
    
    else:
        print("1. 网络连接问题")
        print("   - 检查网络连接")
        print("   - 尝试关闭 VPN/代理")
        print()
        print("2. Google 服务访问问题")
        print("   - 确认可以访问 Google 服务")
        print()
    
    print()
    print("💡 建议操作:")
    print("1. 删除当前 API Key（已暴露在对话中）")
    print("2. 在 Google AI Studio 创建新的 API Key")
    print("3. 更新 .env 文件")
    print("4. 重新运行此测试脚本")
    print()
    print("完整错误信息:")
    print("-" * 60)
    import traceback
    traceback.print_exc()
