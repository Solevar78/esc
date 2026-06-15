import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 630, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Terminator V3 - Account Terminator")
clock = pygame.time.Clock()

# Цвета
COLOR_BG = (24, 24, 28)
COLOR_PANEL_BG = (18, 18, 20)
COLOR_TEXT_MUTED = (120, 120, 125)
COLOR_TEXT_LIGHT = (200, 200, 205)
COLOR_TEXT_BRIGHT = (255, 255, 255)
COLOR_BORDER = (45, 45, 50)
COLOR_BTN_HOVER = (60, 60, 65)
COLOR_PROGRESS = (50, 150, 50)

# Шрифты
font_title = pygame.font.SysFont("Calibri", 28, bold=True)
font_main = pygame.font.SysFont("Calibri", 16)
font_console = pygame.font.SysFont("Consolas", 14)

# Эффект падающих символов (Матрица)
FONT_SIZE = 14
columns = WIDTH // FONT_SIZE
drops = [random.randint(-40, 0) for _ in range(columns)]
chars = ["@", "#", "$", "%", "&", "*", "1", "0", "§"]

# Состояние интерфейса
username = ""
is_running = False
progress = 0.0  # От 0 до 100
start_time = 0
current_stage = 0

# Тайминги для логов (всего ~11 секунд)
# Структура: (время_в_секундах, функция_генерации_текста)
stages = [
    (0.0, lambda u: [f"НАЧАЛО ПРОЦЕССА БЛОКИРОВКИ ДЛЯ {u}...", f"Ищу аккаунт {u}..."]),
    (1.5, lambda u: [f"Ищу аккаунт {u}...", "Пользователь найден"]),
    (2.5, lambda u: ["Анализ активности аккаунта...", "Сканирую историю: 23%"]),
    (2.8, lambda u: ["Анализ активности аккаунта...", "Сканирую историю: 57%"]),
    (3.2, lambda u: ["Анализ активности аккаунта...", "Сканирую историю: 100%"]),
    (3.5, lambda u: ["Поиск нарушений правил...", "Найдено нарушений: 1"]),
    (4.0, lambda u: ["Найдено нарушений: 2", "Найдено нарушений: 3"]),
    (4.5, lambda u: ["Найдено нарушений: 4", "Найдено нарушений: 5"]),
    (5.0, lambda u: ["Найдено нарушений: 6", "Найдено нарушений: 7"]),
    (5.5, lambda u: ["Подготовка жалоб...", "Подготовлено жалоб: 1"]),
    (6.0, lambda u: ["Подготовлено жалоб: 2", "Подготовлено жалоб: 3"]),
    (6.5, lambda u: ["Подготовлено жалоб: 4", "Подготовлено жалоб: 5"]),
    (7.0, lambda u: ["Подготовлено жалоб: 6", "Отправка жалоб на серверы Telegram..."]),
    (8.0, lambda u: ["Отправка жалоб на серверы Telegram...", "Отправлено 5/30 жалоб"]),
    (8.5, lambda u: ["Отправлено 10/30 жалоб", "Отправлено 15/30 жалоб"]),
    (9.0, lambda u: ["Отправлено 20/30 жалоб", "Отправлено 25/30 жалоб"]),
    (9.5, lambda u: ["Отправлено 30/30 жалоб", "Процесс завершен!"]),
    (10.5, lambda u: [f"Процесс завершен! {u} будет заблокирован"])
]

def draw_matrix_background():
    """Рисует плавно падающие символы на фоне."""
    for i in range(len(drops)):
        char = random.choice(chars)
        # Полупрозрачный серый цвет для символов, чтобы не отвлекали
        char_surface = font_console.render(char, True, (45, 45, 50))
        x = i * FONT_SIZE
        y = drops[i] * FONT_SIZE
        screen.blit(char_surface, (x, y))
        
        # Сбрасываем каплю наверх с шансом, если она ушла за экран
        if y > HEIGHT and random.random() > 0.975:
            drops[i] = random.randint(-10, 0)
        else:
            drops[i] += 0.5  # Скорость падения

def draw_panel(rect, border_color=COLOR_BORDER, bg_color=COLOR_PANEL_BG, radius=10):
    """Вспомогательная функция для отрисовки скругленных панелей."""
    pygame.draw.rect(screen, bg_color, rect, border_radius=radius)
    pygame.draw.rect(screen, border_color, rect, width=1, border_radius=radius)

