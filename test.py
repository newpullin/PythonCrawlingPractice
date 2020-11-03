import re
import urllib
import urllib.request
import time
import itertools
from urllib import robotparser
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib.parse import urljoin


def download(url, user_agent='wswp', num_retries=2):
    print('Downloading:', url)

    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)

    try:
        html = urllib.request.urlopen(request).read()
    except (URLError, HTTPError, ContentTooShortError) as e:
        print('Download error:' , e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, num_retries-1)

    return html


def crawl_sitemap(url):
    sitemap = download(url)
    sitemap = sitemap.decode('utf-8')
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


def link_crawler(start_url , link_regex, robots_url=None, user_agent='wswp'):
    """
    지정된 시작 URL 에서 link_regex와 일치하는 링크를 크롤링한다.
    :param start_url:str
    :param link_regex: str
    :return: void
    """
    crawl_queue = [start_url]
    #이전에 본 것인지 확인
    seen = set(crawl_queue)

    if not robots_url:
        robots_url = f"{start_url}/robots.txt"
    rp = get_robots_parser(robots_url)

    while crawl_queue:
        url = crawl_queue.pop()
        if rp.can_fetch(user_agent, url):
            time.sleep(5)
            html = download(url)

            if html is None:
                continue
            html = html.decode('utf-8')
            for link in get_links(html):
                if re.match(link_regex, link):
                    abs_link = urljoin(start_url, link)
                    if abs_link not in seen:
                        seen.add(abs_link)
                        crawl_queue.append(abs_link)
        else:
            print("Blocked by robots.txt", url)


def get_robots_parser(robots_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()

    return rp

link_crawler('http://example.webscraping.com', '.*/(index|view)/.*', user_agent='BadCrawler')