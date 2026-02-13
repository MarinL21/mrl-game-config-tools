"""
API 测试脚本

快速测试后端 API 是否正常工作
"""

import requests
import json
import sys

def print_header(text):
    """打印美化的标题"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def test_health(base_url):
    """测试健康检查接口"""
    print_header("测试 1: 健康检查")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务状态: {data['status']}")
            print(f"✅ API 已配置: {data['api_configured']}")
            print(f"✅ 支持语言数: {data['supported_languages']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！请确认后端服务是否正在运行")
        print(f"   尝试访问: {base_url}")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def test_languages(base_url):
    """测试语言列表接口"""
    print_header("测试 2: 获取支持的语言")
    
    try:
        response = requests.get(f"{base_url}/api/languages", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 支持 {data['count']} 种语言")
            print(f"   语言代码: {', '.join(data['codes'][:5])}...")
            return True
        else:
            print(f"❌ 获取语言列表失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def test_translate(base_url):
    """测试翻译接口"""
    print_header("测试 3: 翻译功能")
    
    test_texts = ["规则", "如何取得点数"]
    print(f"测试文本: {test_texts}")
    print("⏳ 正在翻译...")
    
    try:
        response = requests.post(
            f"{base_url}/api/translate",
            json={
                "texts": test_texts,
                "model": "models/gemini-2.5-flash"
            },
            timeout=60  # 翻译可能需要较长时间
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success']:
                print(f"✅ {data['message']}")
                print(f"\n📊 翻译结果示例:")
                
                # 显示第一行的翻译结果（前5种语言）
                if data['data']:
                    first_row = data['data'][0]
                    print(f"\n原文: {test_texts[0]}")
                    for lang in ['en', 'fr', 'de', 'jp', 'kr']:
                        if lang in first_row:
                            print(f"  {lang}: {first_row[lang]}")
                
                return True
            else:
                print(f"❌ 翻译失败: {data.get('message', '未知错误')}")
                return False
        else:
            error_detail = response.json().get('detail', '未知错误')
            print(f"❌ API 请求失败 ({response.status_code})")
            print(f"   错误详情: {error_detail}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时！翻译可能需要较长时间")
        print("   建议: 增加超时时间或减少测试文本数量")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("\n" + "🧪 " + "="*55)
    print("     游戏运营策划工具 - 后端 API 测试")
    print("="*60)
    
    # 默认测试 localhost，也可以测试部署的服务
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = "http://localhost:8000"
    
    print(f"\n🔗 测试目标: {base_url}")
    print(f"💡 提示: 可通过命令行参数指定地址")
    print(f"   示例: python test_api.py https://your-backend.vercel.app\n")
    
    # 运行测试
    results = []
    
    results.append(("健康检查", test_health(base_url)))
    
    if results[-1][1]:  # 如果健康检查通过，继续其他测试
        results.append(("语言列表", test_languages(base_url)))
        results.append(("翻译功能", test_translate(base_url)))
    else:
        print("\n⚠️  健康检查失败，跳过后续测试")
    
    # 总结
    print_header("测试总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}  {test_name}")
    
    print(f"\n📊 总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！后端服务运行正常")
        print(f"\n📖 API 文档: {base_url}/docs")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查:")
        print("  1. 后端服务是否正在运行")
        print("  2. GEMINI_API_KEY 是否正确配置")
        print("  3. 网络连接是否正常")
        print(f"\n💡 查看详细日志: {base_url}/docs")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
