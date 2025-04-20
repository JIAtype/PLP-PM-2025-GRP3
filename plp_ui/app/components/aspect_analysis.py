import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_aspect_analysis(aspects_data):
    st.header("Aspect-Based Sentiment Analysis")
    
    # 确保数据包含必要的列
    required_columns = ["creator", "aspect", "video_id"]
    missing_columns = [col for col in required_columns if col not in aspects_data.columns]
    
    if missing_columns:
        st.error(f"Data is missing required columns: {', '.join(missing_columns)}")
        return
    
    # 选择情感分析方法（如果有多种）
    sentiment_methods = [col for col in aspects_data.columns if col.endswith('_sentiment')]
    
    if not sentiment_methods:
        st.error("Data does not contain sentiment analysis method results!")
        return
    
    # 让用户选择使用哪种情感分析方法
    method_names = [method.replace('_sentiment', '') for method in sentiment_methods]
    selected_method = st.selectbox(
        "Select Sentiment Analysis Method",
        options=method_names,
        index=0
    )
    
    sentiment_column = f"{selected_method}_sentiment"
    
    # 创建基于方面的分析
    st.subheader(f"Aspect-Based Analysis using {selected_method}")
    
    # 首先按创作者和方面计算平均情感分数
    aspect_summary = aspects_data.groupby(["creator", "aspect"])[sentiment_column].mean().reset_index()
    aspect_summary = aspect_summary.rename(columns={sentiment_column: "sentiment_score"})
    
    # 按创作者和积极情感百分比排序主题
    creators = aspects_data["creator"].unique()
    aspects = aspects_data["aspect"].unique()
    
    # 创建每个创作者的主题百分比表格
    st.markdown("### Aspect Sentiment by Creator")
    
    # 计算基于积极情感百分比的TOP方面
    def get_positive_aspects(creator_data, top_n=10):
        # 对方面按情感分数排序
        sorted_aspects = creator_data.sort_values(by="sentiment_score", ascending=False)
        return sorted_aspects.head(top_n)
    
    # 显示各创作者的前10个方面
    col1, col2 = st.columns(2)
    
    # 创作者选择
    with col1:
        creator1 = st.selectbox("Select First Creator", options=creators, index=0, key="creator1")
        creator1_data = aspect_summary[aspect_summary["creator"] == creator1]
        top_aspects1 = get_positive_aspects(creator1_data)
        
        st.markdown(f"#### Top Aspects for {creator1}")
        st.dataframe(
            top_aspects1,
            column_config={
                "aspect": "Aspect",
                "sentiment_score": st.column_config.ProgressColumn(
                    "Sentiment",
                    format="%.2f",
                    min_value=-1,
                    max_value=1,
                )
            },
            hide_index=True
        )
        
    with col2:
        creator2 = st.selectbox("Select Second Creator", options=creators, index=min(1, len(creators)-1), key="creator2")
        creator2_data = aspect_summary[aspect_summary["creator"] == creator2]
        top_aspects2 = get_positive_aspects(creator2_data)
        
        st.markdown(f"#### Top Aspects for {creator2}")
        st.dataframe(
            top_aspects2,
            column_config={
                "aspect": "Aspect",
                "sentiment_score": st.column_config.ProgressColumn(
                    "Sentiment",
                    format="%.2f",
                    min_value=-1,
                    max_value=1,
                )
            },
            hide_index=True
        )
    
    # 创建单个创作者的方面热力图
    st.subheader("Creator's Aspect Sentiment Heatmap")
    
    selected_creator_heatmap = st.selectbox("Select Creator for Heatmap", options=creators)
    
    # 获取所选创作者的数据
    creator_aspects = aspects_data[aspects_data["creator"] == selected_creator_heatmap]
    
    # 创建透视表，显示方面和视频之间的情感
    pivot_data = creator_aspects.pivot_table(
        index="aspect",
        columns="video_id",
        values=sentiment_column,
        aggfunc="mean"
    ).fillna(0)
    
    # 创建热力图
    fig = px.imshow(
        pivot_data,
        color_continuous_scale="RdYlGn",
        labels=dict(x="Video", y="Aspect", color="Sentiment"),
        title=f"Aspect-Video Sentiment Heatmap for {selected_creator_heatmap}",
        height=max(400, 100 + len(pivot_data) * 25)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建创作者之间的方面比较
    st.subheader("Aspect Comparison Between Creators")
    
    # 用户可以选择要比较的方面
    selected_aspects = st.multiselect(
        "Select Aspects to Compare",
        options=aspects,
        default=aspects[:5] if len(aspects) > 5 else aspects
    )
    
    if not selected_aspects:
        st.warning("Please select at least one aspect to compare")
        return
    
    # 过滤数据
    filtered_aspects = aspect_summary[aspect_summary["aspect"].isin(selected_aspects)]
    
    # 创建条形图比较创作者在各个方面的表现
    fig = px.bar(
        filtered_aspects,
        x="aspect",
        y="sentiment_score",
        color="creator",
        barmode="group",
        title="Aspect Sentiment Comparison Across Creators",
        labels={"aspect": "Aspect", "sentiment_score": "Sentiment Score", "creator": "Creator"},
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建总合热力图
    st.subheader("Combined Aspect-Creator Sentiment Heatmap")
    
    # 创建方面-创作者透视表
    pivot_combined = filtered_aspects.pivot_table(
        index="aspect",
        columns="creator",
        values="sentiment_score",
        aggfunc="mean"
    ).fillna(0)
    
    # 创建热力图
    fig = px.imshow(
        pivot_combined,
        color_continuous_scale="RdYlGn",
        labels=dict(x="Creator", y="Aspect", color="Sentiment"),
        title="Aspect-Creator Sentiment Heatmap",
        height=max(400, 100 + len(selected_aspects) * 25)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建基于方面的时间趋势分析
    st.subheader("Aspect Sentiment Trends")
    
    # 为演示添加一个模拟的时间列
    @st.cache_data
    def add_time_data():
        # 创建一个随时间变化的模拟数据
        unique_videos = aspects_data["video_id"].unique()
        video_dates = {}
        
        # 为每个视频分配一个日期
        dates = pd.date_range("2023-01-01", periods=len(unique_videos), freq="W")
        for i, video_id in enumerate(unique_videos):
            video_dates[video_id] = dates[i]
        
        # 添加日期列
        aspects_with_dates = aspects_data.copy()
        aspects_with_dates["date"] = aspects_with_dates["video_id"].map(video_dates)
        
        return aspects_with_dates
    
    time_data = add_time_data()
    
    # 创建时间序列图表
    selected_aspect_trend = st.selectbox("Select Aspect for Trend Analysis", options=aspects)
    
    # 过滤数据
    aspect_trend_data = time_data[time_data["aspect"] == selected_aspect_trend]
    
    # 计算每个创作者每个日期的平均情感
    trend_summary = aspect_trend_data.groupby(["creator", "date"])[sentiment_column].mean().reset_index()
    trend_summary = trend_summary.rename(columns={sentiment_column: "sentiment_score"})
    
    # 创建时间序列图
    fig = px.line(
        trend_summary,
        x="date",
        y="sentiment_score",
        color="creator",
        title=f"Sentiment Trend for '{selected_aspect_trend}' Aspect",
        labels={"date": "Date", "sentiment_score": "Sentiment Score", "creator": "Creator"},
        line_shape="spline"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 提供下载数据功能
    st.markdown("### Download Aspect Analysis Data")
    csv = aspect_summary.to_csv(index=False)
    st.download_button(
        label="Download Aspect Analysis Data",
        data=csv,
        file_name="aspect_analysis.csv",
        mime="text/csv",
    ) 