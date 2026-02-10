"""
Command-line interface for camilladsp-autoswitch.

This CLI is intentionally THIN.

Responsibilities:
- Parse user intent
- Validate user input (lightweight)
- Delegate state changes to flags.py
- Present clear, user-friendly output

Non-responsibilities:
- Business logic
- Validation of DSP/YAML internals
- Direct interaction with CamillaDSP
"""

import argparse
import sys
from pathlib import Path

from camilladsp_autoswitch.flags import load_state, update_state
from camilladsp_autoswitch.registry.profiles import ProfileRegistry
from camilladsp_autoswitch.validators.camilladsp_validator import (
    CamillaDSPBinaryValidator,
)
from camilladsp_autoswitch.config.paths import get_config_dir
from camilladsp_autoswitch.registry.errors import ProfileRegistryError


# ============================================================================
# Command implementations
# ============================================================================

def cmd_status(_args):
    """
    Show the current runtime state.
    Read-only operation (never fails due to permissions).
    """
    state = load_state()
    print("CamillaDSP Autoswitch status:\n")
    for field, value in state.__dict__.items():
        print(f"{field:16}: {value}")


def cmd_auto(_args):
    """
    Enable automatic mode.
    """
    update_state(mode="auto")
    print("Mode set to AUTO")


def cmd_manual(_args):
    """
    Enable manual mode.
    """
    update_state(mode="manual")
    print("Mode set to MANUAL")


def cmd_profile(args):
    """
    Select base profile (music / cinema).
    """
    allowed = ("music", "cinema")
    if args.name not in allowed:
        sys.exit(f"Invalid profile '{args.name}'. Use: {', '.join(allowed)}")

    update_state(profile=args.name)
    print(f"Profile set to {args.name}")


def cmd_variant(args):
    """
    Select profile variant (normal / night / lowlevel).
    """
    update_state(variant=args.name)
    print(f"Variant set to {args.name}")


def cmd_experimental_on(args):
    """
    Enable experimental YAML override.
    """
    yml = Path(args.file).expanduser().resolve()

    if not yml.exists():
        sys.exit(f"YAML file not found: {yml}")

    update_state(experimental_yml=str(yml))
    print(f"Experimental YAML enabled: {yml}")


def cmd_experimental_off(_args):
    """
    Disable experimental YAML override.
    """
    update_state(experimental_yml=None)
    print("Experimental YAML disabled")

def cmd_profile_add(args):
    """
    Register a validated CamillaDSP YAML profile.
    """
    registry = ProfileRegistry(
        get_config_dir(),
        validator=CamillaDSPBinaryValidator(),
    )

    try:
        registry.add(
            name=args.name,
            variant=args.variant,
            source_path=Path(args.file),
            force=args.force,
        )
    except ProfileRegistryError as exc:
        print(f"✖ Failed to register profile '{args.name}'\n")

        print("Reason:")
        print("  CamillaDSP rejected the configuration\n")

        print("Details:")
        for line in str(exc).splitlines():
            print(f"  {line}")

        sys.exit(1)

    if args.variant:
        print(f"Profile '{args.name}.{args.variant}' registered")
    else:
        print(f"Profile '{args.name}' registered")


# ============================================================================
# Argument parser construction
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the CLI argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="cdspctl",
        description="Control CLI for CamillaDSP Autoswitch",
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands",
    )

    # Status
    p = sub.add_parser("status", help="Show current runtime state")
    p.set_defaults(func=cmd_status)

    # Mode selection
    p = sub.add_parser("auto", help="Enable automatic mode")
    p.set_defaults(func=cmd_auto)

    p = sub.add_parser("manual", help="Enable manual mode")
    p.set_defaults(func=cmd_manual)

    # Profile
    p = sub.add_parser("profile", help="Manage audio profiles")
    profile_sub = p.add_subparsers(
        dest="profile_cmd",
        required=True,
    )

    # profile add
    p_add = profile_sub.add_parser(
        "add",
        help="Register a CamillaDSP YAML profile",
    )
    p_add.add_argument("name", help="Profile name (e.g. music, cinema)")
    p_add.add_argument("file", help="Path to YAML file")
    p_add.add_argument(
        "--variant",
        help="Optional profile variant (e.g. night)",
    )
    p_add.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing profile",
    )
    p_add.set_defaults(func=cmd_profile_add)

    # Variant
    p = sub.add_parser("variant", help="Select profile variant")
    p.add_argument("name", help="normal | night | lowlevel")
    p.set_defaults(func=cmd_variant)

    # Experimental YAML handling
    p = sub.add_parser("experimental", help="Manage experimental YAML override")
    exp = p.add_subparsers(
        dest="exp_cmd",
        required=True,
    )

    p_on = exp.add_parser("on", help="Enable experimental YAML")
    p_on.add_argument("file", help="Path to YAML file")
    p_on.set_defaults(func=cmd_experimental_on)

    p_off = exp.add_parser("off", help="Disable experimental YAML")
    p_off.set_defaults(func=cmd_experimental_off)

    return parser


# ============================================================================
# Entry point
# ============================================================================

def main():
    """
    CLI entry point.

    Handles:
    - argument parsing
    - graceful error reporting (no stacktraces for users)
    """
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except PermissionError as e:
        # Friendly message for common DEV/PROD mistake
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
