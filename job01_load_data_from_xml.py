import pandas as pd
import requests
from bs4 import BeautifulSoup

def parse():
    try:
        # row_id = item.find("row id").get_text()
        PRDLST_REPORT_NO = item.find("PRDLST_REPORT_NO").get_text()
        PRMS_DT = item.find("PRMS_DT").get_text()
        PRDLST_NM = item.find("PRDLST_NM").get_text()
        BAR_CD = item.find("BAR_CD").get_text()
        POG_DAYCNT = item.find("POG_DAYCNT").get_text()
        PRDLST_DCNM = item.find("PRDLST_DCNM").get_text()
        BSSH_NM = item.find("BSSH_NM").get_text()

        return {
            "품목보고(신고)번호":PRDLST_REPORT_NO,
            "보고(신고일)":PRMS_DT,
            "제품명":PRDLST_NM,
            "유통바코드":BAR_CD,
            "유통/소비기한":POG_DAYCNT,
            "식품 유형":PRDLST_DCNM,
            "제조사명":BSSH_NM,
            }

    except AttributeError as e:
        return {
            "품목보고(신고)번호": None,
            "보고(신고일)": None,
            "제품명": None,
            "유통바코드": None,
            "유통/소비기한": None,
            "식품 유형": None,
            "제조사명": None,
        }
#
for i in range (a, b, 1000):  # a부터 b까지 범위 설정, 1회당 1000개의 데이터씩만 로딩 가능
    url = 'http://openapi.foodsafetykorea.go.kr/api/1e8975ea0aa941a7b9e5/C005/xml/{}/{}'.format(i, i+999)
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'lxml-xml')   # result 내의 text를 'lxml-xml' 파서를 써서 크롤링 | why? 유일하게 'lxml-xml'만이 xml를 구문 분석할 수 있음.
    items = soup.find_all("row") # xml에서 row의 하위에 있는 모든 데이터를 추출
    rows = []
    for item in items:
        rows.append(parse())
    df = pd.DataFrame(rows)
    df.to_csv('./datasets/barcode_{}.csv'.format(i+999))
    print(i+999)



