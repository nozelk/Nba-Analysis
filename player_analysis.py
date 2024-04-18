import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import main
import json
from PIL import Image, ImageTk
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import os

class PlayerAnalysisPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Player Analysis").pack(side="top", fill="x", pady=10)
        tk.Button(self, text="Home page",
                  command=lambda: master.switch_frame(main.StartPage)).pack()
        

        with open("files/curr_top_50.json", "r", encoding="utf-8") as f:
            self.players = []
            players_ = json.load(f)
            for i in players_:
                self.players.append(i)
        
        self.selected_player = tk.StringVar(self)
        self.selected_player.set(self.players[0])

        with open("files/first_last_year_of_player.json", "r", encoding="utf-8") as f:
            self.f_l = json.load(f)
            self.start_year = tk.StringVar(self)
            self.end_year = tk.StringVar(self)
            print(self.f_l[str(self.selected_player.get())])
            self.start_year.set(self.f_l[str(self.selected_player.get())]["First"])
            self.end_year.set(self.f_l[str(self.selected_player.get())]["Last"])


        self.player_menu = tk.OptionMenu(self, self.selected_player, *self.players)
        self.player_menu.pack()


        self.years = list(range(int(self.start_year.get()),int(self.end_year.get()) + 1))


        self.start_year_menu = tk.OptionMenu(self, self.start_year, *self.years[:-1])
        self.start_year_menu.pack()

        self.end_year_menu = tk.OptionMenu(self, self.end_year, *self.years)
        self.end_year_menu.pack()

        image_url = f"players/{str(self.selected_player.get()).split()[0]}_{str(self.selected_player.get()).split()[1]}.png"
        image = Image.open(image_url)
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.label = tk.Label(self, image=photo)
        self.label.image = photo
        self.label.pack(side="top", fill="both", expand="yes")

        self.selected_player.trace('w', self.update_player)

        self.start_year.trace('w', self.update_start_year)
        self.end_year.trace('w', self.update_end_year)

        self.stats = ["FGM", "FGA", "FG%", "FTM", "FTA", "FT%", "FG3M", "FG3A", "FG3%", "OREB", "DREB", "REB", "AST", "PF", "STL", "TOV", "BLK", "PTS", "SALARY"]
        self.stats_vars = {stat: tk.BooleanVar() for stat in self.stats}

        for stat in self.stats:
            cb = tk.Checkbutton(self, text=stat, variable=self.stats_vars[stat])
            cb.pack()

        self.draw_button = tk.Button(self, text="Draw graphs", command=self.draw_graphs)
        self.draw_button.pack()



    def update_player(self, *args):
        player = self.selected_player.get()
        print(player)
        if player == "Luka Dončić":
            image_url = f"players/Luka_Doncic.png"
        elif player == "Nikola Jokić":
            image_url = f"players/Nikola_Jokic.png"
        elif player == "De'Aaron Fox":
            image_url = f"players/DeAaron_Fox.png"
        elif player == "Jaren Jackson Jr.":
            image_url = f"players/Jaren Jackson.jpg"
        else:
            image_url = f"players/{str(self.selected_player.get()).split()[0]}_{str(self.selected_player.get()).split()[1]}.png"
        image = Image.open(image_url)
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.label.config(image=photo)
        self.label.image = photo
        self.update_years()
        self.start_year.set(self.f_l[str(self.selected_player.get())]["First"])  # Add this line
        self.end_year.set(self.f_l[str(self.selected_player.get())]["Last"])  # Add this line
        return player




    def update_start_year(self, *args):
        start = int(self.start_year.get())
        end = int(self.end_year.get())
        if start > end:
            self.end_year.set(self.start_year.get())
        self.update_years()

    def update_end_year(self, *args):
        start = int(self.start_year.get())
        end = int(self.end_year.get())
        if end < start:
            self.start_year.set(self.end_year.get())
        self.update_years()

    def update_years(self, *args):
        start = int(self.f_l[str(self.selected_player.get())]["First"])
        end = int(self.f_l[str(self.selected_player.get())]["Last"])
        self.years = list(range(start, 2024))
        self.start_year_menu['menu'].delete(0, 'end')
        for year in self.years[:-1]:
            self.start_year_menu['menu'].add_command(label=str(year), command=tk._setit(self.start_year, str(year)))
        self.end_year_menu['menu'].delete(0, 'end')
        for year in self.years:
            self.end_year_menu['menu'].add_command(label=str(year), command=tk._setit(self.end_year, str(year)))



    def draw_graphs(self):
        selected_stats = [stat for stat, var in self.stats_vars.items() if var.get()]
        start_year = int(self.start_year.get())
        end_year = int(self.end_year.get())
        player_name = self.selected_player.get()
        #if player_name == "Luka Dončić":
        #    player_name = "Luka Doncic"
        #elif player_name == "Nikola Jokić":
        #    player_name = "Nikola Jokic"
        #elif player_name == "Jaren Jackson Jr.":
        #    player_name = "Jaren Jackson Jr"
        #else:
        #    player_name = player_name 
        with open("files/curr_top_50_stats.json", "r",encoding="utf-8") as f:
            players_data = json.load(f)
        #print(players_data)
        player_data = players_data[player_name]

        print(player_data)
        for i, stat in enumerate(selected_stats):
            graph_window = tk.Toplevel(self)
            graph_window.attributes('-fullscreen', True)
            graph_window.title(f"Graph for {stat}")

            x = list(range(start_year, end_year+1))
            y = [player_data[str(year)][stat] for year in range(start_year, end_year+1)]

            fig = Figure(figsize=(10, 10), dpi=100)
            ax = fig.add_subplot(111)

            if stat.endswith('%'):
                line, = ax.plot(x, y, marker='o', label=f'{player_name.split(" ")[1]}')
                hover = self.create_hover(line, ax, fig)
            else:
                ax.bar(x, y, label=f'{player_name.split(" ")[1]}')
                hover = self.create_hover_columnar(ax.containers[0], ax, fig)

            ax.set_title(f"Analysis {stat} of {self.selected_player.get()}")
            ax.legend()

            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            canvas.mpl_connect("motion_notify_event", hover)


            save_button = tk.Button(graph_window, text="Save graph", command=lambda: self.save_graph(fig, stat))
            save_button.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

            close_button = tk.Button(graph_window, text="Close graph", command=graph_window.destroy)
            close_button.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

    def create_hover(self, line, ax, fig):
        annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(ind, line=line, annot=annot):
            x,y = line.get_data()
            annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
            text = "{}, {}".format(x[ind["ind"][0]], y[ind["ind"][0]])
            annot.set_text(text)

        def hover(event, line=line, annot=annot):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, ind = line.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        return hover
    def create_hover_columnar(self, bars, ax, fig):
        annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
    
        def update_annot(ind, bars=bars, annot=annot):
            x,y = bars[ind["ind"][0]].get_x() + bars[ind["ind"][0]].get_width() / 2, bars[ind["ind"][0]].get_height()
            annot.xy = (x, y)
            text = "{}, {}".format(x, y)
            annot.set_text(text)
    
        def hover(event, bars=bars, annot=annot):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont = False
                ind = None
                for i, bar in enumerate(bars):
                    if bar.contains(event)[0]:
                        cont = True
                        ind = {"ind": [i]}
                        break
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

    
        return hover
    

    def save_graph(self, fig, stat):
        start_year = int(self.start_year.get())
        end_year = int(self.end_year.get())
        directory = f"graphs/{self.selected_player.get()}/{start_year}-{end_year}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        fig.savefig(f"{directory}/{stat}.png")