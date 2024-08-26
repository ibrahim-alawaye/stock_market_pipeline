from airflow.decorators import dag
from airflow.utils.dates import days_ago
from astro import sql as aql
from astro.files import File
from astro.sql.table import Table, Metadata

from include.stock_market.pipeline_tasks import get_minio_client
bucket_name='stock-market'


@aql.transform
def _get_transformed_data(path):
    client = get_minio_client()
    prefix_name = f"{path.split('/')[1]}/formatted_prices/"
    objects = client.list_objects(bucket_name, prefix=prefix_name, recursive=True)
    for obj in objects:
        if obj.object_name.endswith('.csv'):
            return obj.object_name
    raise AirflowNotFoundException('File not found in the object folder')

@dag(schedule_interval=None, start_date=days_ago(1))
def minio_to_postgres_dag():

    # Pull the file path from MinIO
    file_path = _get_transformed_data("AAPL/formatted_prices")

    # Load data into PostgreSQL
    load_data_postgres = aql.load_file(
        task_id='load_data_warehouse',
        input_file=File(
            path=f"s3://{bucket_name}/{file_path}", 
            conn_id='minio',
            filetype="csv"  # Ensure the filetype is specified correctly
        ),
        output_table=Table(
            name='stock_market',
            conn_id='postgres',
            metadata=Metadata(
                schema='public'
            )
        )
    )

    load_data_postgres

dag = minio_to_postgres_dag()
