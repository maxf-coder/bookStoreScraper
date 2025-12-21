import random
import requests
from scrapy.http import HtmlResponse
from configs import scrapingLogger
from twisted.internet import defer
import treq


class ScrapeOpsHeadersMiddleware:

    def __init__(self, api_key, num_results):
        self.headers_pool = []
        self.api_key = api_key
        self.num_results = num_results

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get("SCRAPEOPS_API_KEY")
        num_results = crawler.settings.getint("SCRAPEOPS_NUM_RESULTS", 50)

        if not api_key:
            raise RuntimeError("SCRAPEOPS_API_KEY missing")
        
        mw = cls(api_key, num_results)
        mw._load_headers()
        return mw
    
    def _load_headers(self):

        r = requests.get(
            "https://headers.scrapeops.io/v1/browser-headers",
            params={
                "api_key": self.api_key,
                "num_results": self.num_results
            },
            timeout=10
        )

        if r.status_code != 200:
            raise RuntimeError("Scrapeops headers API failed")
        
        data = r.json().get("result")
        if not data:
            raise RuntimeError("Empty headers list from ScrapeOps")
        
        self.headers_pool = data

    def process_request(self, request, spider):
        headers = random.choice(self.headers_pool)
        for k,v in headers.items():
            request.headers[k] = v


class ScrapeOpsProxyFallbackMiddleware:

    def __init__(self, api_key):
        self.api_key = api_key

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get("SCRAPEOPS_API_KEY")
        if not api_key:
            raise RuntimeError("SCRAPEOPS_API_KEY missing")
        return cls(api_key)

    def process_response(self, request, response, spider):
        if response.status not in (403, 429):
            return response

        scrapingLogger.warning(f"Blocked ({response.status}), retry via scrapeops: {request.url}")

        proxy_url = f'https://proxy.scrapeops.io/v1/?api_key={self.api_key}&url={request.url}'

        d = treq.get(proxy_url)

        def cb(resp):
            return treq.content(resp)

        def cb2(body):
            return HtmlResponse(
                url=request.url,
                body=body,
                encoding="utf-8",
                request=request
            )

        def eb(failure):
            spider.logger.warning(f"ScrapeOps proxy failed: {failure}")
            return response

        d.addCallback(cb)
        d.addCallback(cb2)
        d.addErrback(eb)

        return d