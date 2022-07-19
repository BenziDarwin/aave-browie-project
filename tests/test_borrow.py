from brownie import accounts, config, network, interface
from scripts.helpful_scripts import (
    approve_erc20,
    get_account,
    get_borrowable_data,
    get_lending_pool,
    get_weth,
)
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def test_get_weth():
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    txn = weth.deposit({"from": account, "value": amount})
    txn.wait(1)
    balance = weth.balanceOf(account, {"from": account})
    assert balance == amount


def test_approve():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    erc20 = interface.IERC20(erc20_address)
    lending_pool = get_lending_pool()
    tx = erc20.approve(lending_pool.address, amount, {"from", account})
    tx.wait(1)
    assert tx != False


def test_deposit():
    account = get_account()
    # Depositing
    lending_pool = get_lending_pool()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    get_weth()
    print("Depositing into aave..")
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    tx = lending_pool.deposit(erc20_address, amount, account, 0, {"from": account})
    tx.wait(1)
    total_collateral_eth = get_borrowable_data(lending_pool, account)[0]
    assert total_collateral_eth != 0
