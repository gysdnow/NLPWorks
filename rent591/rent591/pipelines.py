import datetime
from pymongo import MongoClient
from rent591.items import rentPageItem ,pageIndexItem

class MongoDBPipeline:

    def open_spider(self,spider):
        db_uri = spider.settings.get('MONGODB_URI','mongodb://localhost:27017')
        db_name = spider.settings.get('MONGODB_DB_NAME', 'rent')
        self.db_client = MongoClient('mongodb://localhost:27017')
        self.db = self.db_client[db_name]
    
    def process_item(self, item, spider):
        if isinstance(item,rentPageItem):
            self.db.pageContent.insert_one(dict(item))
        if isinstance(item,pageIndexItem):
            self.db.pageIndex.insert_one(dict(item))

    def close_spider(self, spider):
        self.db_client.close()
