import base64
import hashlib
from typing import Optional, Union

import requests


class ServerChan:
    DEFAULT_CHANNEL = 66  # 默认消息通道
    API_URL = "https://sctapi.ftqq.com/"  # API URL
    ENCRYPT_IV_PREFIX = "SCT"  # 端对端加密IV前缀

    def __init__(self, ScKey: str, Uid: str = None):
        """
        初始化ServerChan实例

        :param ScKey: ServerChan的SCKEY
        :param Uid: 用户ID，选填
        """
        self.ScKey = ScKey
        self.Uid = Uid

    def send_push(self, title: str, desp: Optional[str] = None, short: Optional[str] = None,
                  channel: Optional[Union[int, str]] = None, openid: Optional[str] = None,
                  encrypted: bool = False, key: Optional[str] = None) -> requests.Response:
        """
        发起推送

        :param title: 消息标题
        :param desp: 消息内容
        :param short: 消息卡片内容，选填
        :param channel: 动态指定本次推送使用的消息通道，选填
        :param openid: 消息抄送的openid，选填
        :param encrypted: 是否启用端对端加密，默认否
        :param key: 阅读时输入的密码
        :return: requests.Response对象
        """
        url = f"{self.API_URL}{self.ScKey}.send"
        data = {
            "title": title,
            "desp": desp,
            "short": short,
            "channel": channel or self.DEFAULT_CHANNEL,
            "openid": openid
        }

        if encrypted and key and self.Uid:
            data["desp"] = self.encrypt_content(desp, key, self.ENCRYPT_IV_PREFIX + self.Uid)
            data["encoded"] = 1

        return requests.post(url, json = data)

    def query_push_status(self, push_id: str, read_key: str) -> requests.Response:
        """
        查询推送状态

        :param push_id: 推送ID
        :param read_key: 阅读密钥
        :return: requests.Response对象
        """
        url = f"{self.API_URL}push?id={push_id}&readkey={read_key}"
        return requests.get(url)

    @staticmethod
    def encrypt_content(content: str, key: str, iv: str) -> str:
        """
        端对端加密

        :param content: 待加密内容
        :param key: 密钥
        :param iv: 加密向量
        :return: 加密后的字符串
        """
        key = hashlib.md5(key.encode('utf-8')).hexdigest()[:16].encode('utf-8')
        iv = hashlib.md5(iv.encode('utf-8')).hexdigest()[:16].encode('utf-8')

        cipher = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        return cipher
