#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API调试脚本 - 测试sound/tool_complete接口
包含网络诊断和多种测试模式
"""

import requests
import json
import time
import socket
from urllib.parse import urlparse

def check_network_connectivity(host, port):
    """检查网络连通性"""
    print(f"正在检查 {host}:{port} 的连通性...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ {host}:{port} 端口开放")
            return True
        else:
            print(f"❌ {host}:{port} 端口关闭或无法访问")
            return False
            
    except socket.gaierror:
        print(f"❌ 无法解析主机名: {host}")
        return False
    except Exception as e:
        print(f"❌ 网络检查错误: {e}")
        return False

def test_sound_complete():
    """测试声音完成接口"""
    
    # API配置
    url = "http://10.39.7.46:8899/test/sound/tool_complete"
    headers = {
        "accept": "application/json"
    }
    
    # 解析URL获取主机和端口
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or 80
    
    print("=" * 60)
    print("开始测试声音完成接口...")
    print(f"URL: {url}")
    print(f"主机: {host}:{port}")
    print("=" * 60)
    
    # 先检查网络连通性
    if not check_network_connectivity(host, port):
        print("\n建议:")
        print("1. 检查目标服务器是否运行")
        print("2. 确认IP地址和端口是否正确")
        print("3. 检查防火墙设置")
        print("4. 确认网络连接是否正常")
        return
    
    try:
        # 发送POST请求
        print("\n正在发送请求...")
        response = requests.post(
            url=url,
            headers=headers,
            data='',
            timeout=10
        )
        
        # 打印响应详情
        print(f"\n状态码: {response.status_code}")
        print(f"响应时间: {response.elapsed.total_seconds():.2f}秒")
        
        # 打印响应头
        print("\n响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # 尝试解析响应内容
        print("\n响应内容:")
        try:
            json_data = response.json()
            print(json.dumps(json_data, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print("响应内容(非JSON):")
            print(response.text)
            
        # 检查响应状态
        if response.status_code == 200:
            print("\n✅ 请求成功!")
        else:
            print(f"\n⚠️  请求完成，但状态码为: {response.status_code}")
            
    except requests.exceptions.ConnectTimeout:
        print("❌ 连接超时 - 服务器无响应")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ 请求超时: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

def test_localhost_alternative():
    """测试本地替代方案"""
    print("\n" + "=" * 60)
    print("测试本地替代方案...")
    print("=" * 60)
    
    # 你可以在这里修改成本地测试URL
    local_url = "http://localhost:8080/test/sound/tool_complete"
    
    try:
        response = requests.post(local_url, headers={"accept": "application/json"}, data='', timeout=5)
        print(f"本地测试 - 状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"本地测试失败: {e}")

def print_usage_examples():
    """打印使用示例"""
    print("\n" + "=" * 60)
    print("使用示例:")
    print("=" * 60)
    
    examples = [
        {
            "name": "基础POST请求",
            "code": """
import requests

url = "http://10.39.7.46:8899/test/sound/tool_complete"
headers = {"accept": "application/json"}
response = requests.post(url, headers=headers, data='')
print(response.status_code, response.json())
            """
        },
        {
            "name": "带错误处理的请求",
            "code": """
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(
        "http://10.39.7.46:8899/test/sound/tool_complete",
        headers={"accept": "application/json"},
        data='',
        timeout=10
    )
    response.raise_for_status()
    print("成功:", response.json())
except RequestException as e:
    print("请求失败:", e)
            """
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}:")
        print(example['code'])

if __name__ == "__main__":
    # 运行主测试
    test_sound_complete()
    
    # 打印使用示例
    print_usage_examples()
    
    print("\n测试完成!")
