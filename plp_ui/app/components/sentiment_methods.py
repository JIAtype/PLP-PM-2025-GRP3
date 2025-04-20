import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

def show_sentiment_methods(aspects_data):
    st.header("Sentiment Analysis Methods Comparison")
    
    # 确认数据中包含不同的情感分析方法列
    sentiment_methods = [col for col in aspects_data.columns if col.endswith('_sentiment')]
    
    if not sentiment_methods:
        st.error("Data does not contain sentiment analysis method results!")
        return
    
    # 提取方法名称
    method_names = [method.replace('_sentiment', '') for method in sentiment_methods]
    
    # 概述各种方法
    st.subheader("Overview of Sentiment Analysis Methods")
    
    st.markdown("""
    This section compares different sentiment analysis methods applied to the same content:
    
    1. **VADER** - Rule-based sentiment analyzer specifically attuned to sentiments expressed in social media
    2. **RoBERTa** - A transformer-based model trained on large-scale data
    3. **Fine-Tuned ROBERTA ABSA** - RoBERTa fine-tuned for aspect-based sentiment analysis
    4. **BART** - A sequence-to-sequence model for sentiment prediction
    
    The comparison helps identify which method works best for different types of content.
    """)
    
    # 创建方法选择器
    selected_methods = st.multiselect(
        "Select Methods to Compare",
        options=method_names,
        default=method_names
    )
    
    if not selected_methods:
        st.warning("Please select at least one method to analyze")
        return
    
    # 过滤创作者选择
    creators = aspects_data["creator"].unique()
    selected_creator = st.selectbox("Select Creator", options=creators)
    
    creator_data = aspects_data[aspects_data["creator"] == selected_creator]
    
    # 计算每种方法的平均情感分数
    method_averages = {}
    for method_name, method_col in zip(method_names, sentiment_methods):
        if method_name in selected_methods:
            method_averages[method_name] = creator_data[method_col].mean()
    
    # 显示平均分数
    st.subheader(f"Average Sentiment Scores for {selected_creator}")
    
    # 创建条形图
    avg_data = pd.DataFrame({
        "Method": list(method_averages.keys()),
        "Average Sentiment": list(method_averages.values())
    })
    
    # 定义一个颜色映射函数
    def get_color(val):
        if val > 0.2:
            return "green"
        elif val < -0.2:
            return "red"
        else:
            return "gray"
    
    avg_data["Color"] = avg_data["Average Sentiment"].apply(get_color)
    
    fig = px.bar(
        avg_data,
        x="Method",
        y="Average Sentiment",
        color="Color",
        color_discrete_map={"green": "green", "gray": "gray", "red": "red"},
        title=f"Average Sentiment by Method for {selected_creator}",
        labels={"Method": "Sentiment Method", "Average Sentiment": "Average Score (-1 to 1)"},
        height=400
    )
    
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # 比较方法在不同方面的表现
    st.subheader("Method Comparison by Aspect")
    
    # 获取方面列表
    aspects = creator_data["aspect"].unique()
    
    # 用户可以选择特定方面
    selected_aspects = st.multiselect(
        "Select Aspects to Compare",
        options=aspects,
        default=aspects[:5] if len(aspects) > 5 else aspects
    )
    
    if not selected_aspects:
        st.warning("Please select at least one aspect to analyze")
        return
    
    # 过滤数据以获取所选方面
    filtered_data = creator_data[creator_data["aspect"].isin(selected_aspects)]
    
    # 按方面分组计算平均情感分数
    aspect_comparisons = []
    
    for aspect in selected_aspects:
        aspect_data = filtered_data[filtered_data["aspect"] == aspect]
        for method_name, method_col in zip(method_names, sentiment_methods):
            if method_name in selected_methods:
                aspect_comparisons.append({
                    "Aspect": aspect,
                    "Method": method_name,
                    "Sentiment Score": aspect_data[method_col].mean()
                })
    
    aspect_comp_df = pd.DataFrame(aspect_comparisons)
    
    # 创建方法和方面的热力图
    aspect_pivot = aspect_comp_df.pivot(index="Aspect", columns="Method", values="Sentiment Score")
    
    fig = px.imshow(
        aspect_pivot,
        color_continuous_scale="RdYlGn",
        labels=dict(x="Method", y="Aspect", color="Sentiment Score"),
        title=f"Method Comparison by Aspect for {selected_creator}",
        height=100 + len(selected_aspects) * 30
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 方法一致性分析
    st.subheader("Method Agreement Analysis")
    
    # 为所选方法创建散点图矩阵
    if len(selected_methods) > 1:
        # 创建方法之间的散点图矩阵
        scatter_data = filtered_data[["aspect"] + [m + "_sentiment" for m in selected_methods]]
        
        # 重命名列以便更好地显示
        rename_dict = {m + "_sentiment": m for m in selected_methods}
        scatter_data = scatter_data.rename(columns=rename_dict)
        
        # 使用Plotly创建散点图矩阵
        fig = px.scatter_matrix(
            scatter_data,
            dimensions=selected_methods,
            color="aspect",
            title=f"Method Agreement Analysis for {selected_creator}",
            opacity=0.7
        )
        
        fig.update_layout(height=250 * len(selected_methods))
        st.plotly_chart(fig, use_container_width=True)
        
        # 计算方法间的相关性
        corr_matrix = scatter_data[selected_methods].corr()
        
        # 显示相关性热力图
        fig = px.imshow(
            corr_matrix,
            color_continuous_scale="Viridis",
            labels=dict(x="Method", y="Method", color="Correlation"),
            title=f"Correlation Between Sentiment Methods"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示相关系数
        st.markdown("### Correlation Coefficients")
        st.dataframe(corr_matrix.style.background_gradient(cmap="viridis"))
    else:
        st.info("Select at least two methods to see agreement analysis")
    
    # 提供下载数据功能
    st.markdown("### Download Method Comparison Data")
    csv = aspect_comp_df.to_csv(index=False)
    st.download_button(
        label="Download Method Comparison Data",
        data=csv,
        file_name="sentiment_methods_comparison.csv",
        mime="text/csv",
    ) 