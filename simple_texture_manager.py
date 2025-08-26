#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化纹理管理器 - 避免复杂预处理
直接加载纹理到OpenGL，提高稳定性
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os
import time
import config


class SimpleTextureManager:
    """简化纹理管理器 - 直接加载，避免复杂预处理"""
    
    def __init__(self):
        self.textures = {}
        self.texture_path = "pictures/"
        self.loading_threads = {}
        self.textures_loaded = False
        
        # 确保目录存在
        if not os.path.exists(self.texture_path):
            print(f"警告: 纹理目录 {self.texture_path} 不存在")
            return
        
    def _init_async_loading(self):
        """异步初始化纹理加载"""
        print("正在异步加载天体纹理...")
        
        # 天体纹理映射
        texture_files = {
            "sun": "sun.jpg",
            "mercury": "mercury.jpg", 
            "venus": "venus.jpg",
            "earth": "earth.jpg",
            "mars": "mars.jpg",
            "jupiter": "jupiter.jpg",
            "saturn": "saturn.jpg",
            "uranus": "uranus.jpg",
            "neptune": "neptune.jpg",
            "moon": "moon.jpg"
        }
        
        # 使用线程池异步加载纹理
        import threading
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            for texture_name, filename in texture_files.items():
                future = executor.submit(self._load_texture_simple, texture_name, filename)
                futures[future] = texture_name
            
            # 等待所有加载完成
            for future in futures:
                texture_name = futures[future]
                try:
                    result = future.result(timeout=30)  # 30秒超时
                    if result:
                        print(f"  ✓ {texture_name} 加载成功")
                    else:
                        print(f"  ✗ {texture_name} 加载失败")
                except Exception as e:
                    print(f"  ✗ {texture_name} 加载异常: {e}")
        
        print(f"异步纹理加载完成！共加载 {len(self.textures)} 个纹理")
    
    def _load_texture_simple(self, texture_name, filename):
        """简化纹理加载 - 直接加载到OpenGL"""
        try:
            file_path = os.path.join(self.texture_path, filename)
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return False
            
            print(f"处理纹理: {filename}")
            
            # 使用pygame加载图像
            image = pygame.image.load(file_path)
            
            # 转换为OpenGL格式
            image_data = pygame.image.tostring(image, "RGBA", True)
            width, height = image.get_size()
            
            # 生成OpenGL纹理
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # 设置纹理参数
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            
            # 上传纹理数据
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            
            # 生成mipmap
            glGenerateMipmap(GL_TEXTURE_2D)
            
            # 保存纹理ID
            self.textures[texture_name] = texture_id
            
            return True
            
        except Exception as e:
            print(f"纹理加载失败 {texture_name}: {e}")
            return False
    
    def get_texture(self, texture_name):
        """获取纹理ID"""
        return self.textures.get(texture_name)
    
    def has_texture(self, texture_name):
        """检查是否有纹理"""
        return texture_name in self.textures
    
    def bind_texture(self, texture_name):
        """绑定纹理到OpenGL"""
        if texture_name in self.textures:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textures[texture_name])
            return True
        else:
            # 如果没有纹理，禁用纹理
            glDisable(GL_TEXTURE_2D)
            return False
    
    def unbind_texture(self):
        """解绑纹理"""
        glDisable(GL_TEXTURE_2D)
    
    def update_animations(self):
        """更新纹理动画（简化版）"""
        # 目前没有复杂的动画，但保持接口一致
        pass
    
    def cleanup(self):
        """清理纹理资源"""
        for texture_id in self.textures.values():
            glDeleteTextures([texture_id])
        self.textures.clear() 