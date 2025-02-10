import os
import time
import tkinter as tk
from ttkbootstrap import Style
from threading import Thread

# Variável global para armazenar o tempo restante
tempo_restante = 0
contador_ativo = False  # Controle do contador

# Função para atualizar a contagem regressiva
def atualizar_contagem():
    global tempo_restante, contador_ativo
    while contador_ativo and tempo_restante > 0:
        horas = tempo_restante // 3600
        minutos = (tempo_restante % 3600) // 60
        segundos = tempo_restante % 60
        label_tempo.config(text=f"{horas:02d}:{minutos:02d}:{segundos:02d}")
        time.sleep(1)
        tempo_restante -= 1
    
    if tempo_restante <= 0:
        label_tempo.config(text="00:00:00")

# Função para agendar o desligamento
def agendar_desligamento():
    global tempo_restante, contador_ativo
    try:
        horas = int(entry_horas.get())
        minutos = int(entry_minutos.get())
        tempo_restante = (horas * 3600) + (minutos * 60)

        if tempo_restante > 0:
            os.system(f'shutdown -s -t {tempo_restante}')
            label_status.config(text=f"Desligamento agendado em {horas}h {minutos}min.", foreground="green")
            contador_ativo = True
            Thread(target=atualizar_contagem, daemon=True).start()
        else:
            label_status.config(text="Erro: Insira um tempo válido.", foreground="red")
    except ValueError:
        label_status.config(text="Erro: Insira valores numéricos.", foreground="red")

# Função para cancelar o desligamento
def cancelar_desligamento():
    global tempo_restante, contador_ativo
    os.system("shutdown -a")
    label_status.config(text="Desligamento cancelado!", foreground="red")
    tempo_restante = 0
    contador_ativo = False
    label_tempo.config(text="00:00:00")

# Criando a interface gráfica
root = tk.Tk()
root.title("Agendador de Desligamento")
root.geometry("400x300")
root.resizable(False, False)

# Aplicando estilo moderno
style = Style(theme="darkly")

# Criando widgets
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True)

label_titulo = tk.Label(frame, text="Agendador de Desligamento", font=("Arial", 14, "bold"))
label_titulo.grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(frame, text="Horas:").grid(row=1, column=0, pady=5)
entry_horas = tk.Entry(frame, width=5)
entry_horas.grid(row=1, column=1, pady=5)

tk.Label(frame, text="Minutos:").grid(row=2, column=0, pady=5)
entry_minutos = tk.Entry(frame, width=5)
entry_minutos.grid(row=2, column=1, pady=5)

btn_agendar = tk.Button(frame, text="Agendar", command=agendar_desligamento, width=15, bg="#28a745", fg="white")
btn_agendar.grid(row=3, column=0, columnspan=2, pady=10)

btn_cancelar = tk.Button(frame, text="Cancelar", command=cancelar_desligamento, width=15, bg="#dc3545", fg="white")
btn_cancelar.grid(row=4, column=0, columnspan=2, pady=5)

label_status = tk.Label(frame, text="Aguardando comando...", fg="yellow")
label_status.grid(row=5, column=0, columnspan=2, pady=10)

label_tempo = tk.Label(frame, text="00:00:00", font=("Arial", 18, "bold"), fg="cyan")
label_tempo.grid(row=6, column=0, columnspan=2, pady=10)

# Inicia a interface
root.mainloop()
