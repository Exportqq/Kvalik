# Система заказов на Python с Tkinter и SQLite

Приложение демонстрирует работу с базой данных и графическим интерфейсом для пользователей и администраторов.

---

## 1️⃣ Библиотеки

```python
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
```

* **tkinter** — стандартная библиотека для создания графических окон (GUI) в Python.
* **ttk** — модуль с красивыми виджетами: стильные кнопки, таблицы, комбобоксы.
* **messagebox** — показывает окна с ошибкой или информацией.
* **simpledialog** — простые диалоги для ввода данных пользователем (строка, число).
* **sqlite3** — встроенная база данных для хранения данных в файле `.db`.
* **datetime** — работа с датой и временем.

---

## 2️⃣ Класс `DB` — работа с базой данных

Отвечает за всю работу с данными: пользователи, товары, заказы.

```python
class DB:
    def __init__(self):
        self.conn = sqlite3.connect("app.db")
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.setup()
```

### Метод `setup`

```python
def setup(self):
    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")
    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        stock INTEGER,
        category TEXT
    )""")
    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        product TEXT,
        qty INTEGER,
        total REAL,
        created_at TEXT
    )""")
    self.conn.commit()
```

### Методы работы с данными

| Метод                                  | Назначение                                |
| -------------------------------------- | ----------------------------------------- |
| `login(u, p)`                          | Проверка логина пользователя              |
| `products(category=None)`              | Получение товаров                         |
| `categories()`                         | Список уникальных категорий               |
| `add_product(name, price, stock, cat)` | Добавление нового товара                  |
| `delete_product(name)`                 | Удаление товара                           |
| `add_order(u, name, qty, total)`       | Добавление заказа и уменьшение количества |
| `user_orders(u)`                       | История заказов пользователя              |
| `revenue_today()`                      | Выручка за сегодня                        |

> ⚡ Все изменения нужно сохранять через `self.conn.commit()`.

---

## 3️⃣ Класс `App` — графический интерфейс

```python
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Система заказов")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f3f4f6")
        self.db = DB()
        self.user = None
        self.style()
        self.login_screen()
```

### Стили интерфейса

```python
def style(self):
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("TFrame", background="#f3f4f6")
    s.configure("Card.TFrame", background="white", padding=30)
    s.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), background="white")
    s.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#f3f4f6")
    s.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), padding=10)
    s.configure("Treeview", rowheight=32, font=("Segoe UI", 11))
    s.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
```

### Очистка окна

```python
def clear(self):
    for w in self.root.winfo_children():
        w.destroy()
```

### Экран логина

```python
def login_screen(self):
    self.clear()
    box = ttk.Frame(self.root)
    box.place(relx=0.5, rely=0.5, anchor="center")
    card = ttk.Frame(box, style="Card.TFrame")
    card.pack()
    ttk.Label(card, text="Вход", style="Title.TLabel").pack(pady=20)
    self.u = ttk.Entry(card, width=30)
    self.u.pack(pady=5)
    self.u.insert(0, "admin")
    self.p = ttk.Entry(card, width=30, show="*")
    self.p.pack(pady=5)
    self.p.insert(0, "admin")
    ttk.Button(card, text="Войти", style="Primary.TButton", command=self.login).pack(fill="x", pady=10)
```

### Метод `login`

```python
def login(self):
    r = self.db.login(self.u.get(), self.p.get())
    if not r:
        messagebox.showerror("Ошибка", "Неверные данные")
        return
    self.user = r
    self.dashboard()
```

### Экран каталога (dashboard)

* Верхняя панель с названием и пользователем.
* Таблица товаров: Treeview.
* Фильтр по категориям: Combobox.
* Кнопки действий в зависимости от роли пользователя.

### Методы работы с товарами и заказами

| Метод              | Назначение                                  |
| ------------------ | ------------------------------------------- |
| `load_products()`  | Загружает товары в таблицу                  |
| `buy()`            | Выбор товара, количество, добавление заказа |
| `add_product()`    | Диалог для ввода нового товара              |
| `delete_product()` | Удаление выбранного товара                  |
| `orders()`         | История заказов в отдельном окне            |

### Главный цикл приложения

```python
root = tk.Tk()
App(root)
root.mainloop()
```

* `tk.Tk()` — создаёт главное окно.
* `App(root)` — запускает приложение.
* `mainloop()` — вечный цикл окна.

---

## 4️⃣ Что нужно знать для создания такого приложения

**Tkinter**: Frame, Label, Entry, Button, Treeview, Combobox, `pack()`, `grid()`, `place()`, `mainloop()`
**SQLite**: CREATE TABLE, INSERT, SELECT, UPDATE, DELETE, fetchone(), fetchall(), commit()
**Python**: классы и методы, self, списковые включения, работа с датой (`datetime.now()`)
**Логика**: логин → проверка базы → dashboard → кнопки → работа с базой → обновление таблицы
