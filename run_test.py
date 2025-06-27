#!/usr/bin/env python3
"""
跨平台Godot项目启动器
支持Windows、macOS、Linux
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def find_godot_executable():
    """查找系统中的Godot可执行文件"""
    system = platform.system().lower()
    
    if system == "windows":
        possible_paths = [
            "D:/godot/Godot_v4.4.1-stable_mono_win64.exe",
            "C:/godot/Godot_v4.4.1-stable_mono_win64.exe",
            "C:/Program Files/Godot/Godot.exe",
            "./Godot.exe",
            "./godot.exe"
        ]
        # 也检查PATH中的godot
        try:
            result = subprocess.run(["where", "godot"], capture_output=True, text=True)
            if result.returncode == 0:
                possible_paths.insert(0, result.stdout.strip().split('\n')[0])
        except:
            pass
            
    elif system == "darwin":  # macOS
        possible_paths = [
            "/Applications/Godot.app/Contents/MacOS/Godot",
            "/Applications/Godot_mono.app/Contents/MacOS/Godot",
            "/usr/local/bin/godot",
            "./godot"
        ]
        # 检查PATH中的godot
        try:
            result = subprocess.run(["which", "godot"], capture_output=True, text=True)
            if result.returncode == 0:
                possible_paths.insert(0, result.stdout.strip())
        except:
            pass
            
    else:  # Linux
        possible_paths = [
            "/usr/bin/godot",
            "/usr/local/bin/godot", 
            "/opt/godot/godot",
            "./godot",
            "../godot/godot"
        ]
        
        # WSL环境：添加Windows路径
        if "microsoft" in platform.release().lower() or "wsl" in platform.release().lower():
            possible_paths.extend([
                "/mnt/d/godot/Godot_v4.4.1-stable_mono_win64.exe",
                "/mnt/c/godot/Godot_v4.4.1-stable_mono_win64.exe",
                "/mnt/d/Godot/Godot.exe",
                "/mnt/c/Godot/Godot.exe"
            ])
        # 检查PATH中的godot
        try:
            result = subprocess.run(["which", "godot"], capture_output=True, text=True)
            if result.returncode == 0:
                possible_paths.insert(0, result.stdout.strip())
        except:
            pass
    
    # 寻找第一个存在的可执行文件
    for path in possible_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    return None

def main():
    print("🎮 Godot集成系统测试启动器")
    print(f"📍 操作系统: {platform.system()} {platform.release()}")
    
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    print(f"📁 项目目录: {script_dir}")
    
    # 查找Godot可执行文件
    godot_exec = find_godot_executable()
    
    if not godot_exec:
        print("❌ 未找到Godot可执行文件")
        print("请确保:")
        print("  1. Godot已正确安装")
        print("  2. Godot路径已添加到PATH环境变量")
        print("  3. 或者修改此脚本中的possible_paths")
        sys.exit(1)
    
    print(f"✅ 找到Godot: {godot_exec}")
    
    # 检查项目文件
    if not os.path.exists("project.godot"):
        print("❌ 未找到project.godot文件")
        print("请确保在Godot项目根目录运行此脚本")
        sys.exit(1)
    
    print("🚀 启动集成系统测试...")
    
    try:
        # WSL环境路径转换
        project_path = str(script_dir)
        if "microsoft" in platform.release().lower() or "wsl" in platform.release().lower():
            if godot_exec.endswith(".exe"):
                # 将WSL路径转换为Windows路径
                if project_path.startswith("/mnt/"):
                    drive = project_path[5]  # 获取盘符
                    path_rest = project_path[6:]  # 获取路径余下部分
                    project_path = f"{drive.upper()}:{path_rest}"
                    print(f"🔄 路径转换: {script_dir} -> {project_path}")
        
        # 运行Godot项目
        subprocess.run([godot_exec, "--path", project_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 用户中断")

if __name__ == "__main__":
    main()