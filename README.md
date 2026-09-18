# E-Commerce NLP Customer Support System

A local NLP-based customer support prototype for an e-commerce workflow. Customers submit complaints through Streamlit, FastAPI sends the complaint through the prediction service, and SQLite stores the resulting support ticket.

The current prediction service is a temporary keyword-based dummy model. A teammate can replace it with a trained RNN, BiLSTM, or another NLP model without changing the customer UI, admin dashboard, API routes, or database contract, as long as the prediction contract is preserved.

## Features

- Customer complaint submission through a Streamlit UI
- FastAPI backend with automatic Swagger documentation
- Dataset-aligned prediction fields:
  - `Category` maps to `subsystem`
  - `Urgency` maps to `priority`
- SQLite ticket storage
- Admin dashboard with subsystem and priority filters
- Ticket sorting by date or priority
- Ticket status updates: `Pending` and `Resolved`
- Replaceable NLP model layer in `backend/model_service.py`

## Project Structure

```text
ecommerce-nlp-support/
├── backend/
│   ├── main.py                 # FastAPI application and routes
│   ├── database.py             # SQLite connection and ticket operations
│   ├── model_service.py        # Prediction contract and current dummy model
│   └── model/                  # Place trained model artifacts here
│       └── .gitkeep
├── frontend/
│   ├── User.py                 # Customer-facing Streamlit page
│   └── pages/
│       └── Admin.py            # Admin dashboard page
├── requirements.txt
├── .gitignore
└── README.md
```

## Technology Stack

| Technology | Purpose |
| --- | --- |
| Python | Application language |
| FastAPI | Backend REST API |
| Uvicorn | ASGI server for FastAPI |
| Streamlit | Customer UI and admin dashboard |
| Requests | Frontend-to-backend HTTP communication |
| SQLite | Local ticket database |
| Pandas | Admin dashboard filtering and table handling |

## Clone and Setup

These commands are for Windows PowerShell. Run them from the folder where you want to keep the project.

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks virtual environment activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

The repository does not include the virtual environment, Python cache files, or the local SQLite database. They are excluded by `.gitignore`.

## Run the Project

The backend and frontend must run in separate terminals. Activate the virtual environment in both terminals.

### Terminal 1: FastAPI backend

From the project root:

```powershell
uvicorn main:app --reload --app-dir backend
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

When the backend starts, SQLite automatically creates this local file if it does not exist:

```text
backend/tickets.db
```

### Terminal 2: Streamlit frontend

From the project root:

```powershell
streamlit run frontend/User.py
```

Open the local Streamlit URL shown in the terminal, normally:

```text
http://localhost:8501
```

The Admin page is available from the Streamlit sidebar as `Admin`.

## Application Flow

```text
Customer complaint
        |
        v
Streamlit User page
        |
        | POST /tickets
        v
FastAPI backend
        |
        v
backend/model_service.py
        |
        | subsystem + priority
        v
SQLite backend/tickets.db
        |
        v
Admin dashboard through FastAPI API
```

The Streamlit frontend never accesses SQLite directly. All frontend data access goes through FastAPI.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | Health check |
| POST | `/tickets` | Predict and create a ticket |
| GET | `/tickets` | Return all tickets, newest first |
| PATCH | `/tickets/{ticket_id}/status` | Update a ticket to `Pending` or `Resolved` |

Example request:

```json
{
  "query": "amar taka kete gese but order confirm hoy nai"
}
```

Example response shape:

```json
{
  "id": 1,
  "query": "amar taka kete gese but order confirm hoy nai",
  "subsystem": "Payment",
  "priority": "High",
  "status": "Pending",
  "created_at": "2026-09-18 01:20:00"
}
```

## Database

The project uses Python's built-in `sqlite3` library. The database table is `tickets` with these fields:

```text
id
query
subsystem
priority
status
created_at
```

Each teammate gets a separate local `backend/tickets.db` file. The database is intentionally ignored by Git, so ticket data is not pushed to GitHub or synchronized between computers. The backend creates the database and table automatically on startup.

## Current Prediction Contract

The only model interface used by the backend is:

```python
def predict(query: str) -> dict:
```

The current contract is:

```python
{
    "subsystem": "Payment",
    "priority": "High"
}
```

The dictionary must contain exactly these fields for the current API and database implementation. The current dummy model recognizes simple keywords for Payment, Delivery, and Product, then falls back to Technical Support.

The dataset fields map as follows:

```text
Dataset Category  -> subsystem
Dataset Urgency   -> priority
```

The project supports `Low`, `Medium`, `High`, and `Immediate` priority values. The model should return the same labels used by the training dataset.

## Integrating a Trained RNN or BiLSTM

The teammate should work on a separate branch:

```powershell
git checkout -b integrate-trained-model
```

Place model artifacts under:

```text
backend/model/
```

For example:

```text
backend/model/
├── model.pth
├── tokenizer.pkl
├── labels.json
└── config.json
```

If PyTorch is used, add the required direct dependency to `requirements.txt`, for example:

```text
torch
```

Then install it:

```powershell
pip install -r requirements.txt
```

Replace only the dummy prediction logic in `backend/model_service.py`. The function must continue to return:

```python
{
    "subsystem": predicted_subsystem,
    "priority": predicted_priority,
}
```

The tokenizer, vocabulary, padding length, label mapping, and model configuration used during training must be saved and reused during inference. The trained model should be loaded once when the backend starts, not once per customer request.

If the model later predicts additional fields, the teammate must update `database.py`, `main.py`, and the dashboard together. Extra dictionary keys are not automatically stored in SQLite or shown in the UI.

## Development Checks

After changing the project, run:

```powershell
python -m py_compile backend\model_service.py backend\database.py backend\main.py frontend\User.py frontend\pages\Admin.py
```

Then start both services and test:

1. Submit a complaint from the User page.
2. Confirm the ticket appears in the Admin page.
3. Filter by subsystem and priority.
4. Change the ticket status to `Resolved`.
5. Confirm the updated status appears after refresh.

## Git Workflow for the Team

Commit and push the initial project:

```powershell
git add .
git commit -m "Initial e-commerce NLP support system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

For model integration:

```powershell
git checkout -b integrate-trained-model
git add backend\model backend\model_service.py requirements.txt
git commit -m "Integrate trained NLP model"
git push -u origin integrate-trained-model
```

The teammate can then open a Pull Request for review. Do not commit `.venv/`, `__pycache__/`, or `backend/tickets.db`.

## Troubleshooting

### Backend import or command error

Confirm the command is run from the project root and uses:

```powershell
uvicorn main:app --reload --app-dir backend
```

### Frontend says backend is unavailable

Start the backend first and confirm that `http://127.0.0.1:8000/` opens successfully.

###  Port already in use

Stop the old process or run FastAPI on another port. If the port changes, update `API_URL` in `frontend/User.py` and `frontend/pages/Admin.py`.
