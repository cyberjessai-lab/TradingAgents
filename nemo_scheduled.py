#!/usr/bin/env python3
"""
Nemo Boost Scheduled Council
Runs the trading council every hour Mon-Fri during market hours.
Weekend: data gathering only, no council debate.
"""

import time
import os
import sys
from datetime import datetime

# Must be in the TradingAgents directory
os.chdir("/home/cylon/TradingAgents")

from dotenv import load_dotenv
load_dotenv()

from nemo_runner import run_council, log, send_telegram_sync
from nemo_config import NEMO_ASSETS

SCAN_INTERVAL = 60 * 60  # 1 hour
PRIORITY_ASSETS = ["GOLD", "SILVER", "OIL"]  # Always scan these
FULL_SCAN_ASSETS = list(NEMO_ASSETS.keys())   # All 7 assets

def is_market_hours():
    """Check if Nemo Boost markets are open (Mon-Fri, roughly)."""
    now = datetime.now()
    # Nemo CFDs trade Mon-Fri (crypto 24/7 but we follow the same schedule)
    return now.weekday() < 5  # 0=Mon, 4=Fri

def main():
    log("=== Nemo Scheduled Council Starting ===")
    send_telegram_sync("*Nemo Trading Council* is online. Scanning every hour Mon-Fri.")

    cycle = 0
    while True:
        try:
            now = datetime.now()

            if not is_market_hours():
                log(f"Weekend — markets closed. Sleeping until Monday.")
                # Sleep until next check
                time.sleep(SCAN_INTERVAL)
                continue

            cycle += 1

            # Every 4th cycle: full scan (all 7 assets)
            # Otherwise: priority assets only (GOLD, SILVER, OIL)
            if cycle % 4 == 0:
                log(f"Cycle {cycle}: Full scan (all assets)")
                run_council(FULL_SCAN_ASSETS)
            else:
                log(f"Cycle {cycle}: Priority scan (GOLD, SILVER, OIL)")
                run_council(PRIORITY_ASSETS)

        except Exception as e:
            log(f"Council error: {e}")
            import traceback
            traceback.print_exc()

        log(f"Next scan in {SCAN_INTERVAL // 60} minutes")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
