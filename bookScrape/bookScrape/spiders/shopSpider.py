import scrapy
from bookScrape.items import ShopItem

class ShopspiderSpider(scrapy.Spider):
    name = "shopSpider"
    allowed_domains = ["librarius.md", "www.librarius.md"]
    start_urls = ["https://librarius.md/ro/points-of-sales"]


    def parse(self, response):

        shop = ShopItem()

        shopDivs = response.css("div.shop-item").getall()