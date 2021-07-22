# -*- coding: utf-8 -*-
from scrapy import Spider
# from scrapy.selector import Selector
from scrapy.http import Request
from tripadvisor.items import GreekaRestaurantItem, TripadvisorImagesItem
from scrapy.loader import ItemLoader


class GreekaSpider(Spider):
    name = 'greeka'
    allowed_domains = ['www.greeka.com']
    start_urls = ['https://www.greeka.com/greece-eat-drink/restaurants/1/']
    item=GreekaRestaurantItem(rest_id=0)

    def parse(self, response,item=item):
    	pages = response.xpath('//*[@class= "pagination__container no-push"]//li//@href').extract()

    	for page in pages:
        	absolute_url = 'https://www.greeka.com' + page
        	yield Request(absolute_url, callback = self.parse_page)



    def parse_page(self,response,item=item):
        urls = response.xpath('//div[@class="business__info col s12"]/div//@href').extract()
        for url in urls:
        	absolute_url = 'https://www.greeka.com' + url
        	yield Request(absolute_url, callback = self.parse_restaurant)


    def parse_restaurant(self,response,item=item):
    	self.counter = item['rest_id']
    	self.counter = self.counter+1

    	l=ItemLoader(item=TripadvisorImagesItem(),response=response)

    	info = response.xpath('//*[@class="breadcrumbs__single link"]/a/text()').extract()

    	item['name'] = info[-1]
    	item['city'] = info[-3]
    	item['province'] = info[-4]

    	kind = response.xpath('//*[@class="business__type flex--start"]/a/text()').extract()
    	if kind:
    		item['kind'] = ' '.join([str(elem) for elem in kind])

    	item['price'] = response.xpath('//*[@class="business__type--price"]/text()').extract_first()
    	item['cuisine'] = response.xpath('//*[@class="business__subtype flex--start"]/span/text()').extract_first()

    	item['address'] = response.xpath('//*[@id="navToMap"]/text()').extract_first()

    	# make list string
    	description = response.xpath('//*[@class="section__header-text section__text section__text--left text-overview no-push col s12"]/p/text()').extract()
    	if description:
    		item['description'] = ' '.join([str(elem) for elem in description])


    	item['extras'] = response.xpath('//*[@id="tab_facilities"]/h2[contains(text(),"Extra Features")]/following::ul[1]/li/text()').extract()
    	item['goodfor'] = response.xpath('//*[@id="tab_facilities"]/h2[contains(text(),"Good For")]/following::ul[1]/li/text()').extract()
    	item['meals'] = response.xpath('//*[@id="tab_facilities"]/h2[contains(text(),"Meals")]/following::ul[1]/li/text()').extract()
    	item['bussiness_type'] = response.xpath('//*[@id="tab_facilities"]/h2[contains(text(),"Business Type")]/following::ul[1]/li/text()').extract()

    	coord = response.xpath('//a[contains(@href,"#tab_map")]/@data-map').extract_first()
    	if coord:
    		coord=coord.replace('[','')
    		coord=coord.replace(']','')
    		coord=coord.split(',')

    		item['lat'] = float(coord[0])
    		item['lng'] = float(coord[1])

    	item['rest_id'] = self.counter

    	yield item



    	img=response.xpath('//*[@class="business-info__slider carousel carousel-slider"]/a/img').extract_first()
    	if img:
    		img =img.split('srcset="')
    		img= img[1].split('jpg')[0]
    		img = 'https://www.greeka.com' + img + 'jpg'

    		img_id = self.counter
    		l.add_value('image_urls',img)
    		l.add_value('img_id',img_id)

    	yield l.load_item()

    # 	facilities_url = response.xpath('//*[@id="facilities_tab"]/@href').extract_first()
    # 	if facilities_url:
    # 		yield Request(response.urljoin(facilities_url), callback=self.parse_facilities)

    # def parse_facilities(self,response):
    	

