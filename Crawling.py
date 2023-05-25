import json
import logging
from datetime import datetime
from urllib.parse import urljoin

import chardet
import requests
from bs4 import BeautifulSoup
from retrying import retry


class Website:
    def __init__(self,
                 title_selector: str, href_selector: str, time_selector: str,
                 task_name: str, task_url: str, task_icon: str, ) -> None:
        self.title_selector = title_selector
        self.href_selector = href_selector
        self.time_selector = time_selector
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

        origin_datas = self.__process_website_data(soup, website)

        if not len(origin_datas):
            return
        for origin_data in origin_datas:
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
    @retry(wait_fixed = 5000, stop_max_attempt_number = 3)
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
            response.encoding = chardet.detect(response.content)["encoding"]
            return BeautifulSoup(response.text, "html5lib")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            raise e
        except Exception as e:
            logging.error(f"Error: {e}")
            raise e

    def __process_website_data(self, soup, website):
        """
        处理网站数据

        :param soup: BeautifulSoup对象
        :param website: Website对象
        :return: 包含所有数据的列表
        """
        if soup is None:
            return []

        titles = self.__process_titles(soup, website.title_selector)
        hrefs = self.__process_hrefs(soup, website.href_selector, website.task_url)
        times = self.__process_times(soup, website.time_selector)

        results = []
        for title, href, time in zip(titles, hrefs, times):
            result = {
                "task_name": website.task_name,
                "task_url": website.task_url,
                "task_icon": website.task_icon,
                "crawling_time": self.__format_time(),
                "title": title,
                "time": time,
                "href": href,
            }
            results.append(result)

        return results

    @staticmethod
    def __process_titles(soup, selector):
        """
        处理标题数据

        :param soup: BeautifulSoup对象
        :param selector: 标题选择器
        :return: 标题文本列表
        """
        return [title.text.strip() for title in soup.select(selector)]

    def __process_hrefs(self, soup, selector, base_url):
        """
        处理链接数据

        :param soup: BeautifulSoup对象
        :param selector: 链接选择器
        :param base_url: 网站基础链接
        :return: 链接列表
        """
        hrefs = soup.select(selector)
        return [self.__process_href(href, base_url) for href in hrefs]

    @staticmethod
    def __process_href(href, base_url):
        """
        处理单个链接数据

        :param href: 链接对象
        :param base_url: 网站基础链接
        :return: 处理后的链接
        """
        return urljoin(base_url, href.get('href'))

    @staticmethod
    def __process_times(soup, selector):
        """
        处理时间数据

        :param soup: BeautifulSoup对象
        :param selector: 时间选择器
        :return: 时间文本列表
        """
        return [time.text.strip() for time in soup.select(selector)]

    @staticmethod
    def __format_time():
        """
        格式化时间

        :return: 格式化后的时间字符串
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ArticleManager:
    def __init__(self):
        # 存储文章数据的列表
        self.articles = []

    def add_article_to_list(self, article):
        """
        将不存在的新文章添加到文章数据列表中

        :param article: 包含文章数据的字典。
        :type article: dict
        """
        if not self.is_article_exists(article["title"], article["time"]):
            self.articles.append(article)
            logging.debug(f"Added new article to manager: {article['title']}")

    def add_articles_to_list(self, articles):
        """
        用articles列表调用add_article()函数，将每篇文章加入到网站对象的articles列表中。

        :param articles: 包含多篇文章的列表。
        :type articles: list
        :return: None
        """
        for article in articles:
            self.add_article_to_list(article)

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

    def process_data_add_name(self, addition):
        """
        为每一项添加前缀

        :param addition: 所需添加的前缀
        :return: None
        """
        for i in range(len(self.articles)):
            self.articles[i]['task_name'] = addition + '-' + self.articles[i]['task_name']


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
        去除articles重复后排序并保存文章

        :param articles: 包含文章数据的列表。
        :type articles: list
        :return: None
        """
        existing_data = self.load_data()
        new_data = self.exclude_duplicate(articles)
        len_new_data = len(new_data)
        new_data.extend(existing_data)
        new_data.sort(key = lambda x: x["time"], reverse = True)
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
