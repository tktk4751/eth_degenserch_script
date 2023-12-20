# eth_degenserch_script

This script helps you to find smart degen plays on Ethereum DEXs by analyzing the trading data of any token.  

## How to use

To use this script, you need to:  
- Get an APIKEY from Infura¹, a platform that provides access to Ethereum and IPFS networks.
- Look at the chart of the token you are interested in and identify the time period when a smart degen play might have occurred.
- Use EtherScan², a blockchain explorer for Ethereum, to download the DEX trades data for the token and the time period you selected.
- Paste all the buy addresses into /input/buy_hash.py and all the sell addresses into /input/sell_hash.py.
- Run main.py and see the results.
