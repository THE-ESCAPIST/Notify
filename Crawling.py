import json
import logging
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from retrying import retry


# # 配置日志记录器
# logging.basicConfig(
#     filename = "app.log",
#     level = logging.DEBUG,
#     format = '%(levelname)s %(asctime)s "%(filename)s" %(funcName)s() : %(message)s',
#     encoding = "utf-8",
# )


class Website:
    def __init__(self,
                 title_para_tag: str, title_para_attrs: str,
                 port_para_tag: str, port_para_attrs: str,
                 time_para_tag: str, time_para_attrs: str,
                 task_name: str, task_url: str, task_icon: str, ) -> None:
        self.title_para_tag = title_para_tag
        self.title_para_attrs = title_para_attrs
        self.port_para_tag = port_para_tag
        self.port_para_attrs = port_para_attrs
        self.time_para_tag = time_para_tag
        self.time_para_attrs = time_para_attrs
        self.task_name = task_name
        self.task_url = task_url
        self.task_icon = task_icon


class WebsiteManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.Website_list = self.load_Website()

    def load_Website(self):
        """
        该函数用于从文件中加载网站信息。

        :return: 网站列表。
        :rtype: list
        """
        try:
            with open(self.file_path, "r", encoding = "utf-8") as f:
                websites = json.load(f)
                websites = [Website(**w) for w in websites]
        except FileNotFoundError:
            logging.error(f"Open {self.file_path} : File Not Found Error")
            websites = []

        return websites


