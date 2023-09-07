# 必要なライブラリをインポートします
from web3 import Web3
import csv
from concurrent.futures import ThreadPoolExecutor

# Infura APIキーを設定（自分のものに置き換える）
infura_url = "https://mainnet.infura.io/v3/9c09fc0297de455dafb8a31432571042"

# Web3オブジェクトを作成
web3 = Web3(Web3.HTTPProvider(infura_url))

# コントラクトアドレスを設定（自分のものに置き換える）
contract_address = '0xbe0...5bd6'

# アドレスがウォレットかどうかを判定する関数
def is_wallet(address):
    code_size = len(web3.eth.getCode(address))  # アドレスに関連付けられたコードのサイズを取得
    return code_size == 0  # コードのサイズが0ならばウォレットと判断

# トランザクションハッシュからトランザクションオブジェクトを取得し、実行者のウォレットアドレスを取得
def get_sender(tx_hash, check_wallet=True):
    tx = web3.eth.get_transaction(tx_hash)  # トランザクションオブジェクトを取得
    if check_wallet:  # sender_addresses用のチェック
        if is_wallet(tx["from"]):  # fromAddressがウォレットであれば
            return tx["from"]  # 実行者のウォレットアドレスを取得
        else:  # fromAddressがコントラクトであれば
            return None  # Noneを返す
    else:  # sell_addresses用のチェック
        if not is_wallet(tx["from"]) and is_wallet(tx["to"]):  # fromAddressがコントラクトであり、toAddressがウォレットであれば
            return tx["from"]  # 実行者のウォレットアドレスを取得
        else:  # fromAddressかtoAddressが条件に合わなければ
            return None  # Noneを返す

# 指定した期間のブロックタイムとトランザクションハッシュを取得する関数
def get_block_and_tx(start_time, end_time):
    # ブロックタイムを取得
    start_block = web3.eth.get_block(start_time)
    end_block = web3.eth.get_block(end_time)

    # フィルターを作成
    filter = web3.eth.filter({
        'address': contract_address,
        'fromBlock': start_block['number'],
        'toBlock': end_block['number']
    })

    # フィルターからトランザクションハッシュのリストを取得
    tx_hashes = filter.get_all_entries()

    return tx_hashes

# sender_addressesを調べるための期間を入力（人間が読める記述で）
sender_start_time = input('sender_addressesを調べるための期間の開始日時を入力してください（例：2023-09-01T19:00:00Z）：')
sender_end_time = input('sender_addressesを調べるための期間の終了日時を入力してください（例：2023-09-01T20:00:00Z）：')

# sender_addresses用のトランザクションハッシュを取得
sender_tx_hashes = get_block_and_tx(sender_start_time, sender_end_time)

# ThreadPoolExecutorを作成し、すべてのトランザクションハッシュに対して非同期にget_senderを実行（sender_addresses用）
with ThreadPoolExecutor() as executor:
    sender_addresses = list(executor.map(get_sender, sender_tx_hashes, [True] * len(sender_tx_hashes)))

# senderアドレスをCSVファイルに書き込む（Noneは除外する）
with open("NEWPEPE_sender_addresses.csv", "w") as file:
    file.writelines("\n".join([address for address in sender_addresses if address is not None]))

# sell_addressesを調べるための期間を入力（人間が読める記述で）
sell_start_time = input('sell_addressesを調べるための期間の開始日時を入力してください（例：2023-09-01T19:00:00Z）：')
sell_end_time = input('sell_addressesを調べるための期間の終了日時を入力してください（例：2023-09-01T20:00:00Z）：')

# sell_addresses用のトランザクションハッシュを取得
sell_tx_hashes = get_block_and_tx(sell_start_time, sell_end_time)

# ThreadPoolExecutorを作成し、すべてのトランザクションハッシュに対して非同期にget_senderを実行（sell_addresses用）
with ThreadPoolExecutor() as executor:
    sell_addresses = list(executor.map(get_sender, sell_tx_hashes, [False] * len(sell_tx_hashes)))

# sellアドレスをCSVファイルに書き込む（Noneは除外する）
with open("NEWPEPE_sell_addresses.csv", "w") as file:
    file.writelines("\n".join([address for address in sell_addresses if address is not None]))

# tx_hashes.csvとsell_hash.csvのウォレットアドレスのリストを比較して、共通の要素を見つける
common_addresses = list(set(sender_addresses).intersection(set(sell_addresses)))

# 共通のウォレットアドレスを新しいCSVファイルに書き込む
with open("common_addresses.csv", "w") as file:
    file.writelines("\n".join(common_addresses))
