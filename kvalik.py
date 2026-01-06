import tkinter as tk                      # импортируем tkinter как tk для создания окон и виджетов
from tkinter import ttk, messagebox, simpledialog  # ttk — стильные виджеты, messagebox — окна с ошибкой, simpledialog — простые диалоги
import sqlite3                           # встроенная база данных SQLite
from datetime import datetime, timedelta # работа с датой и временем, timedelta — для вычислений с датой


class DB:                                  # создаём класс базы данных (кладовая)
    def __init__(self):                    # метод инициализации — вызывается при создании объекта
        self.conn = sqlite3.connect("app.db")     # создаём или открываем файл базы данных app.db
        self.conn.row_factory = sqlite3.Row       # чтобы строки возвращались как словари с именами колонок
        self.cur = self.conn.cursor()             # создаём курсор для выполнения SQL-запросов
        self.setup()                              # вызываем метод setup для создания таблиц и начальных данных

    def setup(self):                             
        self.cur.execute("""                      # создаём таблицу пользователей, если её нет
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, # уникальный ID, увеличивается автоматически
            username TEXT UNIQUE,                 # логин пользователя, уникальный
            password TEXT,                         # пароль пользователя
            role TEXT                              # роль: admin или user
        )""")

        self.cur.execute("""                      # создаём таблицу товаров
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, # уникальный ID товара
            name TEXT,                             # название товара
            price REAL,                            # цена товара
            stock INTEGER,                          # количество на складе
            category TEXT                           # категория товара (например, "цветы")
        )""")

        self.cur.execute("""                      # создаём таблицу заказов
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, # уникальный ID заказа
            username TEXT,                        # кто купил
            product TEXT,                         # название товара
            qty INTEGER,                           # количество
            total REAL,                            # общая сумма
            created_at TEXT                         # дата и время покупки
        )""")

        self.cur.execute(                         # создаём пользователя admin, если его нет
            "INSERT OR IGNORE INTO users VALUES(NULL,'admin','admin','admin')"
        )
        self.cur.execute(                         # создаём обычного пользователя user, если его нет
            "INSERT OR IGNORE INTO users VALUES(NULL,'user','user','user')"
        )

        self.cur.execute(                         # создаём товар "цветы" если его нет
            "INSERT OR IGNORE INTO products VALUES(NULL,'цветы',350,10,'цветы')"
        )
        self.cur.execute(                         # создаём товар "аксессуар" если его нет
            "INSERT OR IGNORE INTO products VALUES(NULL,'аксессуар',150,25,'аксессуар')"
        )
        self.cur.execute(                         # создаём товар "упаковка" если его нет
            "INSERT OR IGNORE INTO products VALUES(NULL,'упаковка',120,40,'упаковка')"
        )

        self.conn.commit()                        # сохраняем все изменения в базе

    def login(self, u, p):                        # метод для проверки логина и пароля
        return self.cur.execute(                  # выполняем SQL-запрос
            "SELECT * FROM users WHERE username=? AND password=?", # ищем пользователя с этим логином и паролем
            (u, p)                                # параметры запроса
        ).fetchone()                              # возвращаем первую найденную запись или None

    def products(self, category=None):            # метод получения товаров, можно фильтровать по категории
        if category and category != "Все":        # если выбрана категория, кроме "Все"
            return self.cur.execute(              # возвращаем только товары этой категории
                "SELECT * FROM products WHERE category=?",
                (category,)
            ).fetchall()
        return self.cur.execute(                  # иначе возвращаем все товары
            "SELECT * FROM products"
        ).fetchall()

    def categories(self):                         # метод получения всех уникальных категорий товаров
        return [r["category"] for r in self.cur.execute(
            "SELECT DISTINCT category FROM products"  # выбираем только уникальные категории
        ).fetchall()]

    def add_product(self, name, price, stock, cat):  # метод добавления нового товара
        self.cur.execute(
            "INSERT INTO products VALUES(NULL,?,?,?,?)",
            (name, price, stock, cat)
        )
        self.conn.commit()                        # сохраняем изменения

    def delete_product(self, name):                # метод удаления товара по имени
        self.cur.execute(
            "DELETE FROM products WHERE name=?",
            (name,)
        )
        self.conn.commit()                        # сохраняем изменения

    def add_order(self, u, name, qty, total):      # метод добавления заказа
        self.cur.execute(
            "INSERT INTO orders VALUES(NULL,?,?,?,?,?)",
            (u, name, qty, total,
             datetime.now().strftime('%Y-%m-%d %H:%M')) # текущая дата и время
        )
        self.cur.execute(                         # уменьшаем количество товара на складе
            "UPDATE products SET stock = stock - ? WHERE name=?",
            (qty, name)
        )
        self.conn.commit()                        # сохраняем изменения

    def user_orders(self, u):                       # метод получения всех заказов пользователя
        return self.cur.execute(
            "SELECT * FROM orders WHERE username=?",
            (u,)
        ).fetchall()

    def revenue_today(self):                        # метод подсчёта выручки за сегодня
        r = self.cur.execute(
            "SELECT SUM(total) s FROM orders WHERE DATE(created_at)=DATE('now')" # суммируем total по сегодняшним заказам
        ).fetchone()
        return r["s"] or 0                        # если нет заказов, возвращаем 0


