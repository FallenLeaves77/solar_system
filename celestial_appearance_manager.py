#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天体外观管理器
根据真实图片样式渲染天体的外观特征
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import time
from PIL import Image, ImageEnhance, ImageFilter
import cv2


class CelestialAppearanceManager:
    """天体外观管理器 - 根据真实图片样式渲染"""
    
    def __init__(self):
        # 天体外观特征配置
        self.appearance_configs = {
            "sun": {
                "surface_features": ["solar_flares", "sunspots"],  # 删除corona
                "color_temperature": 5778,  # 开尔文
                "brightness": 1.5,  # 从1.0提高到1.5
                "glow_radius": 1.0,  # 设置为1.0，无光晕
                "surface_detail": "high",
                "animation_speed": 2.0,
                "special_effects": []  # 完全删除所有特效
            },
            "mercury": {
                "surface_features": ["craters", "basins", "scarps"],
                "color_temperature": 440,  # 开尔文
                "brightness": 0.8,  # 从0.3提高到0.8
                "glow_radius": 1.0,
                "surface_detail": "high",
                "animation_speed": 1.0,
                "special_effects": ["crater_shadows", "thermal_variation"]
            },
            "venus": {
                "surface_features": ["clouds", "volcanoes"],  # 删除atmosphere
                "color_temperature": 737,  # 开尔文
                "brightness": 1.2,  # 从0.7提高到1.2
                "glow_radius": 1.0,  # 从1.1降低到1.0，无光晕
                "surface_detail": "medium",
                "animation_speed": 0.8,
                "special_effects": ["cloud_movement"]  # 删除atmospheric_scattering
            },
            "earth": {
                "surface_features": ["continents", "oceans", "clouds", "atmosphere"],
                "color_temperature": 288,  # 开尔文
                "brightness": 1.3,  # 从0.8提高到1.3
                "glow_radius": 1.05,
                "surface_detail": "ultra_high",
                "animation_speed": 1.0,
                "special_effects": ["cloud_rotation", "atmospheric_glow", "aurora"]
            },
            "mars": {
                "surface_features": ["craters", "canyons", "volcanoes", "dust_storms"],
                "color_temperature": 210,  # 开尔文
                "brightness": 0.9,  # 从0.4提高到0.9
                "glow_radius": 1.0,
                "surface_detail": "high",
                "animation_speed": 0.9,
                "special_effects": ["dust_storm", "seasonal_changes"]
            },
            "jupiter": {
                "surface_features": ["bands", "spots", "storms", "atmosphere"],
                "color_temperature": 165,  # 开尔文
                "brightness": 1.1,  # 从0.6提高到1.1
                "glow_radius": 1.15,
                "surface_detail": "high",
                "animation_speed": 0.0,  # 设置为0，完全禁用动画
                "special_effects": []  # 移除所有特殊效果
            },
            "saturn": {
                "surface_features": ["rings", "bands", "storms", "atmosphere"],
                "color_temperature": 134,  # 开尔文
                "brightness": 1.0,  # 从0.5提高到1.0
                "glow_radius": 1.1,
                "surface_detail": "high",
                "animation_speed": 1.8,
                "special_effects": ["ring_shadows", "band_movement", "storm_systems"]
            },
            "uranus": {
                "surface_features": ["bands", "storms"],
                "color_temperature": 76,  # 开尔文
                "brightness": 0.8,  # 从0.3提高到0.8
                "glow_radius": 1.0,
                "surface_detail": "medium",
                "animation_speed": 1.5,
                "special_effects": ["atmospheric_bands"]
            },
            "neptune": {
                "surface_features": ["storms", "bands", "atmosphere"],
                "color_temperature": 72,  # 开尔文
                "brightness": 0.8,  # 从0.3提高到0.8
                "glow_radius": 1.0,
                "surface_detail": "medium",
                "animation_speed": 1.6,
                "special_effects": ["storm_systems", "atmospheric_movement"]
            },
            "moon": {
                "surface_features": ["craters", "highlands", "maria"],
                "color_temperature": 250,  # 开尔文
                "brightness": 0.7,  # 从0.2提高到0.7
                "glow_radius": 1.0,
                "surface_detail": "high",
                "animation_speed": 0.5,
                "special_effects": ["crater_shadows", "phase_effects"]
            }
        }
        
        # 特殊效果参数
        self.effect_params = {
            "corona_glow": {"intensity": 0.8, "radius": 1.5, "color": [1.0, 0.8, 0.2]},
            "atmospheric_scattering": {"intensity": 0.4, "radius": 1.1, "color": [0.8, 0.6, 0.4]},
            "aurora": {"intensity": 0.6, "radius": 1.05, "color": [0.2, 0.8, 0.4]},
            "dust_storm": {"intensity": 0.3, "radius": 1.02, "color": [0.6, 0.4, 0.2]},
            "storm_rotation": {"intensity": 0.3, "radius": 1.03, "color": [0.7, 0.5, 0.3]}  # 从0.5降低到0.3
        }
        
        # 动画状态
        self.animation_time = 0.0
        self.animation_speed = 1.0
        
        # 初始化着色器
        self._setup_shaders()
    
    def _setup_shaders(self):
        """设置着色器（如果支持）"""
        try:
            # 这里可以添加自定义着色器代码
            # 目前使用OpenGL固定管线
            pass
        except Exception as e:
            print(f"着色器设置失败: {e}")
    
    def get_appearance_config(self, body_name):
        """获取天体外观配置"""
        return self.appearance_configs.get(body_name, {})
    
    def render_celestial_body(self, body_name, position, radius, rotation_angle, 
                            distance_from_camera, texture_manager):
        """渲染天体外观"""
        config = self.get_appearance_config(body_name)
        if not config:
            return
        
        glPushMatrix()
        
        # 应用变换
        glTranslatef(position[0], position[1], position[2])
        glRotatef(rotation_angle, 0, 0, 1)
        
        # 根据距离应用缩放
        scale_factor = 1.0 + (distance_from_camera / 1000.0) * 0.1
        glScalef(scale_factor, scale_factor, scale_factor)
        
        # 渲染主体
        self._render_body_main(body_name, radius, config, texture_manager)
        
        # 渲染特殊效果
        self._render_special_effects(body_name, radius, config, distance_from_camera)
        
        # 渲染大气层（如果有）
        if "atmosphere" in config.get("surface_features", []):
            self._render_atmosphere(body_name, radius, config, distance_from_camera)
        
        # 渲染光环（只有土星有光环）
        if body_name == "saturn":
            self._render_rings(body_name, radius, config, distance_from_camera)
        
        glPopMatrix()
        
        # 更新动画时间
        self.animation_time += time.time() * self.animation_speed * config.get("animation_speed", 1.0)
    
    def _render_body_main(self, body_name, radius, config, texture_manager):
        """渲染天体主体"""
        # 设置材质属性
        self._set_body_material(body_name, config)
        
        # 绑定纹理
        texture_manager.bind_texture(body_name)
        
        # 渲染球体
        detail_level = self._calculate_detail_level(config.get("surface_detail", "medium"))
        self._render_sphere(radius, detail_level, body_name)
        
        # 解绑纹理
        texture_manager.unbind_texture()
    
    def _set_body_material(self, body_name, config):
        """设置天体材质属性"""
        # 根据颜色温度设置材质
        color_temp = config.get("color_temperature", 300)
        brightness = config.get("brightness", 0.5)
        
        # 计算RGB颜色（简化版）
        if color_temp > 5000:  # 高温（太阳）
            color = [1.0, 0.8, 0.2]
        elif color_temp > 3000:  # 中高温（金星）
            color = [0.8, 0.6, 0.4]
        elif color_temp > 1000:  # 中温（地球、火星）
            color = [0.6, 0.5, 0.4]
        else:  # 低温（气态行星）
            color = [0.4, 0.3, 0.2]
        
        # 应用亮度
        color = [c * brightness for c in color]
        
        # 设置材质属性 - 提高亮度
        glMaterialfv(GL_FRONT, GL_AMBIENT, [color[0] * 0.4, color[1] * 0.4, color[2] * 0.4, 1.0])  # 从0.2提高到0.4
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [color[0] * 1.0, color[1] * 1.0, color[2] * 1.0, 1.0])  # 从0.8提高到1.0
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 40.0)  # 从50.0降低到40.0，让表面更亮
    
    def _calculate_detail_level(self, detail_level):
        """计算细节层次"""
        detail_map = {
            "ultra_high": 48,
            "high": 32,
            "medium": 24,
            "low": 16
        }
        return detail_map.get(detail_level, 24)
    
    def _render_sphere(self, radius, detail_level, body_name):
        """渲染球体"""
        # 使用球面坐标生成顶点
        vertices = []
        normals = []
        tex_coords = []
        
        for i in range(detail_level + 1):
            lat = math.pi * (-0.5 + float(i) / detail_level)
            for j in range(detail_level + 1):
                lon = 2 * math.pi * float(j) / detail_level
                
                x = math.cos(lat) * math.cos(lon)
                y = math.cos(lat) * math.sin(lon)
                z = math.sin(lat)
                
                # 顶点位置
                vertices.extend([x * radius, y * radius, z * radius])
                
                # 法向量（用于光照）
                normals.extend([x, y, z])
                
                # 纹理坐标 - 使用优化的球面映射
                u, v = self._calculate_optimal_uv(lat, lon, i, j, detail_level)
                tex_coords.extend([u, v])
        
        # 生成索引
        indices = []
        for i in range(detail_level):
            for j in range(detail_level):
                first = i * (detail_level + 1) + j
                second = first + detail_level + 1
                
                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])
        
        # 渲染球体
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        
        glVertexPointer(3, GL_FLOAT, 0, vertices)
        glNormalPointer(GL_FLOAT, 0, normals)
        glTexCoordPointer(2, GL_FLOAT, 0, tex_coords)
        
        # 使用索引渲染
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    
    def _calculate_optimal_uv(self, lat, lon, i, j, detail_level):
        """计算最优的UV坐标，确保贴图完全覆盖球体"""
        # U坐标：经度，确保无缝连接
        u = j / detail_level
        
        # V坐标：使用改进的等面积投影，避免极地变形
        # 将球面坐标转换为等面积投影的V坐标
        sin_lat = math.sin(lat)
        
        # 使用等面积投影公式，确保贴图完全覆盖
        if abs(sin_lat) < 0.999:  # 非极地区域
            # 等面积投影：v = 0.5 * (1 - sin(lat))
            v = 0.5 * (1.0 - sin_lat)
        else:  # 极地区域，使用线性插值避免变形
            v = 0.0 if sin_lat > 0 else 1.0
        
        # 确保UV坐标在有效范围内
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))
        
        return u, v
    
    def _render_special_effects(self, body_name, radius, config, distance_from_camera):
        """渲染特殊效果"""
        effects = config.get("special_effects", [])
        
        for effect in effects:
            if effect in self.effect_params:
                params = self.effect_params[effect]
                self._render_effect(effect, radius, params, distance_from_camera)
    
    def _render_effect(self, effect_name, radius, params, distance_from_camera):
        """渲染单个特效"""
        glPushMatrix()
        
        # 启用混合
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 设置特效材质
        color = params["color"]
        intensity = params["intensity"]
        effect_radius = radius * params["radius"]
        
        glMaterialfv(GL_FRONT, GL_AMBIENT, [color[0] * intensity, color[1] * intensity, color[2] * intensity, 0.3])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [color[0] * intensity, color[1] * intensity, color[2] * intensity, 0.3])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 0.5])
        
        # 根据特效类型渲染
        if effect_name == "corona_glow":
            self._render_corona_glow(effect_radius, params)
        elif effect_name == "atmospheric_scattering":
            self._render_atmospheric_scattering(effect_radius, params)
        elif effect_name == "aurora":
            self._render_aurora(effect_radius, params)
        elif effect_name == "dust_storm":
            self._render_dust_storm(effect_radius, params)
        elif effect_name == "storm_rotation":
            self._render_storm_rotation(effect_radius, params)
        
        glDisable(GL_BLEND)
        glPopMatrix()
    
    def _render_corona_glow(self, radius, params):
        """渲染日冕光晕"""
        # 渲染多层光晕
        for i in range(3):
            alpha = 0.1 - i * 0.03
            glow_radius = radius * (1.0 + i * 0.2)
            
            glMaterialfv(GL_FRONT, GL_AMBIENT, [1.0, 0.8, 0.2, alpha])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.8, 0.2, alpha])
            
            self._render_sphere(glow_radius, 16, "corona")
    
    def _render_atmospheric_scattering(self, radius, params):
        """渲染大气散射"""
        # 渲染大气层
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.8, 0.6, 0.4, 0.2])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.6, 0.4, 0.2])
        
        self._render_sphere(radius, 16, "atmosphere")
    
    def _render_aurora(self, radius, params):
        """渲染极光效果"""
        # 渲染极光带
        aurora_radius = radius * 1.02
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.8, 0.4, 0.4])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.2, 0.8, 0.4, 0.4])
        
        # 渲染极光环
        self._render_aurora_ring(aurora_radius)
    
    def _render_aurora_ring(self, radius):
        """渲染极光环"""
        # 简化的极光环渲染
        glBegin(GL_LINES)
        for i in range(36):
            angle = i * 10 * math.pi / 180
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            glVertex3f(x, y, 0)
            glVertex3f(x, y, radius * 0.1)
        glEnd()
    
    def _render_dust_storm(self, radius, params):
        """渲染沙尘暴效果"""
        # 渲染沙尘云
        dust_radius = radius * 1.01
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.6, 0.4, 0.2, 0.3])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.6, 0.4, 0.2, 0.3])
        
        self._render_sphere(dust_radius, 16, "dust")
    
    def _render_storm_rotation(self, radius, params):
        """渲染风暴旋转效果"""
        # 渲染风暴云
        storm_radius = radius * 1.02
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.7, 0.5, 0.3, 0.25])  # 从0.4降低到0.25
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.7, 0.5, 0.3, 0.25])  # 从0.4降低到0.25
        
        # 根据动画时间旋转
        glRotatef(self.animation_time * 10, 0, 0, 1)
        self._render_sphere(storm_radius, 16, "storm")
    
    def _render_atmosphere(self, body_name, radius, config, distance_from_camera):
        """渲染大气层"""
        if body_name in ["earth", "venus", "mars"]:
            # 地球、金星、火星有大气层
            self._render_terrestrial_atmosphere(radius, body_name)
        elif body_name == "saturn":  # 移除木星，只保留土星
            # 气态行星有厚厚的大气层
            self._render_gas_giant_atmosphere(radius, body_name)
    
    def _render_terrestrial_atmosphere(self, radius, body_name):
        """渲染类地行星大气层"""
        atmosphere_radius = radius * 1.02
        
        # 设置大气层材质
        if body_name == "earth":
            color = [0.5, 0.7, 1.0]  # 蓝色
            # 地球保留大气层
            glMaterialfv(GL_FRONT, GL_AMBIENT, [color[0] * 0.3, color[1] * 0.3, color[2] * 0.3, 0.2])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [color[0] * 0.3, color[1] * 0.3, color[2] * 0.3, 0.2])
            self._render_sphere(atmosphere_radius, 16, "atmosphere")
        elif body_name == "venus":
            # 金星删除大气层光晕环
            pass
        else:  # mars
            color = [0.6, 0.4, 0.2]  # 红色
            # 火星保留大气层
            glMaterialfv(GL_FRONT, GL_AMBIENT, [color[0] * 0.3, color[1] * 0.3, color[2] * 0.3, 0.2])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [color[0] * 0.3, color[1] * 0.3, color[2] * 0.3, 0.2])
            self._render_sphere(atmosphere_radius, 16, "atmosphere")
    
    def _render_gas_giant_atmosphere(self, radius, body_name):
        """渲染气态巨行星大气层"""
        atmosphere_radius = radius * 1.05
        
        # 设置大气层材质
        if body_name == "jupiter":
            color = [0.8, 0.6, 0.4]  # 橙色
        else:  # saturn
            color = [0.9, 0.8, 0.6]  # 黄色
        
        glMaterialfv(GL_FRONT, GL_AMBIENT, [color[0] * 0.4, color[1] * 0.4, color[2] * 0.4, 0.2])  # 从0.3降低到0.2
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [color[0] * 0.4, color[1] * 0.4, color[2] * 0.4, 0.2])  # 从0.3降低到0.2
        
        self._render_sphere(atmosphere_radius, 16, "atmosphere")
    
    def _render_rings(self, body_name, radius, config, distance_from_camera):
        """渲染行星环"""
        if body_name == "saturn":
            self._render_saturn_rings(radius)
        # 天王星和海王星没有外部光环，已删除
    
    def _render_saturn_rings(self, radius):
        """渲染土星环"""
        ring_inner = radius * 1.2
        ring_outer = radius * 2.0
        
        # 设置环的材质
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.8, 0.7, 0.5, 0.6])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.7, 0.5, 0.6])
        
        # 渲染环
        self._render_ring(ring_inner, ring_outer, 32)
    

    
    def _render_ring(self, inner_radius, outer_radius, segments):
        """渲染行星环"""
        glBegin(GL_QUADS)
        
        for i in range(segments):
            angle1 = i * 2 * math.pi / segments
            angle2 = (i + 1) * 2 * math.pi / segments
            
            x1_inner = math.cos(angle1) * inner_radius
            y1_inner = math.sin(angle1) * inner_radius
            x2_inner = math.cos(angle2) * inner_radius
            y2_inner = math.sin(angle2) * inner_radius
            
            x1_outer = math.cos(angle1) * outer_radius
            y1_outer = math.sin(angle1) * outer_radius
            x2_outer = math.cos(angle2) * outer_radius
            y2_outer = math.sin(angle2) * outer_radius
            
            # 环的上表面
            glVertex3f(x1_inner, y1_inner, 0.01)
            glVertex3f(x2_inner, y2_inner, 0.01)
            glVertex3f(x2_outer, y2_outer, 0.01)
            glVertex3f(x1_outer, y1_outer, 0.01)
            
            # 环的下表面
            glVertex3f(x1_inner, y1_inner, -0.01)
            glVertex3f(x1_outer, y1_outer, -0.01)
            glVertex3f(x2_outer, y2_outer, -0.01)
            glVertex3f(x2_inner, y2_inner, -0.01)
        
        glEnd()
    
    def update_animations(self):
        """更新动画状态"""
        self.animation_time += 0.016  # 假设60FPS
    
    def set_animation_speed(self, speed):
        """设置动画速度"""
        self.animation_speed = speed 