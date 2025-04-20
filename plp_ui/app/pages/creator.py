from app.components.spam_summary import show_spam_summary
import streamlit as st
import json
from collections import defaultdict
import pandas as pd
import numpy as np
import altair as alt
from app.components.video_analysis import show_video_analysis
from app.components.overview import show_overview_analysis
from app.components.spam_analysis import show_spam_analysis

def show_creator_page():
    st.title("Content Creator Analytics")
    
    # 加载示例数据
    # 实际使用时，应该连接到真实的数据源
    @st.cache_data
    def load_creator_data():
        # 这里是模拟数据
        # 实际应用中，这应该从数据库或API获取
        return {
            "videos": pd.DataFrame({
                "video_id": [f"v{i}" for i in range(1, 11)],
                "title": [f"Video {i}" for i in range(1, 11)],
                "creator": np.random.choice(["Fully Charged Show", "Bjorn Nyland", "Electric Vehicle Man", "Now You Know", "E for Electric"], 10),
                "comments": np.random.randint(50, 500, 10),
                "topics": np.random.randint(3, 15, 10),
                "positive": np.random.uniform(0.3, 0.8, 10),
                "negative": np.random.uniform(0.05, 0.3, 10),
                "neutral": np.random.uniform(0.1, 0.4, 10),
            }),
            "topics": pd.DataFrame({
                "topic": [f"Topic {i}" for i in range(1, 16)],
                "creator": np.random.choice(["Fully Charged Show", "Bjorn Nyland", "Electric Vehicle Man", "Now You Know", "E for Electric"], 15),
                "positive": np.random.uniform(0.3, 0.9, 15),
                "negative": np.random.uniform(0.05, 0.4, 15),
                "neutral": np.random.uniform(0.05, 0.3, 15),
            }),
            "entities": pd.DataFrame({
                "entity": [f"Entity {i}" for i in range(1, 21)],
                "creator": np.random.choice(["Fully Charged Show", "Bjorn Nyland", "Electric Vehicle Man", "Now You Know", "E for Electric"], 20),
                "mentions": np.random.randint(5, 100, 20),
                "sentiment": np.random.uniform(-1, 1, 20),
                "category": np.random.choice(["Person", "Product", "Place", "Organization"], 20),
            })
        }
    
    data = load_creator_data()
    
    # 创建侧边栏过滤器
    st.sidebar.subheader("Content Creator Analytics")
    
    # 选择时间范围(模拟)
    # st.sidebar.date_input("Date Range", value=(pd.to_datetime("2023-01-01"), pd.to_datetime("2023-12-31")))
    
    # 添加Content Creator过滤器
    creator_options = ["Fully Charged Show", "Bjorn Nyland", "Electric Vehicle Man", "Now You Know", "E for Electric"]
    selected_creator = st.sidebar.selectbox("Select Content Creator", creator_options)

    analysis_type = st.sidebar.radio(
        "Select Analysis",
        ["Overview","Sentiment Analysis", "Spam Analysis", "Spam Summary"]
    )
    
    # 根据选择的分析类型显示相应的组件，并传递过滤后的数据
    if analysis_type == "Sentiment Analysis":
        show_video_analysis(selected_creator)
    elif analysis_type == "Overview":
        show_overview_analysis(selected_creator)
    elif analysis_type == "Spam Analysis":
        show_spam_analysis()
    elif analysis_type == "Spam Summary":
        show_spam_summary(selected_creator)