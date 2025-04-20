import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

def show_video_summary():
    st.header("Video-Level Summary")
    
    st.subheader("Overview")
    st.write("This section visualizes sentiment analysis across different content creators based on comments data.")

    # st.set_page_config(layout="wide", page_title="Comment Sentiment Analysis")

    st.title("YouTube Comment Sentiment Analysis")
    st.write("Analysis of sentiment across different YouTube channels using VADER and RoBERTa models")

    try:
        # Load data
        df = pd.read_csv("data/comment_sentiment_roberta_and_vader.csv")
        
        # Show data preview in an expandable section
        with st.expander("Preview of the sentiment data"):
            st.dataframe(df.head(10))
        
        # Create two columns for the first set of charts
        col1, col2 = st.columns(2)
        
        # VADER Sentiment Chart
        with col1:
            fig_vader = px.histogram(
                df, 
                x="sentiment_vader", 
                color="channel",
                title="VADER Sentiment Distribution by Channel",
                labels={"sentiment_vader": "Sentiment Score", "count": "Number of Comments"},
                opacity=0.7,
                color_discrete_sequence=px.colors.qualitative.Bold,
                histnorm='percent',  # Show as percentage for better comparison
                barmode='overlay'  # Overlay bars for easier comparison between channels
            )
            fig_vader.update_layout(
                legend_title_text="Channel",
                xaxis_title="VADER Sentiment Score (Negative → Positive)",
                yaxis_title="Percentage of Comments",
            )
            st.plotly_chart(fig_vader, use_container_width=True)
        
        # RoBERTa Sentiment Chart
        with col2:
            fig_roberta = px.histogram(
                df, 
                x="sentiment_roberta", 
                color="channel",
                title="RoBERTa ABSA Sentiment Distribution by Channel",
                labels={"sentiment_roberta": "Sentiment Score", "count": "Number of Comments"},
                opacity=0.7,
                color_discrete_sequence=px.colors.qualitative.Bold,
                histnorm='percent',  # Show as percentage for better comparison
                barmode='overlay'  # Overlay bars for easier comparison between channels
            )
            fig_roberta.update_layout(
                legend_title_text="Channel",
                xaxis_title="RoBERTa Sentiment Score (Negative → Positive)",
                yaxis_title="Percentage of Comments",
            )
            st.plotly_chart(fig_roberta, use_container_width=True)
        
        # Add some analytical insights
        # st.subheader("Sentiment Model Comparison")
        
        # Comparison scatter plot with trendline
        # if "sentiment_vader" in df.columns and "sentiment_roberta" in df.columns:
        #     fig_compare = px.scatter(
        #         df, 
        #         x="sentiment_vader", 
        #         y="sentiment_roberta", 
        #         color="channel",
        #         title="VADER vs RoBERTa Sentiment Correlation",
        #         labels={
        #             "sentiment_vader": "VADER Sentiment", 
        #             "sentiment_roberta": "RoBERTa Sentiment"
        #         },
        #         opacity=0.6,
        #         color_discrete_sequence=px.colors.qualitative.Bold,
        #         trendline="ols",  # Add trendline for correlation
        #         trendline_scope="overall"
        #     )
        #     fig_compare.update_layout(
        #         legend_title_text="Channel",
        #         height=600,
        #         xaxis_title="VADER Sentiment Score (Negative → Positive)",
        #         yaxis_title="RoBERTa Sentiment Score (Negative → Positive)",
        #     )
        #     st.plotly_chart(fig_compare, use_container_width=True)
            
            # # Calculate correlation
            # correlation = df['sentiment_vader'].corr(df['sentiment_roberta'])
            # st.metric("Correlation between VADER and RoBERTa", f"{correlation:.3f}")
            
            # # Add some insights
            # if correlation > 0.5:
            #     st.info("The sentiment models show strong positive correlation, suggesting they broadly agree on sentiment classification.")
            # elif correlation > 0.2:
            #     st.info("The sentiment models show moderate correlation, with some agreement but also differences in classification approaches.")
            # else:
            #     st.warning("The sentiment models show weak correlation, suggesting they may be detecting different aspects of sentiment.")
        
        # Add time-based analysis
        if "date" in df.columns:
            st.subheader("Sentiment Over Time")
            
            # Convert date to datetime and extract month-year
            df['date'] = pd.to_datetime(df['date'])
            df['month_year'] = df['date'].dt.strftime('%Y-%m')
            
            # Aggregate by month and channel
            monthly_sentiment = df.groupby(['month_year', 'channel']).agg({
                'sentiment_vader': 'mean',
                'sentiment_roberta': 'mean'
            }).reset_index()
            
            # Plot time series
            fig_time = px.line(
                monthly_sentiment, 
                x="month_year", 
                y=["sentiment_vader", "sentiment_roberta"],
                color="channel",
                title="Average Sentiment Score Over Time by Channel",
                labels={
                    "month_year": "Month", 
                    "value": "Avg Sentiment Score",
                    "variable": "Sentiment Model"
                },
                markers=True
            )
            fig_time.update_layout(
                xaxis_title="Time Period",
                yaxis_title="Average Sentiment (Negative → Positive)",
                legend_title="Channel & Model"
            )
            st.plotly_chart(fig_time, use_container_width=True)

    except Exception as e:
        st.error(f"Error processing the sentiment data: {e}")
        st.info("Please check that the data file exists and contains the expected columns.")

    try:
        df = pd.read_csv('data/video_sentiment_summary.csv')

        summary = df.groupby("Content Creator").agg({
            "Positive Comments": "sum",
            "Negative Comments": "sum",
            "Neutral Comments": "sum",
            "Number of Topics": "sum",
            "Video ID": "count"  # Total number of videos
        }).rename(columns={
            "Video ID": "Total Videos",
            "Number of Topics": "Total Topics"
        }).reset_index()

        # Compute total comments
        summary["Total Comments"] = (
            summary["Positive Comments"] +
            summary["Negative Comments"] +
            summary["Neutral Comments"]
        )

        # Compute average topics per video
        summary["Avg Topics/Video"] = (summary["Total Topics"] / summary["Total Videos"]).round(2)

        # Calculate sentiment percentages
        summary["% Positive"] = (summary["Positive Comments"] / summary["Total Comments"] * 100).round(2)
        summary["% Negative"] = (summary["Negative Comments"] / summary["Total Comments"] * 100).round(2)
        summary["% Neutral"]  = (summary["Neutral Comments"] / summary["Total Comments"] * 100).round(2)

        # Reorder columns
        summary = summary[[
            "Content Creator", "Total Videos", "Total Topics", "Avg Topics/Video",
            "Positive Comments", "Negative Comments", "Neutral Comments",
            "Total Comments", "% Positive", "% Negative", "% Neutral"
        ]]

        st.subheader("Video Engagement and Topics Overview")
        
        # Display the summary table first
        st.dataframe(summary.style.highlight_max(axis=0, subset=['Total Videos', 'Total Comments', '% Positive']), 
                   use_container_width=True)

        # Chart 1: Total Videos per Creator
        st.subheader("Total Videos per Creator")
        fig_videos = px.bar(
            summary.sort_values("Total Videos", ascending=True),
            x="Total Videos",
            y="Content Creator",
            orientation="h",
            title="Total Number of Videos per Creator",
            text="Total Videos",  # Show count on bars
            color="Content Creator",
            labels={"Total Videos": "Number of Videos"}
        )

        # Optional layout polish
        fig_videos.update_layout(
            xaxis_title="Number of Videos",
            yaxis_title="Content Creator",
            bargap=0.3,
            showlegend=False
        )

        fig_videos.update_traces(textposition='outside')
        st.plotly_chart(fig_videos, use_container_width=True)

        st.subheader("Total Comments per Creator")
        try:
            df_comments = pd.read_csv("data/total_comments_roberta_and_vader..csv")
            
            # Rename columns for better clarity
            df_comments.columns = ["Content Creator", "Comment Count"]
            
            fig_comments = px.bar(
                df_comments.sort_values("Comment Count", ascending=False),
                x="Content Creator",
                y="Comment Count",
                color="Content Creator",
                title="Total Number of Comments per Creator",
                text="Comment Count"
            )
            
            fig_comments.update_layout(
                xaxis_title="Content Creator",
                yaxis_title="Number of Comments",
                xaxis_tickangle=-45,
                showlegend=False
            )
            
            fig_comments.update_traces(textposition='outside')
            st.plotly_chart(fig_comments, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading comments data: {e}")
            st.write("Error details:", str(e))
            
        # Chart 3: Sentiment Distribution per Creator
        st.subheader("Sentiment Distribution per Creator")
        
        # Prepare data for stacked bar chart
        sentiment_data = summary[["Content Creator", "Positive Comments", "Negative Comments", "Neutral Comments"]]
        sentiment_data_melted = pd.melt(
            sentiment_data, 
            id_vars=["Content Creator"],
            value_vars=["Positive Comments", "Negative Comments", "Neutral Comments"],
            var_name="Sentiment Type",
            value_name="Count"
        )
        
        # Create stacked bar chart
        fig_sentiment = px.bar(
            sentiment_data_melted,
            x="Content Creator",
            y="Count",
            color="Sentiment Type",
            title="Sentiment Distribution Across Content Creators",
            color_discrete_map={
                "Positive Comments": "green",
                "Neutral Comments": "gray",
                "Negative Comments": "red"
            }
        )
        
        fig_sentiment.update_layout(
            xaxis_title="Content Creator",
            yaxis_title="Number of Comments",
            xaxis_tickangle=-45,
            barmode="stack"
        )
        
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # Chart 4: Percentage Sentiment Distribution
        st.subheader("Percentage Sentiment Distribution")
        
        # Prepare percentage data
        percentage_data = summary[["Content Creator", "% Positive", "% Negative", "% Neutral"]]
        percentage_data_melted = pd.melt(
            percentage_data,
            id_vars=["Content Creator"],
            value_vars=["% Positive", "% Negative", "% Neutral"],
            var_name="Sentiment Type",
            value_name="Percentage"
        )
        
        # Create 100% stacked bar chart
        fig_percentage = px.bar(
            percentage_data_melted,
            x="Content Creator",
            y="Percentage",
            color="Sentiment Type",
            title="Percentage Sentiment Distribution by Content Creator",
            color_discrete_map={
                "% Positive": "green",
                "% Neutral": "gray",
                "% Negative": "red"
            }
        )
        
        fig_percentage.update_layout(
            xaxis_title="Content Creator",
            yaxis_title="Percentage of Comments",
            xaxis_tickangle=-45,
            barmode="stack"
        )
        
        st.plotly_chart(fig_percentage, use_container_width=True)
        
        # Chart 5: Topic Distribution
        st.subheader("Topic Distribution by Creator")
        
        # Create a chart for average topics per video
        fig_topics = px.bar(
            summary.sort_values("Avg Topics/Video", ascending=False),
            x="Content Creator",
            y="Avg Topics/Video",
            color="Content Creator",
            title="Average Number of Topics per Video",
            text="Avg Topics/Video"
        )
        
        fig_topics.update_layout(
            xaxis_title="Content Creator",
            yaxis_title="Average Topics per Video",
            xaxis_tickangle=-45,
            showlegend=False
        )
        
        fig_topics.update_traces(textposition='outside')
        st.plotly_chart(fig_topics, use_container_width=True)
        
        # Bonus: Engagement vs Topics scatterplot
        st.subheader("Engagement vs Topics Analysis")
        
        fig_scatter = px.scatter(
            summary,
            x="Total Comments",
            y="Total Topics",
            size="Total Videos",
            color="Content Creator",
            hover_name="Content Creator",
            text="Content Creator",
            title="Relationship Between Comments, Topics and Videos",
            labels={
                "Total Comments": "Total Number of Comments",
                "Total Topics": "Total Number of Topics",
                "Total Videos": "Number of Videos"
            }
        )
        
        fig_scatter.update_traces(
            textposition='top center',
            marker=dict(line=dict(width=1, color='DarkSlateGrey'))
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.subheader("Number of Comments Over Time by Content Creator")
        try:
            # 使用正确格式的时间序列数据文件
            comment_time_series = pd.read_csv("data/comment_time_series_roberta_and_vader..csv")
            
            # 将日期列转换为datetime类型
            comment_time_series['date'] = pd.to_datetime(comment_time_series['date'])
            
            # 将宽格式数据转换为长格式以便绘图
            # 除了date列外的所有列都是创作者
            creators = comment_time_series.columns[1:]
            
            # 使用melt函数转换数据格式
            melted_df = comment_time_series.melt(
                id_vars=['date'],
                value_vars=creators,
                var_name='channel',
                value_name='count'
            )
            
            # 使用Plotly创建交互式时间序列图
            fig = px.line(
                melted_df, 
                x="date", 
                y="count", 
                color="channel",
                title="Number of Comments Over Time by Content Creator",
                labels={"date": "Date", "count": "Number of Comments", "channel": "Content Creator"}
            )
            
            # 改进布局
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Comments",
                xaxis_tickangle=-45,
                legend_title="Content Creator",
                hovermode="x unified",
                height=500
            )
            
            # 添加范围滑块以便更好地导航日期
            fig.update_xaxes(rangeslider_visible=True)
            
            # 显示图表
            st.plotly_chart(fig, use_container_width=True)
            
            # 添加日期范围选择器，用于更详细的分析
            st.write("Select date range for more detailed analysis:")
            
            # 获取日期范围
            date_min = comment_time_series['date'].min()
            date_max = comment_time_series['date'].max()
            
            # 转换为日期对象，以便在date_input中使用
            date_min = pd.to_datetime(date_min).date()
            date_max = pd.to_datetime(date_max).date()
            
            selected_range = st.date_input(
                "Date range", 
                [date_min, date_max],
                min_value=date_min,
                max_value=date_max
            )
            
            if len(selected_range) == 2:
                # 将选定日期转换为datetime以便过滤
                start_date = pd.Timestamp(selected_range[0])
                end_date = pd.Timestamp(selected_range[1])
                
                # 过滤数据
                filtered_df = melted_df[
                    (melted_df['date'] >= start_date) & 
                    (melted_df['date'] <= end_date)
                ]
                
                # 创建过滤后的视图
                if not filtered_df.empty:
                    fig_filtered = px.line(
                        filtered_df, 
                        x="date", 
                        y="count", 
                        color="channel",
                        title=f"Comments from {selected_range[0]} to {selected_range[1]}",
                        labels={"date": "Date", "count": "Number of Comments", "channel": "Content Creator"}
                    )
                    
                    fig_filtered.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Number of Comments",
                        xaxis_tickangle=-45,
                        legend_title="Content Creator",
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig_filtered, use_container_width=True)
                else:
                    st.warning("No data available for the selected date range.")
            
            # 添加评论活跃度热图
            st.subheader("Comment Activity Heatmap")
            
            # 重新整理数据以创建热图 - 使用原始宽格式数据
            # 将日期设为索引以便更好地显示
            heatmap_data = comment_time_series.set_index('date')
            
            # 创建热图
            fig = px.imshow(
                heatmap_data.T,  # 转置以便创作者在y轴
                labels=dict(x="Date", y="Content Creator", color="Comment Count"),
                title="Comment Activity Heatmap",
                color_continuous_scale="YlOrRd"
            )
            
            # 调整布局
            fig.update_layout(height=500)
            
            # 显示热图
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading or processing time series data: {e}")
            st.write("Please check that the file 'data/comment_time_series_roberta_and_vader..csv' exists and contains the expected columns.")

    except Exception as e:
        st.error(f"Error processing video summary data: {e}")
        st.write("Please check that the data file exists at 'data/video_sentiment_summary.csv' and has the expected format.")
