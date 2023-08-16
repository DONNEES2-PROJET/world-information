from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = {ACCESS_KEY}
SECRET_KEY = {SECRET_KEY}
BUCKET_NAME = 'projet.donnes'
FOLDER_NAME = 'input/'

def upload_to_s3(local_file, s3_file):

    try:
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        s3.upload_file(local_file, BUCKET_NAME, s3_file)
        print(f"{local_file} téléversé avec succès en tant que {s3_file}")
    except NoCredentialsError:
        print("Les informations d'identification AWS n'ont pas été trouvées.")

#deployer les fichier vers input dans S3
def deploy_to_input_s3():

    local_file_paths = ['country-data.csv', 'economics-data.csv', 'education-data.csv', 'environment-data.csv','health-data.csv','population-data.csv']

    for local_file in local_file_paths:
        s3_file = FOLDER_NAME + local_file.split('/')[-1]
        upload_to_s3(local_file, s3_file)

def upload_to_output_s3():
    education_data = pd.read_csv('./education-data.csv')
    health_data = pd.read_csv('./health-data.csv')
    environment_data = pd.read_csv('./environment-data.csv')
    economics_data = pd.read_csv('./economics-data.csv')
    population_data = pd.read_csv('./population-data.csv')
    country_data = pd.read_csv('./country-data.csv')
    # Perform transformations
    merged_data = country_data.merge(education_data, on='Country', how='outer')
    merged_data = merged_data.merge(health_data, on='Country', how='outer')
    merged_data = merged_data.merge(environment_data, on='Country', how='outer')
    merged_data = merged_data.merge(economics_data, on='Country', how='outer')
    merged_data = merged_data.merge(population_data, on='Country', how='outer')
    
    # Save processed data to CSV
    output_filename = f"sujet_{datetime.now().strftime('%d_%m_%Y')}.csv"
    merged_data.to_csv(output_filename)
    
    # Upload to S3
    s3_file = 'output/' + output_filename
    upload_to_s3(output_filename, s3_file)

    

with DAG(
    'world_information',
    default_args={
        "depends_on_past": False,
        "email": ["hei.miaritiana@gmail.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="A simple tutorial DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2023, 8, 14),
    end_date=datetime(2023,12,31),
    catchup=False,
    tags=["world information"],
) as dag:
    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    ),
    t2 = PythonOperator(
        task_id="upload_to_input_s3",
        python_callable=deploy_to_input_s3,
        dag=dag
    )
    t3 = PythonOperator(
        task_id="upload_to_output_s3",
        python_callable=upload_to_output_s3,
        dag=dag
    )
    
#Ordonner les taches
t1>>t2>>t3