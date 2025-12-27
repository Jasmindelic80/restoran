import requests
import tkinter as tk
from tkinter import messagebox
import os
import webbrowser

BASE_URL = "http://127.0.0.1:8000/api/"
auth = None

STOLOVI = list(range(1, 11))
selected_table = None
orders_map = {}  # pamti ID otvorene narudžbe po stolu
current_items = []
items_cache = []


# ==================== API ====================

def login():
    global auth
    auth = (
        username_entry.get().strip(),
        password_entry.get().strip()
    )
    try:
        r = requests.get(BASE_URL + "narudzbe/", auth=auth)
        r.raise_for_status()
        login_frame.pack_forget()
        app_frame.pack()
        status.config(text=f"Prijavljen: {auth[0]}")
        load_items()
    except:
        messagebox.showerror("Greška", "Neuspješan login")
        auth = None


def load_items():
    global items_cache
    r = requests.get(BASE_URL + "stavke/", auth=auth)
    items_cache = r.json()
    menu_list.delete(0, tk.END)
    for s in items_cache:
        menu_list.insert(
            tk.END,
            f"{s['id']} | {s['naziv']} | {s['cijena']}€"
        )


def create_or_get_order(sto):
    """Dohvati aktivnu narudžbu ili kreiraj novu"""
    r = requests.get(BASE_URL + f"narudzbe/?sto={sto}", auth=auth)
    r.raise_for_status()

    for o in r.json():
        if o["status"] not in ["ZATVORENA", "PLACENA"]:
            orders_map[sto] = o["id"]
            return o["id"]

    # Nema aktivne narudžbe -> kreiraj novu
    r = requests.post(
        BASE_URL + "narudzbe/",
        json={"sto_broj": sto},
        auth=auth
    )
    r.raise_for_status()
    order_data = r.json()
    orders_map[sto] = order_data["id"]
    return order_data["id"]


def fetch_order_items(order_id):
    global current_items
    r = requests.get(
        BASE_URL + f"stavke_narudzbe/?narudzba={order_id}",
        auth=auth
    )
    current_items = r.json()
    refresh_receipt()


# ==================== GUI FUNKCIJE ====================

def select_table(sto):
    global selected_table, current_items
    selected_table = sto

    # Reset UI
    for b in table_buttons.values():
        b.config(relief="raised", bg="SystemButtonFace")
    table_buttons[sto].config(relief="sunken", bg="lightgreen")

    # Očisti stare stavke
    current_items.clear()
    receipt_list.delete(0, tk.END)
    total_label.config(text="UKUPNO: 0 €")

    # Dohvati ili kreiraj narudžbu
    order_id = create_or_get_order(sto)
    fetch_order_items(order_id)

    status.config(text=f"Odabran sto {sto}")


def add_item():
    if not selected_table:
        messagebox.showwarning("Greška", "Odaberi sto")
        return
    if not menu_list.curselection():
        messagebox.showwarning("Greška", "Odaberi piće")
        return
    try:
        qty = int(qty_entry.get())
        if qty <= 0:
            raise ValueError
    except:
        messagebox.showwarning("Greška", "Neispravna količina")
        return

    idx = menu_list.curselection()[0]
    item = items_cache[idx]
    order_id = create_or_get_order(selected_table)

    # Dodaj stavku u narudžbu
    r = requests.post(
        BASE_URL + "stavke_narudzbe/",
        json={
            "narudzba": order_id,
            "stavka": item['id'],
            "kolicina": qty
        },
        auth=auth
    )
    r.raise_for_status()
    fetch_order_items(order_id)
    qty_entry.delete(0, tk.END)


def refresh_receipt():
    receipt_list.delete(0, tk.END)
    total = 0
    for i in current_items:
        line = f"{i['stavka_naziv']} x {i['kolicina']}  {i['stavka_cijena']}€"
        receipt_list.insert(tk.END, line)
        total += i['kolicina'] * float(i['stavka_cijena'])
    total_label.config(text=f"UKUPNO: {total:.2f} €")


