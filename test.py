# requestsとjsonとpandasをインポートする
import requests
import json
import pandas as pd

# APIキーとウォレットアドレスとコントラクトアドレス（Uniswap V2）を設定する
api_key = "ZI456ZQ8K6K7RUCRPJAB8MJDI1UAHXHVCF"
wallet_address = "0x2095df2d67b1d2eb71b5af6bdf09bec261cc5a89"
contract_address = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"

# エンドポイントとパラメータを設定する
endpoint = "https://api.etherscan.io/"
params = {
    "module": "account",
    "action": "tokentx",
    "address": wallet_address,
    "contractaddress": contract_address,
    "apikey": api_key,
}

# HTTPリクエストを送信し、レスポンスを受け取る
response = requests.get(endpoint, params=params)

# レスポンスが正常であれば、JSONデータを取得する
if response.status_code == 200:
    data = response.json()
else:
    print("Error:", response.status_code)

# JSONデータからスワップトランザクションのリストを取得する
swap_list = data["result"]

# スワップトランザクションのリストをpandasのデータフレームに変換する
swap_df = pd.DataFrame(swap_list)

# データフレームの内容を表示する
print(swap_df)
