import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

# Cache data loading operations to improve performance
@st.cache_data(ttl=3600)
def load_data(file_path):
    return pd.read_csv(file_path)

# Function to create downloadable link for dataframe
def get_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Function to create consistent heatmaps
def create_heatmap(data, title, x_label, y_label, annot=True, fmt=".1f", figsize=(12, 8), cmap="YlGnBu"):
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        data, 
        annot=annot, 
        cmap=cmap, 
        fmt=fmt, 
        cbar=True,
        linewidths=0.5,
        ax=ax
    )
    
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_xlabel(x_label, fontsize=12)
    plt.tight_layout()
    return fig

# Function to create more consistent bar charts with Plotly
def create_stacked_bar(data, x_col, y_cols, title, x_label, y_label, legend_title, color_map=None):
    fig = px.bar(
        data,
        x=x_col,
        y=y_cols,
        title=title,
        labels={"x": x_label, "y": y_label, "variable": legend_title},
        color_discrete_map=color_map or {"positive": "green", "neutral": "blue", "negative": "red"}
    )
    
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend_title=legend_title,
        barmode='stack',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # Improve hover information
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{y} comments<extra></extra>"
    )
    
    return fig

def show_tdidf_vader_sentiment_analysis():
    st.header("Video-Level Sentiment Analysis")
    
    # Add progress indicator for initial data loading
    with st.spinner('Loading sentiment data...'):
        # Load all necessary datasets at the beginning
        sentiment_counts_vader = load_data('data/TD_IDF_sentiment_counts_vader.csv')
        sentiment_counts_vader = sentiment_counts_vader.set_index('channel').astype(int).transpose()

        comments_per_creator_sentiment = load_data("data/TD_IDF_comments_per_creator_sentiment_vader.csv")
        topic_sentiment_df = load_data('data/TD_IDF_sentiment_df_vader.csv')
        topic_sentiment_matrix = load_data("data/TD_IDF_aspect_sentiment_per_creator_vader_new.csv")
        topic_sentiment_matrix_indexed = topic_sentiment_matrix.set_index('topic')
        topic_sentiment_matrix_transposed = topic_sentiment_matrix_indexed.T

        grouped = load_data('data/TD_IDF_aspect_sentiment_per_creator_vader.csv')
        positive_comment_time_series = load_data("data/TD_IDF_positive_comment_time_series_vader.csv")
        date_col = positive_comment_time_series.columns[0]
        if 'date' in positive_comment_time_series.columns:
            date_col = 'date'
            
        positive_comment_time_series[date_col] = pd.to_datetime(positive_comment_time_series[date_col])
        positive_comment_time_series = positive_comment_time_series.set_index(date_col)
        
        creator_aspect_sentiment = load_data("data/TD_IDF_aspect_sentiment_matrix_vader.csv")
        creator_aspect_sentiment = creator_aspect_sentiment.T
        
        aspect_video_df = load_data("data/TD_IDF_aspect_sentiment_matrix_creators_vader.csv")
        # comment_sentiment = load_data("data/comment_sentiment_roberta_and_vader.csv")
    
    # Add tabs for better organization
    tabs = st.tabs(["Overview", "By Creator", "By Topic", "Time Series", "Aspect-Based"])
    
    # Consistent color scheme for sentiment across all visualizations
    sentiment_colors = {"positive": "#2ca02c", "neutral": "#1f77b4", "negative": "#d62728"}
    
    with tabs[0]:  # Overview tab
        st.subheader("Overall Sentiment Distribution per Creator")
        
        # Toggle between absolute values and percentages
        view_option = st.radio(
            "Select View:",
            ('Absolute Numbers', 'Percentages'),
            horizontal=True
        )
        
        # Calculate percentages
        percentage_data = sentiment_counts_vader.copy()
        for col in percentage_data.columns:
            percentage_data[col] = (percentage_data[col] / percentage_data[col].sum() * 100).round(1)
        
        if view_option == 'Absolute Numbers':
            fig = create_heatmap(
                sentiment_counts_vader,
                'Overall Sentiment Distribution per Creator',
                'Sentiment',
                'Creator',
                fmt="d"
            )
            st.pyplot(fig)
            
            # Add download button for the data
            st.markdown(
                get_download_link(
                    sentiment_counts_vader.reset_index(),
                    "sentiment_counts_absolute.csv",
                    "📥 Download this data as CSV"
                ),
                unsafe_allow_html=True
            )
        else:
            fig = create_heatmap(
                percentage_data,
                'Sentiment Distribution per Creator (Percentage %)',
                'Sentiment',
                'Creator'
            )
            st.pyplot(fig)
            
            # Add download button for the percentage data
            st.markdown(
                get_download_link(
                    percentage_data.reset_index(),
                    "sentiment_counts_percentage.csv",
                    "📥 Download this data as CSV"
                ),
                unsafe_allow_html=True
            )
        
        # Show stacked bar chart for sentiment distribution
        st.subheader("Sentiment Distribution by Content Creator")
        
        fig = create_stacked_bar(
            comments_per_creator_sentiment,
            comments_per_creator_sentiment.index,
            comments_per_creator_sentiment.columns,
            "Sentiment Distribution by Content Creator",
            "Content Creator",
            "Number of Comments",
            "Sentiment",
            sentiment_colors
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add analytical insights
        with st.expander("Key Insights", expanded=True):
            st.write("""
            From the data, we can observe that:
            - Fully Charged Show and Now You Know have the most positive comments overall
            - Most creators have a higher proportion of positive comments than neutral and negative ones
            - Bjorn Nyland has a relatively small number of total comments, but a higher proportion of positive comments
            """)
        
    with tabs[1]:  # By Creator tab
        st.subheader("Creator-Specific Sentiment Analysis")
        
        # Select creator for detailed analysis
        selected_creator = st.selectbox(
            'Select a creator to view detailed sentiment distribution',
            sentiment_counts_vader.index.tolist()
        )
        
        if selected_creator:
            col1, col2 = st.columns(2)
            
            with col1:
                # Create pie chart for selected creator
                fig = px.pie(
                    values=sentiment_counts_vader.loc[selected_creator],
                    names=sentiment_counts_vader.columns,
                    title=f'{selected_creator} Sentiment Distribution',
                    color_discrete_map=sentiment_colors
                )
                # Improve hover information
                fig.update_traces(
                    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Create radar chart for sentiment comparison
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=sentiment_counts_vader.loc[selected_creator].values,
                    theta=sentiment_counts_vader.columns,
                    fill='toself',
                    name=selected_creator,
                    line=dict(color=sentiment_colors["positive"])
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                        )
                    ),
                    showlegend=True,
                    title=f"{selected_creator} Sentiment Distribution"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Add comparison with overall average
            st.subheader(f"Comparing {selected_creator} with Average")
            
            # Calculate average sentiment across all creators
            average_sentiment = sentiment_counts_vader.mean()
            
            # Create comparison dataframe
            comparison_df = pd.DataFrame({
                'Sentiment': sentiment_counts_vader.columns,
                f'{selected_creator}': sentiment_counts_vader.loc[selected_creator].values,
                'Average': average_sentiment.values
            })
            
            # Create comparison bar chart
            fig = px.bar(
                comparison_df,
                x='Sentiment',
                y=[f'{selected_creator}', 'Average'],
                barmode='group',
                title=f"Sentiment Comparison: {selected_creator} vs. Average",
                color_discrete_sequence=[sentiment_colors["positive"], "#9467bd"]
            )
            
            fig.update_layout(
                xaxis_title="Sentiment",
                yaxis_title="Count",
                legend_title="",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:  # By Topic tab
        st.subheader("Topic-Based Sentiment Analysis")
        
        # Create table for positive sentiment percentage per topic
        st.subheader("Positive Sentiment Percentage Per Topic")
        
        # Add a search box for topics
        topic_search = st.text_input("Search for specific topics:")
        
        # Filter the dataframe based on search
        if topic_search:
            filtered_topic_df = topic_sentiment_df[topic_sentiment_df.iloc[:, 0].str.contains(topic_search, case=False)]
        else:
            filtered_topic_df = topic_sentiment_df
        
        # Add pagination for better readability
        page_size = st.slider("Rows per page:", min_value=5, max_value=20, value=10, step=5)
        total_pages = max(1, len(filtered_topic_df) // page_size + (1 if len(filtered_topic_df) % page_size > 0 else 0))
        page_number = st.number_input("Page:", min_value=1, max_value=total_pages, value=1, step=1)
        
        # Calculate start and end indices
        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_topic_df))
        
        # Display the current page of data
        current_page_df = filtered_topic_df.iloc[start_idx:end_idx]
        
        # Create matplotlib table
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.axis("tight")
        ax.axis("off")
        
        table = ax.table(
            cellText=current_page_df.values, 
            colLabels=current_page_df.columns, 
            cellLoc="center", 
            loc="center"
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width([i for i in range(len(current_page_df.columns))])
        
        # Style the header row
        for key, cell in table.get_celld().items():
            if key[0] == 0:  # Header row
                cell.set_text_props(weight="bold", color="white")
                cell.set_facecolor("#2E74B5")  # Blue header
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Add download button for the topic sentiment data
        st.markdown(
            get_download_link(
                topic_sentiment_df,
                "topic_sentiment_summary.csv",
                "📥 Download complete topic sentiment data as CSV"
            ),
            unsafe_allow_html=True
        )
        
        # Topic-sentiment matrix heatmap with improved interactivity
        st.subheader("Topic-Based Sentiment Comparison")
        
        # Add zoom controls explanation
        st.info("👆 Tip: Click and drag on the heatmap to zoom in. Double-click to reset the view.")
        
        fig = px.imshow(
            topic_sentiment_matrix_transposed,
            labels=dict(x="Topic", y="Creator", color="Sentiment Score"),
            x=topic_sentiment_matrix_transposed.columns,
            y=topic_sentiment_matrix_transposed.index,
            color_continuous_scale="RdYlGn",
            aspect="auto",
            text_auto=True
        )

        fig.update_layout(
            title="Top 10 Topic-Based Sentiment Comparison per Creator",
            xaxis_title="Topic",
            yaxis_title="Creator",
            height=600
        )
        
        # Improve hover information
        fig.update_traces(
            hovertemplate="<b>Creator:</b> %{y}<br><b>Topic:</b> %{x}<br><b>Sentiment Score:</b> %{z:.2f}<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # Topic sentiment per creator analysis
        st.subheader("Sentiment Distribution per Topic per Creator")
        
        st.subheader("Emotional distribution by creator and topic")
        
        # Create selectors
        col1, col2 = st.columns(2)
        
        with col1:
            selected_channel = st.selectbox(
                "Select Creator:",
                options=grouped["channel"].unique()
            )
        
        with col2:
            view_option = st.radio(
                "Select the data display method:",
                ["Absolute number", "Percentage"],
                horizontal=True
            )
        
        # Filter data
        subset = grouped[grouped["channel"] == selected_channel].set_index("topics")[["Positive", "Negative", "Neutral"]]
        
        if view_option == "Percentage":
            # Calculate percentages
            subset_pct = subset.div(subset.sum(axis=1), axis=0) * 100
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(subset_pct.T, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax)
            plt.title(f"{selected_channel} - Topic sentiment distribution (%)")
            plt.ylabel("Sentiment")
            plt.xlabel("Topic")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Add bar chart for better comparison
            st.write("Topic sentiment distribution bar chart:")
            
            # Use Plotly to create bar chart
            chart_data = subset_pct.reset_index().melt(id_vars='topics', var_name='Sentiment', value_name='Percentage')
            
            fig = px.bar(
                chart_data,
                x='topics',
                y='Percentage',
                color='Sentiment',
                title=f"{selected_channel} - Topic sentiment distribution (%)",
                labels={'topics': 'Topic', 'Percentage': 'Percentage'},
                color_discrete_map=sentiment_colors
            )
            
            # Improve hover information
            fig.update_traces(
                hovertemplate="<b>Topic:</b> %{x}<br><b>%{data.name}:</b> %{y:.1f}%<extra></extra>"
            )
            
            # Adjust layout
            fig.update_layout(
                xaxis_tickangle=-45,
                legend_title_text='Sentiment',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Absolute count heatmap
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(subset.T, annot=True, fmt="d", cmap="YlGnBu", ax=ax)
            plt.title(f"{selected_channel} - Topic sentiment distribution (absolute number)")
            plt.ylabel("Sentiment")
            plt.xlabel("Topic")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Add bar chart
            st.write("Topic sentiment distribution bar chart:")
            
            chart_data = subset.reset_index().melt(id_vars='topics', var_name='Sentiment', value_name='Count')
            
            fig = px.bar(
                chart_data,
                x='topics',
                y='Count',
                color='Sentiment',
                title=f"{selected_channel} - Topic sentiment distribution (absolute number)",
                labels={'topics': 'Topic', 'Count': 'Number of comments'},
                color_discrete_map=sentiment_colors
            )
            
            # Improve hover information
            fig.update_traces(
                hovertemplate="<b>Topic:</b> %{x}<br><b>%{data.name}:</b> %{y}<extra></extra>"
            )
            
            # Adjust layout
            fig.update_layout(
                xaxis_tickangle=-45,
                legend_title_text='Sentiment',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add download button for the topic data
            st.markdown(
                get_download_link(
                    subset.reset_index(),
                    f"{selected_channel}_topic_sentiment.csv",
                    "📥 Download this data as CSV"
                ),
                unsafe_allow_html=True
            )

    with tabs[3]:  # Time Series tab
        st.subheader("Sentiment Over Time")
        
        # Add date range selector
        date_min = positive_comment_time_series.index.min().date()
        date_max = positive_comment_time_series.index.max().date()
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start date", date_min, min_value=date_min, max_value=date_max)
        
        with col2:
            end_date = st.date_input("End date", date_max, min_value=date_min, max_value=date_max)
        
        # Filter by date range
        filtered_time_series = positive_comment_time_series.loc[start_date:end_date]
        
        # Add aggregation options
        aggregation = st.radio(
            "Aggregate by:",
            ("Daily", "Weekly", "Monthly"),
            horizontal=True
        )
        
        # Aggregate data based on selection
        if aggregation == "Weekly":
            aggregated_data = filtered_time_series.resample('W').mean()
            time_format = "%b %d, %Y"
        elif aggregation == "Monthly":
            aggregated_data = filtered_time_series.resample('M').mean()
            time_format = "%b %Y"
        else:  # Daily
            aggregated_data = filtered_time_series
            time_format = "%b %d, %Y"
        
        # Create time series plot
        fig = px.line(
            aggregated_data,
            y=aggregated_data.columns,
            title=f"Time Series of Positive Comments per Creator ({aggregation})",
            labels={"value": "Number of Positive Comments", "variable": "Creator"},
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Positive Comments",
            legend_title="Creator",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            )
        )
        
        # Improve hover information
        fig.update_traces(
            hovertemplate="<b>Date:</b> %{x|" + time_format + "}<br><b>%{data.name}:</b> %{y:.1f}<extra></extra>"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Allow user to select specific creators
        st.subheader("Compare specific creators")
        selected_creators = st.multiselect(
            "Select creators to display:",
            aggregated_data.columns,
            default=aggregated_data.columns[:3]  # Default to first three
        )
        
        if selected_creators:
            # Create filtered time series plot
            fig = px.line(
                aggregated_data[selected_creators],
                y=selected_creators,
                title=f"Time Series of Positive Comments for Selected Creators ({aggregation})",
                labels={"value": "Number of Positive Comments", "variable": "Creator"}
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Positive Comments",
                legend_title="Creator",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial"
                )
            )
            
            # Improve hover information
            fig.update_traces(
                hovertemplate="<b>Date:</b> %{x|" + time_format + "}<br><b>%{data.name}:</b> %{y:.1f}<extra></extra>"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add anomaly detection
            if st.checkbox("Show anomalies (values outside of 2 standard deviations)"):
                st.info("Anomalies are data points that are significantly different from the average trend.")
                
                for creator in selected_creators:
                    # Calculate rolling mean and standard deviation
                    rolling_mean = aggregated_data[creator].rolling(window=5).mean()
                    rolling_std = aggregated_data[creator].rolling(window=5).std()
                    
                    # Identify anomalies (outside 2 standard deviations)
                    upper_bound = rolling_mean + 2 * rolling_std
                    lower_bound = rolling_mean - 2 * rolling_std
                    
                    anomalies = aggregated_data[creator][(aggregated_data[creator] > upper_bound) | 
                                                      (aggregated_data[creator] < lower_bound)]
                    
                    if not anomalies.empty:
                        # Create anomaly plot
                        fig = go.Figure()
                        
                        # Add main time series
                        fig.add_trace(go.Scatter(
                            x=aggregated_data.index,
                            y=aggregated_data[creator],
                            mode='lines',
                            name=creator,
                            line=dict(color='blue')
                        ))
                        
                        # Add upper and lower bounds
                        fig.add_trace(go.Scatter(
                            x=upper_bound.index,
                            y=upper_bound,
                            mode='lines',
                            name='Upper Bound (2σ)',
                            line=dict(color='rgba(255,0,0,0.3)')
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=lower_bound.index,
                            y=lower_bound,
                            mode='lines',
                            name='Lower Bound (2σ)',
                            line=dict(color='rgba(255,0,0,0.3)')
                        ))
                        
                        # Add anomalies as points
                        fig.add_trace(go.Scatter(
                            x=anomalies.index,
                            y=anomalies.values,
                            mode='markers',
                            name='Anomalies',
                            marker=dict(color='red', size=8)
                        ))
                        
                        fig.update_layout(
                            title=f"Anomaly Detection for {creator}",
                            xaxis_title="Date",
                            yaxis_title="Number of Positive Comments",
                            hoverlabel=dict(
                                bgcolor="white",
                                font_size=12,
                                font_family="Arial"
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.write(f"No anomalies detected for {creator} in the selected time range.")
    
    with tabs[4]:  # Aspect-Based tab
        st.subheader("Aspect-Based Sentiment Analysis")
        
        # Compare aspects across creators
        st.subheader("Cross-Creator Aspect Sentiment Comparison")
        
        # Add explanation
        st.info("""
        This heatmap shows how different creators' content performs on various aspects. 
        Greener cells indicate more positive sentiment, while redder cells indicate more negative sentiment.
        """)
        
        fig = px.imshow(
            creator_aspect_sentiment,
            labels=dict(x="Aspect", y="Creator", color="Sentiment Score"),
            color_continuous_scale="RdYlGn",
            aspect="auto"
        )
        
        fig.update_layout(
            title="Aspect-Based Sentiment Comparison across Creators",
            xaxis_title="Aspect",
            yaxis_title="Creator",
            height=600,
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            )
        )
        
        # Improve hover information
        fig.update_traces(
            hovertemplate="<b>Creator:</b> %{y}<br><b>Aspect:</b> %{x}<br><b>Sentiment Score:</b> %{z:.2f}<extra></extra>"
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Creator-specific aspect analysis
        st.subheader("Creator-Specific Aspect Analysis")
        
        # Creator selection for aspect-based analysis
        selected_creator = st.selectbox(
            "Select creator:",
            aspect_video_df["channel"].unique()
        )

        # Video search functionality
        video_search = st.text_input("Search for specific video ID (optional):")
        
        # Filter the dataframe based on creator and search
        creator_data = aspect_video_df[aspect_video_df["channel"] == selected_creator]
        if video_search:
            creator_data = creator_data[creator_data["video"].str.contains(video_search, case=False)]
        
        # Create pivot table
        aspects = aspect_video_df.columns[2:]
        pivot_data = pd.pivot_table(
            creator_data, 
            index="video", 
            values=aspects,
            aggfunc='first'
        )
        
        if not pivot_data.empty:
            st.subheader(f"Aspect-Based Sentiment for {selected_creator} Videos")
            
            fig = px.imshow(
                pivot_data,
                labels=dict(x="Aspect", y="Video", color="Score"),
                color_continuous_scale="RdYlGn",
                aspect="auto",
                height=max(400, min(800, 100 + 30 * len(pivot_data)))  # Dynamic height based on number of videos
            )
            
            fig.update_layout(
                xaxis_title="Aspect",
                yaxis_title="Video ID",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial"
                )
            )
            
            # Improve hover information
            fig.update_traces(
                hovertemplate="<b>Video:</b> %{y}<br><b>Aspect:</b> %{x}<br><b>Sentiment Score:</b> %{z:.2f}<extra></extra>"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add download option for this data
            st.markdown(
                get_download_link(
                    pivot_data.reset_index(),
                    f"{selected_creator}_aspect_sentiment.csv",
                    "📥 Download aspect sentiment data as CSV"
                ),
                unsafe_allow_html=True
            )
        else:
            st.warning("No data available for the selected creator or search criteria.")
        
        # Show most positive and most negative aspects for selected creator
        if not creator_data.empty:
            st.subheader(f"Most Positive and Negative Aspects for {selected_creator}")
            
            # Calculate average sentiment per aspect
            aspect_avg = creator_data[aspects].mean()
            
            # Sort and get top and bottom aspects
            top_aspects = aspect_avg.sort_values(ascending=False).head(5)
            bottom_aspects = aspect_avg.sort_values().head(5)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Most Positive Aspects")
                fig = px.bar(
                    x=top_aspects.index,
                    y=top_aspects.values,
                    labels={'x': 'Aspect', 'y': 'Sentiment Score'},
                    color=top_aspects.values,
                    color_continuous_scale='Greens',
                    title=f"Top 5 Positive Aspects for {selected_creator}"
                )
                
                fig.update_layout(
                    xaxis_tickangle=-45,
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Arial"
                    )
                )
                
                # Improve hover information
                fig.update_traces(
                    hovertemplate="<b>Aspect:</b> %{x}<br><b>Sentiment Score:</b> %{y:.2f}<extra></extra>"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("Most Negative Aspects")
                fig = px.bar(
                    x=bottom_aspects.index,
                    y=bottom_aspects.values,
                    labels={'x': 'Aspect', 'y': 'Sentiment Score'},
                    color=bottom_aspects.values,
                    color_continuous_scale='Reds_r',
                    title=f"Top 5 Negative Aspects for {selected_creator}"
                )
                
                fig.update_layout(
                    xaxis_tickangle=-45,
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Arial"
                    )
                )
                
                # Improve hover information
                fig.update_traces(
                    hovertemplate="<b>Aspect:</b> %{x}<br><b>Sentiment Score:</b> %{y:.2f}<extra></extra>"
                )
                
                st.plotly_chart(fig, use_container_width=True)

            st.subheader(f"Aspect-Based Sentiment for {selected_creator}")
            if not creator_data.empty:
                df = pd.read_csv("data/comment_sentiment_roberta_and_vader.csv")
                creator_df = df[df["channel"] == selected_creator].explode("topics")
                aspect_video_sentiment = creator_df.groupby(["video_id", "topics", "sentiment_vader"]).size().unstack(fill_value=0)
                fig, ax = plt.subplots(figsize=(15, 8))
                sns.heatmap(aspect_video_sentiment, cmap="coolwarm", annot=False, fmt="d")
                plt.title(f"Aspect-Based Sentiment for {selected_creator} Across Videos")
                plt.xlabel("Sentiment")
                plt.ylabel("Video ID - Topic")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)