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
最好的学习方式是使用一个shell, Scrapy shell来学习如何提取数据。Run:
`scrapy shell 'http://quotes.toscrape.com/page/1/'`
结果是：

```
...
s] Available Scrapy objects:
[s]   scrapy     scrapy module (contains scrapy.Request, scrapy.Selector, etc)
[s]   crawler    <scrapy.crawler.Crawler object at 0x1028054e0>
[s]   item       {}
[s]   request    <GET http://quotes.toscrape.com/page/1/>
[s]   response   <200 http://quotes.toscrape.com/page/1/>
[s]   settings   <scrapy.settings.Settings object at 0x10362d550>
[s]   spider     <DefaultSpider 'default' at 0x1038fa198>
[s] Useful shortcuts:
[s]   fetch(url[, redirect=True]) Fetch URL and update local objects (by default, redirects are followed)
[s]   fetch(req)                  Fetch a scrapy.Request and update local objects
[s]   shelp()           Shell help (print this help)
[s]   view(response)    View response in a browser
```
使用shell，你可以对返回的数据使用selecting elements 通过用CSS筛选:

```python
In [4]: response.css('title')
Out[4]: [<Selector xpath='descendant-or-self::title' data='<title>Quotes to Scrape</title>'>]
```
```python
In [2]: response.css('title::text').extract()
Out[2]: ['Quotes to Scrape']
```


#### XPath: a brief intro
Besides CSS, Scrapy selectors also support using XPath expressions:

```ipython
In [6]: response.xpath('//title')
Out[6]: [<Selector xpath='//title' data='<title>Quotes to Scrape</title>'>]

In [7]: response.xpath('//title').extract_first()
Out[7]: '<title>Quotes to Scrape</title>'

In [8]: response.xpath('//title/text()').extract_first()
Out[8]: 'Quotes to Scrape'
```
XPath expressions are very powerful, and are the foundation of Scrapy Selectors. In fact, CSS selectors are converted to XPath under-the-hood. You can see that if you read closely the text representation of the selector objects in the shell.

While perhaps not as popular as CSS selectors, XPath expressions offer more power because besides navigating the structure, it can also look at the content. Using XPath, you’re able to select things like: select the link that contains the text “Next Page”. This makes XPath very fitting to the task of scraping, and we encourage you to learn XPath even if you already know how to construct CSS selectors, it will make scraping much easier.

