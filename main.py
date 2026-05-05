import flet as ft
import random
import os
# Importiruem alignment napryamuyu dlya nadejnosti
from flet import alignment

CVETA = {
    0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
    16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
    256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e"
}

def main(page: ft.Page):
    page.title = "2048 Beskonechnost"
    page.bgcolor = "#faf8ef"
    # Ispolzuem stroki, eto samiy bezopasniy variant dlya Render
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    pole = [[0] * 4 for _ in range(4)]
    score = 0
    cells = []

    def obnovit_vizual():
        for i in range(16):
            r, c = i // 4, i % 4
            val = pole[r][c]
            cells[i].content.value = str(val) if val > 0 else ""
            cells[i].bgcolor = CVETA.get(val, "#3c3a32")
            cells[i].content.color = "#776e65" if val <= 4 else "#f9f6f2"
        score_text.value = f"Score: {score}"
        page.update()

    def dobavit_chislo():
        pustie = [(r, c) for r in range(4) for c in range(4) if pole[r][c] == 0]
        if pustie:
            r, c = random.choice(pustie)
            pole[r][c] = 2 if random.random() < 0.9 else 4

    def sdvig(ryad):
        n_ryad = [x for x in ryad if x != 0]
        for i in range(len(n_ryad) - 1):
            if n_ryad[i] == n_ryad[i+1]:
                nonlocal score
                n_ryad[i] *= 2
                score += n_ryad[i]
                n_ryad[i+1] = 0
        n_ryad = [x for x in n_ryad if x != 0]
        return n_ryad + [0] * (4 - len(n_ryad))

    def move(direction):
        nonlocal pole
        stary_pole = [r[:] for r in pole]
        for _ in range(direction):
            pole = [list(r) for r in zip(*pole[::-1])]
        for i in range(4):
            pole[i] = sdvig(pole[i])
        for _ in range((4 - direction) % 4):
            pole = [list(r) for r in zip(*pole[::-1])]
        if stary_pole != pole:
            dobavit_chislo()
            obnovit_vizual()

    grid = ft.GridView(
        runs_count=4,
        max_extent=80,
        spacing=10,
        run_spacing=10,
    )

    for _ in range(16):
        c = ft.Container(
            content=ft.Text("", size=25, weight="bold"),
            # Tut ispolzuem importirovanniy klass alignment
            alignment=alignment.center, 
            border_radius=5,
        )
        cells.append(c)
        grid.controls.append(c)

    score_text = ft.Text("Score: 0", size=30, weight="bold", color="#776e65")

    controls = ft.Row([
        ft.ElevatedButton("⬅️", on_click=lambda _: move(0)),
        ft.ElevatedButton("⬆️", on_click=lambda _: move(3)),
        ft.ElevatedButton("⬇️", on_click=lambda _: move(1)),
        ft.ElevatedButton("➡️", on_click=lambda _: move(2)),
    ], alignment="center")

    page.add(
        score_text,
        ft.Container(grid, width=340, height=340, bgcolor="#bbada0", padding=10, border_radius=10),
        controls
    )

    dobavit_chislo(); dobavit_chislo()
    obnovit_vizual()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
