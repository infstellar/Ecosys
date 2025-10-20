# 🌱 生态系统模拟器 - Ecosystem Simulator 🐅

一个基于Python和Pygame的生态系统模拟程序，模拟草原生态系统中草、牛、老虎之间的捕食关系和种群动态。

A comprehensive ecosystem simulation built with Python and Pygame, modeling predator-prey relationships and population dynamics in a grassland ecosystem.

## ✨ 功能特点 (Features)

### 🎯 核心功能 (Core Features)
- **物种模拟**: 草🌿、牛🐄、老虎🐅三个物种的完整生命周期
- **生态平衡**: 真实的捕食关系和种群动态
- **实时可视化**: 基于Pygame的流畅动画和图形界面
- **交互控制**: 丰富的参数调节和模拟控制选项
- **数据分析**: 实时统计图表和种群数量追踪

### 🏗️ 技术架构 (Technical Architecture)
- **前后端分离**: 清晰的架构设计，便于扩展和维护
- **模块化设计**: 高度解耦的组件系统
- **事件驱动**: 响应式的用户交互处理
- **面向对象**: 清晰的类层次结构和继承关系

## 🚀 快速开始 (Quick Start)

### 📋 系统要求 (Requirements)
- Python 3.7+
- Pygame 2.1.0+

### 🔧 安装步骤 (Installation)

1. **克隆项目 (Clone the repository)**
   ```bash
   git clone <repository-url>
   cd Ecosys
   ```

2. **安装依赖 (Install dependencies)**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序 (Run the simulator)**
   ```bash
   python main.py
   ```

## 🎮 使用说明 (Usage Guide)

### ⌨️ 键盘控制 (Keyboard Controls)
- **空格键 (Space)**: 开始/暂停模拟
- **R键**: 重置模拟到初始状态
- **+/- 键**: 增加/减少模拟速度
- **ESC键**: 退出程序

### 🖱️ 鼠标操作 (Mouse Controls)
- **左键点击**: 与UI控件交互
- **模拟区域点击**: 查看该位置的物种信息
- **拖拽滑块**: 调整各种参数

### 🎛️ 控制面板 (Control Panel)

#### 模拟控制 (Simulation Control)
- **开始/暂停按钮**: 控制模拟的运行状态
- **重置按钮**: 重新初始化生态系统
- **速度滑块**: 调整模拟速度 (0.1x - 5.0x)

#### 参数配置 (Parameter Configuration)
- **草数量**: 设置初始草的数量 (10-200)
- **牛数量**: 设置初始牛的数量 (5-50)
- **老虎数量**: 设置初始老虎的数量 (1-20)
- **世界大小**: 调整模拟世界的尺寸 (400x400 - 1000x1000)

#### 信息显示 (Information Display)
- **实时统计**: 当前时间步、模拟速度
- **种群数量**: 各物种的实时数量
- **生死统计**: 总出生数和死亡数
- **灭绝警告**: 物种灭绝提醒

#### 数据图表 (Data Charts)
- **种群变化图**: 实时显示各物种数量变化趋势
- **多色线图**: 不同颜色代表不同物种
- **历史数据**: 保留最近100个时间点的数据

## 🧬 生态系统规则 (Ecosystem Rules)

### 🌿 草 (Grass)
- **特性**: 自动生长和繁殖
- **生长**: 在空旷区域随机生成
- **生命周期**: 无限制，除非被吃掉
- **繁殖**: 周期性在附近区域产生新草

### 🐄 牛 (Cows)
- **特性**: 草食动物，群居性强
- **食物**: 只吃草
- **移动**: 随机游走寻找食物
- **繁殖**: 能量充足时可以繁殖
- **死亡**: 能量耗尽或被老虎捕食
- **寿命**: 有限的生命周期

### 🐅 老虎 (Tigers)
- **特性**: 顶级捕食者，独居性强
- **食物**: 只捕食牛
- **移动**: 主动寻找猎物
- **繁殖**: 能量充足时可以繁殖
- **死亡**: 能量耗尽或年老
- **寿命**: 有限的生命周期

