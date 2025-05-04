import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# 下载 NLTK 必需的资源
nltk.download('punkt')
nltk.download('stopwords')

class TopicModeling:
    def __init__(self, json_file, num_topics=5):
        """
        初始化 TopicModeling 类，接收 JSON 文件路径和主题数量。
        :param json_file: 输入的 JSON 文件路径
        :param num_topics: 提取的主题数
        """
        self.json_file = json_file
        self.num_topics = num_topics
        self.data = self.load_data()

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
                        captions_list.append(captions)
                        video_id_map.append((author, playlist_id, video_id))

        return captions_list, video_id_map

    def topic_modeling(self, captions_list):
        """
        使用 NMF 进行主题建模。
        :param captions_list: 提取的字幕文本列表
        :return: 主题关键词
        """
        # 进行文本向量化
        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        X = vectorizer.fit_transform(captions_list)

        # 训练 NMF 模型
        nmf_model = NMF(n_components=self.num_topics, random_state=42)
        W = nmf_model.fit_transform(X)
        H = nmf_model.components_

        # 获取主题关键词
        terms = vectorizer.get_feature_names_out()
        topic_keywords = [" ".join([terms[i] for i in topic.argsort()[-10:]]) for topic in H]

        return topic_keywords, W

    def assign_topics(self, video_id_map, W, topic_keywords):
        """
        将主题分配给每个视频。
        :param video_id_map: 存储 (author, playlist_id, video_id) 的列表
        :param W: 主题分配矩阵
        :param topic_keywords: 主题关键词
        """
        for i, (author, playlist_id, video_id) in enumerate(video_id_map):
            best_topic = W[i].argmax()
            self.data[author][playlist_id][video_id]["topic"] = topic_keywords[best_topic]  # 直接存字符串

    def save_data(self):
        """
        将更新后的数据写回到 JSON 文件。
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
        
        topic_keywords, W = self.topic_modeling(captions_list)
        self.assign_topics(video_id_map, W, topic_keywords)
        self.save_data()

if __name__ == "__main__":
    # 这里传入数据文件的路径，和你想要提取的主题数
    topic_modeler = TopicModeling("data.json", num_topics=5)
    topic_modeler.run()