import os
import time
import docker

from prometheus_client import Gauge, start_http_server

client = docker.DockerClient(
    base_url=os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
)

cpu_gauge = Gauge(
    "docker_container_cpu_percent",
    "Docker container CPU usage percentage",
    ["container"]
)

memory_gauge = Gauge(
    "docker_container_memory_bytes",
    "Docker container memory usage in bytes",
    ["container"]
)

running_gauge = Gauge(
    "docker_container_running",
    "Docker container running status",
    ["container"]
)


def collect_metrics():
    containers = client.containers.list(all=True)

    cpu_gauge.clear()
    memory_gauge.clear()
    running_gauge.clear()

    for container in containers:
        name = container.name

        running = container.status == "running"
        running_gauge.labels(container=name).set(int(running))

        if not running:
            continue

        stats = container.stats(stream=False)

        memory = stats.get("memory_stats", {}).get("usage", 0)

        cpu = stats.get("cpu_stats", {})
        precpu = stats.get("precpu_stats", {})

        cpu_delta = (
            cpu.get("cpu_usage", {}).get("total_usage", 0)
            - precpu.get("cpu_usage", {}).get("total_usage", 0)
        )

        system_delta = (
            cpu.get("system_cpu_usage", 0)
            - precpu.get("system_cpu_usage", 0)
        )

        online_cpus = cpu.get("online_cpus", 1)

        cpu_percent = 0

        if system_delta > 0 and cpu_delta >= 0:
            cpu_percent = (
                cpu_delta / system_delta
            ) * online_cpus * 100

        cpu_gauge.labels(container=name).set(cpu_percent)
        memory_gauge.labels(container=name).set(memory)


if __name__ == "__main__":
    start_http_server(9101)

    print("Docker Metrics Exporter started on port 9101", flush=True)

    while True:
        try:
            collect_metrics()
        except Exception as error:
            print(f"Metrics collection error: {error}", flush=True)

        time.sleep(15)