# Главный цикл
running = True
while running:
    screen.fill(COLOR_BG)
    
    # 1. Задний фон
    draw_matrix_background()
    
    # Расчет логики процесса, если он запущен
    if is_running:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
        progress = min((elapsed_time / 11.0) * 100, 100)
        
        # Переключение стадий текста на основе времени
        for stage_idx, (stage_time, _) in enumerate(stages):
            if elapsed_time >= stage_time:
                current_stage = stage_idx
        
        if elapsed_time >= 11.0:
            is_running = False
            progress = 100.0

    # 2. Отрисовка элементов интерфейса
    
    # Заголовок "Terminator v3"
    draw_panel(pygame.Rect(35, 20, 560, 60))
    title_text = font_title.render("⚔ Terminator v3 ⚔", True, COLOR_TEXT_BRIGHT)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 33))
    
    # Подзаголовок
    sub_text = font_main.render("Система блокировки аккаунтов Telegram", True, COLOR_TEXT_MUTED)
    screen.blit(sub_text, (WIDTH//2 - sub_text.get_width()//2, 95))
    
    # Контакты разработчика
    draw_panel(pygame.Rect(35, 125, 560, 35), radius=5)
    dev_text = font_main.render("Telegram: @webratsnoser3", True, COLOR_TEXT_MUTED)
    screen.blit(dev_text, (WIDTH//2 - dev_text.get_width()//2, 133))
    
    # Метка поля ввода
    label_text = font_main.render("Введите имя пользователя Telegram:", True, COLOR_TEXT_LIGHT)
    screen.blit(label_text, (35, 185))
    
    # Поле ввода @username
    draw_panel(pygame.Rect(35, 210, 560, 45), radius=5)
    display_user = username if username else "@username"
    user_color = COLOR_TEXT_LIGHT if username else COLOR_TEXT_MUTED
    input_text = font_main.render(display_user, True, user_color)
    screen.blit(input_text, (50, 223))
    
    # Кнопка "НАЧАТЬ ПРОЦЕСС БЛОКИРОВКИ"
    btn_rect = pygame.Rect(35, 275, 560, 45)
    # Кнопка горит ярче, если введен текст и процесс не идет
    has_input = len(username.strip()) > 0 and username != "@"
    btn_bg = COLOR_BTN_HOVER if (has_input and not is_running) else COLOR_PANEL_BG
    btn_border = COLOR_TEXT_LIGHT if (has_input and not is_running) else COLOR_BORDER
    btn_text_color = COLOR_TEXT_BRIGHT if has_input else COLOR_TEXT_MUTED
    
    draw_panel(btn_rect, border_color=btn_border, bg_color=btn_bg, radius=5)
    btn_text = font_main.render("НАЧАТЬ ПРОЦЕСС БЛОКИРОВКИ", True, btn_text_color)
    screen.blit(btn_text, (WIDTH//2 - btn_text.get_width()//2, 288))
    
    # Ползунок загрузки (Прогресс-бар)
    progress_container = pygame.Rect(35, 335, 560, 15)
    draw_panel(progress_container, radius=5)
    if progress > 0:
        progress_width = int((progress / 100) * 556)
        if progress_width > 0:
            pygame.draw.rect(screen, COLOR_PROGRESS, pygame.Rect(37, 337, progress_width, 11), border_radius=3)
            
    # Большая панель вывода логов
    console_rect = pygame.Rect(35, 365, 560, 170)
    draw_panel(console_rect, radius=8)
    
    # Отрисовка строк логов
    if progress > 0:
        current_lines = stages[current_stage][1](username)
        for idx, line in enumerate(current_lines):
            line_surface = font_console.render(line, True, COLOR_TEXT_LIGHT)
            screen.blit(line_surface, (50, 385 + idx * 22))
            
    # Самая нижняя панель статуса
    status_rect = pygame.Rect(35, 550, 560, 25)
    draw_panel(status_rect, radius=5)
    
    status_string = "Ожидание запуска..."
    if is_running:
        status_string = f"Выполнение... {elapsed_time:.1f} сек."
    elif progress >= 100:
        status_string = "Процесс завершен!"
        
    status_text = font_console.render(status_string, True, COLOR_TEXT_MUTED)
    screen.blit(status_text, (WIDTH - status_text.get_width() - 45, 554))

    # 3. Обработка событий (Клики, Ввод текста)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN and not is_running:
            if event.key == pygame.K_BACKSPACE:
                username = username[:-1]
            elif event.key == pygame.K_RETURN and has_input:
                # Старт по кнопке Enter
                is_running = True
                progress = 0.0
                start_time = pygame.time.get_ticks()
            else:
                # Ограничение по длине и ввод только валидных для юзернейма символов
                if len(username) < 25 and event.unicode.isprintable():
                    # Автоматически добавляем @ в начало, если её нет
                    if len(username) == 0 and event.unicode != "@":
                        username = "@" + event.unicode
                    else:
                        username += event.unicode
                        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Проверка клика по кнопке
            if btn_rect.collidepoint(event.pos) and has_input and not is_running:
                is_running = True
                progress = 0.0
                start_time = pygame.time.get_ticks()

    pygame.display.flip()
    clock.tick(60)  # Стабильные 60 FPS

pygame.quit()
sys.exit()
