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

# Global Config — DIPERBAIKI: hapus spasi ekstra di BASE_URL
BASE_URL = "https://almo.up.railway.app"
CONFIG_FILE = "config.json"
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

config = load_config()


class AlmoClient:
    def __init__(self):
        # DIPERBAIKI: hapus spasi ekstra di origin & referer
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
        self.fid = config.get("fid")

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

        entry = f"[{timestamp}] {icon} [{color}]{message}[/{color}]"
        LOGS.insert(0, entry)
        if len(LOGS) > 20:
            LOGS.pop()

    def get_dashboard(self):
        url = f"{BASE_URL}/api/proxy/casts/dashboard?page=1&limit=20&filter=standard&sort=desc"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    casts = data.get("casts", [])
                    self.log(f"Fetched {len(casts)} casts from dashboard", "info")
                    return casts
                except json.JSONDecodeError:
                    self.log("Failed to parse dashboard JSON", "error")
                    return []
            else:
                self.log(f"Dashboard returned status {resp.status_code}: {resp.text[:100]}", "error")
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
                self.log(f"Balance API error: {resp.status_code}", "warning")
                return None
        except Exception as e:
            self.log(f"Balance fetch error: {str(e)}", "warning")
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
                result = resp.json()
                success = result.get("success", False)
                if success:
                    self.log(f"✅ {action_type.upper()} succeeded on {target_hash[:8]} (FID: {target_fid})", "success")
                else:
                    self.log(f"❌ {action_type.upper()} failed: {result.get('message', 'No message')}", "error")
                return success
            else:
                self.log(f"Hub action {action_type} HTTP {resp.status_code}", "error")
                return False
        except Exception as e:
            self.log(f"Hub action {action_type} exception: {str(e)}", "error")
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
                result = resp.json()
                success = result.get("success", False)
                if success:
                    self.log(f"✅ Followed FID {target_fid}", "success")
                else:
                    self.log(f"❌ Follow failed: {result.get('message', 'No message')}", "error")
                return success
            else:
                self.log(f"Follow HTTP {resp.status_code}", "error")
                return False
        except Exception as e:
            self.log(f"Follow exception: {str(e)}", "error")
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
                result = resp.json()
                success = result.get("success", False)
                if success:
                    self.log(f"✅ Replied to {parent_hash[:8]}: '{text_reply}'", "success")
                else:
                    self.log(f"❌ Reply failed: {result.get('message', 'No message')}", "error")
                return success
            else:
                self.log(f"Reply HTTP {resp.status_code}", "error")
                return False
        except Exception as e:
            self.log(f"Reply exception: {str(e)}", "error")
            return False


# ==============================
# UI SECTION - STABIL
# ==============================

def make_header():
    # Generate the Figlet text once and store it as a static string
    f = Figlet(font="slant", width=110)
    figlet_text = f.renderText("Airdrop 888")

    # Calculate the height (number of lines) and width (max line length) of the Figlet text
    lines = figlet_text.splitlines()
    header_height = len(lines)
    header_width = max(len(line) for line in lines) if lines else 0

    # Create a Panel with fixed dimensions to prevent shifting
    # We add padding to ensure the text doesn't touch the border
    header_panel = Panel(
        Text(figlet_text, style="bold cyan"),
        title="",
        subtitle="",
        border_style="bold cyan",
        padding=(0, 1),  # Optional: adjust padding if needed
        width=header_width + 4,  # Add extra space for borders/padding
        height=header_height + 2  # Add extra space for borders/padding
    )

    # Add the author credit below the Figlet text within the same panel or as a separate element
    # Here, we'll add it as a separate row in a Grid for better control
    grid = Table.grid(expand=True)
    grid.add_column(justify="center")
    grid.add_row(header_panel)
    grid.add_row(
        Text("Script coded by - @balveerxyz || ALMO Bot",
             style="bold white on blue", justify="center")
    )

    return Panel(grid, border_style="cyan", padding=(0, 1))


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


