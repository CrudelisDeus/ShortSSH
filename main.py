import os
import sys
from functools import wraps
from typing import Any, Callable, Optional


def clear_console() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def require_ssh_private_key(
    func: Callable[..., Any],
) -> Callable[..., Optional[Any]]:
    @wraps(func)
    def wrapper(self: "ShortSSH", *args: Any, **kwargs: Any) -> Optional[Any]:
        ssh_dir = os.path.dirname(self.path_ssh_config)

        if not os.path.isdir(ssh_dir):
            os.makedirs(ssh_dir, exist_ok=True)
            if not self.is_windows():
                os.chmod(ssh_dir, 0o700)

        private_keys: list[str] = []

        for name in os.listdir(ssh_dir):
            path = os.path.join(ssh_dir, name)
            if not os.path.isfile(path):
                continue

            low = name.lower()

            if low == "config":
                continue
            if low.startswith("known_hosts"):
                continue
            if low.endswith(".pub"):
                continue

            private_keys.append(name)

        if not private_keys:
            clear_console()
            print(self.logo())
            print("[!] No SSH private keys found")
            print("\n[!] Create SSH key? (y/n)")
            ch = input("\n[>]: ").strip().lower()
            if ch == "y":
                os.system("ssh-keygen -t ed25519")
            input("\nPress Enter...")
            return None

        return func(self, *args, **kwargs)

    return wrapper


def require_ssh_config(
    func: Callable[..., Any],
) -> Callable[..., Optional[Any]]:
    @wraps(func)
    def wrapper(self: "ShortSSH", *args: Any, **kwargs: Any) -> Optional[Any]:
        if not os.path.exists(self.path_ssh_config):
            clear_console()
            print(self.logo())
            print(f"[!] SSH config file not found: {self.path_ssh_config}")
            print("\n[!] Create SSH config file? (y/n)")
            ch = input("\n" "[>]: ").strip().lower()

            if ch == "y":
                ssh_dir = os.path.dirname(self.path_ssh_config)
                os.makedirs(ssh_dir, exist_ok=True)
                if not self.is_windows():
                    os.chmod(ssh_dir, 0o700)
                with open(self.path_ssh_config, "w") as f:
                    print("\n[+] Creating SSH config file...")
                    f.write(
                        """#-----------------#
# ShortSSH Config #
#-----------------#
"""
                    )
                if not self.is_windows():
                    os.chmod(self.path_ssh_config, 0o600)
            return None
        return func(self, *args, **kwargs)

    return wrapper


