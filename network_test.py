"""
网络连接测试工具
用于诊断和测试 Claude Hook Notification Service 的网络访问问题
"""
import socket
import requests
import subprocess
import sys
from pathlib import Path
from dynaconf import Dynaconf


def get_local_ip():
    """获取本机IP地址"""
    try:
        # 连接到外部地址获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "无法获取"


def test_port_open(host, port):
    """测试端口是否开放"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            result = s.connect_ex((host, port))
            return result == 0
    except Exception:
        return False


def test_http_request(url):
    """测试HTTP请求"""
    try:
        response = requests.get(url, timeout=5)
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "连接被拒绝"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "请求超时"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_firewall_rules():
    """检查Windows防火墙规则"""
    try:
        result = subprocess.run([
            "netsh", "advfirewall", "firewall", "show", "rule", 
            "name=Claude Hook Notification Service"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return {"exists": True, "details": result.stdout}
        else:
            return {"exists": False, "error": result.stderr}
    except Exception as e:
        return {"exists": False, "error": str(e)}


def main():
    """主测试函数"""
    print("=" * 60)
    print("Claude Hook Notification Service 网络诊断工具")
    print("=" * 60)
    
    # 加载配置
    try:
        config = Dynaconf(
            envvar_prefix="CLAUDE",
            settings_files=["config.toml"],
            load_dotenv=True
        )
        host = config.server.host
        port = config.server.port
        print(f"配置加载成功: {host}:{port}")
    except Exception as e:
        print(f"配置加载失败: {e}")
        host = "0.0.0.0"
        port = 8899
        print(f"使用默认配置: {host}:{port}")
    
    print()
    
    # 1. 获取本机IP地址
    print("1. 网络信息:")
    local_ip = get_local_ip()
    print(f"   本机IP地址: {local_ip}")
    print(f"   服务配置: {host}:{port}")
    print()
    
    # 2. 测试端口是否开放
    print("2. 端口连接测试:")
    
    # 测试本地连接
    localhost_open = test_port_open("127.0.0.1", port)
    print(f"   localhost:{port} - {'✓ 开放' if localhost_open else '✗ 关闭'}")
    
    # 测试本机IP连接
    if local_ip != "无法获取":
        localip_open = test_port_open(local_ip, port)
        print(f"   {local_ip}:{port} - {'✓ 开放' if localip_open else '✗ 关闭'}")
    
    print()
    
    # 3. HTTP请求测试
    print("3. HTTP请求测试:")
    
    test_urls = [
        f"http://127.0.0.1:{port}/health",
        f"http://localhost:{port}/health"
    ]
    
    if local_ip != "无法获取":
        test_urls.append(f"http://{local_ip}:{port}/health")
    
    for url in test_urls:
        print(f"   测试: {url}")
        result = test_http_request(url)
        if result["success"]:
            print(f"      ✓ 成功 (状态码: {result['status_code']})")
        else:
            print(f"      ✗ 失败: {result['error']}")
    
    print()
    
    # 4. 防火墙规则检查
    print("4. 防火墙规则检查:")
    firewall_result = check_firewall_rules()
    if firewall_result["exists"]:
        print("   ✓ 防火墙规则存在")
        if "Enabled" in firewall_result["details"]:
            print("   ✓ 规则已启用")
        else:
            print("   ⚠ 规则可能未启用")
    else:
        print("   ✗ 防火墙规则不存在")
        print("   建议运行: setup_firewall.bat 或 setup_firewall.ps1")
    
    print()
    
    # 5. 诊断建议
    print("5. 诊断建议:")
    
    if not localhost_open:
        print("   ⚠ 服务未启动或端口被占用")
        print("     - 检查服务是否正在运行: python main.py")
        print("     - 检查端口占用: netstat -ano | findstr :8899")
    
    elif localhost_open and local_ip != "无法获取" and not test_port_open(local_ip, port):
        print("   ⚠ 防火墙可能阻止了外部访问")
        print("     - 运行防火墙配置脚本: setup_firewall.bat")
        print("     - 检查第三方防火墙软件设置")
        print("     - 确认Windows Defender防火墙设置")
    
    elif all([localhost_open, local_ip != "无法获取", test_port_open(local_ip, port)]):
        print("   ✓ 网络配置正常")
        print(f"     - 其他设备可以通过 http://{local_ip}:{port} 访问服务")
        print(f"     - Claude Code Hook 配置: http://{local_ip}:{port}/notify/hook")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()