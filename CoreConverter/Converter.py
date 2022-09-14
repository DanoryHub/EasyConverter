import os
from os import path

import ffmpeg
import pillow_heif
from PIL import Image


class Converter:
    def __init__(self, save_directory: str):
        self.save_directory = save_directory
        self.compress_modes = {'DISCORD': 8.0}

    def convert(self, input_file_path: str, output_file_format: str):
        dir_filename, file_ext = path.splitext(input_file_path)
        file_ext = file_ext.replace('.', '')

        if file_ext.upper() == 'HEIC':
            pillow_heif.register_heif_opener()
        elif file_ext.upper() == 'AVIF':
            pillow_heif.register_avif_opener()

        img_object = Image.open(input_file_path)

        self.compress(image_obj=img_object, input_file_path=input_file_path, compress_mode="DISCORD")

        suffix = '.' + output_file_format.lower()
        output_file_name = path.basename(dir_filename) + suffix
        output_file_path = path.join(self.save_directory, output_file_name)

        img_object.save(output_file_path)

        return output_file_path

    def compress(self, image_obj, input_file_path: str, compress_mode: str):
        bytes_in_megabyte = 1000000
        img_size = path.getsize(input_file_path)
        img_size = img_size / bytes_in_megabyte

        compress_aim_size = self.compress_modes[compress_mode]

        if img_size > compress_aim_size:
            compress_ratio: float = compress_aim_size / img_size
            compress_ratio = round(compress_ratio, 1) - 0.1
            image_obj = image_obj.resize((int(image_obj.size[0] * compress_ratio),
                                          int(image_obj.size[1] * compress_ratio)),
                                         Image.ANTIALIAS)

        return image_obj

    def compress_video(self, video_full_path, size_upper_bound, two_pass=True, filename_suffix='cps_'):
        filename, extension = os.path.splitext(video_full_path)
        extension = '.mp4'
        output_file_name = filename + filename_suffix + extension

        total_bitrate_lower_bound = 11000
        min_audio_bitrate = 32000
        max_audio_bitrate = 256000
        min_video_bitrate = 100000

        try:
            probe = ffmpeg.probe(video_full_path)
            duration = float(probe['format']['duration'])
            audio_bitrate = float(
                next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
            target_total_bitrate = (size_upper_bound * 1024 * 8) / (1.073741824 * duration)
            if target_total_bitrate < total_bitrate_lower_bound:
                print('Bitrate is extremely low! Stop compress!')
                return False

            best_min_size = (min_audio_bitrate + min_video_bitrate) * (1.073741824 * duration) / (8 * 1024)
            if size_upper_bound < best_min_size:
                print('Quality not good! Recommended minimum size:', '{:,}'.format(int(best_min_size)), 'KB.')
                # return False

            audio_bitrate = audio_bitrate

            if 10 * audio_bitrate > target_total_bitrate:
                audio_bitrate = target_total_bitrate / 10
                if audio_bitrate < min_audio_bitrate < target_total_bitrate:
                    audio_bitrate = min_audio_bitrate
                elif audio_bitrate > max_audio_bitrate:
                    audio_bitrate = max_audio_bitrate

            video_bitrate = target_total_bitrate - audio_bitrate
            if video_bitrate < 1000:
                print('Bitrate {} is extremely low! Stop compress.'.format(video_bitrate))
                return False

            i = ffmpeg.input(video_full_path)
            if two_pass:
                ffmpeg.output(i, os.devnull,
                              **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                              ).overwrite_output().run()
                ffmpeg.output(i, output_file_name,
                              **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac',
                                 'b:a': audio_bitrate}
                              ).overwrite_output().run()
            else:
                ffmpeg.output(i, output_file_name,
                              **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
                              ).overwrite_output().run()

            if path.getsize(output_file_name) <= size_upper_bound * 1024:
                return output_file_name
            elif path.getsize(output_file_name) < path.getsize(video_full_path):  # Do it again
                return self.compress_video(output_file_name, size_upper_bound)
            else:
                return False
        except FileNotFoundError as e:
            print('You do not have ffmpeg installed!', e)
            return False


if __name__ == "__main__":
    comp_obj = Converter("C:\\Users\\User\\Desktop\\EasyConverter\\Save")
    comp_obj.convert("C:\\Users\\User\\Desktop\\1212.png", "PNG")
    comp_obj.compress_video("C:\\Users\\User\\Desktop\\video.mp4", 8*1000)
    #comp_obj.convert("C:\\Users\\User\\Desktop\\IMG_2908.HEIC", "PNG")
