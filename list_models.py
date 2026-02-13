"""
列出您账号下所有可用的 Gemini 模型
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
print("📋 查询您账号下的可用模型")
print("="*70)
print()

try:
    print("🔍 正在查询...")
    print()
    
    models = list(genai.list_models())
    
    if not models:
        print("❌ 没有找到任何可用的模型")
        print()
        print("="*70)
        print("🔧 需要启用 API")
        print("="*70)
        print()
        print("请按照以下步骤操作：")
        print()
        print("1️⃣ 访问 Google Cloud Console:")
        print("   https://console.cloud.google.com/")
        print()
        print("2️⃣ 选择您的项目")
        print("   （就是创建 API Key 时的项目）")
        print()
        print("3️⃣ 在搜索框中输入：")
        print("   Generative Language API")
        print()
        print("4️⃣ 点击进入，点击 '启用' 按钮")
        print()
        print("5️⃣ 等待 1-2 分钟，然后重新运行此脚本")
        print()
        print("="*70)
    else:
        print(f"✅ 找到 {len(models)} 个模型")
        print()
        
        generation_models = []
        
        for model in models:
            print(f"模型: {model.name}")
            print(f"  显示名称: {model.display_name}")
            print(f"  支持的方法: {', '.join(model.supported_generation_methods)}")
            
            if 'generateContent' in model.supported_generation_methods:
                generation_models.append(model.name)
                print(f"  ✅ 支持文本生成")
            
            print()
        
        if generation_models:
            print("="*70)
            print(f"🎯 可用于翻译的模型（{len(generation_models)} 个）:")
            print("="*70)
            for m in generation_models:
                print(f"  - {m}")
            print()
            print(f"💡 推荐使用: {generation_models[0]}")
            print()
            print("请记下这个模型名称，我们将在配置中使用它。")
        else:
            print("⚠️  没有找到支持文本生成的模型")

except Exception as e:
    print(f"❌ 查询失败: {e}")
    print()
    
    error_str = str(e).lower()
    
    if "403" in error_str or "permission" in error_str:
        print("="*70)
        print("🔧 权限问题 - 需要启用 API")
        print("="*70)
        print()
        print("解决步骤：")
        print()
        print("1️⃣ 访问 Google Cloud Console:")
        print("   https://console.cloud.google.com/")
        print()
        print("2️⃣ 在左侧菜单选择:")
        print("   API 和服务 → 库")
        print()
        print("3️⃣ 搜索：Generative Language API")
        print()
        print("4️⃣ 点击并启用该 API")
        print()
        print("5️⃣ 等待 1-2 分钟后重试")
    
    elif "404" in error_str:
        print("="*70)
        print("🔧 API 未启用")
        print("="*70)
        print()
        print("这通常意味着需要在 Google Cloud Console 中启用 API。")
        print()
        print("快速启用链接：")
        print("https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
        print()
        print("或者：")
        print("1. 访问 https://console.cloud.google.com/")
        print("2. 搜索 'Generative Language API'")
        print("3. 点击启用")
    
    else:
        print("未知错误，请检查网络连接或稍后重试")
    
    print()
