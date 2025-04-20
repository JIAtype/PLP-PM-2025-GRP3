# import streamlit as st
# import pandas as pd
# import numpy as np
# import altair as alt
# import plotly.express as px
# import plotly.graph_objects as go

# def show_topic_analysis():

#     st.header("Positive Sentiment Topic Analysis")
    
#     st.subheader("Topic Sentiment Overview")

#     topic_sentiment_df = pd.read_csv('data/topic_sentiment_summary.csv')

#     fig = px.bar(
#         topic_sentiment_df.head(20),
#         x="Topic",
#         y="% Positive",
#         title="Top 20 Topics by Positive Sentiment (%)",
#         labels={"% Positive": "Positive Sentiment (%)"},
#         color="% Positive",
#         color_continuous_scale="Blues"
#     )
#     fig.update_layout(xaxis_tickangle=-45)
#     fig.show()

#     st.subheader("第二个图")
#     import plotly.express as px

#     # Melt the DataFrame to long format for grouped bar plotting
#     melted_df = topic_sentiment_df.melt(
#         id_vars=["Topic", "Total Mentions"],
#         value_vars=["Positive", "Negative", "Neutral"],
#         var_name="Sentiment",
#         value_name="Count"
#     )

#     # Optional: Filter to top N topics by mentions
#     top_topics = melted_df["Topic"].value_counts().index[:20]
#     melted_df = melted_df[melted_df["Topic"].isin(top_topics)]

#     # Plot grouped bar chart
#     fig = px.bar(
#         melted_df,
#         x="Topic",
#         y="Count",
#         color="Sentiment",
#         barmode="group",
#         title="Sentiment Breakdown per Topic",
#         labels={"Count": "Number of Comments"}
#     )
#     fig.update_layout(xaxis_tickangle=-45)
#     fig.show()

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

