# PetersenExplorer - Petersen音律系统探索工具包

## 📖 概述

PetersenExplorer是一个全面的Petersen音律系统探索、分析和验证工具包。基于开放性原则，它能够系统性地探索Petersen音律的参数空间，并从多个维度评估每个音律系统的特性和应用潜力。

### 🎯 核心特性

- **参数空间系统性探索**: 全面测试φ和δθ预设的所有组合
- **多维度评估体系**: 传统兼容性、微分音潜力、实验创新性等8个维度
- **开放性分类系统**: 6种主要类别，支持多样化音律系统
- **音频验证测试**: 使用Enhanced Petersen Player进行实际播放测试
- **综合报告生成**: 详细的分析报告和数据导出

### 🔬 开放性原则

1. **多样性优于单一性**: 不同类型的音律系统都有其独特价值
2. **潜力优于完美**: 关注音乐构建潜力而非与现有标准的完美匹配
3. **创新性优于保守性**: 鼓励探索前所未有的音乐可能性
4. **适应性优于固定性**: 同一音律在不同应用场景下可能展现不同特质

## 🚀 快速开始

### 简单探索

```python
from PetersenExplorer import quick_exploration

# 快速探索（使用默认参数）
summary = quick_exploration()
print(f"发现 {summary['statistics']['successful_systems']} 个可用音律系统")
```

### 详细探索

```python
from PetersenExplorer import PetersenMainExplorer, ExplorationConfiguration

# 配置探索参数
config = ExplorationConfiguration(
    f_base_candidates=[220.0, 261.63, 293.66],
    enable_audio_testing=True,
    enable_detailed_analysis=True,
    enable_reporting=True
)

# 创建并运行探索器
explorer = PetersenMainExplorer(config)
summary = explorer.run_complete_exploration()

# 获取顶级系统
top_systems = explorer.get_top_systems(10)
```

### 特定预设探索

```python
from PetersenExplorer import explore_specific_presets

# 探索特定φ和δθ组合
results = explore_specific_presets(
    phi_names=["golden", "silver", "bronze"],
    delta_theta_names=["petersen_original", "harmonic_minor"],
    f_base=220.0
)
```

## 📁 项目结构

```
PetersenExplorer/
├── core/                          # 核心分析模块
│   ├── parameter_explorer.py      # 参数空间探索
│   ├── characteristic_analyzer.py # 音律特性分析
│   ├── evaluation_framework.py    # 多维度评估
│   └── classification_system.py   # 开放性分类
├── audio/                         # 音频验证模块
│   ├── playback_tester.py         # 播放测试器
│   ├── musicality_validator.py    # 音乐性验证
│   └── soundfont_controller.py    # SoundFont控制
├── reporting/                     # 报告生成模块
│   ├── report_generator.py        # 报告生成器
│   ├── visualization.py           # 可视化工具
│   └── export_manager.py          # 导出管理
├── examples/                      # 示例和演示
│   ├── demo_exploration.py        # 演示脚本
│   └── advanced_usage.py          # 高级用法示例
├── main_explorer.py              # 主控制器
└── __init__.py                   # 包初始化
```

## 🔧 配置选项

### ExplorationConfiguration 参数

```python
config = ExplorationConfiguration(
    # 参数空间配置
    f_base_candidates=[110.0, 220.0, 440.0],  # 基频候选值
    f_min=110.0,                              # 最小频率
    f_max=880.0,                              # 最大频率
    
    # 筛选标准
    min_entries=5,                            # 最少音符数
    max_entries=60,                           # 最多音符数
    min_interval_cents=5.0,                   # 最小音程
    max_interval_cents=600.0,                 # 最大音程
    
    # 功能开关
    enable_audio_testing=True,                # 启用音频测试
    enable_detailed_analysis=True,            # 启用详细分析
    enable_reporting=True,                    # 启用报告生成
    
    # 性能配置
    max_workers=4,                            # 并行线程数
    audio_test_sample_size=20,                # 音频测试样本数
    
    # 输出配置
    report_name="my_exploration",             # 报告名称
    output_dir=Path("./output")               # 输出目录
)
```

## 📊 评估维度

PetersenExplorer使用8个维度评估音律系统：

1. **传统兼容性** (traditional_compatibility): 与传统音乐理论的兼容程度
2. **微分音潜力** (microtonal_potential): 微分音表达能力
3. **世界音乐亲和性** (world_music_affinity): 与非西方音乐传统的兼容性
4. **实验创新性** (experimental_innovation): 创新性和独特性
5. **治疗价值** (therapeutic_value): 音乐治疗和身心健康应用潜力
6. **和声丰富度** (harmonic_richness): 和声构建能力
7. **旋律表达力** (melodic_expressiveness): 旋律构建和表达能力
8. **技术可行性** (technical_feasibility): 实际实现和使用的技术难度