class WebCrawler:
    LINK_FINDER = "a"

    def __init__(self):
        self.origin_data = []

    def crawl_Website(self, website):
        """
        该方法用于爬取指定网站的文章，并将其加入到self.article_data中。

        :param website: 爬取目标网站的信息，包括url和需要解析的html标签等。
        :type website: Website
        :return: None
        """
        soup = self.__get_soup(website.task_url)

        for article in soup.find_all(website.port_para_tag, website.port_para_attrs):
            for link in article.find_all(website.title_para_tag, website.title_para_attrs):
                origin_data = self.__process_link(link, website)

                if origin_data is None:
                    continue
                self.origin_data.append(origin_data)

    def crawl_Website_list(self, websites):
        """
        该函数用于获取当前 websites 列表中website下的文章添加进self.article_data中。

        :param websites: 包含需要爬取的网站链接的列表。
        :type websites: list
        """
        for website in websites:
            self.crawl_Website(website)

    @staticmethod
    @retry(wait_fixed=5000, stop_max_attempt_number=3)
    def __get_soup(url):
        """
        该函数用于获取网页的 BeautifulSoup 对象。

        :param url: 网页链接。
        :type url: str
        :return: BeautifulSoup 对象。
        :rtype: BeautifulSoup
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            response.encoding = "utf-8"
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            raise e
        except Exception as e:
            logging.error(f"Error: {e}")
            raise e

    def __process_link(self, link, website):
        """
        从文章中提取数据并返回一个包含文章数据的字典。

        :param link: 文章链接。
        :type link: bs4.element.Tag
        :param website: 网站信息。
        :type website: Website
        :return: 包含文章数据的字典。
        :rtype: dict
        """
        if link is None:
            return None

        title = link.find(self.LINK_FINDER)["title"]
        href = link.find(self.LINK_FINDER)["href"]
        href = self.__process_href(href, website.task_url)
        time = link.find(website.time_para_tag, website.time_para_attrs).text

        return {
            "task_name": website.task_name,
            "task_url": website.task_url,
            "task_icon": website.task_icon,
            "crawling_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "time": time,
            "href": href,
        }

    @staticmethod
    def __process_href(href, task_url):
        """
        将给定的链接处理为完整的URL。

        :param href: 待处理的链接。
        :type href: str
        :param task_url: 当前任务的URL。
        :type task_url: str
        :return: 完整的URL。
        :rtype: str
        """
        if href.startswith("http"):
            return href
        else:
            return "{uri.scheme}://{uri.netloc}".format(uri = urlparse(task_url)) + href


class ArticleManager:
    def __init__(self):
        # 存储文章数据的列表
        self.articles = []

    def add_article(self, article):
        """
        将不存在的新文章添加到文章数据列表中

        :param article: 包含文章数据的字典。
        :type article: dict
        """
        if not self.is_article_exists(article["title"], article["time"]):
            self.articles.append(article)
            logging.debug(f"Added new article to manager: {article['title']}")

    def add_article_list(self, articles):
        """
        用articles列表调用add_article()函数，将每篇文章加入到网站对象的articles列表中。

        :param articles: 包含多篇文章的列表。
        :type articles: list
        :return: None
        """
        for article in articles:
            self.add_article(article)

    def is_article_exists(self, title, time):
        """
        判断一篇文章是否已经存在于网站对象的文章数据列表中。

        :param title: 文章标题。
        :type title: str
        :param time: 文章发布时间。
        :type time: str
        :return: 如果文章已存在，返回True，否则返回False。
        :rtype: bool
        """
        for article in self.articles:
            if article["title"] == title and article["time"] == time:
                return True
        return False

    def process_data_sort(self, is_reverse: bool = True):
        """
        获取所有已存储的文章并按时间倒序排序

        :param is_reverse: 是否按时间正序排序，默认为True，即按时间倒序排序。
        :type is_reverse: bool
        :return: 排序后的文章列表。
        :rtype: list
        """
        self.articles.sort(key = lambda x: x["time"], reverse = is_reverse)
        return self.articles


class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        """
        从本地文件中加载已有数据，并返回一个包含已有数据的列表。

        :return: 包含已有数据的列表。
        :rtype: list
        :raises FileNotFoundError: 如果文件不存在，则抛出FileNotFoundError异常。
        :raises json.decoder.JSONDecodeError: 如果文件为空或JSON格式无效，则抛出json.decoder.JSONDecodeError异常。
        :raises Exception: 如果发生其他异常，则抛出该异常。
        """
        try:
            with open(self.file_path, "r", encoding = "utf-8") as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = []
            logging.warning(f"Open {self.file_path}: File Not Found Error")
        except json.decoder.JSONDecodeError:
            existing_data = []
            logging.warning(f"Open {self.file_path}: Empty file or invalid JSON")
        except Exception as e:
            logging.error(f"Open {self.file_path}: {e}")
            raise
        return existing_data

    def save_articles(self, articles):
        """
        去除articles重复后保存文章

        :param articles: 包含文章数据的列表。
        :type articles: list
        :return: None
        """
        existing_data = self.load_data()
        new_data = self.exclude_duplicate(articles)
        len_new_data = len(new_data)
        new_data.extend(existing_data)
        self.__write_data(new_data)

        if len_new_data > 0:
            logging.info(f"Added {len_new_data} new articles to {self.file_path}")
        else:
            logging.debug(f"No new articles added to {self.file_path}")

    def __write_data(self, data):
        """
        将数据写入文件。

        :param data: 要写入的数据。
        :type data: list
        """
        try:
            with open(self.file_path, "w+", encoding = "utf-8") as f:
                json.dump(data, f, ensure_ascii = False, indent = 4)
        except PermissionError:
            logging.error("no write permission")
        except Exception as e:
            logging.error(f"open wrong: {e}")

    def exclude_duplicate(self, articles):
        """
        去除articles中与已有数据重复的文章。

        :param articles: 包含文章数据的列表。
        :type articles: list
        :return: 去除重复项后的文章数据列表。
        :rtype: list
        """
        existing_data = self.load_data()
        existing_set = {(d["href"], d["title"]) for d in existing_data}

        def is_duplicate(x):
            return (x["href"], x["title"]) in existing_set

        new_articles = list(filter(lambda x: not is_duplicate(x), articles))
        # if not new_articles:
        #     return existing_data, 0
        # existing_set.update((article["href"], article["title"]) for article in new_articles)

        new_articles.sort(key = lambda x: x["time"], reverse = True)
        return new_articles
