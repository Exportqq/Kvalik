# Система заказов на Python с Tkinter и SQLite

Приложение демонстрирует работу с базой данных и графическим интерфейсом для пользователей и администраторов.

---

## 1️⃣ Библиотеки

```python
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
tkinter — стандартная библиотека для создания графических окон (GUI) в Python.

tk — сокращение для удобства.

С помощью tkinter можно создавать кнопки, поля ввода, таблицы, окна.

ttk — модуль с красивыми виджетами: стильные кнопки, таблицы, комбобоксы.

messagebox — показывает окна с ошибкой или информацией.

python
Копировать код
messagebox.showerror("Ошибка", "Неверные данные")
simpledialog — простые диалоги для ввода данных пользователем (строка, число).

python
Копировать код
q = simpledialog.askinteger("Количество", "Введите число")
sqlite3 — встроенная база данных для хранения данных в файле .db.

SQL-запросы: SELECT, INSERT, DELETE, UPDATE.

datetime — работа с датой и временем.

python
Копировать код
datetime.now()         # текущее время
timedelta(days=1)      # сдвиг на 1 день
2️⃣ Класс DB — работа с базой данных
Отвечает за всю работу с данными: пользователи, товары, заказы.

python
Копировать код
class DB:
    def __init__(self):
        self.conn = sqlite3.connect("app.db")     # создаём файл базы данных
        self.conn.row_factory = sqlite3.Row       # строки как словарь
        self.cur = self.conn.cursor()             # курсор для выполнения SQL-запросов
        self.setup()                              # создаём таблицы и начальные данные
Курсор — «ручка» для SQL-запросов.

row_factory позволяет обращаться к столбцам по имени: row["username"].

Метод setup — создание таблиц
python
Копировать код
def setup(self):
    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")
    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS products (...)
    """)
    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (...)
    """)
    self.conn.commit()
CREATE TABLE IF NOT EXISTS — создаёт таблицу, если её нет.

PRIMARY KEY AUTOINCREMENT — уникальный ID, который увеличивается автоматически.

INSERT OR IGNORE — добавляет данные, если их ещё нет.

Методы работы с данными
Метод	Назначение
login(u, p)	Проверка логина пользователя
products(category=None)	Получение товаров (все или по категории)
categories()	Список уникальных категорий товаров
add_product(name, price, stock, cat)	Добавление нового товара
delete_product(name)	Удаление товара
add_order(u, name, qty, total)	Добавление заказа и уменьшение количества товара
user_orders(u)	История заказов пользователя
revenue_today()	Выручка за сегодня

⚡ Все изменения нужно сохранять через self.conn.commit().

3️⃣ Класс App — графический интерфейс
Отвечает за окно, кнопки, таблицы и взаимодействие с пользователем.

python
Копировать код
class App:
    def __init__(self, root):
        self.root = root                        # главное окно
        self.root.title("Система заказов")      # заголовок
        self.root.geometry("1100x700")          # размер окна
        self.root.configure(bg="#f3f4f6")       # цвет фона
Всё, что создаётся через tkinter, нужно помещать в окно (root) или Frame.

Стили интерфейса
python
Копировать код
def style(self):
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("TFrame", background="#f3f4f6")
    s.configure("Card.TFrame", background="white", padding=30)
    s.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), background="white")
ttk.Style() — меняет шрифт, фон и отступы для всех виджетов.

Можно создавать свои стили, например Card.TFrame.

Очистка окна
python
Копировать код
def clear(self):
    for w in self.root.winfo_children():
        w.destroy()
winfo_children() — возвращает все элементы окна.

destroy() — удаляет элемент.

Используется для смены экранов (логин → каталог).

Экран логина
python
Копировать код
def login_screen(self):
    self.clear()
    box = ttk.Frame(self.root)
    box.place(relx=0.5, rely=0.5, anchor="center")
Frame — контейнер для виджетов.

place(relx=0.5, rely=0.5, anchor="center") — центрирование окна.

Entry — поле ввода текста.

Button — кнопка с command для вызова функции.

Метод login
python
Копировать код
def login(self):
    r = self.db.login(self.u.get(), self.p.get())
    if not r:
        messagebox.showerror("Ошибка", "Неверные данные")
        return
    self.user = r
    self.dashboard()
get() — берёт текст из поля ввода.

Если пользователь найден → показываем dashboard.

Экран каталога (dashboard)
python
Копировать код
def dashboard(self):
    self.clear()
    head = ttk.Frame(self.root)
    head.pack(fill="x", padx=30, pady=20)
Создаём верхнюю панель с названием и пользователем.

pack(fill="x") растягивает панель по ширине.

padx/pady — отступы.

Таблица товаров
python
Копировать код
self.tree = ttk.Treeview(
    self.root,
    columns=("услуга", "Цена", "Остаток", "Категория"),
    show="headings"
)
Treeview — таблица.

columns — названия колонок.

show="headings" — скрывает колонку с индексами.

python
Копировать код
for c in self.tree["columns"]:
    self.tree.heading(c, text=c)
    self.tree.column(c, anchor="center")
Настройка заголовков и выравнивания.

Фильтр по категории
python
Копировать код
self.cat = ttk.Combobox(top, values=["Все"] + self.db.categories(), state="readonly")
self.cat.current(0)
self.cat.bind("<<ComboboxSelected>>", lambda e: self.load_products())
Combobox — выпадающий список.

state="readonly" — нельзя писать вручную, только выбрать.

bind("<<ComboboxSelected>>") — обновление таблицы при выборе категории.

Кнопки для пользователей и админа
Пользователь:

"Оформить заказ" → buy()

"История заказов" → orders()

Админ:

"Добавить товар" → add_product()

"Удалить товар" → delete_product()

"Выход" → logout()

Методы работы с товарами и заказами
Метод	Назначение
load_products()	Загружает товары в таблицу
buy()	Выбор товара, количество, добавление заказа
add_product()	Диалог для ввода нового товара
delete_product()	Удаление выбранного товара
orders()	История заказов в отдельном окне

Главный цикл приложения
python
Копировать код
root = tk.Tk()
App(root)
root.mainloop()
tk.Tk() — создаёт главное окно.

App(root) — запускает приложение.

mainloop() — вечный цикл окна, пока пользователь его не закроет.

4️⃣ Что нужно знать для создания такого приложения
Tkinter
Frame, Label, Entry, Button, Treeview, Combobox

pack(), grid(), place() — размещение элементов

mainloop() — главный цикл окна

SQLite
CREATE TABLE, INSERT, SELECT, UPDATE, DELETE

fetchone() — одна запись, fetchall() — все записи

commit() — сохраняет изменения

Python
Классы и методы

self — текущий объект

Списковые включения: [r["category"] for r in ...]

Работа с датой: datetime.now().strftime(...)
