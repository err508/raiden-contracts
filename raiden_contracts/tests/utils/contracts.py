from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider

from raiden_libs.test.fixtures.web3 import (
    FAUCET_ALLOWANCE,
)

from raiden_libs.utils import private_key_to_address

from raiden_contracts.constants import CONTRACT_CUSTOM_TOKEN
from raiden_contracts.tests.fixtures import contracts_manager


def get_web3(eth_tester, deployer_key):
    """Returns an initialized Web3 instance"""
    provider = EthereumTesterProvider(eth_tester)
    web3 = Web3(provider)

    # add faucet account to tester
    eth_tester.add_account(deployer_key.hex())

    # make faucet rich
    eth_tester.send_transaction({
        'from': eth_tester.get_accounts()[0],
        'to': private_key_to_address(deployer_key.hex()),
        'gas': 21000,
        'value': FAUCET_ALLOWANCE,
    })

    return web3


def deploy_contract(web3, contract_name, deployer_key, libs=None, args=None):
    deployer_address = private_key_to_address(deployer_key.hex())

    json_contract = contracts_manager().compile_contract(contract_name, libs)
    contract = web3.eth.contract(
        abi=json_contract['abi'],
        bytecode=json_contract['bin'],
    )
    tx_hash = contract.constructor(*args).transact({
        'from': deployer_address,
        'gas': 3141619,
    })
    contract_address = web3.eth.getTransactionReceipt(tx_hash).contractAddress

    return contract(contract_address)


def deploy_custom_token(web3, deployer_key):
    return deploy_contract(
        web3,
        CONTRACT_CUSTOM_TOKEN,
        deployer_key,
        [],
        (10 ** 26, 18, CONTRACT_CUSTOM_TOKEN, 'TKN'),
    )
