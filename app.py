#!/usr/bin/python
# -*- coding: utf8 -*-
import random
from lib2to3.pgen2.grammar import line
from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import json
from flask import jsonify
from requests.packages import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


__name__ = '__main__'
app = Flask(__name__)

def get_num(s):
    if isinstance(s, int): s = str(s)

    amount = None
    currency = ''
    multiplier = 1.0

    for token in s.split(' '):

        token = token.lower()

        if token in ['$', '€', '£', '¥']:
            currency = token

        # Extract multipliers from their string names/abbrevs
        if token in ['million', 'm', 'mm']:
            multiplier = 1e6
        # ... or you could use a dict:
        # multiplier = {'million': 1e6, 'm': 1e6...}.get(token, 1.0)

        # Assume anything else is some string format of number/int/float/scientific
        try:
            token = token.replace(',', '')
            amount = float(token)
        except:
            pass  # Process your parse failures...

    # Return a tuple, or whatever you prefer
    op = currency, amount * multiplier
    return op[1]
    
@app.route('/trends/<qur>')
def search(qur):
    websites = [
        ['https://fashionbug.lk/?s={keyword}&post_type=product'.format(keyword=qur), 'li.product', 'men', "Fashion Bug",
         10, "https://fashionbug.lk"],
        ['https://hameedia.com/index.php?search={keyword}&route=product%2Fsearch'.format(keyword=qur), '.product-tile',
         'men', 'Hameedia', 10, "https://hameedia.com"],
        ['https://www.nilsonline.lk/index.php?route=product/search&search={keyword}'.format(keyword=qur),
         '.product-thumb', 'women', 'Nils Store', 10, "https://www.nilsonline.lk/"],
        ['https://www.beverlystreet.lk/catalogsearch/result/?q={keyword}'.format(keyword=qur),
         '.products-grid .product-block', 'men', 'Beverly Street', 10,
         "https://www.beverlystreet.lk"],
        ['https://gflock.lk/search?type=product&q={keyword}'.format(keyword=qur), '.thumbnail', 'women', 'GF lock', 10,
         "https://gflock.lk"]
    ]
    body = []
    selectors = [
        ['.woocommerce-loop-product__title', 'title', 'text'],
        ['.woocommerce-Price-amount', 'price', 'number'],
        ['.woocommerce-LoopProduct-link', 'link', 'href', False],
        ['li.product a img', 'image', 'src', False],
        ['.product-name', 'title', 'text'],
        ['.name-link', 'link', 'href', False],
        ['.product-sales-price', 'price', 'number'],
        ['.orig', 'image', 'src', False],
        ['.product-thumb h4', 'title', 'text'],
        ['.product-thumb .price', 'price', 'number'],
        ['.product-thumb h4 a', 'link', 'href', False],
        ['.product-thumb .image img', 'image', 'src', True],
        ['.product-block .product-info .product-name a', 'title', 'text'],
        ['.product-block .product-info .product-name a', 'link', 'href', False],
        ['.price-box .price', 'price', 'number'],
        ['.products-grid .product-image img', 'image', 'src', False],
        ['.thumbnail .info .title', 'title', 'text'],
        ['.thumbnail .info .price', 'price', 'number'],
        ['.thumbnail a', 'link', 'href', True],
        ['.thumbnail img', 'image', 'src', False]
    ]

    for web in websites:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        try:
            r = requests.get(web[0], headers=headers, verify=False)
        except:
            continue
        if r:
            body.append(r)
    result = []
    for i, content in enumerate(body, 0):
        soup = BeautifulSoup(content.text, 'lxml')
        all_items = soup.select(websites[i][1])
        shop = websites[i][3]
        ab_url = websites[i][5]
        if all_items:
            all_items = all_items[:websites[i][4]]

            for x, row in enumerate(all_items, 0):
                cols = {}
                for tags in selectors:
                    if row.select(tags[0]):
                        datatype = tags[2]
                        if datatype == "text":
                            txt = row.select_one(tags[0]).text.replace('  ', '')
                            txt1 = txt.replace('\n', '')
                            txt2 = txt1.replace('\r', '')

                            cols[tags[1]] = txt2
                        elif datatype == "number":
                            p = row.select_one(tags[0]).text
                            cols[tags[1]] = get_num(p)
                        else:
                            if tags[3]:
                                cols[tags[1]] = ab_url + row.select_one(tags[0])[datatype]
                            else:
                                cols[tags[1]] = row.select_one(tags[0])[datatype]

                cols["shop"] = shop
                result.append(cols)
            
    random.shuffle(result)
    final = {'total': len(result), 'trends': result}
    return jsonify(final)
    
