import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from app.components.creator_comparison import show_creator_comparison
from app.components.tdidf_roberta_sentiment_analysis import show_tdidf_roberta_sentiment_analysis
from app.components.tdidf_vader_sentiment_analysis import show_tdidf_vader_sentiment_analysis
from app.components.topics_roberta_sentiment_analysis import show_roberta_sentiment_analysis
from app.components.video_summary import show_video_summary
from app.components.sentiment_summary import show_sentiment_summary
from app.components.topic_analysis import show_topic_analysis
from app.components.entity_analysis import show_entity_analysis
from app.components.topics_vader_sentiment_analysis import show_vader_sentiment_analysis
from app.components.tdidf_bart_sentiment_analysis import show_tdidf_bart_sentiment_analysis

def show_business_page():
    st.title("Business Intelligence Dashboard")
    
    # 加载示例数据
    @st.cache_data
    def load_business_data():
        # 模拟多个创作者的数据
        creators = ["Creator A", "Creator B", "Creator C", "Creator D"]
        videos_per_creator = 5
        aspects = ["Quality", "Price", "Design", "Service", "Performance", "Features", "Usability", "Value"]
        
        # 创建创作者-视频数据
        videos_data = []
        for creator in creators:
            for i in range(1, videos_per_creator + 1):
                videos_data.append({
                    "creator": creator,
                    "video_id": f"{creator.lower().replace(' ', '')}_v{i}",
                    "title": f"{creator}'s Video {i}",
                    "views": np.random.randint(1000, 100000),
                    "comments": np.random.randint(50, 1000),
                    "positive": np.random.uniform(0.3, 0.8),
                    "negative": np.random.uniform(0.05, 0.3),
                    "neutral": np.random.uniform(0.05, 0.3),
                })
        
        # 创建基于方面的情感数据
        aspect_data = []
        for creator in creators:
            for aspect in aspects:
                for i in range(1, videos_per_creator + 1):
                    aspect_data.append({
                        "creator": creator,
                        "video_id": f"{creator.lower().replace(' ', '')}_v{i}",
                        "aspect": aspect,
                        "mentions": np.random.randint(5, 50),
                        "vader_sentiment": np.random.uniform(-1, 1),
                        "roberta_sentiment": np.random.uniform(-1, 1),
                        "bart_sentiment": np.random.uniform(-1, 1),
                        "fine_tuned_sentiment": np.random.uniform(-1, 1),
                    })
        
        # 创建时间序列数据
        time_data = []
        dates = pd.date_range("2023-01-01", "2023-12-31", freq="W")
        for creator in creators:
            sentiment_trend = np.cumsum(np.random.normal(0, 0.1, len(dates))) + 0.5  # 创建随机趋势
            sentiment_trend = np.clip(sentiment_trend, 0, 1)  # 限制在0-1范围内
            
            for i, date in enumerate(dates):
                time_data.append({
                    "creator": creator,
                    "date": date,
                    "positive_ratio": sentiment_trend[i],
                    "engagement": np.random.randint(100, 1000)
                })
        
        return {
            "videos": pd.DataFrame(videos_data),
            "aspects": pd.DataFrame(aspect_data),
            "time_series": pd.DataFrame(time_data)
        }
    
    data = load_business_data()
    
    # 创建侧边栏过滤器
    st.sidebar.subheader("Business Intelligence")
    
    # 创作者选择
    selected_creators = st.sidebar.multiselect(
        "Select Creators",
        options=data["videos"]["creator"].unique(),
        default=data["videos"]["creator"].unique()[:2]
    )
    
    # 时间范围选择
    time_range = st.sidebar.date_input(
        "Date Range", 
        value=(data["time_series"]["date"].min(), data["time_series"]["date"].max())
    )
    
    # 分析类型选择
    analysis_type = st.sidebar.radio(
        "Select Analysis",
        ["Creator Comparison","Sentiment Summary","Topic Analysis","Entity Analysis", "Video Summary","Topics As Aspects - VADER Sentiment Analysis","Topics As Aspects - ROBERTA ABSA Sentiment Analysis","TD-IDF Extracted Aspects - VADER Sentiment Analysis","TD-IDF Extracted Aspects - ROBERTA ABSA Sentiment Analysis","TD-IDF Extracted Aspects - BART ABSA Sentiment Analysis"]
    )
    
    # 过滤数据
    filtered_videos = data["videos"][data["videos"]["creator"].isin(selected_creators)]
    filtered_aspects = data["aspects"][data["aspects"]["creator"].isin(selected_creators)]
    filtered_time = data["time_series"][
        (data["time_series"]["creator"].isin(selected_creators)) & 
        (data["time_series"]["date"] >= pd.Timestamp(time_range[0])) &
        (data["time_series"]["date"] <= pd.Timestamp(time_range[1]))
    ]
    
    # 显示选定的分析
    if analysis_type == "Creator Comparison":
        show_creator_comparison(filtered_videos)
    elif analysis_type == "Sentiment Summary":
        show_sentiment_summary()
    elif analysis_type == "Video Summary":
        show_video_summary()
    elif analysis_type == "Topic Analysis":
        show_topic_analysis()
    elif analysis_type == "Entity Analysis":
        show_entity_analysis()
    elif analysis_type == "Topics As Aspects - VADER Sentiment Analysis":
        show_vader_sentiment_analysis()
    elif analysis_type == "Topics As Aspects - ROBERTA ABSA Sentiment Analysis":
        show_roberta_sentiment_analysis()
    elif analysis_type == "TD-IDF Extracted Aspects - VADER Sentiment Analysis":
        show_tdidf_vader_sentiment_analysis()
    elif analysis_type == "TD-IDF Extracted Aspects - ROBERTA ABSA Sentiment Analysis":
        show_tdidf_roberta_sentiment_analysis()
    elif analysis_type == "TD-IDF Extracted Aspects - BART ABSA Sentiment Analysis":
        show_tdidf_bart_sentiment_analysis()