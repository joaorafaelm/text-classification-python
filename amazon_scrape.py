from time import sleep
from lxml import html
import requests
import dataset
import csv
from threading import Thread
from queue import Queue
import sys
import random
import logging


logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(threadName)s %(message)s',
    level=logging.INFO
)


# Number of workers
THREADS = 30

# List of subdomains to use with gmodules.
PROXY_SUB = [
    'hosting', 'ig', '0.blogger', '1.blogger',
    'blogger', '0.open', '1.open', '2.open'
]

# Gmodules proxy url, you can set the cache time using the *refresh* param.
PROXY = 'gmodules.com/gadgets/proxy?refresh=0&' \
        'container=gplus&gadgets=http%3A%2F%2Forkut.com%2Fimg.xml&url='

# Amazon URL
URL = 'http://www.amazon.com/dp/'


# Strip a list of str and encode as utf8
def strip(str_list):
    str_list = [x.encode('utf-8') for x in str_list]
    return list(filter(None, map(lambda x: x.strip(), str_list)))


# Worker
def fetch():

    # One DB connection per thread,
    # bc I had too many issues using one instance shared between threads
    db_thread = dataset.connect('sqlite:///dataset.db')

    while True:
        if not q.empty():
            identifier = q.get()

            # Randomly selects a subdomain for gmodules
            subdomain = 'http://www.{}.'.format(random.choice(PROXY_SUB))
            page = requests.get(subdomain + PROXY + URL + identifier)

            try:
                doc = html.fromstring(page.content)

                # Product title
                name = strip(doc.xpath('//h1[@id="title"]//text()'))

                # List of the products category tree
                category = strip(
                    doc.xpath(
                        '//a[@class="a-link-normal a-color-tertiary"]//text()'
                    )
                )

                # List of features of the product
                features = strip(
                    doc.xpath(
                        '//div[@id="feature-bullets"]//'
                        'span[@class="a-list-item"]/text()'
                    )
                )

                # Description or editor review of the product
                description = strip(
                    doc.xpath('//div[@id="productDescription"]//p/text()')
                )

                # Grabs page title to detect if
                # amazon classified this request as a bot
                page_title = strip(
                    doc.xpath('//title/text()')
                )

                # Transform all lists into strings
                name = b' '.join(name) if name else ''
                category = b' > '.join(category) if category else ''
                features = b'. '.join(features) if features else ''
                description = b' '.join(description) if description else ''
                page_title = b''.join(page_title) if page_title else ''

                # data = {
                #     'identifier': identifier.decode('utf-8'),
                #     'name': name.decode('utf-8'),
                #     'category': category.decode('utf-8'),
                #     'features': features.decode('utf-8'),
                #     'description': description.decode('utf-8'),
                #     'status': str(page.status_code)
                # }
                #
                data = {
                    'identifier': identifier,
                    'name': name,
                    'category': category,
                    'features': features,
                    'description': description,
                    'status': str(page.status_code)
                }

                # Only add to database if the product has one
                # of the attributes: category, features, description or name
                # OR if the request status code is 404
                # and the title is not  "Robot Check".
                if any(
                        [category, features, description, name]
                ) or (
                    data.get('status') == '404' and page_title != 'Robot Check'
                ):

                    # Not using transaction bc of
                    # issues a ran into using sqlite on disk
                    db_thread['products'].insert(data)
                    logging.info('done fetching for {} - {} {}'.format(
                        URL + identifier, data.get('status'), page_title)
                    )

                else:
                    pass
                    # Amazon knows you are a bot.
                    # logging.info('done fetching for {} - {} {}'.format(
                    #     URL + identifier, '302', page_title)
                    # )

                    # The identifier should be put once again into the Queue.
                    # But the denial rate is bigger than task consumption.
                    # q.put(identifier)

                q.task_done()
                page.close()

            except Exception as e:
                logging.exception(e)

# Start queue prefetching number of threads * 2
q = Queue(THREADS * 2)

# Start workers
for i in range(THREADS):
    t = Thread(target=fetch)
    t.daemon = True
    t.start()

try:
    db = dataset.connect('sqlite:///dataset.db')

    # Create a dict of ASINS already fetched,
    # so it wont be fetched again.
    id_filter = {}
    id_filter = db.query('SELECT identifier FROM products')
    id_filter = {x['identifier']: True for x in id_filter}

    # Load csv with the ASINS.
    asins = csv.reader(open('asins.csv'), delimiter=',')
    for i in asins:

        # Discard fetched ASINS.
        if not id_filter.get(i[0], False):
            while True:

                # Add ASIN to the queue if it is not full.
                # **Queue size: threads x 2**
                if not q.full():
                    logging.info(
                        'enqueue request for {} - line: {} - qsize: {}'.format(
                            i[0],
                            asins.line_num,
                            q.qsize()
                        )
                    )
                    q.put(i[0])
                    break

                # Wait 3 seconds before trying to enqueue again
                sleep(3)

    q.join()

except KeyboardInterrupt:
    sys.exit(1)
