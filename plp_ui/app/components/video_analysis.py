# import streamlit as st
# import pandas as pd
# import numpy as np
# import altair as alt
# import plotly.express as px
# import plotly.graph_objects as go

# def show_video_analysis(selected_creator):
#     st.header("Video-Level Analysis")

#     try:
#         # 加载视频情感分析数据
#         videos_data = pd.read_csv('data/video_sentiment_summary.csv')
#         df_sentiment = videos_data[videos_data["Content Creator"] == selected_creator]
        
#         if df_sentiment.empty:
#             st.warning(f"No sentiment analysis data available for {selected_creator}")
#             return
            
#         st.subheader("Video Sentiment Summary")
        
#         # 定义要显示的列
#         columns_to_show = [
#             "Content Creator", "Playlist ID", "Video ID", 
#             "Overall Sentiment", "Positive %", "Negative %", "Neutral %", 
#             "Number of Topics", "Topics"
#         ]
        
#         # 确保所有所需列都存在
#         df_summary_view = df_sentiment[columns_to_show].copy()
        
#         # 处理Topics列，截断长文本或添加换行符
#         if "Topics" in df_summary_view.columns:
#             # 将长文本添加HTML换行标签
#             df_summary_view["Topics"] = df_summary_view["Topics"].apply(
#                 lambda x: '<br>'.join([x[i:i+30] for i in range(0, len(str(x)), 30)]) if pd.notna(x) else ""
#             )
        
#         # 创建自定义Plotly表格，移除wrap属性
#         fig = go.Figure(data=[go.Table(
#             header=dict(
#                 values=list(df_summary_view.columns),
#                 fill_color='rgb(63, 81, 181)',
#                 font=dict(color='white', size=12),
#                 align='left',
#                 height=40
#             ),
#             cells=dict(
#                 values=[df_summary_view[col] for col in df_summary_view.columns],
#                 # 为百分比列设置颜色渐变
#                 fill=dict(
#                     color=[
#                         ['rgba(26, 118, 255, {})'.format(float(str(val).replace('%', ''))/100) 
#                          if col in ['Positive %'] and pd.notna(val) else
#                          'rgba(255, 79, 79, {})'.format(float(str(val).replace('%', ''))/100)
#                          if col in ['Negative %'] and pd.notna(val) else 
#                          'rgba(158, 158, 158, {})'.format(float(str(val).replace('%', ''))/100)
#                          if col in ['Neutral %'] and pd.notna(val) else
#                          'rgb(240, 240, 240)'
#                          for val in df_summary_view[col]]
#                         for col in df_summary_view.columns
#                     ]
#                 ),
#                 align='left',
#                 font=dict(size=12),
#                 height=40  # 增加单元格高度来容纳更多文本
#             )
#         )])
        
#         # 调整表格布局
#         fig.update_layout(
#             autosize=True,
#             margin=dict(l=0, r=0, t=30, b=0),
#             height=800,  # 增加高度以容纳更多行
#             width=1200   # 增加宽度
#         )
        
#         # 显示自定义表格
#         st.plotly_chart(fig, use_container_width=True)
        
#         # 提供可下载的CSV版本
#         csv = df_sentiment[columns_to_show].to_csv(index=False)
#         st.download_button(
#             label="Download data as CSV",
#             data=csv,
#             file_name=f"{selected_creator}_video_analysis.csv",
#             mime="text/csv",
#         )
        
#         # 添加情感分布图表
#         st.subheader("Sentiment Distribution Across Videos")
        
#         # 为图表准备数据
#         chart_data = df_sentiment.copy()
#         if len(chart_data) > 15:
#             chart_data = chart_data.head(15)  # 限制为前15个视频
        
#         # 确保数值是浮点数
#         for col in ['Positive %', 'Negative %', 'Neutral %']:
#             chart_data[col] = pd.to_numeric(chart_data[col], errors='coerce')
        
#         # 创建情感分布堆叠条形图
#         fig_sentiment = go.Figure()
        
#         fig_sentiment.add_trace(go.Bar(
#             x=chart_data['Video ID'],
#             y=chart_data['Positive %'],
#             name='Positive',
#             marker_color='rgb(26, 118, 255)'
#         ))
        
