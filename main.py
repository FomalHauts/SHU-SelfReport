import sys
import os
root_path = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(root_path,"src")
sys.path.extend([root_path, src_path])

import datetime
import logging
import os
import time
import traceback
import ast
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from login.login import Loginer
from report.report import Reporter
from fstate.generator import FstateGenerator
from mail.send_email import Emailer

from config import config

cur_dir_path = os.path.dirname(os.path.abspath(__file__))



# 配置日志显示
logging.basicConfig(level=logging.INFO,
                 format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                 datefmt='%Y-%m-%d %H:%M:%S',
                filename=os.path.join(cur_dir_path,"log","report.log"),
                filemode='a')



class Launcher:

    REPORT_TIMEOUT = 45                             # 报送时间间隔
    ADMIN_EMAIL = config['email']['admin']
    
    def __init__(self) -> None:
        self.loginer =  Loginer()                   # 登录器
        self.reporter = Reporter()                  # 报送器
        self.fstate_generator = FstateGenerator()   # fstate生成器
        self.emailer = Emailer()                    # 邮件发送器


    def autoreport(self, user_info: dict, date: datetime):
        """按传入的日期进行报送
        Args:
            user_info (dict): 用户信息
            date (datetime): 日期
        """
        try:
            session = self.loginer.login(user_info['username'], user_info['password'])
            fstate = self.fstate_generator.generate_fstate(date, user_info)
            report_result = self.reporter.report(session, date, user_info, fstate)
            if report_result:
                return report_result
        except:
            logging.info(f"AutoReport fail")
            logging.info(traceback.format_exc())

    @staticmethod
    def str_to_datetime(date_str: str):
        if date_str:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return 

    def history_report(self,user_info: dict,today:datetime):
        history_date = self.str_to_datetime(user_info['history_report_begin_date'])
        if history_date and history_date <= today:
            logging.info(f"begin history report from:{history_date}")
            while history_date <= today:
                report_result = self.autoreport(user_info, history_date)
                if report_result:
                    if ast.literal_eval(user_info["success_email"]):
                        self.emailer.send_email(history_date, user_info['email_address'], user_info['email_type'])
                else:
                    self.emailer.send_email(today, self.ADMIN_EMAIL, email_type=user_info['email_type'], identity="admin", user_id=user_info['username'])
                time.sleep(self.REPORT_TIMEOUT)
                history_date = history_date + datetime.timedelta(days=1)

    def today_report(self,user_info: dict,today:datetime):
        report_result = self.autoreport(user_info, today)
        if report_result:
            if ast.literal_eval(user_info["success_email"]):
                self.emailer.send_email(today, user_info['email_address'], email_type=user_info['email_type'])
        else:
            self.emailer.send_email(today, self.ADMIN_EMAIL, email_type=user_info['email_type'], identity="admin", user_id=user_info['username'])

    def main(self):
        try:
            today = datetime.datetime.today()
            for key, user_info in config.items():
                # 判断用户
                if "user" in key:
                    # 历史报送
                    self.history_report(user_info,today)
                    # 今日报送
                    self.today_report(user_info,today)
                time.sleep(self.REPORT_TIMEOUT)
        except:
            self.emailer.send_email(today, self.ADMIN_EMAIL, email_type=user_info['email_type'], identity="admin")
            logging.info(f"Report fail")
            logging.info(traceback.format_exc())

def crontab_listener(event):
    if event.exception:
        logging.error('autoreport failed!!!')
    else:
        logging.info('autoreport success...')

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    launcher = Launcher()
    # launcher.main()
    scheduler.add_job(func=launcher.main, trigger='cron', hour=6, minute=50, id='cron_task')

    # 配置任务执行完成和执行错误的监听
    scheduler.add_listener(crontab_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # 设置日志
    scheduler._logger = logging

    scheduler.start()
