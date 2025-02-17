import tkinter as tk
from tkinter import ttk
import requests
import threading
import time
from datetime import datetime
import socket
import json

class ProxyChK:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy ChK | H4CK3R")
        self.root.configure(bg='black')
        
        # Configuração da janela
        self.root.geometry("800x600")
        
        # Estilo
        style = ttk.Style()
        style.configure("Custom.TLabel", foreground="lime", background="black")
        style.configure("Custom.TButton", foreground="lime", background="black")
        
        # Frame principal
        main_frame = tk.Frame(root, bg='black')
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        header = tk.Label(main_frame, text="Proxy ChK v1.0", 
                         fg="lime", bg="black", font=("Courier", 20))
        header.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(main_frame, text="Status: Aguardando...", 
                                   fg="lime", bg="black", font=("Courier", 12))
        self.status_label.pack()
        
        # Área de resultados
        self.result_text = tk.Text(main_frame, height=20, bg="black", fg="lime",
                                 font=("Courier", 10))
        self.result_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Configurar tags de cores
        self.result_text.tag_configure("live", foreground="lime")
        self.result_text.tag_configure("dead", foreground="red")
        
        # Botão de início
        self.start_button = tk.Button(main_frame, text="INICIAR TESTE", 
                                    command=self.start_testing,
                                    bg="black", fg="lime", font=("Courier", 12))
        self.start_button.pack(pady=10)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, length=300, mode='determinate')
        self.progress.pack(pady=10)
        
    def log(self, message, status=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.result_text.insert(tk.END, full_message)
        
        # Aplica cor à última linha baseado no status
        if status == "live":
            last_line_start = self.result_text.index("end-2c linestart")
            last_line_end = self.result_text.index("end-1c")
            self.result_text.tag_add("live", last_line_start, last_line_end)
        elif status == "dead":
            last_line_start = self.result_text.index("end-2c linestart")
            last_line_end = self.result_text.index("end-1c")
            self.result_text.tag_add("dead", last_line_start, last_line_end)
            
        self.result_text.see(tk.END)
        
    def format_proxy(self, proxy):
        """Formata o proxy corretamente removendo prefixos http:// se existirem"""
        proxy = proxy.strip()
        proxy = proxy.replace('http://', '')
        proxy = proxy.replace('https://', '')
        return proxy

    def test_proxy(self, proxy):
        try:
            proxy = self.format_proxy(proxy)
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            # Inicia a contagem do tempo
            start_time = time.time()
            
            # Faz o teste com timeout de 10 segundos
            response = requests.get('http://ip-api.com/json', 
                                 proxies=proxies, 
                                 timeout=10,
                                 verify=False)
            
            # Calcula o tempo de resposta
            response_time = (time.time() - start_time) * 1000  # Converte para ms
            
            if response.status_code == 200:
                # Obtém informações de localização
                data = response.json()
                country = data.get('country', 'Desconhecido')
                
                # Salva proxy funcional (modo append)
                with open('live.txt', 'a') as f:
                    f.write(f"{proxy}\n")
                
                self.log(f"LIVE: {proxy} | País: {country} | "
                        f"Tempo de Resposta: {int(response_time)}ms", "live")
            else:
                self.log(f"DEAD: {proxy} | Status code: {response.status_code}", "dead")
                
        except requests.exceptions.ProxyError as e:
            self.log(f"DEAD: {proxy} | Erro de conexão com proxy", "dead")
        except requests.exceptions.ConnectTimeout:
            self.log(f"DEAD: {proxy} | Timeout", "dead")
        except requests.exceptions.SSLError:
            self.log(f"DEAD: {proxy} | Erro SSL", "dead")
        except Exception as e:
            self.log(f"DEAD: {proxy} | Erro: {str(e)}", "dead")
            
    def start_testing(self):
        def run_tests():
            try:
                with open('lista.txt', 'r') as f:
                    proxies = f.read().splitlines()
                
                total = len(proxies)
                self.progress['maximum'] = total
                
                for i, proxy in enumerate(proxies):
                    self.status_label.config(
                        text=f"Status: Testando {i+1}/{total} proxies...")
                    self.test_proxy(proxy)
                    self.progress['value'] = i + 1
                    self.root.update()
                
                self.status_label.config(text="Status: Teste concluído!")
                self.log("=== TESTE FINALIZADO ===")
                
            except Exception as e:
                self.log(f"Erro ao ler arquivo: {str(e)}")
        
        # Inicia os testes em uma thread separada
        threading.Thread(target=run_tests, daemon=True).start()

# Inicialização da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = ProxyChK(root)
    root.mainloop()