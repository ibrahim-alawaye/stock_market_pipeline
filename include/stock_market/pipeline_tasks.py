from io import BytesIO
from airflow.hooks.base import BaseHook
import requests
import json
from minio import Minio

def _get_stock_prices(url, symbol):
    url = f"{url}{symbol}?matrics=high?&interval=1d&range=1y"
    api = BaseHook.get_connection('stock_api')
    response = requests.get(url, headers=api.extra_dejson['headers'])
    return json.dumps(response.json()['chart']['result'][0])


def _store_raw_data(stock):
    minio = BaseHook.get_connection('minio_api')
    # client = Minio(
        #endpoint=minio.extra_dejson['endpoint_url'].split('//')[1],
        #access_key=minio.login,
        #secret_key=minio.password,
        #secure=False
        # Hardcoding MinIO credentials and URL
    endpoint = 'minio:9000'
    access_key = 'minio'
    secret_key = 'minio123'
    
    client = Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )
    bucket_name = "stock-prices"
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    stock_data = json.loads(stock)
    symbol = stock_data['meta']['symbol']
    data = json.dumps(stock_data, ensure_ascii=False).encode('utf8')
    objw = client.put_object(
        bucket_name=bucket_name,
        object_name=f'{symbol}/prices.json',
        data=BytesIO(data),
        length=len(data)
    )
    return f'{objw.bucket_name}/{symbol}'