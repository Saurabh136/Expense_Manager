# 💰 Expense Manager

A full-stack **Expense Management Web Application** built using **Streamlit (Frontend)** and **FastAPI (Backend)**.  
It helps you **track, update, and analyze** your daily spending with beautiful visualizations and real-time analytics.

---

## 🚀 Features

✅ **Add / Update Expenses** – Quickly log your daily spending by category and notes.  
✅ **Analytics Dashboard** – Interactive charts and category-wise summaries for any date range.  
✅ **Theme Support** – Seamless Light 🌞 and Dark 🌙 modes for a clean user experience.  
✅ **Summary Tables & Exports** – View detailed tables and download analytics as CSV or Excel.  
✅ **Fast & Lightweight** – Built using modern Python frameworks (Streamlit + FastAPI).  

---

## 🧠 Tech Stack

| Layer | Technology               |
|-------|--------------------------|
| **Frontend** | Streamlit                |
| **Backend** | FastAPI                  |
| **Database** | MySQL(configurable)      |
| **Visualization** | Plotly                   |
| **Styling** | Custom CSS (theme-aware) |
| **Export** | Pandas, XlsxWriter       |

---

## Project Structure

- **frontend/**: Contains the Streamlit application code.
- **backend/**: Contains the FastAPI backend server code.
- **tests/**: Contains the test cases for both frontend and backend.
- **requirements.txt**: Lists the required Python packages.
- **README.md**: Provides an overview and instructions for the project.

---

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/expense-management-system.git
   cd expense-management-system
   ```
1. **Install dependencies:**:   
   ```commandline
    pip install -r requirements.txt
   ```
1. **Run the FastAPI server:**:   
   ```commandline
    uvicorn server.server:app --reload
   ```
1. **Run the Streamlit app:**:   
   ```commandline
    streamlit run frontend/app.py
   ```