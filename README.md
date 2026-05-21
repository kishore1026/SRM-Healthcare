# 🏥 SRM Health Care – Healthcare Management System

A secure, responsive, doctor-centric healthcare management web application built with **Flask + MySQL + XAMPP**.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-XAMPP-orange?logo=mysql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)

---

## 📋 Features

- **🔐 Doctor Authentication** – Secure login with password hashing and session management
- **👥 Patient Management** – Full CRUD with designation-specific fields (Student/Staff)
- **🔍 Advanced Search** – Multi-filter search by name, disease, roll number, hostel, date range
- **📊 Dashboard Analytics** – Real-time charts (pie, bar, line) with disease trends and visit stats
- **💊 Medicine Inventory** – Stock tracking, batch management, and drug categorization
- **📝 Prescription System** – Dynamic prescription creation with auto stock deduction
- **⚠️ Alert System** – Low stock, expiring, and expired medicine alerts with color coding
- **📥 Excel Export** – Download patients, visits, medicines, expiry reports as Excel files
- **📋 Audit Logs** – Complete activity tracking for all system actions
- **🔄 Auto Stock Deduction** – Medicines auto-deducted when prescriptions are created

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.11+ / Flask 3.1 |
| **Database** | MySQL via XAMPP |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Charts** | Chart.js 4.4 |
| **Icons** | Bootstrap Icons |
| **Typography** | Google Fonts (Inter) |
| **Excel Export** | pandas + openpyxl |
| **Scheduler** | APScheduler |

---

## 📁 Project Structure

```
srm_healthcare/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Flask extensions
│   ├── models/              # SQLAlchemy models (7 models)
│   ├── routes/              # Flask blueprints (8 blueprints)
│   ├── services/            # Business logic layer
│   ├── forms/               # WTForms form classes
│   ├── utils/               # Helpers & decorators
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, JS, images
├── database/
│   └── srm_healthcare.sql   # Full database schema + sample data
├── requirements.txt
├── .env                     # Environment configuration
├── run.py                   # Application entry point
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.11+** installed
- **XAMPP** installed with MySQL

### Step 1: Start XAMPP

1. Open XAMPP Control Panel
2. Click **Start** next to **Apache** (optional, for phpMyAdmin)
3. Click **Start** next to **MySQL** ← **Required!**

### Step 2: Create the Database

**Option A** – Via phpMyAdmin:
1. Open http://localhost/phpmyadmin
2. Click "New" → Name: `srm_healthcare` → Create
3. Import `database/srm_healthcare.sql`

**Option B** – Via MySQL CLI:
```bash
mysql -u root < database/srm_healthcare.sql
```

**Option C** – Automatic:
The app will automatically create the database and tables on first run.

### Step 3: Install Python Dependencies

```bash
cd srm_healthcare
pip install -r requirements.txt
```

### Step 4: Configure Environment

Edit `.env` file if needed:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=         # Your MySQL password (empty for XAMPP default)
DB_NAME=srm_healthcare
```

### Step 5: Run the Application

```bash
python run.py
```

The app will start at: **http://localhost:5000**

---

## 🔑 Default Login Credentials

|

> ⚠️ **Change the default password after first login in production!**

---

## 📖 Usage Guide

### Dashboard
- View summary cards: total patients, visits, top diseases, medicine stock
- Filter by time period: Today / This Week / This Month / Overall
- Interactive charts showing disease distribution and visit trends
- Alert badges for low stock and expiring medicines

### Patient Management
1. Navigate to **Patients** → **Add Patient**
2. Fill in patient details (fields change based on Student/Staff designation)
3. View patient profile to see complete visit history

### Recording a Visit
1. Go to a patient's profile → **Add Visit**
2. Enter complaint, diagnosis, and treatment
3. Create a prescription if medicines need to be issued

### Prescriptions
1. From a visit page, click **Create Prescription**
2. Add medicine rows dynamically (select medicine, dosage, frequency, quantity)
3. System validates stock availability and blocks expired medicines
4. Stock is auto-deducted on successful prescription creation

### Medicine Inventory
- View all medicines with stock status (Safe / Low Stock / Out of Stock)
- Add new medicines or update stock for existing ones
- Check **Alerts** page for low stock and expiry warnings

### Search Patients
- Use **Advanced Search** with multiple filters
- Combine Name + Disease + Date Range for precise results
- Export search results to Excel

### Export Data
- Navigate to **Export Data** page
- Download Excel reports for patients, visits, medicines, or audit logs

---

## 🔒 Security Features

- ✅ Password hashing (PBKDF2-SHA256)
- ✅ CSRF protection (Flask-WTF)
- ✅ XSS prevention (Jinja2 auto-escaping)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Secure session management (server-side, HttpOnly cookies)
- ✅ Auto-logout after 30 minutes of inactivity
- ✅ Input validation (WTForms validators)
- ✅ Audit trail for all critical actions

---

## 🗄️ Database Schema

| Table | Description |
|-------|-------------|
| `doctors` | Doctor authentication & profiles |
| `patients` | Patient demographics & medical history |
| `patient_visits` | Visit records with diagnosis & treatment |
| `prescriptions` | Prescription headers linked to visits |
| `prescription_items` | Individual medicine items in prescriptions |
| `medicines` | Medicine inventory with stock tracking |
| `medicine_stock_logs` | Stock change audit trail |
| `audit_logs` | System-wide activity logging |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `Access denied for user 'root'@'localhost'` | Check MySQL password in `.env` file |
| `Can't connect to MySQL server` | Start MySQL in XAMPP Control Panel |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Database doesn't exist` | The app auto-creates it, or import `database/srm_healthcare.sql` manually |
| Session expired too quickly | Adjust `SESSION_TIMEOUT_MINUTES` in `.env` |
| Charts not loading | Check browser console for JavaScript errors |

---

## 📝 License

This project is developed for SRM Healthcare clinic operations.

---

## 🙏 Credits

- **Flask** – Web framework
- **Bootstrap 5** – UI framework
- **Chart.js** – Data visualization
- **Bootstrap Icons** – Icon library
- **Google Fonts (Inter)** – Typography