## 🏷️ 分类体系

基于评估结果，系统被分类为：

- **传统扩展型**: 在传统音乐基础上的创新扩展
- **微分音探索型**: 专注于微细音程变化的表达
- **实验前卫型**: 完全突破传统框架的创新系统
- **世界音乐融合型**: 与非西方音乐传统的融合
- **声音艺术型**: 超越音乐进入声音艺术领域
- **治疗功能型**: 专注于音乐治疗和身心健康应用
- **综合混合型**: 多维度均衡发展的系统
- **研究探索型**: 适合理论研究和教学的系统

## 🎵 音频测试

PetersenExplorer集成了Enhanced Petersen Player进行实际音频验证：

### 测试类型

- **音阶测试**: 上行/下行音阶播放
- **音程跳跃**: 大音程跳跃能力测试
- **简单旋律**: 旋律构建能力测试
- **和弦进行**: 和声播放能力测试
- **泛音列**: 自然泛音关系测试

### 配置音频测试

```python
# 指定SoundFont路径
config.soundfont_path = "path/to/your/soundfont.sf2"

# 启用音频测试
config.enable_audio_testing = True
config.audio_test_sample_size = 10  # 测试前10个最优系统
```

## 📋 报告系统

探索完成后，PetersenExplorer会生成详细的分析报告：

### 报告结构

```
report_name/
├── README.md                      # 报告索引
├── executive_summary.md           # 执行摘要
├── detailed_analysis/             # 详细分析
│   ├── phi_presets_analysis.md    # φ值分析
│   ├── delta_theta_analysis.md    # δθ值分析
│   └── musical_characteristics.md # 音乐特性分析
├── data_exports/                  # 数据导出
│   ├── complete_exploration_data.csv
│   ├── detailed_data.json
│   └── scale_files/              # 可导入的音阶文件
└── recommendations.md            # 应用建议
```

### 数据导出

- **CSV格式**: 完整的数值数据，适合统计分析
- **JSON格式**: 详细的结构化数据，适合程序处理
- **音阶文件**: Enhanced Petersen Player可直接导入的格式

## 💡 使用示例

### 寻找传统音乐适用的系统

```python
# 获取传统兼容性高的系统
traditional_systems = explorer.get_top_systems(10, criteria="traditional")

for result, evaluation, classification in traditional_systems:
    print(f"系统: {result.parameters.phi_name} × {result.parameters.delta_theta_name}")
    print(f"传统兼容性: {evaluation.dimension_scores['traditional_compatibility'].score:.3f}")
```

### 寻找实验音乐系统

```python
# 获取创新性高的系统
experimental_systems = explorer.get_top_systems(10, criteria="experimental")

for result, evaluation, classification in experimental_systems:
    print(f"系统: {result.parameters.phi_name} × {result.parameters.delta_theta_name}")
    print(f"实验创新性: {evaluation.dimension_scores['experimental_innovation'].score:.3f}")
```

### 导出用于音乐制作

```python
# 导出前5名系统为Enhanced Petersen Player格式
exported_files = explorer.export_top_systems_for_player(5)

print("可导入音阶文件:")
for file_path in exported_files:
    print(f"- {file_path}")
```

## ⚙️ 系统要求

- Python 3.8+
- Enhanced Petersen Player (音频测试功能)
- 推荐SoundFont: Steinway钢琴SoundFont
- 可选: 并行处理支持

## 🤝 扩展开发

PetersenExplorer设计为模块化和可扩展的：

### 添加新的评估维度

```python
from PetersenExplorer.core.evaluation_framework import EvaluationDimension

# 自定义评估维度
class CustomEvaluator(MultiDimensionalEvaluator):
    def _evaluate_custom_dimension(self, characteristics):
        # 实现自定义评估逻辑
        pass
```

### 添加新的分类类别

```python
from PetersenExplorer.core.classification_system import PrimaryCategory

# 扩展分类系统
class ExtendedClassificationSystem(OpenClassificationSystem):
    # 添加新的分类逻辑
    pass
```

## 📞 支持和贡献

- 问题报告: 请提交详细的问题描述和复现步骤
- 功能建议: 欢迎提出新的评估维度和分类标准
- 代码贡献: 请遵循现有的代码风格和文档标准

## 📄 许可证

本项目采用开源许可证，具体条款请查看LICENSE文件。

---

**PetersenExplorer**: 开放探索，多元发现，音乐无界