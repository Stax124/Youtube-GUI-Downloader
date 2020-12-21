import tkinter as tk
from tkinter import filedialog
import youtube_dl
import os
import datetime
import datetime
import traceback
import platform
import os
import json
import re

pattern = re.compile(r"[-][^.]*")

class c:
    header = '\033[95m'
    okblue = '\033[94m'
    okcyan = '\033[96m'
    okgreen = '\033[92m'
    warning = '\033[93m'
    fail = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'


def print_timestamp(*_str):
    print(f"{c.bold}[{c.end}{c.warning}{datetime.datetime.now().strftime('%H:%M:%S')}{c.end}{c.bold}]{c.end}", *_str)


class Config(object):
    "Class for maintaining configuration information and files"
    def print_timestamp(self,*_str):
        print(f"{c.bold}[{c.end}{c.warning}{datetime.datetime.now().strftime('%H:%M:%S')}{c.end}{c.bold}]{c.end}", *_str)

    def load(self):
        self.print_timestamp(f"{c.bold}Loading config...{c.end}")
        try:
            self.config = json.load(open(self.CONFIG))
            type(self.config.keys())
        except:
            self.print_timestamp(f"{c.warning}Config is unavailable or protected.{c.end} {c.bold}Loading fallback...{c.end}")
            self.config = self.fallback
            self.print_timestamp(f"{c.bold}Fallback loaded{c.end}")
            try:
                self.print_timestamp(f"{c.bold}Creating new config file:{c.end} {c.okgreen}{self.CONFIG}{c.end}")
                self.save()
            except Exception as e:
                self.print_timestamp(traceback.format_exc())
                self.print_timestamp(f"{c.fail}Error writing config file, please check if you have permission to write in this location:{c.end} {c.bold}{self.CONFIG}{c.end}")
                return
        self.print_timestamp(f"{c.bold}Config loaded{c.end}")

    def __init__(self):
        if platform.system() == "Windows":
            self.CONFIG = os.environ["userprofile"] + r"\.youtube-gui" # Rename this
        else:
            self.CONFIG = os.path.expanduser("~")+r"/.youtube-gui" # Rename this ... alternative for linux or Unix based systems
        self.config = {}
        self.fallback = {
            "background": "#1c1c1c",
            "foreground": "#ffffff",
            "songs": {},
            "format": "",
            "directory": "",
            "output": "",
            "font": ("Arial", "10", "bold"),
            "accent": "yellow",
            "highlightthickness": 1
        }

    def save(self):
        try:
            with open(self.CONFIG, "w") as f:
                json.dump(self.config, f, indent=4)
        except:
            self.print_timestamp(f"Unable to save data to {self.CONFIG}")

    def json_str(self):
        return json.dumps(self.config)

    def __repr__(self):
        return self.config

    def __getitem__(self, name: str):
        try:
            return self.config[name]
        except:
            self.print_timestamp(f"{c.bold}{name}{c.end} {c.warning}not found in config, trying to get from fallback{c.end}")
            self.config[name] = self.fallback[name]
            self.save()
            return self.fallback[name]

    def __setitem__(self, key: str, val):
        self.config[key] = val
        self.save()

    def __delitem__(self, key: str):
        self.config.pop(key)
        self.save()

