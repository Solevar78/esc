import tkinter as tk
from tkinter import ttk
import random
import time
import threading

class MatrixRain:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.chars = "01@#$%&*()_+-=[]{}|;:,.<>/?абвгдеёжзийклмнопрстуфхцчшщъыьэюяABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.font_size = 14
        self.columns = width // self.font_size
        self.drops = [0] * int(self.columns)
        
    def draw(self):
        self.canvas.delete("all")
        for i in range(len(self.drops)):
            x = i * self.font_size
            y = self.drops[i] * self.font_size
            char = random.choice(self.chars)
            intensity = random.randint(140, 255)
            
            r = random.randint(0, 60)
            g = random.randint(200, 255)
            b = random.randint(0, 100)
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            self.canvas.create_text(x, y, text=char, fill=color, font=("Courier", self.font_size, "bold"))
            
            if random.random() > 0.91:
                self.drops[i] = 0
            else:
                self.drops[i] += 1

class TerminatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminator V3 - Account Terminator")
        self.root.geometry("840x720")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(True, True)
        
        self.canvas = tk.Canvas(self.root, bg="#0a0a0a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.matrix = MatrixRain(self.canvas, 840, 720)
        
        self.overlay = tk.Frame(self.root, bg="#0a0a0a")
        self.overlay.place(relx=0.5, rely=0.5, anchor="center")
        
        self.setup_ui()
        self.animate_matrix()
        self.is_processing = False
    
    def setup_ui(self):
        tk.Label(self.overlay, text="⚔️ Terminator v3 ⚔️", 
                font=("Arial", 34, "bold"), fg="#00ff41", bg="#0a0a0a").pack(pady=10)
        
        tk.Label(self.overlay, text="Система блокировки аккаунтов Telegram", 
                font=("Arial", 14), fg="#aaaaaa", bg="#0a0a0a").pack(pady=5)
        
        tk.Label(self.overlay, text="Telegram: @webratsnoser3", 
                font=("Arial", 12), fg="#00cc00", bg="#0a0a0a").pack(pady=5)
        
        tk.Label(self.overlay, text="Введите имя пользователя Telegram:", 
                font=("Arial", 12), fg="#ffffff", bg="#0a0a0a").pack(pady=(30,5))
        
        self.entry = tk.Entry(self.overlay, font=("Consolas", 16), width=40, 
                             bg="#1a1a1a", fg="#00ff41", insertbackground="#00ff41", justify="center")
        self.entry.pack(pady=10)
        self.entry.insert(0, "@username")
        self.entry.bind("<KeyRelease>", self.on_entry_change)
        
        self.button = tk.Button(self.overlay, text="НАЧАТЬ ПРОЦЕСС БЛОКИРОВКИ", 
                               font=("Arial", 16, "bold"), bg="#222222", fg="#00ff41",
                               activebackground="#00aa22", activeforeground="#000000",
                               width=45, height=2, command=self.start_process)
        self.button.pack(pady=20)
        
        self.progress = ttk.Progressbar(self.overlay, length=680, mode='determinate')
        self.progress.pack(pady=10)
        
        self.status_frame = tk.Frame(self.overlay, bg="#111111", width=720, height=240, relief="sunken", bd=3)
        self.status_frame.pack(pady=15)
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="", 
                                    font=("Consolas", 13), fg="#00ff88", bg="#111111", 
                                    justify="left", anchor="nw", wraplength=690)
        self.status_label.pack(pady=18, padx=20, fill="both", expand=True)
        
        self.bottom_status = tk.Label(self.root, text="Ожидание запуска...", 
                                     font=("Arial", 10), fg="#555555", bg="#0a0a0a")
        self.bottom_status.pack(side="bottom", pady=15)
        
        style = ttk.Style()
        style.configure("TProgressbar", background="#00ff41", troughcolor="#222222")
    
    def animate_matrix(self):
        self.matrix.draw()
        self.root.after(40, self.animate_matrix)
    
    def on_entry_change(self, event=None):
        if self.is_processing:
            return
        text = self.entry.get().strip()
        if text.startswith('@') and len(text) > 3:
            self.button.config(bg="#006600", fg="#ffffff")
        else:
            self.button.config(bg="#222222", fg="#00ff41")
    
    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()
    
    def start_process(self):
        if self.is_processing:
            return
        self.is_processing = True
        self.username = self.entry.get().strip()
        if not self.username.startswith('@'):
            self.username = '@' + self.username.lstrip('@')
        
        self.button.config(state="disabled")
        self.bottom_status.config(text="Процесс запущен...")
        self.progress['value'] = 0
        
        threading.Thread(target=self.process_sequence, daemon=True).start()
    
    def process_sequence(self):
        steps = [
            (f"НАЧАЛО ПРОЦЕССА БЛОКИРОВКИ ДЛЯ {self.username}", 0.7),
            (f"Ищу аккаунт {self.username}...", 1.0),
            (f"Ищу аккаунт {self.username}\nПользователь найден", 0.9),
            ("Анализ активности аккаунта...\nСканирую историю: 0%", 0.4),
        ]
        
        for p in range(5, 101, 6):
            steps.append((f"Анализ активности аккаунта...\nСканирую историю: {p}%", 0.11))
        
        steps.extend([
            ("Поиск нарушений правил...\nНайдено нарушений: 1", 0.6),
        ])
        
        for i in range(2, 8):
            steps.append((f"Поиск нарушений правил...\nНайдено нарушений: {i}", 0.35))
        
        steps.extend([
            ("Подготовка жалоб...\nПодготовлено жалоб: 1", 0.6),
        ])
        
        for i in range(2, 7):
            steps.append((f"Подготовка жалоб...\nПодготовлено жалоб: {i}", 0.35))
        
        steps.append(("Отправка жалоб на серверы Telegram...", 0.7))
        
        for sent in range(5, 31, 5):
            steps.append((f"Отправка жалоб на серверы Telegram...\nОтправлено {sent}/30 жалоб", 0.4))
        
        steps.append((f"Процесс завершен! {self.username} будет заблокирован", 1.5))
        
        for text, delay in steps:
            self.root.after(0, lambda t=text: self.update_status(t))
            time.sleep(delay)
            self.root.after(0, lambda: self.progress.config(value=min(100, self.progress['value'] + 3.5)))
        
        self.root.after(0, lambda: self.bottom_status.config(text="Процесс завершен!"))
        time.sleep(1.2)
        self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        self.is_processing = False
        self.button.config(state="normal")
        self.progress['value'] = 0
        self.on_entry_change()

if __name__ == "__main__":
    root = tk.Tk()
    app = TerminatorApp(root)
    root.mainloop()
