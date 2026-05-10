import flet as ft
import flet_fastapi
from fastapi import FastAPI, Request
import sqlite3
import uvicorn
import os

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect("monitor.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS leituras 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, temp TEXT, hum TEXT, gas TEXT, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn

db_conn = init_db()
app = FastAPI()

# --- LÓGICA DA TELA (FLET) ---
def main(page: ft.Page):
    page.title = "Monitor Silo Bag"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    lbl_temp = ft.Text("0°C", size=50, weight="bold", color="orange")
    lbl_hum = ft.Text("0%", size=50, weight="bold", color="blue")
    lbl_gas = ft.Text("0 ppm", size=50, weight="bold", color="green")

    def atualizar_tela():
        cursor = db_conn.cursor()
        cursor.execute("SELECT temp, hum, gas FROM leituras ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            lbl_temp.value = f"{row[0]}°C"
            lbl_hum.value = f"{row[1]}%"
            lbl_gas.value = f"{row[2]} ppm"
            page.update()

    page.pubsub.subscribe(lambda msg: atualizar_tela())

    # Layout Profissional em Cartões
    def criar_card(titulo, valor, icon_name, icon_color):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon_name, size=40, color=icon_color),
                    ft.Text(titulo, size=16, color="grey"),
                    valor,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30,
                width=250,
            ),
            elevation=5
        )

    page.add(
        ft.Text("📊 Painel de Controle: Silo Bag #1", size=32, weight="bold"),
        ft.Divider(),
        ft.ResponsiveRow([
            criar_card("Temperatura", lbl_temp, ft.icons.THERMOSTAT, "orange"),
            criar_card("Umidade", lbl_hum, ft.icons.WATER_DROP, "blue"),
            criar_card("Gás (CO2)", lbl_gas, ft.icons.CO2, "green"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=30),
        ft.ElevatedButton("Atualizar Histórico", on_click=lambda _: atualizar_tela(), icon=ft.icons.REFRESH)
    )
    atualizar_tela()

# --- ROTA QUE ACEITA DADOS DO ESP32 (POST) ---
@app.post("/update")
async def update_data(request: Request):
    data = await request.json()
    
    # Validação simples
    if not all(k in data for k in ("temp", "hum", "gas")):
        return {"status": "error", "message": "Faltam dados"}
        
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO leituras (temp, hum, gas) VALUES (?, ?, ?)", (data["temp"], data["hum"], data["gas"]))
    db_conn.commit()
    
    flet_fastapi.send_all("/update", {"status": "update"})
    return {"status": "success", "temp": data["temp"]}

# Integração Flet + FastAPI
app.mount("/", flet_fastapi.app(main))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
