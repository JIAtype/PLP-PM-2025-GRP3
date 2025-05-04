import json
from transformers import BertTokenizer, BertModel
import torch
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np

# 下载 NLTK 必需的资源
nltk.download('punkt')

class TopicModelingBERT:
    def __init__(self, json_file, num_topics=5):
        """
        初始化 TopicModelingBERT 类，接收 JSON 文件路径和主题数量。
        :param json_file: 输入的 JSON 文件路径
        :param num_topics: 提取的主题数
        """
        self.json_file = json_file
        self.num_topics = num_topics
        self.data = self.load_data()

        # 加载 BERT tokenizer 和模型
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')

    def load_data(self):
        """
        加载 JSON 数据。
        :return: 加载的 JSON 数据
        """
        try:
            with open(self.json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(f"⚠️ 无法加载 JSON 文件: {e}")
            return {}

    def extract_captions(self):
        """
        提取所有视频的字幕文本。
        :return: 字幕列表和视频 ID 映射
        """
        captions_list = []
        video_id_map = []  # 存储 (author, playlist_id, video_id)

        for author, playlists in self.data.items():
            for playlist_id, videos in playlists.items():
                for video_id, video_data in videos.items():
                    captions = video_data.get("captions", "").strip()  # 读取字幕
                    if captions:
                        sentences = sent_tokenize(captions)  # 按句子拆分
                        captions_list.extend(sentences)
                        for _ in sentences:
                            video_id_map.append((author, playlist_id, video_id))

        return captions_list, video_id_map

    def get_bert_embeddings(self, texts):
        """
        使用 BERT 提取文本特征（嵌入向量）。
        :param texts: 输入的文本列表
        :return: BERT 提取的嵌入向量
        """
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy()  # 使用平均池化得到句子的向量
        return embeddings

    def topic_modeling(self, captions_list):
        """
        使用 KMeans 进行主题建模。
        :param captions_list: 提取的字幕文本列表
        :return: 聚类标签和 BERT 嵌入向量
        """
        # 获取所有句子的 BERT 嵌入向量
        embeddings = self.get_bert_embeddings(captions_list)

        # 使用 KMeans 聚类进行主题建模
        kmeans = KMeans(n_clusters=self.num_topics, random_state=42)
        kmeans.fit(embeddings)

        return kmeans.labels_, embeddings

    def get_top_keywords_for_topics(self, captions, labels, num_keywords=5):
        """
        获取每个主题的关键词（最具代表性的词）。
        :param captions: 输入的字幕列表
        :param labels: 聚类标签
        :param num_keywords: 每个主题提取的关键词数
        :return: 每个主题的关键词
        """
        vectorizer = CountVectorizer(stop_words='english')
        X = vectorizer.fit_transform(captions)
        feature_names = np.array(vectorizer.get_feature_names_out())

        topic_keywords = {}
        for topic_num in range(self.num_topics):
            # 获取属于该主题的所有句子
            topic_indices = np.where(labels == topic_num)[0]
            topic_sentences = [captions[i] for i in topic_indices]

            # 计算这些句子的词频
            topic_matrix = X[topic_indices]
            word_freq = topic_matrix.sum(axis=0).A1  # 获取词频
            sorted_indices = word_freq.argsort()[::-1]  # 排序

            # 提取前 num_keywords 个关键词
            top_keywords = feature_names[sorted_indices][:num_keywords]
            topic_keywords[topic_num] = top_keywords

        return topic_keywords

    def assign_topics(self, video_id_map, kmeans_labels, topic_keywords):
        """
        将主题分配给每个视频。
        :param video_id_map: 存储 (author, playlist_id, video_id) 的列表
        :param kmeans_labels: 聚类标签
        :param topic_keywords: 主题关键词
        """
        for i, (author, playlist_id, video_id) in enumerate(video_id_map):
            best_topic = kmeans_labels[i]
            topic_name = " ".join(topic_keywords[best_topic])  # 通过关键词生成主题名称
            self.data[author][playlist_id][video_id]["topic"] = topic_name

    def save_data(self):
        """
        将更新后的数据保存回 JSON 文件。
        """
        try:
            with open(self.json_file, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
            print("🎉 主题建模完成并保存到 data.json")
        except Exception as e:
            print(f"⚠️ 无法保存 JSON 文件: {e}")

    def run(self):
        """
        运行整个主题建模过程。
        """
        captions_list, video_id_map = self.extract_captions()

        if not captions_list:
            print("No captions found in data.json")
            return

        kmeans_labels, embeddings = self.topic_modeling(captions_list)
        topic_keywords = self.get_top_keywords_for_topics(captions_list, kmeans_labels)
        self.assign_topics(video_id_map, kmeans_labels, topic_keywords)
        self.save_data()


if __name__ == "__main__":
    # 传入数据文件的路径，和你想要提取的主题数
    topic_modeler = TopicModelingBERT("data.json", num_topics=5)
    topic_modeler.run()