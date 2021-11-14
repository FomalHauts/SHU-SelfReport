import os
import logging
import traceback
import datetime
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import config

class Emailer:

    def __init__(self) -> None:
        self.smtp_server = config["email"]["smtp_server"]
        self.username = config["email"]["username"]
        self.password = config["email"]["password"]
        self.smtp = None

    def _smtp_connect(self):
        """smtp服务器连接测试
        """
        try:
            self.smtp = smtplib.SMTP_SSL(self.smtp_server, 465)
            self.smtp.login(self.username, self.password)
            logging.info("smtp connect success")
        except:
            logging.info("smtp connenct fail")
            logging.info(traceback.format_exc())

    def set_html_email(self):
        """设置html格式的email
        """
        cur_dir_path = os.path.dirname(os.path.abspath(__file__))
        html_email_path = os.path.join(cur_dir_path,"success_email.html")
        html_email = open(html_email_path, "rb").read()
        return html_email


    def set_mail_info(self, date: datetime, email_type: str, identity="user", user_id=None):
        """设置邮件主题与正文
        """
        date_str = date.strftime('%Y-%m-%d')
        if identity == "admin":
            mail_subject = f"[{date_str}]{config['email']['admin_fail_subject']}"
            mail_body = MIMEText((config['email']['admin_fail_text']+user_id))
        elif identity == "user":
            mail_subject = f"[{date_str}]{config['email']['success_subject']}"
            if email_type == "html":
                content = self.set_html_email()
                mail_body = MIMEText(content, _subtype='html', _charset='utf-8')
            elif email_type == "text":
                content = config['email']['success_text']
                mail_body = MIMEText(content)
        return mail_subject, mail_body

    def _set_email_info(self, date:datetime, receiver:str, email_type="text", attachment=None, identity="user", user_id=None):
        # 构造一个邮件体：正文 附件
        msg = MIMEMultipart()
        msg['From'] = self.username                # 发件人
        if identity == "admin":
            msg['To'] = receiver                       # 管理员邮箱
        elif identity == "user":
            msg['To'] = receiver                       # 收件人
        mail_subject, mail_body = self.set_mail_info(date, email_type, identity, user_id)    # 主题,正文
        msg['Subject'] = mail_subject
        msg.attach(mail_body)                # 把正文加到邮件体里面去

        if attachment is not None:
            # 构建邮件附件
            attachment = MIMEApplication(open(attachment, 'rb').read())  # 打开附件
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))  # 为附件命名
            msg.attach(attachment)  # 添加附件
        return msg

    def _send_email(self, date: datetime, receiver: str, email_type="text", attachment=None, identity="user", user_id=None):
        """给用户发送邮件
        Args:
            date (datetime): 报送日期
            receiver (str): 收件人
            mail_type (str, optional): 邮件类型(text/html),默认为文本格式邮件，即text
            attachment ([type], optional): 附件(可选)
        """
        try:
            # 发送邮件 SMTP
            msg = self._set_email_info(date, receiver, email_type, attachment, identity, user_id)
            self.smtp.sendmail(self.username, receiver, msg.as_string())
            logging.info(f"[user]:{receiver} -- send email success")
        except Exception as e:
            logging.info(f'[user]:{receiver} -- send email fail')
            logging.info(traceback.format_exc())

    def send_email(self, date: datetime, receiver: str, email_type="text", attachment=None, identity="user", user_id=None):
        self._smtp_connect()
        self._send_email(date, receiver, email_type, attachment, identity, user_id)
        self.dispose()


    def dispose(self):
        """断开与smtp服务器的连接
        """
        if self.smtp:
            self.smtp.quit()



if __name__ == '__main__':
    print(1)
