import requests
from bs4 import BeautifulSoup
import ddddocr

USERNAME = "23252401142"  # 学号
PASSWORD = "ning0108.."  # 门户密码

class User:
    __root = "http://jwxt.gdufe.edu.cn"
    __base = "/jsxsd"
    __captcha = "/verifycode.servlet"
    __login = "/xk/LoginToXkLdap"
    __grades = "/jsxsd/kscj/cjcx_list"
    
    def __init__(self, username, password):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.logged_in = False

    def login(self):
        # 获取验证码
        response = self.session.get(self.__root + self.__base + self.__captcha)
        # 识别验证码
        ocr = ddddocr.DdddOcr(show_ad=False)
        captcha_text = ocr.classification(response.content)
        # 发送登录请求
        data = {
            "USERNAME": self.username,
            "PASSWORD": self.password,
            "RANDOMCODE": captcha_text
        }
        response = self.session.post(self.__root + self.__base + self.__login, data=data)
        print(response.text)
        # 检查是否登录成功
        if response.status_code == 200:
            self.logged_in = True
        else:
            raise Exception("登录失败，请检查用户名和密码。")

    def fetch_grades(self):
        if not self.logged_in:
            raise Exception("请先登录再尝试访问成绩页面。")
        
        # 请求成绩页面
        grades_response = self.session.get(self.__root + self.__grades)
        # 解析成绩页面
        soup = BeautifulSoup(grades_response.text, 'html.parser')
        
        # 查找所有的成绩条目
        grade_entries = soup.find_all('tr')
        
        # 遍历每个成绩条目
        for entry in grade_entries:
            # 查找课程名
            course_name_tag = entry.find('td', align="center")
            course_name = course_name_tag.text.strip() if course_name_tag else None
            
            # 查找成绩链接或直接显示的成绩
            grade_link = entry.find('a', href=lambda href: href and href.startswith('javascript:JsMod'))
            grade_cell = entry.find('td', string=lambda text: text and text.isdigit())

            # 如果找到了成绩链接
            grade = None
            if grade_link:
                href = grade_link['href']
                zcj_start = href.find('zcj=') + 4
                zcj_end = href.find(',', zcj_start)
                grade = href[zcj_start:zcj_end]
                
            # 如果没有找到成绩链接，但找到了直接显示的成绩
            elif grade_cell:
                grade = grade_cell.string
            
            # 查找平时分、实验分和期末分
            序号 = entry.find_all('td')[0].text if len(entry.find_all('td')) > 0 else None
            开课学期 = entry.find_all('td')[1].text if len(entry.find_all('td')) > 1 else None
            课程编号 = entry.find_all('td')[2].text if len(entry.find_all('td')) > 2 else None
            regular_score = entry.find_all('td')[4].text if len(entry.find_all('td')) > 4 else None
            usual_score = entry.find_all('td')[5].text if len(entry.find_all('td')) > 5 else None
            final_score = entry.find_all('td')[6].text if len(entry.find_all('td')) > 6 else None
            study_score = entry.find_all('td')[8].text if len(entry.find_all('td')) > 8 else None
            总学时 = entry.find_all('td')[9].text if len(entry.find_all('td')) > 9 else None
            考核方式 = entry.find_all('td')[10].text if len(entry.find_all('td')) > 10 else None
            课程属性 = entry.find_all('td')[11].text if len(entry.find_all('td')) > 11 else None
            课程性质 = entry.find_all('td')[12].text if len(entry.find_all('td')) > 12 else None
            考试性质 = entry.find_all('td')[14].text if len(entry.find_all('td')) > 14 else None
            # 打印课程名、平时分、实验分、期末分和总评成绩
            print(f"序号: {序号},开课学期: {开课学期},课程编号: {课程编号},课程名: {course_name}, 平时分: {regular_score}, 实验分: {usual_score}, 期末分: {final_score}, 总评成绩: {grade},学分: {study_score},总学时:{总学时},考核方式:{考核方式},课程属性:{课程属性},课程性质:{课程性质},考试性质:{考试性质}")
# 使用示例
# 请在这里输入你的账号和密码
user = User(USERNAME, PASSWORD)
user.login()
user.fetch_grades()