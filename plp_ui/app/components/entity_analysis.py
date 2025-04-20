# import streamlit as st
# import pandas as pd
# import numpy as np
# import altair as alt
# import plotly.express as px
# import plotly.graph_objects as go
# from wordcloud import WordCloud
# import matplotlib.pyplot as plt
# import io

# def show_entity_analysis():
#     st.header("Entity Sentiment Analysis")
#     df_entity_summary = pd.read_csv('entity_sentiment_summary.csv')

#     st.subheader("Top Entities by Sentiment")
#     import plotly.express as px

#     top_entities = df_entity_summary.sort_values("Avg_Sentiment", ascending=False).head(10)
#     fig = px.bar(
#         top_entities,
#         x="Entity",
#         y="Avg_Sentiment",
#         color="Label",
#         text="Avg_Sentiment",
#         title="Top 10 Entities by Average Sentiment"
#     )
#     fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
#     fig.update_layout(xaxis_tickangle=-45)
#     fig.show()

#     st.subheader("第二个图")
#     import seaborn as sns

#     pivot_table = df_entity_summary.pivot_table(
#         index="Entity", columns="Label", values="Avg_Sentiment"
#     )
#     plt.figure(figsize=(12, 8))
#     sns.heatmap(pivot_table.fillna(0), cmap="coolwarm", annot=False)
#     plt.title("Heatmap of Average Sentiment per Entity and Label")
#     plt.show()

#     st.subheader("第三个图")
#     from wordcloud import WordCloud

#     positive_entities = df_entity_summary[df_entity_summary["Avg_Sentiment"] > 0.2]
#     text_pos = " ".join(positive_entities["Entity"])

#     wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_pos)
#     plt.figure(figsize=(10, 5))
#     plt.imshow(wordcloud, interpolation="bilinear")
#     plt.axis("off")
#     plt.title("Word Cloud of Positive Entities")
#     plt.show()

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