class App:                                         # класс приложения (окна, кнопки и т.д.)
    def __init__(self, root):                     # инициализация приложения
        self.root = root
        self.root.title("Система заказов")       # заголовок окна
        self.root.geometry("1100x700")            # размер окна
        self.root.configure(bg="#f3f4f6")         # цвет фона

        self.db = DB()                             # создаём объект базы данных
        self.user = None                           # текущий пользователь (пока нет)

        self.style()                               # применяем стили интерфейса
        self.login_screen()                        # показываем экран логина

    def style(self):                               # метод для настройки стилей
        s = ttk.Style()
        s.theme_use("clam")                        # выбираем тему оформления
        s.configure("TFrame", background="#f3f4f6")   # фон обычных фреймов
        s.configure("Card.TFrame", background="white", padding=30)  # стиль карточек
        s.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), background="white") # заголовок
        s.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#f3f4f6") # шапка
        s.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), padding=10)   # стиль кнопки
        s.configure("Treeview", rowheight=32, font=("Segoe UI", 11)) # таблица
        s.configure("Treeview.Heading", font=("Segoe UI", 11, "bold")) # заголовки таблицы

    def clear(self):                               # метод очистки экрана
        for w in self.root.winfo_children():       # проходимся по всем виджетам окна
            w.destroy()                            # удаляем каждый виджет

    def login_screen(self):                        # метод для экрана логина
        self.clear()                               # очищаем старые виджеты

        box = ttk.Frame(self.root)                 # создаём контейнер для центра
        box.place(relx=0.5, rely=0.5, anchor="center") # центрируем в окне

        card = ttk.Frame(box, style="Card.TFrame") # карточка с белым фоном
        card.pack()

        ttk.Label(card, text="Вход", style="Title.TLabel").pack(pady=20) # заголовок "Вход"

        self.u = ttk.Entry(card, width=30)         # поле ввода логина
        self.u.pack(pady=5)
        self.u.insert(0, "admin")                  # значение по умолчанию

        self.p = ttk.Entry(card, width=30, show="*")  # поле ввода пароля
        self.p.pack(pady=5)
        self.p.insert(0, "admin")                  # значение по умолчанию

        ttk.Button(
            card,
            text="Войти",                           # текст кнопки
            style="Primary.TButton",                # стиль кнопки
            command=self.login                       # вызываем метод login при нажатии
        ).pack(fill="x", pady=10)

    def login(self):                               # метод проверки логина
        r = self.db.login(self.u.get(), self.p.get()) # получаем данные пользователя
        if not r:                                   # если не найден
            messagebox.showerror("Ошибка", "Неверные данные") # показываем ошибку
            return
        self.user = r                               # сохраняем пользователя
        self.dashboard()                            # переходим в каталог товаров

    def logout(self):                               # метод выхода
        if messagebox.askyesno("Выход", "Выйти из аккаунта?"):  # спрашиваем подтверждение
            self.user = None
            self.login_screen()                     # возвращаемся к экрану логина

    def dashboard(self):                            # метод для главного экрана
        self.clear()                                # очищаем окно

        head = ttk.Frame(self.root)                 # верхняя панель
        head.pack(fill="x", padx=30, pady=20)

        ttk.Label(head, text="Каталог товаров", style="Header.TLabel").pack(side="left") # название слева

        ttk.Label(head, text=f"{self.user['username']} ({self.user['role']})", style="Header.TLabel").pack(side="right") # имя и роль справа

        if self.user["role"] == "admin":            # если админ
            card = ttk.Frame(self.root, style="Card.TFrame") # блок с белым фоном
            card.pack(padx=30, pady=10, anchor="w")

            ttk.Label(card, text="Выручка сегодня").pack()   # текст
            ttk.Label(card,
                      text=f"{self.db.revenue_today():.2f} ₽", # сумма выручки
                      font=("Segoe UI", 18, "bold"),
                      background="white").pack()

        top = ttk.Frame(self.root)                   # блок с фильтром категорий
        top.pack(fill="x", padx=30)

        self.cat = ttk.Combobox(
            top,
            values=["Все"] + self.db.categories(), # список категорий
            state="readonly"                       # нельзя писать самому
        )
        self.cat.current(0)                          # по умолчанию "Все"
        self.cat.pack(side="left")
        self.cat.bind("<<ComboboxSelected>>", lambda e: self.load_products()) # при смене категории загружаем товары

        self.tree = ttk.Treeview(
            self.root,
            columns=("услуга", "Цена", "Остаток", "Категория"), # колонки таблицы
            show="headings"
        )

        for c in self.tree["columns"]:
            self.tree.heading(c, text=c)            # заголовки колонок
            self.tree.column(c, anchor="center")    # выравнивание по центру

        self.tree.pack(fill="both", expand=True, padx=30, pady=10) # таблица на весь экран
        self.load_products()                        # загружаем товары

        actions = ttk.Frame(self.root)              # блок с кнопками
        actions.pack(fill="x", padx=30, pady=10)

        if self.user["role"] == "user":             # кнопки для пользователя
            ttk.Button(actions, text="Оформить заказ",
                       style="Primary.TButton",
                       command=self.buy).pack(side="left")

            ttk.Button(actions, text="История заказов",
                       command=self.orders).pack(side="left", padx=10)

        if self.user["role"] == "admin":            # кнопки для админа
            ttk.Button(actions, text="Добавить товар",
                       style="Primary.TButton",
                       command=self.add_product).pack(side="left")

            ttk.Button(actions, text="Удалить товар",
                       command=self.delete_product).pack(side="left", padx=10)

        ttk.Button(actions, text="Выход",
                   command=self.logout).pack(side="right") # кнопка выхода

    def load_products(self):                        # метод для загрузки товаров в таблицу
        self.tree.delete(*self.tree.get_children()) # очищаем таблицу
        for p in self.db.products(self.cat.get()): # проходим по товарам выбранной категории
            self.tree.insert("", "end",             # добавляем в таблицу
                             values=(p["name"], p["price"], p["stock"], p["category"]))

    def buy(self):                                  # метод покупки товара
        sel = self.tree.focus()                     # выбранная строка
        if not sel:
            return

        name, price, stock, _ = self.tree.item(sel)["values"] # получаем данные выбранного товара
        if stock <= 0:                              # если нет в наличии
            return

        q = simpledialog.askinteger(                # спрашиваем количество
            "Количество", name,
            minvalue=1, maxvalue=stock
        )
        if not q:
            return

        self.db.add_order(                           # добавляем заказ в базу
            self.user["username"], name, q,
            q * float(price)
        )
        self.load_products()                          # обновляем таблицу с остатком

    def add_product(self):                            # метод для добавления товара (только admin)
        n = simpledialog.askstring("услуга", "услуга")
        p = simpledialog.askfloat("Цена", "Цена")
        s = simpledialog.askinteger("Остаток", "Остаток")
        c = simpledialog.askstring("Категория", "Категория")

        if n and p and s and c:
            self.db.add_product(n, p, s, c)          # добавляем товар
            self.load_products()                      # обновляем таблицу

    def delete_product(self):                         # метод удаления товара (admin)
        sel = self.tree.focus()                        # выбранная строка
        if not sel:
            return
        name = self.tree.item(sel)["values"][0]       # имя товара
        self.db.delete_product(name)                  # удаляем из базы
        self.load_products()                          # обновляем таблицу

    def orders(self):                                 # метод отображения истории заказов
        w = tk.Toplevel(self.root)                    # новое окно
        w.title("История заказов")
        w.geometry("700x400")

        t = ttk.Treeview(
            w,
            columns=("Товар", "Кол-во", "Сумма", "Дата"),
            show="headings"
        )

        for c in t["columns"]:
            t.heading(c, text=c)
            t.column(c, anchor="center")

        t.pack(fill="both", expand=True)

        for o in self.db.user_orders(self.user["username"]):  # добавляем заказы пользователя
            t.insert("", "end",
                     values=(o["product"], o["qty"], o["total"], o["created_at"]))


root = tk.Tk()                                     # создаём главное окно
App(root)                                          # запускаем приложение
root.mainloop()                                    # запускаем цикл работы окна