def show_topic_analysis():
    st.header("Positive Sentiment Topic Analysis")
    topic_sentiment_df = pd.read_csv('data/topic_sentiment_summary.csv')
    
        
    # 计算总提及次数和百分比
    topic_sentiment_df["Total Mentions"] = (
        topic_sentiment_df["Positive"] + 
        topic_sentiment_df["Negative"] + 
        topic_sentiment_df["Neutral"]
    )
    
    topic_sentiment_df["% Positive"] = (topic_sentiment_df["Positive"] / topic_sentiment_df["Total Mentions"] * 100).round(2)
    topic_sentiment_df["% Negative"] = (topic_sentiment_df["Negative"] / topic_sentiment_df["Total Mentions"] * 100).round(2)
    topic_sentiment_df["% Neutral"] = (topic_sentiment_df["Neutral"] / topic_sentiment_df["Total Mentions"] * 100).round(2)
    
    # 按照正面情感百分比排序
    topic_sentiment_df = topic_sentiment_df.sort_values("% Positive", ascending=False).reset_index(drop=True)
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Topic Sentiment Overview")
        # 显示前20个话题的正面情感百分比条形图
        fig = px.bar(
            topic_sentiment_df.head(20),
            x="Topic",
            y="% Positive",
            title="Top 20 Topics by Positive Sentiment (%)",
            labels={"% Positive": "Positive Sentiment (%)"},
            color="% Positive",
            color_continuous_scale="Blues",
            text="% Positive"  # 在条形上显示数值
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            xaxis_title="Topic",
            yaxis_title="Positive Sentiment (%)"
        )
        
        # 添加数值标签格式
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        
        # Streamlit中正确显示plotly图表
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 显示热门话题的数据表格
        st.subheader("Top Topics Data")
        st.dataframe(
            topic_sentiment_df.head(10)[["Topic", "Total Mentions", "% Positive", "% Negative", "% Neutral"]]
            .style.background_gradient(subset=["% Positive"], cmap="Blues")
            .format({"% Positive": "{:.2f}%", "% Negative": "{:.2f}%", "% Neutral": "{:.2f}%"})
        )
    
    st.subheader("Sentiment Breakdown per Topic")
    
    # 准备数据：融合数据框为长格式，用于分组条形图
    melted_df = topic_sentiment_df.melt(
        id_vars=["Topic", "Total Mentions"],
        value_vars=["Positive", "Negative", "Neutral"],
        var_name="Sentiment",
        value_name="Count"
    )
    
    # 过滤出按提及次数排序的前N个话题
    top_n = min(15, len(topic_sentiment_df))  # 防止数据量太小
    top_topics = topic_sentiment_df.nlargest(top_n, "Total Mentions")["Topic"].tolist()
    filtered_df = melted_df[melted_df["Topic"].isin(top_topics)]
    
    # 绘制分组条形图
    fig = px.bar(
        filtered_df,
        x="Topic",
        y="Count",
        color="Sentiment",
        barmode="group",
        title=f"Sentiment Breakdown for Top {top_n} Topics by Mentions",
        labels={"Count": "Number of Comments", "Topic": "Topic"},
        color_discrete_map={
            "Positive": "#2ca02c",  # 绿色
            "Negative": "#d62728",  # 红色
            "Neutral": "#1f77b4"    # 蓝色
        },
        hover_data=["Total Mentions"]
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        legend_title="Sentiment Type",
        xaxis_title="Topic",
        yaxis_title="Number of Comments"
    )
    
    # Streamlit中正确显示plotly图表
    st.plotly_chart(fig, use_container_width=True)
    
    # 添加堆叠百分比图表
    st.subheader("Proportional Sentiment Distribution")
    
    # 准备比例图数据
    stack_data = topic_sentiment_df.head(10).copy()  # 只取前10个话题，避免拥挤
    
    fig = px.bar(
        stack_data,
        x="Topic",
        y=["% Positive", "% Negative", "% Neutral"],
        title="Sentiment Proportion for Top 10 Topics",
        labels={"value": "Percentage (%)", "variable": "Sentiment Type"},
        barmode="stack",
        color_discrete_map={
            "% Positive": "#2ca02c",
            "% Negative": "#d62728",
            "% Neutral": "#1f77b4"
        }
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        legend_title="Sentiment Type",
        xaxis_title="Topic",
        yaxis_title="Percentage (%)"
    )
    
    # Streamlit中正确显示plotly图表
    st.plotly_chart(fig, use_container_width=True)
    
    # 添加散点图，展示话题热度与正面情感的关系
    st.subheader("Topic Popularity vs. Positive Sentiment")
    
    fig = px.scatter(
        topic_sentiment_df,
        x="Total Mentions",
        y="% Positive",
        size="Total Mentions",  # 气泡大小表示总提及量
        color="% Positive",     # 颜色表示正面情感百分比
        hover_name="Topic",     # 悬停时显示话题名称
        text="Topic",           # 在图上标注话题名称
        color_continuous_scale="Blues",
        title="Topic Popularity vs. Positive Sentiment",
        labels={
            "Total Mentions": "Total Mentions (Popularity)",
            "% Positive": "Positive Sentiment (%)"
        }
    )
    
    # 只显示部分标签，避免重叠
    top_mentions = topic_sentiment_df.nlargest(5, "Total Mentions")["Topic"].tolist()
    top_positive = topic_sentiment_df.nlargest(5, "% Positive")["Topic"].tolist()
    topics_to_show = list(set(top_mentions + top_positive))
    
    fig.update_traces(
        textposition='top center',
        textfont_size=10,
        marker=dict(opacity=0.7),
        # 只为特定点显示文本
        mode=lambda d: 'markers+text' if d.get('hovertext') in topics_to_show else 'markers'
    )
    
    fig.update_layout(
        height=600,
        showlegend=False
    )
    
    # Streamlit中正确显示plotly图表
    st.plotly_chart(fig, use_container_width=True)