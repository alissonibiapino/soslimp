import customtkinter as ctk

FONTE_TITULO = None
FONTE_TEXTO = None

def iniciar_fontes():
    global FONTE_TITULO
    FONTE_TITULO = ctk.CTkFont(family="Segoe UI", size=22, weight='bold')
    FONTE_TEXTO = ctk.CTkFont(family="Segoe UI", size=16)