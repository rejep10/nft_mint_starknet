from chech_abi import CHECK_ABI
from loguru import logger
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
import asyncio


STARKNET_NODE = "https://starknet-mainnet.infura.io/v3/b8cee26424154a7383499cbf46bcf566"
nft_wallet_counter = 0  # Счетчик кошельков с NFT
async def check_nft(account, address):
    global nft_wallet_counter  # Используем глобальную переменную
    to = int(address, 16)
    contract = Contract(
        address=0x00b719f69b00a008a797dc48585449730aa1c09901fdbac1bc94b3bdc287cf76,
        abi=CHECK_ABI,
        provider=account,
    )
    (has_minted,) = await contract.functions["hasMinted"].call(to)

    if has_minted:  # Проверяем, есть ли NFT на кошельке
        nft_wallet_counter += 1  # Увеличиваем счетчик
        logger.info(f'Найдено всего {nft_wallet_counter} NFT из списка')

        # Записываем адрес в текстовый файл
        with open('addresses_with_nft.txt', 'a') as f:
            f.write(f"{address}\n")
async def main():
    logger.info("Начало выполнения скрипта")
    # Открываем файлы с адресами и приватными ключами
    with open('address.txt', 'r') as address_file, open('private_key.txt', 'r') as private_key_file:
        for address, private_key_hex in zip(address_file, private_key_file):
            address = address.strip()  # Удаляем пробелы и символы переноса строки
            private_key_hex = private_key_hex.strip()  # Удаляем пробелы и символы переноса строки

            def create_starknet_account(private_key_hex):
                if private_key_hex.startswith("0x"):
                    private_key_hex = private_key_hex[2:]  # Убираем первые два символа "0x"
                private_key = int(private_key_hex, 16)  # Преобразуем шестнадцатеричную строку в целое число

                return Account(
                    client=FullNodeClient(STARKNET_NODE),
                    address=address,
                    key_pair=KeyPair.from_private_key(key=private_key),
                    chain=StarknetChainId.MAINNET,
                )

            starknet_account = create_starknet_account(private_key_hex)
            await check_nft(starknet_account, address)
# Запуск асинхронной функции main
asyncio.run(main())