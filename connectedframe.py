#!/usr/bin/env python

from Tkinter import *
from os import putenv, getenv, system
from PIL import Image, ImageTk 
from glob import glob

dropbox_link = getenv("https://www.dropbox.com/sh/7uaqqjrnjznn4lc/AABaadoQfvM0JQq9sc9ulaiSa?dl=1")
download_interval = int(getenv("DOWNLOAD_INTERVAL_HOURS")) * 60 * 60 * 1000
carousel_interval = int(getenv("CAROUSEL_INTERVAL_SECONDS")) * 1000
frame_owner = getenv("FRAME_OWNER")
ifttt_key = getenv("IFTTT_KEY")

base_path = "/usr/src/app/images/"
carrousel_status = True
image_index = 0
image_list = []
initial_init = True

def download_images(url):
	archive = base_path + "temp.zip"

	remove = "sudo rm -rf " + base_path + "*"
	download = "wget -q  "+ url + " -O " + archive
	extract = "unzip -o " + archive + " -d " + base_path

	system(remove)
	system(download)
	system(extract)

def resize_images():
	images = list_images()

	for file in images:
		img = Image.open(file)
		img = img.resize((1920, 1080), Image.ANTIALIAS)
		img.save(file, "JPEG")

def list_images():
	images = []

	dir = base_path + "*.jpg","*.png"

	images = glob(dir)

	return images

def previous_image():
	global image_index
	image_index = image_index - 1

	if image_index < 0:
		image_index = len(image_list) - 1

	image_path = image_list[image_index]

	update_image(image_path)
	
def next_image():
	global image_index
	image_index = image_index + 1

	if image_index > len(image_list) - 1:
		image_index = 0

	image_path = image_list[image_index]

	update_image(image_path)

def play_pause():
	global carousel_status

	carousel_status = not carousel_status

	if(carousel_status):
		img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/pause.png"))
	else:
		img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/play.png"))
	
	play_button.configure(image=img)
	play_button.image = img

def carousel():
	if(carousel_status):
		next_image()

	root.after(carousel_interval, carousel)

def update_image(image_path):
	img = ImageTk.PhotoImage(Image.open(image_path))
	center_label.configure(image=img)
	center_label.image = img

	img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/like.png"))
	like_button.configure(image=img)
	like_button.image = img

def initialize():
	global image_list, carousel_status, initial_init
	current_carousel_status = carousel_status
	carousel_status = False

	download_images(dropbox_link)
	resize_images()
	image_list = list_images()

	carousel_status = current_carousel_status

	if(initial_init):
		initial_init = False
		root.after(1000, initialize)
	else:
		root.after(download_interval, initialize)

def send_event():
	img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/liked.png"))
	like_button.configure(image=img)
	like_button.image = img

	command = "curl -X POST -H \"Content-Type: application/json\" -d '{\"value1\":\"" + frame_owner + "\",\"value2\":\"" + image_list[image_index] + "\"}' https://maker.ifttt.com/trigger/connectedframe_like/with/key/" + ifttt_key

	system(command)

root = Tk()
root.title('Connected Frame')
root.geometry('{}x{}'.format(1920, 1080))
root.attributes("-fullscreen", True)
root.config(cursor='none')

initialize()

left_column = Frame(root, bg='black', width=0, height=1080)
center_column = Frame(root, bg='black', width=1920, height=1080)
right_column = Frame(root, bg='black', width=0, height=1080)

left_column.pack_propagate(0)
center_column.pack_propagate(0)
right_column.pack_propagate(0)

left_column.grid(row=0, column=0, sticky="nsew")
center_column.grid(row=0, column=1, sticky="nsew")
right_column.grid(row=0, column=2, sticky="nsew")

next_icon = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/next.png"))
previous_icon = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/previous.png"))
play_icon = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/pause.png"))
like_icon = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/like.png"))

previous_button = Button(left_column, image=previous_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=previous_image)
next_button = Button(left_column, image=next_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=next_image)
play_button = Button(right_column, image=play_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=play_pause)
like_button = Button(right_column, image=like_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=send_event)

center_image = Image.open(image_list[0])
center_photo = ImageTk.PhotoImage(center_image)
center_label = Label(center_column, image=center_photo)

previous_button.pack(fill=BOTH, expand=1)
next_button.pack(fill=BOTH, expand=1)
center_label.pack(side="bottom", fill=BOTH, expand=1)
play_button.pack(fill=BOTH, expand=1)
like_button.pack(fill=BOTH, expand=1)

carousel()

root.mainloop()
