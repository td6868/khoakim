import random
import string

import requests
import base64
from woocommerce import API

def test_api_wp():
    username = 'Test1'
    password = 'Testpass1'
    name = "Test Name"
    first_name = "Test first name"
    last_name = "Test last name"
    email = 'thang@thang.com'
    url = 'https://thangdt.xyz/wp-json/wp/v2/users'
    pass_app = "thang@123456789"
    user_app = "thangdao"

    new_user = {
        "username": username,
        "password": password,
        "name": name,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "roles": "daily1"
    }

    r = requests.post(url, auth=(user_app, pass_app), json=new_user)
    print(r)

def test_api_2():
    user = 'thangdao'
    pas = 'MTry bpf1 1uTW 04Oc pt9w nbnV'
    creds = user + ':' + pas
    token = base64.b64encode(creds.encode())
    header = {'Authorization': 'TEST API ' + token.decode('utf-8')}
    url = 'http://thangdt.xyz/wp-json/wp/v2/'
    post ={
            "date": "2022-01-01T10:00:00",
            "title": "Test API 1",
            "content": "Test Content",
            "status": "publish"
        }
    r = requests.post(url + 'posts', headers=header, json=post)
    # r1 = requests.get(url)
    print(r.json())
    # print(r1.json())

def woocommerce_test_api():
    wcapi = API(
        url="http://thangdt.xyz",
        consumer_key="ck_a7fc5c9a7fe977514c17234a70d725303392a6fd",
        consumer_secret="cs_b5b7196d55a5593d05f2e65c68439b16d65a8e21",
        version="wc/v3"
    )
    for i in range(10):
        data = {
            "name": "Premium Quality 1",
            "type": "simple",
            "regular_price": "21.99",
            "description": "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum tortor quam, feugiat vitae, ultricies eget, tempor sit amet, ante. Donec eu libero sit amet quam egestas semper. Aenean ultricies mi vitae est. Mauris placerat eleifend leo.",
            "short_description": "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.",
            "manage_stock": 1,
            "stock_quantity": "10",
            "sku": "092304930",
            "categories": [
                {
                    "id": 9
                },
                {
                    "id": 14
                }
            ],
            "images": [
                {
                    "src": "http://demo.woothemes.com/woocommerce/wp-content/uploads/sites/56/2013/06/T_2_front.jpg"
                },
                {
                    "src": "http://demo.woothemes.com/woocommerce/wp-content/uploads/sites/56/2013/06/T_2_back.jpg"
                }
            ]
        }
        post = wcapi.post("products", data).json()
        print(post)

def random_char():
    c = string.ascii_lowercase + string.ascii_uppercase + string.digits
    r = random.choice(c)
    print(r)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    random_char()
