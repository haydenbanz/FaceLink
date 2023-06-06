import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtCore import Qt
import time
import requests
import urllib.request

TESTING_MODE = True
APITOKEN = '<YOUR API TOKEN' # Your API Token


class FaceRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceLink")
        self.setGeometry(100, 100, 400, 400)
        self.setWindowIcon(QIcon("icon.png"))

        self.label_url = QLabel("URL:")
        self.textbox_url = QLineEdit()

        self.label_output = QLabel("Output File Name:")
        self.textbox_output = QLineEdit()

        self.button_recognize = QPushButton("Recognize Face")
        self.button_recognize.clicked.connect(self.recognize_face)

        self.output_textbox = QTextEdit()
        self.output_textbox.setReadOnly(True)
        self.output_textbox.setLineWrapMode(QTextEdit.NoWrap)

        layout = QVBoxLayout()
        layout.addWidget(self.label_url)
        layout.addWidget(self.textbox_url)
        layout.addWidget(self.label_output)
        layout.addWidget(self.textbox_output)
        layout.addWidget(self.button_recognize)
        layout.addWidget(self.output_textbox)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #333333;
                color: #ffffff;
            }

            QLabel {
                color: #ffffff;
            }

            QLineEdit {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #ffffff;
            }

            QPushButton {
                background-color: #555555;
                color: #ffffff;
                border: none;
                padding: 5px;
            }

            QPushButton:hover {
                background-color: #777777;
            }

            QTextEdit {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #ffffff;
                padding: 5px;
            }
        """)

    def recognize_face(self):
        url = self.textbox_url.text()
        output_file_name = self.textbox_output.text()

        # Download the photo from the provided URL
        urllib.request.urlretrieve(url, output_file_name)

        def search_by_face(image_file):
            if TESTING_MODE:
                self.append_text('****** WELCOME, SEAERCHING IN PROGRESSS - MADBOT ******')

            site = 'https://facecheck.id'
            headers = {'accept': 'application/json', 'Authorization': APITOKEN}
            files = {'images': open(image_file, 'rb'), 'id_search': None}
            response = requests.post(site+'/api/upload_pic', headers=headers, files=files).json()

            if response['error']:
                return f"{response['error']} ({response['code']})", None

            id_search = response['id_search']
            self.append_text(response['message'] + ' id_search='+id_search)
            json_data = {'id_search': id_search, 'with_progress': True, 'status_only': False, 'demo': TESTING_MODE}

            while True:
                response = requests.post(site+'/api/search', headers=headers, json=json_data).json()
                if response['error']:
                    return f"{response['error']} ({response['code']})", None
                if response['output']:
                    return None, response['output']['items']
                self.append_text(f'{response["message"]} progress: {response["progress"]}%')
                time.sleep(1)

        # Search the Internet by face
        error, urls_images = search_by_face(output_file_name)

        if urls_images:
            for im in urls_images:  # Iterate search results
                score = im['score']  # 0 to 100 score indicating how well the face matches the found image
                url = im['url']  # URL to the webpage where the person was found
                image_base64 = im['base64']  # Thumbnail image encoded as a base64 string
                self.append_text(f"{score} <a href='{url}'>{url}</a> {image_base64[:32]}...")
        else:
            self.append_text(error)

    def append_text(self, text):
        cursor = self.output_textbox.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(f"{text}<br>")
        self.output_textbox.setTextCursor(cursor)
        self.output_textbox.ensureCursorVisible()


if __name__ == "__main__":
    TESTING_MODE = True
    APITOKEN = '<YOUR APTI TOKRN>'

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = FaceRecognitionApp()
    window.show()

    sys.exit(app.exec_())
