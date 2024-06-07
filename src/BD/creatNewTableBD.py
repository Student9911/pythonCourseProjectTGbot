import boto3
import os

#  Создаем функцию с именем create_user_table,
#  которая будет использоваться для создания таблицы в DynamoDB.
def create_user_table():
    # Инициализация клиента DynamoDB с помощью boto3.resource.
    # Здесь используются переменные окружения, такие как ENDURL, AWS_ID и AWS_KEY,
    # чтобы получить доступ к учетным данным AWS и URL конечной точки DynamoDB.
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('ENDURL'),
        region_name = 'us-east-1',
        aws_access_key_id = os.getenv('AWS_ID'),
        aws_secret_access_key = os.getenv('AWS_KEY')
        )
    # Вызов метода dynamodb.create_table() для создания таблицы с именем "Users" в DynamoDB.
    # Определение основного ключа (Primary Key) для таблицы. В данном случае используется атрибут "user_id" в качестве хэш-ключа (Partition Key).
    # Определение атрибута "user_id" с типом данных строка (AttributeType: 'S').
    table = dynamodb.create_table(
        TableName = 'Users',
        KeySchema=[
            {
                'AttributeName': 'user_id',
                'KeyType': 'HASH' # Partition key
            }
        ],
        AttributeDefinitions=[
            {'AttributeName': 'user_id', 'AttributeType': 'S'}
        ]
    )
    return table
# вызываем функцию create_user_table() для создания таблицы "Users" в DynamoDB.
create_user_table()