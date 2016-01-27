from images2gif import writeGif
import os
from PIL import Image

def image_to_gif(images):
	pass
if __name__ == '__main__':
	folder = 'temp_images/'
	n = len([fn for fn in os.listdir(folder) if fn.endswith('.jpg')])
	file_names = [folder+str(i)+'.jpg' for i in range(n)]
	images = [Image.open(fn) for fn in file_names]
	filename = "my_gif.gif"
	writeGif(filename, images, duration=0.4)
