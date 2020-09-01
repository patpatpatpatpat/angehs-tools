import argparse
import os
import shutil

from tqdm import tqdm

from PIL import Image, ImageDraw, ImageFont
ITEM_CODE_TEMPLATE = 'templates/code.PNG'
ITEM_SIZE_PRICE_TEMPLATE = 'templates/size_price.PNG'
DONE_DIR = 'done'
IMG_EXTS =['JPG', 'JPEG']


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
        # TODO: skip if directory
        # TODO: skip if DS_Store
        try:
            process_image(
                dir_path,
                item,
                batch_code,
                index,
                done_dir,
            )
        except Exception:
            print(f'Error happened for: {item}')


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

    # TODO: save final item full path
    


    return item

def make_size_and_price_image(filename):
    """
    :param filename: filename with no ext

    Expected filename

    1_M-S_200_300_400

    1 - Unique identifier
    M-S - Size
    200 - mine price
    300 - steal price
    400 - grab price
    """
    unique_identifier, size_text, *prices = filename.split('_')

    font_color = 'rgb(105,105,105)'  # Gray
    size_price_template = Image.open(ITEM_SIZE_PRICE_TEMPLATE)
    draw_size_price = ImageDraw.Draw(size_price_template)
    size_price_font = ImageFont.truetype('Arial.ttf', size=350)
    size_price_x = 300
    size_price_y = 300

    draw_size_price.text(
        (size_price_x, size_price_y),
        size_text,
        fill=font_color,
        font=size_price_font,
    )

    price_index_to_label = {
        0: 'Mine:':,
        1: 'Steal:',
        2: 'Grab:',
    }

    for i, price in enumerate(prices):
        size_price_y += 400
        price_text = f'{price_index_to_label[i]} {price}'
        draw_size_price.text(
            (size_price_x, size_price_y),
            price_text,
            fill=font_color,
            font=size_price_font,
        )

    size_price_img = size_price_template.resize((750, 700))

    return size_price_img


def make_item_code_image(item_code):
    """
    :param item_code: str

    :returns: img
    """
    font_color = 'rgb(105,105,105)'  # Gray
    item_code = f'{batch}{number:03}'
    final_item_code_with_text = f'{item_code}.{ext}'

    code_template = Image.open(ITEM_CODE_TEMPLATE)
    draw_code = ImageDraw.Draw(code_template)
    code_position = 385, 260
    code_font = ImageFont.truetype('Arial.ttf', size=400)
    draw_code.text(
        code_position,
        item_code,
        fill=font_color,
        font=code_font,
    )
    code_img = code_template.resize((600, 250))

    return code_img


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
    images = []

    item_code = generate_item_code(batch, number)
    code_img = make_item_code_image(item_code)
    images.append({
        'coordinates': (0, 20),
        'img': code_img,
    })


    size_price_img = make_size_and_price_image(filename_no_ext)
    images.append({
        'coordinates': (1450, 300),
        'img': size_price_img,
    })


    final_img = make_final_image(
        original_item_full_path,
        images,
    )



    final_item_code_with_ext = f'{item_code}.{ext}'

    item = Image.open(original_item_full_path)

    item_copy = item.copy()
    # Add code to item
    item_copy.paste(code_img, (0, 20), code_img.convert('RGBA'))
    # Add size & price to item
    item_copy.paste(size_price_img, (1450, 300), size_price_img.convert('RGBA'))

    # Use code as filename for edited item
    final_item_full_path = os.path.join(
        dir_path,
        final_item_code_with_ext
    )
    item_copy.save(final_item_full_path)

    # Move processed image to DONE_DIR
    # TODO: create function
    full_path = os.path.join(
        dir_path,
        filename,
    )
    shutil.move(
        full_path,
        done_dir,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_path', help='dir containing the images.')
    arguments = parser.parse_args()

    prepare_dir_for_publishing(arguments.dir_path)

