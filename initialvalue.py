import boto3

TABLE_NAME = "CounterTable"

dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")

def reset_todo_id():
    """CounterTable の LastTodoID を 0 に初期化する"""
    dynamodb_client.update_item(
        TableName=TABLE_NAME,
        Key={"CounterName": {"S": "LastTodoID"}},
        UpdateExpression="SET LastTodoID = :reset",
        ExpressionAttributeValues={":reset": {"N": "0"}}
    )
    print("LastTodoID を 0 に初期化しました。")

if __name__ == "__main__":
    reset_todo_id()
