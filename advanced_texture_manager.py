#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级纹理管理器 - 优化版
包含智能背景抠图、性能优化和逼真效果
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os
import cv2
from PIL import Image, ImageFilter, ImageEnhance
import math
import time
import config
import threading
from concurrent.futures import ThreadPoolExecutor
import pickle
import hashlib


class AdvancedTextureManager:
    """高级纹理管理器 - 智能背景抠图 + 性能优化 + 逼真效果"""
    
    def __init__(self):
        self.textures = {}
        self.texture_path = "pictures/"
        self.processed_textures = {}
        self.animation_frames = {}
        self.current_frame = 0
        self.last_update = time.time()
        
        # 缓存系统
        self.cache_dir = "texture_cache/"
        self.texture_hashes = {}
        self.loading_threads = {}
        self.processing_queue = []
        
        # 确保目录存在
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            if not os.path.exists(self.texture_path):
                print(f"警告: 纹理目录 {self.texture_path} 不存在")
                print("将使用默认纹理或跳过纹理加载")
                return
                
            # 检查OpenGL上下文是否可用
            try:
                # 尝试获取OpenGL状态
                glGetString(GL_VERSION)
                print("OpenGL上下文可用，开始初始化纹理...")
                # 初始化纹理（异步加载）
                self._init_async_loading()
            except Exception as e:
                print(f"OpenGL上下文不可用: {e}")
                print("纹理管理器将在OpenGL上下文可用时重新初始化")
                
        except Exception as e:
            print(f"纹理管理器初始化失败: {e}")
            print("将使用基本功能模式")
        
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
        
        # 使用线程池异步预处理图像（不包含OpenGL操作）
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            for texture_name, filename in texture_files.items():
                future = executor.submit(self._preprocess_texture_safe, texture_name, filename)
                futures[future] = texture_name
            
            # 等待所有预处理完成
            for future in futures:
                texture_name = futures[future]
                try:
                    result = future.result(timeout=60)  # 增加超时时间到60秒
                    if result and result != "failed":
                        print(f"  ✓ {texture_name} 预处理完成")
                        # 将预处理结果加入队列，等待主线程处理
                        self.processing_queue.append((texture_name, result))
                    else:
                        print(f"  ✗ {texture_name} 预处理失败")
                except Exception as e:
                    print(f"  ✗ {texture_name} 预处理异常: {e}")
                    # 尝试使用备用方法
                    self._fallback_texture_loading(texture_name, texture_files[texture_name])
        
        print(f"异步纹理预处理完成！共处理 {len(self.processing_queue)} 个纹理")
    
    def _preprocess_texture_safe(self, texture_name, filename):
        """安全的纹理预处理（不包含OpenGL操作）"""
        try:
            file_path = os.path.join(self.texture_path, filename)
            if not os.path.exists(file_path):
                print(f"纹理文件不存在: {file_path}")
                return "failed"
            
            # 检查缓存
            cache_file = os.path.join(self.cache_dir, f"{texture_name}_cache.pkl")
            if self._load_from_cache_preprocessed(texture_name, cache_file):
                return "cached"
            
            # 处理纹理
            print(f"处理纹理: {filename}")
            
            # 智能背景抠图（改进版本）
            processed_image = self._smart_background_removal_improved(file_path)
            if processed_image is None:
                print(f"背景抠图失败: {texture_name}")
                # 尝试直接加载原图
                processed_image = self._load_original_image(file_path)
                if processed_image is None:
                    return "failed"
            
            # 纹理增强
            enhanced_image = self._enhance_texture_safe(processed_image, texture_name)
            if enhanced_image is None:
                enhanced_image = processed_image  # 使用原图作为备用
            
            # 生成动画帧
            try:
                self._generate_animation_frames_safe(enhanced_image, texture_name)
            except Exception as e:
                print(f"动画帧生成失败 {texture_name}: {e}")
            
            # 保存预处理结果
            self.processed_textures[texture_name] = enhanced_image
            
            # 保存到缓存
            try:
                self._save_preprocessed_to_cache(texture_name, cache_file, enhanced_image)
            except Exception as e:
                print(f"缓存保存失败 {texture_name}: {e}")
            
            return enhanced_image
            
        except Exception as e:
            print(f"纹理预处理失败 {texture_name}: {e}")
            return "failed"
    
    def _load_original_image(self, file_path):
        """加载原始图像作为备用"""
        try:
            image = Image.open(file_path)
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            return image
        except Exception as e:
            print(f"原始图像加载失败: {e}")
            return None
    
    def _smart_background_removal_improved(self, file_path):
        """改进的智能背景移除算法"""
        try:
            # 使用PIL加载图片
            image = Image.open(file_path)
            
            # 转换为RGBA格式
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # 转换为numpy数组
            data = np.array(image)
            height, width = data.shape[:2]
            
            # 简化背景检测算法，提高稳定性
            mask = self._simple_background_detection(data)
            
            # 应用掩码
            result_data = data.copy()
            result_data[~mask, 3] = 0  # 设置背景为透明
            
            return Image.fromarray(result_data, 'RGBA')
            
        except Exception as e:
            print(f"智能背景移除失败: {e}")
            return None
    
    def _simple_background_detection(self, data):
        """简化的背景检测算法"""
        try:
            height, width = data.shape[:2]
            mask = np.ones((height, width), dtype=bool)
            
            # 使用简单的亮度阈值检测
            if len(data.shape) >= 3:
                # RGB图像
                brightness = np.sum(data[:, :, :3], axis=2)
                threshold = np.percentile(brightness, 85)  # 85%分位数
                mask = brightness < threshold
            else:
                # 灰度图像
                threshold = np.percentile(data, 85)
                mask = data < threshold
            
            # 简单的形态学清理
            try:
                kernel = np.ones((3, 3), np.uint8)
                mask = mask.astype(np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = mask.astype(bool)
            except Exception:
                # 如果OpenCV操作失败，使用原始掩码
                pass
            
            return mask
            
        except Exception as e:
            print(f"背景检测失败: {e}")
            # 返回全True掩码（保留所有像素）
            return np.ones((data.shape[0], data.shape[1]), dtype=bool)
    
    def _enhance_texture_safe(self, image, texture_name):
        """安全的纹理增强"""
        try:
            if image is None:
                return None
            
            # 首先处理纹理边缘，确保无缝连接
            image = self._process_texture_edges(image, texture_name)
            
            # 根据天体类型应用不同的增强效果
            if texture_name == "sun":
                # 太阳：增加亮度和对比度
                try:
                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(1.3)
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(1.2)
                except Exception as e:
                    print(f"太阳纹理增强失败: {e}")
                    
            elif texture_name == "earth":
                # 地球：增加饱和度
                try:
                    enhancer = ImageEnhance.Color(image)
                    image = enhancer.enhance(1.4)
                except Exception as e:
                    print(f"地球纹理增强失败: {e}")
                    
            elif texture_name == "mars":
                # 火星：增加红色调
                try:
                    enhancer = ImageEnhance.Color(image)
                    image = enhancer.enhance(1.5)
                except Exception as e:
                    print(f"火星纹理增强失败: {e}")
                    
            elif texture_name == "jupiter":
                # 木星：增加对比度
                try:
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(1.3)
                except Exception as e:
                    print(f"木星纹理增强失败: {e}")
                    
            elif texture_name == "saturn":
                # 土星：增加锐度
                try:
                    enhancer = ImageEnhance.Sharpness(image)
                    image = enhancer.enhance(1.2)
                except Exception as e:
                    print(f"土星纹理增强失败: {e}")
            
            return image
            
        except Exception as e:
            print(f"纹理增强失败: {e}")
            return image
    
    def _process_texture_edges(self, image, texture_name):
        """处理纹理边缘，确保无缝连接"""
        try:
            if image is None:
                return image
            
            # 获取图像尺寸
            width, height = image.size
            
            # 创建边缘处理后的图像
            processed_image = image.copy()
            
            # 处理左右边缘，确保无缝连接
            edge_width = min(10, width // 20)  # 边缘宽度为图像宽度的5%
            
            # 处理左边缘
            for x in range(edge_width):
                for y in range(height):
                    # 获取左边缘像素
                    left_pixel = image.getpixel((x, y))
                    # 获取右边缘对应像素
                    right_pixel = image.getpixel((width - edge_width + x, y))
                    # 混合像素，创建平滑过渡
                    mixed_pixel = tuple(int((left_pixel[i] + right_pixel[i]) / 2) for i in range(4))
                    processed_image.putpixel((x, y), mixed_pixel)
            
            # 处理右边缘
            for x in range(edge_width):
                for x_pos in range(width - edge_width, width):
                    for y in range(height):
                        # 获取右边缘像素
                        right_pixel = image.getpixel((x_pos, y))
                        # 获取左边缘对应像素
                        left_pixel = image.getpixel((x, y))
                        # 混合像素，创建平滑过渡
                        mixed_pixel = tuple(int((left_pixel[i] + right_pixel[i]) / 2) for i in range(4))
                        processed_image.putpixel((x_pos, y), mixed_pixel)
            
            return processed_image
            
        except Exception as e:
            print(f"纹理边缘处理失败 {texture_name}: {e}")
            return image
    
    def _generate_animation_frames_safe(self, image, texture_name):
        """安全的动画帧生成"""
        try:
            if image is None:
                return
            
            frames = []
            data = np.array(image)
            height, width = data.shape[:2]
            
            # 根据天体类型生成不同的动画效果
            if texture_name == "sun":
                # 太阳：脉动发光效果
                for frame in range(5):  # 减少帧数以提高性能
                    frame_data = data.copy()
                    # 简单的亮度变化
                    brightness_factor = 1.0 + 0.1 * math.sin(frame * 0.5)
                    frame_data[:, :, :3] = np.clip(frame_data[:, :, :3] * brightness_factor, 0, 255)
                    frames.append(Image.fromarray(frame_data, 'RGBA'))
                    
            elif texture_name == "earth":
                # 地球：旋转效果
                for frame in range(5):
                    frame_data = data.copy()
                    # 简单的颜色变化
                    color_factor = 1.0 + 0.05 * math.sin(frame * 0.8)
                    frame_data[:, :, :3] = np.clip(frame_data[:, :, :3] * color_factor, 0, 255)
                    frames.append(Image.fromarray(frame_data, 'RGBA'))
            
            if frames:
                self.animation_frames[texture_name] = frames
                
        except Exception as e:
            print(f"动画帧生成失败: {e}")
    
    def _fallback_texture_loading(self, texture_name, filename):
        """备用纹理加载方法"""
        try:
            file_path = os.path.join(self.texture_path, filename)
            if os.path.exists(file_path):
                # 直接加载原图，不进行复杂处理
                image = Image.open(file_path)
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                self.processed_textures[texture_name] = image
                self.processing_queue.append((texture_name, image))
                print(f"  ✓ {texture_name} 使用备用方法加载成功")
            else:
                print(f"  ✗ {texture_name} 纹理文件不存在")
        except Exception as e:
            print(f"  ✗ {texture_name} 备用加载失败: {e}")
    
    def process_queue(self):
        """处理预处理队列（在主线程中调用）"""
        if not self.processing_queue:
            return
        
        # 处理队列中的纹理
        while self.processing_queue:
            texture_name, preprocessed_result = self.processing_queue.pop(0)
            
            if preprocessed_result == "cached":
                # 从缓存加载
                self._load_cached_texture(texture_name)
            else:
                # 加载到OpenGL
                self._load_to_opengl_main_thread(texture_name, preprocessed_result)
    
    def _load_cached_texture(self, texture_name):
        """从缓存加载纹理"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{texture_name}_cache.pkl")
            if self._load_from_cache_preprocessed(texture_name, cache_file):
                # 现在加载到OpenGL
                if texture_name in self.processed_textures:
                    enhanced_image = self.processed_textures[texture_name]
                    self._load_to_opengl_main_thread(texture_name, enhanced_image)
        except Exception as e:
            print(f"缓存纹理加载失败 {texture_name}: {e}")
    
    def _load_to_opengl_main_thread(self, texture_name, preprocessed_result):
        """在主线程中加载到OpenGL"""
        try:
            if preprocessed_result == "cached":
                # 从缓存加载
                return True
            
            if texture_name not in self.processed_textures:
                return False
            
            enhanced_image = self.processed_textures[texture_name]
            
            # 加载到OpenGL
            texture_id = self._load_texture_to_opengl(enhanced_image)
            if texture_id is None:
                return False
            
            # 更新状态
            self.textures[texture_name] = texture_id
            print(f"  ✓ {texture_name} OpenGL加载成功")
            
            return True
            
        except Exception as e:
            print(f"OpenGL加载失败 {texture_name}: {e}")
            return False
    
    def _save_preprocessed_to_cache(self, texture_name, cache_file, image):
        """保存预处理结果到缓存"""
        try:
            # 计算图像哈希值
            image_hash = hashlib.md5(image.tobytes()).hexdigest()
            self.texture_hashes[texture_name] = image_hash
            
            # 保存预处理图像（不包含OpenGL纹理ID）
            cache_data = {
                'image_hash': image_hash,
                'timestamp': time.time(),
                'image_data': image
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
                
        except Exception as e:
            print(f"预处理缓存保存失败: {e}")
    
    def _load_from_cache_preprocessed(self, texture_name, cache_file):
        """从缓存加载预处理结果"""
        try:
            if not os.path.exists(cache_file):
                return False
            
            # 检查缓存是否过期（24小时）
            if time.time() - os.path.getmtime(cache_file) > 86400:
                return False
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 验证缓存数据
            if 'image_data' not in cache_data or 'image_hash' not in cache_data:
                return False
            
            # 更新状态
            self.processed_textures[texture_name] = cache_data['image_data']
            self.texture_hashes[texture_name] = cache_data['image_hash']
            
            print(f"  ✓ {texture_name} 从缓存加载预处理结果成功")
            return True
            
        except Exception as e:
            print(f"预处理缓存加载失败: {e}")
            return False
    
    def _load_texture_to_opengl(self, image):
        """将PIL图像加载到OpenGL"""
        try:
            # 确保图像是RGBA格式
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # 获取图像数据
            width, height = image.size
            image_data = image.tobytes()
            
            # 创建OpenGL纹理
            texture_id = glGenTextures(1)
            if texture_id == 0:
                print("OpenGL纹理ID生成失败")
                return None
                
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # 设置纹理参数 - 改进贴图环绕模式
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)  # 水平重复，确保无缝连接
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)  # 垂直夹边，避免极地变形
            
            # 设置各向异性过滤，提高贴图质量（检查扩展支持）
            try:
                if hasattr(OpenGL.GL, 'GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT'):
                    max_anisotropy = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
                    if max_anisotropy > 1.0:
                        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, min(4.0, max_anisotropy))
                else:
                    # 如果不支持各向异性过滤，使用标准过滤
                    print("  注意: 当前OpenGL环境不支持各向异性过滤，使用标准过滤")
            except Exception as e:
                print(f"  注意: 各向异性过滤设置失败，使用标准过滤: {e}")
            
            # 上传纹理数据
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            
            # 生成mipmap以提高贴图质量
            glGenerateMipmap(GL_TEXTURE_2D)
            
            # 检查OpenGL错误
            error = glGetError()
            if error != GL_NO_ERROR:
                print(f"OpenGL错误: {error}")
                return None
            
            return texture_id
            
        except Exception as e:
            print(f"OpenGL纹理加载失败: {e}")
            return None
    
    def _save_to_cache(self, texture_name, cache_file, image, texture_id):
        """保存纹理到缓存"""
        try:
            # 计算图像哈希值
            image_hash = hashlib.md5(image.tobytes()).hexdigest()
            self.texture_hashes[texture_name] = image_hash
            
            # 保存缓存数据
            cache_data = {
                'texture_id': texture_id,
                'image_hash': image_hash,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
                
        except Exception as e:
            print(f"缓存保存失败: {e}")
    
    def _load_from_cache(self, texture_name, cache_file):
        """从缓存加载纹理"""
        try:
            if not os.path.exists(cache_file):
                return False
            
            # 检查缓存是否过期（24小时）
            if time.time() - os.path.getmtime(cache_file) > 86400:
                return False
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 验证缓存数据
            if 'texture_id' not in cache_data or 'image_hash' not in cache_data:
                return False
            
            # 检查OpenGL纹理是否仍然有效
            texture_id = cache_data['texture_id']
            if not glIsTexture(texture_id):
                return False
            
            # 更新状态
            self.textures[texture_name] = texture_id
            self.texture_hashes[texture_name] = cache_data['image_hash']
            
            print(f"  ✓ {texture_name} 从缓存加载成功")
            return True
            
        except Exception as e:
            print(f"缓存加载失败: {e}")
            return False
    
    def update_animations(self):
        """更新动画帧"""
        current_time = time.time()
        if current_time - self.last_update > 0.1:  # 每0.1秒更新一次
            self.current_frame = (self.current_frame + 1) % 10
            self.last_update = current_time
    
    def get_animated_texture(self, name):
        """获取动画纹理"""
        if name in self.animation_frames:
            frames = self.animation_frames[name]
            if frames:
                frame_index = self.current_frame % len(frames)
                return frames[frame_index]
        return None
    
    def get_texture(self, name):
        """获取纹理"""
        return self.textures.get(name, None)
    
    def bind_texture(self, name):
        """绑定纹理"""
        texture_id = self.get_texture(name)
        if texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
        else:
            glDisable(GL_TEXTURE_2D)
    
    def bind_animated_texture(self, name):
        """绑定动画纹理"""
        animated_image = self.get_animated_texture(name)
        if animated_image:
            # 临时创建OpenGL纹理
            texture_id = self._load_texture_to_opengl(animated_image)
            if texture_id:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                return texture_id
        
        # 如果动画纹理不可用，使用静态纹理
        self.bind_texture(name)
        return None
    
    def unbind_texture(self):
        """解绑纹理"""
        glDisable(GL_TEXTURE_2D)
    
    def apply_lighting_effects(self, name):
        """应用光照效果"""
        if name in self.processed_textures:
            image = self.processed_textures[name]
            data = np.array(image)
            
            # 添加环境光遮蔽
            height, width = data.shape[:2]
            for y in range(height):
                for x in range(width):
                    if data[y, x, 3] > 0:
                        # 计算到中心的距离
                        center_x, center_y = width // 2, height // 2
                        dx, dy = x - center_x, y - center_y
                        distance = math.sqrt(dx*dx + dy*dy)
                        max_distance = math.sqrt(center_x*center_x + center_y*center_y)
                        
                        # 边缘变暗效果
                        darkening = 1.0 - 0.3 * (distance / max_distance)
                        for c in range(3):
                            data[y, x, c] = np.clip(int(data[y, x, c] * darkening), 0, 255)
            
            return Image.fromarray(data, 'RGBA')
        
        return None
    
    def get_loading_progress(self):
        """获取加载进度"""
        total_textures = 10  # 总纹理数量
        loaded_textures = len(self.textures)
        return loaded_textures / total_textures
    
    def is_loading_complete(self):
        """检查是否加载完成"""
        return len(self.textures) >= 10
    
    def clear_cache(self):
        """清理缓存"""
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
            print("纹理缓存已清理")
        except Exception as e:
            print(f"缓存清理失败: {e}")
    
    def optimize_memory(self):
        """优化内存使用"""
        try:
            # 压缩图像数据
            for name, image in self.processed_textures.items():
                if image.size[0] > 512 or image.size[1] > 512:
                    # 缩小大图像
                    new_size = (512, 512)
                    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
                    self.processed_textures[name] = resized_image
                    print(f"  ✓ {name} 图像已优化为 512x512")
            
            print("内存优化完成")
        except Exception as e:
            print(f"内存优化失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            # 清理OpenGL纹理
            for texture_id in self.textures.values():
                if texture_id and glIsTexture(texture_id):
                    glDeleteTextures([texture_id])
            
            # 清理图像数据
            self.processed_textures.clear()
            self.animation_frames.clear()
            
            # 清理缓存
            self.clear_cache()
            
            print("纹理管理器资源清理完成")
        except Exception as e:
            print(f"纹理管理器清理失败: {e}") 