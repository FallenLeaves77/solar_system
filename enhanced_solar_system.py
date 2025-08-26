#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版太阳系模拟器
整合动态优化和基本渲染
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import time
import sys
import os

# 导入自定义模块
from enhanced_renderer import EnhancedRenderer
import config


class EnhancedSolarSystem:
    """增强版太阳系模拟器"""
    
    def __init__(self):
        pygame.init()
        
        # 设置显示
        self.width = config.SCREEN_WIDTH
        self.height = config.SCREEN_HEIGHT
        self.display = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("增强版太阳系模拟器 - 动态优化 + 基本渲染")
        
        # 初始化渲染器
        self.renderer = EnhancedRenderer()
        
        # 相机控制
        self.camera_distance = 200.0
        self.camera_x_rotation = 0.0
        self.camera_y_rotation = 0.0
        self.camera_speed = 2.0
        
        # 鼠标控制
        self.mouse_dragging = False
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.5
        
        # 天体数据
        self.celestial_bodies = self._initialize_celestial_bodies()
        
        # 时间控制
        self.time_speed = 1.0
        self.current_time = 0.0
        
        # 性能监控
        self.last_fps_update = time.time()
        self.frame_count = 0
        self.current_fps = 0
        
        # 设置OpenGL
        self._setup_opengl()
        
        print("增强版太阳系模拟器初始化完成！")
        print("功能特性：")
        print("- 动态LOD优化")
        print("- 基本光照效果")
        print("- 天体颜色渲染")
        print("- 鼠标自由观察")
        print("- 无限制缩放")
    
    def _setup_opengl(self):
        """设置OpenGL"""
        try:
            glViewport(0, 0, self.width, self.height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45, (self.width / self.height), 0.1, 1000.0)
            glMatrixMode(GL_MODELVIEW)
            
            # 启用深度测试和混合
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # 设置背景色 - 改为纯黑色
            glClearColor(0.0, 0.0, 0.0, 1.0)  # 从深蓝色改为纯黑色
            
            # 检查OpenGL版本和扩展支持
            print(f"OpenGL版本: {glGetString(GL_VERSION).decode()}")
            print(f"OpenGL渲染器: {glGetString(GL_RENDERER).decode()}")
            print(f"OpenGL供应商: {glGetString(GL_VENDOR).decode()}")
            
            # 检查关键扩展支持
            extensions = glGetString(GL_EXTENSIONS).decode().split()
            if 'GL_EXT_texture_filter_anisotropic' in extensions:
                print("支持各向异性过滤")
            else:
                print("不支持各向异性过滤")
                
        except Exception as e:
            print(f"OpenGL设置失败: {e}")
            sys.exit(1)
    
    def _initialize_celestial_bodies(self):
        """初始化天体数据"""
        return {
            "sun": {
                "position": [0, 0, 0],
                "radius": 15.0,
                "rotation_speed": 2.0,
                "orbit_radius": 0,
                "orbit_speed": 0,
                "texture": "sun",
                "has_atmosphere": False,
                "has_particles": False
            },
            "mercury": {
                "position": [0, 0, 0],
                "radius": 3.0,
                "rotation_speed": 1.0,
                "orbit_radius": 50.0,
                "orbit_speed": 0.5,
                "texture": "mercury",
                "has_atmosphere": False,
                "has_particles": False
            },
            "venus": {
                "position": [0, 0, 0],
                "radius": 4.0,
                "rotation_speed": 0.8,
                "orbit_radius": 80.0,
                "orbit_speed": 0.3,
                "texture": "venus",
                "has_atmosphere": False,
                "has_particles": False
            },
            "earth": {
                "position": [0, 0, 0],
                "radius": 5.0,
                "rotation_speed": 1.0,
                "orbit_radius": 120.0,
                "orbit_speed": 0.2,
                "texture": "earth",
                "has_atmosphere": False,
                "has_particles": False
            },
            "mars": {
                "position": [0, 0, 0],
                "radius": 3.5,
                "rotation_speed": 0.9,
                "orbit_radius": 160.0,
                "orbit_speed": 0.15,
                "texture": "mars",
                "has_atmosphere": False,
                "has_particles": False
            },
            "jupiter": {
                "position": [0, 0, 0],
                "radius": 12.0,
                "rotation_speed": 0.5,
                "orbit_radius": 220.0,
                "orbit_speed": 0.1,
                "texture": "jupiter",
                "has_atmosphere": False,
                "has_particles": False
            },
            "saturn": {
                "position": [0, 0, 0],
                "radius": 10.0,
                "rotation_speed": 0.6,
                "orbit_radius": 280.0,
                "orbit_speed": 0.08,
                "texture": "saturn",
                "has_atmosphere": False,
                "has_particles": False
            },
            "uranus": {
                "position": [0, 0, 0],
                "radius": 7.0,
                "rotation_speed": 0.7,
                "orbit_radius": 340.0,
                "orbit_speed": 0.06,
                "texture": "uranus",
                "has_atmosphere": False,
                "has_particles": False
            },
            "neptune": {
                "position": [0, 0, 0],
                "radius": 6.5,
                "rotation_speed": 0.8,
                "orbit_radius": 400.0,
                "orbit_speed": 0.05,
                "texture": "neptune",
                "has_atmosphere": False,
                "has_particles": False
            },
            "moon": {
                "position": [0, 0, 0],
                "radius": 1.5,
                "rotation_speed": 0.5,
                "orbit_radius": 8.0,
                "orbit_speed": 0.2,
                "texture": "moon",
                "has_atmosphere": False,
                "has_particles": False,
                "parent": "earth"
            }
        }
    
    def _update_celestial_positions(self):
        """更新天体位置 - 包括月球围绕地球公转"""
        # 首先更新行星位置（围绕太阳）
        for name, body in self.celestial_bodies.items():
            if body["orbit_radius"] > 0 and not body.get("parent"):
                # 计算轨道位置（围绕太阳）
                angle = self.current_time * body["orbit_speed"]
                body["position"][0] = math.cos(angle) * body["orbit_radius"]
                body["position"][1] = math.sin(angle) * body["orbit_radius"]
                body["position"][2] = 0  # 保持在XY平面上
        
        # 然后更新月球位置（围绕地球）
        if "moon" in self.celestial_bodies and "earth" in self.celestial_bodies:
            moon = self.celestial_bodies["moon"]
            earth = self.celestial_bodies["earth"]
            
            # 计算月球围绕地球的轨道位置
            moon_angle = self.current_time * moon["orbit_speed"]
            moon_orbit_x = math.cos(moon_angle) * moon["orbit_radius"]
            moon_orbit_y = math.sin(moon_angle) * moon["orbit_radius"]
            
            # 月球位置 = 地球位置 + 月球轨道位置
            moon["position"][0] = earth["position"][0] + moon_orbit_x
            moon["position"][1] = earth["position"][1] + moon_orbit_y
            moon["position"][2] = earth["position"][2] + 0  # 保持在XY平面上
    
    def _handle_input(self):
        """处理输入事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.time_speed = 0.0 if self.time_speed > 0 else 1.0
                elif event.key == pygame.K_UP:
                    self.time_speed = min(5.0, self.time_speed + 0.5)
                elif event.key == pygame.K_DOWN:
                    self.time_speed = max(0.0, self.time_speed - 0.5)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 鼠标左键
                    self.mouse_dragging = True
                    self.last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4:  # 滚轮上 - 无限制放大
                    self.camera_distance = max(1.0, self.camera_distance * 0.9)
                elif event.button == 5:  # 滚轮下 - 无限制缩小
                    self.camera_distance = min(1000.0, self.camera_distance * 1.1)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 鼠标左键释放
                    self.mouse_dragging = False
                    self.last_mouse_pos = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_dragging and self.last_mouse_pos:
                    # 计算鼠标移动距离
                    current_pos = pygame.mouse.get_pos()
                    dx = current_pos[0] - self.last_mouse_pos[0]
                    dy = current_pos[1] - self.last_mouse_pos[1]
                    
                    # 更新相机旋转
                    self.camera_y_rotation += dx * self.mouse_sensitivity
                    self.camera_x_rotation += dy * self.mouse_sensitivity
                    
                    # 限制垂直旋转角度，防止相机翻转
                    self.camera_x_rotation = max(-89.0, min(89.0, self.camera_x_rotation))
                    
                    self.last_mouse_pos = current_pos
        
        # 键盘持续输入
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.camera_y_rotation -= self.camera_speed
        if keys[pygame.K_RIGHT]:
            self.camera_y_rotation += self.camera_speed
        if keys[pygame.K_w]:
            self.camera_x_rotation -= self.camera_speed
        if keys[pygame.K_s]:
            self.camera_x_rotation += self.camera_speed
        
        return True
    
    def _update_camera(self):
        """更新相机位置"""
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.camera_x_rotation, 1, 0, 0)
        glRotatef(self.camera_y_rotation, 0, 1, 0)
    
    def _render_scene(self):
        """渲染场景 - 按照真实太阳系顺序"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 更新相机
        self._update_camera()
        
        # 渲染星空背景
        self.renderer.render_starfield([0, 0, 0])
        
        # 渲染轨道路径
        self._render_orbital_paths()
        
        # 更新光照位置（太阳位置）
        sun_position = self.celestial_bodies["sun"]["position"]
        self.renderer.update_lighting(sun_position)
        
        # 先渲染太阳（光源）
        if "sun" in self.celestial_bodies:
            sun = self.celestial_bodies["sun"]
            camera_pos = [0, 0, -self.camera_distance]
            sun_distance = math.sqrt(sum((sun["position"][i] - camera_pos[i]) ** 2 for i in range(3)))
            
            self.renderer.render_celestial_body(
                sun["texture"],
                sun["position"],
                sun["radius"],
                self.current_time * sun["rotation_speed"],
                sun_distance,
                use_animation=True
            )
        
        # 然后渲染其他天体，确保水星优先渲染
        other_bodies = [
            "mercury",  # 水星优先渲染
            "venus",    # 金星
            "earth",    # 地球
            "moon",     # 月球围绕地球
            "mars",     # 火星
            "jupiter",  # 木星
            "saturn",   # 土星
            "uranus",   # 天王星
            "neptune"   # 海王星最远
        ]
        
        for body_name in other_bodies:
            if body_name in self.celestial_bodies:
                body = self.celestial_bodies[body_name]
                
                # 计算到相机的距离
                camera_pos = [0, 0, -self.camera_distance]
                distance = math.sqrt(sum((body["position"][i] - camera_pos[i]) ** 2 for i in range(3)))
                
                # 对于水星，使用特殊的深度测试设置
                if body_name == "mercury":
                    glDepthFunc(GL_LEQUAL)  # 允许水星在太阳前面渲染
                
                # 渲染天体主体
                self.renderer.render_celestial_body(
                    body["texture"],
                    body["position"],
                    body["radius"],
                    self.current_time * body["rotation_speed"],  # 自转
                    distance,
                    use_animation=True
                )
                
                # 恢复默认深度测试
                if body_name == "mercury":
                    glDepthFunc(GL_LESS)
                    
                # 渲染大气效果
                if body["has_atmosphere"]:
                    self.renderer.render_atmosphere_effects(
                        body["texture"],
                        body["position"],
                        body["radius"],
                        distance
                    )
                
                # 渲染粒子效果
                if body["has_particles"]:
                    self.renderer.render_particle_effects(
                        body["texture"],
                        body["position"],
                        body["radius"],
                        distance
                    )
    
    def _render_ui(self):
        """渲染UI信息"""
        # 切换到2D模式
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # 禁用光照和深度测试
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # 渲染文本信息
        font = pygame.font.Font(None, 36)
        
        # FPS信息
        fps_text = font.render(f"FPS: {self.renderer.get_current_fps()}", True, (255, 255, 255))
        self.display.blit(fps_text, (10, 10))
        
        # 时间速度
        speed_text = font.render(f"时间速度: {self.time_speed:.1f}x", True, (255, 255, 255))
        self.display.blit(speed_text, (10, 50))
        
        # 相机距离
        distance_text = font.render(f"相机距离: {self.camera_distance:.0f}", True, (255, 255, 255))
        self.display.blit(distance_text, (10, 90))
        
        # 太阳系信息
        info_font = pygame.font.Font(None, 28)
        info_text = [
            f"太阳系天体: {len(self.celestial_bodies)}个",
            "太阳 + 8大行星 + 月球",
            "按真实比例排列"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = info_font.render(text, True, (200, 255, 200))
            self.display.blit(text_surface, (10, 130 + i * 25))
        
        # 控制说明
        controls_font = pygame.font.Font(None, 24)
        controls = [
            "控制说明:",
            "WASD - 旋转相机",
            "鼠标左键拖拽 - 自由观察",
            "鼠标滚轮 - 无限制缩放",
            "空格 - 暂停/继续",
            "上下箭头 - 调整时间速度",
            "ESC - 退出"
        ]
        
        for i, control in enumerate(controls):
            control_text = controls_font.render(control, True, (200, 200, 200))
            self.display.blit(control_text, (10, 270 + i * 25))
        
        # 恢复3D模式
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        # 重新启用光照和深度测试
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
    
    def _update_fps(self):
        """更新FPS计算"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
    
    def _render_orbital_paths(self):
        """渲染轨道路径 - 包括月球轨道"""
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
        
        # 渲染行星轨道（围绕太阳）
        for name, body in self.celestial_bodies.items():
            if body["orbit_radius"] > 0 and not body.get("parent"):
                self._render_single_orbit([0, 0, 0], body["orbit_radius"], (100, 100, 100))
        
        # 渲染月球轨道（围绕地球）
        if "moon" in self.celestial_bodies and "earth" in self.celestial_bodies:
            earth = self.celestial_bodies["earth"]
            moon = self.celestial_bodies["moon"]
            self._render_single_orbit(earth["position"], moon["orbit_radius"], (150, 150, 150))
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
    
    def _render_single_orbit(self, center, radius, color):
        """渲染单个轨道"""
        glColor3f(color[0]/255.0, color[1]/255.0, color[2]/255.0)
        glBegin(GL_LINE_LOOP)
        
        segments = 64
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            x = center[0] + math.cos(angle) * radius
            y = center[1] + math.sin(angle) * radius
            z = center[2]
            glVertex3f(x, y, z)
        
        glEnd()
        glColor3f(1.0, 1.0, 1.0)  # 恢复白色
    
    def run(self):
        """运行主循环"""
        print("开始运行增强版太阳系模拟器...")
        print("按ESC键退出，空格键暂停/继续")
        
        running = True
        clock = pygame.time.Clock()
        
        # 初始化完成
        print("初始化完成，开始运行...")
        
        try:
            while running:
                # 处理输入
                running = self._handle_input()
                

                
                # 更新时间
                self.current_time += self.time_speed * 0.01
                
                # 更新天体位置
                self._update_celestial_positions()
                
                # 渲染场景
                self._render_scene()
                
                # 渲染UI
                self._render_ui()
                
                # 更新显示
                pygame.display.flip()
                
                # 更新FPS
                self._update_fps()
                
                # 控制帧率
                clock.tick(60)
                
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"运行时错误: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        print("正在清理资源...")
        self.renderer.cleanup()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    try:
        # 检查依赖
        print("依赖包检查通过")
        
        # 运行模拟器
        simulator = EnhancedSolarSystem()
        simulator.run()
        
    except ImportError as e:
        print(f"缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
    except Exception as e:
        print(f"程序启动失败: {e}") 