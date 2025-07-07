# 📦 GroupifyAssist – Smart Grouping and Selection Tool

**GroupifyAssist** is a smart system designed to help organizers (hosts) group or select individuals intelligently based on randomization or specified criteria (e.g. gender, skill level). This system reduces bias, improves fairness, and saves time during group management and participant selection tasks.

Built using **FastAPI**, **SQLModel**, and **PostgreSQL**, it prioritizes **performance**, **scalability**, and **flexibility** for a wide range of use cases.

---

## 🚀 Features

### ✅ Core Functionalities

* **Random Grouping**: Automatically split people into groups with custom size, naming, and reveal settings.
* **Preferential Grouping (Planned)**: Set quotas or rules like “Max 2 beginners per group”.
* **Random & Preferential Selection**: Randomly pick participants, or enforce conditions (e.g. "5 males and 5 females").
* **Host-Defined Fields**: Hosts can dynamically define custom fields (e.g. gender, department) to be filled by members.
* **Code-Based Access**: Session codes for participants (no registration required).
* **CSV & PDF Report Generation**: Download reports of all groupings or selections.

### 🔐 Authentication & Security

* Host account registration and login
* Email verification with short-lived OTP
* JWT-based protected routes
* Expiring access codes for sessions

### ⚙️ Technical Stack

* **FastAPI** – blazing-fast Python web framework
* **SQLModel** – combines SQLAlchemy ORM and Pydantic models
* **PostgreSQL** – robust relational DB with JSONB support
* **Async I/O** – high-performance route functions using `async def`
* **Alembic** – for schema migrations
* **Uvicorn** – lightning-fast ASGI server

---

## 🧠 Use Cases

* Classroom group assignments
* Hackathon or event team formation
* Interviewer or judge assignment
* Corporate or training breakout sessions
* Lottery or raffle-style selections with fairness criteria

---

## 🛠️ Project Structure

```
groupifyassist/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── core/                # Configuration and DB connection
│   ├── models/              # SQLModel-based database models
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic (grouping, selection)
│   ├── utils/               # Utility modules (e.g. code generation, hashing)
│   └── schemas/             # Optional Pydantic DTOs
├── alembic/                 # DB migrations
├── requirements.txt
└── README.md
```

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/omovigho/groupifyassist.git
cd groupifyassist
```

### 2. Create a Virtual Environment

```bash
pipenv shell
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload
```

---

## 📊 Planned Enhancements

* [ ] Preferential grouping (rules & quotas)
* [ ] Member feedback system
* [ ] Admin dashboard for hosts
* [ ] Slack/Zoom/Google Meet integrations
* [ ] Multi-language support
* [ ] Analytics dashboard
* [ ] RESTful API for embedding in third-party apps

---

## 🧑‍💻 Contributing

Pull requests are welcome! Please:

1. Fork the repo
2. Create a new branch: `git checkout -b feature/feature-name`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push and create a PR

---

## 📝 License

MIT License © 2025 \[omovigho]
