from urllib.parse import urlparse
import time

class Throttle:
    """
     동일 도메인간의 다운로드 간 지연을 추가한다.
    """
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_acesssed = self.domains.get(domain)

        if self.delay > 0 and last_acesssed is not None:
            sleep_secs = self.delay - (time.time() - last_acesssed)
            if sleep_secs > 0:
                # 최근에 도메인에 접속했기 때문에
                # 기다려야 한다.
                time.sleep(sleep_secs)

        self.domains[domain] = time.time()

