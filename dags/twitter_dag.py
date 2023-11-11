from airflow.models import DAG
from airflow.utils.dates import days_ago
from operators.twitter_operator import TwitterOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from os.path import join

with DAG(dag_id = "TwitterDAG", start_date = days_ago(2), schedule_interval = '@daily') as dag:
    query = "datascience"
    twitter_extractor = TwitterOperator(file_path= join("bronze/twitter_datascience",
                                            "extract_date={{ ds }}",
                                            "datascience_{{ ds_nodash }}.json"
                                            ),
                        end_time = "{{ data_interval_end.strftime('%Y-%m-%dT%H:%M:%S.00Z') }}", 
                        start_time = "{{ data_interval_start.strftime('%Y-%m-%dT%H:%M:%S.00Z') }}", 
                        query= query, 
                        task_id = 'twitter_datascience')

    twitter_transform = SparkSubmitOperator(task_id = "transform_twitter_datascience",
                                           application="/files/spark/transformation.py",
                                           name = "twitter_transformation",
                                           application_args=["--source", "s3a://datalake/bronze/twitter_datascience" ,
                                                             "--dest", "s3a://datalake/silver",
                                                             "--process_date", "{{ ds }}"
                                                             ]
                                           )
    
    twitter_insight = SparkSubmitOperator(task_id = "twitter_insight",
                                           application="/files/spark/insight_twitter.py",
                                           name = "insight_twitter",
                                           application_args=["--source", "s3a://datalake/silver/tweets" ,
                                                             "--dest", "s3a://datalake/gold",
                                                             "--process_date", "{{ ds }}"
                                                             ]
                                           )

    twitter_extractor >> twitter_transform >> twitter_insight



    