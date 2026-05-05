import flet as ft
import random
import os

# 1. TABLICA CVETOV (Dlya krasoti i ponyatnosti)
CVETA_KLETOK = {
    0: "#cdc1b4",
    2: "#eee4da",
    4: "#ede0c8",
    8: "#f2b179",
    16: "#f59563",
    32: "#f67c5f",
    64: "#f65e3b",
    128: "#edcf72",
    256: "#edcc61",
    512: "#edc850",
    1024: "#edc53f",
    2048: "#edc22e",
}

def main(page: ft.Page):
    # Nastroyki stranici
    page.title = "2048 Beskonechnost Python"
    page.bgcolor = "#faf8ef"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 450
    page.window_height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Peremennie dlya igri
    pole_znacheniya = [[0] * 4 for _ in range(4)]
    tekushiy_schet = 0

    # Spisok dlya hraneniya vizualnih kontejnerov
    vizual_kletki = []

    # Funkciya dlya obnovleniya ekrana
    def obnovit_ekran():
        for r in range(4):
            for c in range(4):
                indeks = r * 4 + c
                znach = pole_znacheniya[r][c]
                # Menyaem tekst i cvet
                vizual_kletki[indeks].content.value = str(znach) if znach != 0 else ""
                vizual_kletki[indeks].bgcolor = CVETA_KLETOK.get(znach, "#3c3a32")
                vizual_kletki[indeks].content.color = "#776e65" if znach <= 4 else "#f9f6f2"
        
        tekst_scheta.value = f"Schet: {tekushiy_schet}"
        page.update()

    # Funkciya dobavleniya novogo chisla (2 ili 4)
    def dobavit_chislo():
        pustie = [(r, c) for r in range(4) for c in range(4) if pole_znacheniya[r][c] == 0]
        if pustie:
            r, c = random.choice(pustie)
            pole_znacheniya[r][c] = 2 if random.random() < 0.9 else 4

    # Logika sdviga stroki (shlopivanie chisel)
    def sdvig_stroki(stroka):
        nonlocal tekushiy_schet
        # Ubiraem nuli
        bez_nuley = [x for x in stroka if x != 0]
        # Shlopivaem odinakovie
        for i in range(len(bez_nuley) - 1):
            if bez_nuley[i] == bez_nuley[i+1]:
                bez_nuley[i] *= 2
                tekushiy_schet += bez_nuley[i]
                bez_nuley[i+1] = 0
        # Snova ubiraem nuli i dobavlyaem ih v konec
        itog = [x for x in bez_nuley if x != 0]
        return itog + [0] * (4 - len(itog))

    # Obschaya funkciya hoda
    def sdelat_hod(napravlenie):
        nonlocal pole_znacheniya
        stary_vid = [r[:] for r in pole_znacheniya]

        # 0: Levo, 1: Vniz, 2: Pravo, 3: Vverh
        for _ in range(napravlenie):
            pole_znacheniya = [list(r) for r in zip(*pole_znacheniya[::-1])]

        for i in range(4):
            pole_znacheniya[i] = sdvig_stroki(pole_znacheniya[i])

        for _ in range((4 - napravlenie) % 4):
            pole_znacheniya = [list(r) for r in zip(*pole_znacheniya[::-1])]

        if stary_vid != pole_znacheniya:
            dobavit_chislo()
            obnovit_ekran()

    # Sozdaem vizualnuyu setku
    setka_grid = ft.GridView(
        expand=False,
        runs_count=4,
        max_extent=80,
        spacing=10,
        run_spacing=10,
        width=350,
        height=350,
    )

    for _ in range(16):
        kletka = ft.Container(
            content=ft.Text("", size=28, weight="bold"),
            alignment=ft.alignment.center,
            border_radius=8,
            bgcolor=CVETA_KLETOK[0],
            width=75,
            height=75,
        )
        vizual_kletki.append(kletka)
        setka_grid.controls.append(kletka)

    # Elementi interfeysa
    tekst_scheta = ft.Text(f"Schet: 0", size=32, weight="bold", color="#776e65")
    
    # Knopki upravleniya (dlya mini-prilojeniya v Telegram)
    knopki_upravleniya = ft.Column([
        ft.Row([ft.IconButton(ft.icons.ARROW_UPWARD, on_click=lambda _: sdelat_hod(3))], alignment="center"),
        ft.Row([
            ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: sdelat_hod(0)),
            ft.IconButton(ft.icons.ARROW_DOWNWARD, on_click=lambda _: sdelat_hod(1)),
            ft.IconButton(ft.icons.ARROW_FORWARD, on_click=lambda _: sdelat_hod(2)),
        ], alignment="center", spacing=20),
    ])

    # Sobytiya klaviatury (dlya proverki na kompe)
    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Arrow Left": sdelat_hod(0)
        elif e.key == "Arrow Right": sdelat_hod(2)
        elif e.key == "Arrow Up": sdelat_hod(3)
        elif e.key == "Arrow Down": sdelat_hod(1)

    page.on_keyboard_event = on_keyboard

    # Sborka stranici
    page.add(
        ft.Text("2048 PYTHON", size=40, weight="bold", color="#776e65"),
        tekst_scheta,
        ft.Container(setka_grid, bgcolor="#bbada0", padding=10, border_radius=10),
        ft.Container(height=20),
        knopki_upravleniya
    )

    # Start igri
    dobavit_chislo()
    dobavit_chislo()
    obnovit_ekran()

# ZAPUSK (Vajnie nastroyki dlya Render)
if __name__ == "__main__":
    # Render naznachaet port sam, mi ego beryom iz peremennih
    port_servera = int(os.getenv("PORT", 8080))
    # Zapuskaem v rezhime web-servera
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port_servera, host="0.0.0.0")