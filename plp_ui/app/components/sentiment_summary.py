import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt

def show_sentiment_summary():
    st.header("Video-Level Summary")
    
    try:
        df = pd.read_csv('data/video_sentiment_summary.csv')
        
        summary = df.groupby("Content Creator").agg({
            "Positive Comments": "sum",
            "Negative Comments": "sum",
            "Neutral Comments": "sum",
            "Number of Topics": "sum",
            "Video ID": "count"  # Total videos
        }).rename(columns={
            "Video ID": "Total Videos",
            "Number of Topics": "Total Topics"
        }).reset_index()

        # Calculate total comments
        summary["Total Comments"] = (
            summary["Positive Comments"] +
            summary["Negative Comments"] +
            summary["Neutral Comments"]
        )

        # Calculate average topics per video
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

        # Display data summary table
        st.subheader("Overview")
        st.dataframe(summary.style.background_gradient(subset=["% Positive", "% Negative", "% Neutral"], cmap="Blues")
                    .format({"% Positive": "{:.2f}%", "% Negative": "{:.2f}%", "% Neutral": "{:.2f}%"}),
                    use_container_width=True)

        # Create column layout for side-by-side charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Content creator positive sentiment ranking")
            # Create interactive bar chart with Altair
            chart = alt.Chart(summary).mark_bar().encode(
                x=alt.X('% Positive:Q', title='Percentage of Positive Reviews(%)'),
                y=alt.Y('Content Creator:N', sort='-x', title='Content Creator'),
                color=alt.Color('% Positive:Q', scale=alt.Scale(scheme='blues'), legend=None),
                tooltip=['Content Creator', '% Positive', 'Total Comments']
            ).properties(
                height=300
            ).interactive()
            st.altair_chart(chart, use_container_width=True)

        with col2:
            st.subheader("Average Positive Sentiment per Content Creator")
            # Create bar chart with Pyplot
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(data=summary.sort_values("% Positive", ascending=False),
                        x="Content Creator", y="% Positive", palette="Blues_d", ax=ax)
            plt.title("Average Positive Sentiment per Content Creator")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)

        # Sentiment stacked bar chart
        st.subheader("Sentiment Breakdown per Content Creator")
        
        # Create stacked bar chart
        fig = px.bar(
            summary,
            x="Content Creator",
            y=["Positive Comments", "Negative Comments", "Neutral Comments"],
            title="Sentiment Breakdown per Content Creator",
            labels={"value": "Number of Comments", "variable": "Sentiment"},
            barmode="stack",
            color_discrete_sequence=["#2ca02c", "#d62728", "#1f77b4"]  # Custom colors for positive, negative, neutral
        )
        
        fig.update_layout(
            xaxis_title="Content Creator",
            yaxis_title="Number of Comments",
            legend_title="Sentiment",
            bargap=0.15,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add sentiment distribution radar chart
        st.subheader("Sentiment distribution radar chart")
        
        # Prepare radar chart data
        fig = go.Figure()
        
        for creator in summary["Content Creator"]:
            creator_data = summary[summary["Content Creator"] == creator]
            fig.add_trace(go.Scatterpolar(
                r=[
                    creator_data["% Positive"].iloc[0],
                    creator_data["% Negative"].iloc[0],
                    creator_data["% Neutral"].iloc[0]
                ],
                theta=["Positive", "Negative", "Neutral"],
                fill='toself',
                name=creator
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                )
            ),
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add sentiment percentage comparison
        st.subheader("Sentiment Percentage Comparison")
        
        # Melt the summary DataFrame to long format for sentiment percentages
        melted = summary.melt(
            id_vars="Content Creator",
            value_vars=["% Positive", "% Negative", "% Neutral"],
            var_name="Sentiment",
            value_name="Percentage"
        )
        
        # Create grouped bar chart
        fig = px.bar(
            melted,
            x="Content Creator",
            y="Percentage",
            color="Sentiment",
            barmode="group",
            title="Sentiment Percentage Comparison per Creator",
            labels={"Percentage": "Sentiment (%)"},
            color_discrete_map={
                "% Positive": "#2ca02c", 
                "% Negative": "#d62728", 
                "% Neutral": "#1f77b4"
            }
        )
        
        # Enhance layout
        fig.update_layout(
            yaxis=dict(range=[0, 100]),
            xaxis_title="Content Creator",
            yaxis_title="Percentage",
            legend_title="Sentiment Type",
            bargap=0.2,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add pie charts for each creator
        st.subheader("Sentiment Distribution by Creator")
        
        # List of content creators
        creators = summary["Content Creator"].tolist()
        
        # Ensure only up to 3 creators per row
        n_creators = len(creators)
        n_rows = (n_creators + 2) // 3  # Calculate number of needed rows
        
        # Create multiple rows of charts if needed
        for row_idx in range(n_rows):
            cols = st.columns(3)  # Create 3 columns per row
            
            for col_idx in range(3):
                creator_idx = row_idx * 3 + col_idx
                
                if creator_idx < n_creators:
                    creator_name = creators[creator_idx]
                    row_data = summary[summary["Content Creator"] == creator_name].iloc[0]
                    
                    with cols[col_idx]:
                        st.write(f"**{creator_name}**")
                        fig = go.Figure(
                            go.Pie(
                                labels=["Positive", "Negative", "Neutral"],
                                values=[
                                    row_data["Positive Comments"],
                                    row_data["Negative Comments"],
                                    row_data["Neutral Comments"]
                                ],
                                textinfo='percent',
                                hole=0.4,  # Make it a donut chart
                                marker=dict(colors=["#2ca02c", "#d62728", "#1f77b4"])
                            )
                        )
                        
                        fig.update_layout(
                            height=250,
                            margin=dict(t=20, b=0, l=0, r=0)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
        
        # Add download functionality for data
        st.subheader("Download Analysis Data")
        csv = summary.to_csv(index=False)
        st.download_button(
            label="Download Summary Data as CSV",
            data=csv,
            file_name='video_sentiment_summary.csv',
            mime='text/csv',
        )
        
    except Exception as e:
        st.error(f"Error processing data: {e}")
        st.write("Please check that the file 'data/video_sentiment_summary.csv' exists and has the expected format.")