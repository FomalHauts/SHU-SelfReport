
import requests
import base64
import logging
import traceback

from encrypt import pwd_encrypt

class Loginer:

    def __init__(self) -> None:
        pass

    def _loginAPI(self, session, username: str, password: str):
        """登录api
        Args:
            session ([type]): requests session
            username (str): 学号
            password (str): 密码
        """
        try:
            res = session.get('https://selfreport.shu.edu.cn/Default.aspx')
            url_suffix = res.url.split('/')[-1]
            url_param = eval(base64.b64decode(url_suffix).decode("utf-8"))
            state = url_param['state']
            data={
                'username': username,
                'password': pwd_encrypt(password)
            }
            session.post(res.url, data=data, allow_redirects=False)
            res = session.get(f'https://newsso.shu.edu.cn/oauth/authorize?response_type=code&client_id=WUHWfrntnWYHZfzQ5QvXUCVy&redirect_uri=https%3a%2f%2fselfreport.shu.edu.cn%2fLoginSSO.aspx%3fReturnUrl%3d%252fDefault.aspx&scope=1&state={state}')
            # print(res.text)
            if res.status_code == 200:
                return session
            else:
                logging.info("status_code:auth fail")
                return 
        except:
            logging.info(traceback.format_exc())
            return 

    def login(self, username, password):
        try:
            session = requests.session()
            session = self._loginAPI(session,username, password)
            if session:
                logging.info(f"[user]:{username} -- login success")
                return session
            else:
                logging.info(f"[user]:{username} -- login fail")
        except:
            logging.info(f"[user]:{username} -- login fail")
            logging.info(traceback.format_exc())
        


if __name__ == "__main__":
    login = Loginer()
    login.login()
