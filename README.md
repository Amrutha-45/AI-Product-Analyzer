# AI Product Analyzer

![Project Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

A web application that takes the guesswork out of grocery shopping. Take a photo of any food product's packaging and ingredient label, and get an instant, easy-to-understand breakdown of what's actually inside it.

🔗 **[Live Demo on Vercel](https://ai-product-analyzer-five.vercel.app/)**

## Why I Built This

Food labels are incredibly confusing. When you're standing in a grocery aisle, you don't have time to Google every single E-number, additive, or hidden sugar variation. I wanted to build a tool that acts like a personal nutritionist in your pocket—something that can instantly scan a label, flag hidden allergens, calculate a genuine health score, and suggest cleaner alternatives.

## Features

- **Dual-Image Scanning**: Upload the front branding and the back nutritional label to catch deceptive marketing claims.
- **Deep Ingredient Breakdown**: Identifies harmful additives, hidden sugars, and specific health risks in plain English.
- **Nova Classification & Health Scoring**: Automatically scores the product from 0-100 and classifies its level of processing.
- **Smart Alternatives**: Suggests healthier, less-processed substitutes for junk food.
- **History Tracking**: Keeps a persistent log of everything you've scanned (powered by Supabase).

## Tech Stack

**Frontend**
- React + Vite
- TypeScript
- Tailwind CSS
- Framer Motion (for micro-animations and transitions)

**Backend**
- Python 3.10+
- FastAPI (Async REST API)
- Pydantic (Strict schema validation for AI outputs)

**Infrastructure & AI**
- **AI Vision**: OpenRouter (using Gemini 2.5 Flash / Llama Vision models)
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Vercel (Frontend), Render (Backend)

---

## Local Development Setup

If you want to run this project locally, follow the steps below.

### 1. Clone the repository
```bash
git clone https://github.com/Amrutha-45/AI-Product-Analyzer.git
cd AI-Product-Analyzer
```

### 2. Backend Setup
Navigate to the backend directory and set up your Python environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory with your API keys:
```env
# AI Configuration
AI_PROVIDER=openrouter
AI_MODEL=google/gemini-2.5-flash
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Supabase (Optional for local testing if you skip auth/history)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Frontend URL for CORS
FRONTEND_ORIGIN=http://localhost:5173
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```
The backend will be running at `http://localhost:8000`.

### 3. Frontend Setup
Open a new terminal window, navigate to the frontend directory, and install dependencies:

```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend` directory:
```env
VITE_API_URL=http://localhost:8000
```

Start the Vite development server:
```bash
npm run dev
```
The frontend will be running at `http://localhost:5173`.

## Contributing
Feel free to open issues or submit pull requests if you want to improve the prompt engineering, add new scanning features, or improve the UI!
