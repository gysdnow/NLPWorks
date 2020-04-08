import pandas as pd
import requests as req
import scrapy 
from pymongo import MongoClient
from scrapy import Request
from rent591.items import rentPageItem
from selenium import webdriver

class rentSpider(scrapy.Spider):
    name = "rentPage"
    def start_requests(self):
        #Mongo DB Settings
        client = MongoClient('localhost', 27017)
        db = client['rent']
        collection = db['pageIndex']
        links = collection.distinct('link')
        #iter From Index 
        for url in links:
            yield Request(url)

    def parse(self, response):
        # Parse Similar Format Pattern - 1
        identity = response.css('div.avatarRight div::text').extract_first()
        name = response.css('span.kfCallName::attr("data-name")').extract_first()
        phoneNum = response.css('span.dialPhoneNum::attr("data-value")').extract_first()
        post_id = response.css('input#hid_post_id::attr("value")').extract_first()
        title = response.css('title::Text').extract_first()
        due_date = response.css('span.ft-rt::text').extract_first().split('：')
        
        all_specs = [['身分',identity], 
                     ['稱謂',name], 
                     ['電話',phoneNum],
                     ['id',post_id], 
                     ['title',title],
                     ['Status_code',response.status],
                     [due_date[0], due_date[1]]]

        # Parse Similar Format Pattern - 2
        elements = response.css('ul.attr li')
        trim_first = [''.join(e.css('::text').extract()) for e in elements]
        trim_second = [''.join(t.split(':')).split() for t in trim_first]

        all_specs += trim_second
        #因為以上都為橫向的TAG切割，故先行轉置

        all_specs_T = list(map(list,zip(*all_specs)))

        #下方為直向的切割 直接併入轉置後的LIST
        one = [''.join(x.css('::text').extract()) for x in response.css('ul.labelList div.one')]
        two = [''.join(x.css('::text').extract()) for x in response.css('ul.labelList div.two')]

        all_specs_T[0] += one
        all_specs_T[1] += two

        #self.all_df = pd.concat([self.all_df, pd.DataFrame([all_specs_T[1]], columns=all_specs_T[0])])
        _df =  pd.DataFrame([all_specs_T[1]], columns=all_specs_T[0])
        item = rentPageItem()
        row = _df.to_dict('r')[0]

        item['row'] = row

        yield item
        