@app.route('/trends')
def dress():
    websites = [
        ['https://fashionbug.lk/product-category/men/', 'li.product', 'men', "Fashion Bug", 5, "https://fashionbug.lk"],
        ['https://fashionbug.lk/product-category/women/', 'li.product', 'women', "Fashion Bug", 5,
         "https://fashionbug.lk"],
        ['https://fashionbug.lk/product-category/kids-baby/', 'li.product', 'kids', "Fashion Bug", 5,
         "https://fashionbug.lk"],
        ['https://hameedia.com/apparel/', '.product-tile', 'men', 'Hameedia', 5, "https://hameedia.com"],
        ['https://www.nilsonline.lk/new-in', '.product-thumb', 'women', 'Nils Store', 5, "https://www.nilsonline.lk"],
        ['https://www.beverlystreet.lk/menswear.html', '.products-grid .product-block', 'men', 'Beverly Street', 5,
         "https://www.beverlystreet.lk"],
        ['https://www.beverlystreet.lk/womenswear.html', '.products-grid .product-block', 'women', 'Beverly Street', 5,
         "https://www.beverlystreet.lk"],
        ['https://gflock.lk/collections/women-all', '.thumbnail', 'women', 'GF lock', 5, "https://gflock.lk"],
        ['https://gflock.lk/collections/mens-all', '.thumbnail', 'men', 'GF lock', 5, "https://gflock.lk"]
    ]
    body = []
    selectors = [
        ['.woocommerce-loop-product__title', 'title', 'text'],
        ['.woocommerce-Price-amount', 'price', 'number'],
        ['.woocommerce-LoopProduct-link', 'link', 'href', False],
        ['li.product a img', 'image', 'src', False],
        ['.product-name', 'title', 'text'],
        ['.name-link', 'link', 'href', False],
        ['.product-sales-price', 'price', 'number'],
        ['.orig', 'image', 'src', False],
        ['.product-thumb h4', 'title', 'text'],
        ['.product-thumb .price', 'price', 'number'],
        ['.product-thumb h4 a', 'link', 'href', False],
        ['.carousel-inner>.active a img', 'image', 'src', True],
        ['.product-block .product-info .product-name a', 'title', 'text'],
        ['.product-block .product-info .product-name a', 'link', 'href', False],
        ['.price-box .price', 'price', 'number'],
        ['.products-grid .product-image img', 'image', 'src', False],
        ['.thumbnail .info .title', 'title', 'text'],
        ['.thumbnail .info .price', 'price', 'number'],
        ['.thumbnail a', 'link', 'href', True],
        ['.thumbnail img', 'image', 'src', False]
    ]

    for web in websites:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        try:
            r = requests.get(web[0], headers=headers, verify=False)
        except:
            continue

        if r:
            body.append(r)
    result = []
    for i, content in enumerate(body, 0):
        soup = BeautifulSoup(content.text, 'lxml')
        all_items = soup.select(websites[i][1])
        cat = websites[i][2]
        shop = websites[i][3]
        ab_url = websites[i][5]
        if all_items:
            all_items = all_items[:websites[i][4]]

            for x, row in enumerate(all_items, 0):
                cols = {}
                for tags in selectors:
                    if row.select(tags[0]):
                        datatype = tags[2]
                        if datatype == "text":
                            txt = row.select_one(tags[0]).text.replace('  ', '')
                            txt1 = txt.replace('\n', '')
                            txt2 = txt1.replace('\r', '')

                            cols[tags[1]] = txt2
                        elif datatype == "number":
                            p = row.select_one(tags[0]).text
                            cols[tags[1]] = get_num(p)
                        else:
                            if tags[3]:
                                cols[tags[1]] = ab_url + row.select_one(tags[0])[datatype]
                            else:
                                cols[tags[1]] = row.select_one(tags[0])[datatype]

                cols["category"] = cat
                cols["shop"] = shop
                result.append(cols)


    random.shuffle(result)
    final = {'total': len(result),'trends': result}
    return jsonify(final)


@app.route('/')
def main():
    data ={'Version': 1.0}
    paths = []
    paths.append('/trends')
    links = {'API': data, 'Paths': paths}
    return jsonify(links)
	
	
if __name__ == '__main__':
    app.run()