class ShortSSH:
    def __init__(self):
        # General
        self.name_app = "ShortSSH"
        self.github_url = "github.com/CrudelisDeus"
        self.version_app = ".dev"

        # ShortSSH
        self.port_host: int | None = None
        self.user_host: str | None = None
        self.ip_host: str | None = None
        self.short_name_host: str | None = None
        self.key_host: str | None = None

        self.path_ssh_config = os.path.expanduser("~/.ssh/config")
        self.program_dir = os.path.dirname(os.path.abspath(__file__))
        self.backup_dir = os.path.join(self.program_dir, "backups")

        # logo
        self.colors = [
            "\033[38;5;20m",
            "\033[38;5;52m",
            "\033[38;5;57m",
            "\033[38;5;63m",
            "\033[38;5;88m",
            "\033[38;5;93m",
        ]
        self.end_color = "\033[0m"

    def logo(self) -> str:
        import random

        selected_color = random.choice(self.colors)

        logo = rf"""{selected_color}
  / _ \
\_\(_)/_/ {self.name_app}{self.end_color} v{self.version_app}
{selected_color} _//o\\_{self.end_color}  {self.github_url}
{selected_color}  /   \{self.end_color}
"""
        return logo

    # ------------------------------------------------------------------------
    # check
    # ------------------------------------------------------------------------
    def get_ssh_private_key_list(self) -> list[str]:
        ssh_dir = os.path.dirname(self.path_ssh_config)

        if not os.path.isdir(ssh_dir):
            return []

        private_keys: list[str] = []
        for name in os.listdir(ssh_dir):
            path = os.path.join(ssh_dir, name)
            if not os.path.isfile(path):
                continue

            low = name.lower()

            if low == "config":
                continue
            if low.startswith("known_hosts"):
                continue
            if low.endswith(".pub"):
                continue

            private_keys.append(name)

        return sorted(private_keys)

    def get_backup_list(self) -> list[str]:
        if not os.path.isdir(self.backup_dir):
            return []

        return sorted(
            f
            for f in os.listdir(self.backup_dir)
            if os.path.isfile(os.path.join(self.backup_dir, f))
        )

    def is_windows(self) -> bool:
        return os.name == "nt"

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
    def not_valid_argument(self) -> None:
        print(self.logo())
        print("[!] Invalid argument. Use --help or -h.\n")

    def doc_help(self) -> None:
        print(self.logo())
        print("Usage:")
        print("  sssh                       Run interactive menu")
        print(
            "  sssh --list OR sssh -l    ",
            "Print hosts as: shortname, ip, port",
        )

        print("  sssh --help OR sssh -h     Show this help\n")

    def list_hosts_short_ip(self) -> None:
        if not os.path.isfile(self.path_ssh_config):
            print(f"[!] SSH config not found: {self.path_ssh_config}")
            return

        hosts: list[tuple[str, str, str]] = []
        cur_host: str | None = None
        cur_ip: str | None = None
        cur_port: str | None = None

        def push() -> None:
            nonlocal cur_host, cur_ip, cur_port
            if cur_host:
                hosts.append((cur_host, cur_ip or "-", cur_port or "22"))
            cur_host, cur_ip, cur_port = None, None, None

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

                low = s.lower()
                if low.startswith("host "):
                    push()
                    parts = s.split()
                    cur_host = parts[1] if len(parts) > 1 else None
                    continue

                if cur_host and low.startswith("hostname "):
                    cur_ip = s.split(None, 1)[1].strip()

                if cur_host and low.startswith("port "):
                    cur_port = s.split(None, 1)[1].strip()

        push()

        print(self.logo())

        if not hosts:
            print("[!] No hosts in config")
        else:
            w_name = max(len(name) for name, _, _ in hosts)
            w_ip = max(len(ip) for _, ip, _ in hosts)

            header = f"{'Name'.ljust(w_name)} | {'IP'.ljust(w_ip)} | Port"

            line = "=" * len(header)

            print(header)
            print(line)

            for name, ip, port in hosts:
                print(f"{name.ljust(w_name)} | {ip.ljust(w_ip)} | {port}")

            print(line + "\n")

    def delete_ssh_config(self) -> None:
        if not os.path.isfile(self.path_ssh_config):
            print("\n[!] SSH config file does not exist")
            return

        os.remove(self.path_ssh_config)
        print("\n[+] SSH config file deleted")

    def change_host(self, selected: str) -> None:
        clear_console()
        print(selected)
        print(self.logo())

        while not self.set_host("port"):
            pass
        while not self.set_host("user"):
            pass
        while not self.set_host("ip"):
            pass

        host_name = selected.splitlines()[0].split(None, 1)[1]

        new_block = (
            f"Host {host_name}\n"
            f"        HostName {self.ip_host}\n"
            f"        User {self.user_host}\n"
            f"        Port {self.port_host}\n"
        )

        with open(
            self.path_ssh_config,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:
            text = f.read()

        text = text.replace(selected, new_block, 1)

        with open(self.path_ssh_config, "w", encoding="utf-8") as f:
            f.write(text)

        if not self.is_windows():
            os.chmod(self.path_ssh_config, 0o600)

        print("\n[+] Host updated")
        input("\nPress Enter...")

    def copy_pubkey_to_host(
        self,
        private_key_name: str,
        port: Optional[int] = None,
        user: Optional[str] = None,
        ip: Optional[str] = None,
    ) -> None:
        clear_console()
        print(self.logo())

        if not port and not user and not ip:
            while not self.set_host("port"):
                pass
            while not self.set_host("user"):
                pass
            while not self.set_host("ip"):
                pass

        print()

        ssh_dir = os.path.dirname(self.path_ssh_config)
        pubkey_path = os.path.join(ssh_dir, private_key_name + ".pub")

        if not os.path.isfile(pubkey_path):
            print(f"\n[!] Public key not found: {pubkey_path}")
            input("\nPress Enter...")
            return

        if self.is_windows():
            os.system(
                f"ssh -p {self.port_host} "
                f"{self.user_host}@{self.ip_host} "
                f'"mkdir -p ~/.ssh && chmod 700 ~/.ssh && '
                f'cat >> ~/.ssh/authorized_keys" '
                f'< "{pubkey_path}"'
            )
        else:
            os.system(
                f'ssh-copy-id -i "{pubkey_path}" '
                f"-p {self.port_host} "
                f"{self.user_host}@{self.ip_host}"
            )

        input("\nPress Enter...")

    def delete_ssh_backup(self, name: str) -> None:
        name = name.strip()
        if not name:
            print("\n[!] Empty backup name")
            return
        src = os.path.join(self.backup_dir, name)
        if not os.path.isfile(src):
            print("\n[!] Backup not found")
            return

        os.remove(src)
        print(f"\n[+] Deleted: {name}")

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

        if not self.is_windows():
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

        clear_console()
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

        clear_console()
        print(self.logo())

        if not blocks:
            print("[!] Not found")
            input("\nPress Enter...")
            return

        while True:
            clear_console()
            print(self.logo())

            print(f"[+] Found: {len(blocks)}\n")
            lines = (
                f"{idx}. {b.rstrip()}"
                for idx, b in enumerate(
                    blocks,
                    start=1,
                )
            )
            print("\n".join(lines))

            print("\nSelect host number (or 'q' to Back): ")
            ch = input("\n[>]: ").strip().lower()
            if ch == "q":
                return
            if not ch.isdigit():
                continue

            num = int(ch)
            if num < 1 or num > len(blocks):
                continue

            break

        selected = blocks[num - 1]

        while True:
            clear_console()
            print(self.logo())

            print("What do you want to do?")
            print("  e - Edit host")
            print("  d - Delete host")
            print("  q - Cancel")

            action = input("\n[>]: ").strip().lower()

            if action == "q":
                return

            if action == "e":
                self.change_host(selected)
                return

            if action == "d":
                clear_console()
                print(self.logo())

                with open(
                    self.path_ssh_config,
                    "r",
                    encoding="utf-8",
                    errors="replace",
                ) as f:
                    text = f.read()

                text = text.replace(selected, "", 1)

                with open(self.path_ssh_config, "w", encoding="utf-8") as f:
                    f.write(text)

                if not self.is_windows():
                    os.chmod(self.path_ssh_config, 0o600)

                print("[+] Host deleted")
                input("\nPress Enter...")
                return

    @require_ssh_config
    def open_editor(self) -> None:
        import os
        import shlex
        import shutil
        import subprocess

        path = self.path_ssh_config
        is_windows = os.name == "nt"

        editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")

        if not editor:
            if is_windows:
                editor = "notepad"
            else:
                for candidate in ("nvim", "vim", "vi", "nano"):
                    if shutil.which(candidate):
                        editor = candidate
                        break

        if not editor:
            print("\n[!] No editor available (set $EDITOR or $VISUAL)")
            input("\nPress Enter...")
            return

        if is_windows and editor.lower() == "notepad":
            cmd = [editor, path]
        else:
            cmd = shlex.split(editor) + [path]

        sys.stdout.flush()
        subprocess.call(cmd)

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
                self.port_host = int(port)
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
            clear_console()
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
    @require_ssh_private_key
    def add_menu(self) -> None:
        clear_console()
        print(self.logo())

        while not self.set_host("port"):
            pass
        while not self.set_host("user"):
            pass
        while not self.set_host("ip"):
            pass
        while not self.set_host("short_name"):
            pass

        private_keys: list[str] = self.get_ssh_private_key_list()

        if not private_keys:
            input("\nPress Enter...")
        else:
            while True:
                clear_console()
                print(self.logo())
                print(
                    "[+] Select Private Key to associate with this host "
                    "(or 'q' to skip):\n"
                )
                for idx, key in enumerate(private_keys, start=1):
                    print(f" {idx}. {key}")
                ch = input("\n[>]: ").strip().lower()
                if ch == "q":
                    break
                if not ch.isdigit():
                    continue

                num = int(ch)
                if num < 1 or num > len(private_keys):
                    continue

                selected_key = private_keys[num - 1]

                self.key_host = os.path.join(
                    os.path.dirname(self.path_ssh_config), selected_key
                )

                break

        while True:
            clear_console()
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
                continue
        while True:
            if self.key_host:
                clear_console()
                print(self.logo())
                print(
                    """Do you want to copy the public key to this host? (y/n)
    """.strip()
                )

                ch = input("\n[>]: ").strip().lower()

                if ch == "n":
                    return
                elif ch == "y":
                    self.copy_pubkey_to_host(
                        os.path.basename(self.key_host),
                        self.port_host,
                        self.user_host,
                        self.ip_host,
                    )
                    return
                else:
                    print("\n[!] Please enter y or n.")

    @require_ssh_config
    def menu_delete_backup(self) -> None:
        while True:
            clear_console()
            print(self.logo())

            backups = self.get_backup_list()
            if not backups:
                print("[!] No backups")
            else:
                print("[+] Backups:\n")
                for b in backups:
                    print(f" - {b}")

            print("\nEnter backup name to delete (or 'q' to Back): ")
            ch = input("\n[>]: ").strip()
            if ch.lower() == "q":
                break
            else:
                self.delete_ssh_backup(ch)
                input("\nPress Enter...")
                break

    @require_ssh_config
    def menu_backup_ssh(self) -> None:
        clear_console()
        print(self.logo())

        while True:
            clear_console()
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
            clear_console()
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
            "3. Delete SSH backup",
            "q. Back",
        ]

        while True:
            clear_console()
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
            elif ch == "3":
                self.menu_delete_backup()

    @require_ssh_config
    @require_ssh_private_key
    def copy_ssh_key_menu(self) -> None:

        while True:
            clear_console()
            print(self.logo())
            private_keys: list[str] = self.get_ssh_private_key_list()
            print("[+] Available SSH Private Keys:\n")
            for idx, key in enumerate(private_keys, start=1):
                print(f" {idx}. {key}")
            print("\nSelect private key number to copy (or 'q' to Back): ")
            ch = input("\n[>]: ").strip().lower()
            if ch == "q":
                break
            if not ch.isdigit():
                continue

            num = int(ch)
            if num < 1 or num > len(private_keys):
                continue

            selected_key = private_keys[num - 1]

            self.copy_pubkey_to_host(selected_key)

    def delete_config_menu(self) -> None:
        # menu: dict[str, tuple[str, Optional[Callable[[], None]]]] = {
        #     "y": ("/ n", self.add_menu),
        #     "n": ("Back", None),
        # }
        while True:
            clear_console()
            print(self.logo())
            msg = " ".join(
                [
                    "[!]",
                    "Are you sure you want to delete",
                    "the SSH config file? (y/n)",
                ]
            )
            print(msg)

            ch = input("\n[>]: ").strip().lower()
            if ch == "y":
                self.delete_ssh_config()
                input("\nPress Enter...")
                break
            elif ch == "n":
                break

    def main_menu(self) -> None:

        menu: dict[str, tuple[str, Optional[Callable[[], None]]]] = {
            "1": ("Add new host", self.add_menu),
            "2": ("Find host", self.find_menu),
            "3": ("Open config in editor", self.open_editor),
            "4": ("Backup/Restore SSH config", self.backup_restore_menu),
            "5": ("Manual copy SSH key to host", self.copy_ssh_key_menu),
            "6": ("Delete SSH config file", self.delete_config_menu),
            "q": ("Quit", None),
        }

        while True:
            clear_console()
            print(self.logo())

            for key, (title, _) in menu.items():
                print(f"{key}. {title}")

            ch = input("\n[>]: ").strip().lower()

            if ch not in menu:
                continue

            _, action = menu[ch]

            if action is None:
                break

            action()

    def main(self) -> None:
        self.main_menu()
        clear_console()


def main():
    app = ShortSSH()

    if len(sys.argv) == 1:
        app.main()

    args = sys.argv[1:]

    if args[0] in ("--list", "-l"):
        app.list_hosts_short_ip()
    elif args[0] in ("--help", "-h"):
        app.doc_help()
    else:
        app.not_valid_argument()


if __name__ == "__main__":
    main()
