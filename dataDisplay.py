from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from Crawling import DataManager


class HTMLGenerator:
    def __init__(self, data_file_path, template_file_path, output_file_path):
        """
        初始化HTMLGenerator类

        :param data_file_path: 数据文件路径
        :param template_file_path: 模板文件路径
        :param output_file_path: 输出文件路径
        """
        self.data_manager = DataManager(data_file_path)
        self.data = self.data_manager.load_data()
        self.template_path = template_file_path
        self.output_path = output_file_path

    def convert_html(self):
        """
        生成html文件

        :return: 无返回值
        """
        html = self.generate_html_from_template()
        self.__save_to_file(html)

    def generate_html_from_template(self):
        """
        从模板中渲染数据生成html

        :return: html字符串
        """
        env = Environment(loader = FileSystemLoader("."))
        template = env.get_template(self.template_path)
        html = template.render(data = self.data, datetime = datetime)
        return html

    def __save_to_file(self, data):
        """
        将生成的html文件保存到本地

        :param data: html字符串
        :return: 无返回值
        """
        with open(self.output_path, "w", encoding = "utf-8") as f:
            f.write(data)
