from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.macros import ds_add
import pendulum
from os.path import join
import pandas as pd

def extrai_dados(data_interval_end):
    # intervalo de datas
    city = 'Boston'
    key = 'DZPQZ6LW9F7655AMW56DNHSMK'

    url = join('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
        ,f'{city}/{data_interval_end}/{ds_add(data_interval_end,7)}?unitGroup=metric&include=days&key={key}&contentType=csv'
    )

    file_path = f'/files/semana={data_interval_end}/'

    dados = pd.read_csv(url)
    dados.to_csv(file_path + 'dados_brutos.csv')
    dados[['datetime','tempmin', 'temp', 'tempmax']].to_csv(file_path + 'temperaturas.csv')
    dados[['datetime', 'description', 'icon']].to_csv(file_path + 'condicoes.csv')


with DAG(
    'dados_climativos',
    start_date= pendulum.datetime(2023, 6, 26, tz = 'UTC'),
    schedule_interval= '0 0 * * 1',
) as dag:
    tarefa_1 = BashOperator(
        task_id= 'cria_pasta',
        bash_command= 'mkdir -p "/files/semana={{data_interval_end.strftime("%Y-%m-%d")}}"'
    )
    tarefa_2 = PythonOperator(
        task_id = 'extrai_dados',
        python_callable= extrai_dados,
        op_kwargs= {
            'data_interval_end': '{{data_interval_end.strftime("%Y-%m-%d")}}'
        }
    )

    tarefa_1 >> tarefa_2