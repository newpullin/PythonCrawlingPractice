import re
import urllib
import urllib.request
import itertools
from urllib import robotparser
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib.parse import urljoin
from crawler.Throttle import Throttle


def download(url, user_agent='wswp', num_retries=2, charset='utf-8', proxy=None):
    print('Downloading:', url)

    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)

    try:
        if proxy:
            proxy_support = urllib.request.ProxyHandler({'http':proxy})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)
        resp = urllib.request.urlopen(request)
        cs = resp.headers.get_content_charset()
        if not cs:
            cs = charset

        html = urllib.request.urlopen(request).read().decode(cs)
    except (URLError, HTTPError, ContentTooShortError) as e:
        print('Download error:' , e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, num_retries-1)

    return html


def crawl_sitemap(url):
    sitemap = download(url)
    links = re.findall('<loc>(.*?)</loc>', sitemap)

    for link in links:
        html = download(link)

def crawl_site(url, max_errors=5):
    num_errors = 0
    for page in itertools.count(1):
        pg_url = f"{url}{page}"
        html = download(pg_url)
        if html is None:
            num_errors += 1
            if num_errors == max_errors:
                break

def get_links(html):
    """html에서 링크 목록을 리턴한다."""
    webpage_Regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)

    return webpage_Regex.findall(html)


def link_crawler(start_url , link_regex, robots_url=None, user_agent='wswp', max_depth=4, delay=5):
    """
    지정된 시작 URL 에서 link_regex와 일치하는 링크를 크롤링한다.
    :param start_url:str
    :param link_regex: str
    :return: void
    """
    crawl_queue = [start_url]
    #이전에 본 것인지 확인
    seen = {}
    throttle = Throttle(delay)
    if not robots_url:
        robots_url = f"{start_url}/robots.txt"
    rp = get_robots_parser(robots_url)

    while crawl_queue:
        url = crawl_queue.pop()
        if rp.can_fetch(user_agent, url):
            depth = seen.get(url, 0)
            if depth == max_depth:
                print(f"Skipping {url} due to depth")
                continue

            throttle.wait(url)
            html = download(url)

            if html is None:
                continue
            for link in get_links(html):
                if re.match(link_regex, link):
                    abs_link = urljoin(start_url, link)
                    if abs_link not in seen:
                        seen[abs_link] = depth + 1
                        crawl_queue.append(abs_link)
        else:
            print("Blocked by robots.txt", url)


def get_robots_parser(robots_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()

    return rp

link_regex = '.*/(index|view)/.*'
start_url = 'http://example.webscraping.com'
link_crawler(start_url, link_regex, max_depth=3)