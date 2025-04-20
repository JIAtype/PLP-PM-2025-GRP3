import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

def show_topics_as_aspects():

    st.header("Topics As Aspects")

    st.subheader("Overview")
    st.write("This section visualizes sentiment analysis across different content creators based on comments data.")

    st.subheader("Comment Sentiment Analysis")
    try:
        # First chart - Comment sentiment using Roberta and VADER
        df = pd.read_csv("data/comment_sentiment_roberta_and_vader.csv")
        st.write("Preview of the sentiment data:")
        st.dataframe(df)
        
        # Create a histogram of sentiment scores
        fig = px.histogram(df, x="sentiment_roberta", color="channel", 
                          title="Distribution of Sentiment Scores by Creator",
                          labels={"sentiment_roberta": "Sentiment Score", "count": "Number of Comments"},
                          opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)
        
        # Compare VADER vs RoBERTa sentiment scores
        if "vader_sentiment" in df.columns:
            fig = px.scatter(df, x="vader_sentiment", y="sentiment_roberta", color="channel",
                            title="VADER vs RoBERTa Sentiment Scores",
                            labels={"vader_sentiment": "VADER Sentiment", "sentiment_roberta": "RoBERTa Sentiment"},
                            opacity=0.6)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading or processing the first dataset: {e}")
    
    # Add sentiment analysis comparison across creators
    st.subheader("Sentiment Analysis Comparison")
    try:
        df_sentiment = pd.read_csv("data/comment_sentiment_roberta_FineTuning.csv")
        
        # 确认列名与您的数据集匹配
        sentiment_column = "sentiment_roberta"
        if sentiment_column not in df_sentiment.columns and "sentiment" in df_sentiment.columns:
            sentiment_column = "sentiment"
            
        sentiment_by_creator = df_sentiment.groupby("channel")[sentiment_column].agg(["mean", "std"]).reset_index()
        
        # Create a bar chart with error bars for sentiment comparison
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=sentiment_by_creator["channel"],
            y=sentiment_by_creator["mean"],
            error_y=dict(type="data", array=sentiment_by_creator["std"]),
            marker_color='indianred',
            name="Average Sentiment"
        ))
        fig.update_layout(
            title="Average Sentiment Score by Content Creator",
            xaxis_title="Content Creator",
            yaxis_title="Average Sentiment Score",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add a download button for the data
        st.subheader("Download Analysis Data")
        
        # 准备下载情感分析数据
        if 'df_sentiment' in locals():
            sentiment_csv = df_sentiment.to_csv(index=False)
            st.download_button(
                label="Download Sentiment Analysis Data",
                data=sentiment_csv,
                file_name="sentiment_analysis_data.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Error loading or processing sentiment comparison data: {e}")