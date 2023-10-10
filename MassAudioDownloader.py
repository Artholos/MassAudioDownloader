import requests, re, os
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from bs4 import BeautifulSoup
from pydub import AudioSegment

urls = []

def get_the_fucking_dot_ogg(string):
    string = re.findall(r'/(?P<word>.*?\.ogg)/', string)
    string = [s.split('/')[-1] for s in string]
    string = ' '.join(string)
    return string

def fuck_that_dot_ogg_lets_have_dot_wav(fp = ""):
    c = 0
    if fp == "":
        fp = filedialog.askdirectory()
    for file in os.listdir(fp):
        if file.endswith(".ogg"):
            sound = AudioSegment.from_ogg(os.path.join(fp, file))
            sound.export(os.path.join(fp, file.replace(".ogg", ".wav")), format="wav")
            os.remove(os.path.join(fp, file))
            c += 1
    print(str(c) + "x .ogg files have been converted to .wav")

def build_the_list(nerple):
    global urls
    url = url_entry.get()
    response = requests.get(url)
    if response.status_code == 200:
        urls.append(url)
        url_entry.delete(0, tk.END)
        url_list.delete(0, tk.END)
        for i, url in enumerate(urls):
            url_list.insert(i, url)
    print(urls)

def on_paste(nerple):
    root.after(100, build_the_list, nerple)

def get_dat_ass(how_many_asses = 1):
    global urls

    create_subdir = False
    if how_many_asses == 0:
        how_many_asses = len(urls)
        if how_many_asses > 1:
            create_subdir = True

    print("Choose a location to download the audio files:")
    folder_path = filedialog.askdirectory()
    put_files_here = folder_path

    while how_many_asses > 0:
        how_many_asses -= 1
        url = urls[0]
        
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
            
        if create_subdir == True:
            fn = soup.title.text
            fn = fn.split(" voice")
            folder_name = fn[0]
            put_files_here = os.path.join(folder_path, folder_name)
            if not os.path.exists(put_files_here):
                os.makedirs(put_files_here)

        del urls[0]
        url_list.delete(0)

        c = 0
        for link in soup.find_all('a', href=True):
            if ".ogg" in link['href']:
                c += 1
                file_url = link['href']
                response = requests.get(file_url)
                file_name = get_the_fucking_dot_ogg(file_url)
                file_path = os.path.join(put_files_here, file_name)
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                print(f"File downloaded successfully at {file_path}")
                #break
        print(str(c) + "x audio files were discovered and downloaded.")
        fuck_that_dot_ogg_lets_have_dot_wav(put_files_here)

root = tk.Tk()
root.title("Mass Audio Downloader")
root.geometry("400x400")

url_label = tk.Label(root, text="Enter URL: ")
url_label.pack()

url_entry = tk.Entry(root)
url_entry.pack()
url_entry.bind("<Return>", build_the_list)
url_entry.bind("<Control-v>", on_paste)

download_button = tk.Button(root, text="Download All", command=lambda: get_dat_ass(0))
download_button.pack()

download_button = tk.Button(root, text="Download Top", command=lambda: get_dat_ass(1))
download_button.pack()

download_button = tk.Button(root, text="WAVify them OGGs", command=fuck_that_dot_ogg_lets_have_dot_wav)
download_button.pack()

url_list_label = tk.Label(root, text="URLs:")
url_list_label.pack()

url_list = tk.Listbox(root)
url_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()