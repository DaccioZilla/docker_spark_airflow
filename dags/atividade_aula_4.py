from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator

def cumprimentos():
        print("Boas-vindas ao Airflow!")

with DAG(
    'atividade_aula_4',
    start_date= days_ago(1),
    schedule_interval= '@daily'
) as dag:
    tarefa_1 = PythonOperator(task_id='cumprimentos', python_callable= cumprimentos)

    tarefa_1 