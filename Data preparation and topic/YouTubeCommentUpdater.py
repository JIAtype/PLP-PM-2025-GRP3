import json
from googleapiclient.discovery import build

class YouTubeCommentExtractor:
    def __init__(self, api_key, json_file):
        """
        初始化 YouTubeCommentExtractor 类，接收 API 密钥和 JSON 文件路径。
        :param api_key: YouTube API 密钥
        :param json_file: 输入的 JSON 文件路径
        """
        self.api_key = api_key
        self.json_file = json_file
        self.data = self.load_data()

        # 初始化 YouTube API 客户端
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

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

    def get_comments_for_video(self, video_id):
        """
        获取指定视频的所有评论。
        :param video_id: 视频 ID
        :return: 所有评论的列表
        """
        all_comments = []
        next_page_token = None

        # 循环获取所有评论
        while True:
            comment_request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=next_page_token,
                textFormat="plainText",
                maxResults=100  # 每次最多返回 100 条评论
            )
            comment_response = comment_request.execute()

            for item in comment_response['items']:
                top_comment = item['snippet']['topLevelComment']['snippet']
                all_comments.append({
                    'Timestamp': top_comment['publishedAt'],
                    'Comment': top_comment['textDisplay'],
                    'VideoID': video_id
                })

            # 获取下一页的 Token，如果没有就结束循环
            next_page_token = comment_response.get('nextPageToken')
            if not next_page_token:
                break
        
        return all_comments

    def extract_comments(self):
        """
        提取所有视频的评论并将其添加到 JSON 数据中。
        """
        for author, playlists in self.data.items():
            for playlist_id, playlist_data in playlists.items():
                for video_id, video_data in playlist_data.items():
                    print(f"正在提取视频 {video_id} 的评论... 作者: {author}, 播放列表: {playlist_id}")
                    
                    # 获取视频评论
                    video_comments = self.get_comments_for_video(video_id)
                    
                    # 将评论添加到 JSON 数据的 comments 字段
                    video_data["comments"] = [{'Timestamp': comment['Timestamp'], 'Comment': comment['Comment']} for comment in video_comments]

    def save_data(self):
        """
        将更新后的数据保存回 JSON 文件。
        """
        try:
            with open(self.json_file, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
            print("🎉 评论提取并成功保存到 data.json!")
        except Exception as e:
            print(f"⚠️ 无法保存 JSON 文件: {e}")

    def run(self):
        """
        运行整个评论提取流程。
        """
        self.extract_comments()
        self.save_data()


if __name__ == "__main__":
    # 输入 YouTube API 密钥和 JSON 文件路径
    api_key = "AIzaSyDFNwUyRKg40gidJuWB55oXtGoP3KMKsPM"
    json_file = "data.json"

    # 创建 YouTubeCommentExtractor 实例并运行
    extractor = YouTubeCommentExtractor(api_key, json_file)
    extractor.run()