# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from tripadvisor.items import TripadvisorAttractionItem , TripadvisorImagesItem ,TripadvisorReviewItem
# from scrapy.loader import ItemLoader


class UrlscrapeSpider(Spider):
    name = 'urlscrape'
    allowed_domains = ['www.tripadvisor.com']
    start_urls = ['https://www.tripadvisor.com/Attraction_Products-g189398-Greece.html/']
    # Create item instance for attraction info. We initialize attraction_id=0 to use it as counter
    item=TripadvisorAttractionItem(attraction_id=0)



    def parse(self, response,item=item):
        f_class = response.xpath('//*[@class="ap_filter_wrap filter_wrap_0 single_select"]')
        category_urls = f_class.xpath('.//*[@class="taLnk"]/@href').extract()


        for url in category_urls:
            c_absolute_url='https://www.tripadvisor.com' + url
            yield Request(c_absolute_url, callback = self.parse_category)




    def parse_category(self, response,item=item):
        # category = response.xpath('//*[@class="taLnk"]/text()').extract_first()
        attractions = response.xpath('//*[@class="listing_title"]/h2/a/@href').extract()



        for attraction in attractions:
            a_absolute_url='https://www.tripadvisor.com' + attraction
            yield Request(a_absolute_url, callback = self.parse_attraction)

        next_page = response.xpath('//div[@class="unified pagination "]/a[contains(text(),"Next")]/@href').extract_first()
        if next_page:
            n_absolute_url='https://www.tripadvisor.com' + next_page
            yield Request(n_absolute_url, callback = self.parse_category)




    def parse_attraction(self,response,item=item):
        self.counter = item['attraction_id']  # I keep in i a auto increment counter as attraction id.
        self.counter = self.counter+1

        # # loader for images
        # l=ItemLoader(item=TripadvisorImagesItem(),response=response)
        # category=response.meta['category']

        # item['category']=category
        item['name'] = response.xpath('//*[@class="_2MCqN-mR"]/span/text()').extract_first()


        name_info = response.xpath('//*[@class="_3Zgdj6Ta"]/span/text()').extract()

        item['country'] = "Greece"
        # I use if statement cause of trip advisor head path lenght. In some cases no enough like seperate convidence, city info so I
        # must set the same name e.g both city and province Crete to avoid give providence value like Greece
        if(name_info[-4]=='Greece'):
            item['city'] = name_info[-3]
            item['province'] = name_info[-3]
        else:
            item['city'] = name_info[-3]
            item['province'] = name_info[-4]



        address = response.xpath('//div[contains(text(), "Departure Point")]/following::div[1]/span/text()').extract_first()
        duration = response.xpath('//div[contains(text(), "Duration")]/following::div[1]/span/text()').extract_first()

        if duration:
            #reformat duration cause in many cases have unique values as 2-3h , 2h 30m etc
            if('d' in duration):
                if('–' in duration):
                    t = duration.split('–')
                    item['duration']=float(''.join(filter(str.isdigit, t[0])))*24
                else:
                    item['duration']=float(''.join(filter(str.isdigit, duration)))*24
            elif('h' in duration):
                if('m' in duration):
                    t = duration.split('h')
                    h=float(''.join(filter(str.isdigit, t[0])))
                    m=float(''.join(filter(str.isdigit, t[1])))
                    item['duration'] = h + m/60
                elif('–' in duration):
                    t = duration.split('–')
                    item['duration']=float(''.join(filter(str.isdigit, t[0])))
                else:
                    item['duration'] = float(''.join(filter(str.isdigit, duration)))
            elif('m' in duration):
                if('–' in duration):
                    t=duration.split('–')
                    m1 = float(''.join(filter(str.isdigit, t[0])))
                    m2 = float(''.join(filter(str.isdigit, t[1])))
                    item['duration']= ((m1+m2)/2)/60
                else:
                    item['duration']=float(''.join(filter(str.isdigit, duration)))/60
        else:
            item['duration'] = None

        # In some cases either we dont have address info so we add city value to help us find some near coordinates
        # or we can have multiple adresses in the same city , something that does not help us so I take the first one
        if not address:
            item['address']=item['city']
        else:
            try:
                address.index('\n')
                item['address']=address.split('\n')[0]
            except ValueError:
                item['address'] = address



        # Price is string type so I must convert it to number
        # All prices on tripavisor are float with 2 decimal points
        # I remove everything from the string except numbers (,.) and after that I divide by 100 to return the price to correct value
        price = response.xpath('//*[@class="_3nF-894k"]/text()').extract_first()
        if price:
            price=price.split('$')[1]
            price=''.join(filter(str.isdigit, price))
            item['price']=int(price)/100
        else:
            item['price']=None

        # item['description']=response.xpath('//div[@class="AvpaRatK"]/span/text()').extract_first()




        rating = response.xpath('//*[@class="_1mvDoCNZ"]//*[@class="_2-JBovPw"]//*[@class="_3KcXyP0F"]/@title').extract_first()
        # If there is no rating for an attraction I put a nan value to avoid errors
        if rating:
            item['rating']=float(rating.split(' of')[0])
        else:
            item['rating'] = None

        print('to item id telos',self.counter)

        item['attraction_id'] = self.counter

        yield item


        # image_urls = response.xpath('//*[@class="_39RSYxGX"]/@style').extract_first().split('url(')[1].replace(')','')
        # img_id = self.counter
        # l.add_value('image_urls',image_urls)
        # l.add_value('img_id',img_id)

        # yield l.load_item()


        #loader for rev
        itemrev = TripadvisorReviewItem()



        reviews = response.xpath('//div[@class="RKsX4xGw"]//div[@class="_1T1U92WJ"]')

        for review in reviews:

            itemrev['user'] = review.xpath('.//*[@class="_1e-v2VZJ _3I1Aup9d"]/text()').extract_first()
            review_rate = review.xpath('.//*[@class="_3KcXyP0F"]/@title').extract_first()
            # If there is no rating for a review I put a null value to avoid errors
            if (review_rate):
                itemrev['rating'] = float(review.xpath('.//*[@class="_3KcXyP0F"]/@title').extract_first().split(' of')[0])
            else:
                itemrev['rating']=None

            review_date = review.xpath('.//*[@class="_3mCNwHy0"]/span/text()').extract_first().split('review ')[1]
            itemrev['review_date'] = review_date
            itemrev['review'] = review.xpath('.//*[@class="_2vmgOjMl "]/span/text()').extract_first()
            itemrev['attraction_id'] = self.counter

            # I keep only reviews made in 2020
            yield itemrev

        # Go to next review page
        next_review_page = response.xpath('//a[@class="_1frVqeI5"]/@href').extract_first()
        # print('Next page : ', next_review_page, 'stop :', self.stop)
        if (next_review_page):
            rn_absolute_url='https://www.tripadvisor.com' + next_review_page
            yield Request(rn_absolute_url, callback = self.parse_review,meta={'counter':self.counter})





    def parse_review(self,response):
        self.stop=0
        itemrev = TripadvisorReviewItem()
        reviews = response.xpath('//div[@class="RKsX4xGw"]//div[@class="_1T1U92WJ"]')
        self.counter=response.meta['counter']
        # self.review_count = response.meta['review_count']

        for review in reviews:

            itemrev['user'] = review.xpath('.//*[@class="_1e-v2VZJ _3I1Aup9d"]/text()').extract_first()
            review_rate = review.xpath('.//*[@class="_3KcXyP0F"]/@title').extract_first()
            # If there is no rating for a review I put a null value to avoid errors
            if (review_rate):
                itemrev['rating'] = float(review.xpath('.//*[@class="_3KcXyP0F"]/@title').extract_first().split(' of')[0])
            else:
                itemrev['rating']=None

            review_date = review.xpath('.//*[@class="_3mCNwHy0"]/span/text()').extract_first().split('review ')[1]
            itemrev['review_date'] = review_date
            itemrev['review'] = review.xpath('.//*[@class="_2vmgOjMl "]/span/text()').extract_first()
            itemrev['attraction_id'] = self.counter

            # I keep only reviews made in 2020
            yield itemrev

            # There are 2 ways to stop scrape reviews. First we check for date to be inside 20 or newer. Second if there
            # are more than 20 we stop.
            # if self.review_count>64:
            #     self.stop=1

            # self.review_count = self.review_count+5
            next_review_page = response.xpath('//a[@class="_1frVqeI5"]/@href').extract_first()
            if (next_review_page):
                # print('sunolo reviews', self.review_count)
                rn1_absolute_url='https://www.tripadvisor.com' + next_review_page
                yield Request(rn1_absolute_url, callback = self.parse_review,meta={'counter':self.counter})





