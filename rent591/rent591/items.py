from scrapy.item import Item,Field
import time
from selenium import webdriver

class rentPageItem(Item):
    row = Field()
class pageIndexItem(Item):
    id = Field()
    title = Field()
    link = Field()
    region = Field()
