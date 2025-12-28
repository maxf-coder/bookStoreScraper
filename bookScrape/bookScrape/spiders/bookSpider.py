import scrapy
from bookScrape.items import BookItem
class BookspiderSpider(scrapy.Spider):
    name = "bookSpider"
    allowed_domains = ["librarius.md", "www.librarius.md"]
    start_urls = ["https://librarius.md/ro/books/page/1"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bookScrape.pipelines.BookscrapePipeline": 300,
            "bookScrape.pipelines.SaveBookToMySQLPipeline": 400,
        }
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        max_pages = crawler.settings.get("BOOKS_MAX_PAGES", 0)
        spider.books_max_pages = int(max_pages) if max_pages is not None else 0
        return spider


    def parse(self, response):
        book_urls = response.css('div.anyproduct-card a::attr(href)').getall()

        for book_url in book_urls:
            yield response.follow(book_url, callback=self.parse_book)

        next_page_url = response.css('li.page-item.active + li.page-item a::attr(href)').get()
        if not next_page_url:
            return

        if self.books_max_pages > 0:
            next_page_num = int(next_page_url.rstrip("/").split("/")[-1])
            if next_page_num > self.books_max_pages:
                return

        yield response.follow(next_page_url, callback=self.parse)


    def parse_book(self, response):
        book = BookItem()

        book['url'] = response.url
        book['name'] = response.css('h1.main-title::text').get(default = "")
        book['img_src'] = response.css('div._book__cover img::attr(src)').get(default = "")
        book['stock'] = response.css('div.product-book-price__stock ::text').get(default="")

        book['price'] = response.css('#addToCartButton::attr(data-price)').get(default="")
        discountDiv = response.css('div.product-book-price__discount')

        if discountDiv:
            book['old_price'] = discountDiv.css('del::text').get(default="")
            book['discount_procent'] = discountDiv.css('span.discount-badge::text').get(default="")
        else:
            book['old_price'] = ""
            book['discount_procent'] = ""

        properties = {}
        properties_rows = response.css('div.book-props-item')
        for row in properties_rows:
            key = row.css('div.book-prop-name *::text').get(default = "")
            value = row.css('div.book-prop-value *::text').get(default = "")
            if key and value:
                properties[key] = value

        book['properties'] = properties

        availabilityRows = response.css("table.table.table-striped tbody tr")
        availability = {}

        for row in availabilityRows:
            idTd = row.xpath("./td[1]")
            key = idTd.xpath("string(.)").get()
            value = row.xpath("./td[3]/text()").get()
            if key and value:
                availability[key.strip()] = value

        book["availability"] = availability

        yield book