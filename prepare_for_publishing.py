import argparse
import os
import shutil

from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

BRAND_TEMPLATE = 'templates/brand.PNG'
ITEM_CODE_TEMPLATE = 'templates/code.PNG'
ITEM_SIZE_PRICE_TEMPLATE = 'templates/size_price.PNG'
BNEW_TAG_TEMPLATE = 'templates/brand_new_tag.PNG'
DONE_DIR = 'done'
IMG_EXTS = ['JPG', 'JPEG']
ITEM_CODE_COORDS = (0, 0)
# RGB Colors
GRAY = 'rgb(105,105,105)'

# Fonts
MARKER_FELT = 'MarkerFelt.ttc'
AMERICAN_TYPEWRITER = 'AmericanTypewriter.ttc'
ARIAL = 'Arial.ttf'
MIN_BID_ADDON = 20


def prepare_for_renaming(dir_path):
    print('Renaming items..')
    for index, item in tqdm(enumerate(os.listdir(dir_path), start=1)):
        ext = item.split('.')[-1]
        full_item_path = os.path.join(
            dir_path,
            item,
        )
        if os.path.isdir(full_item_path) or 'Store' in item:
            continue

        new_path = os.path.join(
            dir_path,
            f'{index}_.{ext}'
        )
        os.rename(
            full_item_path,
            new_path,
        )


def prepare_dir_for_publishing(dir_path):
    done_dir = os.path.join(
        dir_path,
        DONE_DIR,
    )
    batch_code = dir_path.split('/')[-1]

    if not os.path.exists(done_dir):
        os.mkdir(done_dir)

    for index, item in tqdm(enumerate(os.listdir(dir_path), start=1)):
        try:  # TODO: USE logging
            process_image(
                dir_path,
                item,
                batch_code,
                index,
                done_dir,
            )
        except Exception as e:
            print(f'Error happened for: {item} {e}')
            break


def make_final_image(original_full_path, img_dict):
    """
    """
    item = Image.open(original_full_path)
    item_copy = item.copy()

    for img_data in img_dict:
        item_copy.paste(
            img_data['img'],
            img_data['coordinates'],
            img_data['img'].convert('RGBA'),
        )

    return item


def make_size_and_price_code_image(
    size_text: str,
    price: int,
    bid_price: int,
    item_height: int,
    item_width: int,
    item_code: str,
) -> Image.Image:
    font_color = GRAY
    size_price_template = Image.open(ITEM_SIZE_PRICE_TEMPLATE)
    draw_size_price = ImageDraw.Draw(size_price_template)
    size_price_font = ImageFont.truetype(MARKER_FELT, size=300)
    size_price_x = 325
    size_price_y = 325

    # Add size
    draw_size_price.text(
        (size_price_x, size_price_y),
        size_text,
        fill=font_color,
        font=size_price_font,
    )
    price_font = ImageFont.truetype(AMERICAN_TYPEWRITER, size=275)

    size_price_y += 25

    # Add Mine price
    size_price_y += 300
    min_price_text = f"mine: {price}"
    draw_size_price.text(
        (size_price_x, size_price_y),
        min_price_text,
        fill=font_color,
        font=price_font,
    )

    # Add Open for Bidding text
    size_price_y += 300
    bid_font = ImageFont.truetype(AMERICAN_TYPEWRITER, size=150)
    size_price_x += 25
    bid_text_1 = 'Open for bidding'
    draw_size_price.text(
        (size_price_x, size_price_y),
        bid_text_1,
        fill=font_color,
        font=bid_font,
    )
    # Add bid price
    bid_text_2 = f'Starts at {bid_price}'
    size_price_x += 50
    bid_font = ImageFont.truetype(AMERICAN_TYPEWRITER, size=175)
    size_price_y += 150
    draw_size_price.text(
        (size_price_x, size_price_y),
        bid_text_2,
        fill=font_color,
        font=bid_font,
    )

    # Add code
    size_price_x += 185
    size_price_y += 225
    bid_font = ImageFont.truetype(AMERICAN_TYPEWRITER, size=300)
    draw_size_price.text(
        (size_price_x, size_price_y),
        item_code,
        fill=font_color,
        font=bid_font,
    )

    size_price_dimensions = (
        round(item_height * .25),
        round(item_width * .25),
    )
    size_price_img = size_price_template.resize(size_price_dimensions)

    return size_price_img


