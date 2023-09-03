from mint_abi import MINT_ABI
from loguru import logger
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
import asyncio
import random

STARKNET_NODE = "https://starknet-mainnet.public.blastapi.io"

async def mint_nft(account, address):
    max_retries = 5  # Максимальное количество попыток
    retries = 0  # Счетчик текущих попыток

    while retries < max_retries:
        try:
            logger.info("Начало минта ")
            to = int(address, 16)
            contract = Contract(
                address=0x00b719f69b00a008a797dc48585449730aa1c09901fdbac1bc94b3bdc287cf76,
                abi=MINT_ABI,
                provider=account,
            )

            invocation = await contract.functions["mintPublic"].invoke(
                to, auto_estimate=True)

            await invocation.wait_for_acceptance()
            logger.success("Минт прошел успешно")
            break  # Выход из цикла, если минтинг успешен

        except Exception as e:
            logger.error(f"Ошибка при минтинге: {e}")
            retries += 1  # Увеличиваем счетчик попыток
            logger.info(f"Повторная попытка {retries}/{max_retries}")

            # Задержка перед следующей попыткой, если нужно
            delay = random.randint(1, 5)
            await asyncio.sleep(delay)

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
            try:
                await mint_nft(starknet_account, address)
            except Exception as e:
                logger.error(f"Ошибка при минтинге: {e}")
            delay = random.randint(1, 5)  # Выбирает случайное число между 5 и 10
            await asyncio.sleep(delay)  # Задержка на выбранное количество секунд
            logger.info(f'Подождал {delay} сек.')
# Запуск асинхронной функции main
asyncio.run(main())