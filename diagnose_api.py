"""
深度诊断 Gemini API 问题
"""

import os
import sys
from dotenv import load_dotenv

print("="*70)
print("🔬 Gemini API 深度诊断")
print("="*70)
print()

# 1. 检查 .env 文件
print("📋 步骤 1: 检查配置文件")
print("-"*70)

if not os.path.exists('.env'):
    print("❌ .env 文件不存在！")
    print("   请运行: cp .env.example .env")
    sys.exit(1)
else:
    print("✅ .env 文件存在")

# 读取文件内容
with open('.env', 'r') as f:
    content = f.read()
    lines = content.strip().split('\n')
    
print(f"   文件行数: {len(lines)}")
print(f"   文件大小: {len(content)} 字节")

# 显示文件内容（隐藏密钥）
print("\n   文件内容预览:")
for i, line in enumerate(lines, 1):
    if line.strip() and not line.strip().startswith('#'):
        if '=' in line:
            key, value = line.split('=', 1)
            masked_value = value[:10] + '...' + value[-4:] if len(value) > 14 else value
            print(f"   行 {i}: {key}={masked_value}")
        else:
            print(f"   行 {i}: {line[:50]}")
print()

# 2. 加载环境变量
print("📋 步骤 2: 加载环境变量")
print("-"*70)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY 未设置")
    print("\n可能的原因:")
    print("1. .env 文件格式不正确")
    print("2. 变量名拼写错误（应该是 GEMINI_API_KEY）")
    print("3. 等号前后有空格")
    print("\n正确格式示例:")
    print("GEMINI_API_KEY=AIzaSyABCDEF...")
    sys.exit(1)

print("✅ API Key 已加载")
print(f"   长度: {len(api_key)} 字符")
print(f"   开头: {api_key[:10]}")
print(f"   结尾: ...{api_key[-4:]}")

# 验证格式
if not api_key.startswith('AIzaSy'):
    print("\n⚠️  警告: API Key 不是以 'AIzaSy' 开头")
    print("   Google API Key 通常以 'AIzaSy' 开头")
    print("   请确认复制的是正确的 API Key")

if len(api_key) != 39:
    print(f"\n⚠️  警告: API Key 长度不标准")
    print(f"   当前长度: {len(api_key)}")
    print(f"   标准长度: 39")
    print("   可能复制时漏掉或多了字符")

print()

# 3. 测试网络连接
print("📋 步骤 3: 测试网络连接")
print("-"*70)

try:
    import requests
    
    # 测试基本网络
    print("   测试 Google 连接...", end=" ")
    response = requests.get("https://www.google.com", timeout=5)
    if response.status_code == 200:
        print("✅")
    else:
        print(f"⚠️ (状态码: {response.status_code})")
    
    # 测试 Google AI
    print("   测试 Google AI 连接...", end=" ")
    response = requests.get("https://generativelanguage.googleapis.com", timeout=5)
    print("✅")
    
except Exception as e:
    print(f"\n❌ 网络连接失败: {e}")
    print("\n可能的原因:")
    print("1. 网络连接问题")
    print("2. 防火墙或代理拦截")
    print("3. Google 服务在当前地区不可用")

print()

# 4. 测试 Gemini API
print("📋 步骤 4: 测试 Gemini API")
print("-"*70)

try:
    import google.generativeai as genai
    
    print("   配置 API...", end=" ")
    genai.configure(api_key=api_key)
    print("✅")
    
    print("   列出可用模型...")
    
    # 尝试列出模型
    try:
        models = genai.list_models()
        print("   ✅ 成功获取模型列表")
        print(f"\n   可用的模型:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"   - {model.name}")
    except Exception as e:
        print(f"   ⚠️ 无法列出模型: {str(e)[:60]}...")
    
    print("\n   测试简单请求...")
    
    # 尝试不同的模型名称
    model_names = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash', 
        'gemini-1.5-pro-latest',
        'gemini-pro'
    ]
    
    success = False
    for model_name in model_names:
        try:
            print(f"   尝试模型: {model_name}...", end=" ")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            print("✅")
            success = True
            break
        except Exception as e:
            print(f"⚠️ ({str(e)[:40]}...)")
            continue
    
    if not success:
        raise Exception("所有模型都无法使用")
    
    print("   ✅ API 调用成功！")
    print(f"   响应: {response.text[:50]}")
    
except Exception as e:
    print(f"\n❌ API 测试失败")
    print(f"\n错误类型: {type(e).__name__}")
    print(f"错误信息: {str(e)[:200]}")
    
    error_str = str(e).lower()
    
    print("\n" + "="*70)
    print("🔍 问题分析和解决方案")
    print("="*70)
    
    if "api key not valid" in error_str or "api_key_invalid" in error_str:
        print("\n❌ API Key 无效")
        print("\n原因可能是:")
        print("1. API Key 复制不完整或有误")
        print("2. API Key 已被撤销")
        print("3. API Key 创建失败")
        print("\n解决方案:")
        print("1. 访问 Google AI Studio:")
        print("   https://aistudio.google.com/app/apikey")
        print("\n2. 删除现有的 API Key")
        print("\n3. 创建新的 API Key:")
        print("   - 点击 'Create API key'")
        print("   - 选择 'Create API key in new project'")
        print("   - 等待创建完成")
        print("\n4. 完整复制新的 API Key（39个字符）")
        print("\n5. 更新 .env 文件:")
        print("   GEMINI_API_KEY=你的新密钥")
        print("   （注意：等号两边无空格，无引号）")
        
    elif "resource_exhausted" in error_str or "quota" in error_str:
        print("\n❌ 配额已用完")
        print("\n解决方案:")
        print("1. 等待配额重置（每分钟60次，每天1500次）")
        print("2. 或创建新的 Google 账号和 API Key")
        
    elif "permission" in error_str or "403" in error_str:
        print("\n❌ 权限不足")
        print("\n解决方案:")
        print("1. 在 Google Cloud Console 启用 API:")
        print("   https://console.cloud.google.com/")
        print("2. 搜索并启用 'Generative Language API'")
        
    elif "unavailable" in error_str or "region" in error_str:
        print("\n❌ 地区限制")
        print("\n解决方案:")
        print("1. Gemini API 可能在您的地区不可用")
        print("2. 尝试使用 VPN 连接到支持的地区（如美国）")
        
    else:
        print("\n❌ 未知错误")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 尝试关闭 VPN/代理")
        print("3. 重新创建 API Key")
    
    print("\n" + "="*70)
    sys.exit(1)

print("\n" + "="*70)
print("🎉 所有检查通过！您的 API 配置完全正常！")
print("="*70)
print("\n现在可以启动服务了:")
print("  python3 main.py")
print()
