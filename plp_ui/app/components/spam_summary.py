import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import numpy as np
from datetime import datetime

def show_spam_summary(selected_creator=None):
    """
    Visualize spam analysis for YouTube comments data
    
    Parameters:
    -----------
    selected_creator : str, optional
        If provided, analysis will focus on this specific content creator
    """
    st.title("YouTube Comments Spam Analysis")
    
    # Load data
    try:
        df = pd.read_csv('data/comments_analysis_v4.csv')
        # Convert timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Basic data cleaning
    df['is_spam'] = df['Prediction'] == 'SPAM COMMENT'
    
    # Display basic stats
    total_comments = len(df)
    spam_count = df['is_spam'].sum()
    spam_percentage = (spam_count / total_comments) * 100 if total_comments > 0 else 0
    
    # Filter by creator if specified
    if selected_creator:
        df_filtered = df[df['Content Creator'] == selected_creator]
        if len(df_filtered) == 0:
            st.warning(f"No data found for creator: {selected_creator}")
            return
        st.header(f"Analysis for: {selected_creator}")
    else:
        df_filtered = df
        st.header("Overall Analysis")
    
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Comments", len(df_filtered))
    
    with col2:
        creator_spam_count = df_filtered['is_spam'].sum()
        st.metric("Spam Comments", creator_spam_count)
    
    with col3:
        creator_spam_percentage = (creator_spam_count / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
        st.metric("Spam Percentage", f"{creator_spam_percentage:.1f}%")
    
    # Visualizations section
    st.subheader("Visualizations")
    
    # Tab layout for different visualizations
    tab1, tab2, tab3 = st.tabs(["Spam Distribution", "Time Analysis", "Comment Samples"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of spam vs non-spam
            fig, ax = plt.subplots(figsize=(8, 6))
            labels = ['Spam', 'Not Spam']
            sizes = [
                df_filtered['is_spam'].sum(),
                len(df_filtered) - df_filtered['is_spam'].sum()
            ]
            colors = ['#ff9999', '#66b3ff']
            explode = (0.1, 0)
            
            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', shadow=True, startangle=90)
            ax.axis('equal')
            plt.title('Spam vs. Non-Spam Comments')
            st.pyplot(fig)
        
        with col2:
            if not selected_creator:
                # Bar chart showing spam percentage by creator
                creator_spam = df.groupby('Content Creator')['is_spam'].agg(['sum', 'count'])
                creator_spam['percentage'] = creator_spam['sum'] / creator_spam['count'] * 100
                
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=creator_spam.index, y=creator_spam['percentage'], palette='viridis', ax=ax)
                plt.xticks(rotation=45, ha='right')
                plt.title('Spam Percentage by Content Creator')
                plt.ylabel('Spam Percentage (%)')
                plt.xlabel('Content Creator')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                # For selected creator, show video-wise spam distribution if available
                if 'Video ID' in df_filtered.columns and df_filtered['Video ID'].nunique() > 1:
                    video_spam = df_filtered.groupby('Video ID')['is_spam'].agg(['sum', 'count'])
                    video_spam['percentage'] = video_spam['sum'] / video_spam['count'] * 100
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.barplot(x=video_spam.index, y=video_spam['percentage'], palette='viridis', ax=ax)
                    plt.xticks(rotation=90)
                    plt.title('Spam Percentage by Video')
                    plt.ylabel('Spam Percentage (%)')
                    plt.xlabel('Video ID')
                    plt.tight_layout()
                    st.pyplot(fig)

                    # Additional analysis section
                    st.subheader("Additional Analysis")
                    
                    # Comment length analysis
                    df_filtered['comment_length'] = df_filtered['Comment'].str.len()
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.histplot(data=df_filtered, x='comment_length', hue='is_spam', 
                                multiple='stack', bins=30, palette=['blue', 'red'])
                    plt.title('Comment Length Distribution')
                    plt.xlabel('Comment Length (characters)')
                    plt.ylabel('Count')
                    plt.legend(['Not Spam', 'Spam'])
                    st.pyplot(fig)
                    
                    # Average comment length comparison
                    avg_length_spam = df_filtered[df_filtered['is_spam']]['comment_length'].mean()
                    avg_length_nonspam = df_filtered[~df_filtered['is_spam']]['comment_length'].mean()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Avg. Spam Comment Length", f"{avg_length_spam:.1f} chars")
                    with col2:
                        st.metric("Avg. Non-Spam Comment Length", f"{avg_length_nonspam:.1f} chars")
                    
                    # Special characters and emojis
                    if not selected_creator:
                        st.subheader("Creator Comparison")
                        
                        # Create a list of content creators
                        creators = df['Content Creator'].unique()
                        
                        # Create a selection box for the user to select a specific creator
                        st.write("Select a creator to view detailed analysis:")
                        creator_selector = st.selectbox("Creator", [""] + list(creators))
                        
                        if creator_selector:
                            st.write(f"Go to individual analysis for {creator_selector}")
                            if st.button("View Details"):
                                # Redirect to the specific creator analysis
                                st.session_state['selected_creator'] = creator_selector
                                st.experimental_rerun()
                else:
                    st.info("Not enough video data to visualize")

    
    with tab2:
        # Time series analysis if timestamp data is available
        if 'Timestamp' in df_filtered.columns and df_filtered['Timestamp'].notna().any():
            df_filtered['year_month'] = df_filtered['Timestamp'].dt.strftime('%Y-%m')
            
            # Group by year-month and calculate spam percentage
            time_analysis = df_filtered.groupby('year_month')['is_spam'].agg(['sum', 'count']).reset_index()
            time_analysis['percentage'] = time_analysis['sum'] / time_analysis['count'] * 100
            
            # Plot the time series
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(time_analysis['year_month'], time_analysis['percentage'], marker='o', linestyle='-')
            ax.set_xlabel('Time Period')
            ax.set_ylabel('Spam Percentage (%)')
            ax.set_title('Spam Comment Trend Over Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            
            # Additional visualization: Volume of comments over time
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(time_analysis['year_month'], time_analysis['count'], color='skyblue')
            ax.set_xlabel('Time Period')
            ax.set_ylabel('Number of Comments')
            ax.set_title('Comment Volume Over Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("Timestamp data not available for time series analysis")
    
    with tab3:
        # Sample comments
        st.subheader("Comment Samples")
        
        # Button to show random spam comments
        if st.button("Show Random Spam Comments"):
            spam_comments = df_filtered[df_filtered['is_spam'] == True]
            
            if len(spam_comments) > 0:
                sample_size = min(10, len(spam_comments))
                sampled_comments = spam_comments.sample(sample_size)
                
                for i, (idx, row) in enumerate(sampled_comments.iterrows()):
                    with st.expander(f"Spam Comment #{i+1} - {row['Content Creator']}"):
                        st.write(f"**Comment:** {row['Comment']}")
                        if pd.notna(row['Timestamp']):
                            st.write(f"**Date:** {row['Timestamp'].strftime('%Y-%m-%d')}")
                        if pd.notna(row['Video Title']):
                            st.write(f"**Video:** {row['Video Title']}")
            else:
                st.info("No spam comments found")
        
        # Button to show random non-spam comments for comparison
        if st.button("Show Random Non-Spam Comments"):
            nonspam_comments = df_filtered[df_filtered['is_spam'] == False]
            
            if len(nonspam_comments) > 0:
                sample_size = min(10, len(nonspam_comments))
                sampled_comments = nonspam_comments.sample(sample_size)
                
                for i, (idx, row) in enumerate(sampled_comments.iterrows()):
                    with st.expander(f"Non-Spam Comment #{i+1} - {row['Content Creator']}"):
                        st.write(f"**Comment:** {row['Comment']}")
                        if pd.notna(row['Timestamp']):
                            st.write(f"**Date:** {row['Timestamp'].strftime('%Y-%m-%d')}")
                        if pd.notna(row['Video Title']):
                            st.write(f"**Video:** {row['Video Title']}")
            else:
                st.info("No non-spam comments found")
    