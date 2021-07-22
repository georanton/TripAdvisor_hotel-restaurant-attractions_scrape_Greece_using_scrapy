# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from tripadvisor.items import TripadvisorRestaurantItem , TripadvisorImagesItem ,TripadvisorRestaurantReviewItem
import re
from scrapy.loader import ItemLoader


class TripRestaurantsSpider(Spider):
    name = 'trip_restaurants'
    allowed_domains = ['www.tripadvisor.com']
    start_urls = ['https://www.tripadvisor.com/Restaurants-g189398-oa20-Greece.html#LOCATION_LIST']
    item = TripadvisorRestaurantItem(rest_id=0)


    def parse(self, response):
        regions = response.xpath('//*[@class="geoList"]//@href').extract()
        for region in regions:
        	yield Request(response.urljoin(region), callback = self.parse_region)

        next_page = response.xpath('//*[@class="guiArw sprite-pageNext  pid0"]/@href').extract_first()
        if next_page:
        	yield Request(response.urljoin(next_page), callback = self.parse)



    def parse_region(self,response):
    	rest_urls = response.xpath('//div[@class="_2kbTRHSI"]//@href').extract()

    	for rest in rest_urls:
    		yield Request(response.urljoin(rest), callback = self.parse_restaurant)

    	reg_next_page = response.xpath('//a[contains(text(),"Next")]/@href').extract_first()
    	if reg_next_page:
    		yield Request(response.urljoin(reg_next_page), callback = self.parse_region)



    def parse_restaurant(self,response,item=item):
    	self.counter = item['rest_id']
    	self.counter += 1

    	l=ItemLoader(item=TripadvisorImagesItem(),response=response)

    	text = response.body.decode('utf-8')
    	item['name'] = response.xpath('//h1[@class="_3a1XQ88S"]/text()').extract_first()

    	item['address'] = response.xpath('//div[@class="_2vbD36Hr _36TL14Jn"]//text()').extract_first()

    	item['price'] = response.xpath('//span[@class="_13OzAOXO _34GKdBMV"]/a[contains(text(),"$")]/text()').extract_first()

    	# loc_info= re.findall('"geo_name(.*?)}', response.body.decode('utf-8'))
    	# if loc_info:
    	# 	loc_info=loc_info[0].split(',')
    	# 	item['city'] = loc_info[0].replace('":"','').strip()
    	# 	item['region'] = loc_info[1].strip()


    	rating = response.xpath('//*[@class="_3KcXyP0F"]/@title').extract_first()
    	if rating:
    		item['rating'] = int(''.join(filter(str.isdigit, rating.split()[0])))/10
    	else:
    		item['rating'] = None


    	sub_ratings = response.xpath('//*[@class="jT_QMHn2"]//*[contains(@class,"bubble")]/@class').extract()
    	if sub_ratings:
    		item['food_rating'] = int(''.join(filter(str.isdigit, sub_ratings[0].split('bubble_')[-1])))/10
    		item['service_rating'] = int(''.join(filter(str.isdigit, sub_ratings[1].split('bubble_')[-1])))/10
    		item['value_rating'] = int(''.join(filter(str.isdigit, sub_ratings[2].split('bubble_')[-1])))/10
    	

    	lat = re.findall('"latitude":\d+\.\d+', text)
    	lng = re.findall('"longitude":\d+\.\d+', text)
    	if lat:
    		item['lat'] = lat[0].replace('"latitude":','')
    	if lng:
    		item['lng'] = lng[0].replace('"longitude":','')

    	# regex to clear everything from string except alpharithmetic
    	regex = re.compile('[^a-zA-Z]')

    	# first get cuisine values and clear them
    	cuisine =re.findall(',"cuisines(.*?)]}', text)[0]
    	cuisine=regex.sub('',cuisine)
    	cuisine=cuisine.split('tagValue')
    	cuisine.pop(0)
    	item['cuisine'] = [c.replace('tagId','') for c in cuisine]

    	# get diet values and clear them
    	diet= re.findall(',"dietaryRestrictions(.*?)]}', text)[0]
    	diet=regex.sub('',diet)
    	diet=diet.split('tagValue')
    	diet.pop(0)
    	item['diet'] = [d.replace('tagId','') for d in diet]

    	# get meals values and clear them
    	meals= re.findall(',"meals(.*?)]}', text)[0]
    	meals=regex.sub('',meals)
    	meals=meals.split('tagValue')
    	meals.pop(0)
    	item['meals'] = [m.replace('tagId','') for m in meals]

    	# get features values and clear them
    	features= re.findall(',"features(.*?)]}', text)[0]
    	features=regex.sub('',features)
    	features=features.split('tagValue')
    	features.pop(0)
    	item['features'] = [f.replace('tagId','') for f in features]

    	item['rest_id'] = self.counter

    	yield item



    	image_urls = response.xpath('//div[@class="large_photo_wrapper   "]//img/@data-lazyurl').extract_first()
    	img_id = self.counter
    	l.add_value('image_urls',image_urls)
    	l.add_value('img_id',img_id)
    	yield l.load_item()




    	itemrev = TripadvisorRestaurantReviewItem()
    	reviews = response.xpath('//div[@class="review-container"]')

    	for review in reviews:
    		itemrev['user'] = review.xpath('.//div[@class="info_text pointer_cursor"]/div/text()').extract_first()
    		rating = review.xpath('.//span[contains(@class,"bubble")]/@class').extract_first()
    		if rating:
    			itemrev['rating'] = int(''.join(filter(str.isdigit, rating.split('bubble_')[-1])))/10
    		rev_date = review.xpath('.//div[@class="prw_rup prw_reviews_stay_date_hsx"]/text()').extract_first()
    		if rev_date:
    			itemrev['review_date'] = rev_date.strip()
    		itemrev['review'] = review.xpath('.//*[@class="partial_entry"]/text()').extract_first()
    		itemrev['rest_id'] = self.counter

    		yield itemrev

    	next_rev_page = response.xpath('//a[contains(text(),"Next")]/@href').extract_first()
    	if next_rev_page:
    		yield Request(response.urljoin(next_rev_page),callback = self.parse_review,meta={'counter':self.counter})



    def parse_review(self,response):
    	self.counter=response.meta['counter']
    	itemrev = TripadvisorRestaurantReviewItem()

    	reviews = response.xpath('//div[@class="review-container"]')

    	for review in reviews:
    		itemrev['user'] = review.xpath('.//div[@class="info_text pointer_cursor"]/div/text()').extract_first()
    		rating = review.xpath('.//span[contains(@class,"bubble")]/@class').extract_first()
    		if rating:
    			itemrev['rating'] = int(''.join(filter(str.isdigit, rating.split('bubble_')[-1])))/10
    		rev_date = review.xpath('.//div[@class="prw_rup prw_reviews_stay_date_hsx"]/text()').extract_first()
    		if rev_date:
    			itemrev['review_date'] = rev_date.strip()
    		itemrev['review'] = review.xpath('.//*[@class="partial_entry"]/text()').extract_first()
    		itemrev['rest_id'] = self.counter

    		yield itemrev

    	next_rev_page = response.xpath('//a[contains(text(),"Next")]/@href').extract_first()
    	if next_rev_page:
    		yield Request(response.urljoin(next_rev_page),callback = self.parse_review,meta={'counter':self.counter})




