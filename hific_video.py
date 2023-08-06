# High-Fidelity Generative Video Compression with HiFiC
import os
import zipfile
import collections
from PIL import Image
from tfc.models import tfci
import cv2
import time
import pickle
import frames2video

total_start_time = time.time()

FILES_DIR = './in_video'
OUT_DIR = './out_video'

DEFAULT_VIDEO = './parrot4k.mp4'

os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

File = collections.namedtuple('File', ['full_path', 'num_bytes', 'bpp', 'compressed_path', 'compression_time', 'decompression_time'])

# Split Video in frames
def split_video(video):
  vidcap = cv2.VideoCapture(video)
  success, image = vidcap.read()

  fps = vidcap.get(cv2.CAP_PROP_FPS)
  frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
  print(f'fps: {fps}')
  print(f'frames: {frame_count}')

  for i in range(frame_count):
    cv2.imwrite(f'{FILES_DIR}/frame{i}.png', image) # save frame as PNG file (uncompressed)
    success, image = vidcap.read()

"""
hific-lo: highest compression (lowest filesize)
hific-mi: mid compression
hific-hi: low compression (high filesize)
"""
model = 'hific-lo'

# Split the video into single frames
print('Splitting video into single frames...')
split_video(DEFAULT_VIDEO)

# Print out number of extracted frames
all_files = os.listdir(FILES_DIR)

# downsize all frames by facotr of 15 (\\ integer division)
for file_name in all_files:
  img = Image.open(os.path.join(FILES_DIR, file_name))
  w, h = img.size
  img = img.resize((w // 15, h // 15))

SUPPORTED_EXT = {'.png', '.jpg'}

"""
Calculates the bits per pixel (BPP) value for an image.

Args:
    image_dimensions (tuple): A tuple containing the width and height of the image.
    num_bytes (int): The number of bytes used to store the image.

Returns:
    float: The bits per pixel (BPP) value.
"""
def get_bpp(image_dimensions, num_bytes):
  w, h = image_dimensions
  return num_bytes * 8 / (w * h)

"""
Checks whether an image has an alpha channel.

Args:
    img_p (str): The path to the image file.

Returns:
    bool: True if the image has an alpha channel (RGBA mode), False otherwise.
"""
def has_alpha(img_p):
  im = Image.open(img_p)
  return im.mode == 'RGBA'

all_outputs = []
for file_name in all_files:
  # skip directories
  if os.path.isdir(file_name):
    continue
  # file format not supported
  if not any(file_name.endswith(ext) for ext in SUPPORTED_EXT):
    print('Skipping', file_name, '...')
    continue
  
  full_path = os.path.join(FILES_DIR, file_name)
  
  # skip if image has alpha channel, e.g. transparency in PNG
  if has_alpha(full_path):
    print('Skipping because of alpha channel:', file_name)
    continue
  
  file_name, _ = os.path.splitext(file_name)

  compressed_path = os.path.join(OUT_DIR, f'{file_name}_{model}.tfci')
  output_path = os.path.join(OUT_DIR, f'{file_name}_{model}.png')
  
  if os.path.isfile(output_path):
    print('Exists already:', output_path)
    num_bytes = os.path.getsize(compressed_path)
    all_outputs.append(
      File(output_path, num_bytes,
           get_bpp(Image.open(full_path).size, num_bytes)))
    continue

  compress_start_time = time.time()
  print(f'Compressing {file_name} with {model}...')
  
  tfci.compress(model, full_path, compressed_path)
  num_bytes = os.path.getsize(compressed_path)
  compression_time = time.time()-compress_start_time
  
  print(f'Compressed to {num_bytes} bytes, in {compression_time:.2f}s')
  
  decompress_start_time = time.time()
  print(f'Decompressing {file_name}...')
  tfci.decompress(compressed_path, output_path)

  decompression_time = time.time()-decompress_start_time
  print(f'Decompressed in {decompression_time:.2f}s')

  # append File outpout info
  all_outputs.append(
      File(output_path, num_bytes,
           get_bpp(Image.open(full_path).size, num_bytes), compressed_path, compression_time, decompression_time))


COMPRESSED_VIDEO_ZIP = './compressed_video.hific.zip'
DECOMPRESSED_VIDEO_ZIP = './decompressed_video.hific.zip'

COMPRESSION_STATISTICS = 'compression_statistics.pkl'

with zipfile.ZipFile(COMPRESSED_VIDEO_ZIP, 'w') as zf:
  for f in all_outputs:
    zf.write(f.compressed_path)

with zipfile.ZipFile(DECOMPRESSED_VIDEO_ZIP, 'w') as zf:
  for f in all_outputs:
    path_with_bpp = f.full_path.replace('.png', f'-{f.bpp:.3f}bpp.png')
    zf.write(f.full_path, os.path.basename(path_with_bpp))

# save compression statistics to file
pickle.dump(all_outputs, open(COMPRESSION_STATISTICS, 'wb'))

print(f'All done! Compressed & Decompressed in {time.time()-total_start_time:.2f}s')

print(f'Original video filesize: {os.path.getsize(DEFAULT_VIDEO)/1e9:.2f}GB')
print(f'Compressed video filesize: {os.path.getsize(COMPRESSED_VIDEO_ZIP)/1e9:.2f}GB')
print(f'Decompressed video filesize: {os.path.getsize(DECOMPRESSED_VIDEO_ZIP)/1e9:.2f}GB')

OUT_VIDEO_FILE = 'out_hific_lo_' + DEFAULT_VIDEO

frames2video.createMP4fromFrames(OUT_DIR, OUT_VIDEO_FILE, 25)

print(f'\nCompressed video saved to : {COMPRESSED_VIDEO_ZIP}')
print(f'Decompressed video saved to: {OUT_VIDEO_FILE}')
