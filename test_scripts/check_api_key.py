#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 DASHSCOPE_API_KEY 和 DASHSCOPE_WORKSPACE_ID 环境变量是否正确配置
"""

import os
import sys

print("=" * 60)
print("检查 DashScope 环境变量")
print("=" * 60)

# 检查 API Key
api_key = os.getenv("DASHSCOPE_API_KEY")
workspace_id = os.getenv("DASHSCOPE_WORKSPACE_ID")

api_key_ok = False
workspace_id_ok = False

print("\n【1】DASHSCOPE_API_KEY")
print("-" * 60)
if api_key:
    # 隐藏大部分字符，只显示前后几位
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"✓ DASHSCOPE_API_KEY 已设置")
    print(f"  值: {masked_key}")
    print(f"  长度: {len(api_key)} 字符")
    api_key_ok = True
else:
    print("✗ DASHSCOPE_API_KEY 未设置")
    print("\n请设置环境变量：")
    print("  Windows (cmd):       set DASHSCOPE_API_KEY=your_api_key")
    print("  Windows (PowerShell): $env:DASHSCOPE_API_KEY=\"your_api_key\"")
    print("  Linux/Mac:           export DASHSCOPE_API_KEY=\"your_api_key\"")

print("\n【2】DASHSCOPE_WORKSPACE_ID")
print("-" * 60)
if workspace_id:
    print(f"✓ DASHSCOPE_WORKSPACE_ID 已设置")
    print(f"  值: {workspace_id}")
    workspace_id_ok = True
else:
    print("⚠ DASHSCOPE_WORKSPACE_ID 未设置")
    print("  如果你的 API Key 绑定了工作空间，需要设置此变量")
    print("  从 test_rerank_model.py 来看，你的工作空间 ID 可能是:")
    print("    llm-fq43z9u2tnoy3m7o")
    print("\n  设置方法：")
    print("  Windows (cmd):       set DASHSCOPE_WORKSPACE_ID=llm-fq43z9u2tnoy3m7o")
    print("  Windows (PowerShell): $env:DASHSCOPE_WORKSPACE_ID=\"llm-fq43z9u2tnoy3m7o\"")
    print("  Linux/Mac:           export DASHSCOPE_WORKSPACE_ID=\"llm-fq43z9u2tnoy3m7o\"")

# 尝试导入 dashscope 并测试
print("\n【3】DashScope SDK")
print("-" * 60)
if api_key_ok:
    try:
        import dashscope
        dashscope.api_key = api_key

        if workspace_id_ok:
            dashscope.base_http_api_url = f'https://{workspace_id}.cn-beijing.maas.aliyuncs.com/api/v1'
            print("✓ dashscope 库导入成功")
            print(f"  API Key 已设置")
            print(f"  工作空间已配置: {workspace_id}")
        else:
            print("✓ dashscope 库导入成功")
            print(f"  API Key 已设置")
            print(f"  ⚠ 工作空间未配置（如果需要请设置）")

    except ImportError:
        print("✗ dashscope 库未安装")
        print("  请运行: pip install dashscope")

print("\n" + "=" * 60)
print("配置检查完成")
print("=" * 60)

if not api_key_ok:
    print("\n❌ 必需配置缺失：DASHSCOPE_API_KEY")
    sys.exit(1)
elif not workspace_id_ok:
    print("\n⚠️  可选配置缺失：DASHSCOPE_WORKSPACE_ID")
    print("   如果 test_rerank_model.py 可以正常运行，但其他测试失败，")
    print("   说明你需要设置工作空间 ID")
    sys.exit(0)
else:
    print("\n✅ 所有配置正常")
    sys.exit(0)

