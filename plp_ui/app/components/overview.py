import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import json
from collections import defaultdict

def show_overview_analysis(selected_creator):
    st.header("Overview")
    try:
        with open('data/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = defaultdict(lambda: {"playlist_count": 0, "playlists": {}})

        # Walk through the JSON structure
        for creator, playlists in data.items():
            summary[creator]["playlist_count"] = len(playlists)
            for playlist_id, videos in playlists.items():
                summary[creator]["playlists"][playlist_id] = {
                    "video_count": len(videos),
                    "videos": {}
                }
                for video_id, video_data in videos.items():
                    comment_count = len(video_data.get("comments", []))
                    topic_count = len(video_data.get("topic", []))  # Count topics here
                    summary[creator]["playlists"][playlist_id]["videos"][video_id] = {
                        "comment_count": comment_count,
                        "topic_count": topic_count
                    }

        # Flatten the summary into a dataframe for easier viewing
        rows = []
        for creator, creator_data in summary.items():
            for playlist_id, playlist_data in creator_data["playlists"].items():
                for video_id, video_data in playlist_data["videos"].items():
                    rows.append({
                        "Content Creator": creator,
                        "Playlist ID": playlist_id,
                        "Video ID": video_id,
                        "Number of Comments": video_data["comment_count"],
                        "Number of Topics": video_data["topic_count"]
                    })

        # Create DataFrame
        df = pd.DataFrame(rows)

        # 筛选选定创作者的数据
        creator_df = df[df["Content Creator"] == selected_creator]
        
        if not creator_df.empty:
            st.subheader(f"Data for ⭐{selected_creator}⭐")
            
            # 显示创作者基本统计信息
            total_playlists = creator_df["Playlist ID"].nunique()
            total_videos = creator_df.shape[0]
            total_comments = creator_df["Number of Comments"].sum()
            total_topics = creator_df["Number of Topics"].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Playlists", total_playlists)
            col2.metric("Total Videos", total_videos)
            col3.metric("Total Comments", total_comments)
            col4.metric("Total Topics", total_topics)
            
            # 显示数据表格
            st.subheader("Videos and Comments")

            # st.table(creator_df.head(20))

            st.dataframe(
                creator_df.style.background_gradient(
                    subset=["Number of Comments", "Number of Topics"], 
                    cmap="Blues"
                ),
                use_container_width=True  # 使用容器的全部宽度
            )
            
            # 按播放列表分组的视频数量并创建自定义Altair图表
            st.subheader("Videos per Playlist")
            playlist_counts = creator_df.groupby("Playlist ID").size().reset_index(name='Video Count')
            
            # 使用Altair创建带倾斜标签的柱状图
            playlist_chart = alt.Chart(playlist_counts).mark_bar().encode(
                x=alt.X('Playlist ID:N', axis=alt.Axis(labelAngle=-45)),  # 设置标签倾斜45度
                y='Video Count:Q',
                color=alt.value('#1f77b4')  # 使用蓝色保持一致性
            ).properties(
                # width='container',  # 使用容器宽度
                height=500
            )
            st.altair_chart(playlist_chart, use_container_width=True)
            
            # 评论数量最多的视频，使用Altair创建倾斜标签
            st.subheader("Top Videos by Comment Count")
            top_videos = creator_df.sort_values("Number of Comments", ascending=False).head(10)
            
            # 使用Altair创建带倾斜标签的柱状图
            video_chart = alt.Chart(top_videos).mark_bar().encode(
                x=alt.X('Video ID:N', axis=alt.Axis(labelAngle=-45)),  # 设置标签倾斜45度
                y='Number of Comments:Q',
                color=alt.value('#1f77b4')  # 使用蓝色保持一致性
            ).properties(
                # width='container',  # 使用容器宽度
                height=500
            )
            st.altair_chart(video_chart, use_container_width=True)

            # 主题数量最多的视频
            st.subheader("Top Videos by Topic Count")
            top_videos_topics = creator_df.sort_values("Number of Topics", ascending=False).head(10)

            video_chart_topics = alt.Chart(top_videos_topics).mark_bar().encode(
                x=alt.X('Video ID:N', axis=alt.Axis(labelAngle=-45)),
                y='Number of Topics:Q',
                color=alt.value('#ff7f0e')  # 使用不同颜色区分
            ).properties(
                height=500
            )
            st.altair_chart(video_chart_topics, use_container_width=True)

            # # 转换数据格式以便于绘制分组柱状图
            # top_videos = creator_df.sort_values("Number of Comments", ascending=False).head(10)
            # chart_data = pd.melt(
            #     top_videos, 
            #     id_vars=['Video ID'], 
            #     value_vars=['Number of Comments', 'Number of Topics'],
            #     var_name='Metric', 
            #     value_name='Count'
            # )

            # # 创建分组柱状图
            # grouped_chart = alt.Chart(chart_data).mark_bar().encode(
            #     x=alt.X('Video ID:N', axis=alt.Axis(labelAngle=-45)),
            #     y='Count:Q',
            #     color='Metric:N',
            #     column=alt.Column('Metric:N', title=None)
            # ).properties(
            #     height=400
            # )
            # st.altair_chart(grouped_chart, use_container_width=True)

        else:
            st.warning(f"No data available for {selected_creator}")
            
    except Exception as e:
        st.error(f"Error loading or processing data: {str(e)}")