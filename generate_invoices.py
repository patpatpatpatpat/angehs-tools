import argparse

import gspread
from tqdm import tqdm

from settings import (BDO_ACCOUNT_NUMBER, GCASH_NUMBER, PALAWAN_RECIPIENT,
                      PSBANK_ACCOUNT_NUMBER, SERVICE_ACCOUNT_FILENAME)

BUYER_DATA_RANGE = 'A2:C61'

# TODO: include in cli args?
COLLECTION_NAME = "Angeh's Live Selling @ 3-30-21"
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


def get_buyer_data_list(gsheet_filename):
    print(f"Fetching data from Google Sheets file: {gsheet_filename}")
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILENAME)
    sheet = gc.open(gsheet_filename).sheet1
    buyer_data_list = sheet.get(BUYER_DATA_RANGE)

    return filter(None, buyer_data_list)


def restructure_buyer_data_list(data):
    print("Restructuring buyer data...")
    buyers_to_items_bought = {}

    for buyer_data in tqdm(data):
        buyer, code, price, *_ = buyer_data

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


def generate_invoices_file(buyer_to_items_data):
    all_invoices = ""

    print("Generating invoice per buyer...")
    # TODO: include total number of items
    for buyer_name in tqdm(buyer_to_items_data.keys()):
        invoice = TEMPLATE.format(
            palawan_recipient=PALAWAN_RECIPIENT,
            collection=COLLECTION_NAME,
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

    filename = f"{COLLECTION_NAME} invoices.txt"

    with open(filename, "w") as txt_file:
        txt_file.write(all_invoices)

    print(f"Invoices file generated: {filename}")


def generate_invoices(gsheet_filename):
    buyer_data_list = get_buyer_data_list(gsheet_filename)
    buyers_to_items_bought = restructure_buyer_data_list(buyer_data_list)
    generate_invoices_file(buyers_to_items_bought)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('gsheet_filename', help='Google Sheets filename')
    arguments = parser.parse_args()

    generate_invoices(arguments.gsheet_filename)
