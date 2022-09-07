from os import path

import pillow_heif
from PIL import Image


class Converter:
    def __init__(self, save_directory: str):
        self.save_directory = save_directory

    def convert(self, input_file_path: str, output_file_format: str):
        dir_filename, file_ext = path.splitext(input_file_path)
        file_ext = file_ext.replace('.', '')

        if file_ext.upper() == 'HEIC':
            pillow_heif.register_heif_opener()
        elif file_ext.upper() == 'AVIF':
            pillow_heif.register_avif_opener()

        img_object = Image.open(input_file_path)

        suffix = '.' + output_file_format.lower()
        output_file_name = path.basename(dir_filename) + suffix
        output_file_path = path.join(self.save_directory, output_file_name)

        img_object.save(output_file_path)

        return output_file_path