### ⚖️ 生态平衡 (Ecological Balance)
- **能量流动**: 草 → 牛 → 老虎
- **种群控制**: 捕食关系维持种群平衡
- **环境容量**: 世界大小限制总种群数量
- **随机因素**: 自然死亡和环境变化

## 📊 数据分析 (Data Analysis)

### 📈 统计指标 (Statistical Metrics)
- **种群数量**: 实时监控各物种数量
- **出生率**: 每个时间步的新生个体数
- **死亡率**: 每个时间步的死亡个体数
- **年龄分布**: 各物种的年龄结构
- **能量分布**: 个体能量水平统计

### 📉 趋势分析 (Trend Analysis)
- **种群波动**: 观察种群数量的周期性变化
- **捕食压力**: 分析捕食关系对种群的影响
- **生态稳定性**: 评估生态系统的稳定程度
- **灭绝风险**: 预警物种灭绝的可能性

## 🔧 技术细节 (Technical Details)

### 📁 项目结构 (Project Structure)
```
Ecosys/
├── main.py                 # 主入口文件
├── requirements.txt        # 依赖文件
├── README.md              # 项目说明
├── backend/               # 后端模块
│   ├── __init__.py
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   ├── species.py     # 物种类定义
│   │   └── ecosystem.py   # 生态系统状态
│   ├── engine/            # 模拟引擎
│   │   ├── __init__.py
│   │   └── simulation.py  # 模拟逻辑
│   └── interface/         # API接口
│       ├── __init__.py
│       └── api.py         # 前后端通信
└── frontend/              # 前端模块
    ├── __init__.py
    ├── app.py             # 主应用程序
    ├── renderer/          # 渲染系统
    │   ├── __init__.py
    │   └── display.py     # 显示管理
    ├── ui/                # 用户界面
    │   ├── __init__.py
    │   ├── components.py  # UI组件
    │   └── control_panel.py # 控制面板
    └── events/            # 事件处理
        ├── __init__.py
        └── event_handler.py # 事件管理
```

### 🎨 设计模式 (Design Patterns)
- **MVC架构**: 模型-视图-控制器分离
- **观察者模式**: 事件驱动的更新机制
- **策略模式**: 不同物种的行为策略
- **工厂模式**: 物种实例的创建管理

### 🔄 数据流 (Data Flow)
1. **用户输入** → 事件处理器
2. **事件处理器** → API命令
3. **API命令** → 后端引擎
4. **后端引擎** → 模拟更新
5. **模拟数据** → 前端渲染
6. **前端渲染** → 屏幕显示

## 🎯 扩展功能 (Extension Ideas)

### 🌟 可能的增强 (Potential Enhancements)
- **新物种**: 添加更多动植物种类
- **环境因素**: 天气、季节、灾害等
- **遗传算法**: 物种进化和适应
- **3D可视化**: 三维环境展示
- **网络功能**: 多用户协作模拟
- **AI控制**: 智能物种行为
- **数据导出**: 结果保存和分析
- **参数优化**: 自动寻找最佳参数

### 🔬 研究应用 (Research Applications)
- **生态学教学**: 教育演示工具
- **科学研究**: 生态模型验证
- **政策分析**: 环境保护决策支持
- **游戏开发**: 生态游戏机制设计

## 🤝 贡献指南 (Contributing)

欢迎贡献代码、报告问题或提出建议！

We welcome contributions, bug reports, and suggestions!

### 📝 贡献方式 (How to Contribute)
1. Fork 项目仓库
2. 创建功能分支
3. 提交代码更改
4. 发起 Pull Request

### 🐛 问题报告 (Bug Reports)
请在GitHub Issues中报告问题，包含：
- 详细的问题描述
- 重现步骤
- 系统环境信息
- 错误截图或日志

## 📄 许可证 (License)

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 作者 (Authors)

- **开发者**: Trae AI Assistant
- **项目类型**: 教育/研究工具
- **开发时间**: 2024

## 🙏 致谢 (Acknowledgments)

- Pygame社区提供的优秀游戏开发框架
- 生态学研究为模拟提供的理论基础
- 开源社区的持续支持和贡献

---

**享受探索生态系统的奥秘！🌍**

**Enjoy exploring the mysteries of ecosystems! 🌍**