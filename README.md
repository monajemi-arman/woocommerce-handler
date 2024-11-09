# WooCommerce Handler
A WooCommerce Handler python module written using the original WooCommerce Python module.  
The order listener is a key feature of this module. It checks new orders on intervals. The order is processed and the products and name of customer is passed to a given function.

# Installation
* Clone this repository
```bash
git clone https://github.com/monajemi-arman/woocommerce-handler
```
* Install as python module
```bash
cd woocommerce-handler
python -m pip install -e .
```

# Usage
* Prepare config.json with following content, name it 'config.json'.
```json
{
  "url": "URL TO YOUR SITE",
  "consumer_key": "CHANGE THIS",
  "consumer_secret": "CHANGE THIS",
  "interval": 20
}
```

* Load handler
```python
from woocommerce_handler import WoocommerceHandler

wch = WoocommerceHandler('config.json')
```

* Use order listener
The order listener receives a function to pass each order to it for further processing.
```python
def custom_printer(order_object):
    print("New order received!", order_object)

wch.listen_orders(custom_printer)
```

* WooCommerce API actions wrapped in simple to use functions
```python
wch.get_orders()  # Get all orders
wch.get_orders(after='2024-11-06T18:42:15')  # Get all orders after some time
wch.get_product(order_id)  # Get order with specific id
wch.get_products()  # Get all products
wch.get_product(product_id)  # Get product with specific id
wch.update_price(product_id, price)  # Change product price
wch.update_stock(self, product_id, stock)  # Change product stock amount
```

