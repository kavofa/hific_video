# High-Fidelity Generative Video Compression
### Proof of Concept implementation using [HiFiC](https://hific.github.io/) generative image compression.
# Installation
```bash
git https://github.com/kavofa/hific_video
```
Installing dependencies
```bash
sh install.sh
```
Running HiFiC video compression on example video file ```parrot4k.mp4```
```bash
python hific_video.py
```
This will create the folders  ```in_video/``` and  ```out_video/```. In the folder ```in_video``` all extracted frames from the given video will be saved as PNG files.
All HiFiC compressed and decompressed frames will be saved to ```out_video/```. At the end the script will save all compressed frames to ```compressed_video.hific.zip``` – for portability. The final decompressed video will be saved to ```out_hific_lo_{video_filename}.mp4```
