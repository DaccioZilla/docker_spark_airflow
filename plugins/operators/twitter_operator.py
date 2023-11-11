from airflow.models import BaseOperator, DAG, TaskInstance
from os.path import join
from hooks.twitter_hook import TwitterHook
import json
from datetime import datetime, timedelta
from pathlib import Path
from minio import Minio
import urllib3
import os
import io

class TwitterOperator(BaseOperator):

    template_fields = ["query", "object_name", "start_time", "end_time"]

    minio_config = {
        "dest_bucket":    "datalake", # This will be auto created
        "minio_endpoint": os.environ.get('MINIO_API_HOST'),
        "minio_username": os.environ.get('MINIO_ACCESS_KEY'),
        "minio_password": os.environ.get('MINIO_SECRET_KEY'),
    }

    # Since we are using self-signed certs we need to disable TLS verification

    # Initialize MinIO client
    minio_client = Minio(minio_config["minio_endpoint"],
                secure = False,
                access_key=minio_config["minio_username"],
                secret_key=minio_config["minio_password"],
                )

    def __init__(self, file_path, end_time, start_time, query, **kwargs):
        self.object_name = file_path
        self.end_time = end_time
        self.start_time = start_time
        self.query = query
        super().__init__(**kwargs)

    def execute(self, context):
        with io.StringIO() as output_file:
            for pg in TwitterHook(self.end_time, self.start_time, self.query).run():
                output_file.write(json.dumps(pg))
            output_file.seek(0)
            texto = output_file.read()

            data_bytes = texto.encode('utf-8')
        data_stream = io.BytesIO(data_bytes)
        print(data_stream)

        TwitterOperator.minio_client.put_object(TwitterOperator.minio_config["dest_bucket"], self.object_name, data=data_stream, length=len(data_bytes), content_type='application/json')
        


if __name__ == "__main__":
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.00Z"
    end_time = datetime.now().strftime(TIMESTAMP_FORMAT)
    start_time = (datetime.now() + timedelta(-1)).date().strftime(TIMESTAMP_FORMAT)
    query = "datascience"

    with DAG(dag_id = "TwitterTest", start_date = datetime.now()) as dag:
        to = TwitterOperator(file_path = join("twitter_datascience",
                                              f"extract_date={datetime.now().date()}",
                                              f"datascience{datetime.now().date().strftime('%Y%m%d')}.json"
                                              ),
                            end_time = end_time, start_time = start_time, query= query, task_id = 'test_run')
        ti = TaskInstance(task = to)
        to.execute(ti.task_id)