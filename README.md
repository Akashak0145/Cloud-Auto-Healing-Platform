#  Cloud Auto-Healing Platform

A cloud-based application monitoring and automatic recovery system built using **AWS EC2, Docker, Python, Prometheus, and Grafana**.

The platform continuously monitors an application, detects failures, and automatically recovers the application container without manual intervention.

## 📌 Project Overview

In cloud environments, application failures can cause service interruptions and require manual intervention.

This project demonstrates an automated solution that:
- Monitors application health continuously.
- Detects application failures using Prometheus.
- Automatically starts or restarts failed Docker containers.
- Verifies application recovery.
- Visualizes infrastructure and recovery metrics using Grafana.

## 🎯 Objectives

- Deploy an application on AWS EC2.
- Implement containerized application deployment using Docker.
- Monitor application and infrastructure health.
- Build an automated failure detection and recovery mechanism.
- Visualize monitoring and recovery metrics through Grafana.

## 🏗️ System Architecture

```text
                 AWS EC2 (Ubuntu)
                        |
                 Docker Compose
                        |
             +----------+----------+
             |                     |
        FastAPI App            Monitoring
        (demo-app)                  |
             |               Prometheus
             |                    |
        Health Check          Grafana
       (/health)                 |
             |              Dashboard
             |
       Prometheus
             |
      Auto-Healing Engine
        (Python)
             |
       Detect Failure
             |
       Docker Restart
        / Docker Start
             |
       Verify Recovery
             |
       Recovery Metrics
             |
         Prometheus
```

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| AWS EC2 | Cloud infrastructure |
| Ubuntu | Server operating system |
| Docker | Containerization |
| Docker Compose | Container orchestration |
| Python | Auto-healing automation |
| FastAPI | Demo web application |
| Prometheus | Metrics collection and monitoring |
| Grafana | Monitoring dashboards |
| Node Exporter | Host-level metrics |
| Docker Exporter | Docker container metrics |
| cAdvisor | Container monitoring component |

## ✨ Key Features

### 1. Application Monitoring
- Monitors FastAPI application availability.
- Uses Prometheus health metrics.
- Checks application health through `/health`.

### 2. Infrastructure Monitoring
- CPU usage monitoring.
- Memory usage monitoring.
- Disk usage monitoring.
- Network traffic monitoring.

### 3. Docker Container Monitoring
- Container CPU usage.
- Container memory usage.
- Container running status.

### 4. Automatic Healing
- Detects three consecutive failed health checks.
- Identifies whether the application container is running or stopped.
- Automatically restarts or starts the container.
- Verifies application recovery.
- Records recovery events.

### 5. Grafana Dashboard

The dashboard displays:
- EC2 CPU usage.
- EC2 memory usage.
- EC2 disk usage.
- EC2 network traffic.
- Application health.
- Docker container CPU and memory usage.
- Docker container running status.
- Total recovery attempts.
- Successful recoveries.
- Failed recoveries.

## ⚙️ Auto-Healing Workflow

1. The Python healing engine continuously checks application health.
2. Prometheus provides the application availability status.
3. If the application fails, the failure counter increases.
4. After three consecutive failures, recovery is triggered.
5. The engine checks the Docker container status.
6. If the container is stopped, it executes `docker start demo-app`.
7. If the container is running but the application is unhealthy, it executes `docker restart demo-app`.
8. The engine verifies recovery using the application health endpoint.
9. Recovery events are recorded and exposed as Prometheus metrics.

## 📊 Recovery Test Results

A controlled failure test was performed by intentionally stopping the application container.

**Test command:**

```bash
docker stop demo-app
```

The auto-healing engine detected the failure and automatically started the container.

**Verification command:**

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "demo-app"
}
```

### Observed Recovery Metrics

| Metric | Result |
|---|---:|
| Total Recovery Attempts | 6 |
| Successful Recoveries | 6 |
| Failed Recoveries | 0 |
| Observed Success Rate | 100% |

*These metrics include previously recorded recovery history.*

## 🚀 Deployment and Setup

### Prerequisites

- AWS account
- Ubuntu EC2 instance
- Docker
- Docker Compose
- Python 3
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/cloud-auto-healing-platform.git
```

```bash
cd cloud-auto-healing-platform
```

### 2. Start the Docker Services

```bash
docker compose up -d --build
```

### 3. Check Running Containers

```bash
docker ps
```

### 4. Check Application Health

```bash
curl http://localhost:8000/health
```

### 5. Access Monitoring Services

| Service | URL |
|---|---|
| FastAPI Application | `http://EC2-PUBLIC-IP:8000` |
| Prometheus | `http://EC2-PUBLIC-IP:9090` |
| Grafana | `http://localhost:3000` through an SSH tunnel |

For secure Grafana access, create an SSH tunnel:

```bash
ssh -i your-key.pem -L 3000:localhost:3000 ubuntu@EC2-PUBLIC-IP
```

Then open `http://localhost:3000` in your browser.

### 6. Run the Auto-Healing Engine

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r auto-healing/requirements.txt
pip install prometheus-client
```

Start the healing engine:

```bash
python auto-healing/healer.py
```

Start the recovery metrics exporter in another terminal:

```bash
python auto-healing/recovery_exporter.py
```

**Note:** The project uses a configured Docker socket proxy and Prometheus scrape targets. Review `docker-compose.yml` and `monitoring/prometheus/prometheus.yml` before deployment to ensure the service configuration is correct for your environment.

## 📁 Project Structure

```text
cloud-auto-healing-platform/
│
├── app/
│   └── main.py
│
├── auto-healing/
│   ├── healer.py
│   ├── recovery_exporter.py
│   ├── requirements.txt
│   └── logs/
│
├── docker-exporter/
│   └── exporter.py
│
├── monitoring/
│   └── prometheus/
│       └── prometheus.yml
│
├── docker-compose.yml
├── Dockerfile
└── README.md
```

*The structure above highlights the main project components; additional configuration files may also be present.*

## 🔮 Future Enhancements

- Email and real-time failure notifications.
- Advanced failure prediction.
- Kubernetes integration.
- Automated scaling.
- Recovery history database.
- Advanced alert management.

## 🎓 Learning Outcomes

Through this project, I gained practical experience in:

- Cloud computing using AWS EC2.
- Linux server administration.
- Docker containerization.
- Infrastructure monitoring.
- Prometheus and Grafana integration.
- Python automation.
- Automated application recovery.
- Cloud deployment and troubleshooting.

## 👨‍💻 Author

**Your Name**

B.Tech – Information Technology

## ⭐ Acknowledgement

This project was developed as an academic project to demonstrate cloud infrastructure monitoring, container management, and automated application recovery.
