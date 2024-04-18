import tkinter as tk
from PIL import Image, ImageTk
import team_analysis
import player_analysis

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("1200x960")
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        image = Image.open("files4app/LogoNBA.png")
        image = image.resize((384, 240), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(self, image=photo)
        label.image = photo
        label.pack(side="top", fill="both", expand="yes")
        tk.Button(self, text="Team Analysis",
                  command=lambda: master.switch_frame(team_analysis.TeamAnalysisPage)).pack()
        tk.Button(self, text="Player Analysis",
                  command=lambda: master.switch_frame(player_analysis.PlayerAnalysisPage)).pack()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
