# 增强版太阳系模拟器

一个基于OpenGL和Python的高质量太阳系3D模拟器，包含背景抠图、动态优化和逼真效果。

## 🚀 主要特性

### 核心技术
- **背景抠图处理**: 自动移除天体图片背景，实现透明效果
- **动态LOD优化**: 根据距离自动调整渲染细节，提升性能
- **逼真光照系统**: 基于物理的光照模型，支持环境光、漫反射和镜面反射
- **大气层渲染**: 为有大气层的天体添加真实的大气效果
- **粒子特效**: 太阳日冕、地球极光等特殊效果
- **自适应质量**: 根据硬件性能自动调整渲染质量

### 视觉效果
- 真实的天体纹理和材质
- 动态动画效果（太阳脉动、云层移动、大气流动）
- 土星环的逼真渲染
- 深度测试和混合效果
- 平滑的相机控制和缩放

## 📁 项目结构

```
3D地球环绕/
├── enhanced_solar_system.py    # 主程序入口
├── enhanced_renderer.py        # 增强3D渲染器
├── advanced_texture_manager.py # 高级纹理管理器
├── config.py                   # 配置文件
├── requirements.txt            # 依赖包列表
├── README.md                   # 项目说明
└── pictures/                   # 天体纹理图片
    ├── sun.jpg
    ├── earth.jpg
    ├── mars.jpg
    └── ...
```

## 🛠️ 安装依赖

```bash
pip install -r requirements.txt
```

### 必需依赖
- `pygame>=2.0.0` - 游戏引擎和窗口管理
- `PyOpenGL>=3.1.0` - OpenGL绑定
- `PyOpenGL-accelerate>=3.1.0` - OpenGL加速
- `numpy>=1.21.0` - 数值计算
- `opencv-python>=4.5.0` - 图像处理和背景抠图
- `Pillow>=8.3.0` - 图像处理

## 🎮 使用方法

### 运行程序
```bash
python enhanced_solar_system.py
```

### 控制说明
- **WASD** - 旋转相机视角
- **鼠标滚轮** - 缩放相机距离
- **空格键** - 暂停/继续时间
- **上下箭头** - 调整时间速度
- **Q键** - 切换自适应质量
- **ESC键** - 退出程序

## 🔧 技术架构

### 渲染管线
1. **纹理管理**: 自动加载、处理和优化天体纹理
2. **几何生成**: 动态生成球体几何，支持LOD优化
3. **光照计算**: 实时光照和阴影计算
4. **特效渲染**: 大气层、粒子效果等后处理
5. **UI叠加**: 2D界面信息显示

### 性能优化
- **动态LOD**: 根据距离自动调整几何复杂度
- **纹理缓存**: 智能纹理管理和内存优化
- **批量渲染**: 减少OpenGL状态切换
- **自适应质量**: 根据FPS自动调整渲染参数

## 🎨 自定义配置

### 修改config.py
```python
# 屏幕设置
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# 渲染质量
MAX_LOD_LEVEL = 32
MIN_LOD_LEVEL = 8

# 性能设置
TARGET_FPS = 60
ADAPTIVE_QUALITY = True
```

### 添加新天体
在`enhanced_solar_system.py`中的`_initialize_celestial_bodies`方法中添加：

```python
"new_planet": {
    "position": [0, 0, 0],
    "radius": 5.0,
    "rotation_speed": 1.0,
    "orbit_radius": 300.0,
    "orbit_speed": 0.1,
    "texture": "new_planet",
    "has_atmosphere": True,
    "has_particles": False
}
```

## 📊 性能指标

- **目标FPS**: 60 FPS
- **内存使用**: 优化后 < 500MB
- **CPU使用**: 多线程优化，主线程 < 30%
- **GPU使用**: 支持硬件加速，兼容性良好

## 🐛 故障排除

### 常见问题
1. **OpenGL错误**: 确保显卡驱动最新，支持OpenGL 3.0+
2. **纹理加载失败**: 检查pictures文件夹和图片格式
3. **性能问题**: 启用自适应质量，调整LOD参数
4. **依赖缺失**: 运行`pip install -r requirements.txt`

### 调试模式
程序启动时会显示详细的初始化信息和错误日志。

## 🔮 未来计划

- [ ] 支持更多天体类型（小行星、彗星）
- [ ] 添加轨道可视化
- [ ] 支持VR/AR设备
- [ ] 多语言界面
- [ ] 保存/加载场景功能

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**享受探索太阳系的乐趣！** 🌟 