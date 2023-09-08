import scrapy
import re

from yelptesttask.utils import logger
from yelptesttask.spider_item import YelpItem


class YelpSpider(scrapy.Spider):
    name = "yelp"

    def __init__(
        self, query: str, location: str, name=None, **kwargs
    ):
        super().__init__(self.name, **kwargs)
        self.start_urls = [
            f"https://www.yelp.com/search?find_desc={query}&find_loc={location}&sortby=rating"
        ]
        logger.info(f"Starting spider with {self.start_urls}")

    def parse(self, response):
        """Spider entry point

        Args:
            response (_type_): _description_

        Yields:
            _type_: _description_
        """
        links = self.get_items_list(response)

        # parse data from each link page
        for link in links:
            logger.debug(f"Link to parse: {link}")
            yield response.follow(link, callback=self.parse_item)

        # move to the next page
        next_page = response.css("a.next-link::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response):
        """Parse business page

        Args:
            response (_type_): _description_

        Returns:
            _type_: _description_
        """
        # business name is in h1 tag and h1 tag is always present and unique
        biz_name = response.xpath(".//h1/text()").get()
        # amount of reviews is in a tag with href="#reviews"
        # and it's always present and unique
        biz_amount_of_reviews = response.css(
            'a[href="#reviews"]::text'
        ).get()

        # to get rating we need to find span with text
        # that include fload number from 0.0 to 5.0
        spans = response.xpath("//span")
        biz_rating = None

        for span in spans:
            span_text = span.xpath("text()").get()

            if not span_text:
                continue

            if re.match(r"^([0-4](\.\d*)?|5(\.0*)?)$", span_text):
                biz_rating = span_text
                break

        # business website is in a tag with href
        # that include "biz_redir" it may be missing
        biz_redir = response.css(
            'a[href*="biz_redir"]::attr(href)'
        ).get()

        reviews = self.get_item_reviews(response)

        curr_item = YelpItem(
            business_name=biz_name,
            business_rating=biz_rating,
            number_of_reviews=biz_amount_of_reviews,
            business_yelp_url=response.url,
            business_website=biz_redir,
            reviews=reviews[:5],
        )

        return curr_item

    def get_item_reviews(self, response):
        """Get all reviews posts

        Args:
            response (_type_): _description_

        Returns:
            _type_: _description_
        """
        lis = response.xpath("//li")
        reviews = []

        for li in lis:
            # find all links that include "user_details"
            li_links = set(li.css("a[href*='user_details']"))

            if not li_links:
                continue

            review = self.parse_item_review(li)
            logger.debug(f"Review: {review}")
            reviews.append(review)

        return reviews

    def parse_item_review(self, response):
        """_summary_

        Args:
            response (_type_): _description_

        Returns:
            _type_: _description_
        """
        reviewer_name = response.css(
            "a[href*='user_details']::text"
        ).get()

        reviewer_loc = response.xpath(".//span[1]/text()").get()

        # check all span text for date in a specific format
        # mm(m)/dd(d)/yyyy
        date_pattern = r"\b\d{1,2}/\d{1,2}/\d{4}\b"

        all_text = response.css("span::text").getall()
        date_text = [
            text for text in all_text if re.search(date_pattern, text)
        ]

        return {
            "reviewer_name": reviewer_name,
            "reviewer_loc": reviewer_loc,
            "review_date": date_text[0] if date_text else None,
        }

    def get_items_list(self, response):
        lis = response.xpath("//li")

        for li in lis:
            li_links = list(set(li.xpath(".//a")))

            if len(li_links) == 0:
                continue

            for li_link in li_links:
                link_text = li_link.xpath("@href").get()

                if "/biz/" in link_text or "/adredir" in link_text:
                    yield link_text
