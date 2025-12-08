# multiaccount.py — MULTI-ACCOUNT VERSION with ROTATING TASKS

import os
import time
import random
import json
import requests
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.align import Align
from pyfiglet import Figlet
from colorama import Fore, Style, init

# Init Colorama
init(autoreset=True)

# Global Config
BASE_URL = "https://almo.up.railway.app"
CONFIG_FILE = "config.json"
ACCOUNTS_FILE = "accounts.txt"
LOGS = []

# Console Rich Init
console = Console()

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print("[bold red]❌ Config file not found![/bold red]")
        exit()

def load_accounts():
    accounts = []
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" not in line:
                    continue
                parts = line.strip().split("|")
                if len(parts) < 3:
                    continue
                fid, username, wallet = parts[0], parts[1], parts[2]
                accounts.append({
                    "fid": int(fid),
                    "username": username,
                    "wallet": wallet
                })
    except FileNotFoundError:
        console.print("[bold red]❌ Accounts file not found![/bold red]")
        exit()
    return accounts

config = load_config()
accounts = load_accounts()


class AlmoClient:
    def __init__(self, acc):
        self.acc = acc
        self.fid = acc["fid"]
        self.username = acc["username"]
        self.headers = {
            "authority": "almo.up.railway.app",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://almo.up.railway.app",
            "referer": "https://almo.up.railway.app/dashboard",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }

    def log(self, message, type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if type == "success":
            icon = "✅"
            color = "green"
        elif type == "error":
            icon = "❌"
            color = "red"
        elif type == "warning":
            icon = "⚠️"
            color = "yellow"
        else:
            icon = "ℹ️"
            color = "cyan"

        entry = f"[{timestamp}] {icon} [{self.username}] {message}"
        LOGS.insert(0, entry)
        if len(LOGS) > 20:
            LOGS.pop()

    def get_dashboard(self):
        url = f"{BASE_URL}/api/proxy/casts/dashboard?page=1&limit=20&filter=standard&sort=desc"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("casts", [])
            else:
                self.log(f"Failed to get dashboard: HTTP {resp.status_code}", "error")
                return []
        except Exception as e:
            self.log(f"Error fetching dashboard: {str(e)}", "error")
            return []

    def get_balance(self):
        url = f"{BASE_URL}/api/proxy/balance/{self.fid}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            else:
                self.log(f"Failed to get balance: HTTP {resp.status_code}", "error")
                return None
        except Exception as e:
            self.log(f"Error getting balance: {str(e)}", "error")
            return None

    def hub_action(self, action_type, target_hash, target_fid):
        url = f"{BASE_URL}/api/proxy/farcaster/hub-action"
        payload = {
            "actionType": action_type,
            "targetHash": target_hash,
            "targetFid": str(target_fid),
            "fid": self.fid
        }
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("success", False)
            else:
                self.log(f"Hub action failed: HTTP {resp.status_code}", "error")
                return False
        except Exception as e:
            self.log(f"Error in hub action: {str(e)}", "error")
            return False

    def follow_user(self, target_fid, cast_hash):
        url = f"{BASE_URL}/api/proxy/casts/follow"
        payload = {
            "fid": self.fid,
            "followingFid": str(target_fid),
            "castHash": cast_hash
        }
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("success", False)
            else:
                self.log(f"Follow failed: HTTP {resp.status_code}", "error")
                return False
        except Exception as e:
            self.log(f"Error following: {str(e)}", "error")
            return False

    def reply_cast(self, parent_hash, target_fid):
        url = f"{BASE_URL}/api/proxy/casts/reply"
        text_reply = random.choice(config.get("custom_reply", ["LFG!"]))
        payload = {
            "fid": self.fid,
            "text": text_reply,
            "parentCastHash": parent_hash,
            "targetFid": str(target_fid)
        }
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("success", False)
            else:
                self.log(f"Reply failed: HTTP {resp.status_code}", "error")
                return False
        except Exception as e:
            self.log(f"Error replying: {str(e)}", "error")
            return False


# ==============================
# UI FIXED & STABILIZED SECTION
# ==============================

def make_header():
    f = Figlet(font="slant", width=110)
    text = f.renderText("Airdrop 888")

    grid = Table.grid(expand=True)
    grid.add_column(justify="center")
    grid.add_row(Text(text, style="bold cyan"))
    grid.add_row(
        Text("Multi Account Bot | All Accounts Working Together",
             style="bold white on blue", justify="center")
    )

    return Panel(grid, border_style="cyan", padding=(0,1))


def make_layout():
    layout = Layout()

    layout.split(
        Layout(name="header", size=6),
        Layout(name="body")
    )

    layout["body"].split_row(
        Layout(name="left", ratio=1, minimum_size=60),
        Layout(name="right", ratio=1, minimum_size=60)
    )
    return layout


def generate_stats_table(all_stats):
    table = Table(
        title="🤖 ALL ACCOUNT STATISTICS",
        expand=True,
        border_style="green",
        padding=(0, 1)
    )

    table.add_column("Username", style="cyan", no_wrap=True)
    table.add_column("FID", style="magenta")
    table.add_column("Active Tasks", style="yellow")
    table.add_column("Likes", style="blue")
    table.add_column("Recasts", style="red")
    table.add_column("Follows", style="green")
    table.add_column("Replies", style="purple")

    for stats in all_stats:
        table.add_row(
            str(stats.get('username', 'N/A')),
            str(stats.get('fid', 'N/A')),
            str(stats.get('active_tasks', 0)),
            str(stats.get('likes', 0)),
            str(stats.get('recasts', 0)),
            str(stats.get('follows', 0)),
            str(stats.get('replies', 0))
        )

    return Panel(table, border_style="green", padding=(1,1))


def generate_log_panel():
    log_text = Text("\n".join(LOGS), overflow="fold")
    return Panel(
        log_text,
        title="📜 LIVE LOGS",
        border_style="yellow",
        padding=(1, 1)
    )


# ==============================
# PROCESS ONE CAST FOR ONE ACCOUNT
# ==============================

def process_one_cast_for_account(client, stats, processed_casts, stats_layout, log_layout):
    casts = client.get_dashboard()

    if not casts:
        client.log("No casts found or error fetching.", "warning")
        return False  # Tidak ada cast untuk diproses

    for cast in casts:
        cast_hash = cast.get("castHash")
        author = cast.get("author", {})
        target_fid = author.get("fid")
        username = author.get("username")

        if not cast_hash or cast_hash in processed_casts:
            continue

        reward = cast.get("reward", {})
        if not reward.get("isActive"):
            continue

        client.log(f"Processing cast by @{username}", "info")
        log_layout.update(generate_log_panel())

        # LIKE
        if config.get("do_like"):
            if client.hub_action("like", cast_hash, target_fid):
                stats["likes"] += 1
                client.log(f"Liked cast {cast_hash[:8]}...", "success")
            else:
                client.log(f"Failed to like {cast_hash[:8]}", "error")
            time.sleep(random.uniform(1, 3))
            stats_layout.update(generate_stats_table([stats]))  # Update hanya untuk akun ini sementara

        # RECAST
        if config.get("do_recast"):
            if client.hub_action("recast", cast_hash, target_fid):
                stats["recasts"] += 1
                client.log(f"Recasted {cast_hash[:8]}...", "success")
            time.sleep(random.uniform(1, 3))
            stats_layout.update(generate_stats_table([stats]))

        # FOLLOW
        if config.get("do_follow"):
            if client.follow_user(target_fid, cast_hash):
                stats["follows"] += 1
                client.log(f"Followed @{username}", "success")
            time.sleep(random.uniform(1, 3))
            stats_layout.update(generate_stats_table([stats]))

        # REPLY
        if config.get("do_reply"):
            if client.reply_cast(cast_hash, target_fid):
                stats["replies"] += 1
                client.log(f"Replied to @{username}", "success")
            time.sleep(random.uniform(1, 3))
            stats_layout.update(generate_stats_table([stats]))

        processed_casts.add(cast_hash)

        delay = random.randint(config['delay_min'], config['delay_max'])
        client.log(f"Sleeping for {delay} seconds...", "warning")
        log_layout.update(generate_log_panel())
        time.sleep(delay)

        # Jika berhasil memproses satu cast, keluar dari loop
        return True

    # Jika tidak ada cast yang bisa diproses
    return False


# ==============================
# MAIN EXECUTION - ROTATING MODE
# ==============================

def main():
    # Inisialisasi client dan stats untuk setiap akun
    clients = []
    stats_list = []
    processed_casts_list = []

    for acc in accounts:
        clients.append(AlmoClient(acc))
        stats_list.append({
            "username": acc["username"],
            "fid": acc["fid"],
            "active_tasks": 0,
            "likes": 0,
            "recasts": 0,
            "follows": 0,
            "replies": 0
        })
        processed_casts_list.append(set())

    layout = make_layout()
    stats_layout = layout["left"]
    log_layout = layout["right"]

    with Live(layout, refresh_per_second=4, screen=True) as live:
        while True:
            # Perbarui header
            layout["header"].update(make_header())

            # Perbarui panel statistik awal
            stats_layout.update(generate_stats_table(stats_list))

            # Ambil saldo awal untuk semua akun
            for i, client in enumerate(clients):
                balance_info = client.get_balance()
                if balance_info:
                    stats_list[i]['active_tasks'] = balance_info.get('activeTasksCount', 0)

            # Perbarui panel statistik setelah ambil saldo
            stats_layout.update(generate_stats_table(stats_list))

            # Jalankan satu putaran: setiap akun memproses satu cast
            for i, client in enumerate(clients):
                client.log(f"Starting turn for {client.username}", "info")
                success = process_one_cast_for_account(
                    client, stats_list[i], processed_casts_list[i], stats_layout, log_layout
                )
                if success:
                    client.log(f"Finished turn for {client.username}", "success")
                else:
                    client.log(f"No more casts to process for {client.username}", "warning")

            # Setelah semua akun selesai satu putaran, perbarui panel statistik terakhir
            stats_layout.update(generate_stats_table(stats_list))

            # Tandai bahwa satu siklus telah selesai
            LOGS.insert(
                0,
                f"[{datetime.now().strftime('%H:%M:%S')}] ✅ ONE CYCLE COMPLETE — WAIT 60s"
            )
            log_layout.update(generate_log_panel())  # Perbarui log panel juga
            time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Bot stopped by user!{Style.RESET_ALL}")