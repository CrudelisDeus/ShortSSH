import os
import sys
from functools import wraps
from typing import Any, Callable, Optional


def require_ssh_config(
    func: Callable[..., Any],
) -> Callable[..., Optional[Any]]:
    @wraps(func)
    def wrapper(self: "ShortSSH", *args: Any, **kwargs: Any) -> Optional[Any]:
        if not os.path.exists(self.path_ssh_config):
            os.system("clear")
            print(self.logo())
            print(f"[!] SSH config file not found: {self.path_ssh_config}")
            print("\n[!] Create SSH config file? (y/n)")
            ch = input("\n" "[>]: ").strip().lower()

            if ch == "y":
                ssh_dir = os.path.dirname(self.path_ssh_config)
                os.makedirs(ssh_dir, exist_ok=True)
                os.chmod(ssh_dir, 0o700)
                with open(self.path_ssh_config, "w") as f:
                    print("[+] Creating SSH config file...")
                    f.write(
                        """#-----------------#
# ShortSSH Config #
#-----------------#
"""
                    )
                os.chmod(self.path_ssh_config, 0o600)
            return None
        return func(self, *args, **kwargs)

    return wrapper


class ShortSSH:
    def __init__(self):
        # General
        self.name_app = "ShortSSH"
        self.github_url = "github.com/CrudelisDeus"
        self.version_app = "0.0.0"

        # ShortSSH
        self.port_host = None
        self.user_host = None
        self.ip_host = None
        self.short_name_host = None
        self.key_host = None

        self.path_ssh_config = os.path.expanduser("~/.ssh/config")
        self.program_dir = os.path.dirname(os.path.abspath(__file__))
        self.backup_dir = os.path.join(self.program_dir, "backups")

    def logo(self) -> str:
        logo = rf"""
  / _ \
\_\(_)/_/ {self.name_app} v{self.version_app}
 _//o\\_  {self.github_url}
  /   \
"""
        return logo

    # ------------------------------------------------------------------------
    # check
    # ------------------------------------------------------------------------
    def get_backup_list(self) -> list[str]:
        if not os.path.isdir(self.backup_dir):
            return []

        return sorted(
            f
            for f in os.listdir(self.backup_dir)
            if os.path.isfile(os.path.join(self.backup_dir, f))
        )

    def check_backup_exists(self, name: str) -> bool:
        path = os.path.join(self.backup_dir, name)
        return os.path.isfile(path)

    def check_host_ip(self, ip: str) -> bool:
        ip = ip.strip()
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True

    def check_host_port(self, port: str) -> bool:
        port = port.strip()
        if not port.isdigit():
            return False
        num = int(port)
        if num < 1 or num > 65535:
            return False
        return True

    def check_host_short_name(self, short_name: str) -> bool:
        short_name = short_name.strip()
        if not short_name:
            return False
        if " " in short_name:
            return False
        return True

    def check_host_exists(self, short_name: str) -> bool:
        short_name = short_name.strip()
        if not os.path.isfile(self.path_ssh_config):
            return False

        with open(
            self.path_ssh_config,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if s.lower().startswith("host "):
                    parts = s.split()
                    if short_name in parts[1:]:
                        return True
        return False

    # ------------------------------------------------------------------------
    # functionality
    # ------------------------------------------------------------------------
    @require_ssh_config
    def restore_ssh_config(self, name: str) -> None:
        name = name.strip()
        if not name:
            print("\n[!] Empty backup name")
            return
        src = os.path.join(self.backup_dir, name)
        if not os.path.isfile(src):
            print("\n[!] Backup not found")
            return

        with open(src, "r", encoding="utf-8", errors="replace") as fsrc, open(
            self.path_ssh_config, "w", encoding="utf-8"
        ) as fdst:
            fdst.write(fsrc.read())

        os.chmod(self.path_ssh_config, 0o600)
        print(f"\n[+] Restored: {name}")

    @require_ssh_config
    def backup_ssh_config(self, name: str) -> None:
        os.makedirs(self.backup_dir, exist_ok=True)

        dst = os.path.join(self.backup_dir, name)

        if self.check_backup_exists(name):
            print("\n[!] Backup with this name already exists")
            return

        with open(
            self.path_ssh_config, "r", encoding="utf-8", errors="replace"
        ) as src, open(dst, "w", encoding="utf-8") as out:
            out.write(src.read())

        print(f"\n[+] Backup created: {name}")

    @require_ssh_config
    def find_host(self, kind: str) -> None:
        kind = kind.strip().lower()
        if kind not in ("ip", "hostname", "port", "user"):
            return

        os.system("clear")
        print(self.logo())

        if kind == "ip":
            prompt = "Enter IP (or part): "
        elif kind == "hostname":
            prompt = "Enter HostName (or part): "
        elif kind == "port":
            prompt = "Enter Port (or part): "
        else:
            prompt = "Enter Username (or part): "

        query = input(prompt).strip()
        if not query:
            return

        query_l = query.lower()
        blocks: list[str] = []
        buf: list[str] = []

        def push() -> None:
            if not buf:
                return

            block = "".join(buf)
            block_l = block.lower()

            if kind == "hostname":
                first = block_l.splitlines()[0].strip()
                if first.startswith("host ") and query_l in first:
                    blocks.append(block)
                return

            for raw in block_l.splitlines():
                s = raw.strip()
                if kind == "ip" and s.startswith("hostname ") and query_l in s:
                    blocks.append(block)
                    return
                if kind == "port" and s.startswith("port ") and query_l in s:
                    blocks.append(block)
                    return
                if kind == "user" and s.startswith("user ") and query_l in s:
                    blocks.append(block)
                    return

        with open(
            self.path_ssh_config,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:
            for line in f:
                if line.strip().lower().startswith("host "):
                    push()
                    buf = [line]
                elif buf:
                    buf.append(line)
        push()

        os.system("clear")
        print(self.logo())

        if not blocks:
            print("[!] Not found")
            input("\nPress Enter...")
            return

        print(f"[+] Found: {len(blocks)}\n")
        print("\n".join(b.rstrip() for b in blocks))
        input("\nPress Enter...")

    @require_ssh_config
    def open_editor(self) -> None:
        import os
        import shlex
        import shutil
        import subprocess

        path = self.path_ssh_config

        editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
        if not editor:
            for candidate in ("nvim", "vim", "vi", "nano"):
                if shutil.which(candidate):
                    editor = candidate
                    break

        if not editor:
            print("[!] No editor available (set $EDITOR or $VISUAL)")
            input("\nPress Enter...")
            return

        cmd = shlex.split(editor)

        sys.stdout.flush()

        try:
            subprocess.call(cmd + [path])
        finally:
            pass

    def set_host(self, item: str) -> bool:
        if item == "ip":
            ip = input("Enter IP Address: ")
            if self.check_host_ip(ip):
                self.ip_host = ip
            else:
                print("\n[!] Invalid IP address format\n")
                return False
        elif item == "port":
            port = input("Enter Port: ")
            if not port:
                port = "22"
            if self.check_host_port(port):
                self.port_host = port
            else:
                print("\n[!] Invalid Port format\n")
                return False
        elif item == "user":
            user = input("Enter Username: ")
            if not user:
                import getpass

                user = getpass.getuser()
            self.user_host = user
        elif item == "short_name":
            short_name = input("Enter Short Name: ").strip()

            if not self.check_host_short_name(short_name):
                print("\n[!] Invalid Short Name format\n")
                return False

            if self.check_host_exists(short_name):
                print("\n[!] Short Name already exists in SSH config\n")
                return False
            self.short_name_host = short_name
        elif item == "key":
            key = input("Enter Path to Key File (or leave empty): ").strip()
            if key:
                key = os.path.expanduser(key)
                if not os.path.isfile(key):
                    print("\n[!] Key file does not exist\n")
                    return False
                self.key_host = key
            else:
                self.key_host = None

        return True

    # ------------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------------
    @require_ssh_config
    def find_menu(self) -> None:
        menu = [
            "1. Find by IP",
            "2. Find by host name",
            "3. Find by port name",
            "4. Find by user name",
            "q. Back",
        ]
        while True:
            os.system("clear")
            print(self.logo())
            for item in menu:
                print(item)
            ch = input("\n[>]: ").strip().lower()
            if ch == "q":
                break
            elif ch == "1":
                self.find_host("ip")
            elif ch == "2":
                self.find_host("hostname")
            elif ch == "3":
                self.find_host("port")
            elif ch == "4":
                self.find_host("user")

    @require_ssh_config
    def add_menu(self) -> None:
        os.system("clear")
        print(self.logo())

        while not self.set_host("port"):
            pass
        while not self.set_host("user"):
            pass
        while not self.set_host("ip"):
            pass
        while not self.set_host("short_name"):
            pass

        if not self.set_host("key"):
            input("Press Enter...")

        while True:
            os.system("clear")
            print(self.logo())
            print("[+] New Host Details:")
            print(f"    Port: {self.port_host}")
            print(f"    Username: {self.user_host}")
            print(f"    IP Address: {self.ip_host}")
            print(f"    Short Name: {self.short_name_host}")

            if self.key_host:
                print(f"    Key File: {self.key_host}")

            print("\nAre you sure you want to add this host? (y/n)")

            ch = input("\n[>]: ").strip().lower()
            if ch == "y":
                with open(self.path_ssh_config, "a") as f:
                    f.write(
                        f"""Host {self.short_name_host}
        HostName {self.ip_host}
        User {self.user_host}
        Port {self.port_host}
"""
                    )
                    if self.key_host:
                        f.write(f"        IdentityFile {self.key_host}\n")
                break
            elif ch == "n":
                return
            else:
                print("\n[!] Please enter y or n.")

    @require_ssh_config
    def menu_backup_ssh(self) -> None:
        os.system("clear")
        print(self.logo())

        while True:
            os.system("clear")
            print(self.logo())
            print("Enter backup name (or 'q' to Back): ")
            ch = input("\n[>]: ").strip()
            if ch.lower() == "q":
                break
            else:
                os.makedirs(self.backup_dir, exist_ok=True)
                self.backup_ssh_config(ch)
                input("\nPress Enter...")
                break

    @require_ssh_config
    def menu_restore_ssh(self) -> None:
        while True:
            os.system("clear")
            print(self.logo())

            backups = self.get_backup_list()
            if not backups:
                print("[!] No backups")
            else:
                print("[+] Backups:\n")
                for b in backups:
                    print(f" - {b}")

            print("\nEnter backup name to restore (or 'q' to Back): ")
            ch = input("\n[>]: ").strip()
            if ch.lower() == "q":
                break
            else:
                self.restore_ssh_config(ch)
                input("\nPress Enter...")
                break

    def backup_restore_menu(self) -> None:

        menu = [
            "1. Backup SSH config",
            "2. Restore SSH config",
            "q. Back",
        ]

        while True:
            os.system("clear")
            print(self.logo())
            for item in menu:
                print(item)
            ch = input("\n[>]: ").strip().lower()
            if ch == "q":
                break
            elif ch == "1":
                self.menu_backup_ssh()
            elif ch == "2":
                self.menu_restore_ssh()

    def main_menu(self) -> None:

        menu = [
            "1. Add new host",
            "2. Open config in editor",
            "3. Find host",
            "4. Backup/Restore SSH config",
            "q. Quit",
        ]

        while True:
            os.system("clear")
            print(self.logo())
            for item in menu:
                print(item)
            ch = input("\n[>]: ").strip().lower()
            if ch == "q":
                break
            elif ch == "1":
                self.add_menu()
            elif ch == "2":
                self.open_editor()
            elif ch == "3":
                self.find_menu()
            elif ch == "4":
                self.backup_restore_menu()

    def main(self) -> None:
        self.main_menu()
        os.system("clear")


if __name__ == "__main__":
    app = ShortSSH()
    app.main()
