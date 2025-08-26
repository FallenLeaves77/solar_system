#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强3D渲染器
包含动态优化、光照效果和基本渲染
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import time


class EnhancedRenderer:
    """增强3D渲染器 - 动态优化 + 基本渲染"""
    
    def __init__(self):
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
        """渲染天体 - 基本渲染"""
        # 动态LOD（细节层次）优化
        detail_level = self._calculate_lod_level(distance_from_camera)
        
        # 保存当前矩阵
        glPushMatrix()
        
        # 移动到天体位置
        glTranslatef(position[0], position[1], position[2])
        
        # 应用旋转
        glRotatef(rotation_angle, 0, 1, 0)
        
        # 根据天体类型设置颜色和材质
        self._set_celestial_material(body_name)
        
        # 渲染球体
        self._render_sphere(radius, detail_level)
        
        # 恢复矩阵
        glPopMatrix()
        
        # 更新渲染统计
        self._update_render_stats()
    
    def _calculate_lod_level(self, distance):
        """计算细节层次"""
        if distance < self.lod_distance * 0.5:
            return 32  # 高细节
        elif distance < self.lod_distance:
            return 24  # 中等细节
        else:
            return 16  # 低细节
    
    def _set_celestial_material(self, body_name):
        """设置天体材质和颜色"""
        # 根据天体类型设置不同的颜色
        colors = {
            "sun": [1.0, 0.8, 0.0, 1.0],      # 金黄色
            "mercury": [0.7, 0.7, 0.7, 1.0],   # 灰色
            "venus": [1.0, 0.6, 0.3, 1.0],     # 橙黄色
            "earth": [0.2, 0.5, 0.8, 1.0],     # 蓝色
            "mars": [0.8, 0.3, 0.2, 1.0],      # 红色
            "jupiter": [0.8, 0.6, 0.4, 1.0],   # 棕黄色
            "saturn": [0.9, 0.8, 0.6, 1.0],    # 淡黄色
            "uranus": [0.4, 0.7, 0.8, 1.0],    # 青蓝色
            "neptune": [0.2, 0.4, 0.8, 1.0],   # 深蓝色
            "moon": [0.8, 0.8, 0.8, 1.0]       # 银灰色
        }
        
        color = colors.get(body_name, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, color)
        
        # 特殊天体处理
        if body_name == "sun":
            # 太阳发光效果
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.3, 0.2, 0.0, 1.0])
        else:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
    
    def _render_sphere(self, radius, detail_level):
        """渲染球体"""
        # 使用OpenGL的球体函数
        quad = gluNewQuadric()
        gluSphere(quad, radius, detail_level, detail_level)
        gluDeleteQuadric(quad)
    
    def _update_render_stats(self):
        """更新渲染统计"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
    
    def get_fps(self):
        """获取当前FPS"""
        return self.current_fps
    
    def get_current_fps(self):
        """获取当前FPS（兼容性方法）"""
        return self.current_fps
    
    def render_starfield(self, center_position):
        """渲染星空背景"""
        # 禁用光照和深度测试，确保星空在最底层
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # 保存当前矩阵
        glPushMatrix()
        
        # 移动到中心位置
        glTranslatef(center_position[0], center_position[1], center_position[2])
        
        # 设置星空颜色（白色小点）
        glColor3f(1.0, 1.0, 1.0)
        
        # 渲染随机分布的星星
        glBegin(GL_POINTS)
        for i in range(1000):  # 1000颗星星
            # 在球面上随机分布
            phi = np.random.uniform(0, 2 * np.pi)
            theta = np.arccos(np.random.uniform(-1, 1))
            
            # 转换为笛卡尔坐标
            x = 1000 * np.sin(theta) * np.cos(phi)
            y = 1000 * np.sin(theta) * np.sin(phi)
            z = 1000 * np.cos(theta)
            
            glVertex3f(x, y, z)
        glEnd()
        
        # 恢复颜色
        glColor3f(1.0, 1.0, 1.0)
        
        # 恢复矩阵
        glPopMatrix()
        
        # 重新启用光照和深度测试
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
    
    def update_lighting(self, sun_position):
        """更新光照位置（太阳位置）"""
        self.light_position = list(sun_position)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
    
    def render_atmosphere_effects(self, body_name, position, radius, distance):
        """渲染大气效果"""
        # 简化的大气效果 - 渲染一个半透明的球体
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 保存当前矩阵
        glPushMatrix()
        
        # 移动到天体位置
        glTranslatef(position[0], position[1], position[2])
        
        # 设置大气颜色（根据天体类型）
        if body_name == "earth":
            glColor4f(0.5, 0.8, 1.0, 0.1)  # 地球蓝色大气
        elif body_name == "venus":
            glColor4f(1.0, 0.8, 0.5, 0.2)  # 金星橙色大气
        else:
            glColor4f(0.8, 0.8, 0.8, 0.1)  # 默认灰色大气
        
        # 渲染稍大的球体作为大气
        self._render_sphere(radius * 1.1, 16)
        
        # 恢复颜色
        glColor3f(1.0, 1.0, 1.0)
        
        # 恢复矩阵
        glPopMatrix()
        
        glDisable(GL_BLEND)
    
    def render_particle_effects(self, body_name, position, radius, distance):
        """渲染粒子效果"""
        # 简化的粒子效果 - 渲染一些随机点
        if body_name == "saturn":
            # 土星环效果
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            glPushMatrix()
            glTranslatef(position[0], position[1], position[2])
            
            # 设置环的颜色
            glColor4f(0.8, 0.7, 0.5, 0.6)  # 土星环颜色
            
            # 渲染简单的环
            glBegin(GL_QUADS)
            ring_radius = radius * 1.5
            ring_thickness = radius * 0.1
            
            for i in range(32):
                angle1 = i * 2 * np.pi / 32
                angle2 = (i + 1) * 2 * np.pi / 32
                
                x1 = ring_radius * np.cos(angle1)
                z1 = ring_radius * np.sin(angle1)
                x2 = ring_radius * np.cos(angle2)
                z2 = ring_radius * np.sin(angle2)
                
                glVertex3f(x1, -ring_thickness/2, z1)
                glVertex3f(x2, -ring_thickness/2, z2)
                glVertex3f(x2, ring_thickness/2, z2)
                glVertex3f(x1, ring_thickness/2, z1)
            glEnd()
            
            glColor3f(1.0, 1.0, 1.0)
            glPopMatrix()
            glDisable(GL_BLEND)
    
    def cleanup(self):
        """清理资源"""
        # 清理OpenGL状态
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_BLEND) 