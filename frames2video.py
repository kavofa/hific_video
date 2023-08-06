import os

""""
# Pfad zu den PNG-Bildern und Ausgabedatei für das MP4-Video
input_folder = 'Pfad_zu_deinem_Ordner_mit_PNG_Bildern'
output_file = 'ausgabe_video.mp4'

# Einstellungen für das Video
frame_rate = 30  # Bildrate des Videos (Frames pro Sekunde)
"""
def createMP4fromFrames(input_folder, output_file, frame_rate):
    os.system(f'Writing video to {output_file}...')
    os.system(f'ffmpeg -i {input_folder}/frame%d_hific-lo.png -c:v libx264 -vf fps={frame_rate} -pix_fmt yuv420p {output_file}')
