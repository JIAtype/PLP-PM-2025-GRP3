import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

def show_creator_comparison(videos_data):
    st.header("Creator Comparison Overview")
    
    # 确保数据中有creator列
    if "creator" not in videos_data.columns:
        st.error("Data does not contain creator information!")
        return
    
    # 计算每个创作者的汇总统计数据
    creator_summary = videos_data.groupby("creator").agg({
        "comments": ["sum", "mean"],
        "positive": "mean",
        "negative": "mean",
        "neutral": "mean",
        "video_id": "count"
    })
    
    # 修改列名以使其更易读
    creator_summary.columns = [
        "total_comments", "avg_comments_per_video", 
        "avg_positive", "avg_negative", "avg_neutral", 
        "video_count"
    ]
    
    creator_summary = creator_summary.reset_index()
    
    # 显示创作者比较的KPI指标卡
    st.subheader("Creator Performance Metrics")
    
    # 为每个创作者显示关键指标
    creators = creator_summary["creator"].tolist()
    columns = st.columns(len(creators))
    
    for i, creator in enumerate(creators):
        creator_data = creator_summary[creator_summary["creator"] == creator].iloc[0]
        
        with columns[i]:
            st.subheader(creator)
            st.metric("Total Videos", f"{int(creator_data['video_count'])}")
            st.metric("Total Comments", f"{int(creator_data['total_comments']):,}")
            st.metric("Avg. Positive", f"{creator_data['avg_positive']*100:.1f}%")
            
            # 创建简单的进度条
            pos = creator_data["avg_positive"]
            neg = creator_data["avg_negative"]
            neu = creator_data["avg_neutral"]
            
            st.markdown(f"**Sentiment Ratio:**")
            st.markdown(
                f"""
                <div style="display: flex; width: 100%; height: 20px;">
                    <div style="background-color: green; width: {pos*100}%; height: 100%;"></div>
                    <div style="background-color: gray; width: {neu*100}%; height: 100%;"></div>
                    <div style="background-color: red; width: {neg*100}%; height: 100%;"></div>
                </div>
                <div style="display: flex; width: 100%; justify-content: space-between; font-size: 12px;">
                    <div>Positive: {pos*100:.1f}%</div>
                    <div>Neutral: {neu*100:.1f}%</div>
                    <div>Negative: {neg*100:.1f}%</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # 创建情感分布比较图
    st.subheader("Sentiment Distribution by Creator")
    
    # 准备情感数据用于可视化
    sentiment_data = []
    for _, row in creator_summary.iterrows():
        sentiment_data.extend([
            {"creator": row["creator"], "sentiment": "Positive", "percentage": row["avg_positive"]},
            {"creator": row["creator"], "sentiment": "Neutral", "percentage": row["avg_neutral"]},
            {"creator": row["creator"], "sentiment": "Negative", "percentage": row["avg_negative"]}
        ])
    
    sentiment_df = pd.DataFrame(sentiment_data)
    
    # 创建堆叠条形图
    fig = px.bar(
        sentiment_df,
        x="creator",
        y="percentage",
        color="sentiment",
        color_discrete_map={"Positive": "green", "Neutral": "gray", "Negative": "red"},
        title="Sentiment Distribution Comparison",
        labels={"percentage": "Percentage", "creator": "Creator", "sentiment": "Sentiment Type"},
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建互动量和情感关系散点图
    st.subheader("Engagement vs. Sentiment Analysis")
    
    # 准备散点图数据
    videos_data["sentiment_score"] = videos_data["positive"] - videos_data["negative"]
    
    # 创建散点图
    fig = px.scatter(
        videos_data,
        x="comments",
        y="sentiment_score",
        color="creator",
        size="comments",
        hover_name="title",
        title="Engagement vs. Sentiment Score by Video",
        labels={"comments": "Comment Count", "sentiment_score": "Sentiment Score", "creator": "Creator"},
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建视频性能热力图
    st.subheader("Video Performance Heatmap")
    
    # 按创作者和视频ID透视数据
    pivot_videos = videos_data.pivot_table(
        index="creator",
        columns="title",
        values="positive",
        aggfunc="mean"
    ).fillna(0)
    
    # 创建热力图
    fig = px.imshow(
        pivot_videos,
        color_continuous_scale="RdYlGn",
        labels=dict(x="Video", y="Creator", color="Positive %"),
        title="Creator-Video Positive Sentiment Matrix"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 总体创作者排名
    st.subheader("Overall Creator Rankings")
    
    # 计算总体得分 (这只是一个简单的例子，实际应用中可能需要更复杂的计算)
    creator_summary["overall_score"] = (
        creator_summary["avg_positive"] * 2 - 
        creator_summary["avg_negative"] * 1.5 + 
        creator_summary["avg_comments_per_video"] / 100
    )
    
    # 按总体得分排序
    ranked_creators = creator_summary.sort_values(by="overall_score", ascending=False).reset_index(drop=True)
    
    # 显示排名表格
    st.dataframe(
        ranked_creators[["creator", "overall_score", "avg_positive", "avg_negative", "total_comments"]],
        column_config={
            "creator": "Creator",
            "overall_score": st.column_config.NumberColumn(
                "Overall Score",
                format="%.2f"
            ),
            "avg_positive": st.column_config.ProgressColumn(
                "Positive %",
                format="%.1f%%",
                min_value=0,
                max_value=1
            ),
            "avg_negative": st.column_config.ProgressColumn(
                "Negative %",
                format="%.1f%%",
                min_value=0,
                max_value=1
            ),
            "total_comments": st.column_config.NumberColumn(
                "Total Comments",
                format="%d"
            )
        },
        hide_index=True
    )
    
    # 下载数据功能
    st.markdown("### Download Comparison Data")
    csv = creator_summary.to_csv(index=False)
    st.download_button(
        label="Download Creator Comparison Data",
        data=csv,
        file_name="creator_comparison.csv",
        mime="text/csv",
    ) 