# Sync & Celebrate: Event Management System 🎈

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange)
![Bootstrap](https://img.shields.io/badge/Frontend-Bootstrap_4-purple)

## 📌 Project Overview
**Sync & Celebrate** is a comprehensive web-based Event Management System designed to streamline the entire event lifecycle—from booking to billing. It serves two distinct user groups: **Clients** (who book birthdays, anniversaries, etc.) and **Admins** (who manage business operations, revenue, and reports).

Built with **Python Flask** and **MySQL**, this project demonstrates a full-stack architecture featuring secure authentication, dynamic cost calculation, and a RESTful API layer.

## 🚀 Key Features

### 👤 User Panel
* **Secure Authentication:** User registration and login with MD5 password hashing.
* **Event Booking:** Interactive form with guest sliders, date pickers, and tier selection.
* **Dynamic Pricing:** Real-time cost calculation based on guest count, tier (1-4), and extras (DJ, Valet).
* **Dashboard:** View booking history, status (Pending/Completed), and profile management.
* **E-Tickets:** Generate and view printable event tickets.

### 🛠 Admin Panel
* **Analytics Dashboard:** Visual graphs for revenue growth, user registration trends, and booking stats.
* **Event Management:** Edit, update, or cancel existing events.
* **User Management:** View and remove user accounts.
* **Reports:** Export full booking data to CSV for external analysis.

### 🔌 REST API (JSON)
The system includes a fully functional REST API for external integrations:
* `GET /api/events/all` - Fetch all events.
* `GET /api/event/<id>` - Fetch specific event details.
* `POST /api/event/create` - Create new events programmatically.
* `PUT /api/event/update/<id>` - Update event details.
* `DELETE /api/event/delete/<id>` - Remove events.

## 🏗 System Architecture
The application follows a **3-Tier Architecture**:
1.  **Presentation Layer:** HTML5, CSS3, Bootstrap 4 (Responsive GUI).
2.  **Application Layer:** Python Flask (Business Logic, Routing, API).
3.  **Data Layer:** MySQL Database (Relational Data Storage).

## 📸 Screenshots
| **User Dashboard** | **Admin Dashboard** |
|:---:|:---:|
| ![User Dash](https://via.placeholder.com/400x200?text=User+Dashboard) | ![Admin Dash](https://via.placeholder.com/400x200?text=Admin+Dashboard) |

| **Booking Interface** | **REST API (Postman)** |
|:---:|:---:|
| ![Booking](https://via.placeholder.com/400x200?text=Booking+Page) | ![API](https://via.placeholder.com/400x200?text=Postman+Test) |

## 🛠 Tech Stack
* **Backend:** Python, Flask, Werkzeug
* **Database:** MySQL (Hosted on PythonAnywhere)
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 4
* **Tools:** Postman (API Testing), Draw.io (UML Diagrams)

## ⚙️ Installation & Setup

### Prerequisites
* Python 3.x
* MySQL Server

### 1. Clone the Repository
```bash
git clone [https://github.com/sheikhrehanseo/Sync-And-Celebrate-EMS.git](https://github.com/sheikhrehanseo/Sync-And-Celebrate-EMS.git)
cd Sync-And-Celebrate-EMS
