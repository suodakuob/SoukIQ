# 🏪 SoukIQ: Moroccan Retail-Fintech Business Analytics Platform
> **Executive Analytics & Decision-Support System (Simulating WafR Morocco)**  
> *Delivering Consulting-Grade BI, Advanced SQL Modeling, and Behavioral Merchant Segmentation to the C-Suite.*

---

## 📌 Executive Summary
SoukIQ (simulating the operations of Moroccan retail-fintech pioneer **WafR**) is an end-to-end business intelligence and analytics case study. The platform digitizes traditional neighborhood grocery stores (*Hanouts*) in Morocco, converting them into digital financial hubs (processing Mobile Recharges, Bill Payments, and Gaming Top-Ups). SoukIQ monetizes through a micro-commission take-rate model.

During H1 2026, the platform processed **12.96 Million MAD in Gross Merchandise Value (GMV)** across **240,554 transactions**, yielding **363.63K MAD in Net Commission Revenue** at a blended take-rate of **2.81%** across a network of **1,000 active Hanouts**.

This project bypasses over-engineered data engineering pipelines to focus purely on **business value, transactional economics, operational reliability, and C-Suite decision-making**. It answers one question: *"Would the CEO care about this?"*

---

## 🛠️ Project Architecture & Directory Structure
The repository is organized following clean, industry-standard analytics guidelines, separating raw source generation, database storage, advanced modeling, and reporting:

```text
SoukIQ/
│
├── data/
│   ├── raw/                 # Generated source CSV logs (CRM, POS, Marketing, Monitoring)
│   └── cleaned/             # Polished datasets post-Data Quality & Validation pipeline
│
├── sql/
│   ├── schema.sql           # PostgreSQL DDL with optimized relational indexes
│   └── analysis_queries.sql # Master SQL scripts answering the 12 Executive Questions
│
├── notebooks/
│   └── business_analysis.ipynb  # Advanced Python Modeling (RFM, Pareto, Cohort, Outage Churn)
│
├── dashboard/
│   └── SoukIQ.pbix          # 4-Page Clean & Professional Power BI Executive Dashboard
│
├── reports/
│   └── Executive_Report.pdf # Consulting-style PDF summary of strategic recommendations
│
├── src/
│   ├── generate_data.py     # Business-driven synthetic data engine (Poisson & Log-Normal)
│   ├── clean_data.py        # Data cleaning, text standardization & POS duplicate removal
│   └── load_database.py     # Fast-ingestion psycopg2 database migration script
│
└── README.md                # Portfolio landing page & case study presentation
