#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D太阳系模拟器配置文件
"""

# 屏幕配置（向后兼容）
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FOV = 45.0
NEAR_PLANE = 0.1
FAR_PLANE = 1000.0

# 窗口配置
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "真实3D太阳系模拟器"

# 渲染配置
FPS = 60
ANTIALIASING = True
SHADOW_QUALITY = "high"  # low, medium, high
TEXTURE_QUALITY = "high"  # low, medium, high

# 物理配置
GRAVITY_CONSTANT = 6.67430e-11  # 万有引力常数
TIME_SCALE_MIN = 1
TIME_SCALE_MAX = 10000
DEFAULT_TIME_SCALE = 1

# 相机设置 - 支持无限制缩放
CAMERA_DISTANCE_MIN = 1.0  # 最小距离，避免进入天体内部
CAMERA_DISTANCE_MAX = float('inf')  # 无限制最大距离
DEFAULT_CAMERA_DISTANCE = 10000  # 默认距离，适合上帝视角
CAMERA_ROTATION_SPEED = 0.5  # 旋转速度
CAMERA_ZOOM_SPEED = 0.1  # 缩放速度

# 天体配置 - 优化比例参数
SUN_RADIUS = 5.0  # 太阳半径
PLANET_RADIUS_SCALE = 0.1  # 行星半径缩放因子
ORBIT_SCALE = 0.0001  # 轨道距离缩放因子

# 颜色配置
BACKGROUND_COLOR = (0, 0, 0)  # 黑色背景
UI_COLOR = (255, 255, 255)  # 白色UI
ORBIT_COLOR = (1.0, 1.0, 1.0)  # 轨道颜色 - 白色，使用0-1范围

# 天体颜色（RGB格式，0-1范围）
CELESTIAL_BODIES_COLORS = {
    "sun": (1.0, 0.8, 0.0),      # 金黄色
    "mercury": (0.7, 0.7, 0.7),  # 灰色
    "venus": (1.0, 0.6, 0.0),    # 橙黄色
    "earth": (0.0, 0.5, 1.0),    # 蓝色
    "mars": (1.0, 0.3, 0.0),     # 红色
    "jupiter": (0.8, 0.6, 0.4),  # 棕黄色
    "saturn": (0.9, 0.8, 0.6),   # 浅黄色
    "uranus": (0.4, 0.7, 0.8),   # 青蓝色
    "neptune": (0.0, 0.3, 0.8),  # 深蓝色
    "moon": (0.8, 0.8, 0.8),     # 浅灰色
}

# 轨道参数（真实数据，已缩放）
ORBITAL_PARAMETERS = {
    "mercury": {"semi_major_axis": 5.79e7, "eccentricity": 0.205, "period": 88.0},      # 水星
    "venus": {"semi_major_axis": 1.08e8, "eccentricity": 0.007, "period": 224.7},       # 金星
    "earth": {"semi_major_axis": 1.50e8, "eccentricity": 0.017, "period": 365.25},      # 地球
    "mars": {"semi_major_axis": 2.28e8, "eccentricity": 0.093, "period": 687.0},        # 火星
    "jupiter": {"semi_major_axis": 7.79e8, "eccentricity": 0.048, "period": 4333.0},    # 木星
    "saturn": {"semi_major_axis": 1.43e9, "eccentricity": 0.054, "period": 10759.0},    # 土星
    "uranus": {"semi_major_axis": 2.87e9, "eccentricity": 0.047, "period": 30687.0},    # 天王星
    "neptune": {"semi_major_axis": 4.50e9, "eccentricity": 0.009, "period": 60190.0},   # 海王星
}

# 自转周期（地球日）
ROTATION_PERIODS = {
    "sun": 25.0,
    "mercury": 58.6,
    "venus": -243.0,  # 负值表示逆向自转
    "earth": 1.0,
    "mars": 1.03,
    "jupiter": 0.41,
    "saturn": 0.45,
    "uranus": -0.72,  # 负值表示逆向自转
    "neptune": 0.67,
    "moon": 27.3,
}

# 轨道倾角（度）
ORBITAL_INCLINATIONS = {
    "mercury": 7.0,
    "venus": 3.4,
    "earth": 0.0,  # 参考平面
    "mars": 1.9,
    "jupiter": 1.3,
    "saturn": 2.5,
    "uranus": 0.8,
    "neptune": 1.8,
}

# 自转轴倾角（度）
AXIAL_TILTS = {
    "mercury": 0.034,    # 水星自转轴倾角很小
    "venus": 177.4,      # 金星几乎倒转
    "earth": 23.44,      # 地球自转轴倾角
    "mars": 25.19,       # 火星自转轴倾角
    "jupiter": 3.13,     # 木星自转轴倾角
    "saturn": 26.73,     # 土星自转轴倾角
    "uranus": 97.77,     # 天王星几乎侧躺
    "neptune": 28.32,    # 海王星自转轴倾角
}

# 文件路径
TEXTURE_PATH = "pictures/"  # 使用pictures文件夹
SOUND_PATH = "assets/sounds/"
FONT_PATH = "assets/fonts/"

# 调试配置
DEBUG_MODE = False
SHOW_FPS = True
SHOW_COORDINATES = False 