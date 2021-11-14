import base64
import datetime
import json
import random
import os
import ast
import logging
import traceback
import re


from config import config

class FstateGenerator:
    
    def __init__(self) -> None:
        pass

    def generate_fstate(self, date: datetime, user_info: dict) -> str:
        """生成base64格式的fstate
        Args:
            date (datetime): 报送日期
            user_info (dict): 用户信息
        Returns:
            str: [description]
        """
        try:
            cur_dir_path = os.path.dirname(os.path.abspath(__file__))
            if user_info["report_type"] == "once":
                fstate_path = os.path.join(cur_dir_path, "day_fstate.json")
                fstate = self._generate_day_fstate(fstate_path, date, user_info)
            # TODO: 若为每日两报，则在此处进行新增
            # elif user_info["report_type"] == "twice":
            #     fstate_path = os.path.join(cur_dir_path, "halfday_fstate.json")
            #     fstate = self._generate_halfday_fstate(fstate_path, user_info)
            # fstate = json.dumps(fstate, ensure_ascii=False)
            fstate_base64 = self.generate_fstate_base64(fstate)
            logging.info(f"[user]:{user_info['username']} -- get viewstate success")
            return fstate_base64
        except:
            logging.info(f"[user]:{user_info['username']} -- get viewstate fail")
            logging.info(traceback.format_exc())

    # def _generate_halfday_fstate(self):
    #     pass

    def _generate_day_fstate(self, fstate_path: str, date: datetime, user_info: dict) -> str:
        """生成fstate
        Args:
            fstate_path (str): state模版文件的路径
            date (datetime): 报送日期
            user_info (dict): 用户信息
        Returns:
            str : 生成的fstate
        """
        with open(fstate_path, encoding='utf-8') as f:
            raw_fstate = json.loads(f.read())
        raw_fstate['p1_BaoSRQ']['Text'] = date.strftime('%Y-%m-%d')
        fstate = self._generate_fstate_labels(date, raw_fstate, user_info)
        fstate = self._generate_fstate_address(fstate, user_info)
        return fstate
        

    def _generate_fstate_labels(self, date: datetime, fstate: dict, user_info: dict):
        """生成fstate中的提示信息
        """
        fstate["p1"].update({"Title": f"{user_info['realname']}（{int(user_info['username'])}）的每日一报"})
        today_str, last_15_day_str = self.get_time_span(date)
        time_span = f"{last_15_day_str}至{today_str}"
        fstate["p1_FengXDQDL"].update({"Label": f"{time_span}是否在<span style='color:red;'>中高风险地区</span>逗留"})
        fstate["p1_TongZWDLH"].update({"Label":f"上海同住人员是否有{time_span}来自<span style='color:red;'>中高风险地区</span>的人"})
        fstate["p1_CengFWH"].update({"Label": f"{time_span}是否在<span style='color:red;'>中高风险地区</span>逗留过"})
        fstate["p1_JieChu"].update({"Label": f"{time_span}是否与来自<span style='color:red;'>中高风险地区</span>发热人员密切接触"})
        fstate["p1_TuJWH"].update({"Label": f"{time_span}是否乘坐公共交通途径<span style='color:red;'>中高风险地区</span>"})
        fstate["p1_JiaRen"].update({"Label": f"{time_span}家人是否有发热等症状"})
        return fstate
        
        
    def _generate_fstate_address(self, fstate: dict, user_info: dict):
        """根据用户在配置文件中填的信息，设置fstate中的地址信息
        """
        fstate['p1_ShiFZJ']['SelectedValue'] = "是"  if ast.literal_eval(user_info["is_family_address"]) else "否"
        fstate['p1_XiangXDZ']['Label'] = "国内详细地址（省市区县无需重复填写）"
        if ast.literal_eval(user_info["in_shanghai"]):          # 是否在上海
            if ast.literal_eval(user_info["in_school"]):        # 是否在校
                fstate['p1_ShiFSH']['SelectedValue'] = "在上海（校内）"
                fstate['p1_ShiFZX']['SelectedValue'] = "是"
            else:
                fstate['p1_ShiFSH']['SelectedValue'] = "在上海（不在校内）"
                fstate['p1_ShiFZX']['SelectedValue'] = "否"
        else:
            fstate['p1_ShiFSH']['SelectedValue'] = "不在上海"
            fstate['p1_ShiFZX']['SelectedValue'] = "否"
        fstate['p1_ddlSheng']['F_Items'] = [[user_info["current_address_province"], user_info["current_address_province"], 1, '', '']]
        fstate['p1_ddlSheng']['SelectedValueArray'] =  [user_info["current_address_province"]]
        fstate['p1_ddlShi']['F_Items'] = [[user_info["current_address_city"], user_info["current_address_city"], 1, '', '']]
        fstate['p1_ddlShi']['SelectedValueArray'] = [user_info["current_address_city"]]
        fstate['p1_ddlXian']['F_Items'] = [[user_info["current_address_region"], user_info["current_address_region"], 1, '', '']]
        fstate['p1_ddlXian']['SelectedValueArray'] = [user_info["current_address_region"]]
        fstate['p1_XiangXDZ']['Text'] = user_info['current_address_detail']
        return fstate


    @staticmethod
    def get_time_span(date: datetime):
        """获取当前日期及半个月前日期
        """
        day_str = date.strftime('%m月%d日')
        last_15_day_str = (date + datetime.timedelta(days=-14)).strftime('%m月%d日')
        return day_str, last_15_day_str
    
    @staticmethod
    def generate_fstate_base64(fstate):
        """生成base64格式的fstate
        """
        fstate_json = json.dumps(fstate, ensure_ascii=False)
        fstate_bytes = fstate_json.encode("utf-8")
        fstate_base64 = base64.b64encode(fstate_bytes).decode()
        mid = len(fstate_base64) // 2
        fstate_base64 = fstate_base64[:mid] + 'F_STATE' + fstate_base64[mid:]
        return fstate_base64


if __name__ == "__main__":
    fstater = FstateGenerator()
    fstate = fstater.generate_fstate(datetime.date.today(),config["user"])
    logging.info(fstate)