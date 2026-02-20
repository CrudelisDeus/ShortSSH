#!/usr/bin/env python3

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
        self.notes_host: str | None = None
        self.client_port_forward: int | None = None
        self.local_port_forward: int | None = None
        self.host_group: str | None = None

        self.path_ssh_config = os.path.expanduser("~/.ssh/config")
        self.program_dir = os.path.dirname(os.path.abspath(__file__))
        self.backup_dir = os.path.join(self.program_dir, "backups")

        self.add_forward: bool = False

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
    def version(self) -> None:
        version = self.version_app.strip()
        if version.startswith("."):
            version = version[1:]
        print(f"{self.name_app} version: {version}")

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
                if not s:
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
    def sort_ssh_config(self) -> None:
        import re

        with open(
            self.path_ssh_config,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:
            lines = f.readlines()

        re_group = re.compile(r"^\s*#\s*G\s*:\s*(.+?)\s*$", re.IGNORECASE)

        prelude: list[str] = []
        i = 0
        while i < len(lines) and not lines[i].lstrip().lower().startswith(
            "host ",
        ):
            prelude.append(lines[i])
            i += 1

        groups: dict[str, list[tuple[str, list[str]]]] = {}
        pending_group: str | None = None

        def host_name_of(block: list[str]) -> str:
            first = block[0].strip()
            parts = first.split()
            return parts[1] if len(parts) > 1 else ""

        while i < len(lines):
            m = re_group.match(lines[i])
            if m:
                name = m.group(1).strip().lower()
                pending_group = name if name else None
                i += 1
                continue

            if not lines[i].lstrip().lower().startswith("host "):
                i += 1
                continue

            block: list[str] = []
            # attach group comment right above the host block (normalized)
            group = pending_group or "Ungrouped"
            if pending_group:
                block.append(f"# G: {pending_group}\n")
            pending_group = None

            while i < len(lines):
                line_low = lines[i].lstrip().lower()
                if re_group.match(lines[i]) or line_low.startswith("host "):
                    if block and block[-1].lstrip().lower().startswith(
                        "host ",
                    ):
                        pass
                if re_group.match(lines[i]):
                    break
                if (
                    lines[i].lstrip().lower().startswith("host ")
                    and block
                    and any(
                        ln.lstrip()
                        .lower()
                        .startswith(
                            "host ",
                        )
                        for ln in block
                    )
                ):
                    break
                block.append(lines[i])
                i += 1

            name = host_name_of(
                block[1:]
                if block
                and block[0]
                .lstrip()
                .startswith(
                    "#",
                )
                else block
            )
            groups.setdefault(group, []).append((name, block))

        ordered_group_names = sorted(
            (g for g in groups.keys() if g != "Ungrouped"),
        )
        if "Ungrouped" in groups:
            ordered_group_names.append("Ungrouped")

        out: list[str] = []
        out.extend(prelude)

        if out and out[-1].strip() != "":
            out.append("\n")

        for g in ordered_group_names:
            blocks = groups[g]
            blocks.sort(key=lambda x: x[0].lower())
            for _, b in blocks:
                out.extend(b)
                if out and out[-1].strip() != "":
                    out.append("\n")

        with open(self.path_ssh_config, "w", encoding="utf-8") as f:
            f.writelines(out)

        if not self.is_windows():
            os.chmod(self.path_ssh_config, 0o600)

    def reset_add_host_data(self) -> None:
        self.add_forward = False

    def not_valid_argument(self) -> None:
        print(self.logo())
        print("[!] Invalid argument. Use --help or -h.\n")

    def doc_help(self) -> None:
        print(self.logo())
        print("Usage:\n")

        rows = [
            ("sssh", "Run interactive menu"),
            ("sssh --version OR sssh -v", "Show version"),
            ("sssh --list OR sssh -l", "Print hosts as: shortname, ip, port"),
            ("sssh --help OR sssh -h", "Show this help"),
            (
                "sssh --list-group OR -lg <group>",
                "List hosts in group with IP and Port",
            ),
            ("sssh <ssh args>", "Run ssh with provided arguments"),
        ]

        w = max(len(cmd) for cmd, _ in rows)

        for cmd, desc in rows:
            print(f"  {cmd.ljust(w)}   {desc}")

        print()

    def list_hosts_short_ip_group(self, group_name: str) -> None:
        group_name = group_name.strip()
        if not group_name:
            print("[!] Group name is empty. Example: sssh -lg Test")
            return

        if not os.path.isfile(self.path_ssh_config):
            print(f"[!] SSH config not found: {self.path_ssh_config}")
            return

        import re

        groups: dict[str, list[tuple[str, str, str, str]]] = {}

        cur_host: str | None = None
        cur_ip: str | None = None
        cur_port: str | None = None
        cur_notes: str | None = None
        cur_group: str = "Ungrouped"

        pending_group: str | None = None
        re_group = re.compile(r"^\s*#\s*G\s*:\s*(.+?)\s*$", re.IGNORECASE)

        def push() -> None:
            nonlocal cur_host, cur_ip, cur_port, cur_notes, cur_group
            if cur_host:
                row = (
                    cur_host,
                    cur_ip or "-",
                    cur_port or "22",
                    cur_notes or "-",
                )
                groups.setdefault(cur_group, []).append(row)
            cur_host = None
            cur_ip = None
            cur_port = None
            cur_notes = None
            cur_group = "Ungrouped"

        with open(
            self.path_ssh_config,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:
            for line in f:
                raw = line.rstrip("\n")
                s = raw.strip()

                m = re_group.match(raw)
                if m:
                    name = m.group(1).strip()
                    pending_group = name if name else None
                    continue

                if not s:
                    continue

                low = s.lower()

                if low.startswith("host "):
                    push()
                    parts = s.split()
                    cur_host = parts[1] if len(parts) > 1 else None
                    cur_group = pending_group or "Ungrouped"
                    pending_group = None
                    continue

                if cur_host and low.startswith("hostname "):
                    cur_ip = s.split(None, 1)[1].strip()
                    continue

                if cur_host and low.startswith("port "):
                    cur_port = s.split(None, 1)[1].strip()
                    continue

                if cur_host and s.startswith("#"):
                    c = s[1:].strip()
                    c_low = c.lower()
                    if c_low.startswith("notes:"):
                        cur_notes = c.split(":", 1)[1].strip()
                    elif c_low.startswith("notes "):
                        cur_notes = c.split(None, 1)[1].strip()

        push()

        hosts = groups.get(group_name)

        if not hosts:
            if group_name in groups:
                print(f"[!] Group '{group_name}' exists but has no hosts")
            else:
                print(f"[!] Group '{group_name}' not found")
            return

        print(self.logo())

        w_name = max(len("Name"), max(len(r[0]) for r in hosts))
        w_ip = max(len("IP"), max(len(r[1]) for r in hosts))
        w_port = max(len("Port"), max(len(r[2]) for r in hosts))
        w_notes = max(len("Notes"), max(len(r[3]) for r in hosts))

        header = (
            "| "
            + f"{'Name'.ljust(w_name)} | {'IP'.ljust(w_ip)} | "
            + f"{'Port'.ljust(w_port)} | {'Notes'.ljust(w_notes)} |"
        )
        line = "=" * len(header)

        def print_group_row(name: str) -> None:
            inner_width = len(header) - 4
            text = f"Group: {name}"
            print("| " + text.ljust(inner_width) + " |")

        print(line)
        print(header)
        print(line)
        print_group_row(group_name)
        print(line)

        for name, ip, port, notes in hosts:
            row = (
                "| "
                + f"{name.ljust(w_name)} | {ip.ljust(w_ip)} | "
                + f"{port.ljust(w_port)} | {notes.ljust(w_notes)} |"
            )
            print(row)

        print(line + "\n")

    def list_hosts_short_ip(self) -> None:
        if not os.path.isfile(self.path_ssh_config):
            print(f"[!] SSH config not found: {self.path_ssh_config}")
            return

        import re

        groups: dict[str, list[tuple[str, str, str, str]]] = {}

        cur_host: str | None = None
        cur_ip: str | None = None
        cur_port: str | None = None
        cur_notes: str | None = None
        cur_group: str = "Ungrouped"

        pending_group: str | None = None
        re_group = re.compile(r"^\s*#\s*G\s*:\s*(.+?)\s*$", re.IGNORECASE)

        def push() -> None:
            nonlocal cur_host, cur_ip, cur_port, cur_notes, cur_group
            if cur_host:
                row = (
                    cur_host,
                    cur_ip or "-",
                    cur_port or "22",
                    cur_notes or "-",
                )
                groups.setdefault(cur_group, []).append(row)
            cur_host = None
            cur_ip = None
            cur_port = None
            cur_notes = None
            cur_group = "Ungrouped"

        with open(
            self.path_ssh_config,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:
            for line in f:
                raw = line.rstrip("\n")
                s = raw.strip()

                m = re_group.match(raw)
                if m:
                    name = m.group(1).strip()
                    pending_group = name if name else None
                    continue

                if not s:
                    continue

                low = s.lower()

                if low.startswith("host "):
                    push()
                    parts = s.split()
                    cur_host = parts[1] if len(parts) > 1 else None
                    cur_group = pending_group or "Ungrouped"
                    pending_group = None
                    continue

                if cur_host and low.startswith("hostname "):
                    cur_ip = s.split(None, 1)[1].strip()
                    continue

                if cur_host and low.startswith("port "):
                    cur_port = s.split(None, 1)[1].strip()
                    continue

                if cur_host and s.startswith("#"):
                    c = s[1:].strip()
                    c_low = c.lower()
                    if c_low.startswith("notes:"):
                        cur_notes = c.split(":", 1)[1].strip()
                    elif c_low.startswith("notes "):
                        cur_notes = c.split(None, 1)[1].strip()

        push()

        print(self.logo())

        if not groups:
            print("[!] No hosts in config")
            return

        order: list[str] = []
        if "Ungrouped" in groups:
            order.append("Ungrouped")
        order.extend(sorted(g for g in groups.keys() if g != "Ungrouped"))

        all_rows: list[tuple[str, str, str, str]] = []
        for g in order:
            all_rows.extend(groups.get(g, []))

        if not all_rows:
            print("[!] No hosts in config")
            return

        w_name = max(len("Name"), max(len(r[0]) for r in all_rows))
        w_ip = max(len("IP"), max(len(r[1]) for r in all_rows))
        w_port = max(len("Port"), max(len(r[2]) for r in all_rows))
        w_notes = max(len("Notes"), max(len(r[3]) for r in all_rows))

        header = (
            "| "
            + f"{'Name'.ljust(w_name)} | { 'IP'.ljust(w_ip) } | "
            + f"{'Port'.ljust(w_port)} | { 'Notes'.ljust(w_notes) } |"
        )
        line = "=" * len(header)

        def print_group_row(group_name: str) -> None:
            inner_width = len(header) - 4
            text = f"Group: {group_name}"
            print("| " + text.ljust(inner_width) + " |")

        print(line)
        print(header)
        print(line)

        for g in order:
            print_group_row(g)
            print(line)
            for name, ip, port, notes in groups.get(g, []):
                row = (
                    "| "
                    + f"{name.ljust(w_name)} | {ip.ljust(w_ip)} | "
                    + f"{port.ljust(w_port)} | {notes.ljust(w_notes)} |"
                )
                print(row)
            print(line)

        print()

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
        elif item == "forward_client_port":
            client_port = input("Enter Client Port: ")
            if self.check_host_port(client_port):
                self.client_port_forward = int(client_port)
            else:
                print("\n[!] Invalid Port format\n")
                return False
        elif item == "forward_local_port":
            local_port = input("Enter Local Port: ")
            if self.check_host_port(local_port):
                self.local_port_forward = int(local_port)
            else:
                print("\n[!] Invalid Port format\n")
                return False

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
        elif item == "notes":
            notes = input("Enter Notes (optional, Enter to skip): ").strip()
            self.notes_host = notes if notes else "-"
        elif item == "host_group":
            host_group = input(
                "Enter Host Group (optional, Enter to skip): ",
            ).strip()
            self.host_group = host_group.lower() if host_group else None

        return True

    # ------------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------------
    def select_add_menu(self) -> None:

        menu = [
            "1. Add standart host",
            "2. Add port forward host",
            "q. Back",
        ]

        while True:
            clear_console()
            print(self.logo())
            for item in menu:
                print(item)
            ch = input("\n[>]: ").strip().lower()
            if ch == "q":
                return
            elif ch == "1":
                break
            elif ch == "2":
                self.add_forward = True
                break

        self.add_menu()
        self.reset_add_host_data()

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
        while not self.set_host("notes"):
            pass
        while not self.set_host("host_group"):
            pass

        if self.add_forward:
            while not self.set_host("forward_client_port"):
                pass
            while not self.set_host("forward_local_port"):
                pass

        private_keys: list[str] = self.get_ssh_private_key_list()

        if not private_keys:
            input("\nPress Enter...")
        elif len(private_keys) == 1:
            selected_key = private_keys[0]
            self.key_host = os.path.join(
                os.path.dirname(self.path_ssh_config), selected_key
            )
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
            if self.host_group:
                print(f"    Group: {self.host_group}")
            print(f"    Port: {self.port_host}")
            print(f"    Username: {self.user_host}")
            print(f"    IP Address: {self.ip_host}")
            print(f"    Short Name: {self.short_name_host}")
            if self.key_host:
                print(f"    Key File: {self.key_host}")

            if self.notes_host:
                print(f"    Notes: {self.notes_host}")

            if self.add_forward:
                print(f"    Forward Client Port: {self.client_port_forward}")
                print(f"    Forward Local Port: {self.local_port_forward}")

            print("\nAre you sure you want to add this host? (y/n)")

            ch = input("\n[>]: ").strip().lower()
            if ch == "y":
                with open(self.path_ssh_config, "a") as f:
                    if self.host_group:
                        f.write(f"# G: {self.host_group}\n")
                    f.write(
                        f"""Host {self.short_name_host}
        HostName {self.ip_host}
        User {self.user_host}
        Port {self.port_host}
"""
                    )
                    if self.key_host:
                        f.write(f"        IdentityFile {self.key_host}\n")
                    if self.notes_host:
                        f.write(f"        # Notes: {self.notes_host}\n")
                    if self.add_forward:
                        f.write(
                            f"        LocalForward {self.local_port_forward} "
                            f"localhost:{self.client_port_forward}\n"
                        )
                break
            elif ch == "n":
                return
            else:
                print("\n[!] Please enter y or n.")
                continue
        while True:
            if not self.key_host:
                return

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

    @require_ssh_config
    def backup_restore_menu(self) -> None:

        menu = [
            "1. Backup SSH config",
            "2. Restore SSH config",
            "3. Delete SSH backup",
            "4. Delete SSH config",
            "5. Sort SSH config (by work group)",
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
            elif ch == "4":
                self.delete_config_menu()
            elif ch == "5":
                self.sort_ssh_config()

    @require_ssh_config
    @require_ssh_private_key
    def copy_ssh_key_menu(self) -> None:

        while True:
            clear_console()
            print(self.logo())
            private_keys: list[str] = self.get_ssh_private_key_list()

            if not private_keys:
                print("[!] No SSH private keys found")
                input("\nPress Enter...")
                return

            if len(private_keys) == 1:
                self.copy_pubkey_to_host(private_keys[0])
                return

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
            "1": ("Add new host", self.select_add_menu),
            # "2": ("Find host", self.find_menu),
            "2": ("Open config in editor", self.open_editor),
            "3": (
                "Backup/Restore/Delete/Sort SSH config",
                self.backup_restore_menu,
            ),
            "4": ("Manual copy SSH key to host", self.copy_ssh_key_menu),
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
        return

    args = sys.argv[1:]

    if args[0] in ("--list", "-l"):
        app.list_hosts_short_ip()
    elif args[0] in ("--help", "-h"):
        app.doc_help()
    elif args[0] in ("--version", "-v"):
        app.version()
    elif args[0] in ("--list-group", "-lg"):
        if len(args) < 2:
            print("[!] Usage: sssh -lg <group>")
            return
        group_name = " ".join(args[1:]).strip()
        if not group_name:
            print("[!] Usage: sssh -lg <group>")
            return
        app.list_hosts_short_ip_group(group_name)

    else:
        os.system("ssh " + " ".join(args))


if __name__ == "__main__":
    main()
