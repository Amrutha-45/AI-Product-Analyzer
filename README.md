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

