import pyzbar.pyzbar as pyzbar
import pandas as pd
import pyttsx3
import threading    # 멀티 프로세싱 (Run Without Wait)
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtGui import QPixmap
import cv2 #카메라 모듈

form_window = uic.loadUiType('./app.ui')[0]

class PThread(QThread):

    changePixmap = pyqtSignal(QImage)

    def __init__(self, mainWindow): #mainWindow는 QWidget에서 전달하는 self이다.(QWidget의 인스턴스)
        super().__init__(mainWindow)
        self.mainWindow = mainWindow #self.mainWindow를 사용하여 QWidget 위젯을 제어할 수 있다.
        self.df = pd.read_csv('./datasets/barcode_final.csv')


    def run(self): #쓰레드로 동작시킬 함수 내용 구현(런에 원하는 동작을 넣어줘야한다!)
        cap = cv2.VideoCapture(0)
        TTS_init= '구매하실 제품의 바코드를 화면에 대주세요'
        threading.Thread(target=self.mainWindow.say, args=(TTS_init,)).start()

        print('run')
        while True:
            ret, frame = cap.read()


            if ret:

                # 바코드 및 QR코드 인식
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                decoded = pyzbar.decode(gray)

                for d in decoded:
                    x, y, w, h = d.rect
                    try:

                        barcode_data = d.data.decode("utf-8")
                        barcode_int = int(barcode_data)
                        print(barcode_int)
                        print(type(barcode_int))

                        barcode_type = d.type

                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                        text = '%s (%s)' % (barcode_data, barcode_type)
                        # time.sleep(0.2)
                        cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
                        self.mainWindow.lbl_result.setText(text)

                        # barcode_data값 df에서 찾기
                        try:

                            product_idx = self.df[self.df['유통바코드'] == barcode_int].index[0]
                            print(product_idx)

                            TTS_data = self.df.iloc[product_idx, :]
                            TTS_text = '이 제품은 {}이고, {}카테고리의 제품입니다.'.format(TTS_data[0], TTS_data[2])
                            TTS_text_1 = '이 제품은 {}이고, \n {}카테고리의 제품입니다.'.format(TTS_data[0], TTS_data[2])
                            # 멀티프로세싱 코드 (target = 해당 동작 , args = 입력값)
                            threading.Thread(target=self.mainWindow.say, args=(TTS_text,)).start()
                            self.mainWindow.lbl_result.setText(TTS_text_1)


                        # barcode_data값을 찾기 못했을 경우
                        except:
                            TTS_text = '해당 제품은 등록되지 않은 제품입니다'
                            threading.Thread(target=self.mainWindow.say, args=(TTS_text,)).start()
                            self.mainWindow.lbl_result.setText(TTS_text)


                            continue

                    # QR코드 인식할 경우
                    except:
                        print(1)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        print(2)
                        TTS_text = '바코드를 정확하게 인식시켜 주세요'
                        print(3)
                        threading.Thread(target=self.mainWindow.say, args=(TTS_text,)).start()
                        print(4)
                        self.mainWindow.lbl_result.setText(TTS_text)

                        continue
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 640, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
        cap.release()
        cv2.destroyAllWindows()


class App_Barcode(QWidget, form_window):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.lbl_result.setText('exam')
        th = PThread(self) #self는 WindowClass의 인스턴스, Thread 클래스에서 mainWindow로 전달
        th.changePixmap.connect(self.setImage)
        th.start()  #쓰레드 클래스의 run 메서드를 동작시키는 부분(위젯이랑 쓰레드 연결(run))

    def say(self, TTS_text):                    # TTS 재생 함수
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say('{}'.format(TTS_text))
        engine.runAndWait()

    def setImage(self, image):
        self.lbl_image.setPixmap(QPixmap.fromImage(image))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = App_Barcode()
    mainWindow.show()
    sys.exit(app.exec_())