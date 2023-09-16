from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QCheckBox, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot
from TikTokApi import TikTokApi
import asyncio
import os

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'TikTok Video Search and Download'
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.search_entry = QLineEdit(self)
        self.search_entry.setPlaceholderText("Search Term")
        layout.addWidget(self.search_entry)

        self.min_view_entry = QLineEdit(self)
        self.min_view_entry.setPlaceholderText("Min Views")
        layout.addWidget(self.min_view_entry)
        self.view_check = QCheckBox('Enable View Limit', self)
        layout.addWidget(self.view_check)

        self.min_like_entry = QLineEdit(self)
        self.min_like_entry.setPlaceholderText("Min Likes")
        layout.addWidget(self.min_like_entry)
        self.like_check = QCheckBox('Enable Like Limit', self)
        layout.addWidget(self.like_check)

        self.min_comment_entry = QLineEdit(self)
        self.min_comment_entry.setPlaceholderText("Min Comments")
        layout.addWidget(self.min_comment_entry)
        self.comment_check = QCheckBox('Enable Comment Limit', self)
        layout.addWidget(self.comment_check)

        self.min_save_entry = QLineEdit(self)
        self.min_save_entry.setPlaceholderText("Min Saves")
        layout.addWidget(self.min_save_entry)
        self.save_check = QCheckBox('Enable Save Limit', self)
        layout.addWidget(self.save_check)

        self.button = QPushButton('Search TikTok', self)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.button.clicked.connect(self.on_click)
        self.show()

    @pyqtSlot()
    def on_click(self):
        asyncio.run(self.search_tiktoks())

    async def search_tiktoks(self):
        try:
            async with TikTokApi() as api:
                ms_token = os.environ.get("ms_token", None)  # set your own ms_token
                await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
                
                #with open('C:/Users/Joe/Documents/Code/TikTok-Api/Downloads/cook.txt', 'a') as f:
                #    f.write(ms_token)

                search_term = self.search_entry.text()
                min_view_count = self.view_check.isChecked() and int(self.min_view_entry.text()) or None
                min_like_count = self.like_check.isChecked() and int(self.min_like_entry.text()) or None
                min_comment_count = self.comment_check.isChecked() and int(self.min_comment_entry.text()) or None
                min_save_count = self.save_check.isChecked() and int(self.min_save_entry.text()) or None

                filtered_tiktoks = []
                tag = api.hashtag(name=search_term)
                async for video in tag.videos(count=5):
                    stats = video.as_dict['stats']
                    if (min_view_count is None or stats['playCount'] >= min_view_count) and \
                    (min_like_count is None or stats['diggCount'] >= min_like_count) and \
                    (min_comment_count is None or stats['commentCount'] >= min_comment_count) and \
                    (min_save_count is None or stats['shareCount'] >= min_save_count):
                        filtered_tiktoks.append(video)

                download_path = 'C:/Users/Joe/Documents/Code/TikTok-Api/Downloads' #QFileDialog.getExistingDirectory(self, 'Choose Download Location')

                for i, tiktok in enumerate(filtered_tiktoks):

                    video_bytes = await api.video(data=tiktok.as_dict).bytes()  # Note the await here
                    
                    print(tiktok.as_dict['video']['downloadAddr'])


                    with open(os.path.join(download_path, f'video_{i+1}.mp4'), 'wb') as out:
                        out.write(video_bytes)
            
                    stats = tiktok['stats']
                    timestamp = int(tiktok['createTime'])
                    text_content = f"""
                    Date Uploaded: {timestamp}
                    Account Name: {tiktok['author']['uniqueId']}
                    View Count: {stats['playCount']}
                    Like Count: {stats['diggCount']}
                    Comment Count: {stats['commentCount']}
                    Save Count: {stats['shareCount']}
                    """

                with open(os.path.join(download_path, f'video_{i+1}_info.txt'), 'w') as txt_file:
                    txt_file.write(text_content)

                QMessageBox.information('Success', 'Videos downloaded and info saved.')
            
        except Exception as e:
            print(e)
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    app.exec_()
