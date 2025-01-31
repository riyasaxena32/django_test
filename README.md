# **FAQ Management System**  

A **Django-based** FAQ management system with **multilingual support**, **rich text editing**, and a **REST API**. The system provides automatic translation into **Hindi and Bengali** and features a modern admin interface for content management.  

## **Features**  

✅ **FAQ Creation & Management** with rich text editing  
✅ **Automatic Translation** to Hindi and Bengali  
✅ **REST API** for programmatic access  
✅ **Admin Interface** with translation preview  
✅ **Real-Time Translation Status Indicators**  
✅ **Caching** for improved performance  
✅ **Comprehensive Test Coverage**  
✅ **Dockerized Deployment** for easy setup  

---

## **Tech Stack**  

- **Backend:** Django 4.2, Django REST Framework  
- **Database:** PostgreSQL 15  
- **Frontend:** Django Quill Editor (for rich text)  
- **Containerization:** Docker & Docker Compose  
- **Testing:** Pytest  
- **Programming Language:** Python 3.12  

---

## **Installation**  

### **Prerequisites**  

- **Docker & Docker Compose**  
-  **Git**  

### **Quick Start**  

1️⃣ Clone the repository:  
   ```bash
   git clone <repository-url>
   cd project
   ```

2️⃣ Create a `.env` file and add:  
   ```ini
   DEBUG=1
   DJANGO_SETTINGS_MODULE=project.settings
   POSTGRES_DB=faq_db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   ```

3️⃣ Build and start the containers:  
   ```bash
   docker-compose up --build
   ```

4️⃣ Create a superuser:  
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5️⃣ Access the services:  
   - **Django App:** [http://localhost:8000](http://localhost:8000)  
  ---