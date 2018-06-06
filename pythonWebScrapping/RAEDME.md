> 简介: 项目，爬虫快速学习，使用scrapy框架+beautiful soup; 抓取网页；解析html和页面

# Scrapy学习入门
# 第一步
## 初窥Scrapy
Scrapy是一个为了**爬取网站数据**，**提取结构性数据**而编写的应用框架。 可以应用在包括数据挖掘，信息处理或存储历史数据等一系列的程序中。
其最初是为了 **页面抓取** (更确切来说, **网络抓取** )所设计的， 也可以应用在获取API所返回的数据(例如 Amazon Associates Web Services ) 或者通用的网络爬虫。

### 一窥示例spider
当您需要从某个网站中获取信息，但该网站未提供API或能通过程序获取信息的机制时， Scrapy可以助你一臂之力。
一个Scrapy Spider的示例，并且以最简单的方式启动该spider。
以下的代码将跟进StackOverflow上具有投票数最多的链接，并且爬取其中的一些数据:

```python
import scrapy
class StackOverflowSpider(scrapy.Spider):
    name = 'stackoverflow'
    start_urls = ['http://stackoverflow.com/questions?sort=votes']

    def parse(self, response):
        for href in response.css('.question-summary h3 a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_question)

    def parse_question(self, response):
        yield {
            'title': response.css('h1 a::text').extract()[0],
            'votes': response.css('.question .vote-count-post::text').extract()[0],
            'body': response.css('.question .post-text').extract()[0],
            'tags': response.css('.question .post-tag::text').extract(),
            'link': response.url,
        }
```
将上述代码存入到某个文件中，以类似于 `stackoverflow_spider.py` 命名, 并且使用 `runspider` 命令运行: 
`scrapy runspider stackoverflow_spider.py -o top-stackoverflow-questions.json`
当命令执行完后，您将会得到 `top-stackoverflow-questions.json` 文件。 该文件以JSON格式保存了`StackOverflow`上获得`upvote`最多的问题， 包含了标题、链接、upvote的数目、相关的tags以及以HTML格式保存的问题内容， 看起来类似于这样(为了更容易阅读，对内容进行重新排版):

```
[{
    "body": "... LONG HTML HERE ...",
    "link": "http://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-an-unsorted-array",
    "tags": ["java", "c++", "performance", "optimization"],
    "title": "Why is processing a sorted array faster than an unsorted array?",
    "votes": "9924"
},
{
    "body": "... LONG HTML HERE ...",
    "link": "http://stackoverflow.com/questions/1260748/how-do-i-remove-a-git-submodule",
    "tags": ["git", "git-submodules"],
    "title": "How do I remove a Git submodule?",
    "votes": "1764"
},
...]
```
### 刚刚发生了什么?
当您运行 `scrapy runspider somefile.py` 命令时，`Scrapy`尝试从该文件中查找`Spider`的定义，并且在爬取引擎中运行它。

1. Scrapy首先 
    1. 读取定义在 `start_urls` 属性中的URL(在本示例中，就是`StackOverflow`的top question页面的URL)， 创建请求，
    2. 并将接收到的response作为参数调用默认的回调函数 `parse` ，来启动爬取。 
    3. 在回调函数 `parse` 中，我们使用`CSS Selector`来提取链接。
    4. 接着，我们产生(`yield`)更多的请求， 注册 `parse_question` 作为这些请求完成时的回调函数。
2. 这里，Scrapy的一个最主要的优势: `请求(request)`是 被**异步调度和处理**的 。 这意味着，Scrapy并不需要等待一个请求(request)完成及处理，在此同时， 也发送其他请求或者做些其他事情。 这也意味着，当有些请求失败或者处理过程中出现错误时，其他的请求也能继续处理。
3. 在允许您可以以非常快的速度进行爬取时(以容忍错误的方式同时发送多个request), Scrapy也通过 一些设置 来允许您控制其爬取的方式。 例如，您可以为两个request之间设置下载延迟， 限制单域名(domain)或单个IP的并发请求量，甚至可以 使用自动限制插件 来自动处理这些问题。
4. 最终， `parse_question` 回调函数从每个页面中爬取到问题(`question`)的数据并产生了一个dict， Scrapy收集并按照终端(command line)的要求将这些结果写入到了JSON文件中。
### 还有什么？
您已经了解了如何通过Scrapy提取存储网页中的信息，但这仅仅只是冰山一角。Scrapy提供了很多强大的特性来使得爬取更为简单高效, 例如:
- 对`HTML, XML`源数据 **选择及提取** 的内置支持, 提供了**CSS选择器**(selector)以及**XPath表达式**进行处理， 以及一些帮助函数(helper method)来使用**正则表达式**来提取数据.
- 提供 **交互式shell终端** , 为您测试CSS及XPath表达式，编写和调试爬虫提供了极大的方便
- 通过 **feed导出** 提供了多格式(JSON、CSV、XML)，多存储后端(FTP、S3、本地文件系统)的内置支持
- 提供了一系列在spider之间共享的可复用的过滤器(即 Item Loaders)，对智能处理爬取数据提供了内置支持。
- 针对非英语语系中不标准或者错误的编码声明, 提供了自动检测以及健壮的编码支持。
- 高扩展性。您可以通过使用 `signals` ，设计好的API(中间件, extensions, pipelines)来定制实现您的功能。
- 内置的中间件及扩展为下列功能提供了支持: **cookies and session 处理** **HTTP 压缩** **HTTP 认证** **HTTP 缓存** **user-agent模拟** **robots.txt** **爬取深度限制** **其他**
- 内置 Telnet终端 ，通过在Scrapy进程中钩入Python终端，使您可以查看并且调试爬虫
- 以及其他一些特性，例如可重用的，从 Sitemaps 及 XML/CSV feeds中爬取网站的爬虫、 可以 自动下载 爬取到的数据中的图片(或者其他资源)的media pipeline、 带缓存的DNS解析器，以及更多的特性。
## 安装指南
使用virtualenv, pip3 install scrapy
## Scrapy入门教程
我们将会scrape quotes.toscape.com; 引用名言的网站；

