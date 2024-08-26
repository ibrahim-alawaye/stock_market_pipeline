from io import BytesIO
from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowNotFoundException
import requests
import json
from minio import Minio

    
endpoint = 'minio:9000'
access_key = 'minio'
secret_key = 'minio123'
BUCKET_NAME = "stock-prices"


def get_minio_client():
    client= Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )
    return client

def _get_stock_prices(url, symbol):
    url = f"{url}{symbol}?matrics=high?&interval=1d&range=1y"
    api = BaseHook.get_connection('stock_api')
    response = requests.get(url, headers=api.extra_dejson['headers'])
    return json.dumps(response.json()['chart']['result'][0])


def _store_raw_data(stock):
    client = get_minio_client()
    #minio = BaseHook.get_connection('minio_api')
    # client = Minio(
        #endpoint=minio.extra_dejson['endpoint_url'].split('//')[1],
        #access_key=minio.login,
        #secret_key=minio.password,
        #secure=False
        # Hardcoding MinIO credentials and URL

    
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
    stock_data = json.loads(stock)
    symbol = stock_data['meta']['symbol']
    data = json.dumps(stock_data, ensure_ascii=False).encode('utf8')
    objw = client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=f'{symbol}/prices.json',
        data=BytesIO(data),
        length=len(data)
    )
    return f'{objw.bucket_name}/{symbol}'

def _get_transformed_data(path):
    #path=f"{BUCKET_NAME}/AAPL/"
    client = get_minio_client()
    objects = client.list_objects(f'stock-prices', prefix='AAPL/formatted_prices/', recursive=True)
    csv_file = [obj for obj in objects if obj.object_name.endswith('.csv')][0]
    return f's3://{csv_file.bucket_name}/{csv_file.object_name}'


    #prefix_name = f"{path.split('/')[1]}/formatted_prices/"
    #objects = client.list_objects(BUCKET_NAME, prefix=prefix_name, recursive=True)
    #for obj in objects:
        #if obj.object_name.endswith('.csv'):
            #return obj.object_name
    #raise AirflowNotFoundException('File not found in the object folder')



