# 必要なライブラリをインポートします
from web3 import Web3
import csv
from concurrent.futures import ThreadPoolExecutor
from web3 import exceptions  # web3.exceptionsサブモジュールをインポート
import datetime
from ens import ENS

# Infura APIキーを設定（自分のものに置き換える）
provider = "https://mainnet.infura.io/v3/9c09fc0297de455dafb8a31432571042"
# infura_url = "https://mainnet.infura.io/v3/9c09fc0297de455dafb8a31432571042"
# Alchemy = "https://eth-mainnet.g.alchemy.com/v2/XwXZbko-cznfVHS7LJ8RY4ni7ZNq84Lv"
# quicknode_url = "https://hardworking-convincing-morning.discover.quiknode.pro/b54523cc1be0295dd1869b2779084f041fbf9755/"

# Web3オブジェクトを作成
web3 = Web3(Web3.HTTPProvider(provider))

# ENSオブジェクトを作成
ens = ENS.from_web3(web3)

# トークンの名前を変数として定義する

token_name = "NAVYSEAL"

# CSVファイルの名前をformat関数で変数を使って指定する
csv_name = "./csv/{}_buy_addresses.csv".format(token_name)
csv_name2 = "./csv/{}_smart_addresses.csv".format(token_name)

# CSVファイルからトランザクションハッシュを読み込む
with open("./input/buy_hash.csv", "r") as file:
    reader = csv.reader(file)
    tx_hashes = [row[0] for row in reader]  # 各行からトランザクションハッシュを読み込む

# トランザクションハッシュからトランザクションオブジェクトを取得し、実行者のウォレットアドレスを取得
def get_buy(tx_hash):
    try:
        tx = web3.eth.get_transaction(tx_hash)  # トランザクションオブジェクトを取得
        return tx["from"]  # 実行者のウォレットアドレスを取得
    except exceptions.TransactionNotFound:  # トランザクションが見つからなかった場合
        return None  # Noneを返す

# ThreadPoolExecutorを作成し、すべてのトランザクションハッシュに対して非同期にget_buyを実行
with ThreadPoolExecutor() as executor:
    buy_addresses = list(executor.map(get_buy, tx_hashes))

# Noneの要素を除去する
buy_addresses = [address for address in buy_addresses if address is not None]

# buyアドレスをCSVファイルに書き込む
with open(csv_name, "w") as file:
    file.writelines("\n".join(buy_addresses))

# sell_hash.csvからトランザクションハッシュを読み込む
with open("./input/sell_hash.csv", "r") as file:
    reader = csv.reader(file)
    sell_hashes = [row[0] for row in reader]  # 各行からトランザクションハッシュを読み込む

# sell_hash.csvのトランザクションハッシュから実行者のウォレットアドレスを取得する
with ThreadPoolExecutor() as executor:
    sell_addresses = list(executor.map(get_buy, sell_hashes))

# tx_hashes.csvとsell_hash.csvのウォレットアドレスのリストを比較して、共通の要素を見つける
common_addresses = list(set(buy_addresses).intersection(set(sell_addresses)))

# 0xae2Fc483527B8EF99EB5D9B44875F005ba1FaE13 このアドレスを除外する
common_addresses.remove("0xae2Fc483527B8EF99EB5D9B44875F005ba1FaE13")

# 共通のウォレットアドレスとそのETH残高のタプルのリストを作成する
common_balances = []
for address in common_addresses:
    balance = web3.eth.get_balance(address)  # ウォレットアドレスのETH残高を取得する
    balance = web3.from_wei(balance, 'ether')  # WEIからETHに変換する
    common_balances.append((address, balance))  # タプルとしてリストに追加する

# ETH残高が多い順にタプルのリストを並び替える（降順）
common_balances.sort(key=lambda x: -x[1])



# 共通のウォレットアドレスをETH残高が多い順に新しいCSVファイルに書き込む
with open(csv_name2, "w") as file:  # ファイルパスを変更する
    writer = csv.writer(file)
    writer.writerow(["address", "balance"])  # ヘッダー行を書き込む
    writer.writerows(common_balances)  # タプルのリストを書き込む