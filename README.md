# 🧳 ALX Travel App (0x02)

This Django-based **Travel App** is part of the ALX Backend Python curriculum.  
It demonstrates how to define Django models, apply migrations, and interact with the ORM for data persistence.

---

## 🚀 Project Overview

The Travel App allows managing **Bookings** and their corresponding **Payments**.

### **Features**
- Create and store booking records
- Link each payment to a booking
- Perform database operations using Django ORM
- Maintain relational integrity between tables

---

## 🧩 Models

### **Booking**
| Field | Type | Description |
|-------|------|--------------|
| `customer_name` | CharField | Name of the customer |
| `email` | EmailField | Customer’s email address |
| `destination` | CharField | Travel destination |
| `travel_date` | DateField | Date of the travel |
| `amount` | DecimalField | Cost of the booking |
| `status` | CharField | Booking status |

### **Payment**
| Field | Type | Description |
|-------|------|--------------|
| `booking` | ForeignKey | Linked booking |
| `payment_date` | DateField | Date of payment |
| `amount` | DecimalField | Amount paid |
| `status` | CharField | Payment status |

---

## 🛠️ Setup Instructions

### **1. Clone the repository**
```bash
git clone https://github.com/<your-username>/alx_travel_app_0x02.git
cd alx_travel_app_0x02
