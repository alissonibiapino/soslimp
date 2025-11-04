import customtkinter as ctk
from PIL import Image

# Outras views
from views.home import Home
from views.transaction import Transaction

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração inicial do App
        ctk.set_appearance_mode("light")
        self.title("SOSLimp")
        self.geometry("1280x720")
        # self.minsize("1280x720")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        for screen in (Home, Transaction):
            frame = screen(self.container, self)
            self.frames[screen] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Home)
        
        self.mainloop()

    def show_frame(self, screen):
        frame = self.frames[screen]
        frame.tkraise()

App()