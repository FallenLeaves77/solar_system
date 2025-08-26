#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强相机控制系统
支持以任意天体为中心的观察模式，实现平滑切换和位置跟随
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import time


class EnhancedCameraSystem:
    """增强相机控制系统 - 支持多中心观察"""
    
    def __init__(self):
        # 相机状态
        self.camera_distance = 200.0
        self.camera_x_rotation = 0.0  # 俯仰角 (pitch)
        self.camera_y_rotation = 0.0  # 偏航角 (yaw)
        self.camera_speed = 2.0
        self.zoom_speed = 15.0
        
        # 观察中心
        self.observation_center = "sun"  # 默认以太阳为中心
        self.observation_position = [0.0, 0.0, 0.0]  # 当前观察中心的世界坐标
        
        # 鼠标控制
        self.mouse_dragging = False
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.5
        
        # 相机动画
        self.target_position = None
        self.transition_speed = 0.05
        self.is_transitioning = False
        self.transition_start_time = 0.0
        self.transition_duration = 1.0  # 1秒的过渡时间
        
        # 相机限制
        self.min_distance = 5.0
        self.max_distance = 2000.0
        
        # 性能优化
        self.last_update_time = time.time()
        self.smooth_factor = 0.1
    
    def set_observation_center(self, body_name, body_position, body_radius):
        """设置新的观察中心"""
        if body_name != self.observation_center:
            print(f"切换到以 {body_name} 为中心的观察模式")
            self.observation_center = body_name
            
            # 计算合适的相机距离（基于天体半径）
            target_distance = max(body_radius * 10, self.min_distance)
            self.camera_distance = target_distance
            
            # 重置相机角度
            self.camera_x_rotation = 0.0
            self.camera_y_rotation = 0.0
            
            # 设置目标位置
            self.target_position = body_position.copy()
            self.is_transitioning = True
            
            # 记录切换时间，用于平滑过渡
            self.transition_start_time = time.time()
            self.transition_duration = 1.0  # 1秒的过渡时间
    
    def update(self, celestial_bodies):
        """更新相机系统"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 更新观察中心位置 - 实时跟随天体位置
        if self.observation_center in celestial_bodies:
            body = celestial_bodies[self.observation_center]
            current_body_position = body["position"].copy()
            
            # 如果正在过渡中，平滑插值到新位置
            if self.is_transitioning and self.target_position:
                # 计算过渡进度
                elapsed = current_time - self.transition_start_time
                progress = min(elapsed / self.transition_duration, 1.0)
                
                # 使用缓动函数实现平滑过渡
                ease_progress = self._ease_in_out_cubic(progress)
                
                # 平滑插值位置
                for i in range(3):
                    self.observation_position[i] = (
                        self.target_position[i] * ease_progress + 
                        self.observation_position[i] * (1 - ease_progress)
                    )
                
                # 检查过渡是否完成
                if progress >= 1.0:
                    self.is_transitioning = False
                    self.target_position = None
                    # 过渡完成后，直接跟随天体位置
                    self.observation_position = current_body_position.copy()
            else:
                # 不在过渡中，直接跟随天体位置
                self.observation_position = current_body_position.copy()
    
    def _ease_in_out_cubic(self, t):
        """缓动函数：实现平滑的过渡效果"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            f = ((2 * t) - 2)
            return 0.5 * f * f * f + 1
    
    def handle_input(self, event):
        """处理输入事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 鼠标左键
                self.mouse_dragging = True
                self.last_mouse_pos = pygame.mouse.get_pos()
            elif event.button == 4:  # 滚轮上 - 放大
                self.zoom_in()
            elif event.button == 5:  # 滚轮下 - 缩小
                self.zoom_out()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 鼠标左键释放
                self.mouse_dragging = False
                self.last_mouse_pos = None
        
        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_dragging and self.last_mouse_pos:
                current_pos = pygame.mouse.get_pos()
                dx = current_pos[0] - self.last_mouse_pos[0]
                dy = current_pos[1] - self.last_mouse_pos[1]
                
                # 更新相机旋转
                self.camera_y_rotation += dx * self.mouse_sensitivity * 0.5
                self.camera_x_rotation += dy * self.mouse_sensitivity * 0.5
                
                # 限制俯仰角范围
                self.camera_x_rotation = max(-80, min(80, self.camera_x_rotation))
                
                self.last_mouse_pos = current_pos
    
    def handle_keyboard_input(self, keys):
        """处理键盘输入"""
        if keys[pygame.K_LEFT]:
            self.camera_y_rotation -= self.camera_speed
        if keys[pygame.K_RIGHT]:
            self.camera_y_rotation += self.camera_speed
        if keys[pygame.K_w]:
            self.camera_x_rotation -= self.camera_speed
        if keys[pygame.K_s]:
            self.camera_x_rotation += self.camera_speed
    
    def zoom_in(self):
        """放大"""
        self.camera_distance = max(self.min_distance, self.camera_distance * 0.9)
    
    def zoom_out(self):
        """缩小"""
        self.camera_distance = min(self.max_distance, self.camera_distance * 1.1)
    
    def apply_camera_transform(self):
        """应用相机变换"""
        glLoadIdentity()
        
        # 移动到观察中心
        glTranslatef(
            -self.observation_position[0],
            -self.observation_position[1], 
            -self.observation_position[2]
        )
        
        # 应用相机距离和旋转
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.camera_x_rotation, 1, 0, 0)
        glRotatef(self.camera_y_rotation, 0, 1, 0)
    
    def get_camera_info(self):
        """获取相机信息"""
        return {
            "center": self.observation_center,
            "distance": self.camera_distance,
            "position": self.observation_position.copy(),
            "rotation": (self.camera_x_rotation, self.camera_y_rotation),
            "is_transitioning": self.is_transitioning
        }
    
    def reset_to_sun(self):
        """重置到以太阳为中心的观察模式"""
        self.set_observation_center("sun", [0.0, 0.0, 0.0], 5.0)
    
    def get_world_to_camera_matrix(self):
        """获取世界坐标到相机坐标的变换矩阵"""
        # 这里可以返回一个4x4的变换矩阵
        # 用于精确的坐标变换计算
        pass
    
    def screen_to_world_ray(self, screen_x, screen_y, screen_width, screen_height):
        """将屏幕坐标转换为世界射线（用于点击检测）"""
        # 获取当前OpenGL矩阵
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        # 计算近平面和远平面的点
        near_point = gluUnProject(screen_x, screen_y, 0.0, modelview, projection, viewport)
        far_point = gluUnProject(screen_x, screen_y, 1.0, modelview, projection, viewport)
        
        if near_point and far_point:
            # 计算射线方向
            direction = [
                far_point[0] - near_point[0],
                far_point[1] - near_point[1],
                far_point[2] - far_point[2]
            ]
            
            # 标准化方向向量
            length = math.sqrt(sum(d * d for d in direction))
            if length > 0:
                direction = [d / length for d in direction]
            
            return near_point, direction
        
        return None, None 