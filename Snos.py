import tkinter as tk
import random
import time

class TerminatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminator V3 - Account Terminator")
        self.root.geometry("630x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#18181c")

        # Настройки шрифтов
        self.font_title = ("Calibri", 24, "bold")
        self.font_main = ("Calibri", 12)
        self.font_console = ("Consolas", 11)

        # Переменные состояния
        self.is_running = False
        self.start_time = 0
        self.username = ""
        
        # Эффект падающих символов
        self.chars = ["@", "#", "$", "%", "&", "*", "1", "0", "§"]
        self.drops = []
        
        self.create_widgets()
        self.init_matrix()
        self.animate_matrix()

    def create_widgets(self):
        # Главный холст для заднего фона с символами
        self.canvas = tk.Canvas(self.root, width=630, height=620, bg="#18181c", highlightthickness=0)
        self.canvas.place(x=0, y=0)

        # 1. Заголовок
        self.draw_panel(35, 20, 595, 80, "#121214")
        self.canvas.create_text(315, 50, text="⚔ Terminator v3 ⚔", fill="#ffffff", font=self.font_title)

        # Подзаголовок
        self.canvas.create_text(315, 105, text="Система блокировки аккаунтов Telegram", fill="#78787d", font=self.font_main)

        # 2. Контакты
        self.draw_panel(35, 125, 595, 160, "#121214")
        self.canvas.create_text(315, 142, text="Telegram: @webratsnoser3", fill="#78787d", font=self.font_main)

        # Метка поля ввода
        self.canvas.create_text(35, 190, text="Введите имя пользователя Telegram:", fill="#c8c8cd", font=self.font_main, anchor="w")

        # 3. Поле ввода (Кастомное через Canvas)
        self.draw_panel(35, 210, 595, 255, "#121214")
        self.input_text_id = self.canvas.create_text(50, 232, text="@username", fill="#78787d", font=self.font_main, anchor="w")
        
        # Привязка ввода символов к окну
        self.root.bind("<Key>", self.handle_keypress)
        self.root.bind("<BackSpace>", self.handle_backspace)

        # 4. Кнопка запуска
        self.btn_id = self.draw_panel(35, 275, 595, 320, "#121214", border_color="#2d2d32")
        self.btn_text_id = self.canvas.create_text(315, 297, text="НАЧАТЬ ПРОЦЕСС БЛОКИРОВКИ", fill="#78787d", font=self.font_main)
        
        # Сделать панель-кнопку кликабельной
        self.canvas.tag_bind(self.btn_id, "<Button-1>", self.start_process)
        self.canvas.tag_bind(self.btn_text_id, "<Button-1>", self.start_process)

        # 5. Ползунок загрузки (Прогресс-бар)
        self.draw_panel(35, 335, 595, 350, "#121214")
        self.progress_bar = self.canvas.create_rectangle(37, 337, 37, 348, fill="#329632", width=0)

        # 6. Консоль вывода логов
        self.draw_panel(35, 365, 595, 545, "#121214")
        self.log_text_1 = self.canvas.create_text(50, 390, text="", fill="#c8c8cd", font=self.font_console, anchor="w")
        self.log_text_2 = self.canvas.create_text(50, 415, text="", fill="#c8c8cd", font=self.font_console, anchor="w")

        # 7. Нижний статус-бар
        self.draw_panel(35, 560, 595, 590, "#121214")
        self.status_text_id = self.canvas.create_text(580, 575, text="Ожидание запуска...", fill="#78787d", font=self.font_console, anchor="e")

    def draw_panel(self, x1, y1, x2, y2, bg_color, border_color="#2d2d32"):
        """Рисует прямоугольную панель с рамкой на холсте."""
        return self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline=border_color, width=1)

    def init_matrix(self):
        """Инициализация капель для матричного дождя."""
        columns = 630 // 15
        for i in range(columns):
            # Каждый элемент: [x, y, id_текста, символ]
            x = i * 15
            y = random.randint(-400, 0)
            char = random.choice(self.chars)
            text_id = self.canvas.create_text(x, y, text=char, fill="#232326", font=self.font_console, anchor="nw")
            self.drops.append([x, y, text_id])# Отправляем символы на самый задний план, чтобы они не перекрывали интерфейс
            self.canvas.tag_lower(text_id)

    def animate_matrix(self):
        """Анимация падения символов."""
        for drop in self.drops:
            drop[1] += 5  # Скорость падения
            if drop[1] > 620:
                drop[1] = random.randint(-50, 0)
                self.canvas.itemconfig(drop[2], text=random.choice(self.chars))
            self.canvas.coords(drop[2], drop[0], drop[1])
        self.root.after(50, self.animate_matrix)

    def update_input_view(self):
        """Обновляет внешний вид поля ввода и кнопки."""
        if not self.username:
            self.canvas.itemconfig(self.input_text_id, text="@username", fill="#78787d")
            self.canvas.itemconfig(self.btn_id, fill="#121214", outline="#2d2d32")
            self.canvas.itemconfig(self.btn_text_id, fill="#78787d")
        else:
            self.canvas.itemconfig(self.input_text_id, text=self.username, fill="#c8c8cd")
            if not self.is_running:
                # Подсвечиваем кнопку, если есть текст
                self.canvas.itemconfig(self.btn_id, fill="#3c3c41", outline="#c8c8cd")
                self.canvas.itemconfig(self.btn_text_id, fill="#ffffff")

    def handle_keypress(self, event):
        if self.is_running: return
        if event.char.isprintable() and len(event.char) == 1:
            if not self.username:
                self.username = "@" + event.char if event.char != "@" else "@"
            elif len(self.username) < 25:
                self.username += event.char
            self.update_input_view()

    def handle_backspace(self, event):
        if self.is_running: return
        if self.username:
            self.username = self.username[:-1]
            if self.username == "@": # Если осталась только собачка, стираем полностью
                self.username = ""
            self.update_input_view()

    def start_process(self, event):
        if self.is_running or not self.username or self.username == "@":
            return
        self.is_running = True
        self.start_time = time.time()
        # Блокируем кнопку (делаем тусклой во время процесса)
        self.canvas.itemconfig(self.btn_id, fill="#121214", outline="#2d2d32")
        self.canvas.itemconfig(self.btn_text_id, fill="#78787d")
        self.run_logic()

    def update_logs(self, line1, line2=""):
        self.canvas.itemconfig(self.log_text_1, text=line1)
        self.canvas.itemconfig(self.log_text_2, text=line2)

    def run_logic(self):
        if not self.is_running: return
        
        elapsed = time.time() - self.start_time
        u = self.username

        # Рассчет прогресс-бара (макс ширина 556 пикселей: от 37 до 593)
        progress_ratio = min(elapsed / 11.0, 1.0)
        current_width = 37 + int(progress_ratio * 556)
        self.canvas.coords(self.progress_bar, 37, 337, current_width, 348)

        # Тайминги смены текста
        if elapsed < 1.5:
            self.update_logs(f"НАЧАЛО ПРОЦЕССА БЛОКИРОВКИ ДЛЯ {u}", f"Ищу аккаунт {u}...")
        elif elapsed < 2.5:
            self.update_logs(f"Ищу аккаунт {u}", "Пользователь найден")
        elif elapsed < 2.8:
            self.update_logs("Анализ активности аккаунта...", "Сканирую историю: 23%")
        elif elapsed < 3.2:
            self.update_logs("Анализ активности аккаунта...", "Сканирую историю: 57%")
        elif elapsed < 3.5:
            self.update_logs("Анализ активности аккаунта...", "Сканирую историю: 100%")
        elif elapsed < 4.0:
            self.update_logs("Поиск нарушений правил...", "Найдено нарушений: 1")
        elif elapsed < 4.5:
            self.update_logs("Найдено нарушений: 2", "Найдено нарушений: 3")
        elif elapsed < 5.0:
            self.update_logs("Найдено нарушений: 4", "Найдено нарушений: 5")
        elif elapsed < 5.5:
            self.update_logs("Найдено нарушений: 6", "Найдено нарушений: 7")
        elif elapsed < 6.0:
            self.update_logs("Подготовка жалоб...", "Подготовлено жалоб: 1")
        elif elapsed < 6.5:self.update_logs("Подготовлено жалоб: 2", "Подготовлено жалоб: 3")
        elif elapsed < 7.0:
            self.update_logs("Подготовлено жалоб: 4", "Подготовлено жалоб: 5")
        elif elapsed < 8.0:
            self.update_logs("Подготовлено жалоб: 6", "Отправка жалоб на серверы Telegram...")
        elif elapsed < 8.5:
            self.update_logs("Отправка жалоб на серверы Telegram...", "Отправлено 5/30 жалоб")
        elif elapsed < 9.0:
            self.update_logs("Отправлено 10/30 жалоб", "Отправлено 15/30 жалоб")
        elif elapsed < 9.5:
            self.update_logs("Отправлено 20/30 жалоб", "Отправлено 25/30 жалоб")
        elif elapsed < 10.5:
            self.update_logs("Отправлено 30/30 жалоб", "Процесс завершен!")
        elif elapsed < 11.0:
            self.update_logs(f"Процесс завершен! {u} будет заблокирован")

        # Обновление статус-бара снизу
        if elapsed < 11.0:
            self.canvas.itemconfig(self.status_text_id, text=f"Выполнение... {elapsed:.1f} сек.")
            # Повторяем цикл логики каждые 50 мс
            self.root.after(50, self.run_logic)
        else:
            self.is_running = False
            self.canvas.coords(self.progress_bar, 37, 337, 593, 348) # Фиксируем на 100%
            self.canvas.itemconfig(self.status_text_id, text="Процесс завершен!")

if __name__ == "__main__":
    root = tk.Tk()
    app = TerminatorApp(root)
    root.mainloop()
