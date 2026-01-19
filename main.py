import os
from functools import wraps
from typing import Any, Callable, Optional


def require_ssh_config(
    func: Callable[..., Any],
) -> Callable[..., Optional[Any]]:
    @wraps(func)
    def wrapper(self: "ShortSSH", *args: Any, **kwargs: Any) -> Optional[Any]:
        if not os.path.exists(self.path_ssh_config):
            os.system("cls" if os.name == "nt" else "clear")
            print(self.logo())
            print(f"[!] SSH config file not found: {self.path_ssh_config}")
            print("\n[!] Create SSH config file? (y/n)")
            ch = input("\n" "[>]: ").strip().lower()

            if ch == "y":
                with open(self.path_ssh_config, "w") as f:
                    print("[+] Creating SSH config file...")
                    f.write(
                        """-------------------
# ShortSSH Config #
-------------------
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

        self.path_ssh_config = os.path.expanduser("~/.ssh/config")

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

    # ------------------------------------------------------------------------
    # functionality
    # ------------------------------------------------------------------------
    def set_host(self, item: str) -> bool:
        if item == "ip":
            ip = input("Enter IP Address: ")
            if self.check_host_ip(ip):
                self.ip_host = ip
            else:
                print("[!] Invalid IP address format")
                return False
        elif item == "port":
            port = input("Enter Port: ")
            if not port:
                port = "22"
            if self.check_host_port(port):
                self.port_host = port
            else:
                print("[!] Invalid Port format")
                return False
        elif item == "user":
            user = input("Enter Username: ")
            if not user:
                import getpass

                user = getpass.getuser()
            self.user_host = user
        elif item == "short_name":
            self.short_name_host = input("Enter Short Name: ")
        return True

    # ------------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------------
    @require_ssh_config
    def add_menu(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")
        print(self.logo())

        self.set_host("port")
        self.set_host("user")
        self.set_host("ip")
        self.set_host("short_name")

        # print(self.ip_host)
        # print(self.port_host)
        # print(self.user_host)
        # print(self.short_name_host)

        # input("\nPress Enter to continue...")

    def main_menu(self) -> None:

        menu = [
            "1. Add new host",
            "2. Find host",
            "3. Open config in editor",
            "4. View config ssh",
            "q. Quit",
        ]

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print(self.logo())
            for item in menu:
                print(item)
            ch = input("\n[>]: ").strip().lower()
            if ch == "q":
                break
            elif ch == "1":
                self.add_menu()

    def main(self) -> None:
        self.main_menu()


if __name__ == "__main__":
    app = ShortSSH()
    app.main()
