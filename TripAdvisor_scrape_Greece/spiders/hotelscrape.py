# -*- coding: utf-8 -*-
from time import sleep

from scrapy import Spider
from scrapy.selector import Selector
from selenium import webdriver
from scrapy.http import Request
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from tripadvisor.items import TripadvisorHotelItem , TripadvisorImagesItem ,TripadvisorHotelReviewItem
# from scrapy.loader import ItemLoader


class HotelscrapeSpider(Spider):
    name = 'hotelscrape'
    allowed_domains = ['www.tripadvisor.com']
    # start_urls = ['http://www.tripadvisor.com/Hotels-g189398-Greece-Hotels.html/']
    item=TripadvisorHotelItem(hotel_id=2343)

    def start_requests(self,item=item):
    	#main page hotel urls
    	# request each category to parse the results.4 categories: hotels,b&bs, condos , villas
    	# category_url = response.xpath('//span[contains(text(),"Property types")]/following::div/span/a/@href').extract()[:2]
    	# option = webdriver.ChromeOptions()
    	# chrome_prefs = {}
    	# option.experimental_options["prefs"] = chrome_prefs
    	# chrome_prefs["profile.default_content_settings"] = {"images": 2}
    	# chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

    	#dont load image on browser to speed up the process
        self.chromeOptions = webdriver.ChromeOptions()
        self.prefs = {'profile.managed_default_content_settings.images':2}
        self.chromeOptions.add_experimental_option("prefs", self.prefs)

        self.driver = webdriver.Chrome("C:/Users/Giorgos A/chromedriver.exe",chrome_options=self.chromeOptions)
        # categories = ['https://www.tripadvisor.com/Hotels-g189398-Greece-Hotels.html' , 'https://www.tripadvisor.com/Hotels-g189398-c2-Greece-Hotels.html' , 'https://www.tripadvisor.com/Hotels-g189398-c3-zff28-Greece-Hotels.html' , 'https://www.tripadvisor.com/Hotels-g189398-c3-zff22-Greece-Hotels.html']

        self.driver.get('https://www.tripadvisor.com/Hotels-g189398-c3-zff22-Greece-Hotels.html')

        sel = Selector(text=self.driver.page_source)

        # names = sel.xpath('//div[@class="listing_title"]/a/text()').extract()

        urls = sel.xpath('//div[@class="listing_title"]/a/@href').extract()
    	# url = urls[1]
    	# absolute_url='http://www.tripadvisor.com' + url
    	# self.price = sel.xpath('//div[contains(@data-url,"'+url+'")]//div[contains(text(),"€")]/text()').extract_first()
    	# yield Request(absolute_url,callback=self.parse_hotel,meta={'price':self.price})

        for url in urls:
            absolute_url='http://www.tripadvisor.com' + url
            # we pass the price as meta from the start page cause in the redirect page take some time to load and produce wrong values
            self.price = sel.xpath('//div[contains(@data-url,"'+url+'")]//div[contains(text(),"€")]/text()').extract_first()
            self.category = sel.xpath('//div[@class="_2zD_TL6k _2j9j4lRx"]/text()').extract_first()
            yield Request(absolute_url,callback=self.parse_hotel,meta={'price':self.price, 'category':self.category})                
        while True:
            try:
                next_page = self.driver.find_element_by_xpath('//span[text()="Next"]')
                myElem = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'taplc_main_pagination_bar_dusty_hotels_resp_0')))
                self.logger.info('Page is ready!')
                self.driver.execute_script("arguments[0].click();", next_page)                    
                sel = Selector(text=self.driver.page_source)
                urls = sel.xpath('//div[@class="listing_title"]/a/@href').extract()

                for url in urls:
                    absolute_url='http://www.tripadvisor.com' + url
                    self.price = sel.xpath('//div[contains(@data-url,"'+url+'")]//div[contains(text(),"€")]/text()').extract_first()
                    self.category = sel.xpath('//div[@class="_2zD_TL6k _2j9j4lRx"]/text()').extract_first()
                    yield Request(absolute_url,callback=self.parse_hotel,meta={'price':self.price, 'category':self.category})
    			    # names = sel.xpath('//div[@class="listing_title"]/a/text()').extract()
    			
    			    # for name in names:
    			    # 	yield { 'name': name}

            except NoSuchElementException:
                self.logger.info('No more pages to load.')
                self.driver.quit()
                break

    def parse_hotel(self,response,item=item):
    	#Hotel info collection
        self.counter = item['hotel_id']  # I keep in i a auto increment counter as attraction id.
        self.counter += 1

        # l=ItemLoader(item=TripadvisorImagesItem(),response=response)


        item['name'] = response.xpath('//h1[@class="_1mTlpMC3"]/text()').extract_first()

        name_info =response.xpath('//li[@class="breadcrumb"]/a/span/text()').extract()

        item['category'] = response.meta['category']

        item['city'] = name_info[-2]

        item['region'] = name_info[-3]

        address = response.xpath('//span[@class="_3ErVArsu jke2_wbp"]/text()').extract_first()
        # In some cases either we dont have address info so we add city value to help us find some near coordinates
        # or we can have multiple adresses in the same city , something that does not help us so I take the first one
        if not address:
        	item['address']=item['city']
        else:
        	item['address'] = address

        item['country'] = 'Greece'

        rating = float(response.xpath('//span[@class="_3cjYfwwQ"]/text()').extract_first())
        if rating:
        	item['rating'] = rating
        else:
        	rating=None


        item['expirience'] = response.xpath('//div[@class="_2-OvcgvB"]/text()').extract_first()

        sub_ratings = response.xpath('//div[contains(@class,"_1krg1t5y")]/span/@class').extract()
        if sub_ratings:
            item['location_rating']=int(''.join(filter(str.isdigit, sub_ratings[0].split('bubble_')[-1])))/10
            item['clean_rating']=int(''.join(filter(str.isdigit, sub_ratings[1].split('bubble_')[-1])))/10
            item['service_rating']=int(''.join(filter(str.isdigit, sub_ratings[2].split('bubble_')[-1])))/10
            item['value_rating']=int(''.join(filter(str.isdigit, sub_ratings[3].split('bubble_')[-1])))/10


        item['amenities']=response.xpath('//div[@class="_1nAmDotd"]/div/text()').extract()


        # price = response.xpath('//div[@class="_1oVAnyb8"]//div[contains(text(),"€")]/text()').extract_first()
        self.price=response.meta['price']
        if self.price:
        	#remove concurency symbols and turn the value to numeric
        	item['price'] = int(''.join(filter(str.isdigit, self.price)))
        else:
        	item['price'] = None

        item['hotel_id'] = self.counter

        yield item
    	# End of hotel info collection

    	# Get images
        # image_urls = response.xpath('//li[@class="_13UaEdHg _2CIU8LK-"]/div/img/@src').extract_first()
        # img_id = self.counter
        # l.add_value('image_urls',image_urls)
        # l.add_value('img_id',img_id)

        # yield l.load_item()
        # End of image collection

        #start collect reviews
        itemrev = TripadvisorHotelReviewItem()

        # Stop running when the reviews reach a oldest date
        # self.stop=0 #stop criteria
        # self.review_count = 5


        reviews =  response.xpath('//div[@class="_2wrUUKlw _3hFEdNs8"]')

        for review in reviews:

            itemrev['user'] = review.xpath('.//div[@class="_2fxQ4TOx"]/span/a/text()').extract_first()
            itemrev['user_profile'] = review.xpath('.//div[@class="_2fxQ4TOx"]/span/a/@href').extract_first()
            review_rate = review.xpath('.//div[@class="nf9vGX55"]/span').extract_first().split('bubble_')[-1]
            # If there is no rating for a review I put a null value to avoid errors
            if (review_rate):
            	itemrev['rating'] = int(''.join(filter(str.isdigit, review_rate)))/10
            else:
            	itemrev['rating']=None

            review_date = review.xpath('.//div[@class="_2fxQ4TOx"]/span/text()').extract_first().split('review ')[1]
            itemrev['review_date'] = review_date
            itemrev['review'] = review.xpath('.//q[@class="IRsGHoPm"]/span/text()').extract_first()
            itemrev['hotel_id'] = self.counter

            # I keep only reviews made until 19 or we set a limit of 50 reviews per hotel
            yield itemrev

        # Go to next review page
        next_review_page = response.xpath('//a[@class="ui_button nav next primary "]/@href').extract_first()
        # print('Next page : ', next_review_page, 'stop :', self.stop)
        if (next_review_page):
            yield Request(response.urljoin(next_review_page), callback = self.parse_review,meta={'counter':self.counter})
        #end of collecting reviews ( 1st page of reviews. Continue in the function below)




    def parse_review(self,response):
        print('MPHKA')
        # self.stop=0
        itemrev = TripadvisorHotelReviewItem()
        reviews = response.xpath('//div[@class="_2wrUUKlw _3hFEdNs8"]')
        self.counter=response.meta['counter']
        # self.review_count = response.meta['review_count']

        for review in reviews:

            itemrev['user'] = review.xpath('.//div[@class="_2fxQ4TOx"]/span/a/text()').extract_first()
            itemrev['user_profile'] = review.xpath('.//div[@class="_2fxQ4TOx"]/span/a/@href').extract_first()
            review_rate = review.xpath('.//div[@class="nf9vGX55"]/span').extract_first().split('bubble_')[-1]
            # If there is no rating for a review I put a null value to avoid errors
            if (review_rate):
                itemrev['rating'] = int(''.join(filter(str.isdigit, review_rate)))/10
            else:
                itemrev['rating']=None

            review_date = review.xpath('.//div[@class="_2fxQ4TOx"]/span/text()').extract_first().split('review ')[1]
            itemrev['review_date'] = review_date
            itemrev['review'] = review.xpath('.//q[@class="IRsGHoPm"]/span/text()').extract_first()
            itemrev['hotel_id'] = self.counter

            # I keep only reviews made until 19 or we set a limit of 50 reviews per hotel
            yield itemrev

            # There are 2 ways to stop scrape reviews. First we check for date to be inside 19 or newer. Second if there
            # are more than 50 we stop.
            # if self.review_count>64:
            #     self.stop=1

            # self.review_count = self.review_count+5
        next_review_page = response.xpath('//a[@class="ui_button nav next primary "]/@href').extract_first()
        # print('next_review_page : ',next_review_page, "stop : ",self.stop)
        if (next_review_page):
            yield Request(response.urljoin(next_review_page), callback = self.parse_review,meta={'counter':self.counter})

