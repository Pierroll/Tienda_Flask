from locust import HttpUser, task, between

class MyUser(HttpUser):
    host = "http://192.168.18.34:5000"  # Aquí defines tu URL base
    # Tiempo de espera entre tareas (1-2 segundos aleatorios)
    wait_time = between(1, 2)

    # Tarea: acceder a la página de inicio
    @task
    def index(self):
        self.client.get("/")  # Simula una solicitud GET a la raíz de tu app

    # Tarea: realizar login
    @task
    def login(self):
        self.client.post("/login", data={"email": "admin@example.com", "password": "admin123"})