This tutorial will walk you through these tasks:
1. 创建一个新的Scrapy项目
2. 写一个爬虫去爬去网站和额外的数据
3. 导出数据用命令行模式
4. 根据link 递归调用爬虫
5. 运用爬虫参数
### 创建项目
在开始爬取之前，您必须创建一个新的Scrapy项目。 进入您打算存储代码的目录中，运行下列命令:
`scrapy startproject tutorial`
该命令将会创建包含下列内容的 tutorial 目录:

```
tutorial/
    scrapy.cfg            # deploy configuration file
    tutorial/             # project's Python module, you'll import your code from here
        __init__.py
        items.py          # project items definition file
        middlewares.py    # project middlewares file
        pipelines.py      # project pipelines file
        settings.py       # project settings file
        spiders/          # a directory where you'll later put your spiders
            __init__.py
```
### 定义Item
Item 是**保存爬取到的数据的容器**；其使用方法和python字典类似。虽然您也可以在Scrapy中直接使用dict，但是 Item 提供了额外保护机制来避免拼写错误导致的未定义字段错误。 They can also be used with Item Loaders, a mechanism with helpers to conveniently populate Items.

类似在ORM中做的一样，您可以通过创建一个 scrapy.Item 类， 并且定义类型为 scrapy.Field 的类属性来定义一个Item。 (如果不了解ORM, 不用担心，您会发现这个步骤非常简单)

首先根据需要从`quotes.toscape.com`获取到的数据对item进行建模。 我们需要从quotes.toscape.com中获取名字，url，以及网站的描述。 对此，在item中定义相应的字段。编辑 `tutorial` 目录中的 `items.py` 文件:

```python
import scrapy
class QuoteItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()
```
一开始这看起来可能有点复杂，但是通过定义item， 您可以很方便的使用Scrapy的其他方法。而这些方法需要知道您的item的定义。
### 编写第一个爬虫(Spider)
Spider是用户定义，编写用于从单个网站(或者一些网站)爬取数据的类。他们必须是`scrape.Spider`的子类，定义一个初始的请求，可选择是否进入页面中的链接，以及如何分析下载网页内容变成提提取数据
这个是我们第一个爬虫代码，保存为`quotes_spider.py`在`tutorial/spiders`目录下:

```python
import scrapy
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
```
我们的Spider subclass `scrapy.Spider` ，定义了一些属性和方法：
- `name`: 用于区别Spider。 该名字必须是唯一的，不可为不同的Spider设定相同的名字。
- `start_request()`: 必须返回一个可迭代的可以进行爬虫的请求url数组(你可以返回一个请求列表或者一个生成函数);后续的请求将会生成从这些初始的请求。
- `parse()`:  是spider的一个方法。 被调用时，每个初始URL完成下载后生成的 Response 对象将会作为唯一的参数传递给该函数。 该方法负责解析返回的数据(response data)，提取数据(生成item)以及生成需要进一步处理的URL的 Request 对象。parse() 经常解析数据，获取爬虫数据作为字典和找到一新的url创建新的请求。
### 爬虫
为了让爬虫工作，到顶级目录下，执行:
`scrapy crawl quotes`
这个命令将会执行我们刚加的spider with the name `quotes`，并且将会发送一些请求到`quotes.toscrape.com`， 你将会得到以下输出:

```
2018-06-06 21:48:47 [scrapy.utils.log] INFO: Scrapy 1.5.0 started (bot: tutorial)
2018-06-06 21:48:47 [scrapy.utils.log] INFO: Versions: lxml 4.2.1.0, libxml2 2.9.8, cssselect 1.0.3, parsel 1.4.0, w3lib 1.19.0, Twisted 18.4.0, Python 3.6.5 (default, Mar 30 2018, 06:41:53) - [GCC 4.2.1 Compatible Apple LLVM 9.0.0 (clang-900.0.39.2)], pyOpenSSL 18.0.0 (OpenSSL 1.1.0h  27 Mar 2018), cryptography 2.2.2, Platform Darwin-17.6.0-x86_64-i386-64bit
 .....
 'scheduler/dequeued/memory': 2,
 'scheduler/enqueued': 2,
 'scheduler/enqueued/memory': 2,
 'start_time': datetime.datetime(2018, 6, 6, 13, 48, 47, 958697)}
2018-06-06 21:48:49 [scrapy.core.engine] INFO: Spider closed (finished)
```
在项目目录下， 将会出现quotes-1.html, quotes-2.html.
### 发生过程
Scrapy调度那些 由`start_request`方法返回的`scrapy.Request`对象。根据每一个返回的Response， 它初始化了一个Response对象， 用parse作为回调函数，response作为参数。

### 一个快速start_request方法
除去实现一个`start_requests()`方法从URL来生成`scrapy.Request`对象之外，你可以直接定义一个`start_urls`类代表一系列URL。这些URL将会被执行通过默认实现的`start_requests()`来创建这个初始的请求：

```python
import scrapy
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        "http://quotes.toscrape.com/page/1/",
        "http://quotes.toscrape.com/page/2/"
    ]
    def parse(self, response):
        page = response.url.split("/")[-2]
        fileName = 'quotes-%s.html' % page
        with open(fileName, 'wb') as f:
            f.write(response.body)
```
`parse()`方法将会被唤起去操作这些URLS中每一个请求，即使我们没有详细告诉Scrapy去执行，因为这是默认回调的方法。
### Extracting Data




