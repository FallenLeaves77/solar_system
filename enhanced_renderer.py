#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强3D渲染器
包含动态优化、光照效果和逼真渲染
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import time
from advanced_texture_manager import AdvancedTextureManager
from celestial_appearance_manager import CelestialAppearanceManager


class EnhancedRenderer:
    """增强3D渲染器 - 动态优化 + 逼真效果 + 天体外观管理"""
    
    def __init__(self):
        self.texture_manager = AdvancedTextureManager()
        self.appearance_manager = CelestialAppearanceManager()
        
        # 光照设置 - 大幅提高亮度
        self.light_position = [0.0, 0.0, 100.0]
        self.light_color = [1.0, 1.0, 1.0]
        self.ambient_light = [0.6, 0.6, 0.6]  # 提高环境光从0.2到0.6
        self.diffuse_light = [1.0, 1.0, 1.0]  # 提高漫反射光从0.8到1.0
        self.specular_light = [1.0, 1.0, 1.0]
        self.shininess = 80.0  # 降低反光度，让表面更亮
        
        # 动态优化参数
        self.lod_distance = 50.0
        self.max_vertices = 1000
        self.adaptive_quality = True
        
        # 渲染统计
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0
        
        self._setup_lighting()
        self._setup_shaders()
    
    def _setup_lighting(self):
        """设置光照系统"""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 设置光照参数
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient_light)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse_light)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular_light)
        
        # 材质属性 - 提高亮度
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.6, 0.6, 0.6, 1.0])  # 提高环境材质从0.2到0.6
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # 提高漫反射材质从0.8到1.0
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, self.shininess)
    
    def _setup_shaders(self):
        """设置着色器（如果支持）"""
        try:
            # 这里可以添加自定义着色器代码
            # 目前使用OpenGL固定管线
            pass
        except Exception as e:
            print(f"着色器设置失败: {e}")
    
    def render_celestial_body(self, body_name, position, radius, rotation_angle, 
                            distance_from_camera, use_animation=True):
        """渲染天体 - 使用外观管理器"""
        # 动态LOD（细节层次）优化
        detail_level = self._calculate_lod_level(distance_from_camera)
        
        # 更新动画
        if use_animation:
            self.texture_manager.update_animations()
            self.appearance_manager.update_animations()
        
        # 使用外观管理器渲染天体
        self.appearance_manager.render_celestial_body(
            body_name, position, radius, rotation_angle, 
            distance_from_camera, self.texture_manager
        )
        
        # 更新渲染统计
        self._update_render_stats()
    
    def _calculate_lod_level(self, distance):
        """计算细节层次"""
        if distance < self.lod_distance * 0.5:
            return 32  # 高细节
        elif distance < self.lod_distance:
            return 24  # 中等细节
        elif distance < self.lod_distance * 2:
            return 16  # 低细节
        else:
            return 8   # 最低细节
    
    def render_atmosphere_effects(self, body_name, position, radius, distance_from_camera):
        """渲染大气效果 - 现在由外观管理器处理"""
        # 大气效果现在由外观管理器统一处理
        pass
    
    def render_particle_effects(self, body_name, position, radius, distance_from_camera):
        """渲染粒子效果"""
        if body_name == "sun":
            self._render_solar_particles(position, radius)
        elif body_name == "earth":
            self._render_earth_particles(position, radius)
        # 木星特殊渲染
        elif body_name == "jupiter":
            # 渲染木星本体
            glMaterialfv(GL_FRONT, GL_AMBIENT, [0.8, 0.6, 0.4, 1.0])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.6, 0.4, 1.0])
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
            
            # 渲染木星球体
            self._render_sphere(radius, 32, "jupiter")
            
            # 木星粒子效果已禁用，保持静态显示
            # self._render_jupiter_particles(position, radius)
    
    def _render_solar_particles(self, position, radius):
        """渲染太阳粒子效果"""
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])
        
        # 启用混合
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 渲染太阳风粒子
        particle_count = 50
        for i in range(particle_count):
            angle = (i / particle_count) * 2 * math.pi
            distance = radius * (1.5 + (i % 3) * 0.2)
            
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            
            # 粒子大小和透明度
            size = 0.5 + (i % 3) * 0.3
            alpha = 0.6 - (i % 3) * 0.2
            
            glMaterialfv(GL_FRONT, GL_AMBIENT, [1.0, 0.8, 0.2, alpha])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.8, 0.2, alpha])
            
            # 渲染粒子
            glBegin(GL_QUADS)
            glVertex3f(x - size, y - size, 0)
            glVertex3f(x + size, y - size, 0)
            glVertex3f(x + size, y + size, 0)
            glVertex3f(x - size, y + size, 0)
            glEnd()
        
        glDisable(GL_BLEND)
        glPopMatrix()
    
    def _render_earth_particles(self, position, radius):
        """渲染地球粒子效果"""
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])
        
        # 启用混合
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 渲染云层粒子
        particle_count = 30
        for i in range(particle_count):
            angle = (i / particle_count) * 2 * math.pi
            distance = radius * (1.02 + (i % 2) * 0.01)
            
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            
            # 粒子大小和透明度
            size = 0.3 + (i % 2) * 0.2
            alpha = 0.4 - (i % 2) * 0.1
            
            glMaterialfv(GL_FRONT, GL_AMBIENT, [1.0, 1.0, 1.0, alpha])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 1.0, alpha])
            
            # 渲染粒子
            glBegin(GL_QUADS)
            glVertex3f(x - size, y - size, 0)
            glVertex3f(x + size, y - size, 0)
            glVertex3f(x + size, y + size, 0)
            glVertex3f(x - size, y + size, 0)
            glEnd()
        
        glDisable(GL_BLEND)
        glPopMatrix()
    
    def _render_jupiter_particles(self, position, radius):
        """渲染木星粒子效果 - 已禁用"""
        # 木星粒子效果已禁用，保持静态显示
        pass
    
    def render_orbital_paths(self, celestial_bodies):
        """渲染轨道路径"""
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        
        for body_name, body_data in celestial_bodies.items():
            if body_data.get("orbit_radius", 0) > 0:
                # 检查是否有父天体（卫星系统）
                if "parent" in body_data and body_data["parent"] in celestial_bodies:
                    # 渲染卫星轨道（相对于父天体）
                    parent_body = celestial_bodies[body_data["parent"]]
                    parent_pos = parent_body["position"]
                    self._render_orbital_path_relative(body_data["orbit_radius"], parent_pos)
                else:
                    # 渲染行星轨道（围绕太阳）
                    self._render_orbital_path(body_data["orbit_radius"])
        
        glEnable(GL_LIGHTING)
    
    def _render_orbital_path(self, orbit_radius):
        """渲染单个轨道路径"""
        glColor3f(0.3, 0.3, 0.5)
        glLineWidth(1.0)
        
        glBegin(GL_LINE_LOOP)
        segments = 64
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = math.cos(angle) * orbit_radius
            y = math.sin(angle) * orbit_radius
            glVertex3f(x, y, 0)
        glEnd()
        
        glColor3f(1.0, 1.0, 1.0)  # 重置颜色
    
    def _render_orbital_path_relative(self, orbit_radius, parent_position):
        """渲染相对于父天体的轨道路径"""
        glColor3f(0.2, 0.2, 0.4)  # 稍微不同的颜色表示卫星轨道
        glLineWidth(0.8)  # 稍微细一点的线条
        
        glPushMatrix()
        glTranslatef(parent_position[0], parent_position[1], parent_position[2])
        
        glBegin(GL_LINE_LOOP)
        segments = 32  # 卫星轨道使用较少的段数
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = math.cos(angle) * orbit_radius
            y = math.sin(angle) * orbit_radius
            glVertex3f(x, y, 0)
        glEnd()
        
        glPopMatrix()
        glColor3f(1.0, 1.0, 1.0)  # 重置颜色
    
    def render_starfield(self, camera_position):
        """渲染星空背景 - 静态分布，不闪烁"""
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        
        # 生成静态星星 - 增加数量，固定位置
        star_count = 2000  # 从1000增加到2000
        glPointSize(1.5)  # 稍微增大星星尺寸
        
        # 使用固定的随机种子确保星星位置不变
        np.random.seed(42)
        
        glBegin(GL_POINTS)
        for i in range(star_count):
            # 生成随机位置 - 使用固定种子确保位置不变
            x = (np.random.random() - 0.5) * 1500  # 扩大星空范围
            y = (np.random.random() - 0.5) * 1500
            z = (np.random.random() - 0.5) * 1500
            
            # 根据距离调整亮度 - 让星星更亮
            distance = math.sqrt(x*x + y*y + z*z)
            if distance > 150:  # 调整距离阈值
                # 提高星星亮度，减少闪烁
                brightness = np.random.random() * 0.4 + 0.6  # 从0.2-1.0改为0.6-1.0
                # 添加一些彩色星星
                if np.random.random() < 0.3:  # 30%的星星有颜色
                    r = brightness
                    g = brightness * 0.8
                    b = brightness * 1.2
                else:
                    r = g = b = brightness
                
                glColor3f(r, g, b)
                glVertex3f(x, y, z)
        
        glEnd()
        
        # 重置随机种子
        np.random.seed()
        
        glColor3f(1.0, 1.0, 1.0)  # 重置颜色
        glEnable(GL_LIGHTING)
    
    def render_ui_overlay(self, celestial_bodies, camera_distance, fps):
        """渲染UI覆盖层"""
        # 这里可以添加UI元素，如信息面板、控制按钮等
        pass
    
    def _update_render_stats(self):
        """更新渲染统计"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time
    
    def get_current_fps(self):
        """获取当前FPS"""
        return self.current_fps
    
    def set_quality_level(self, level):
        """设置质量等级"""
        quality_levels = {
            "low": {"lod_distance": 30, "max_vertices": 500},
            "medium": {"lod_distance": 50, "max_vertices": 1000},
            "high": {"lod_distance": 80, "max_vertices": 2000},
            "ultra": {"lod_distance": 120, "max_vertices": 4000}
        }
        
        if level in quality_levels:
            config = quality_levels[level]
            self.lod_distance = config["lod_distance"]
            self.max_vertices = config["max_vertices"]
            print(f"质量等级设置为: {level}")
    
    def set_animation_speed(self, speed):
        """设置动画速度"""
        self.appearance_manager.set_animation_speed(speed)
        print(f"动画速度设置为: {speed}")
    
    def update_lighting(self, sun_position=None):
        """更新光照系统"""
        # 如果提供了太阳位置，更新光照位置
        if sun_position is not None:
            self.light_position = [sun_position[0], sun_position[1], sun_position[2] + 100.0]
        
        # 更新光照位置和参数
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient_light)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse_light)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular_light)
    
    def cleanup(self):
        """清理资源"""
        self.texture_manager.cleanup()
        print("渲染器资源清理完成") 