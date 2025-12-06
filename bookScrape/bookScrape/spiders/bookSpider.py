import scrapy
from bookScrape.items import BookItem

class BookspiderSpider(scrapy.Spider):
    name = "bookSpider"
    allowed_domains = ["librarius.md"]
    start_urls = ["https://librarius.md/ro/catalog/hot-offers"]



    def parse(self, response):
        books = response.css('div.book-fixed-card')
        for book in books:
            book_url = book.css('a::attr(href)').get()
            yield response.follow(book_url, callback = self.parse_book)

    def parse_book(self, response):
        book = BookItem()

        book['url'] = response.url
        book['name'] = response.css('h1.main-title::text').get(default = "")
        book['img_src'] = response.css('div._book__cover img::attr(src)').get(default = "")
        book['stock'] = response.css('div.product-book-price__stock ::text').get(default='')
        price_text = response.css('div.product-book-price__actual::text').get(default = " nu s-a gasit text")
        book['price'] = price_text

        props = {}
        props_rows = response.css('div.book-props-item')
        for row in props_rows:
            key = row.css('div.book-prop-name::text').get(default = '')
            value = row.css('div.book-prop-value::text').get(default = '')
            if key and value:
                props[key] = value
        book['props'] = props

        yield book