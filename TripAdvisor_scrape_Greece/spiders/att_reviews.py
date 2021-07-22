# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from tripadvisor.items import TripadvisorReviewItem


class AttReviewsSpider(Spider):
    name = 'att_reviews'
    allowed_domains = ['www.tripadvisor.com']
    start_urls = ['https://www.tripadvisor.com/Attraction_Products-g189398-Greece.html/']
    item =TripadvisorReviewItem()
    item['attraction_id']=0

    def parse(self, response):
        f_class = response.xpath('//*[@class="ap_filter_wrap filter_wrap_0 single_select"]')
        # category_urls = f_class.xpath('.//*[@class="taLnk"]/@href').extract()[:2]
        url = f_class.xpath('.//*[@class="taLnk"]/@href').extract()[0]
        yield Request(response.urljoin(url), callback = self.parse_category)

        # for url in category_urls:
        # 	yield Request(response.urljoin(url), callback = self.parse_category)


    def parse_category(self, response):
    	self.count=0
    	attractions = response.xpath('//*[@class="listing_title"]/h2/a/@href').extract()
    	attraction = response.xpath('//*[@class="listing_title"]/h2/a/@href').extract()[0]
    	yield Request(response.urljoin(attraction), callback = self.parse_attraction)

        # for attraction in attractions:
        #     yield Request(response.urljoin(attraction), callback = self.parse_attraction,
        #         dont_filter = True)

    def parse_attraction(self,response):
    	# Stop running when the reviews reach a oldest date
    	self.stop=0


    	# if response.xpath('//*[@class="_1mvDoCNZ"]//*[@class="_2-JBovPw"]//*[@class="_3KcXyP0F"]/@title').extract_first():
    	# 	item['rating']=float(response.xpath('//*[@class="_1mvDoCNZ"]//*[@class="_2-JBovPw"]//*[@class="_3KcXyP0F"]/@title').extract_first().split(' of')[0])
    	# else:
    	# 	item['rating'] = None


    	reviews = response.xpath('//div[@class="RKsX4xGw"]//div[@class="_1T1U92WJ"]')

    	for review in reviews:
    		item['review'] = review.xpath('.//*[@class="_1e-v2VZJ _3I1Aup9d"]/text()').extract_first()
    		review_rate = review.xpath('.//*[@class="_3KcXyP0F"]/@title').extract_first()
    		# If there is no rating for a review I put a null value to avoid errors
    		if (review_rate):
    			item['rating'] = float(review.xpath('.//*[@class="_3KcXyP0F"]/@title').extract_first().split(' of')[0])
    		else:
    			item['rating']=None

    		item['review_date'] = review.xpath('.//*[@class="_3mCNwHy0"]/span/text()').extract_first().split('review ')[1]
    		item['review'] = review.xpath('.//*[@class="_2vmgOjMl "]/span/text()').extract_first()

    		# I keep only reviews made in 2020
    		if(int(review_date.split()[1]) ==2020 ):
    			yield item
    		else:
    			self.stop=1

    	# Go to next review page
    	next_review_page = response.xpath('//a[@class="_1frVqeI5"]/@href').extract_first()
    	if (next_review_page and self.stop==0):
    		yield Request(response.urljoin(next_review_page), callback = self.parse_attraction)