def show_entity_analysis():
    st.header("Entity Sentiment Analysis")
    df_entity_summary = pd.read_csv('data/entity_sentiment_summary3.csv')
    
    # 读取数据，添加错误处理
    # try:
        
    # except FileNotFoundError:
    #     st.error("数据文件 'entity_sentiment_summary.csv' 未找到。请确保文件存在。")
    #     # 为了演示，创建示例数据
    #     st.info("正在使用示例数据进行演示...")
        
    #     # 创建模拟实体数据
    #     entities = ["Product", "Company", "Service", "Feature", "Support", 
    #                "Quality", "Design", "Price", "Value", "App", 
    #                "Website", "Customer", "Team", "Performance", "Experience",
    #                "Interface", "Security", "Reliability", "Update", "Brand"]
        
    #     labels = ["PRODUCT", "ORGANIZATION", "SERVICE", "FEATURE", "SUPPORT"]
        
    #     # 生成示例数据
    #     data = []
    #     for entity in entities:
    #         # 为每个实体随机选择1-3个标签
    #         num_labels = np.random.randint(1, 4)
    #         selected_labels = np.random.choice(labels, size=num_labels, replace=False)
            
    #         for label in selected_labels:
    #             # 生成随机情感分数，偏向正面
    #             sentiment = np.random.normal(0.3, 0.5)
    #             # 限制在 -1 到 1 之间
    #             sentiment = max(min(sentiment, 1.0), -1.0)
                
    #             # 生成随机频率
    #             freq = np.random.randint(5, 100)
                
    #             data.append({
    #                 "Entity": entity,
    #                 "Label": label,
    #                 "Avg_Sentiment": round(sentiment, 2),
    #                 "Frequency": freq
    #             })
        
    #     df_entity_summary = pd.DataFrame(data)
    
    # 1. 顶部实体情感条形图
    st.subheader("Top Entities by Sentiment")
    
    # 按平均情感排序获取前10个实体
    top_entities = df_entity_summary.sort_values("Avg_Sentiment", ascending=False).head(10)
    
    fig = px.bar(
        top_entities,
        x="Entity",
        y="Avg_Sentiment",
        color="Label",
        text="Avg_Sentiment",
        title="Top 10 Entities by Average Sentiment",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        xaxis_title="Entity",
        yaxis_title="Average Sentiment Score (-1 to 1)",
        legend_title="Entity Type"
    )
    
    # Streamlit中正确显示plotly图表
    st.plotly_chart(fig, use_container_width=True)
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        # 2. 实体类型分布
        st.subheader("Entity Type Distribution")
        
        label_counts = df_entity_summary["Label"].value_counts().reset_index()
        label_counts.columns = ["Label", "Count"]
        
        fig = px.pie(
            label_counts, 
            values="Count", 
            names="Label",
            title="Distribution of Entity Types",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 3. 情感分布箱形图
        st.subheader("Sentiment Distribution by Entity Type")
        
        fig = px.box(
            df_entity_summary,
            x="Label",
            y="Avg_Sentiment",
            color="Label",
            title="Sentiment Distribution by Entity Type",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            points="all"
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Entity Type",
            yaxis_title="Average Sentiment Score"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 4. 热图 - 实体和标签的情感
    st.subheader("Entity-Label Sentiment Heatmap")
    
    # 提供两种热图展示选项
    heatmap_option = st.radio(
        "Select heatmap style",
        ["Show All Entities", "Show only the top 15 entities with the highest sum of sentiment scores"],
        horizontal=True
    )
    
    # 获取实体和热图数据
    if heatmap_option == "Show All Entities":
        # 使用所有实体，与PLP2相同的实现
        pivot_table = df_entity_summary.pivot_table(
            index="Entity", 
            columns="Label", 
            values="Avg_Sentiment"
        ).fillna(0)
        
        # 使用matplotlib创建热图
        fig, ax = plt.subplots(figsize=(12, 8))
        
        sns.heatmap(
            pivot_table, 
            cmap="coolwarm", 
            annot=False,
            ax=ax
        )
        
        plt.title("Heatmap of Average Sentiment per Entity and Label")
        plt.tight_layout()
    
    else:
        # 增强版本：获取出现频率最高的前15个实体
        top_freq_entities = df_entity_summary.groupby("Entity")["Avg_Sentiment"].sum().nlargest(15).index.tolist()
        filtered_df = df_entity_summary[df_entity_summary["Entity"].isin(top_freq_entities)]
        
        # 创建透视表
        pivot_table = filtered_df.pivot_table(
            index="Entity", 
            columns="Label", 
            values="Avg_Sentiment"
        ).fillna(0)
        
        # 使用matplotlib创建热图
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 创建自定义颜色映射：从红色（负面）到白色（中性）到蓝色（正面）
        colors = ["#d62728", "#ffffff", "#1f77b4"]  # 红、白、蓝
        cmap = LinearSegmentedColormap.from_list("sentiment_cmap", colors, N=100)
        
        sns.heatmap(
            pivot_table, 
            cmap=cmap, 
            annot=True, 
            fmt=".2f", 
            linewidths=0.5,
            vmin=-1, 
            vmax=1,
            center=0,
            ax=ax
        )
        
        plt.title("Heatmap of Average Sentiment per Entity and Label (Top 15 Entities)")
        plt.tight_layout()
    
    # 将matplotlib图表显示在Streamlit中
    st.pyplot(fig)
    
    # 5. 词云图 - 积极实体
    st.subheader("Word Clouds by Sentiment")
    
    # 添加词云风格选择
    wordcloud_style = st.radio(
        "Select wordcloud style",
        ["Intuitive positive emotion word cloud", "A word cloud using a weighted system that takes into account the frequency and sentiment scores of entities"],
        horizontal=True
    )
    
    if wordcloud_style == "Intuitive positive emotion word cloud":
        # 使用与PLP2相同的实现
        st.write("Word Cloud of Positive Entities (Sentiment > 0.2)")
        positive_entities = df_entity_summary[df_entity_summary["Avg_Sentiment"] > 0.2]
        
        if len(positive_entities) > 0:
            # 简单合并实体名称 - 确保所有实体都是字符串类型
            # 将所有实体转换为字符串，避免数字类型引起的错误
            text_pos = " ".join(positive_entities["Entity"].astype(str))
            
            # 创建词云 - 与PLP2参数完全相同
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white'
            ).generate(text_pos)
            
            # 显示词云
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            ax.set_title("Word Cloud of Positive Entities")
            st.pyplot(fig)
        else:
            st.write("No positive entities found.")
    
    else:
        # 高级词云版本 - 三列布局
        cloud_col1, cloud_col2, cloud_col3 = st.columns(3)
        
        with cloud_col1:
            st.write("Positive Entities (Sentiment > 0.2)")
            positive_entities = df_entity_summary[df_entity_summary["Avg_Sentiment"] > 0.2]
            
            if len(positive_entities) > 0:
                # 创建频率字典
                freq_dict = {}
                for _, row in positive_entities.iterrows():
                    entity = row["Entity"]
                    sentiment = row["Avg_Sentiment"]
                    # 确保使用行中的Frequency字段
                    frequency = row.get("Frequency", 1)  # 如果没有频率字段，默认为1
                    # 使用频率和情感得分的组合作为权重
                    weight = frequency * (1 + sentiment)
                    freq_dict[entity] = freq_dict.get(entity, 0) + weight
                
                if freq_dict:
                    # 创建词云
                    wordcloud = WordCloud(
                        width=300, 
                        height=300, 
                        background_color='white',
                        colormap='Blues',
                        max_font_size=100
                    ).generate_from_frequencies(freq_dict)
                    
                    # 显示词云
                    fig, ax = plt.subplots(figsize=(5, 5))
                    ax.imshow(wordcloud, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)
                else:
                    st.write("No positive entities found.")
            else:
                st.write("No positive entities found.")
        
        with cloud_col2:
            st.write("Neutral Entities (-0.2 ≤ Sentiment ≤ 0.2)")
            neutral_entities = df_entity_summary[(df_entity_summary["Avg_Sentiment"] >= -0.2) & 
                                            (df_entity_summary["Avg_Sentiment"] <= 0.2)]
            
            if len(neutral_entities) > 0:
                # 创建频率字典
                freq_dict = {}
                for _, row in neutral_entities.iterrows():
                    entity = row["Entity"]
                    # 确保使用行中的Frequency字段
                    frequency = row.get("Frequency", 1)  # 如果没有频率字段，默认为1
                    freq_dict[entity] = freq_dict.get(entity, 0) + frequency
                
                if freq_dict:
                    # 创建词云
                    wordcloud = WordCloud(
                        width=300, 
                        height=300, 
                        background_color='white',
                        colormap='Greys',
                        max_font_size=100
                    ).generate_from_frequencies(freq_dict)
                    
                    # 显示词云
                    fig, ax = plt.subplots(figsize=(5, 5))
                    ax.imshow(wordcloud, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)
                else:
                    st.write("No neutral entities found.")
            else:
                st.write("No neutral entities found.")
        
        with cloud_col3:
            st.write("Negative Entities (Sentiment < -0.2)")
            negative_entities = df_entity_summary[df_entity_summary["Avg_Sentiment"] < -0.2]
            
            if len(negative_entities) > 0:
                # 创建频率字典
                freq_dict = {}
                for _, row in negative_entities.iterrows():
                    entity = row["Entity"]
                    sentiment = row["Avg_Sentiment"]
                    # 确保使用行中的Frequency字段
                    frequency = row.get("Frequency", 1)  # 如果没有频率字段，默认为1
                    # 使用频率和情感得分的绝对值作为权重
                    weight = frequency * (1 + abs(sentiment))
                    freq_dict[entity] = freq_dict.get(entity, 0) + weight
                
                if freq_dict:
                    # 创建词云
                    wordcloud = WordCloud(
                        width=300, 
                        height=300, 
                        background_color='white',
                        colormap='Reds',
                        max_font_size=100
                    ).generate_from_frequencies(freq_dict)
                    
                    # 显示词云
                    fig, ax = plt.subplots(figsize=(5, 5))
                    ax.imshow(wordcloud, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)
                else:
                    st.write("No negative entities found.")
            else:
                st.write("No negative entities found.")
    
    # 6. 添加交互式散点图 - 实体频率与情感
    st.subheader("Entity Frequency vs. Sentiment")
    
    # 检查数据集中是否有Frequency列
    if "Frequency" in df_entity_summary.columns:
        # 按标签分组计算实体频率和平均情感
        entity_agg = df_entity_summary.groupby(["Entity", "Label"]).agg({
            "Avg_Sentiment": "mean",
            "Frequency": "sum"  # 确保聚合Frequency
        }).reset_index()
        
        # 创建散点图
        fig = px.scatter(
            entity_agg,
            x="Frequency",
            y="Avg_Sentiment",
            color="Label",
            hover_name="Entity",
            text="Entity",
            title="Entity Frequency vs. Sentiment Score",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={
                "Frequency": "Mention Frequency",
                "Avg_Sentiment": "Average Sentiment Score (-1 to 1)"
            }
        )
        
        # 仅对频率较高的实体显示标签
        fig.update_traces(
            textposition='top center',
            textfont_size=10,
            mode=lambda d: 'markers+text' if d.get('x', 0) > np.percentile(entity_agg["Frequency"], 75) else 'markers'
        )
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("无法创建频率vs情感散点图：数据集中缺少'Frequency'列")
    
    # 7. 下载数据按钮
    st.subheader("Download Entity Analysis Data")
    csv = df_entity_summary.to_csv(index=False)
    st.download_button(
        label="Download Entity Data as CSV",
        data=csv,
        file_name="entity_sentiment_analysis.csv",
        mime="text/csv"
    )