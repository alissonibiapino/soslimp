import customtkinter as ctk
from PIL import Image

# Outras views
from views.home import Home
from views.transaction import Transaction
from views.login import Login

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração inicial do App
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("soslimp-theme.json")
        self.title("SOSLimp")
        self.geometry("1280x720")

        # Inicia o app sem nada, depois inicia e chama a home
        self.current_frame = None
        self.show_login()
        # self.current_frame = Home(self)
        # self.current_frame.pack(fill="both", expand=True)

        # self.frames = {}

        # for screen in (Home, Transaction):
        #     frame = screen(self.container, self)
        #     self.frames[screen] = frame
        #     frame.grid(row=0, column=0, sticky="nsew")

        # self.show_frame(Home)
        
        # self.mainloop()
    
    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = Login(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_home(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = Home(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_transaction(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = Transaction(self)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
