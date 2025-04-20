# Content Analysis Dashboard

这是一个基于Streamlit的交互式用户界面，为内容创作者和企业提供定制化的分析结果展示。该应用程序允许用户浏览和分析视频评论、情感和主题数据，以获取有价值的洞察。

## 功能

### 内容创作者模块

- **视频级别分析**：展示每个视频的评论数和主题数，并利用颜色梯度直观地突出高互动和高主题的视频
- **创作者汇总**：展示每个创作者的总体情感百分比和评论总数
- **积极情感主题分析**：按积极情感百分比排序主题，展示每个主题的情感分布
- **实体情感分析**：展示评论中出现的实体及其情感得分

### 商业用途模块

- **创作者比较概览**：比较多个创作者的关键指标
- **情感分析方法选择**：展示不同情感分析方法的结果
- **基于主题/方面的分析**：展示各创作者不同主题/方面的情感分析
- **时间序列趋势**：展示情感随时间的变化趋势

## 项目结构

```
plp_ui/
├── app.py                    # 主程序入口
├── app/
│   ├── pages/                # 页面模块
│   │   ├── home.py           # 主页
│   │   ├── creator.py        # 内容创作者页面
│   │   └── business.py       # 商业用户页面
│   ├── components/           # 组件模块
│   │   ├── video_analysis.py # 视频分析组件
│   │   ├── creator_summary.py# 创作者汇总组件
│   │   ├── topic_analysis.py # 主题分析组件
│   │   ├── entity_analysis.py# 实体分析组件
│   │   ├── creator_comparison.py # 创作者比较组件
│   │   ├── sentiment_methods.py  # 情感分析方法组件
│   │   ├── aspect_analysis.py    # 方面分析组件
│   │   └── time_series.py        # 时间序列组件
│   ├── utils/                # 工具函数
│   └── data/                 # 数据处理模块
├── requirements.txt          # 项目依赖
└── README.md                 # 项目说明
```

## 安装与运行

1. 安装依赖项:

```bash
pip install -r requirements.txt
```

2. 运行应用程序:

```bash
streamlit run app.py
```

## 系统要求

- Python 3.8+
- 安装requirements.txt中列出的所有包
