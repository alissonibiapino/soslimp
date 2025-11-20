import customtkinter as ctk

from PIL import Image
from database.queries import get_lojas, login

from sessao import SessaoDeLogin

lojas = get_lojas()

class Login(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        loja_escolhida = ctk.StringVar(value="Selecione uma loja")

        def logar():
            status_login = login(usuario_input.get(), senha_input.get(), lojas.get(opcao_de_loja.get(), {}).get('cod_loja'))
            if usuario_input.get() == "" : status_login_mensagem.configure(text="Insira um usuário")
            elif senha_input.get() == "" : status_login_mensagem.configure(text="Insira sua senha")
            elif opcao_de_loja.get() == "Selecione uma loja" : status_login_mensagem.configure(text="Escolha uma loja")
            elif status_login == True:
                master.show_home()
            else : status_login_mensagem.configure(text="Usuário ou senha incorretos")


        # Agilizar o login
        login_nome = ctk.StringVar(value="daniel")
        login_senha = ctk.StringVar(value="1234")

        logo = ctk.CTkImage(
            light_image=Image.open("assets/img/SOSLimp.png"),
            dark_image=Image.open("assets/img/SOSLimp.png"),
            size=(180, 50)
        )
        logo_label = ctk.CTkLabel(self, text="", image=logo)
        logo_label.pack(side="top", pady=(50, 0))

        label_login = ctk.CTkLabel(self, text="Bem-vindo", width=40, height=28, fg_color="transparent", font=("", 30))
        label_login.pack(side="top", pady=20)

        usuario_input = ctk.CTkEntry(self, placeholder_text="Usuário", width=250, height=35, font=("", 15), textvariable=login_nome)
        usuario_input.pack(side="top", pady=5)

        senha_input = ctk.CTkEntry(self, placeholder_text="Senha", width=250, height=35, font=("", 15), show="*", textvariable=login_senha)
        senha_input.pack(side="top", pady=5)

        opcao_de_loja = ctk.CTkOptionMenu(self, width=250, variable=loja_escolhida, values=list(lojas.keys()))
        opcao_de_loja.pack(side="top", pady=5)

        status_login_mensagem = ctk.CTkLabel(self, text="", text_color="red")
        status_login_mensagem.pack(side="top", pady=5)

        botao_login = ctk.CTkButton(self, text="Login", width=250, height=35, font=("", 15), command=logar)
        botao_login.pack(side="top", pady=15)

        # registrar_login = ctk.CTkButton(self, text="Registrar novo usuário", fg_color="#FAFAFA", border_width = 2, border_color = "#212121", text_color="#212121", hover_color="#EEEEEE", width=250, height=35, font=("", 15))
        # registrar_login.pack(side="top", pady=15)
