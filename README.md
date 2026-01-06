1️⃣ Библиотеки
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta


tkinter — стандартная библиотека для создания графических окон (GUI) в Python.

tk — сокращение для удобства.

С его помощью можно делать кнопки, поля ввода, таблицы, окна и т.д.

ttk — модуль в tkinter с красивыми виджетами: стильные кнопки, таблицы, комбобоксы.

messagebox — показывает окна с ошибкой или информацией.
Пример:

messagebox.showerror("Ошибка", "Неверные данные")


simpledialog — простые диалоги для ввода данных пользователем (строка, число).
Пример:

q = simpledialog.askinteger("Количество", "Введите число")


sqlite3 — встроенная база данных, чтобы хранить данные в файле .db.

Работает как маленькая версия SQL.

SQL-запросы такие же, как в больших базах: SELECT, INSERT, DELETE, UPDATE.

datetime — работа с датой и временем.

datetime.now() — текущее время.

timedelta(days=1) — сдвиг на 1 день.

2️⃣ Класс DB — работа с базой данных

Класс DB отвечает за всю работу с данными: пользователи, товары, заказы.

class DB:
    def __init__(self):
        self.conn = sqlite3.connect("app.db")     # создаём файл базы данных
        self.conn.row_factory = sqlite3.Row       # строки как словарь {название_столбца: значение}
        self.cur = self.conn.cursor()             # курсор для выполнения SQL-запросов
        self.setup()                              # создаём таблицы и начальные данные


Курсор — это как «ручка» для SQL. С его помощью выполняем запросы.

row_factory позволяет обращаться к столбцам через row["username"], а не по индексу.

Метод setup — создание таблиц
def setup(self):
    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS users (...))
    """)
    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS products (...))
    """)
    self.cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (...))
    """)
    self.conn.commit()


CREATE TABLE IF NOT EXISTS — создаёт таблицу, если её нет.

PRIMARY KEY AUTOINCREMENT — уникальный ID, который увеличивается автоматически.

INSERT OR IGNORE — добавляет начальные данные, но если уже есть — не добавляет.

Методы DB для работы с данными

login — проверка логина:

SELECT * FROM users WHERE username=? AND password=?


products — получает товары (все или по категории).

categories — возвращает список уникальных категорий товаров.

add_product / delete_product — добавление/удаление товаров.

add_order — добавляет заказ и уменьшает количество товара.

user_orders — история заказов конкретного пользователя.

revenue_today — сумма всех заказов за сегодня.

⚡ Важно знать: все изменения базы нужно сохранять через self.conn.commit().

3️⃣ Класс App — графический интерфейс

Класс App отвечает за окно, кнопки, таблицы и взаимодействие с пользователем.

class App:
    def __init__(self, root):
        self.root = root                        # главное окно
        self.root.title("Система заказов")      # заголовок окна
        self.root.geometry("1100x700")           # размер окна
        self.root.configure(bg="#f3f4f6")        # цвет фона


root — главное окно, которое создаётся в конце через tk.Tk().

Всё, что создаётся через tkinter, нужно помещать в окно (root или фреймы).

Стили интерфейса
def style(self):
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("TFrame", background="#f3f4f6")
    s.configure("Card.TFrame", background="white", padding=30)
    s.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), background="white")


ttk.Style() позволяет менять шрифт, фон, отступы для всех виджетов.

Можно создавать свои типы стилей, например Card.TFrame для карточек товаров.

Очистка окна
def clear(self):
    for w in self.root.winfo_children():
        w.destroy()


winfo_children() — возвращает все элементы внутри окна.

destroy() — удаляет их.

Это нужно, чтобы сменить экран, например с входа на каталог товаров.

Экран логина
def login_screen(self):
    self.clear()
    box = ttk.Frame(self.root)
    box.place(relx=0.5, rely=0.5, anchor="center")
    ...
    ttk.Button(card, text="Войти", command=self.login).pack()


Используем Frame как контейнер для виджетов.

place(relx, rely, anchor) — ставим блок в центр окна.

Entry — поле ввода текста. show="*" скрывает символы (для пароля).

Button — кнопка, command — метод, который вызывается при нажатии.

Метод login
def login(self):
    r = self.db.login(self.u.get(), self.p.get())
    if not r:
        messagebox.showerror("Ошибка", "Неверные данные")
        return
    self.user = r
    self.dashboard()


get() — берёт текст из поля ввода.

Если пользователь не найден — ошибка.

Если найден — показываем экран с товарами (dashboard).

Экран каталога (dashboard)
def dashboard(self):
    self.clear()
    head = ttk.Frame(self.root)
    head.pack(fill="x", padx=30, pady=20)


Создаём верхнюю панель, где будет название и имя пользователя.

pack(fill="x") растягивает панель по ширине окна.

padx/pady — отступы по горизонтали и вертикали.

Таблица товаров
self.tree = ttk.Treeview(self.root, columns=("услуга", "Цена", "Остаток", "Категория"), show="headings")


Treeview — таблица.

columns — названия колонок.

show="headings" — скрывает колонку с индексами.

for c in self.tree["columns"]:
    self.tree.heading(c, text=c)
    self.tree.column(c, anchor="center")


Настраиваем заголовки и выравнивание колонок.

Фильтр по категории
self.cat = ttk.Combobox(top, values=["Все"] + self.db.categories(), state="readonly")
self.cat.current(0)
self.cat.bind("<<ComboboxSelected>>", lambda e: self.load_products())


Combobox — выпадающий список.

state="readonly" — нельзя писать вручную, только выбрать.

bind("<<ComboboxSelected>>") — при выборе категории обновляем товары.

Кнопки для пользователя и админа

Пользователь (role="user"):

Оформить заказ → вызывает buy()

История заказов → вызывает orders()

Админ (role="admin"):

Добавить товар → вызывает add_product()

Удалить товар → вызывает delete_product()

Выход — вызывает logout()

Методы работы с товарами и заказами

load_products() — загружает товары в таблицу по выбранной категории.

buy() — выбираем товар, спрашиваем количество, добавляем заказ и уменьшаем остаток.

add_product() — диалог для ввода данных нового товара.

delete_product() — удаляем выбранный товар.

orders() — открывает новое окно с историей заказов пользователя.

Главный цикл приложения
root = tk.Tk()
App(root)
root.mainloop()


tk.Tk() — создаём главное окно.

App(root) — запускаем наше приложение.

mainloop() — вечный цикл окна, пока пользователь его не закроет.

4️⃣ Что нужно знать, чтобы писать такой код самому

Tkinter:

Frame, Label, Entry, Button, Treeview, Combobox

pack(), grid(), place() — разные способы размещения элементов

mainloop() — главный цикл окна

SQLite:

CREATE TABLE, INSERT, SELECT, UPDATE, DELETE

fetchone() — одна запись, fetchall() — все записи

commit() — сохраняет изменения

Python:

классы и методы

self — текущий объект

списковые включения: [r["category"] for r in ...]

работа с датой: datetime.now().strftime(...)

Логика приложения:

экран логина → проверка базы → открываем dashboard

dashboard показывает таблицу и кнопки

кнопки вызывают методы для работы с базой (покупка, добавление, удаление)

данные всегда берутся из базы и после изменений таблица обновляется
