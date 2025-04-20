import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_time_series(time_data):
    st.header("Time Series Sentiment Trends")
    
    # 确保数据包含必要的列
    required_columns = ["creator", "date", "positive_ratio"]
    missing_columns = [col for col in required_columns if col not in time_data.columns]
    
    if missing_columns:
        st.error(f"Data is missing required columns: {', '.join(missing_columns)}")
        return
    
    # 获取所有创作者
    creators = time_data["creator"].unique()
    
    # 将日期转换为日期时间格式(如果尚未)
    time_data["date"] = pd.to_datetime(time_data["date"])
    
    # 创建情感随时间变化的趋势
    st.subheader("Positive Sentiment Trends Over Time")
    
    # 创建多线图
    fig = px.line(
        time_data,
        x="date",
        y="positive_ratio",
        color="creator",
        title="Positive Sentiment Trends by Creator",
        labels={"date": "Date", "positive_ratio": "Positive Sentiment Ratio", "creator": "Creator"},
        line_shape="spline"
    )
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建带交互选择的趋势
    st.subheader("Interactive Creator Comparison")
    
    # 创建创作者选择器
    selected_creators = st.multiselect(
        "Select Creators to Compare",
        options=creators,
        default=creators[:2] if len(creators) > 1 else creators
    )
    
    if not selected_creators:
        st.warning("Please select at least one creator to analyze")
        return
    
    # 过滤数据
    filtered_trends = time_data[time_data["creator"].isin(selected_creators)]
    
    # 创建趋势图
    fig = px.line(
        filtered_trends,
        x="date",
        y="positive_ratio",
        color="creator",
        title="Comparative Sentiment Trends",
        labels={"date": "Date", "positive_ratio": "Positive Sentiment Ratio", "creator": "Creator"},
        line_shape="spline"
    )
    
    # 添加范围滑块
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建时间周期分析
    st.subheader("Periodic Sentiment Analysis")
    
    # 创建时间周期选择
    period_type = st.radio(
        "Select Time Period Analysis",
        ["Weekly", "Monthly", "Quarterly"]
    )
    
    # 基于选择的时间周期添加时间列
    time_data_with_period = time_data.copy()
    
    if period_type == "Weekly":
        time_data_with_period["period"] = time_data_with_period["date"].dt.isocalendar().week
        period_name = "Week of Year"
    elif period_type == "Monthly":
        time_data_with_period["period"] = time_data_with_period["date"].dt.month
        period_name = "Month"
    else:  # Quarterly
        time_data_with_period["period"] = time_data_with_period["date"].dt.quarter
        period_name = "Quarter"
    
    # 计算每个周期的平均情感
    period_summary = time_data_with_period.groupby(["creator", "period"])["positive_ratio"].mean().reset_index()
    
    # 创建周期分析图
    fig = px.bar(
        period_summary,
        x="period",
        y="positive_ratio",
        color="creator",
        barmode="group",
        title=f"Sentiment by {period_name}",
        labels={"period": period_name, "positive_ratio": "Positive Sentiment Ratio", "creator": "Creator"},
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建情感与参与度关系
    st.subheader("Sentiment vs. Engagement Analysis")
    
    # 确保数据有一个参与度列
    if "engagement" not in time_data.columns:
        st.warning("Data does not contain engagement metrics")
    else:
        # 创建散点图展示情感与参与度的关系
        fig = px.scatter(
            time_data[time_data["creator"].isin(selected_creators)],
            x="positive_ratio",
            y="engagement",
            color="creator",
            size="engagement",
            hover_data=["date"],
            title="Sentiment vs. Engagement",
            labels={"positive_ratio": "Positive Sentiment Ratio", "engagement": "Engagement", "creator": "Creator"},
            height=500
        )
        
        # 添加趋势线
        fig.update_layout(
            shapes=[
                dict(
                    type="line",
                    yref="paper", y0=0, y1=1,
                    xref="x", x0=0.5, x1=0.5,
                    line=dict(
                        color="gray",
                        width=1,
                        dash="dash",
                    )
                )
            ]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 创建热力图显示情感随时间变化
    st.subheader("Sentiment Heatmap Over Time")
    
    # 创建数据点
    # 将日期转换为更粗粒度的格式用于热力图
    heatmap_data = time_data.copy()
    heatmap_data["year_month"] = heatmap_data["date"].dt.strftime("%Y-%m")
    
    # 创建透视表
    pivot_heat = heatmap_data.pivot_table(
        index="creator",
        columns="year_month",
        values="positive_ratio",
        aggfunc="mean"
    ).fillna(0)
    
    # 创建热力图
    fig = px.imshow(
        pivot_heat,
        color_continuous_scale="RdYlGn",
        labels=dict(x="Month", y="Creator", color="Positive Ratio"),
        title="Sentiment Heatmap Over Time",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 提供下载数据功能
    st.markdown("### Download Time Series Data")
    csv = time_data.to_csv(index=False)
    st.download_button(
        label="Download Time Series Data",
        data=csv,
        file_name="time_series_analysis.csv",
        mime="text/csv",
    ) 