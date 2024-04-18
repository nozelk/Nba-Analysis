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

class TeamAnalysisPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Team Analysis").pack(side="top", fill="x", pady=10)
        tk.Button(self, text="Home page",
                  command=lambda: master.switch_frame(main.StartPage)).pack()

        with open("files/teams.json", "r") as f:
            self.teams = []
            teams_ = json.load(f)
            for i in teams_:
                self.teams.append(i["full_name"])

        self.selected_team = tk.StringVar(self)
        self.selected_team.set(self.teams[0])

        self.team_menu = tk.OptionMenu(self, self.selected_team, *self.teams)
        self.team_menu.pack()

        self.years = list(range(2004,2024))
        self.start_year = tk.StringVar(self)
        self.start_year.set(self.years[0])
        self.end_year = tk.StringVar(self)
        self.end_year.set(self.years[-1])

        self.start_year_menu = tk.OptionMenu(self, self.start_year, *self.years[:-1])
        self.start_year_menu.pack()

        self.end_year_menu = tk.OptionMenu(self, self.end_year, *self.years)
        self.end_year_menu.pack()

        image = Image.open(f"logos/{str(self.selected_team.get())}.png")
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.label = tk.Label(self, image=photo)
        self.label.image = photo
        self.label.pack(side="top", fill="both", expand="yes")


        self.stats = ["WIN%", "FGM", "FGA", "FG%", "FTM", "FTA", "FT%", "FG3M", "FG3A", "FG3%", "OREB", "DREB", "REB", "AST", "PF", "STL", "TOV", "BLK", "PTS"]
        self.stats_vars = {stat: tk.BooleanVar() for stat in self.stats}

        for stat in self.stats:
            cb = tk.Checkbutton(self, text=stat, variable=self.stats_vars[stat])
            cb.pack()

        self.start_year.trace('w', self.update_years)
        self.selected_team.trace('w', self.update_team)

        self.draw_button = tk.Button(self, text="Draw graphs", command=self.draw_graphs)
        self.draw_button.pack()


        self.salary_year = tk.StringVar(self)
        self.salary_year.set(self.years[0])

        self.salary_year_menu = tk.OptionMenu(self, self.salary_year, *self.years)
        self.salary_year_menu.pack()

        self.show_salary_button = tk.Button(self, text="Show salaries", command=self.show_and_draw_salaries)
        self.show_salary_button.pack()


    def show_and_draw_salaries(self):
        with open("files/rosters_per_year.json", "r") as f:
            rosters = json.load(f)
            team = self.selected_team.get()
            year = self.salary_year.get()

            if team in rosters and year in rosters[team]:
                salaries = {player: int(info["Salary"]) for player, info in rosters[team][year].items()}
                total = sum(salaries.values())
                small_salaries = {player: salary for player, salary in salaries.items() if salary / total < 0.02}
                other_total = sum(small_salaries.values())
                large_salaries = {player: salary for player, salary in salaries.items() if salary / total >= 0.02}

                if other_total > 0:
                    large_salaries["Other"] = other_total

                new_window = tk.Toplevel(self)
                new_window.attributes('-fullscreen', True)
                new_window.title(f"Graph for {team}")
                fig = Figure(figsize=(10, 10), dpi=100)
                ax = fig.add_subplot(111)
                labels = [f"{player}: ${salary:,}" for player, salary in large_salaries.items()]
                wedges, texts, autotexts = ax.pie(large_salaries.values(), labels=labels, autopct='%1.1f%%')
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                if "Other" in large_salaries:
                    other_legend = [f"{player}: {salary / other_total * 100:.1f}%" for player, salary in small_salaries.items()]
                    ax.legend(wedges, other_legend, title="Other", loc="upper left", bbox_to_anchor=(0, 1))

                # Nastavite naslov grafa
                with open("files/teams_salaries_per_year.json", "r") as f:
                    team_salaries = json.load(f)
                    if team in team_salaries and year in team_salaries[team]:
                        ax.set_title(f"Total Salary {year}: ${team_salaries[team][year]['Payroll']:,}")

                canvas = FigureCanvasTkAgg(fig, master=new_window)  # A tk.DrawingArea.
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

                # Dodajte gumbe za shranjevanje in zapiranje
                save_button = tk.Button(new_window, text="Save graph", command=lambda: self.save_graph_pie(fig, "salaries"))
                save_button.pack(side=tk.TOP, fill=tk.X, expand=True)

                close_button = tk.Button(new_window, text="Close graph", command=new_window.destroy)
                close_button.pack(side=tk.BOTTOM, fill=tk.X, expand=True)








    def draw_graphs(self):
        selected_stats = [stat for stat, var in self.stats_vars.items() if var.get()]
        start_year = int(self.start_year.get())
        end_year = int(self.end_year.get())
        team_name = self.selected_team.get()

        with open("files/teams_data_by_years_2004.json", "r") as f:
            teams_data = json.load(f)
        team_data = teams_data[team_name]

        with open("files/teams_data_by_years_avg_2004.json", "r") as f:
            avg_data = json.load(f)

        with open("files/teams_data_by_years_max_2004.json", "r") as f:
            max_data = json.load(f)

        with open("files/teams_data_by_years_min_2004.json", "r") as f:
            min_data = json.load(f)

        for i, stat in enumerate(selected_stats):
            graph_window = tk.Toplevel(self)
            graph_window.attributes('-fullscreen', True)
            graph_window.title(f"Graph for {stat}")

            x = list(range(start_year, end_year+1))
            y = [team_data[str(year)][stat] for year in range(start_year, end_year+1)]
            y_avg = [avg_data[str(year)][stat] for year in range(start_year, end_year+1)]
            y_max = [max_data[str(year)][stat] for year in range(start_year, end_year+1)]
            y_min = [min_data[str(year)][stat] for year in range(start_year, end_year+1)]

            fig = Figure(figsize=(10, 10), dpi=100)
            ax = fig.add_subplot(111)

            if stat.endswith('%'):
                line, = ax.plot(x, y, marker='o', label=f'{team_name.split(" ")[1]}')
                line_avg, = ax.plot(x, y_avg, marker='o', color='orange', label='Average')
                line_min, = ax.plot(x, y_min, marker='o', color='red', label='Minumum')
                line_max, = ax.plot(x, y_max, marker='o', color='green', label='Maximum')
                hover = self.create_hover(line, ax, fig)
                hover_avg = self.create_hover(line_avg, ax, fig)
                hover_min = self.create_hover(line_min, ax, fig)
                hover_max = self.create_hover(line_max, ax, fig)
            else:
                ax.bar(x, y, label=f'{team_name.split(" ")[1]}')
                line_avg, = ax.plot(x, y_avg, marker='o', color='orange', label='Average', linestyle='None')
                line_min, = ax.plot(x, y_min, marker='o', color='red', label='Minumum')
                line_max, = ax.plot(x, y_max, marker='o', color='green', label='Maximum')
                hover = self.create_hover_columnar(ax.containers[0], ax, fig)
                hover_avg = self.create_hover(line_avg, ax, fig)
                hover_min = self.create_hover(line_min, ax, fig)
                hover_max = self.create_hover(line_max, ax, fig)

            ax.set_title(f"Analysis {stat} of {self.selected_team.get()}")
            ax.legend()

            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            canvas.mpl_connect("motion_notify_event", hover)
            canvas.mpl_connect("motion_notify_event", hover_avg)
            canvas.mpl_connect("motion_notify_event", hover_min)
            canvas.mpl_connect("motion_notify_event", hover_max)

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
        directory = f"graphs/{self.selected_team.get()}/{start_year}-{end_year}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        fig.savefig(f"{directory}/{stat}.png")
    
    def save_graph_pie(self, fig, stat):
        year = int(self.salary_year.get())
        directory = f"graphs/{self.selected_team.get()}/salary/{year}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        fig.savefig(f"{directory}/{stat}.png")

    def update_years(self, *args):
        start = int(self.start_year.get())
        end = int(self.end_year.get())
        self.years = list(range(start + 1 ,2024))
        self.end_year_menu['menu'].delete(0, 'end')
        for year in self.years:
            self.end_year_menu['menu'].add_command(label=year, command=tk._setit(self.end_year, year))
        if start >= end:
            self.end_year.set(self.years[0])

    def update_team(self, *args):
        team = self.selected_team.get()
        print(team)


        image = Image.open(f"logos/{str(self.selected_team.get())}.png")
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.label.config(image=photo)
        self.label.image = photo 

        return team
