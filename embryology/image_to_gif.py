# from images2gif import writeGif
import os
import gzip
import pickle
# from PIL import Image

def image_to_gif(images):
	pass
if __name__ == '__main__':
	filename = '/Users/joelsimon/Downloads/neat-checkpoint-10'
	f = gzip.open(filename)
	foo = pickle.load(f)
	print(foo[5])

	# folder = 'temp_images/'
	# n = len([fn for fn in os.listdir(folder) if fn.endswith('.jpg')])
	# file_names = [folder+str(i)+'.jpg' for i in range(n)]
	# images = [Image.open(fn) for fn in file_names]
	# filename = "my_gif.gif"
	# writeGif(filename, images, duration=0.4)
