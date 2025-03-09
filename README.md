# **FastAPI URL Shortener**

I built this project to **learn FastAPI** and **deepen my understanding of APIs**. It allows users to generate **short, unique URLs** for longer web links and redirect them when accessed.

## **🔹 Features**
- **URL Shortening** → Converts long URLs into short, Base62-encoded links.
- **Redirects** → Accessing a short URL redirects to the original link.
- **Click Tracking** → Logs how many times each short URL has been accessed.
- **Database Storage** → URLs and click counts are stored using **SQLModel**.
- **Dockerized Deployment** → Packaged in a **Docker container** for easy deployment.

## **🔹 Technologies Used**
- **FastAPI** → High-performance web framework for Python.
- **SQLModel** → Database ORM for storing URLs and analytics.
- **Base62 Encoding** → Generates short, unique URL identifiers.
- **Docker** → Containerization for easy deployment.

## **🔹 Installation & Usage**
### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/fastapi-url-shortener.git
cd fastapi-url-shortener
```

### **2. Run with Docker** 
```bash
docker build -t fastapi-url-shortener .
docker run -p 8080:8080 fastapi-url-shortener
```

