from brownie import config, interface, network
from web3 import Web3
from scripts.helpful_scripts import (
    get_account,
    get_account_data,
    get_asset_price,
    approve_erc20,
    get_lending_pool,
    get_borrowable_data,
    get_weth,
)

amount = Web3.toWei(0.1, "ether")


def deposit_weth(_lending_pool, _erc20_address, _amount, _account):
    print("Depositing...")
    tx = _lending_pool.deposit(
        _erc20_address, _amount, _account.address, 0, {"from": _account}
    )
    tx.wait(1)
    print("Deposited!")


def borrow_erc20(lending_pool, amount, account):
    erc20_address = config["networks"][network.show_active()]["dai_token"]
    # 1 is stable interest rate
    # 0 is the referral code
    dai_amount = Web3.toWei(amount, "ether")
    lending_pool.borrow(
        erc20_address,
        dai_amount,
        1,
        0,
        account.address,
        {"from": account},
    )
    print(f"Congratulations! We have just borrowed {amount} in DAI.")


def repay_all(amount, lending_pool, account):
    total_debt = get_account_data(lending_pool, account)[1]
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        Web3.toWei(total_debt, "ether"),
        1,
        account.address,
        {"from": account},
    )
    tx.wait(1)
    print("Repaid!")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    # deposit_weth(lending_pool, erc20_address, amount, account)

    # Checking for borrowable ETH, total debt, and total collateral in ETH.

    borrowable_eth, total_debt_eth = get_borrowable_data(lending_pool, account)
    erc20_eth_price = get_asset_price()
    amount_erc20_to_borrow = (1 / erc20_eth_price) * (borrowable_eth * 0.90)
    print(f"We are going to borrow {amount_erc20_to_borrow} DAI")
    borrow_erc20(lending_pool, amount_erc20_to_borrow, account)
    amount_erc20_to_repay = (1 / erc20_eth_price) * (total_debt_eth * 0.95)
    repay_all(amount_erc20_to_borrow, lending_pool, account)
    # Then print out our borrowable data
    get_borrowable_data(lending_pool, account)
