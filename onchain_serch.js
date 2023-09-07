// 必要なライブラリをインポートします
const fs = require('fs'); // ファイル操作用
const csv = require('csv-parse'); // CSVパース用
const csvStringify = require('csv-stringify'); // CSV生成用
const { CoinGecko } = require('coingecko-api'); // ETH/USDレート取得用
const { ethers } = require('ethers'); // Ethereum操作用

// Infura APIキーを設定
const infuraApiKey = 'https://mainnet.infura.io/v3/9c09fc0297de455dafb8a31432571042';

// Providerオブジェクトを作成
const provider = new ethers.providers.InfuraProvider('homestead', infuraApiKey);

// CSVファイルからトランザクションハッシュを読み込む
const txHashes = []; // トランザクションハッシュの配列
fs.createReadStream('tx_hashes.csv') // ファイルストリームを作成
  .pipe(csv()) // CSVパーサーにパイプ
  .on('data', (row) => {
    txHashes.push(row[0]); // 各行からトランザクションハッシュを読み込む
  })
  .on('end', async () => {
    // ファイルの読み込みが終わったら、メインの処理を実行
    await main();
  });

// トランザクションハッシュからトランザクションオブジェクトを取得し、実行者のウォレットアドレスを取得
async function getSender(txHash) {
  try {
    const tx = await provider.getTransaction(txHash); // トランザクションオブジェクトを取得
    return tx.from; // 実行者のウォレットアドレスを取得
  } catch (error) {
    console.log(`Transaction with hash: '${txHash}' not found.`);
    return null;
  }
}

// ETHをUSDに変換するための現在のレートを取得
async function getEthToUsdRate() {
  const coingecko = new CoinGecko(); // CoinGecko APIクライアントを作成
  const response = await coingecko.simple.price({
    ids: ['ethereum'],
    vs_currencies: ['usd'],
  }); // ETH/USDレートを取得
  return ethers.utils.parseUnits(response.data.ethereum.usd.toString(), 18); // Wei単位に変換
}

let ethToUsdRate; // ETH/USDレートを保持する変数

async function getEthBalance(address) {
  const balance = await provider.getBalance(address); // Wei単位で残高を取得
  const balanceUsd = balance.mul(ethToUsdRate).div(ethers.constants.WeiPerEther); // USDに変換
  return [address, balanceUsd]; // アドレスと残高（USD）のペアを返す
}

// メインの処理
async function main() {
  ethToUsdRate = await getEthToUsdRate(); // ETH/USDレートを取得

  // すべてのトランザクションハッシュに対して非同期にgetSenderを実行し、Promiseの配列を作成
  const senderPromises = txHashes.map((txHash) => getSender(txHash));

  // Promiseの配列を解決し、実行者のウォレットアドレスの配列を作成
  const senderAddresses = (await Promise.all(senderPromises)).filter(
    (addr) => addr !== null
  );

  // 重複を削除したアドレスリストを作成
  const uniqueAddresses = [...new Set(senderAddresses)];

  // 各アドレスのETH残高（USD）を非同期に取得し、Promiseの配列を作成
  const balancePromises = uniqueAddresses.map((address) => getEthBalance(address));

  // Promiseの配列を解決し、アドレスと残高（USD）のペアの配列を作成
  const addressBalances = await Promise.all(balancePromises);

  // 残高（USD）でソートされたアドレスと残高（USD）のペアの配列を作成
  const sortedAddressBalances = addressBalances.sort((a, b) => b[1].sub(a[1]));

  // senderアドレスと残高（USD）をCSVファイルに書き込む
  csvStringify(sortedAddressBalances, { header: true, columns: ['Address', 'Balance(USD)'] }) // CSV文字列に変換
    .pipe(fs.createWriteStream('SHIB_sender_addresses_sorted.csv')); // ファイルストリームにパイプ

}
