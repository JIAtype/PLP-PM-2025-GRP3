import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

def show_creator_summary(videos_data):
    st.header("Creator Analytics Summary")
    
    # 假设我们有多个创作者的数据，为了演示，我们添加一个创作者列
    videos_data = videos_data.copy()
    creators = ["Creator A", "Creator B", "Creator C"]
    videos_data["creator"] = np.random.choice(creators, size=len(videos_data))
    
    # 计算每个创作者的总体情感分布
    creator_summary = videos_data.groupby("creator").agg({
        "comments": "sum",
        "positive": "mean",
        "negative": "mean",
        "neutral": "mean",
        "video_id": "count"
    }).reset_index()
    
    creator_summary = creator_summary.rename(columns={"video_id": "videos_count"})
    
    # 显示创作者摘要
    st.subheader("Creator Performance Overview")
    
    # KPI 指标卡片
    total_videos = creator_summary["videos_count"].sum()
    total_comments = creator_summary["comments"].sum()
    avg_positive = creator_summary["positive"].mean() * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Videos", f"{total_videos}")
    
    with col2:
        st.metric("Total Comments", f"{total_comments:,}")
    
    with col3:
        st.metric("Avg. Positive Sentiment", f"{avg_positive:.1f}%")
    
    # 创作者表现表格
    st.markdown("### Creator Performance Metrics")
    
    # 格式化百分比
    display_summary = creator_summary.copy()
    for col in ['positive', 'negative', 'neutral']:
        display_summary[col] = display_summary[col].apply(lambda x: f"{x*100:.1f}%")
    
    st.dataframe(display_summary)
    
    # 创作者情感百分比饼图
    st.subheader("Creator Sentiment Distribution")
    
    # 创建创作者选择器
    selected_creator = st.selectbox(
        "Select Creator",
        creator_summary["creator"].tolist()
    )
    
    # 获取所选创作者的数据
    creator_data = creator_summary[creator_summary["creator"] == selected_creator].iloc[0]
    
    # 准备饼图数据
    sentiment_labels = ["Positive", "Negative", "Neutral"]
    sentiment_values = [creator_data["positive"], creator_data["negative"], creator_data["neutral"]]
    
    # 创建饼图
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_labels,
        values=sentiment_values,
        hole=.4,
        marker_colors=['green', 'red', 'gray']
    )])
    
    fig.update_layout(
        title_text=f"Sentiment Distribution for {selected_creator}",
        annotations=[dict(text=f"{float(creator_data['positive'])*100:.1f}%<br>Positive", x=0.5, y=0.5, font_size=15, showarrow=False)]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 创作者评论数量比较
    st.subheader("Creator Comment Volumes")
    
    # 创建条形图
    fig = px.bar(
        creator_summary,
        x="creator",
        y="comments",
        color="positive",
        color_continuous_scale="Viridis",
        title="Comment Volume by Creator (colored by positive sentiment)",
        labels={"comments": "Total Comments", "creator": "Creator", "positive": "Positive %"},
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建可下载的分析汇总
    st.markdown("### Download Analysis")
    csv = creator_summary.to_csv(index=False)
    st.download_button(
        label="Download Creator Summary",
        data=csv,
        file_name="creator_summary.csv",
        mime="text/csv",
    ) 