#         fig_sentiment.add_trace(go.Bar(
#             x=chart_data['Video ID'],
#             y=chart_data['Neutral %'],
#             name='Neutral',
#             marker_color='rgb(158, 158, 158)'
#         ))
        
#         fig_sentiment.add_trace(go.Bar(
#             x=chart_data['Video ID'],
#             y=chart_data['Negative %'],
#             name='Negative',
#             marker_color='rgb(255, 79, 79)'
#         ))
        
#         fig_sentiment.update_layout(
#             title='Sentiment Distribution by Video',
#             xaxis={'categoryorder':'total descending', 'tickangle': -45},
#             yaxis=dict(title='Percentage'),
#             barmode='stack',
#             legend=dict(x=0, y=1.0),
#             margin=dict(l=50, r=50, t=80, b=100),
#             height=600
#         )
        
#         st.plotly_chart(fig_sentiment, use_container_width=True)
        
#     except Exception as e:
#         st.error(f"Error analyzing video data: {str(e)}")
#         st.exception(e)  # 显示详细错误信息，方便调试









import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

def show_video_analysis(selected_creator):
    st.header("Video-Level Analysis")

    try:
        # 加载视频情感分析数据
        videos_data = pd.read_csv('data/video_sentiment_summary.csv')
        df_sentiment = videos_data[videos_data["Content Creator"] == selected_creator]
        
        if df_sentiment.empty:
            st.warning(f"No sentiment analysis data available for {selected_creator}")
            return
            
        # st.subheader("Video Sentiment Summary")
        
        # # 定义要显示的列
        # columns_to_show = [
        #     "Content Creator", "Playlist ID", "Video ID", 
        #     "Overall Sentiment", "Positive %", "Negative %", "Neutral %", 
        #     "Number of Topics", "Topics"
        # ]
        
        # # 确保所有所需列都存在
        # df_summary_view = df_sentiment[columns_to_show].copy()
        
        # # 格式化百分比列
        # for col in ["Positive %", "Negative %", "Neutral %"]:
        #     if col in df_summary_view.columns:
        #         df_summary_view[col] = df_summary_view[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                
        # # 使用Plotly创建表格，确保它能很好地适应宽度
        # fig = ff.create_table(df_summary_view)
        # fig.update_layout(
        #     autosize=True,
        #     margin=dict(l=0, r=0, t=30, b=0),
        # )
        # st.plotly_chart(fig, use_container_width=True)
        


        st.subheader("Video Sentiment Summary")

        # 定义要显示的列
        columns_to_show = [
            "Content Creator", "Playlist ID", "Video ID", 
            "Overall Sentiment", "Positive %", "Negative %", "Neutral %",
            "Number of Topics", "Topics"
        ]

        # 确保所有所需列都存在
        df_summary_view = df_sentiment[columns_to_show].copy()

        # 格式化百分比列
        for col in ["Positive %", "Negative %", "Neutral %"]:
            if col in df_summary_view.columns:
                df_summary_view[col] = df_summary_view[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")

        # 使用pandas的styler来设置颜色渐变
        def style_dataframe(df):
            # 提取百分比值用于颜色渐变
            df_numeric = df.copy()
            for col in ["Positive %", "Negative %", "Neutral %"]:
                if col in df.columns:
                    df_numeric[col] = df[col].str.rstrip('%').astype(float)
            
            # 应用样式
            return df_numeric.style\
                .background_gradient(subset=["Positive %", "Negative %", "Neutral %"], cmap="Blues")\
                .format({"Positive %": "{:.2f}%", "Negative %": "{:.2f}%", "Neutral %": "{:.2f}%"})\
                .set_properties(**{
                    'white-space': 'pre-wrap',  # 允许文本换行
                    'text-align': 'left'
                })\
                .set_table_styles([
                    {'selector': 'td', 'props': [('max-width', '200px'), ('word-wrap', 'break-word')]},
                ])

        # 显示带样式的数据框
        styled_df = style_dataframe(df_summary_view)
        st.write(styled_df)

        # 添加自定义CSS以确保表格可以水平滚动且文本换行
        st.markdown("""
        <style>
            .stTable {
                overflow-x: auto;
            }
            .dataframe td {
                white-space: pre-wrap !important;
                max-width: 200px;
                word-wrap: break-word;
            }
            .dataframe th {
                white-space: normal !important;
            }
        </style>
        """, unsafe_allow_html=True)







        # 添加情感分布图表
        st.subheader("Sentiment Distribution Across Videos")
        
        # 为图表准备数据 - 取前10个视频进行比较
        chart_data = df_sentiment.head(10).copy()
        
        # 创建情感分布堆叠条形图
        fig_sentiment = go.Figure()
        
        fig_sentiment.add_trace(go.Bar(
            x=chart_data['Video ID'],
            y=chart_data['Positive %'],
            name='Positive',
            marker_color='rgb(26, 118, 255)'
        ))
        
        fig_sentiment.add_trace(go.Bar(
            x=chart_data['Video ID'],
            y=chart_data['Neutral %'],
            name='Neutral',
            marker_color='rgb(158, 158, 158)'
        ))
        
        fig_sentiment.add_trace(go.Bar(
            x=chart_data['Video ID'],
            y=chart_data['Negative %'],
            name='Negative',
            marker_color='rgb(255, 79, 79)'
        ))
        
        fig_sentiment.update_layout(
            title='Sentiment Distribution by Video',
            xaxis={'categoryorder':'total descending', 'tickangle': -45},
            yaxis=dict(title='Percentage'),
            barmode='stack',
            legend=dict(x=0, y=1.0),
            margin=dict(l=50, r=50, t=80, b=100),
            height=600
        )
        
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # 热门话题分析
        st.subheader("Topic Analysis")
        
        # 提取所有话题并计算频率
        all_topics = []
        for topics_str in df_sentiment['Topics'].dropna():
            if isinstance(topics_str, str):
                # 假设话题是以某种方式分隔的，例如逗号
                topics = [t.strip() for t in topics_str.split(',')]
                all_topics.extend(topics)
        
        if all_topics:
            topic_counts = pd.Series(all_topics).value_counts().reset_index()
            topic_counts.columns = ['Topic', 'Count']
            
            # 显示前15个最常见话题
            top_topics = topic_counts.head(15)
            
            fig_topics = px.bar(
                top_topics, 
                x='Topic', 
                y='Count',
                title=f'Top 15 Topics for {selected_creator}',
                color='Count',
                color_continuous_scale='Blues'
            )
            
            fig_topics.update_layout(
                xaxis={'categoryorder':'total descending', 'tickangle': -45},
                yaxis_title='Frequency',
                margin=dict(l=50, r=50, t=80, b=100),
                height=500
            )
            
            st.plotly_chart(fig_topics, use_container_width=True)
        else:
            st.info("No topic data available for analysis")
        
        # 添加视频按情感排序的表格
        st.subheader("Videos Ranked by Sentiment")
        
        # 创建一个排序后的视图
        df_ranked = df_sentiment.sort_values(by="Positive %", ascending=False).copy()
        columns_for_ranking = ["Video ID", "Overall Sentiment", "Positive %", "Negative %", "Neutral %"]
        df_ranked_view = df_ranked[columns_for_ranking]
        
        # 格式化百分比
        for col in ["Positive %", "Negative %", "Neutral %"]:
            if col in df_ranked_view.columns:
                df_ranked_view[col] = df_ranked_view[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        
        # 用热图样式显示排名
        fig_ranked = ff.create_table(df_ranked_view.head(10))
        st.plotly_chart(fig_ranked, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error analyzing video data: {str(e)}")
        st.exception(e)  # 显示详细错误信息，方便调试








    # st.subheader("Video Engagement and Topics Overview")

    # # Plotly table
    

    # fig = go.Figure(data=[go.Table(
    #     header=dict(
    #         values=list(df_sentiment.columns),
    #         fill_color='paleturquoise',
    #         align='left'
    #     ),
    #     cells=dict(
    #         values=[df_sentiment[col] for col in df_sentiment.columns],
    #         fill_color='lavender',
    #         align='left'
    #     )
    # )])

    # fig.show()

    # st.subheader("第二个图表")
    # columns_to_show = [
    # "Content Creator", "Playlist ID", "Video ID", 
    # "Overall Sentiment", "Positive %", "Negative %", "Neutral %", 
    # "Number of Topics"
    # ]

    # df_summary_view = df_sentiment[columns_to_show]

    # # Display it cleanly
    # df_summary_view.style.background_gradient(subset=["Positive %", "Negative %", "Neutral %"])