We won’t cover much of XPath here, but you can read more about [using XPath with Scrapy Selectors here](https://doc.scrapy.org/en/latest/topics/selectors.html#topics-selectors). To learn more about XPath, we recommend [this tutorial to learn XPath through examples](http://zvon.org/comp/r/tut-XPath_1.html), and [this tutorial to learn “how to think in XPath”](http://plasmasturm.org/log/xpath101/).

#### Extracting quotes and authors
Now that you know a bit about selection and extraction, let’s complete our spider by writing the code to extract the quotes from the web page.
Each quote in http://quotes.toscrape.com is represented by HTML elements that look like this:

```html
<div class="quote">
    <span class="text">“The world as we have created it is a process of our
    thinking. It cannot be changed without changing our thinking.”</span>
    <span>
        by <small class="author">Albert Einstein</small>
        <a href="/author/Albert-Einstein">(about)</a>
    </span>
    <div class="tags">
        Tags:
        <a class="tag" href="/tag/change/page/1/">change</a>
        <a class="tag" href="/tag/deep-thoughts/page/1/">deep-thoughts</a>
        <a class="tag" href="/tag/thinking/page/1/">thinking</a>
        <a class="tag" href="/tag/world/page/1/">world</a>
    </div>
</div>
```

Let’s open up scrapy shell and play a bit to find out how to extract the data we want:
`scrapy shell 'http://quotes.toscrape.com'`
We get a list of selectors for the quote HTML elements with:
`response.css("div.quote")`

Now, let’s extract title, author and the tags from that quote using the quote object we just created:
```
title = quote.css("span.text::text").extract_first()
title
'“The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”'
 author = quote.css("small.author::text").extract_first()
author
'Albert Einstein'
```
Given that the tags are a list of strings, we can use the .extract() method to get all of them:

```
tags = quote.css("div.tags a.tag::text").extract()
tags
['change', 'deep-thoughts', 'thinking', 'world']
```
Having figured out how to extract each bit, we can now iterate over all the quotes elements and put them together into a Python dictionary:

```
for quote in response.css("div.quote"):
...     text = quote.css("span.text::text").extract_first()
...     author = quote.css("small.author::text").extract_first()
...     tags = quote.css("div.tags a.tag::text").extract()
...     print(dict(text=text, author=author, tags=tags))
{'tags': ['change', 'deep-thoughts', 'thinking', 'world'], 'author': 'Albert Einstein', 'text': '“The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”'}
{'tags': ['abilities', 'choices'], 'author': 'J.K. Rowling', 'text': '“It is our choices, Harry, that show what we truly are, far more than our abilities.”'}
    ... a few more of these, omitted for brevity
```

#### Extracting data in our spider
Let’s get back to our spider. Until now, it doesn’t extract any data in particular, just saves the whole HTML page to a local file. Let’s integrate the extraction logic above into our spider.
A Scrapy spider typically generates many dictionaries containing the data extracted from the page. To do that, we use the **yield** Python keyword in the callback, as you can see below:

```python
import scrapy
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
```
If you run this spider, it will output the extracted data with the log:

```
{'tags': ['life', 'love'], 'author': 'André Gide', 'text': '“It is better to be hated for what you are than to be loved for what you are not.”'}
2016-09-19 18:57:19 [scrapy.core.scraper] DEBUG: Scraped from <200 http://quotes.toscrape.com/page/1/>
{'tags': ['edison', 'failure', 'inspirational', 'paraphrased'], 'author': 'Thomas A. Edison', 'text': "“I have not failed. I've just found 10,000 ways that won't work.”
```
### Storing the scraped data
The simplest way to store the scraped data is by using [Feed exports](https://doc.scrapy.org/en/latest/topics/feed-exports.html#topics-feed-exports), with the following command:
`scrapy crawl quotes -o quotes.json`
That will generate an q**uotes.json** file containing all scraped items, serialized in JSON.
For historic reasons, Scrapy appends to a given file instead of overwriting its contents. If you run this command twice without removing the file before the second time, you’ll end up with a broken JSON file.
You can also use other formats, like JSON Lines:
`scrapy crawl quotes -o quotes.jl`
The JSON Lines format is useful because it’s stream-like, you can easily append new records to it. It doesn’t have the same problem of JSON when you run twice. Also, as each record is a separate line, you can process big files without having to fit everything in memory, there are tools like JQ to help doing that at the command-line.
In small projects (like the one in this tutorial), that should be enough. However, if you want to perform more complex things with the scraped items, you can write an [Item Pipeline](https://doc.scrapy.org/en/latest/topics/item-pipeline.html#topics-item-pipeline). A placeholder file for Item Pipelines has been set up for you when the project is created, in **tutorial/pipelines.py**. Though you don’t need to implement any item pipelines if you just want to store the scraped items.
### Following links
Let’s say, instead of just scraping the stuff from the first two pages from http://quotes.toscrape.com, you want quotes from **all** the pages in the website.
Now that you know how to extract data from pages, let’s see how to follow links from them.
First thing is to **extract the link to the page we want to follow**. Examining our page, we can see there is a link to the next page with the following markup:

```html5
<ul class="pager">
    <li class="next">
        <a href="/page/2/">Next <span aria-hidden="true">&rarr;</span></a>
    </li>
</ul>
```
We can try extracting it in the shell:

```
In [3]: response.css('li.next a').extract_first()
Out[3]: '<a href="/page/2/">Next <span aria-hidden="true">→</span></a>'
In [2]: response.css('li.next a::attr(href)').extract_first()
Out[2]: '/page/2
```
Let’s see now our spider modified to recursively follow the link to the next page, extracting data from it:

```python
# version4 add follow link
import scrapy
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]
    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)
```
Now, after extracting the data, the `parse()` method looks for the link to the next page, builds a full absolute URL using the `urljoin()` method (since the links can be relative) and yields a new request to the next page, registering itself as callback to handle the data extraction for the next page and to keep the crawling going through all the pages.
What you see here is Scrapy’s mechanism of following links: when you yield a Request in a callback method, Scrapy will schedule that request to be sent and register a callback method to be executed when that request finishes.
Using this, you can build complex crawlers that follow links according to rules you define, and extract different kinds of data depending on the page it’s visiting.
In our example, it creates a sort of loop, following all the links to the next page until it doesn’t find one – handy for crawling blogs, forums and other sites with pagination.
#### A shortcut for creating Requests
As a shortcut for creating Request objects you can use `response.follow`:

```python
import scrapy
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('span small::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }

        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
```
Unlike `scrapy.Request`, `response.follow` supports relative URLs directly - no need to call `urljoin`. Note that `response.follow` just returns a Request instance; you still have to yield this Request.
You can also pass a selector to `response.follow` instead of a string; this selector should extract necessary attributes:

```python
for href in response.css('li.next a::attr(href)'):
    yield response.follow(href, callback=self.parse)
```
For `<a>` elements there is a shortcut: response.follow uses their href attribute automatically. So the code can be shortened further:

```python
for a in response.css('li.next a'):
    yield response.follow(a, callback=self.parse)
```
#### More examples and patterns
Here is another spider that illustrates callbacks and following links, this time for scraping author information:

```python
import scrapy
class AuthorSpider(scrapy.Spider):
    name = 'author'
    start_urls = ['http://quotes.toscrape.com/']
    def parse(self, response):
        # follow links to author pages
        for href in response.css('.author + a::attr(href)'):
            yield response.follow(href, self.parse_author)

        # follow pagination links
        for href in response.css('li.next a::attr(href)'):
            yield response.follow(href, self.parse)

    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()
        yield {
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('.author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }
```
This spider will start from the main page, it will follow all the links to the authors pages calling the `parse_author` callback for each of them, and also the pagination links with the `parse` callback as we saw before.
Here we’re passing callbacks to `response.follow` as positional arguments to make the code shorter; it also works for `scrapy.Request`.
The `parse_author` callback defines a helper function to extract and cleanup the data from a CSS query and yields the Python dict with the author data.
Another interesting thing this spider demonstrates is that, even if there are many quotes from the same author, we don’t need to worry about visiting the same author page multiple times. By default, Scrapy filters out duplicated requests to URLs already visited, avoiding the problem of hitting servers too much because of a programming mistake. This can be configured by the setting `DUPEFILTER_CLASS`.
Hopefully by now you have a good understanding of how to use the mechanism of following links and callbacks with Scrapy.
As yet another example spider that leverages the mechanism of following links, check out the `CrawlSpider` class for a generic spider that implements a small rules engine that you can use to write your crawlers on top of it.
Also, a common pattern is to build an item with data from more than one page, using a trick to pass additional data to the callbacks.
### Using spider arguments
You can provide command line arguments to your spiders by using the -a option when running them:
`scrapy crawl quotes -o quotes-humor.json -a tag=humor`
These arguments are passed to the Spider’s `__init__` method and become spider attributes by default.
In this example, the value provided for the `tag` argument will be available via `self.tag`. You can use this to make your spider fetch only quotes with a specific tag, building the URL based on the argument:

```python
import scrapy
class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        url = 'http://quotes.toscrape.com/'
        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
            }

        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
```
If you pass the `tag=humor` argument to this spider, you’ll notice that it will only visit URLs from the `humor` tag, such as `http://quotes.toscrape.com/tag/humor`
You can [learn more about handling spider arguments here.](https://doc.scrapy.org/en/latest/topics/spiders.html#spiderargs)
### Next steps

You can continue from the section [Basic concepts](https://doc.scrapy.org/en/latest/index.html#section-basics) to know more about the command-line tool, spiders, selectors and other things the tutorial hasn’t covered like modeling the scraped data. If you prefer to play with an example project, check the [Examples](https://doc.scrapy.org/en/latest/intro/examples.html#intro-examples) section.

## Examples
The best way to learn is with examples, and Scrapy is no exception. For this reason, there is an example Scrapy project named [quotesbot](https://github.com/scrapy/quotesbot), that you can use to play and learn more about Scrapy. It contains two spiders for http://quotes.toscrape.com, one using CSS selectors and another one using XPath expressions.
The quotesbot project is available at: https://github.com/scrapy/quotesbot. You can find more information about it in the project’s README.
If you’re familiar with git, you can checkout the code. Otherwise you can download the project as a zip file by clicking here.

