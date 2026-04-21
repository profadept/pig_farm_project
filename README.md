# 🚜 FarmOS: Livestock & Agricultural ERP

## Overview
FarmOS is an ongoing full-stack Enterprise Resource Planning (ERP) web application designed to transition manual pig farming operations into a secure, data-driven ecosystem. 

The primary objective of this project is to track comprehensive farm data—ranging from financial transactions to livestock lifecycles and supply inventories to eventually power predictive data analysis. By tracking historical data, the system will forecast feed consumption rates, predict medication requirements, and optimize the overall Feed Conversion Ratio (FCR) to ensure a highly profitable and scalable business model.

## 🛠️ Core Technology Stack
* **Backend:** Python, FastAPI
* **Database:** PostgreSQL, SQLModel (ORM)
* **Frontend:** Jinja2 Templates, HTML5, Bootstrap 5
* **Security:** Cryptographic Password Hashing, Role-Based Access Control (RBAC), Session Cookies, Global Exception Handling

## 🚀 Current Architecture & Features
* **Phase 1: Security & User Management:** Secure registration, authentication, and strict route protection differentiating `ADMIN` and `STAFF` access levels.
* **Phase 2: Financial Ledger:** A robust, immutable record of all farm expenses and profits, complete with filtering and CRUD operations.
* **Phase 3: Inventory & Livestock Vaults (In Development):** A triple-vault relational database schema tracking bulk supplies (feed/medicine), livestock batches and individuals (Sows/Boars), and an immutable audit log of all physical movements on the farm.

## 📈 Future Roadmap (Data & Analytics)
* Implementation of the Inventory and Livestock User Interfaces.
* Automated tracking of animal life stages (Piglet → Weaner → Grower).
* Statistical analysis modules to predict monthly feed costs based on current batch weights and historical consumption.