config = Config()
config.load()


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, height=42, width=42, bg=config["background"])
        self.master = master
        self.pack()
        self.directory = "."
        self.create_widgets()

    def create_widgets(self):
        self.urllabel = tk.Label(self, text="URL to download", bg=config["background"], fg=config["foreground"], font=config["font"])
        self.urllabel.pack()

        self.urlframe = tk.Frame(self, bg=config["background"])
        self.urlframe.pack()
        self.userInput = tk.Entry(self, width=60, font=config["font"], highlightbackground=config["accent"], fg="white", bg=config["background"], highlightthickness=config["highlightthickness"])
        self.userInput.pack(in_=self.urlframe, side=tk.LEFT)
        self.Addbutton = tk.Button(self, font=config["font"], fg="white", bg=config["background"])
        self.Addbutton["text"] = "Add"
        self.Addbutton["command"] = self.appendURL
        self.Addbutton.pack(in_=self.urlframe, side=tk.LEFT)

        self.list = tk.Listbox(self, width=100, height=30, fg="white", bg=config["background"], font=config["font"], highlightbackground=config["accent"])
        self.list.insert(0, *config["songs"])
        self.list.pack()

        self.bottomframe = tk.Frame(self, bg=config["background"])
        self.bottomframe.pack()
        self.remove_from_list = tk.Button(self,width=20, font=config["font"], highlightbackground=config["accent"], fg="white", bg=config["background"])
        self.remove_from_list["text"] = "Remove"
        self.remove_from_list["command"] = self.remove
        self.remove_from_list.pack(pady=2, in_=self.bottomframe, side=tk.LEFT)
        self.get_formats = tk.Button(self,width=20, font=config["font"], highlightbackground=config["accent"], fg="white", bg=config["background"])
        self.get_formats["text"] = "Formats"
        self.get_formats["command"] = self.formats
        self.get_formats.pack(pady=2, in_=self.bottomframe, side=tk.LEFT)

        self.formatlabel = tk.Label(self, text="Youtube format", bg=config["background"], fg=config["foreground"], font=config["font"], highlightbackground=config["accent"])
        self.formatlabel.pack()
        self.format = tk.Entry(self, width=90, font=config["font"], highlightbackground=config["accent"], fg="white", bg=config["background"], highlightthickness=1)
        self.format.insert("1", config["format"])
        self.format.pack()

        self.outputlabel = tk.Label(self, text="Output format", bg=config["background"], fg=config["foreground"], font=config["font"], highlightbackground=config["accent"])
        self.outputlabel.pack()
        self.output = tk.Entry(self, width=90, font=config["font"], highlightbackground=config["accent"], fg="white", bg=config["background"], highlightthickness=1)
        self.output.insert("1", config["output"])
        self.output.pack()

        self.outputlabel = tk.Label(self, text="Directory", bg=config["background"], fg=config["foreground"], font=config["font"], highlightbackground=config["accent"])
        self.outputlabel.pack()
        self.dirframe = tk.Frame(self, bg=config["background"])
        self.dirframe.pack()
        self.direntry = tk.Entry(self, width=60, font=config["font"], highlightbackground=config["accent"], fg="white", bg=config["background"], highlightthickness=1)
        self.direntry.insert("1", config["directory"])
        self.direntry.pack(in_=self.dirframe, side=tk.LEFT)
        self.files = tk.Button(self, text="Browse", command=self.dir, font=config["font"], highlightbackground=config["accent"], fg="white", bg=config["background"])
        self.files.pack(in_=self.dirframe, side=tk.LEFT)

        self.convert_button = tk.Button(self,width=20, font=config["font"], highlightbackground=config["accent"], fg="white", bg=config["background"])
        self.convert_button["text"] = "Convert"
        self.convert_button["command"] = self.download
        self.convert_button.pack(pady=8)

    def remove(self):
        config["songs"].pop(self.list.curselection()[0])
        config.save()
        self.list.delete(self.list.curselection())

    def formats(self):
        try:
            target = self.list.get(self.list.curselection())
        except:
            print_timestamp(f"{c.fail}No URL selected from list{c.end}")
            return
        print_timestamp(f"{c.bold}Getting available formats for:{c.end} {c.warning}{target}{c.end}")

        opts = {
            "listformats": True
        }
        downloader = youtube_dl.YoutubeDL(opts)
        downloader.download([target])

    def appendURL(self):
        data = self.userInput.get()
        if data != "":
            self.list.insert(tk.END,data)
            self.userInput.delete(0,"end")
            config["songs"].append(data)
            config.save()

    def download(self):
        os.chdir(self.direntry.get())
        ids = []
        for file in os.listdir("."):
            matches = re.findall(pattern=pattern, string=file)
            match = matches[-1].split("-")[-1]
            ids.append(match)

        ids = list(dict.fromkeys(ids))

        l = list(self.list.get(0,tk.END))
        urls = []
        for url in l:
            urls.append(url.split("&list")[0])
            for id in ids:
                if id in url:
                    print(f"{c.bold}Excluding{c.end} {c.warning}{url}{c.end} {c.bold}because it already exists{c.end}")
                    urls.pop(urls.index(url))

        config["output"] = self.output.get()
        config["format"] = self.format.get()

        opts = {
            "format": self.format.get() if self.format.get() != "" else None,
            "noplaylist": False,
            "continuedl": True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.output.get(),
            }] if self.output.get() != "" else [],
        }
        downloader = youtube_dl.YoutubeDL(opts)
        urls_string = ""
        index = 1
        for url in urls:
            urls_string += f"{index}: {url}\n"
            index += 1
        print_timestamp(f"{c.bold}Starting download of{c.end}:\n{c.okgreen}{urls_string}{c.end}\n{c.bold}Count:{c.end} {c.warning}{len(urls)}{c.end}")
        downloader.download(urls)
        print_timestamp(f"{c.bold}Done{c.end}")

    def dir(self):
        self.directory = filedialog.askdirectory()
        self.direntry.delete(0, tk.END)
        self.direntry.insert(0, self.directory)
        config["directory"] = self.directory
        print_timestamp(f"{c.bold}Target directory: {c.end}{c.okgreen}{self.directory}{c.end}")

root = tk.Tk()
root.resizable(False, False)
root.winfo_toplevel().title("Youtube downloader")
app = Application(master=root)
app.mainloop()
