import json
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeCaptionUpdater:
    def __init__(self, json_file):
        """
        初始化 YouTubeCaptionUpdater 类，传入数据文件路径。
        :param json_file: 要更新的 JSON 文件路径
        """
        self.json_file = json_file
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

    def update_captions(self):
        """
        遍历 JSON 数据，获取 YouTube 视频字幕，并更新 JSON 数据。
        """
        for channel, playlists in self.data.items():
            for playlist_id, videos in playlists.items():
                for video_id in videos.keys():
                    try:
                        # 获取字幕
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        # 组合字幕文本
                        script = "\n".join([item["text"] for item in transcript])
                        # 存入 JSON 数据
                        self.data[channel][playlist_id][video_id]["captions"] = script
                        print(f"✅ 成功获取字幕: {video_id}")
                    except Exception as e:
                        print(f"⚠️ 无法获取 {video_id} 的字幕: {e}")

    def save_data(self):
        """
        将更新后的数据写回到 JSON 文件。
        """
        try:
            with open(self.json_file, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
            print("🎉 字幕已更新并保存到 data.json")
        except Exception as e:
            print(f"⚠️ 无法保存 JSON 文件: {e}")

    def run(self):
        """
        运行整个字幕更新过程。
        """
        self.update_captions()
        self.save_data()

if __name__ == "__main__":
    # 这里传入数据文件的路径
    caption_updater = YouTubeCaptionUpdater("data.json")
    caption_updater.run()