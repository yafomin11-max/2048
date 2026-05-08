import flet as ft  # библиотека для интерфейса
import random  # для рандома
import os  # чтобы взять порт
import sqlite3  # библиотека для базы данных (сохранение рекордов)

# цвета для каждого числа
CVETA = {
    0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
    16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
    256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e"
}

# --- НОВОЕ: РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    """создает файл базы данных, если его еще нет"""
    conn = sqlite3.connect("leaderboard.db", check_same_thread=False)
    cursor = conn.cursor()
    # создаем таблицу: имя игрока и его лучший счет
    cursor.execute("CREATE TABLE IF NOT EXISTS players (name TEXT, score INTEGER)")
    conn.commit()
    return conn, cursor

db_conn, db_cursor = init_db()

def save_score(name, score):
    """сохраняет результат в базу"""
    if not name: name = "Аноним"
    db_cursor.execute("INSERT INTO players VALUES (?, ?)", (name, score))
    db_conn.commit()

def get_top_scores():
    """берет топ-5 лучших результатов из базы"""
    db_cursor.execute("SELECT name, score FROM players ORDER BY score DESC LIMIT 5")
    return db_cursor.fetchall()


def main(page: ft.Page):
    # настройки окна
    page.title = "2048"  # название
    page.bgcolor = "#faf8ef"  # цвет фона
    page.vertical_alignment = "center"  # всё по центру
    page.horizontal_alignment = "center"

    # переменные игры
    pole = [[0] * 4 for _ in range(4)]
    score = 0
    cells = []
    user_name = "" # имя игрока для лидерборда

    # --- НОВОЕ: ФУНКЦИЯ ПЕРЕЗАПУСКА ---
    def restart_game(e):
        """полностью сбрасывает игру до начального состояния"""
        nonlocal pole, score
        # перед сбросом сохраняем текущий результат, если он больше 0
        if score > 0:
            save_score(name_input.value, score)
        
        pole = [[0] * 4 for _ in range(4)] # обнуляем матрицу
        score = 0 # обнуляем счет
        dobavit_chislo() # добавляем две новые плитки
        dobavit_chislo()
        obnovit_vizual() # обновляем экран

    # --- НОВОЕ: ТАБЛИЦА ЛИДЕРОВ ---
    def show_leaderboard(e):
        """показывает всплывающее окно с топ-игроками"""
        tops = get_top_scores()
        items = [ft.Text(f"{n} — {s} очков", size=18) for n, s in tops]
        
        if not items:
            items = [ft.Text("Пока рекордов нет! Будь первым!", italic=True)]

        dialog = ft.AlertDialog(
            title=ft.Text("Топ игроков 🏆"),
            content=ft.Column(items, tight=True),
            actions=[ft.TextButton("Закрыть", on_click=lambda _: page.close(dialog))]
        )
        page.open(dialog)

    def obnovit_vizual():
        """обновляет экран, меняет цвета и цифры во всех клетках"""
        for i in range(16):
            r, c = i // 4, i % 4
            val = pole[r][c]
            cells[i].content.value = str(val) if val > 0 else ""
            cells[i].bgcolor = CVETA.get(val, "#3c3a32")
            cells[i].content.color = "#776e65" if val <= 4 else "#f9f6f2"

        score_text.value = f"Score: {score}"
        page.update()

    def dobavit_chislo():
        """добавляет новую цифру в случайную пустую клетку"""
        pustie = [(r, c) for r in range(4) for c in range(4) if pole[r][c] == 0]
        if pustie:
            r, c = random.choice(pustie)
            pole[r][c] = 2 if random.random() < 0.9 else 4

    def sdvig(ryad):
        """сдвигает ряд и объединяет одинаковые числа"""
        n = [x for x in ryad if x != 0]
        for i in range(len(n) - 1):
            if n[i] == n[i + 1]:
                nonlocal score
                n[i] *= 2
                score += n[i]
                n[i + 1] = 0
        n = [x for x in n if x != 0]
        return n + [0] * (4 - len(n))

    def move(direction):
        """обрабатывает нажатие кнопок: двигает плитки"""
        nonlocal pole
        stary = [r[:] for r in pole]
        for _ in range(direction):
            pole = [list(r) for r in zip(*pole[::-1])]
        for i in range(4):
            pole[i] = sdvig(pole[i])
        for _ in range((4 - direction) % 4):
            pole = [list(r) for r in zip(*pole[::-1])]
        if stary != pole:
            dobavit_chislo()
            obnovit_vizual()

    # СОЗДАНИЕ КЛЕТОК
    grid = ft.GridView(runs_count=4, max_extent=80, spacing=10, run_spacing=10)
    for _ in range(16):
        c = ft.Container(
            content=ft.Text("", size=25, weight="bold"),
            alignment=ft.Alignment(0, 0),
            border_radius=5,
        )
        cells.append(c)
        grid.controls.append(c)

    # --- НОВОЕ: ПОЛЯ ВВОДА И КНОПКИ ---
    score_text = ft.Text("Score: 0", size=30, weight="bold", color="#776e65")
    
    # Поле для ввода имени (чтобы попасть в лидерборд)
    name_input = ft.TextField(label="Твоё имя", value="Игрок", width=150, text_size=14)

    # Кнопки управления (стрелочки)
    controls = ft.Row([
        ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: move(0)),
        ft.IconButton(ft.icons.ARROW_UPWARD, on_click=lambda _: move(3)),
        ft.IconButton(ft.icons.ARROW_DOWNWARD, on_click=lambda _: move(1)),
        ft.IconButton(ft.icons.ARROW_FORWARD, on_click=lambda _: move(2)),
    ], alignment="center")

    # Дополнительные кнопки (Старт заново и Лидерборд)
    extra_buttons = ft.Row([
        ft.ElevatedButton("🔄 Заново", on_click=restart_game, bgcolor="#8f7a66", color="white"),
        ft.ElevatedButton("🏆 Лидеры", on_click=show_leaderboard),
    ], alignment="center")

    # ВСЁ ВМЕСТЕ НА ЭКРАНЕ
    page.add(
        ft.Row([score_text, name_input], alignment="center"), # Счет и имя в одну строку
        ft.Container(grid, width=340, height=340, bgcolor="#bbada0", padding=10, border_radius=10),
        controls,
        extra_buttons # Кнопки перезапуска и лидеров
    )

    # ЗАПУСК ИГРЫ
    dobavit_chislo()
    dobavit_chislo()
    obnovit_vizual()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view="web_browser", port=port)
