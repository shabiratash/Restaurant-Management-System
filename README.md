<div align="center">

# 🍽️ Restaurant Management System

### A premium, fully-responsive restaurant point-of-sale & management suite for the desktop

*Take orders, watch your floor in real time, manage your menu & stock, and read your sales — all from one beautiful screen.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt5/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-555?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)]()

<br/>

**[✨ Features](#-features) · [🚀 Quick Start](#-quick-start) · [🔑 Login](#-login) · [📖 Guide](#-using-the-app) · [🏗️ Architecture](#️-architecture) · [🧩 Tech](#-tech-stack) · [❓ FAQ](#-faq)**

</div>

---

## 💡 Overview

This **Restaurant Management System** behaves like the commercial software you'd see at
the counter of a modern restaurant (think Toast, Square, or Lightspeed). It runs entirely
on your computer — no internet, no cloud account, no setup beyond a single `pip install`.

> 🎯 **Three steps to running:** [Install](#-quick-start) → [Log in](#-login) → [Take your first order](#-using-the-app)

<table>
<tr>
<td>⚡ <b>Real-time floor view</b></td>
<td>🧾 <b>Live order feed</b></td>
<td>📊 <b>Sales analytics</b></td>
</tr>
<tr>
<td>🍔 <b>Menu & categories</b></td>
<td>📦 <b>Inventory tracking</b></td>
<td>👥 <b>Customer directory</b></td>
</tr>
</table>

---

## ✨ Features

Every item below is its own page, reached from the **sidebar** on the left.

| Page | What it does |
|------|--------------|
| 📊 **Dashboard** | Today's key numbers, a **live map of your tables**, the newest orders, and trend charts. |
| 🧾 **Orders** | Build orders in a cart (table + customer + items), then advance them: `Pending → Preparing → Ready → Served`. |
| 🍔 **Menu** | Add / edit / remove food, set prices, group by category, toggle availability. |
| 👥 **Customers** | A searchable address book of your guests. |
| 📦 **Inventory** | Track stock; items at/below their reorder level are flagged **Low stock** in red. |
| 📈 **Reports** | 30-day summary, revenue by category, daily table, and one-click **CSV export**. |
| ⚙️ **Settings** | Account info, add/remove tables on the floor plan, app details. |

<details>
<summary><b>🎨 What makes it feel premium</b> (click to expand)</summary>

<br/>

- **Responsive layout** — readable from a small laptop (`1280×720`) up to a large monitor (`2560×1440`); cards re-flow and side-by-side panels stack when space is tight.
- **Clean light theme** — one consistent, professional color system.
- **Custom-drawn charts** — rendered with `QPainter`, so there are **zero charting dependencies**, and they stay crisp at any size.
- **Code-drawn vector icons** — no image assets to ship; they recolor to match the theme.
- **Polished UX** — drop shadows, hover states, status badges, and a split-screen login.

</details>

---

## 🚀 Quick Start

> **Requirement:** Python **3.10 or newer**.

```bash
# 1. (Recommended) create an isolated environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate      # macOS / Linux

# 2. install the only dependency
pip install -r requirements.txt

# 3. launch
python main.py
```

✅ On first launch, the app **creates and seeds its own database** (sample menu,
tables, customers, and orders) so the dashboard isn't empty. Nothing else to set up.

---

## 🔑 Login

Pick any built-in demo account on the login screen:

| 👤 Username | 🔒 Password | 🎭 Role | Intended for |
|------------|------------|---------|--------------|
| `admin`    | `admin123`   | **Admin**   | Owners / administrators (full access) |
| `manager`  | `manager123` | **Manager** | Floor managers |
| `cashier`  | `cashier123` | **Cashier** | Front-of-house staff |

> 💡 Click **Show** to reveal the password, or just press **Enter** to sign in.
> Passwords are stored hashed with **PBKDF2-HMAC-SHA256** — never as plain text.

---

## 📖 Using the app

<details open>
<summary><b>🧾 Take a new order</b></summary>

1. Open **Orders** → click **➕ New Order**.
2. Choose a **Table** (or *Takeaway*) and a **Customer** (or *Walk-in*).
3. Pick a food item, set the quantity, click **Add** — totals (subtotal, tax, total) update live.
4. Click **Place Order**. It appears as `Pending`, and the table is auto-marked **Occupied**.

</details>

<details>
<summary><b>👨‍🍳 Move an order through the kitchen</b></summary>

Use the status dropdown on each order row to advance it. Marking an order **Served**
or **Cancelled** automatically frees the table again.

</details>

<details>
<summary><b>🗺️ Read the restaurant floor</b></summary>

Each tile is a table. The colored stripe shows its state — 🟢 **Available**,
🟡 **Reserved**, 🔴 **Occupied**. Click a tile to cycle its status.

</details>

<details>
<summary><b>🍔 Manage the menu &nbsp;·&nbsp; 📈 Export a report</b></summary>

- **Menu:** click **➕ Add Item**, set name/category/price/availability; use **Edit**/**Delete** anytime.
- **Reports:** click **Export CSV** — a spreadsheet is saved to `exports/` and the app shows the path.

</details>

---

## 🏗️ Architecture

The project follows a clean **MVC + services** structure: screens (UI) are fully separated
from business logic and from the database.

```
restaurant-management-system/
├─ main.py            🚀 Entry point — boots the app and opens the window
├─ requirements.txt   📦 Dependencies (just PyQt5)
│
├─ app/               ⚙️  App-wide setup
│   ├─ config.py          paths, tax rate, currency, statuses
│   └─ theme.py           design system: colors, fonts, global styling
│
├─ database/          🗄️  Storage layer
│   ├─ connection.py      safe SQLite access, transactions & errors
│   ├─ schema.py          tables + integrity rules (FKs, CHECKs)
│   └─ seed.py            demo data on first run
│
├─ models/            🧱 Plain data containers (User, Food, Order, Table…)
│
├─ services/          🧠 ALL business logic
│   ├─ auth_service.py        login / logout
│   ├─ order_service.py       orders, status, totals
│   ├─ food_service.py        menu CRUD
│   ├─ customer_service.py    customer CRUD
│   ├─ inventory_service.py   stock CRUD + low-stock checks
│   ├─ table_service.py       floor / table management
│   ├─ dashboard_service.py   KPI + chart calculations
│   └─ report_service.py      reports + CSV export
│
├─ views/             🖼️  User interface (no business logic)
│   ├─ login / dashboard / orders / menu / customers / inventory / reports / settings
│   ├─ main_window.py         shell: sidebar + page switching
│   └─ components/            sidebar, KPI cards, charts, floor tiles, dialogs, icons
│
├─ utils/             🔧 Logging, validation, errors, formatting
└─ tests/             🧪 Headless smoke test covering every screen
```

> **Why it matters:** change *how it looks* in `views/`; change *the rules* (e.g. tax,
> totals) in `app/config.py` or `services/` — without ever touching the UI.

---

## 🗂️ Where your data lives

Created automatically on first run:

| Path | Contents |
|------|----------|
| `data/restaurant.db` | The SQLite database — menu, orders, customers, everything |
| `logs/` | Daily log files (activity + errors) |
| `exports/` | CSV reports from the Reports page |
| `backups/` | Reserved for database backups |

> 🔄 **Want a clean slate?** Close the app and delete `data/restaurant.db` — the next launch rebuilds fresh demo data.

---

## 🧩 Tech Stack

| Area | Details |
|------|---------|
| **Language / UI** | Python 3.10+, PyQt5 |
| **Database** | SQLite with foreign keys, CHECK constraints, and transactions for integrity |
| **Charts** | Hand-drawn with `QPainter` — no charting libraries, fully resize-aware |
| **Icons** | Vector line-icons drawn in code, theme-recolorable |
| **Security** | PBKDF2-HMAC-SHA256 password hashing |
| **Resilience** | Friendly error messages; unexpected errors logged to `logs/` |

### 🧪 Run the test

```bash
python tests/test_smoke.py     # prints "SMOKE OK" and exits 0
# or:  pytest -q
```

The smoke test boots the app, opens every page, creates an order, and resizes the
window across common resolutions.

---

## 🩺 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'PyQt5'` | Run `pip install -r requirements.txt` (activate your venv first). |
| `python` is not recognised | Install Python 3.10+ and add it to PATH; some systems use `py main.py`. |
| Window feels too small/large | Just resize it — the layout adapts (minimum `1024×680`). |
| Want the demo data back | Delete `data/restaurant.db` and restart. |
| Something failed quietly | Check the newest file in `logs/`. |

---

## ❓ FAQ

> **Do I need internet?** &nbsp;No — everything runs locally.
>
> **Where is my data?** &nbsp;In one file: `data/restaurant.db`.
>
> **Change tax rate or currency?** &nbsp;Edit `TAX_RATE` / `CURRENCY_SYMBOL` in `app/config.py`.
>
> **Add my own tables / menu items?** &nbsp;Yes — via **Settings** (tables) and **Menu** (food). No coding needed.
>
> **Is there a dark theme?** &nbsp;No — the app intentionally ships a single, polished light theme.

---

<div align="center">

Made with ❤️ using **Python** & **PyQt5**

⭐ If you find this project useful, consider giving it a star!

</div>
