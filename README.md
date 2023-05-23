# Notify

## 介绍

该项目能够自动获取多个网站上的文章信息，将其保存为本地的json文件，将获取到的数据保存到本地文件，对文章进行排重、排序、生成HTML文件等操作。

同时支持通过 Check 酱推送新文章通知。

## 安装

### 通过仓库获取

1. 克隆仓库到本地

   ```
   git clone https://github.com/escap/Notify.git
   ```

2. 安装依赖

   ```
   pip install -r requirements.txt
   ```

### 获取可执行文件

在[Release](https://github.com/esclm/Notify/releases)下载可执行文件

## 使用

1. 配置文件

   在 `config.ini` 中配置相关默认参数，如日志等级、Check 酱推送等。

   在代码根目录下创建config.ini文件，如不创建可直接执行程序生成默认配置
   
   可按照以下格式进行配置：

   ```ini
   [DEFAULT]
   LOG_LEVEL = WARNING
   DEBUG_LEVEL = False

   [Checkftqq1]
   SCKEY = SCTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Uid = xxxxx

   [Checkftqq2]
   SCKEY = SCTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Uid = xxxxx
   ```

   - LOG_LEVEL为日志等级，可选值为DEBUG, INFO, WARNING, ERROR, CRITICAL
   - DEBUG_LEVEL为调试模式开关，开启时为True，否则为False
   - SCKEY、Uid为Server酱的SCKEY和Uid，可多账号同时使用，如不填则不可用

2. 填写需要获取文章的网站列表

   在 `websites.json` 中添加需要获取的网站，包括网站名称、网址、文章列表页地址、文章详情页地址规则等。

   选项空白模板：

   ```json
   [
      {
         "port_para_tag": "",
         "port_para_attrs": {
            "class": ""
         },
         "title_para_tag": "",
         "title_para_attrs": {},
         "time_para_tag": "",
         "time_para_attrs": {
            "class": ""
         },
         "task_name": "",
         "task_url": "",
         "task_icon": ""
      },
      {
      }
   ]
   ```

3. 运行

   1. 通过仓库获取

      ```
      python main.py [-h] [-l LOG] [--debug] [-c]
      ```

   2. 获取可执行文件

      ```
      Notify [-h] [-l LOG] [--debug] [-c]
      ```

      ```
      Notifyw [-l LOG] [--debug] [-c]
      ```

   可以使用以下命令行参数：

   - `-h`：显示帮助信息，使用Notifyw的可执行文件时不能使用
   - `-l LOG` 或 `--log LOG`：设置日志等级，可选值为 `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`
   - `--debug`：启用调试模式
   - `-c` 或 `--check`：启用Check酱推送

4. 查看结果

   获取到的数据会保存到 `datas/data.json` 文件中
   
   同时会生成一个 HTML 文件 `index.html`，包含了所有获取到的文章信息。

   如果启用了Check酱推送，则程序会将最新获取的文章通过Check酱上发送；
   否则会将最新爬取的文章输出到控制台。


## 注意事项

- 本程序仅用于学习和研究使用，请勿用于商业用途。
- Check酱是一个免费的微信推送服务，需要在`config.ini`中配置SCKEY才能使用。
- 可以通过修改`resourse/template.html`文件来自定义生成的网页样式。

## 维护者

[@escap](https://github.com/esclm)

## 如何贡献

非常欢迎你的加入！[提一个 Issue](https://github.com/esclm/Notify/issues/new) 或者提交一个 Pull Request。

在提交 PR 前，请确保你的代码风格与项目保持一致，并通过所有测试。

## 使用许可

[LGPL](LICENSE) © escap
