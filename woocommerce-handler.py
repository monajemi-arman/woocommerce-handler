#!/usr/bin/env python
from woocommerce import API
import json

# API Config JSON path
config_json = 'config.json'


class WoocommerceHandler:
    def __init__(self, config_json):
        # Variables
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

    def get_items(self, name, item_id=None):
        if item_id:
            suffix = '/' + str(item_id)
        else:
            suffix = ''
        return self.wcapi.get(self.endpoints[name] + suffix).json()

    def get_orders(self):
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


def main():
    wch = WoocommerceHandler(config_json)



if __name__ == '__main__':
    main()
