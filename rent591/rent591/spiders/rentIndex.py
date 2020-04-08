import pandas as pd
import requests as req
import scrapy 
from rent591.items import pageIndexItem
import time
from selenium import webdriver

class rentSpider(scrapy.Spider):
    name = "rentIndex"
    start_urls = ['https://rent.591.com.tw/?kind=0&region=1&order=posttime&orderType=desc']

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('chromedriver',options=options)
        self.region_dict = {'台北市': '1', '新北市': '3'}
        self.all_df = pd.DataFrame()

    def next_page(self,bool_gonext):
        time.sleep(1)
        btn_next_page = self.driver.find_element_by_css_selector('div.pageBar a.pageNext')
        href_next_page = self.driver.find_element_by_css_selector('div.pageBar a.pageNext').get_attribute('href')
        bool_next_page = (href_next_page != None)
        if (bool_next_page & bool_gonext):
            self.driver.execute_script("arguments[0].click();", btn_next_page)
            time.sleep(5)
            print('Loading Next Page ... ')
        
        current_page = self.driver.find_element_by_css_selector('div.pageBar span.pageCurrent')\
                             .get_attribute('innerText')
        return int(current_page), bool_next_page

    def extract_articles(self):
        time.sleep(1)
        ids =[x.get_attribute('data-bind') for x in  self.driver.find_elements_by_css_selector('ul.listInfo img')]
        titles =[x.get_attribute('title') for x in  self.driver.find_elements_by_css_selector('ul.listInfo img')]
        links =[x.get_attribute('href') for x in  self.driver.find_elements_by_css_selector('ul.listInfo h3 a')]
        col_names = ['id','title', 'link']
        # [ids[0], titles[0], links[0]]
        infos = list(map(list,(zip(ids, titles, links))))

        # [{'id':1, 'title':1, link:1}]
        return [dict(zip(col_names,info)) for info in infos]

    def switch_region(self,region_code):
        region_switch = self.driver.find_element_by_css_selector('span.search-location-span')
        self.driver.execute_script("arguments[0].click();", region_switch)
        btn_region = self.driver.find_element_by_css_selector('ul li.city-li a[data-id="{}"]'.format(region_code))
        self.driver.execute_script("arguments[0].click();", btn_region)
        self.driver.refresh()
        time.sleep(3)
        print('current url : {}'.format(self.driver.current_url))

    def region_crawler(self, key):
        print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',key)
        _, bool_next_page = self.next_page(bool_gonext=False) 
        while bool_next_page:
            item = pageIndexItem()
            list_info = self.extract_articles()
            for info in list_info:
                item['id'] = info['id']
                item['title'] = info['title']
                item['link'] = info['link']
                item['region'] = key
                yield item
            _, bool_next_page = self.next_page(bool_gonext=True)
    
    def parse(self, response):
        self.driver.get(response.url)
        #Region could right at where you crawl
        current_url = self.driver.current_url
        current_region = current_url.split('=')[-1]
        for key, value in self.region_dict.items():
            if(str(current_region) != str(value)):
                self.switch_region(value)
                print('From {} Switch To {}'.format(current_region,value))
            print('.............CRAWLING.............')
            _, bool_next_page = self.next_page(bool_gonext=False) 
            while bool_next_page:
                item = pageIndexItem()
                list_info = self.extract_articles()
                for info in list_info:
                    item['id'] = info['id']
                    item['title'] = info['title']
                    item['link'] = info['link']
                    item['region'] = key
                    yield item
                _, bool_next_page = self.next_page(bool_gonext=True)
