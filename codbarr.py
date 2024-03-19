from pyzbar.pyzbar import decode
import cv2
import csv
import tkinter as tk
from tkinter import simpledialog
import sqlite3

# Conexión a la base de datos SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS codigos_barras
                  (codigo TEXT PRIMARY KEY, tipo TEXT, cantidad INTEGER)''')
conn.commit()

def add_to_database(barcode_data, barcode_type):
    cursor.execute("INSERT INTO codigos_barras (codigo, tipo, cantidad) VALUES (?, ?, 1)", (barcode_data, barcode_type))
    conn.commit()

def update_quantity(barcode_data):
    cursor.execute("UPDATE codigos_barras SET cantidad = cantidad + 1 WHERE codigo = ?", (barcode_data,))
    conn.commit()

def check_database(barcode_data):
    cursor.execute("SELECT * FROM codigos_barras WHERE codigo = ?", (barcode_data,))
    result = cursor.fetchone()
    if result:
        update_quantity(barcode_data)
        return True, result[1]
    else:
        return False, None

# Función para agregar un nuevo código de barras a la base de datos
def add_barcode_to_database(barcode_data, barcode_type):
    answer = tk.messagebox.askquestion("Código de Barras Nuevo", f"El código de barras '{barcode_data}' no está en la base de datos. ¿Desea agregarlo?")
    if answer == 'yes':
        add_to_database(barcode_data, barcode_type)
        tk.messagebox.showinfo("Código de Barras Agregado", f"El código de barras '{barcode_data}' ha sido agregado a la base de datos.")

# Configuración de la ventana tkinter para agregar datos
def add_data():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    barcode_data = simpledialog.askstring("Agregar Código de Barras", "Ingrese el código de barras:")
    barcode_type = simpledialog.askstring("Tipo de Código de Barras", "Ingrese el tipo de código de barras (Ej. EAN13):")
    if barcode_data and barcode_type:
        add_to_database(barcode_data, barcode_type)

# Configuración de la captura de video
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    barcodes = decode(frame)

    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        found_in_database, barcode_type_db = check_database(barcode_data)

        if found_in_database:
            text = f"{barcode_data} ({barcode_type_db}) x 1"
        else:
            text = f"{barcode_data} ({barcode_type}) - No en BD"
            add_barcode_to_database(barcode_data, barcode_type)

        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow("Barcode Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.waitKey(1) & 0xFF == ord('a'):
        add_data()

cap.release()
cv2.destroyAllWindows()
conn.close()
