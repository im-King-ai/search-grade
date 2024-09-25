import requests, ddddocr, re
from bs4 import BeautifulSoup

USERNAME = ""  # 学号
PASSWORD = ""  # 门户密码


class User:
    __root = "http://jwxt.gdufe.edu.cn"
    __base = "/jsxsd"
    __captcha = f"{__base}/verifycode.servlet"
    __login = f"{__base}/xk/LoginToXkLdap"
    __progress = f"{__base}/pyfa/xyjdcx"

    def __init__(self, name, pwd):
        if name == "" or pwd == "":
            raise Exception("请填写 USERNAME，PASSWORD")

        with requests.Session() as session:
            self.__session = session

        self.__session.get(self.__root + self.__base)

        for _ in range(0, 5):
            response = self.__session.get(self.__root + self.__captcha)

            ocr = ddddocr.DdddOcr(show_ad=False)
            text = ocr.classification(response.content)

            data = {
                "USERNAME": name,
                "PASSWORD": pwd,
                "RANDOMCODE": text
            }
            response = self.__session.post(self.__root + self.__login, data=data)

            soup = BeautifulSoup(response.text, "html.parser")
            if soup.find("title").text == "学生个人中心":
                return
        raise Exception("超出最大重试次数，登录失败，请检查信息后重试。")

    def progress(self):
        param = {"type": "cx"}
        data = {"xdlx": "0"}
        response = self.__session.post(self.__root + self.__progress, params=param, data=data)
        soup = BeautifulSoup(response.text, "html.parser")

        tables = soup.find_all("table")

        for index in range(1, len(tables)):
            rows = tables[index].find_all("tr")
            last_items = rows[-1].find_all("td")

            print(">>>>>>", re.sub(r"\s+", " ", rows[0].find("th").text), "<<<<<<")
            print("要求学分", last_items[1].text.strip())
            print("已获学分", last_items[2].text.strip())

            for row_index in range(2, len(rows) - 1):
                elements = rows[row_index].find_all("td")
                print()
                print("课程编号", elements[2].text)
                print("课程名", elements[3].text)
                print("模块", elements[0].text)
                print("要求学分", elements[4].text)
                print("学期", elements[5].text)
                print("免听免修", elements[6].text)
                print("已获学分", elements[8].text.strip())

            print()
            print()


if __name__ == "__main__":
    User(USERNAME, PASSWORD).progress()