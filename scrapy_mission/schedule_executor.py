import time
import scrapy
from scrapy.crawler import CrawlerProcess
from spiders.hermes_spider import HermesSpider
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import deferLater

def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)


process = CrawlerProcess(get_project_settings())

def _crawl(result, spider):
    deferred = process.crawl(spider)
    deferred.addCallback(lambda results: print('waiting 300 seconds before restart...'))
    deferred.addCallback(sleep, seconds=300)
    deferred.addCallback(_crawl, spider)
    return deferred


_crawl(None, HermesSpider)
process.start()
