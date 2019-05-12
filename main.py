import operator
import requests

from bs4 import BeautifulSoup
from typing import Dict, Set

class Page:
    def __init__(self, title, url, views=0):
        self.title = title
        self.url = url
        self.views = views

    def __eq__(self, other):
        if isinstance(other, Page):
            return self.url == other.url
        return False

    def __hash__(self):
        return hash(self.url)

class AnchorPage:
  def __init__(self, title, views, link_heres):
    self.title = title
    self.views = views
    self.link_heres = link_heres

def fetch_pages_that_link_here(page_title: str) -> Set[Page]:
    def process_link_heres(url: str) -> Dict[str, str]:
        print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        body = soup.find("div", {"id": "bodyContent"})

        links_here = {}
        next_page = None
        for link in body.find_all('a'):
            href = link["href"]
            if "/wiki/" in href:
                links_here[href] = link.text
            elif "next 500" in link.text:
                next_page = 'https://en.m.wikipedia.org' + href

        if next_page:
            next_page_links_here = process_link_heres(next_page)
            links_here.update(next_page_links_here)
        
        return links_here

    inital_url = 'https://en.m.wikipedia.org/w/index.php?title=Special:WhatLinksHere/' + page_title + '&namespace=0&limit=500&hidetrans=1&hideredirs=1'
    link_heres = process_link_heres(inital_url)

    pages = []
    for url, title in link_heres.items():
        pages.append(Page(title=title, url=url))
    return set(pages)

def fetch_page_views(page_title: str) -> int:
    url = 'https://en.wikipedia.org/w/index.php?title=' + page_title + '&action=info'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    elements = soup.findAll("div", {"class": "mw-pvi-month"})
    if len(elements) > 0:
        return int(elements[0].text.replace(",", ""))
    return 0



title = "Apple_Inc."
apple_page = AnchorPage(
    title=title,
    views=fetch_page_views(page_title=title),
    link_heres=fetch_pages_that_link_here(page_title=title)
)
title = "Microsoft"
microsoft_page = AnchorPage(
    title=title,
    views=fetch_page_views(page_title=title),
    link_heres=fetch_pages_that_link_here(page_title=title)
)

import threading
from queue import Queue

print_lock = threading.Lock()

def print_top_overlaps(page_one: AnchorPage, page_two: AnchorPage):

    page_queue = Queue()

    def threaded_fetch_page_views(page: Page):
        with print_lock:
            print("\nStarting thread {}".format(threading.current_thread().name))
        page.views = fetch_page_views(page.title.replace("/wiki/", ""))
        with print_lock:
            print("\nFinished thread {}".format(threading.current_thread().name))
    
    def process_queue():
        while True:
            print("Queue size: " + str(page_queue.qsize()))
            current_page = page_queue.get()
            threaded_fetch_page_views(page=current_page)
            page_queue.task_done()
    
    for i in range(10):
        t = threading.Thread(target=process_queue)
        t.daemon = True
        t.start()

    overlap = page_one.link_heres.intersection(page_two.link_heres)
    for page in overlap:
        page_queue.put(page)
    page_queue.join()

    print(threading.enumerate())


    print("=========\nTop viewed overlap pages: ")
    for page in reversed(sorted(overlap, key=operator.attrgetter('views'))):
        print(page.title + ": " + str(page.views))


print_top_overlaps(page_one=apple_page, page_two=microsoft_page)