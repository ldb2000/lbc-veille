"""Orchestrateur de l'add-on : boucle scrape -> Supabase -> MQTT."""
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone

import lbc

import departments
import scraper
import state_store
from mqtt_client import MqttPublisher

STATE_FILE = "/data/state.json"


def parse_departements(raw):
    """Parse l'option 'departements' (JSON array ou liste vide)."""
    if not raw:
        return []
    try:
        value = json.loads(raw)
        return value if isinstance(value, list) else []
    except (ValueError, json.JSONDecodeError):
        return []


def main():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    pages = int(os.environ.get("PAGES", "2"))
    interval_h = int(os.environ.get("INTERVAL_HOURS", "1"))
    proxy_mode = os.environ.get("PROXY_MODE", "sans")
    brd_user = os.environ.get("BRD_USER", "")
    brd_pass = os.environ.get("BRD_PASS", "")
    stale_days = int(os.environ.get("MARK_STALE_DAYS", "7"))
    configured = parse_departements(os.environ.get("DEPARTEMENTS", ""))

    mqtt = MqttPublisher(
        os.environ.get("MQTT_HOST", "core-mosquitto"),
        os.environ.get("MQTT_PORT", "1883"),
        os.environ.get("MQTT_USER", ""),
        os.environ.get("MQTT_PASS", ""),
    )
    mqtt.connect()
    mqtt.publish_discovery()

    def shutdown(*_):
        mqtt.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    sb = scraper.make_supabase(url, key)
    proxy_url = scraper.get_proxy_url(proxy_mode, brd_user, brd_pass)
    client = scraper.make_lbc_client(proxy_url)
    metro = departments.all_metro()

    while True:
        cursor = state_store.load_cursor(STATE_FILE)
        if configured:
            targets = departments.resolve(lbc.Department, configured)
        else:
            idx = cursor % len(metro)
            targets = [metro[idx]]
            state_store.save_cursor(STATE_FILE, (idx + 1) % len(metro))

        print(f"--- RUN depts={[d.value[2] for d in targets]} ---")
        stats = scraper.run_scraper(sb, client, targets, pages=pages, proxy_mode=proxy_mode)

        try:
            scraper.mark_stale(sb, stale_days)
            total_active = scraper.count_active(sb)
        except Exception as exc:
            stats["errors"] += 1
            total_active = None
            print(f"Erreur Supabase stats: {exc}")

        payload = {
            "total_active": total_active,
            "new_last_run": stats["new"],
            "price_drops": stats["price_drops"],
            "last_run": datetime.now(timezone.utc).isoformat(),
            "status": "ok" if stats["ok"] and stats["errors"] == 0 else "error",
            "errors": stats["errors"],
            "duration_s": stats["duration_s"],
            "depts": stats["depts"],
        }
        mqtt.publish_state(payload)
        print(f"--- État publié: {payload} ---")
        time.sleep(interval_h * 3600)


if __name__ == "__main__":
    main()
