#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态太阳系模拟器启动文件
展示基本渲染效果和动态优化
"""

import sys
import os
import traceback

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_opengl_support():
    """检查OpenGL支持情况"""
    try:
        import pygame
        from OpenGL.GL import *
        from OpenGL.GLU import *
        
        # 初始化Pygame
        pygame.init()
        
        # 尝试创建OpenGL上下文
        display = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)
        
        # 检查OpenGL版本
        version = glGetString(GL_VERSION).decode()
        renderer = glGetString(GL_RENDERER).decode()
        vendor = glGetString(GL_VENDOR).decode()
        
        print("✓ OpenGL支持检查通过")
        print(f"  版本: {version}")
        print(f"  渲染器: {renderer}")
        print(f"  供应商: {vendor}")
        
        # 检查扩展支持
        extensions = glGetString(GL_EXTENSIONS).decode().split()
        if 'GL_EXT_texture_filter_anisotropic' in extensions:
            print("  ✓ 支持各向异性过滤")
        else:
            print("  ⚠ 不支持各向异性过滤（将使用标准过滤）")
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"✗ OpenGL支持检查失败: {e}")
        print("请确保您的系统支持OpenGL，并已安装正确的显卡驱动")
        return False

def main():
    """主函数"""
    print("启动动态太阳系模拟器...")
    print("正在检查系统兼容性...")
    
    # 检查OpenGL支持
    if not check_opengl_support():
        print("\n系统兼容性检查失败，程序无法启动")
        print("请检查以下项目：")
        print("1. 显卡驱动是否最新")
        print("2. OpenGL是否支持")
        print("3. Python依赖是否正确安装")
        return
    
    print("\n系统兼容性检查通过！")
    print("特色功能：")
    print("- 太阳发光效果")
    print("- 行星基本颜色渲染")
    print("- 动态LOD优化")
    print("- 基本光照系统")
    print("- 真实轨道运动")
    print("- 相机自由控制")
    print("- 性能自适应")
    print()
    
    try:
        # 导入主模块
        from enhanced_solar_system import EnhancedSolarSystem
        
        # 创建太阳系模拟器
        print("正在初始化太阳系模拟器...")
        solar_system = EnhancedSolarSystem()
        
        # 运行模拟
        print("启动模拟...")
        solar_system.run()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except ImportError as e:
        print(f"\n模块导入失败: {e}")
        print("请检查所有依赖是否正确安装")
        print("运行命令: pip install -r requirements.txt")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        print("详细错误信息:")
        traceback.print_exc()
    finally:
        print("\n正在清理资源...")
        try:
            pygame.quit()
        except:
            pass
        print("程序结束")

if __name__ == "__main__":
    main()
