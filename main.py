import flet as ft
import flet_fastapi
from fastapi import FastAPI, Request
import sqlite3
import uvicorn
import os

# --- DATABASE INIT ---
def init_db():
    conn = sqlite3.connect("monitor.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS leituras 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, temp TEXT, hum TEXT, gas TEXT, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn

db_conn = init_db()
app = FastAPI()

def main(page: ft.Page):
    page.title = "Monitor Silo Bag"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    lbl_temp = ft.Text("0°C", size=50, weight="bold", color="orange")
    lbl_hum = ft.Text("0%", size=50, weight="bold", color="blue")
    lbl_gas = ft.Text("0 ppm", size=50, weight="bold", color="green")

    def atualizar_tela():
        try:
            cursor = db_conn.cursor()
            cursor.execute("SELECT temp, hum, gas FROM leituras ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                lbl_temp.value = f"{row[0]}°C"
                lbl_hum.value = f"{row[1]}%"
                lbl_gas.value = f"{row[2]} ppm"
                page.update()
        except:
            pass

    page.pubsub.subscribe(lambda _: atualizar_tela())

    page.add(
        ft.Text("📊 Painel Silo Bag", size=32, weight="bold"),
        ft.Divider(),
        ft.Column([
            ft.Container(content=ft.Column([ft.Text("Temperatura"), lbl_temp]), bgcolor="#333333", padding=20, border_radius=10, width=300),
            ft.Container(content=ft.Column([ft.Text("Umidade"), lbl_hum]), bgcolor="#333333", padding=20, border_radius=10, width=300),
            ft.Container(content=ft.Column([ft.Text("Gas CO2"), lbl_gas]), bgcolor="#333333", padding=20, border_radius=10, width=300),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
    atualizar_tela()

@app.post("/update")
async def update_data(request: Request):
    data = await request.json()
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO leituras (temp, hum, gas) VALUES (?, ?, ?)", 
                   (data.get("temp"), data.get("hum"), data.get("gas")))
    db_conn.commit()
    flet_fastapi.send_all("/update", {"status": "ok"})
    return {"status": "success"}

app.mount("/", flet_fastapi.app(main))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
