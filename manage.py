#!/usr/bin/env python3
"""
MedCase Pro Platform - Boshqaruv Skripti
Django-style manage.py komandalar bilan

Foydalanish:
    python3 manage.py runserver      - Lokal server
    python3 manage.py runglobal      - Ngrok bilan global server
    python3 manage.py migrate        - Migratsiyalarni bajarish
    python3 manage.py seed           - Boshlang'ich ma'lumotlar
    python3 manage.py test           - Testlarni ishga tushirish
    python3 manage.py shell          - Python shell
"""

import os
import sys
import subprocess
import signal
import time
import threading
import json
import logging

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bcrypt warninglarni yashirish
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Ngrok konfiguratsiya
NGROK_AUTHTOKEN = "2J5Jz1cRN7uvC2pMiTLADxbVgKS_3ebRRgDnLVjvAwe8cn1d3"
DEFAULT_PORT = 8000


def run_command(cmd, shell=True, capture=False):
    """Komandani ishga tushirish."""
    try:
        if capture:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
            return result.stdout, result.stderr, result.returncode
        else:
            return subprocess.run(cmd, shell=shell)
    except KeyboardInterrupt:
        pass


def check_ngrok_installed():
    """Ngrok o'rnatilganligini tekshirish."""
    stdout, _, code = run_command("which ngrok || where ngrok 2>/dev/null", capture=True)
    return code == 0 and stdout.strip()


def install_ngrok():
    """Ngrok o'rnatish (macOS uchun)."""
    logger.info("Ngrok o'rnatilmoqda...")
    
    # macOS uchun homebrew
    if sys.platform == "darwin":
        result = run_command("brew install ngrok/ngrok/ngrok")
        if result.returncode != 0:
            # pip orqali pyngrok
            run_command(f"{sys.executable} -m pip install pyngrok")
            return "pyngrok"
    else:
        # Linux/Windows uchun pyngrok
        run_command(f"{sys.executable} -m pip install pyngrok")
        return "pyngrok"
    
    return "ngrok"


def setup_ngrok_auth():
    """Ngrok authtokenni sozlash."""
    logger.info("Ngrok authtoken sozlanmoqda...")
    run_command(f"ngrok config add-authtoken {NGROK_AUTHTOKEN}")


def get_ngrok_url():
    """Ngrok public URL ni olish."""
    try:
        import urllib.request
        response = urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels")
        data = json.loads(response.read().decode())
        for tunnel in data.get("tunnels", []):
            if tunnel.get("proto") == "https":
                return tunnel.get("public_url")
        # HTTPS topilmasa HTTP
        for tunnel in data.get("tunnels", []):
            return tunnel.get("public_url")
    except Exception as e:
        logger.debug(f"Ngrok URL olishda xato: {e}")
    return None


def run_server(port=DEFAULT_PORT, reload=True):
    """Lokal serverni ishga tushirish."""
    logger.info(f"🚀 MedCase Pro server ishga tushmoqda (port: {port})...")
    
    reload_flag = "--reload" if reload else ""
    cmd = f"{sys.executable} -m uvicorn ilova.asosiy:ilova --host 0.0.0.0 --port {port} {reload_flag}"
    run_command(cmd)


