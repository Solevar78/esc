import customtkinter as ctk
import tkinter as tk
import random
import time

ctk.set_appearance_mode("dark")

class MatrixRain:
    def __init__(self, canvas, width=550, height=750):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.chars = ['@', '#', '$', '&', '§', '1', '0', 'e', '£']
        self.drops = []
        for _ in range(60):
            x = random.randint(0, self.width)
            y = random.randint(-self.height, 0)
            speed = random.randint(3, 7)
            self.drops.append([x, y, speed])
        self.animate()

    def animate(self):
        self.canvas.delete("all")
        for drop in self.drops:
            x, y, speed = drop
            char = random.choice(self.chars)
            self.canvas.create_text(x, y, text=char, fill="#5a5a60", font=("Consolas", 14))
            drop[1] += speed
            if drop[1] > self.height:
                drop[1] = random.randint(-100, -10)
                drop[0] = random.randint(0, self.width)
        self.canvas.after(50, self.animate)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Terminator V3 - Account Terminator")
        self.geometry("540x650")
        self.resizable(False, False)
        self.configure(fg_color="#1c1c21")

        # ФОН
        self.bg_canvas = tk.Canvas(self, bg="#1c1c21", highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        MatrixRain(self.bg_canvas, 540, 650)

        # Заголовок
        title_frame = ctk.CTkFrame(self, fg_color="#26262b", corner_radius=10, border_width=1, border_color="#3a3a40", width=480, height=55)
        title_frame.place(x=30, y=25)
        ctk.CTkLabel(title_frame, text="⚔️ Terminator v3 ⚔️", font=("Arial Black", 22), text_color="white").pack(pady=10)

        # Подзаголовок
        sub_frame = ctk.CTkFrame(self, fg_color="#1f1f23", corner_radius=8, width=480, height=35)
        sub_frame.place(x=30, y=95)
        ctk.CTkLabel(sub_frame, text="Система блокировки аккаунтов Telegram", font=("Arial", 14), text_color="#b0b0b5").pack(pady=5)

        # Telegram @
        tg_frame = ctk.CTkFrame(self, fg_color="#26262b", corner_radius=10, border_width=1, border_color="#3a3a40", width=480, height=40)
        tg_frame.place(x=30, y=145)
        ctk.CTkLabel(tg_frame, text="Telegram: @webratsnoser3", font=("Arial", 13), text_color="#888").pack(pady=8)

        # Поле ввода
        ctk.CTkLabel(self, text="Введите имя пользователя Telegram:", font=("Arial", 13), text_color="white", fg_color="#1c1c21").place(x=35, y=205)
        self.entry = ctk.CTkEntry(self, placeholder_text="@username", width=480, height=45, fg_color="#2e2e33", border_color="#444", font=("Arial", 15))
        self.entry.place(x=30, y=235)
        self.entry.bind("<KeyRelease>", self.on_type)

        # Кнопка
        self.start_btn = ctk.CTkButton(self, text="НАЧАТЬ ПРОЦЕСС БЛОКИРОВКИ", width=480, height=50, fg_color="#2a2a2f", hover_color="#3a3a40", text_color="#6a6a6f", font=("Arial Bold", 13), state="disabled", command=self.start_process)
        self.start_btn.place(x=30, y=295)

        # Прогресс бар
        self.progress = ctk.CTkProgressBar(self, width=480, height=12, fg_color="#2a2a2f", progress_color="#7a7aff", corner_radius=5)
        self.progress.place(x=30, y=360)
        self.progress.set(0)

        # ЛОГ ПАНЕЛЬ
        self.log_box = ctk.CTkTextbox(self, width=480, height=155, fg_color="#1a1a1f", border_color="#333", border_width=1, font=("Consolas", 13), text_color="#00ff88")
        self.log_box.place(x=30, y=385)
        self.log_box.configure(state="disabled")

        # НИЖНИЙ СТАТУС
        self.status = ctk.CTkLabel(self, text="Ожидание запуска...", width=480, height=25, fg_color="#15151a", text_color="#888", anchor="e", font=("Arial", 11), corner_radius=6)
        self.status.place(x=30, y=555)

        self.running = False

    def on_type(self, event=None):
        username = self.entry.get().strip()
        if username.startswith("@") and len(username) > 2:
            self.start_btn.configure(state="normal", fg_color="#3e3e45", text_color="white", hover_color="#505058")
        else:
            self.start_btn.configure(state="disabled", fg_color="#2a2a2f", text_color="#6a6a6f")

    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("1.0", text)
        self.log_box.configure(state="disabled")

    def start_process(self):
        if self.running: return
        self.running = True
        username = self.entry.get().strip()
        self.start_btn.configure(state="disabled")
        self.progress.set(0)
        self.start_time = time.time()
        self.update_timer()

        sequence = [
            (0, f"НАЧАЛО ПРОЦЕССА БЛОКИРОВКИ ДЛЯ {username}\nИщу аккаунт {username}..."),
            (700, f"Ищу аккаунт {username}\nПользователь найден"),
            (1400, f"Анализ активности аккаунта...\nСканирую историю: 0%"),
            (2200, f"Поиск нарушений правил...\nНайдено нарушений: 1"),
            (3000, f"Найдено нарушений: 2\nНайдено нарушений: 3"),
            (3700, f"Найдено нарушений: 4\nНайдено нарушений: 5"),
            (4400, f"Найдено нарушений: 6\nНайдено нарушений: 7"),
            (5100, f"Подготовка жалоб...\nПодготовлено жалоб: 1"),
            (5800, f"Подготовлено жалоб: 2\nПодготовлено жалоб: 3"),
            (6500, f"Подготовлено жалоб: 4\nПодготовлено жалоб: 5"),
            (7200, f"Подготовлено жалоб: 6\nОтправка жалоб на серверы Telegram..."),
            (7900, f"Отправка жалоб на серверы Telegram...\nОтправлено 5/30 жалоб"),
            (8600, f"Отправлено 10/30 жалоб\nОтправлено 15/30 жалоб"),
            (9300, f"Отправлено 20/30 жалоб\nОтправлено 25/30 жалоб"),
            (10000, f"Отправлено 30/30 жалоб\nПроцесс завершен! {username} будет заблокирован"),
        ]

        for delay, text in sequence:
            self.after(delay, lambda t=text, p=delay/11000: self.update_step(t, p))
        
        for i in range(0, 101, 5):
            self.after(1450 + i*7, lambda p=i: self.log(f"Анализ активности аккаунта...\nСканирую историю: {p}%"))

        self.after(11000, self.finish)

    def update_step(self, text, progress):
        self.log(text)
        self.progress.set(progress)

    def update_timer(self):
        if not self.running: return
        elapsed = time.time() - self.start_time
        self.status.configure(text=f"Выполняется... {elapsed:.1f}s")
        if elapsed < 11:
            self.after(100, self.update_timer)

    def finish(self):
        self.running = False
        self.progress.set(1)
        self.status.configure(text="Процесс завершен!")
        self.start_btn.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()
