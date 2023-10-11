import requests, re, os, glob, whisper, torch
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from bs4 import BeautifulSoup
from pydub import AudioSegment

urls = []

#region WAVs and OGGs
def get_the_fucking_dot_ogg(string):
    string = re.findall(r'/(?P<word>.*?\.ogg)/', string)
    string = [s.split('/')[-1] for s in string]
    string = ' '.join(string)
    return string

def fuck_that_dot_ogg_lets_have_dot_wav(fp):
    sound = AudioSegment.from_ogg(fp)
    nfp = fp.replace('.ogg', '.wav')
    sound.export(nfp, format="wav")
    os.remove(fp)
    return nfp

def fuck_that_dot_ogg_lets_have_dot_wav_folder(fp = ""):
    c = 0
    if fp == "":
        fp = filedialog.askdirectory()
    for file in os.listdir(fp):
        if file.endswith(".ogg"):
            fuck_that_dot_ogg_lets_have_dot_wav(os.path.join(fp, file))
            c += 1
    print(str(c) + "x .ogg files have been converted to .wav")
#endregion

#region The URL List
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
#endregion

#region AI Audio File Filtering
def spool_whisper_model():
    if torch.cuda.is_available():
        print("Cuda Time!")
        TheWhisperer = whisper.load_model('large-v2', device='cuda')
    else:
        print("CPU Time :c")
        TheWhisperer = whisper.load_model('large-v2')
    return TheWhisperer
TheWhisperer = spool_whisper_model()

def purge_the_voiceless(file_path, TheWhisperer):
    r = 0
    das_text = TheWhisperer.transcribe(file_path, fp16=False)
    das_text = das_text['text']
    print("Transcription: " + str(das_text))
    if not any(char.isalpha() for char in das_text) or re.search(r'[^\x00-\x7F]+', das_text):
        print("deleted: " + str(file_path))
        os.remove(file_path)
        r = 1
    return r

def purge_the_voiceless_folder(folder_path = ''):
    c = 0
    if folder_path == '':
        folder_path = filedialog.askdirectory()

    global TheWhisperer

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".wav"):
                c += purge_the_voiceless(os.path.join(root, file), TheWhisperer)
    print(str(c) + "x speechless audio files were discovered and deleted.")
#endregion

#region Moneytime - It all happens here.
def get_dat_ass(how_many_asses = 1):
    global urls, TheWhisperer

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
        k = 0
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
                file_path = fuck_that_dot_ogg_lets_have_dot_wav(file_path)
                k += purge_the_voiceless(file_path, TheWhisperer)
                #break
        print(str(c) + "x audio files were discovered and downloaded.")
        print(str(k) + "x of those downloaded were speechless audio files and were deleted.")
#endregion


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

download_button = tk.Button(root, text="WAVify them OGGs", command=fuck_that_dot_ogg_lets_have_dot_wav_folder)
download_button.pack()

download_button = tk.Button(root, text="Purge Speechless Files", command=purge_the_voiceless_folder)
download_button.pack()

url_list_label = tk.Label(root, text="URLs:")
url_list_label.pack()

url_list = tk.Listbox(root)
url_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()