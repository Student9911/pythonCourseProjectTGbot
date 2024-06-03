# В этом файле почти вся логика связанная с базой данных
from telebot import types
import os
import logging
import boto3
from botocore.exceptions import ClientError


# Функция подсчета пользователей
def count_users(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.environ.get('USER_STORAGE_URL'),
            region_name='us-east-1',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    table = dynamodb.Table('Users')
    try:
        response = table.scan()
    except ClientError as e:
        logging.error(e.response['Error']['Message'])
        return "Произошла ошибка при подсчете пользователей."
    else:
        return len(response['Items'])


# Функция для отправки сообщения от админа всем пользователям из базы данных
def send_message_to_all_users(message_text, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.environ.get('USER_STORAGE_URL'),
            region_name='us-east-1',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    table = dynamodb.Table('Users')
    response = table.scan()
    remove_keyboard = types.ReplyKeyboardRemove()
    for item in response['Items']:

        try:

            bot.send_message(int(item['user_id']), str(item[
                                                           'first_name']) + ", " + message_text + "\n\n\n\nесли вы больше не хотите получать рассылку\nотправьте сообщение с текстом 'Отписаться'",
                             reply_markup=remove_keyboard)


        except Exception as e:
            logging.error(e)


def read_user(user_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.environ.get('USER_STORAGE_URL'),
            region_name='us-east-1',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    table = dynamodb.Table('Users')
    try:
        response = table.get_item(Key={'user_id': str(user_id)})
    except ClientError as e:
        logging.error(e.response['Error']['Message'])
        return None
    else:
        return response.get('Item')


def create_user(user_id, first_name, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.environ.get('USER_STORAGE_URL'),
            region_name='us-east-1',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )

    table = dynamodb.Table('Users')
    try:
        response = table.put_item(
            Item={
                'user_id': str(user_id),
                'first_name': str(first_name)
            }
        )
    except ClientError as e:
        logging.error(e.response['Error']['Message'])
        return "Произошла ошибка при подписке. Попробуйте еще раз позже."
    else:
        return "Вы успешно подписались на новостную рассылку!"


def delete_user(user_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.environ.get('USER_STORAGE_URL'),
            region_name='us-east-1',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    try:
        response = dynamodb.Table('Users').delete_item(Key={'user_id': str(user_id)})
    except ClientError as e:
        logging.error(e.response['Error']['Message'])
        return "Произошла ошибка при отписке. Попробуйте еще раз позже."
    else:
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return "Вы успешно отписались от новостной рассылки.\nЕсли вы передумали, отправьте повторно \n/start"
        else:
            return "Произошла ошибка при отписке. Попробуйте еще раз позже."