def run_global(port=DEFAULT_PORT):
    """Ngrok bilan global serverni ishga tushirish."""
    print("\n" + "=" * 60)
    print("🌍 MedCase Pro Global Server")
    print("=" * 60)
    
    # Ngrok tekshirish
    if not check_ngrok_installed():
        logger.info("Ngrok topilmadi, o'rnatilmoqda...")
        ngrok_type = install_ngrok()
        
        if ngrok_type == "pyngrok":
            # pyngrok orqali ishga tushirish
            run_global_with_pyngrok(port)
            return
    
    # Ngrok authtoken sozlash
    setup_ngrok_auth()
    
    # Uvicorn server jarayoni
    server_process = None
    ngrok_process = None
    
    def cleanup(signum=None, frame=None):
        """Jarayonlarni to'xtatish."""
        logger.info("\n🛑 Server to'xtatilmoqda...")
        if server_process:
            server_process.terminate()
        if ngrok_process:
            ngrok_process.terminate()
        sys.exit(0)
    
    # Signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # 1. Uvicorn serverni background da ishga tushirish
        logger.info(f"📦 Backend server ishga tushmoqda (port: {port})...")
        server_cmd = f"{sys.executable} -m uvicorn ilova.asosiy:ilova --host 0.0.0.0 --port {port}"
        server_process = subprocess.Popen(
            server_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        # Server ishga tushishini kutish
        time.sleep(3)
        
        # 2. Ngrok tunnel ochish
        logger.info("🌐 Ngrok tunnel ochilmoqda...")
        ngrok_process = subprocess.Popen(
            f"ngrok http {port}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        # Ngrok ishga tushishini kutish
        time.sleep(3)
        
        # 3. Public URL olish
        public_url = None
        for _ in range(10):
            public_url = get_ngrok_url()
            if public_url:
                break
            time.sleep(1)
        
        if public_url:
            print("\n" + "=" * 60)
            print("✅ MedCase Pro Global Server tayyor!")
            print("=" * 60)
            print(f"\n🌍 PUBLIC URL: {public_url}")
            print(f"📱 API: {public_url}/api/v1")
            print(f"📚 Docs: {public_url}/hujjatlar")
            print(f"\n🏠 Local: http://localhost:{port}")
            print("\n💡 Frontend .env ga qo'shing:")
            print(f"   VITE_API_URL={public_url}/api/v1")
            print(f"   VITE_WS_URL={public_url.replace('https', 'wss')}/api/v1/ws")
            print("\n" + "=" * 60)
            print("To'xtatish uchun Ctrl+C bosing")
            print("=" * 60 + "\n")
        else:
            logger.warning("⚠️ Ngrok URL olinmadi, ngrok dashboardni tekshiring: http://127.0.0.1:4040")
        
        # Server loglarini ko'rsatish
        while True:
            output = server_process.stdout.readline()
            if output:
                print(output.decode().strip())
            elif server_process.poll() is not None:
                break
            time.sleep(0.1)
            
    except Exception as e:
        logger.error(f"Xatolik: {e}")
    finally:
        cleanup()


def run_global_with_pyngrok(port=DEFAULT_PORT):
    """pyngrok kutubxonasi orqali global server."""
    try:
        from pyngrok import ngrok, conf
        
        # Authtoken sozlash
        conf.get_default().auth_token = NGROK_AUTHTOKEN
        
        print("\n" + "=" * 60)
        print("🌍 MedCase Pro Global Server (pyngrok)")
        print("=" * 60)
        
        # Ngrok tunnel ochish
        logger.info("🌐 Ngrok tunnel ochilmoqda...")
        public_url = ngrok.connect(port, "http").public_url
        
        print("\n" + "=" * 60)
        print("✅ Ngrok tunnel tayyor!")
        print("=" * 60)
        print(f"\n🌍 PUBLIC URL: {public_url}")
        print(f"📱 API: {public_url}/api/v1")
        print(f"📚 Docs: {public_url}/hujjatlar")
        print(f"\n🏠 Local: http://localhost:{port}")
        print("\n💡 Frontend .env ga qo'shing:")
        print(f"   VITE_API_URL={public_url}/api/v1")
        print(f"   VITE_WS_URL={public_url.replace('https', 'wss')}/api/v1/ws")
        print("\n" + "=" * 60)
        print("Server ishga tushmoqda... To'xtatish uchun Ctrl+C")
        print("=" * 60 + "\n")
        
        # Uvicorn server
        run_server(port, reload=True)
        
    except ImportError:
        logger.error("pyngrok o'rnatilmagan. O'rnatish: pip install pyngrok")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        sys.exit(1)


def run_migrate():
    """Alembic migratsiyalarini bajarish."""
    logger.info("📦 Migratsiyalar bajarilmoqda...")
    run_command("alembic upgrade head")


def run_seed():
    """Boshlang'ich ma'lumotlarni yuklash."""
    logger.info("🌱 Boshlang'ich ma'lumotlar yuklanmoqda...")
    run_command(f"{sys.executable} -m skriptlar.boshlangich_malumotlar")


def run_test():
    """Testlarni ishga tushirish."""
    logger.info("🧪 Testlar ishga tushmoqda...")
    run_command(f"{sys.executable} -m pytest testlar/ -v")


def run_shell():
    """Python interactive shell."""
    logger.info("🐍 Python shell ishga tushmoqda...")
    
    # IPython mavjudligini tekshirish
    try:
        import IPython
        IPython.embed()
    except ImportError:
        import code
        code.interact(local=dict(globals(), **locals()))


def run_frontend(port=5173):
    """Frontend serverni ishga tushirish."""
    logger.info("⚛️ Frontend server ishga tushmoqda...")
    os.chdir("frontend")
    run_command(f"npm run dev -- --port {port}")


def run_frontend_global(port=5173):
    """Frontend serverni ngrok bilan global ishga tushirish."""
    print("\n" + "=" * 60)
    print("🌍 MedCase Pro Frontend Global Server")
    print("=" * 60)
    
    # Ngrok tekshirish va sozlash
    if not check_ngrok_installed():
        logger.info("Ngrok topilmadi, o'rnatilmoqda...")
        ngrok_type = install_ngrok()
        
        if ngrok_type == "pyngrok":
            run_frontend_global_pyngrok(port)
            return
    
    setup_ngrok_auth()
    
    frontend_process = None
    ngrok_process = None
    
    def cleanup(signum=None, frame=None):
        logger.info("\n🛑 Frontend server to'xtatilmoqda...")
        if frontend_process:
            frontend_process.terminate()
        if ngrok_process:
            ngrok_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # 1. Frontend serverni background da ishga tushirish
        logger.info(f"⚛️ Frontend server ishga tushmoqda (port: {port})...")
        original_dir = os.getcwd()
        os.chdir("frontend")
        frontend_cmd = f"npm run dev -- --port {port} --host"
        frontend_process = subprocess.Popen(
            frontend_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        os.chdir(original_dir)
        
        time.sleep(5)  # Vite ishga tushishini kutish
        
        # 2. Ngrok tunnel ochish
        logger.info("🌐 Ngrok tunnel ochilmoqda...")
        ngrok_process = subprocess.Popen(
            f"ngrok http {port}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        time.sleep(3)
        
        # 3. Public URL olish
        public_url = None
        for _ in range(10):
            public_url = get_ngrok_url()
            if public_url:
                break
            time.sleep(1)
        
        if public_url:
            print("\n" + "=" * 60)
            print("✅ MedCase Pro Frontend Global tayyor!")
            print("=" * 60)
            print(f"\n🌍 PUBLIC URL: {public_url}")
            print(f"\n📱 Bu linkni do'stingizga yuboring!")
            print(f"\n🏠 Local: http://localhost:{port}")
            print("\n" + "=" * 60)
            print("To'xtatish uchun Ctrl+C bosing")
            print("=" * 60 + "\n")
        else:
            logger.warning("⚠️ Ngrok URL olinmadi, http://127.0.0.1:4040 ni tekshiring")
        
        # Frontend loglarini ko'rsatish
        while True:
            output = frontend_process.stdout.readline()
            if output:
                print(output.decode().strip())
            elif frontend_process.poll() is not None:
                break
            time.sleep(0.1)
            
    except Exception as e:
        logger.error(f"Xatolik: {e}")
    finally:
        cleanup()


def run_frontend_global_pyngrok(port=5173):
    """Frontend serverni pyngrok bilan global ishga tushirish."""
    try:
        from pyngrok import ngrok, conf
        
        conf.get_default().auth_token = NGROK_AUTHTOKEN
        
        print("\n" + "=" * 60)
        print("🌍 MedCase Pro Frontend Global Server (pyngrok)")
        print("=" * 60)
        
        # Ngrok tunnel ochish
        logger.info("🌐 Ngrok tunnel ochilmoqda...")
        public_url = ngrok.connect(port, "http").public_url
        
        print("\n" + "=" * 60)
        print("✅ Frontend Global tayyor!")
        print("=" * 60)
        print(f"\n🌍 PUBLIC URL: {public_url}")
        print(f"\n📱 Bu linkni do'stingizga yuboring!")
        print(f"\n🏠 Local: http://localhost:{port}")
        print("\n" + "=" * 60)
        print("Frontend ishga tushmoqda... To'xtatish uchun Ctrl+C")
        print("=" * 60 + "\n")
        
        # Frontend server
        os.chdir("frontend")
        run_command(f"npm run dev -- --port {port} --host")
        
    except ImportError:
        logger.error("pyngrok o'rnatilmagan. O'rnatish: pip install pyngrok")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        sys.exit(1)


def kill_port(port):
    """Portni band qilgan jarayonni to'xtatish."""
    try:
        if sys.platform == "darwin" or sys.platform.startswith("linux"):
            os.system(f"lsof -ti:{port} | xargs kill -9 2>/dev/null")
        else:
            os.system(f"for /f \"tokens=5\" %a in ('netstat -aon ^| find \":{port}\"') do taskkill /F /PID %a 2>nul")
    except:
        pass


def update_vite_allowed_hosts(ngrok_host):
    """Vite config'ga ngrok hostni qo'shish."""
    vite_config_path = "frontend/vite.config.js"
    
    try:
        with open(vite_config_path, "r") as f:
            content = f.read()
        
        # Agar bu host allaqachon qo'shilgan bo'lsa, o'tkazib yuborish
        if ngrok_host in content:
            return
        
        # allowedHosts arrayiga yangi hostni qo'shish
        # '.ngrok-free.app' dan oldin qo'shamiz
        old_pattern = "'.ngrok-free.app',"
        new_pattern = f"'{ngrok_host}',\n      '.ngrok-free.app',"
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            
            with open(vite_config_path, "w") as f:
                f.write(content)
            
            logger.info(f"✅ Vite config yangilandi: {ngrok_host}")
    except Exception as e:
        logger.warning(f"Vite config yangilashda xato: {e}")


def cleanup_all():
    """Barcha eski jarayonlarni to'xtatish."""
    logger.info("🧹 Eski jarayonlar tozalanmoqda...")
    
    # Jarayonlarni to'xtatish
    if sys.platform == "darwin" or sys.platform.startswith("linux"):
        os.system("pkill -9 -f 'uvicorn ilova' 2>/dev/null")
        os.system("pkill -9 -f 'ngrok' 2>/dev/null")
    
    # Portlarni tozalash
    kill_port(8000)
    kill_port(5173)
    kill_port(4040)
    
    time.sleep(1)


def run_all_global(backend_port=8000, frontend_port=5173):
    """Backend va Frontend ni global ishga tushirish."""
    
    # Avval eski jarayonlarni tozalash
    cleanup_all()
    
    print("\n" + "=" * 60)
    print("🌍 MedCase Pro Full Stack Global Server")
    print("=" * 60)
    
    try:
        from pyngrok import ngrok, conf
        conf.get_default().auth_token = NGROK_AUTHTOKEN
    except ImportError:
        logger.info("pyngrok o'rnatilmoqda...")
        run_command(f"{sys.executable} -m pip install pyngrok")
        from pyngrok import ngrok, conf
        conf.get_default().auth_token = NGROK_AUTHTOKEN
    
    # Eski ngrok tunnellarni yopish
    try:
        ngrok.kill()
    except:
        pass
    
    backend_process = None
    frontend_process = None
    
    def cleanup(signum=None, frame=None):
        logger.info("\n🛑 Serverlar to'xtatilmoqda...")
        ngrok.kill()
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # 1. Backend server
        logger.info(f"📦 Backend server ishga tushmoqda (port: {backend_port})...")
        backend_cmd = f"{sys.executable} -m uvicorn ilova.asosiy:ilova --host 0.0.0.0 --port {backend_port}"
        backend_process = subprocess.Popen(backend_cmd, shell=True)
        time.sleep(4)
        
        # 2. Backend ngrok
        logger.info("🌐 Backend tunnel ochilmoqda...")
        backend_url = ngrok.connect(backend_port, "http").public_url
        
        # 3. Frontend .env - proxy orqali ishlaydi, o'zgartirish shart emas
        logger.info(f"✅ Backend URL: {backend_url}")
        
        # 4. Frontend server
        logger.info(f"⚛️ Frontend server ishga tushmoqda (port: {frontend_port})...")
        original_dir = os.getcwd()
        os.chdir("frontend")
        frontend_cmd = f"npm run dev -- --port {frontend_port} --host"
        frontend_process = subprocess.Popen(frontend_cmd, shell=True)
        os.chdir(original_dir)
        time.sleep(5)
        
        # 5. Frontend ngrok
        logger.info("🌐 Frontend tunnel ochilmoqda...")
        frontend_url = ngrok.connect(frontend_port, "http").public_url
        
        # Natijalarni ko'rsatish
        print("\n" + "=" * 70)
        print("✅ MedCase Pro Full Stack Global tayyor!")
        print("=" * 70)
        print(f"""
🖥️  FRONTEND (do'stingizga yuboring):
    {frontend_url}

📦 BACKEND API:
    {backend_url}/api/v1

📚 API Docs:
    {backend_url}/hujjatlar

🏠 Local URLs:
    Frontend: http://localhost:{frontend_port}
    Backend:  http://localhost:{backend_port}
""")
        print("=" * 70)
        print("To'xtatish uchun Ctrl+C bosing")
        print("=" * 70 + "\n")
        
        # Kutish
        while True:
            time.sleep(1)
            if backend_process.poll() is not None or frontend_process.poll() is not None:
                break
                
    except Exception as e:
        logger.error(f"Xatolik: {e}")
    finally:
        cleanup()


def run_both():
    """Backend va Frontend serverni parallel ishga tushirish."""
    logger.info("🚀 Backend va Frontend serverlar ishga tushmoqda...")
    
    import threading
    
    def run_backend():
        run_server(reload=True)
    
    def run_frontend_thread():
        time.sleep(2)
        os.chdir("frontend")
        run_command("npm run dev")
    
    backend_thread = threading.Thread(target=run_backend)
    frontend_thread = threading.Thread(target=run_frontend_thread)
    
    backend_thread.start()
    frontend_thread.start()
    
    backend_thread.join()
    frontend_thread.join()


def show_help():
    """Yordam ko'rsatish."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║              MedCase Pro Platform - Boshqaruv Skripti                  ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Komandalar:                                                       ║
║  ────────────────────────────────────────────────────────────────  ║
║                                                                    ║
║  🚀 Lokal Server:                                                  ║
║     runserver       - Lokal backend serverni ishga tushirish       ║
║     runfrontend     - Lokal frontend serverni ishga tushirish      ║
║     runboth         - Backend + Frontend parallel (lokal)          ║
║                                                                    ║
║  🌍 Global Server (Ngrok):                                         ║
║     runglobal       - Backend ni global ishga tushirish            ║
║     runglobal_front - Frontend ni global ishga tushirish           ║
║     runglobal_all   - Backend + Frontend global (tavsiya!)         ║
║                                                                    ║
║  📦 Ma'lumotlar bazasi:                                            ║
║     migrate         - Migratsiyalarni bajarish                     ║
║     seed            - Boshlang'ich ma'lumotlar yuklash             ║
║                                                                    ║
║  🧪 Test va Debug:                                                 ║
║     test            - Testlarni ishga tushirish                    ║
║     shell           - Python interactive shell                     ║
║                                                                    ║
║  ────────────────────────────────────────────────────────────────  ║
║                                                                    ║
║  Misollar:                                                         ║
║     python3 manage.py runglobal_all   # Eng oson - hammasi global  ║
║     python3 manage.py runglobal_front # Faqat frontend global      ║
║     python3 manage.py runserver       # Faqat backend lokal        ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")


def main():
    """Asosiy funksiya."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    # Qo'shimcha argumentlar
    port = DEFAULT_PORT
    if "--port" in sys.argv:
        port_idx = sys.argv.index("--port") + 1
        if port_idx < len(sys.argv):
            port = int(sys.argv[port_idx])
    
    commands = {
        "runserver": lambda: run_server(port),
        "runglobal": lambda: run_global(port),
        "runfrontend": lambda: run_frontend(),
        "runglobal_front": lambda: run_frontend_global(),
        "runglobal_all": lambda: run_all_global(),
        "runboth": run_both,
        "migrate": run_migrate,
        "seed": run_seed,
        "test": run_test,
        "shell": run_shell,
        "help": show_help,
        "-h": show_help,
        "--help": show_help,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ Noma'lum komanda: {command}")
        show_help()


if __name__ == "__main__":
    main()
