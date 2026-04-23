"""
tools/deploy_tools.py
=====================
Инструменты для агента деплоя (управление Docker-контейнерами).
"""

from langchain.tools import tool
from config import run_cmd, DOCKER_DIR, OUTPUT_DIR


@tool
def stop_and_remove_containers(placeholder: str = "") -> str:
    """Остановить и удалить все контейнеры текущего проекта. Передай пустую строку."""
    print(f"\n🛑 [Deploy] Останавливаю контейнеры...")
    abs_docker_dir = DOCKER_DIR.resolve()

    code, out, err = run_cmd("docker-compose down --remove-orphans", cwd=abs_docker_dir)
    if code == 0:
        print(f"   ✅ Контейнеры остановлены")
    else:
        print(f"   ⚠️  {err}")

    code2, out2, _ = run_cmd("docker ps -q --filter name=weather-app")
    if out2:
        run_cmd(f"docker rm -f {out2}")
        print(f"   ✅ Принудительно удалён: {out2}")

    return "Контейнеры остановлены и удалены"


@tool
def build_and_run_docker(placeholder: str = "") -> str:
    """Собрать образ и запустить контейнер. Передай пустую строку."""
    print(f"\n🐳 [Deploy] Собираю и запускаю контейнер...")

    abs_docker_dir = DOCKER_DIR.resolve()
    abs_output_dir = OUTPUT_DIR.resolve()
    compose_file = abs_docker_dir / "docker-compose.yml"
    dockerfile = abs_docker_dir / "Dockerfile"

    if not compose_file.exists():
        return f"❌ Ошибка: docker-compose.yml не найден в {abs_docker_dir}"
    if not dockerfile.exists():
        return f"❌ Ошибка: Dockerfile не найден в {abs_docker_dir}"

    print(f"   📂 DOCKER_DIR : {abs_docker_dir}")
    print(f"   📂 OUTPUT_DIR : {abs_output_dir}")
    print(f"   📄 Dockerfile :\n{dockerfile.read_text()}")
    print(f"   📄 docker-compose.yml :\n{compose_file.read_text()}")

    print(f"\n   🔨 Сборка образа...")
    code, out, err = run_cmd("docker-compose build --no-cache", cwd=abs_docker_dir)
    print(f"   stdout: {out[:300]}")
    if code != 0:
        print(f"   stderr: {err[:500]}")
        return f"❌ Ошибка сборки:\n{err}"
    print(f"   ✅ Образ собран")

    print(f"\n   🚀 Запуск контейнера...")
    code, out, err = run_cmd("docker-compose up -d", cwd=abs_docker_dir)
    if code != 0:
        print(f"   stderr: {err[:500]}")
        return f"❌ Ошибка запуска:\n{err}"
    print(f"   ✅ Контейнер запущен")

    code, port_out, _ = run_cmd("docker-compose port weather-app 80", cwd=abs_docker_dir)
    port = port_out.split(":")[-1] if ":" in port_out else "8080"
    url = f"http://localhost:{port}"
    print(f"   🌐 URL: {url}")
    return f"✅ Контейнер запущен. URL: {url}"


@tool
def check_container_status(placeholder: str = "") -> str:
    """Проверить статус контейнеров. Передай пустую строку."""
    code, out, err = run_cmd("docker-compose ps", cwd=DOCKER_DIR.resolve())
    if code != 0:
        return f"Ошибка: {err}"
    return out if out else "Контейнеры не запущены"
