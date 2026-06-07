#!/usr/bin/env python3
"""Inspect, print, probe, and launch macOS real Chrome CDP sessions."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


STABLE = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BETA = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"


@dataclass(frozen=True)
class ChromeProcess:
    pid: str
    variant: str
    profile: str | None
    port: str | None


def default_profile(variant: str) -> str:
    if variant == "beta":
        return str(Path.home() / ".real-agent-browser-beta")
    return str(Path.home() / ".real-agent-browser")


def executable_for(variant: str) -> str:
    return BETA if variant == "beta" else STABLE


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def launch_command(variant: str, profile: str, port: int, url: str) -> list[str]:
    return [
        executable_for(variant),
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile}",
        url,
    ]


def printable_command(argv: list[str]) -> str:
    return " ".join(shell_quote(part) for part in argv)


def detect_processes() -> list[ChromeProcess]:
    result = subprocess.run(
        ["ps", "-axo", "pid=,command="],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    processes: list[ChromeProcess] = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        pid, _, command = stripped.partition(" ")
        if STABLE in command:
            variant = "stable"
        elif BETA in command:
            variant = "beta"
        else:
            continue
        profile_match = re.search(r"--user-data-dir(?:=|\s+)(\"[^\"]+\"|'[^']+'|\S+)", command)
        port_match = re.search(r"--remote-debugging-port(?:=|\s+)(\d+)", command)
        profile = profile_match.group(1).strip("\"'") if profile_match else None
        port = port_match.group(1) if port_match else None
        processes.append(ChromeProcess(pid, variant, profile, port))
    return processes


def profile_warning(variant: str, profile: str) -> str | None:
    normalized = profile.lower()
    has_beta = "beta" in normalized
    if variant == "beta" and not has_beta:
        return "WARNING: Chrome Beta selected with a non-beta-looking profile directory."
    if variant == "stable" and has_beta:
        return "WARNING: Stable Chrome selected with a beta-looking profile directory."
    return None


def print_status() -> int:
    processes = detect_processes()
    if not processes:
        print("No stable Chrome or Chrome Beta processes found.")
        return 0
    for proc in processes:
        print(f"{proc.variant}: pid={proc.pid}")
        print(f"  profile={proc.profile or '(none)'}")
        print(f"  remote_debugging_port={proc.port or '(none)'}")
    return 0


def probe(port: int) -> int:
    url = f"http://127.0.0.1:{port}/json/version"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"CDP probe failed on port {port}: {exc}", file=sys.stderr)
        return 1
    print(payload.get("Browser", "(unknown browser)"))
    print(payload.get("User-Agent", "(unknown user agent)"))
    return 0


def wait_for_cdp(port: int, timeout: float = 12.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def command_action(args: argparse.Namespace) -> int:
    profile = os.path.expanduser(args.profile or default_profile(args.variant))
    warning = profile_warning(args.variant, profile)
    if warning:
        print(warning, file=sys.stderr)
    argv = launch_command(args.variant, profile, args.port, args.url)
    print(printable_command(argv))
    return 0


def launch(args: argparse.Namespace) -> int:
    profile = os.path.expanduser(args.profile or default_profile(args.variant))
    executable = executable_for(args.variant)
    if not Path(executable).exists():
        print(f"Chrome executable not found: {executable}", file=sys.stderr)
        return 1
    if not Path(profile).exists():
        print(f"Profile directory not found: {profile}", file=sys.stderr)
        return 1

    selected_running = [proc for proc in detect_processes() if proc.variant == args.variant]
    if selected_running:
        print(f"{args.variant} Chrome is already running. Close it and rerun after user says OK.", file=sys.stderr)
        for proc in selected_running:
            print(f"  pid={proc.pid} profile={proc.profile or '(none)'} port={proc.port or '(none)'}", file=sys.stderr)
        return 2

    warning = profile_warning(args.variant, profile)
    if warning:
        print(warning, file=sys.stderr)

    argv = launch_command(args.variant, profile, args.port, args.url)
    print("Launching:")
    print(printable_command(argv))
    process = subprocess.Popen(
        argv,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    if not wait_for_cdp(args.port):
        print(f"Chrome launched with pid={process.pid}, but CDP did not answer on port {args.port}.", file=sys.stderr)
        return 1
    print(f"Success: {args.variant} Chrome pid={process.pid} is accessible on CDP port {args.port}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="show running stable Chrome and Chrome Beta processes")
    status.set_defaults(func=lambda _args: print_status())

    probe_parser = sub.add_parser("probe", help="probe an existing CDP endpoint")
    probe_parser.add_argument("--port", type=int, default=9222)
    probe_parser.set_defaults(func=lambda args: probe(args.port))

    for name, func in (("command", command_action), ("launch", launch)):
        command_parser = sub.add_parser(name, help=f"{name} real Chrome")
        command_parser.add_argument("--variant", choices=("stable", "beta"), default="stable")
        command_parser.add_argument("--profile", help="explicit user data directory")
        command_parser.add_argument("--port", type=int, default=9222)
        command_parser.add_argument("--url", default="https://www.booking.com")
        command_parser.set_defaults(func=func)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
