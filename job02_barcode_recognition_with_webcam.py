import pyzbar.pyzbar as pyzbar
import cv2
import pandas as pd
import pyttsx3
import threading    # 멀티 프로세싱 (Run Without Wait)

def say(TTS_text):                    # TTS 재생 함수
    engine = pyttsx3.init()
    engine.say('{}'.format(TTS_text))
    engine.runAndWait()

cap = cv2.VideoCapture(0) # 웹캠 실행

i = 0
while(cap.isOpened()):
    ret, img = cap.read()

    if not ret:
        continue

    # 바코드 및 QR코드 인식
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    decoded = pyzbar.decode(gray)

    # 해당 프로젝트는 바코드만 인식해야하기 때문에, QR을 인식할 경우 Except로 넘어감.
    for d in decoded:
        x, y, w, h = d.rect
        try:

            barcode_data = d.data.decode("utf-8")
            # 앞선 바코드 데이터를 int형태로 변경 -> csv파일 내 바코드 숫자랑 일치 해야하기에
            barcode_int = int(barcode_data)
            barcode_type = d.type

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

            text = '%s (%s)' % (barcode_data, barcode_type)

            cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
            # cv2.LINE_AA : 선 유형 / 더 나은 모양을 위해 lineType = cv2.LINE_AA가 권장
            # cv2.LINE_AA = 16

            # barcode_data값 df에서 찾기
            try:
                df = pd.read_csv('./datasets/barcode_final.csv') # csv를 읽는다
                product_idx = df[df['유통바코드'] == barcode_int].index[0]
                # 바코드와 csv내의 유통바코드가 같을 시 해당 인덱스0번(제품명)을 product_idx로 선언
                print(product_idx)

                TTS_data = df.iloc[product_idx, :] # 일치한 product_idx의 해당 전체를 TTS_data로 선언
                TTS_text = '이 제품은 {}이고, {}카테고리의 제품입니다.'.format(TTS_data[0], TTS_data[2]) #인덱스0번은 제품명 / 인덱스2번은 식품유형
                # 멀티프로세싱 코드 (target = 해당 동작 , args = 입력값)
                threading.Thread(target=say, args=(TTS_text,)).start()

            # barcode_data값을 찾기 못했을 경우
            except:
                TTS_text = '해당 제품은 등록되지 않은 제품입니다'
                threading.Thread(target=say, args=(TTS_text,)).start()
                continue

        # QR코드 인식할 경우 / # 바코드 읽는 부분이 없고 그냥 사각형인 형체일 때
        except:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            TTS_text = '바코드를 정확하게 인식시켜 주세요'
            threading.Thread(target=say, args=(TTS_text,)).start()
            continue

    cv2.imshow('img', img)

    # 단축키 Q와 S 실행 코드
    # waitKey : 키 입력 후 대기 시간 (ms)
    key = cv2.waitKey(1)
    # Q 누를 시에, 프로그램 종료
    if key == ord('q'):
        break
    # S 누를 시에, 화면 캡쳐 후 저장.
    elif key == ord('s'):
        i += 1
        cv2.imwrite('c_%03d.jpg' % i, img)

cap.release()
cv2.destroyAllWindows()