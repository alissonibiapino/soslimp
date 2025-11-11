import customtkinter as ctk

from PIL import Image

class Login(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        def login():
            master.show_home()

        logo = ctk.CTkImage(
            light_image=Image.open("assets/img/SOSLimp.png"),
            dark_image=Image.open("assets/img/SOSLimp.png"),
            size=(180, 50)
        )
        logo_label = ctk.CTkLabel(self, text="", image=logo)
        logo_label.pack(side="top", pady=(50, 0))

        label_login = ctk.CTkLabel(self, text="Bem-vindo", width=40, height=28, fg_color="transparent", font=("", 30))
        label_login.pack(side="top", pady=20)

        usuario_input = ctk.CTkEntry(self, placeholder_text="Usuário", width=250, height=35, font=("", 15))
        usuario_input.pack(side="top", pady=5)

        senha_input = ctk.CTkEntry(self, placeholder_text="Senha", width=250, height=35, font=("", 15), show="*")
        senha_input.pack(side="top", pady=5)

        botao_login = ctk.CTkButton(self, text="Login", width=250, height=35, font=("", 15), command=login)
        botao_login.pack(side="top", pady=15)

        registrar_login = ctk.CTkButton(self, text="Registrar novo usuário", fg_color="#FAFAFA", border_width = 2, border_color = "#212121", text_color="#212121", hover_color="#EEEEEE", width=250, height=35, font=("", 15))
        registrar_login.pack(side="top", pady=15)
