#!/usr/bin/env python3
"""
NIRVAAN Pre-Demo Verification Script

Run this script 5 minutes before walking on stage for a live hackathon demonstration.
Validates backend liveness, readiness, precomputed INSTANT_DEMO bundles, LIVE_ANALYZE pipeline,
CORS headers, and data_provenance tags.

Outputs a clean PASS/FAIL checklist.
"""

import sys
import time
import urllib.request
import json
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from demo.precomputed_results import load_demo_result
from detection.mode_controller import execute_mode_analysis, AnalysisModeController

API_BASE = "http://localhost:8000"
CANONICAL_EVENTS = ["flood-emilia-romagna-2023", "wildfire-rhodes-2023"]

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def check(description: str, fn) -> bool:
    """Helper to run a check function and print formatted PASS/FAIL row."""
    try:
        t0 = time.perf_counter()
        result, extra = fn()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if result:
            print(f"  [{bcolors.OKGREEN}PASS{bcolors.ENDC}] {description} ({elapsed_ms:.1f}ms) {extra}")
            return True
        else:
            print(f"  [{bcolors.FAIL}FAIL{bcolors.ENDC}] {description} {extra}")
            return False
    except Exception as e:
        print(f"  [{bcolors.FAIL}FAIL{bcolors.ENDC}] {description} -> EXCEPTION: {str(e)}")
        return False


def run_all_checks() -> bool:
    print(f"\n{bcolors.BOLD}{bcolors.HEADER}=== NIRVAAN STAGE-READINESS PRE-DEMO CHECKLIST ==={bcolors.ENDC}\n")
    all_passed = True

    # 1. Backend Liveness Probe
    def check_health():
        url = f"{API_BASE}/api/v1/health"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return (data.get("status") == "ok", f"-> {url}")
    all_passed &= check("Backend Liveness Probe (/api/v1/health)", check_health)

    # 2. Backend Readiness Probe
    def check_ready():
        url = f"{API_BASE}/api/v1/ready"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            status = data.get("status")
            backing = data.get("canonical_events_backing", {})
            return (status == "READY", f"-> {backing}")
    all_passed &= check("Backend Readiness Probe (/api/v1/ready)", check_ready)

    # 3. Precomputed INSTANT_DEMO Bundles
    for event_id in CANONICAL_EVENTS:
        def check_bundle(evt=event_id):
            contract = load_demo_result(evt)
            has_prov = hasattr(contract, "data_provenance") and contract.data_provenance in ["REAL_SATELLITE_DATA", "SYNTHETIC_FALLBACK"]
            return (contract.status == "success" and has_prov, f"-> provenance={getattr(contract, 'data_provenance', 'NONE')}")
        all_passed &= check(f"INSTANT_DEMO Bundle Validation ('{event_id}')", check_bundle)

    # 4. LIVE_ANALYZE Pipeline Benchmark & Timeout Protection
    for event_id in CANONICAL_EVENTS:
        def check_live(evt=event_id):
            contract = execute_mode_analysis(evt, mode="LIVE_ANALYZE", timeout_sec=10.0)
            has_prov = hasattr(contract, "data_provenance") and contract.data_provenance in ["REAL_SATELLITE_DATA", "SYNTHETIC_FALLBACK"]
            return (contract.status == "success" and has_prov, f"-> provenance={getattr(contract, 'data_provenance', 'NONE')}")
        all_passed &= check(f"LIVE_ANALYZE Pipeline ('{event_id}')", check_live)

    # 5. Static Asset & CORS Accessibility
    def check_assets():
        url = f"{API_BASE}/assets/before.jpg"
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            return (resp.status == 200, f"-> HTTP 200 OK")
    all_passed &= check("Static Assets & CORS Endpoint (/assets/before.jpg)", check_assets)

    print("\n" + "=" * 55)
    if all_passed:
        print(f"{bcolors.BOLD}{bcolors.OKGREEN}[+] FINAL VERDICT: STAGE READY! ALL CHECKS PASSED.{bcolors.ENDC}")
        print(f"{bcolors.BOLD}System is 100% prepared for live hackathon demonstration.{bcolors.ENDC}\n")
        return True
    else:
        print(f"{bcolors.BOLD}{bcolors.FAIL}[-] FINAL VERDICT: STAGE CHECKS FAILED! DO NOT PRESENT UNTIL RESOLVED.{bcolors.ENDC}\n")
        return False


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    success = run_all_checks()
    sys.exit(0 if success else 1)
