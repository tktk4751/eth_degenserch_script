# 必要なライブラリをインポートします
from web3 import Web3
import csv
from concurrent.futures import ThreadPoolExecutor
import requests
from operator import itemgetter
from concurrent.futures import as_completed
from decimal import Decimal
from web3.exceptions import TransactionNotFound

# Infura APIキーを設定
infura_url = "YOUR_AIP_KEY"

# Web3オブジェクトを作成
web3 = Web3(Web3.HTTPProvider(infura_url))

# CSVファイルからトランザクションハッシュを読み込む
with open("./input/tx_hashes.csv", "r") as file:
    reader = csv.reader(file)
    tx_hashes = [row[0] for row in reader]  # 各行からトランザクションハッシュを読み込む


# トランザクションハッシュからトランザクションオブジェクトを取得し、実行者のウォレットアドレスを取得
def get_sender(tx_hash):
    try:
        tx = web3.eth.get_transaction(tx_hash)  # トランザクションオブジェクトを取得
        return tx["from"]  # 実行者のウォレットアドレスを取得
    except TransactionNotFound:
        print(f"Transaction with hash: '{tx_hash}' not found.")
        return None


# ETHをUSDに変換するための現在のレートを取得
def get_eth_to_usd_rate():
    response = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    )
    return Decimal(response.json()["ethereum"]["usd"])


eth_to_usd_rate = get_eth_to_usd_rate()


def get_eth_balance(address):
    balance = web3.eth.get_balance(address)  # Wei単位で残高を取得
    balance_eth = Decimal(Web3.from_wei(balance, "ether"))  # ETHに変換
    balance_usd = balance_eth * eth_to_usd_rate  # USDに変換
    return address, balance_usd


# ThreadPoolExecutorを作成し、すべてのトランザクションハッシュに対して非同期にget_senderを実行
with ThreadPoolExecutor() as executor:
    sender_addresses = [
        addr for addr in executor.map(get_sender, tx_hashes) if addr is not None
    ]

# 重複を削除したアドレスリストを作成
unique_addresses = list(set(sender_addresses))

# 各アドレスのETH残高を非同期に取得
address_balances = {}
with ThreadPoolExecutor() as executor:
    future_to_address = {
        executor.submit(get_eth_balance, address): address
        for address in unique_addresses
    }
    for future in as_completed(future_to_address):
        address, balance_usd = future.result()
        address_balances[address] = balance_usd

# 残高（USD）でソートされたアドレスを取得
sorted_addresses = sorted(address_balances.items(), key=itemgetter(1), reverse=True)


# senderアドレスをCSVファイルに書き込む
with open("ETH_sender_addresses_sorted.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(["Address", "Balance(USD)"])  # ヘッダー行を書き込む
    for address, balance in sorted_addresses:
        writer.writerow([f'"{address}"', f"{int(balance)} USD"])  # 小数部分を除き、USDを追加
