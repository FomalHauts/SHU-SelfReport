from datetime import datetime
import logging
from os import fstat
import traceback
import time
from bs4 import BeautifulSoup
from report.data import report_data
import ast

class Reporter:

    def __init__(self) -> None:
        pass

    def get_view_state(self, session, url: str):
        """获取viewstate
        Args:
            session ([type]): requests session
            url (str): 报送url
        """
        try:
            res = session.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})
            if view_state is None or 'invalid_grant' in res.text:
                logging.info("get view_state fail")
                return
            return view_state['value']
        except:
            logging.info(traceback.format_exc())
            logging.info("after logined, auth to selfreport site fail")


    def is_in_shanghai(self,user_info:dict):
        if ast.literal_eval(user_info["in_shanghai"]):          # 是否在上海
            if ast.literal_eval(user_info["in_school"]):        # 是否在校
                in_shanghai =  "在上海（校内）"
            else:
                in_shanghai = "在上海（不在校内）"
        else:
            in_shanghai = "不在上海"
        return in_shanghai
                
        
    def get_report_data(self, date: datetime, user_info: dict, view_state: str, fstate: str):
        """通过更新模版文件,获取报送数据
        Args:
            date (datetime): 报送日期
            user_info (dict): 用户信息
            view_state (str): viewstate
            fstate (str): fstate
        """
        update_dict = {
            "__VIEWSTATE": view_state,
            "p1$BaoSRQ": date.strftime('%Y-%m-%d'),      # 报送日期
            "p1$ShiFSH": self.is_in_shanghai(user_info),      # 是否在上海
            "p1$ShiFZX": "是" if ast.literal_eval(user_info["in_school"]) else "否",                # 是否住校
            "p1$ddlSheng$Value": user_info["current_address_province"],       # 当天所在省
            "p1$ddlSheng": user_info["current_address_province"],            # 当天所在省
            "p1$ddlShi$Value": user_info["current_address_city"],       # 当天所在市
            "p1$ddlShi": user_info["current_address_city"],            # 当天所在市
            "p1$ddlXian$Value": user_info["current_address_region"],      # 当天所在县区
            "p1$ddlXian": user_info["current_address_region"],          # 当天所在县区
            "p1$XiangXDZ": user_info["current_address_detail"], # 校内：校内宿舍地址（校区、幢楼 、房间）, 不住校：国内详细地址（省市区县无需重复填写）：
            "p1$ShiFZJ": "是" if ast.literal_eval(user_info["is_family_address"]) else "否",               # 是否家庭住址
            "F_STATE": fstate,
        }
        report_data.update(update_dict)        
        return report_data
    
    def report(self, session, date: datetime, user_info: dict, fstate: str):
        """报送接口
        """
        try:        
            url = f'https://selfreport.shu.edu.cn/DayReport.aspx?day={date.year}-{date.month}-{date.day}'
            view_state = self.get_view_state(session, url)
            report_data = self.get_report_data(date, user_info, view_state, fstate)
            res = session.post(url, data=report_data, headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-FineUI-Ajax': 'true'
            }, allow_redirects=False)
            # print(res.text)
            if any(i in res.text for i in ['提交成功', '历史信息不能修改', '现在还没到晚报时间', '只能填报当天或补填以前的信息']):
                logging.info(f"[user]:{user_info['username']} -- [{date}] -- report success")
                return True
            else:
                logging.info(f"[user]:{user_info['username']} -- [{date}] -- report fail")
                return False
        except Exception as e:
            logging.info(traceback.format_exc())



if __name__ == "__main__":
    pass

