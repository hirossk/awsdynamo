import boto3
from boto3.dynamodb.types import TypeDeserializer

# テーブル名の設定
TODO_TABLE = "TodoTable"  # TODOリストを管理するテーブル
TODO_COUNTER_TABLE = "CounterTable"  # シーケンシャルなIDを管理するカウンターテーブル
dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")  # DynamoDBクライアントを作成

def dynamo_to_python(dynamo_object):
    """DynamoDBのレスポンスをPythonの辞書型に変換する関数"""
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_object.items()}

def get_next_todo_id():
    """シーケンシャルなTodoIDを取得する関数"""
    response = dynamodb_client.update_item(
        TableName=TODO_COUNTER_TABLE,
        Key={"CounterName": {"S": "LastTodoID"}},  # キーは固定値 "LastTodoID"
        UpdateExpression="SET LastTodoID = LastTodoID + :inc",  # IDをインクリメント
        ExpressionAttributeValues={":inc": {"N": "1"}},  # インクリメント値は1
        ReturnValues="UPDATED_NEW"  # 更新後の値を取得
    )
    return int(response["Attributes"]["LastTodoID"]["N"])  # 数値として返す

def get_item(args):
    """特定のTodoIDを持つアイテムを取得する関数"""
    if not args.get("todo_id"):  # todo_idが指定されていなければ空の辞書を返す
        return {}

    todo_id = int(args.get("todo_id"))  # IDを整数型に変換
    item = dynamodb_client.get_item(
        TableName=TODO_TABLE, Key={"TodoID": {"N": str(todo_id)}}
    ).get("Item")

    return dynamo_to_python(item) if item else {}  # 取得できなかった場合は空の辞書を返す

def scan_items():
    """テーブル内の全アイテムを取得する関数"""
    items = []
    response = dynamodb_client.scan(TableName=TODO_TABLE)  # 全件スキャン
    for dynamo_object in response["Items"]:
        items.append(dynamo_to_python(dynamo_object))  # 取得したデータをPython辞書に変換

    return items

def put_item(form):
    """新しいTODOを登録する関数"""
    todo_id = get_next_todo_id()  # シーケンシャルなIDを取得
    title = form["title"]
    detail = form["detail"]
    status = form["status"]

    # 取得したIDを使ってDynamoDBに新規レコードを追加
    dynamodb_client.put_item(
        TableName=TODO_TABLE,
        Item={
            "TodoID": {"N": str(todo_id)},  # 数値型のTodoIDを設定
            "Title": {"S": title},  # 文字列型のタイトル
            "Detail": {"S": detail},  # 文字列型の詳細
            "TodoStatus": {"S": status},  # 文字列型のステータス
        },
    )

def update_item(form):
    """指定したTodoIDのTODOを更新する関数"""
    todo_id = int(form["todo_id"])  # IDを整数型に変換
    title = form["title"]
    detail = form["detail"]
    status = form["status"]

    # 更新処理
    dynamodb_client.update_item(
        TableName=TODO_TABLE,
        Key={"TodoID": {"N": str(todo_id)}},  # 更新対象のキー
        UpdateExpression="SET Title=:title, Detail=:detail, TodoStatus=:status",  # 更新内容
        ExpressionAttributeValues={
            ":title": {"S": title},
            ":detail": {"S": detail},
            ":status": {"S": status},
        },
    )

def delete_item(todo_id):
    """指定したTodoIDのTODOを削除する関数"""
    dynamodb_client.delete_item(
        TableName=TODO_TABLE, Key={"TodoID": {"N": str(todo_id)}}
    )
