#!/usr/bin/env python
import json
import os
from woocommerce import API

# API Config JSON path (MUST EXIST, make from config.json.default)
config_json = 'config.json'

# App data save to JSON (should not exist on first run)
app_data_path = 'app-data.json'


class WoocommerceHandler:
    def __init__(self, config_json, app_data_path=app_data_path):
        # Variables
        self.app_data_vars = {
            'last_order_time': 'last_order_time'
        }
        self.app_data_vars_default = {
            'last_order_time': '2024-01-01T00:00:00'
        }
        self.app_data = self.AppData(app_data_path, defaults=self.app_data_vars_default)
        self.endpoints = {
            'products': 'products',
            'orders': 'orders'
        }
        self.property_names = {
            'price': ['price', 'regular_price'],
            'sale_price': 'sale_price',
            'stock_quantity': 'stock_quantity',
            'manage_stock': 'manage_stock',
            'customer_id': 'customer_id',
            'billing': 'billing',
            'line_items': 'line_items'
        }
        self.templates = {
            'order': {
                'products': [],
                'customer': {'id': '', 'name': ''}
            }
        }

        with open(config_json) as f:
            config = json.load(f)

        self.wcapi = API(
            url=config["url"],
            consumer_key=config["consumer_key"],
            consumer_secret=config["consumer_secret"],
            version="wc/v3"
        )

    class AppData:
        def __init__(self, app_data_path, defaults={}):
            self.app_data_path = app_data_path
            self.defaults = defaults
            if not os.path.exists(self.app_data_path):
                self.initialize()

        def initialize(self):
            with open(self.app_data_path, 'w') as f:
                json.dump(self.defaults, f)

        def load(self):
            with open(self.app_data_path) as f:
                self.data = json.load(f)

        def save(self):
            with open(self.app_data_path, 'w') as f:
                json.dump(self.data, f)

        def get(self, key):
            self.load()
            return self.data.get(key)

        def set(self, key, value):
            self.load()
            self.data[key] = value
            self.save()

    def get_items(self, name, item_id=None, params=None):
        if item_id:
            suffix = '/' + str(item_id)
        else:
            suffix = ''
        if params:
            return self.wcapi.get(self.endpoints[name] + suffix, params=params).json()
        else:
            return self.wcapi.get(self.endpoints[name] + suffix).json()

    def get_orders(self, after=None):
        if after:
            return self.get_items('orders', params={'after': after})
        else:
            return self.get_items('orders')

    def get_order(self, order_id):
        order_raw = self.get_items('orders', order_id)
        # Customer info
        order = self.templates['order']
        order['customer']['id'] = order_raw.get(self.property_names['customer_id'])
        billing = order_raw.get(self.property_names['billing'])
        if billing:
            order['customer']['name'] = billing['first_name'] + ' ' + billing['last_name']
        # Product list with amount
        order['products'] = []
        line_items = order_raw.get(self.property_names['line_items'])
        for line_item in line_items:
            product_id = line_item['product_id']
            quantity = line_item['quantity']
            order['products'].append([product_id, quantity])
        return order

    def get_products(self):
        return self.get_items('products')

    def get_product(self, product_id):
        return self.get_items('products', product_id)

    def update_product(self, product_id, property_key_value):
        return self.wcapi.put(self.endpoints['products'] + '/' + str(product_id), property_key_value)

    def update_price(self, product_id, price, sale_price=None):
        price = str(price)
        property_key_value = {}
        for name in self.property_names['price']:
            property_key_value[name] = price
        if sale_price:
            property_key_value['sale_price'] = sale_price
        return self.update_product(product_id, property_key_value)

    def update_stock(self, product_id, stock):
        property_key_value = {self.property_names['stock_quantity']: stock,
                              self.property_names['manage_stock']: True}
        return self.update_product(product_id, property_key_value)

    @property
    def last_order_time(self):
        return self.app_data.get(self.app_data_vars['last_order_time'])

    @last_order_time.setter
    def last_order_time(self, newtime):
        self.app_data.set(self.app_data_vars['last_order_time'], newtime)


def main():
    wch = WoocommerceHandler(config_json)
    print(wch.last_order_time)


if __name__ == '__main__':
    main()
