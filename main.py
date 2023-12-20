from web3 import Web3, HTTPProvider
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime

INFURA_URL = "YOUR_API_KEY"
TOKEN_ADDRESS = "0x25127685dc35d4dc96c7feac7370749d004c5040"
START_DATE = "2023-05-25"
END_DATE = "2023-05-28"
INPUT_CSV_PATH = "sender_addresses.csv"
OUTPUT_CSV_PATH_1 = "sold_addresses.csv"
OUTPUT_CSV_PATH_2 = "holding_addresses.csv"
TRANSFER_EVENT_SIGNATURE = (
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
)

web3 = Web3(HTTPProvider(INFURA_URL))


def get_block_number_by_date(date_str):
    target_timestamp = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
    current_block = web3.eth.get_block("latest").number
    while True:
        current_timestamp = web3.eth.get_block(current_block).timestamp
        if current_timestamp < target_timestamp:
            return current_block
        else:
            current_block -= 1


def sold_token_in_period(address, token_address, start_block, end_block):
    # Get the logs of Transfer events in the block
    logs = web3.eth.getLogs(
        {
            "fromBlock": start_block,
            "toBlock": end_block,
            "address": token_address,
            "topics": [TRANSFER_EVENT_SIGNATURE, web3.eth.abi.encode_hex(address)],
        }
    )
    # If any logs exist, the address sold some tokens in this period
    return len(logs) > 0


def write_to_csv(data, output_path):
    with open(output_path, "w") as file:
        file.writelines("\n".join(data))


start_block = get_block_number_by_date(START_DATE)
end_block = get_block_number_by_date(END_DATE)

with open(INPUT_CSV_PATH, "r") as file:
    reader = csv.reader(file)
    sender_addresses = [row[0] for row in reader]

sold_addresses = []
holding_addresses = []

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(
            sold_token_in_period, address, TOKEN_ADDRESS, start_block, end_block
        )
        for address in sender_addresses
    ]
    for address, future in zip(sender_addresses, futures):
        if future.result():
            sold_addresses.append(address)
        else:
            holding_addresses.append(address)

write_to_csv(sold_addresses, OUTPUT_CSV_PATH_1)
write_to_csv(holding_addresses, OUTPUT_CSV_PATH_2)