def generate_stats_table(stats_data):
    table = Table(title="🤖 BOT STATISTICS", expand=True, border_style="green", padding=(0, 1))
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta", no_wrap=True)
    table.add_row("👤 Username", str(config.get('username', 'N/A')))
    table.add_row("🆔 FID", str(config.get('fid', 'N/A')))
    table.add_row("💰 Active Tasks", str(stats_data.get('active_tasks', 0)))
    table.add_row("👍 Likes Sent", str(stats_data.get('likes', 0)))
    table.add_row("🔁 Recasts", str(stats_data.get('recasts', 0)))
    table.add_row("👥 Follows", str(stats_data.get('follows', 0)))
    table.add_row("💬 Replies", str(stats_data.get('replies', 0)))
    return Panel(table, border_style="green", padding=(1, 1))


def generate_log_panel():
    display_logs = LOGS[:15] or ["[dim]No logs yet...[/dim]"]
    log_text = Text("\n".join(display_logs), overflow="fold")
    return Panel(log_text, title="📜 LIVE LOGS", border_style="yellow", padding=(1, 1))


# ==============================
# MAIN LOOP
# ==============================

def main():
    client = AlmoClient()
    layout = make_layout()
    layout["header"].update(make_header())

    stats = {
        "likes": 0, "recasts": 0, "follows": 0,
        "replies": 0, "active_tasks": 0
    }

    processed_casts = set()

    with Live(layout, refresh_per_second=2, screen=True) as live:
        while True:
            # Update balance & stats
            balance_info = client.get_balance()
            if balance_info:
                stats['active_tasks'] = balance_info.get('activeTasksCount', 0)

            layout["left"].update(generate_stats_table(stats))
            layout["right"].update(generate_log_panel())

            client.log("🔄 Fetching dashboard tasks...", "info")
            casts = client.get_dashboard()

            if not casts:
                client.log("⚠️ No casts or error fetching dashboard.", "warning")
                time.sleep(30)
                continue

            for cast in casts:
                cast_hash = cast.get("castHash")
                author = cast.get("author", {})
                target_fid = author.get("fid")
                username = author.get("username")

                if not cast_hash or not target_fid:
                    client.log("⚠️ Invalid cast data, skipping.", "warning")
                    continue

                if cast_hash in processed_casts:
                    continue

                reward = cast.get("reward", {})
                if not reward.get("isActive", False):
                    continue

                client.log(f"🎯 Processing cast by @{username} (FID: {target_fid})", "info")
                layout["right"].update(generate_log_panel())

                # === LIKE ===
                if config.get("do_like", False):
                    if client.hub_action("like", cast_hash, target_fid):
                        stats["likes"] += 1
                    time.sleep(random.uniform(1.5, 2.5))
                    layout["left"].update(generate_stats_table(stats))

                # === RECAST ===
                if config.get("do_recast", False):
                    if client.hub_action("recast", cast_hash, target_fid):
                        stats["recasts"] += 1
                    time.sleep(random.uniform(1.5, 2.5))
                    layout["left"].update(generate_stats_table(stats))

                # === FOLLOW ===
                if config.get("do_follow", False):
                    if client.follow_user(target_fid, cast_hash):
                        stats["follows"] += 1
                    time.sleep(random.uniform(1.5, 2.5))
                    layout["left"].update(generate_stats_table(stats))

                # === REPLY ===
                if config.get("do_reply", False):
                    if client.reply_cast(cast_hash, target_fid):
                        stats["replies"] += 1
                    time.sleep(random.uniform(1.5, 2.5))
                    layout["left"].update(generate_stats_table(stats))

                processed_casts.add(cast_hash)

                delay = random.randint(config.get("delay_min", 10), config.get("delay_max", 20))
                client.log(f"⏳ Sleeping for {delay} seconds...", "warning")
                layout["right"].update(generate_log_panel())
                time.sleep(delay)

            client.log("✅ Cycle finished. Waiting 60s for next check...", "info")
            layout["right"].update(generate_log_panel())
            time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Bot stopped by user.[/bold red]")
        exit()