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

    def logo(self) -> str:
        logo = rf"""
  / _ \
\_\(_)/_/ {self.name_app} v{self.version_app}
 _//o\\_  {self.github_url}
  /   \
"""
        return logo

    # ------------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------------
    def main_menu(self) -> None:
        import os

        menu = [
            "1. Find host",
            "2. Add new host",
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

    def main(self) -> None:
        self.main_menu()


if __name__ == "__main__":
    app = ShortSSH()
    app.main()
