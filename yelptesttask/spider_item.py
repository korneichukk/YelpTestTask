import scrapy


class YelpItem(scrapy.Item):
    business_name = scrapy.Field()
    business_rating = scrapy.Field()
    number_of_reviews = scrapy.Field()
    business_yelp_url = scrapy.Field()
    business_website = scrapy.Field()
    reviews = scrapy.Field()
