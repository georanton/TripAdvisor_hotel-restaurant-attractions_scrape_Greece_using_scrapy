# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

class TripadvisorPipeline(object):
    def process_item(self, item, spider):
        os.chdir('C: ###')

        if item['images'][0]['path']:
        	new_image_name = item['name'][0] + '.jpg'
        	new_image_path = r'C: ###' + new_image_name

        	os.rename(item['images'][0]['path'], new_image_path)



