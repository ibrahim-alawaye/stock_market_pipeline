from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.sensors.base import PokeReturnValue
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from astro import sql as aql
from astro.files import File
from astro.sql.table import Table, Metadata
from datetime import datetime
import requests
import sqlalchemy

from include.stock_market.pipeline_tasks import _get_stock_prices, _store_raw_data, _get_transformed_data, BUCKET_NAME
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
        op_kwargs={'url': '{{ task_instance.xcom_pull(task_ids="check_api") }}', 'symbol': SYMBOL}
    )
    
    store_raw_data = PythonOperator(
        task_id="store_raw_data",
        op_kwargs={'stock': '{{ task_instance.xcom_pull(task_ids="get_stock_prices") }}'},
        python_callable=_store_raw_data
    )

    transform_prices = DockerOperator(
        task_id ='transform_prices',
        image='airflow/transform-stock',
        container_name='transform--prices',
        api_version='auto',
        auto_remove=True,
        docker_url='tcp://docker-proxy:2375',
        network_mode='container:spark-master',
        tty=True,
        xcom_all=False,
        mount_tmp_dir=False,
        environment={
            'SPARK_APPLICATION_ARGS': '{{ task_instance.xcom_pull(task_ids="store_raw_data") }}'
        }
    )

    get_transformed_data = PythonOperator(
        task_id='get_transformed_data',
        python_callable=_get_transformed_data,
        op_kwargs={
            'path': '{{ task_instance.xcom_pull(task_ids="store_raw_data") }}'
        }

    )
    
    load_data_postgres = aql.load_file(
        task_id='load_data_warehouse',
        input_file=File(path='{{ ti.xcom_pull(task_ids="get_transformed_data") }}',conn_id='minio'),
        output_table=Table(
            name='stock_market',
            conn_id='postgres',
            metadata=Metadata(
                schema='public'
            ),
            columns=[
                sqlalchemy.Column('timestamp', sqlalchemy.BigInteger, primary_key=True),
                sqlalchemy.Column('close', sqlalchemy.Float),
                sqlalchemy.Column('high', sqlalchemy.Float),
                sqlalchemy.Column('low', sqlalchemy.Float),
                sqlalchemy.Column('open', sqlalchemy.Float),
                sqlalchemy.Column('volume', sqlalchemy.Integer),
                sqlalchemy.Column('date', sqlalchemy.Date),
            ]
        )
    )


    check_api() >> get_stock_prices >> store_raw_data >> transform_prices >> get_transformed_data >> load_data_postgres

stock_market()
