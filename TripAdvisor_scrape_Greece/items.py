# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class TripadvisorAttractionItem(Item):
	#for attraction info
    attraction_id =Field()
    category=Field()
    name=Field()
    country=Field()
    province=Field()
    city=Field()
    address=Field()
    price=Field()
    rating=Field()
    duration=Field()
    description=Field()

class TripadvisorReviewItem(Item):
	#for attraction reviews
	attraction_id=Field()
	rating=Field()
	review=Field()
	review_date=Field()
	user=Field()

class TripadvisorImagesItem(Item):
    image_urls=Field()
    images=Field()
    img_id=Field()

class TripadvisorHotelItem(Item):
	# for hotel info
	hotel_id =Field()
	category=Field()
	name=Field()
	city=Field()
	region=Field()
	address=Field()
	country=Field()
	rating=Field()
	expirience=Field()
	price=Field()
	amenities=Field()
	location_rating=Field()
	clean_rating=Field()
	service_rating=Field()
	value_rating=Field()

class TripadvisorRestaurantItem(Item):
	# for hotel info
	rest_id =Field()
	name=Field()
	# city=Field()
	# region=Field()
	address=Field()
	rating=Field()
	price=Field()
	food_rating=Field()
	service_rating=Field()
	value_rating=Field()
	lat=Field()
	lng=Field()
	cuisine=Field()
	diet=Field()
	meals=Field()
	features=Field()


class TripadvisorHotelReviewItem(Item):
	# for hotel reviews
	hotel_id =Field()
	user=Field()
	user_profile=Field()
	rating=Field()
	review=Field()
	review_date=Field()

class TripadvisorRestaurantReviewItem(Item):
	# for hotel reviews
	rest_id =Field()
	user=Field()
	rating=Field()
	review=Field()
	review_date=Field()


class GreekaRestaurantItem(Item):
	rest_id=Field()
	name=Field()
	city=Field()
	province=Field()
	kind=Field()
	price=Field()
	cuisine=Field()
	address=Field()
	description=Field()
	extras=Field()
	goodfor=Field()
	meals=Field()
	bussiness_type=Field()
	lat=Field()
	lng=Field()