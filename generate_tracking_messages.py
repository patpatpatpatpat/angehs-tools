import argparse

import gspread
from tqdm import tqdm

SERVICE_ACCOUNT_FILENAME = 'service_account.json'
BRANCH_PICK_UP_TEMPLATE = """
BUYER: {buyer}
BRANCH PICK UP - {branch_name}
PAY UPON PICK UP: PHP {delivery_fee}.00

Your item will be picked up by LBC tomorrow.
Tracking Number:
{tracking_number}

Delivery lead-time & tracking page: https://www.lbcexpress.com/track/

IMPORTANT: Please track your package at least ONCE A DAY!
If parcel is ready for PICK UP, do it ASAP to avoid item being returned to me.

Xoxo,
Angeh
"""

HOME_DELIVERY_TEMPLATE = """
BUYER: {buyer}
HOME DELIVERY - {home_delivery_address}
PAY UPON DELIVERY: PHP {delivery_fee}.00

Your item will be picked up by LBC tomorrow.
Tracking Number:
{tracking_number}

Delivery lead-time & tracking page: https://www.lbcexpress.com/track/

IMPORTANT: Please track your package at least ONCE A DAY and keep your lines open!

Xoxo,
Angeh
"""


def get_tracking_data(gsheet_filename, data_range):
    print(f"Fetching data from Google Sheets file: {gsheet_filename}")
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILENAME)
    sheet = gc.open(gsheet_filename).sheet1

    return sheet.get(data_range)


def restructure_tracking_data(data):
    print("Restructuring tracking data...")
    tracking_data_per_buyer = []
    for tracking in data:
        buyer, delivery_type, street, branch, tracking_number = tracking

        tracking_data_per_buyer.append({
            'buyer': buyer,
            'delivery_type': delivery_type,
            'home_delivery_address': street,
            'branch_name': branch,
            'tracking_number': tracking_number,
        })

    return tracking_data_per_buyer


def generate_tracking_file(tracking_data_per_buyer, batch_name):
    all_tracking_messages = ""
    print("Generating tracking message per buyer...")
    for data in tqdm(tracking_data_per_buyer):
        if data['delivery_type'] == 'BRANCH PICK UP':
            template = BRANCH_PICK_UP_TEMPLATE
        else:
            template = HOME_DELIVERY_TEMPLATE

        message = template.format(
            **data
        )
        message += "\n\n\n"
        all_tracking_messages += message

    filename = f"{batch_name} tracking messages.txt"

    with open(filename, "w") as txt_file:
        txt_file.write(all_tracking_messages)

    print(f"Tracking messages file generated: {filename}")


def generate_tracking_messages(**kwargs):
    tracking_data = get_tracking_data(
        kwargs['gsheet_filename'],
        kwargs['data_range'],
    )
    tracking_data_per_buyer = restructure_tracking_data(tracking_data)
    generate_tracking_file(
        tracking_data_per_buyer,
        kwargs['batch_name'],
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('gsheet_filename', help='Google Sheets filename')
    parser.add_argument('data_range', help='Cell range. Example: A1:E7s')
    parser.add_argument('batch_name', help='For output file. Example: #46')
    arguments = dict(parser.parse_args()._get_kwargs())

    generate_tracking_messages(**arguments)
