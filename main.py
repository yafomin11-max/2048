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

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    """создает файл базы данных, если его еще нет"""
    conn = sqlite3.connect("leaderboard.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS players (name TEXT, score INTEGER)")
    conn.commit()
    return conn, cursor

db_conn, db_cursor = init_db()

def save_score(name, score):
    """сохраняет результат в базу данных"""
    if not name or name.strip() == "": name = "Игрок"
    db_cursor.execute("INSERT INTO players VALUES (?, ?)", (name, score))
    db_conn.commit()

def get_top_scores():
    """берет топ-5 лучших результатов из базы"""
    db_cursor.execute("SELECT name, score FROM players ORDER BY score DESC LIMIT 5")
    return db_cursor.fetchall()


def main(page: ft.Page):
    # настройки окна
    page.title = "2048"
    page.bgcolor = "#faf8ef"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.theme_mode = ft.ThemeMode.LIGHT # форсируем светлую тему для красоты

    # переменные игры
    pole = [[0] * 4 for _ in range(4)]
    score = 0
    cells = []

    # --- ФУНКЦИИ УПРАВЛЕНИЯ ---

    def restart_game(e):
        """сбрасывает игру и сохраняет текущий результат"""
        nonlocal pole, score
        if score > 0:
            save_score(name_input.value, score)
        
        pole = [[0] * 4 for _ in range(4)]
        score = 0
        dobavit_chislo()
        dobavit_chislo()
        obnovit_vizual()

    def show_leaderboard(e):
        """показывает всплывающее окно с рекордами (исправлено под новые версии Flet)"""
        tops = get_top_scores()
        items = [ft.Text(f"{n} — {s} очков", size=18, weight="bold") for n, s in tops]
        
        if not items:
            items = [ft.Text("Рекордов пока нет. Будь первым!", italic=True)]

        def close_dlg(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Топ игроков 🏆"),
            content=ft.Column(items, tight=True, width=200),
            actions=[
                ft.TextButton("Понятно", on_click=close_dlg)
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def obnovit_vizual():
        """обновляет экран: цифры и цвета"""
        for i in range(16):
            r, c = i // 4, i % 4
            val = pole[r][c]
            cells[i].content.value = str(val) if val > 0 else ""
            cells[i].bgcolor = CVETA.get(val, "#3c3a32")
            cells[i].content.color = "#776e65" if val <= 4 else "#f9f6f2"

        score_text.value = f"Score: {score}"
        page.update()

    def dobavit_chislo():
        """ставит 2 или 4 в пустую клетку"""
        pustie = [(r, c) for r in range(4) for c in range(4) if pole[r][c] == 0]
        if pustie:
            r, c = random.choice(pustie)
            pole[r][c] = 2 if random.random() < 0.9 else 4

    def sdvig(ryad):
        """логика слияния чисел"""
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
        """двигает плитки через поворот матрицы"""
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

    # ИНТЕРФЕЙС

    grid = ft.GridView(runs_count=4, max_extent=80, spacing=10, run_spacing=10)
    for _ in range(16):
        c = ft.Container(
            content=ft.Text("", size=25, weight="bold"),
            alignment=ft.Alignment(0, 0),
            border_radius=5,
        )
        cells.append(c)
        grid.controls.append(c)

    score_text = ft.Text("Score: 0", size=30, weight="bold", color="#776e65")
    name_input = ft.TextField(label="Имя", value="Ярослав", width=120, height=40, text_size=14)

    # Кнопки со стрелками (эмодзи - самый надежный вариант)
    controls = ft.Row([
        ft.ElevatedButton("⬅️", on_click=lambda _: move(0), style=ft.ButtonStyle(padding=10)),
        ft.ElevatedButton("⬆️", on_click=lambda _: move(3), style=ft.ButtonStyle(padding=10)),
        ft.ElevatedButton("⬇️", on_click=lambda _: move(1), style=ft.ButtonStyle(padding=10)),
        ft.ElevatedButton("➡️", on_click=lambda _: move(2), style=ft.ButtonStyle(padding=10)),
    ], alignment="center")

    # Дополнительные кнопки
    extra_menu = ft.Row([
        ft.ElevatedButton("🔄 Заново", on_click=restart_game, bgcolor="#8f7a66", color="white"),
        ft.ElevatedButton("🏆 Лидеры", on_click=show_leaderboard),
    ], alignment="center")

    page.add(
        ft.Row([score_text, name_input], alignment="center", vertical_alignment="center"),
        ft.Container(grid, width=340, height=340, bgcolor="#bbada0", padding=10, border_radius=10),
        ft.Divider(height=10, color="transparent"),
        controls,
        ft.Divider(height=10, color="transparent"),
        extra_menu
    )

    # Старт игры
    dobavit_chislo()
    dobavit_chislo()
    obnovit_vizual()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view="web_browser", port=port)
