import argparse
import configparser
import logging
from typing import List

import Checkftqq
import Crawling
import dataDisplay


def setup_logging(level: int = logging.WARNING):
    logging.basicConfig(
        filename = "app.log",
        level = level,
        format = '%(levelname)s %(asctime)s "%(filename)s" %(funcName)s() : %(message)s',
        encoding = "utf-8",
    )


def process_desp_str(data_process):
    """
    该函数用于生成一段描述字符串，并返回该字符串。

    :param data_process: 包含所需信息的字典。
    :type data_process: dict
    :return: 描述字符串。
    :rtype: str
    """
    desp_str_process = '## [{title}]({href})\n\n#### 时间：{time}\n\n#### 来源：[{task_name}]({task_url})\n\n'.format(
        title = data_process["title"],
        href = data_process["href"],
        time = data_process["time"],
        task_name = data_process["task_name"],
        task_url = data_process["task_url"],
    )
    return desp_str_process


class ConfigIni:
    """
    读取配置文件，获取日志级别和ServerChan对象列表。

    :param config_file: 配置文件路径。
    """

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file, encoding = "utf-8")

    def get_default(self, item: str) -> int:
        """
        获取日志级别。

        :return: 日志级别。
        """
        level_str = self.config.get('DEFAULT', item)
        return self.process_log_level(level_str)

    @staticmethod
    def process_log_level(level_str: str) -> int:
        level_dict = {
            'CRITICAL': logging.CRITICAL,
            'FATAL': logging.CRITICAL,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'WARN': logging.WARNING,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'NOTSET': logging.NOTSET
        }
        return level_dict.get(level_str, logging.NOTSET)

    def get_checkftqq_section(self) -> List[Checkftqq.ServerChan]:
        """
        获取ServerChan对象列表。

        :return: ServerChan对象列表。
        """
        servers: List[Checkftqq.ServerChan] = []
        for section in self.config.sections():
            ScKey = self.config.get(section, 'ScKey')
            Uid = self.config.get(section, 'Uid', fallback = None)
            server = Checkftqq.ServerChan(ScKey = ScKey, Uid = Uid)
            servers.append(server)
        return servers


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description = '命令行参数解析')
    parser.add_argument('-l', '--log', action = 'store', help = '日志等级，默认按照config文件设置')
    parser.add_argument('--debug', action = 'store_true', help = '启用调试模式，默认则按照config文件设置')
    parser.add_argument('-c', '--check', action = 'store_true', help = '启用Check酱推送')
    args = parser.parse_args()

    # 载入配置文件
    e_config = ConfigIni("config.ini")
    e_website_manager = Crawling.WebsiteManager("websites.json")
    e_data_manager = Crawling.DataManager("data.json")

    # 配置日志文件
    if args.log:
        setup_logging(ConfigIni.process_log_level(args.log))
    else:
        setup_logging(e_config.get_default("LOG_LEVEL"))

    # 对象实例化
    e_crawler = Crawling.WebCrawler()
    e_article_manager = Crawling.ArticleManager()

    # 获取文章
    e_crawler.crawl_Website_list(e_website_manager.Website_list)
    e_article_manager.add_article_list(e_crawler.origin_data)

    # Check酱
    datas = e_data_manager.exclude_duplicate(e_article_manager.process_data_sort(False))
    if args.check:
        Check_Chans = e_config.get_checkftqq_section()
        for data in datas:
            desp_str = process_desp_str(data)
            for Check_Chan in Check_Chans:
                Check_Chan.send_push(title = data["title"], desp = desp_str, short = data["time"])
    else:
        for data in datas:
            desp_str = process_desp_str(data)
            print(desp_str)

    # 保存到data.json中
    e_data_manager.save_articles(e_article_manager.articles)

    # 使用HTMLGenerator类生成html文件
    generator = dataDisplay.HTMLGenerator("data.json", "template.html", "index.html")
    generator.convert_html()

    # 运行日志
    logging.info("Run Once.")