def make_item_code_image(item_code: str, item_height: int, item_width: int):
    """
    :returns: img
    """
    font_color = GRAY
    code_template = Image.open(ITEM_CODE_TEMPLATE)
    draw_code = ImageDraw.Draw(code_template)
    code_position = 45, 260
    code_font = ImageFont.truetype(ARIAL, size=350)
    draw_code.text(
        code_position,
        item_code,
        fill=font_color,
        font=code_font,
    )

    code_height = round(item_height * .05)
    code_width = round(item_width * .12)
    code_img = code_template.resize((code_width, code_height))
    return code_img


def make_brand_image(brand: str, item_height: int, item_width: int) -> Image.Image:
    if not brand:
        return

    font_color = GRAY
    brand_template = Image.open(BRAND_TEMPLATE)
    draw_brand = ImageDraw.Draw(brand_template)
    brand_position = 70, 500
    brand_font = ImageFont.truetype(ARIAL, size=300)
    draw_brand.text(
        brand_position,
        brand,
        fill=font_color,
        font=brand_font,
    )
    brand_height = round(item_height * .05)
    brand_width = round(item_width * .2)
    brand_img = brand_template.resize((brand_width, brand_height))

    return brand_img


def make_brand_new_tag_image(item_height: int, item_width: int) -> Image.Image:
    """
    """
    tag_template = Image.open(BNEW_TAG_TEMPLATE)
    tag_height = round(item_height * .15)
    tag_width = round(item_width * .20)

    tag_img = tag_template.resize((tag_width, tag_height))

    return tag_img


def generate_item_code(batch, number):
    return f'{batch}{number:03}'


def process_image(dir_path, filename, batch, number, done_dir):
    """
    TODO: guide
    """

    try:
        filename_no_ext, ext = filename.split('.')
    except Exception:
        return

    if ext not in IMG_EXTS:
        return

    original_item_full_path = os.path.join(
        dir_path,
        filename,
    )
    item = Image.open(original_item_full_path)
    item_code = generate_item_code(batch, number)
    item_data = extract_data_from_filename(filename_no_ext)

    size_price_img = make_size_and_price_code_image(
        size_text=item_data["size"],
        price=item_data["price"],
        bid_price=item_data["bid_price"],
        item_height=item.height,
        item_width=item.width,
        item_code=item_code,
    )
    item_copy = item.copy()

    # Add size & price to item
    SIZE_PRICE_COORDS = (
        round(item.width * .35),
        round(item.height * .01),
    )
    item_copy.paste(
        size_price_img,
        SIZE_PRICE_COORDS,
        size_price_img.convert('RGBA'),
    )

    if item_data.get("brand"):
        brand_img = make_brand_image(
            brand=item_data.get("brand"),
            item_height=item.height,
            item_width=item.width,
        )
        brand_x = 0
        brand_y = item.height - brand_img.height
        item_copy.paste(
            brand_img,
            (brand_x, brand_y),
            brand_img.convert('RGBA')
        )

    if item_data["is_new"]:
        bnew_tag_img = make_brand_new_tag_image(
            item.height,
            item.width,
        )
        bnew_tag_x = item.width - bnew_tag_img.width
        bnew_tag_y = item.height - bnew_tag_img.height
        item_copy.paste(
            bnew_tag_img,
            (bnew_tag_x, bnew_tag_y),
            bnew_tag_img.convert('RGBA'),
        )

    # Use code as filename for edited item
    final_item_code_with_ext = f'{item_code}.{ext}'
    final_item_full_path = os.path.join(
        dir_path,
        final_item_code_with_ext
    )
    item_copy.save(final_item_full_path)

    # Move processed image to DONE_DIR
    full_path = os.path.join(
        dir_path,
        filename,
    )
    shutil.move(
        full_path,
        done_dir,
    )


def extract_data_from_filename(filename: str) -> dict:
    """
    filename: filename with no extension

    Format: <size>_<price>_<brand>_<is_new>

    Examples:
        large_300_atmosphere_y
        (Large size, 300 initial price, atmosphere brand, brand new)

        small_200_n_n
        (small size, 200 initial price, no brand, not brand new)
    """
    size, price, brand, is_new = filename.split('_')

    return {
        "size": size.upper(),
        "price": price,
        "bid_price": int(price) + MIN_BID_ADDON,
        "brand": brand.upper() if brand != "n" else None,
        "is_new": True if is_new == "y" else False
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_path', help='dir containing the images.')
    arguments = parser.parse_args()

    prepare_dir_for_publishing(arguments.dir_path)
