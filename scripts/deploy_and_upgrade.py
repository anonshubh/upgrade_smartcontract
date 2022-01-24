from scripts.helpers import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
    config,
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}...")
    box = Box.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=config["networks"][network.show_active()].get("verify", False))

    # initializer = box.store,1
    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"Proxy deployed to {proxy}, now upgradable to v2 possible!")

    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    print(proxy_box.retrieve())

    # Upgrade
    box_v2 = BoxV2.deploy({"from": account}, publish_source=config["networks"][network.show_active()].get("verify", False))
    upgrade_tx = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_tx.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, box_v2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
