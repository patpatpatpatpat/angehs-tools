import argparse

import gspread
from tqdm import tqdm

from settings import (BDO_ACCOUNT_NUMBER, GCASH_NUMBER, PALAWAN_RECIPIENT,
                      PSBANK_ACCOUNT_NUMBER, SERVICE_ACCOUNT_FILENAME)

TEMPLATE = """
=================
💸PAYMENT OPTIONS💸
🏦Palawan Express Pera Padala - {palawan_recipient}
🏦GCash - {gcash}
🏦BDO - {bdo}
🏦PSBank - {psbank}
=================
🌟INVOICE for {collection}🌟

Buyer: {buyer}
🔑 - 💵
"""


def get_buyer_data_list(gsheet_filename: str, buyer_data_range: str) -> list:
    print(f"Fetching data from Google Sheets file: {gsheet_filename}")
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILENAME)
    sheet = gc.open(gsheet_filename).sheet1
    buyer_data_list = sheet.get(buyer_data_range)

    return filter(None, buyer_data_list)


def restructure_buyer_data_list(data: list) -> dict:
    print("Restructuring buyer data...")
    buyers_to_items_bought = {}

    for buyer_data in tqdm(data):
        buyer, code, price, *_ = buyer_data
        buyer = buyer.strip()

        purchased_item_data = {
            'code': code,
            'price': price,
        }

        if buyer in buyers_to_items_bought:
            buyers_to_items_bought[buyer].append(purchased_item_data)
        else:
            buyers_to_items_bought[buyer] = [
                purchased_item_data,
            ]

    return buyers_to_items_bought


def generate_invoices_file(buyer_to_items_data: dict, batch_name: str) -> None:
    """
    TOOD:
    """
    all_invoices = ""

    print("Generating invoice per buyer...")
    # TODO: include total number of items
    for buyer_name in tqdm(buyer_to_items_data.keys()):
        invoice = TEMPLATE.format(
            palawan_recipient=PALAWAN_RECIPIENT,
            collection=batch_name,
            buyer=buyer_name,
            gcash=GCASH_NUMBER,
            bdo=BDO_ACCOUNT_NUMBER,
            psbank=PSBANK_ACCOUNT_NUMBER,
        )
        total = 0
        num_items = len(buyer_to_items_data[buyer_name])

        for item_bought in buyer_to_items_data[buyer_name]:
            invoice += f"{item_bought['code']} - {item_bought['price']}\n"
            total += int(item_bought["price"])

        invoice += f"----------\nTOTAL - {total} ({num_items} item/s)\n\n\n"
        all_invoices += invoice

    filename = f"{batch_name} invoices.txt"

    with open(filename, "w") as txt_file:
        txt_file.write(all_invoices)

    print(f"Invoices file generated: {filename}")


def generate_invoices(**kwargs) -> None:
    buyer_data_list = get_buyer_data_list(kwargs['gsheet_filename'], kwargs['data_range'])
    buyers_to_items_bought = restructure_buyer_data_list(buyer_data_list)
    generate_invoices_file(buyers_to_items_bought, kwargs['batch_name'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('gsheet_filename', help='Google Sheets filename')
    parser.add_argument('data_range', help='Cell range. Example: A4:C109')
    parser.add_argument('batch_name', help='For output file: Example: 15th Collection')
    arguments = parser.parse_args()

    generate_invoices(**arguments)
