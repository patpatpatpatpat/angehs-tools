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

    # Extract size & prices
    unique_identifier, size_text, *prices = filename_no_ext.split('_')

    black_color = 'rgb(105,105,105)'
    original_item_full_path = os.path.join(
        dir_path,
        filename,
    )
    item_code = f'{batch}{number:03}'
    final_item_code_with_ext = f'{item_code}.{ext}'

    # Prepare code template
    code_template  = Image.open(ITEM_CODE_TEMPLATE)
    draw_code = ImageDraw.Draw(code_template)
    code_position = 385, 260
    code_font = ImageFont.truetype('Arial.ttf', size=400)
    draw_code.text(
        code_position,
        item_code,
        fill=black_color,
        font=code_font,
    )
    temp_code_path = os.path.join(
        dir_path,
        f'code_{item_code}.png',
    )
    # code_template = code_template.resize((600, 250))
    # code_template.save(temp_code_path, 'PNG', optimize=True)
    code_img = code_template.resize((600, 250))


    # Prepare price template
    size_price_template = Image.open(ITEM_SIZE_PRICE_TEMPLATE)
    draw_size_price = ImageDraw.Draw(size_price_template)

    size_price_font = ImageFont.truetype('Arial.ttf', size=350)

    size_price_x = 300
    size_price_y = 300

    draw_size_price.text(
        (size_price_x, size_price_y),
        size_text, fill=black_color, font=size_price_font)

    price_index_to_label = {
        0: 'Mine:',
        1: 'Steal:',
        2: 'Grab:',
    }

    for i, price in enumerate(prices):
        size_price_y += 400
        price_text = f'{price_index_to_label[i]} {price}'
        draw_size_price.text(
            (size_price_x, size_price_y),
            price_text,
            fill=black_color,
            font=size_price_font,
        )

    temp_size_price_path = os.path.join(
        dir_path,
        f'size_price_{item_code}.png',
    )

    # size_price_template = size_price_template.resize((750, 700))
    # size_price_template.save(temp_size_price_path, 'PNG', optimize=True)
    size_price_img  = size_price_template.resize((750, 700))


    item = Image.open(original_item_full_path)
    # code_img = Image.open(temp_code_path)
    # size_price_img = Image.open(temp_size_price_path)

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

    # os.remove(temp_code_path)
    # os.remove(temp_size_price_path)
    # Move processed image to DONE_DIR
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

