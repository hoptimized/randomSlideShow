import getopt
import os
import random
import sys

from tkinter import *
from PIL import Image, ImageTk, ImageOps

class App(Tk):
    def __init__(self):
        super().__init__()

        self.job = None
        self.history = []
        self.future = []
        self.running = True

        self.setupWindow()
        self.setupCanvas()
        self.discoverFiles()
        self.runSlideshow()

    def setupWindow(self):
        self.w = self.winfo_screenwidth()
        self.h = self.winfo_screenheight()
        self.title('Slideshow')
        self.attributes('-fullscreen', True)    
        self.config(bg='black')
        self.overrideredirect(1)
        self.geometry("%dx%d+0+0" % (self.w, self.h))
        self.focus_set()    
        self.bind("<Escape>", self.onExit)
        self.bind("<Key>", self.onKeyDown)

    def setupCanvas(self):
        self.canvas = Canvas(self,width=self.w,height=self.h)
        self.canvas.configure(background='black')
        self.canvas.configure(highlightthickness=0)
        self.canvas.configure(bd=0)
        self.canvas.pack()

    def discoverFiles(self):
        self.files = []
        for rel_path in os.listdir(dirPath):
            abs_path = os.path.join(dirPath, rel_path)
            if os.path.isfile(abs_path):
                self.files.append(abs_path)

    def onExit(self, event):
        self.withdraw()
        self.quit()
        exit()

    def onKeyDown(self, event):
        if event.keycode == 39:
            self.seekForward()
        elif event.keycode == 37:
            self.seekBackward()
        elif event.keycode == 32:
            self.toggleRunning()

    def seekForward(self):
        self.pause()
        self.resume()

    def seekBackward(self):
        if len(self.history) >= 2:
            self.pause()
            self.future.append(self.history.pop())
            self.showImage(self.history.pop())

    def toggleRunning(self):
        if self.running == True:
            self.pause()
        else:
            self.resume() 

    def pause(self):
        if self.running == True:
            self.running = False
            self.after_cancel(self.job)
            
    def resume(self):
        if self.running == False:
            self.running = True
            self.runSlideshow()

    def runSlideshow(self):
        file = None

        if len(self.future) > 0:
            file = self.future.pop()
            self.showImage(file)
        else:
            while len(self.files) > 0:
                try:
                    file = random.choice(self.files)
                    self.showImage(file)
                    break
                except:
                    self.files.remove(file)

            if len(self.files) == 0:
                print("No images found in directory. Leaving.")
                self.onExit(None)
                return

        self.job = self.after(secondsPerPhoto * 1000, self.runSlideshow)

    def showImage(self, file):
        img = Image.open(file)
        img = ImageOps.exif_transpose(img)

        imgWidth, imgHeight = img.size
        if imgWidth > self.w or imgHeight > self.h:
            ratio = min(self.w/imgWidth, self.h/imgHeight)
            imgWidth = int(imgWidth*ratio)
            imgHeight = int(imgHeight*ratio)
            img = img.resize((imgWidth,imgHeight), Image.Resampling.LANCZOS)

        self.image = ImageTk.PhotoImage(img)
        self.imagesprite = self.canvas.create_image(self.w/2,self.h/2,image=self.image)

        self.history.append(file)

dirPath = os.getcwd()
secondsPerPhoto = 7

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, "d:s:", ["directory=", "secondsPerPhoto="])
for opt, arg in opts:
    if opt in ['-d', '--directory']:
        dirPath = arg
    if opt in ['-s', '--secondsPerPhoto']:
        secondsPerPhoto = int(arg)

app = App()
app.mainloop()
