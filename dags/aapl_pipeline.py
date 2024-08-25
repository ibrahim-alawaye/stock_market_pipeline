from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.sensors.base import PokeReturnValue
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests

from include.stock_market.pipeline_tasks import _get_stock_prices, _store_raw_data

SYMBOL = 'AAPL'
@dag(
    start_date=datetime(2024, 5, 2),
    schedule='@daily',
    catchup=False,
    tags=['aapl_stock_market']
)
def stock_market():

    @task.sensor(poke_interval=30, timeout=300, mode='poke')
    def check_api() -> PokeReturnValue:
        api = BaseHook.get_connection('stock_api')
        url = f"{api.host}{api.extra_dejson['endpoint']}"
        response = requests.get(url, headers=api.extra_dejson['headers'])
        condition = response.json()['finance']['result'] is None
        return PokeReturnValue(is_done=condition, xcom_value=url)
    
    get_stock_prices = PythonOperator(
        task_id="get_stock_prices",
        python_callable=_get_stock_prices,
        op_kwargs={'url': '{{task_instance.xcom_pull(task_ids="check_api") }}', 'symbol': SYMBOL}
    )
    
    store_raw_data = PythonOperator(
        task_id="store_raw_data",
        op_kwargs={'stock': '{{task_instance.xcom_pull(task_ids="get_stock_prices") }}'},
        python_callable=_store_raw_data
    )

    check_api() >> get_stock_prices >> store_raw_data

stock_market()