def issue_receipt():
    global selected_table, current_items
    if not selected_table:
        messagebox.showerror("Greška", "Odaberi sto")
        return

    order_id = orders_map[selected_table]

    try:
        # Zatvori narudžbu
        r = requests.patch(
            BASE_URL + f"narudzbe/{order_id}/",
            json={"status": "PLACENA"},  # postavi status PLACENA
            auth=auth
        )
        r.raise_for_status()
        # Preuzmi PDF
        pdf_resp = requests.get(
            f"http://127.0.0.1:8000/narudzba/{order_id}/izdaj_racun/",
            auth=auth
        )
        # Opcionalno: obriši sve stavke narudžbe u bazi da ne ostaju
        r2 = requests.get(BASE_URL + f"stavke_narudzbe/?narudzba={order_id}", auth=auth)
        for stavka in r2.json():
            requests.delete(BASE_URL + f"stavke_narudzbe/{stavka['id']}/", auth=auth)



        if pdf_resp.headers.get('Content-Type') == 'application/pdf':
            filename = f"racun_{order_id}.pdf"
            with open(filename, "wb") as f:
                f.write(pdf_resp.content)
            webbrowser.open(filename)
        else:
            messagebox.showerror("Greška", "PDF nije generiran. Provjeri server.")
            return

        # Reset UI
        orders_map.pop(selected_table, None)
        current_items.clear()
        receipt_list.delete(0, tk.END)
        total_label.config(text="UKUPNO: 0 €")
        table_buttons[selected_table].config(relief="raised", bg="SystemButtonFace")
        selected_table = None
        status.config(text="Račun izdan — spremno za novu narudžbu")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Greška", f"Neuspješan zahtjev: {e}")




# ==================== GUI ====================

root = tk.Tk()
root.title("Mini POS")

# --------- LOGIN ----------
login_frame = tk.Frame(root)
tk.Label(login_frame, text="Username").grid(row=0, column=0)
username_entry = tk.Entry(login_frame)
username_entry.grid(row=0, column=1)
tk.Label(login_frame, text="Password").grid(row=1, column=0)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=1, column=1)
tk.Button(login_frame, text="LOGIN", command=login).grid(row=2, columnspan=2, pady=5)
login_frame.pack(pady=10)

# --------- APP ------------
app_frame = tk.Frame(root)

# STOLOVI
table_frame = tk.LabelFrame(app_frame, text="STOLOVI")
table_frame.grid(row=0, column=0)
table_buttons = {}
for i, sto in enumerate(STOLOVI):
    btn = tk.Button(
        table_frame,
        text=f"Sto {sto}",
        width=10,
        command=lambda s=sto: select_table(s)
    )
    btn.grid(row=i // 2, column=i % 2, padx=3, pady=3)
    table_buttons[sto] = btn

# MENI
menu_frame = tk.LabelFrame(app_frame, text="PIĆA")
menu_frame.grid(row=0, column=1)
menu_list = tk.Listbox(menu_frame, width=30, height=10)
menu_list.pack(padx=5, pady=5)

# RAČUN
receipt_frame = tk.LabelFrame(app_frame, text="RAČUN")
receipt_frame.grid(row=0, column=2)
receipt_list = tk.Listbox(receipt_frame, width=35, height=10)
receipt_list.pack(padx=5)
total_label = tk.Label(receipt_frame, text="UKUPNO: 0 €", font=("Arial", 11, "bold"))
total_label.pack()
close_btn = tk.Button(receipt_frame, text="IZDAJ RAČUN", width=18, bg="lightblue", command=issue_receipt)
close_btn.pack(pady=4)

# DODAVANJE
qty_frame = tk.Frame(app_frame)
qty_frame.grid(row=1, column=1)
tk.Label(qty_frame, text="Količina:").pack(side="left")
qty_entry = tk.Entry(qty_frame, width=5)
qty_entry.pack(side="left", padx=3)
tk.Button(app_frame, text="DODAJ PIĆE", width=20, command=add_item).grid(row=2, column=1, pady=5)

app_frame.pack(padx=5, pady=5)
app_frame.pack_forget()  # sakrij dok login ne prođe

# STATUS
status = tk.Label(root, text="Nije prijavljen", bd=1, relief="sunken", anchor="w")
status.pack(fill="x", side="bottom")

root.mainloop()
