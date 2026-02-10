"""
Command-line interface for camilladsp-autoswitch.

Design principles:
- Thin CLI (no business logic)
- Explicit errors, no stacktraces for users
- All filesystem paths resolved via config layer
"""

import argparse
import sys
from pathlib import Path

from camilladsp_autoswitch.infrastructure.runtime_state import load_state, update_state
from camilladsp_autoswitch.infrastructure.filesystem.paths import get_config_dir

from camilladsp_autoswitch.registry.profiles import ProfileRegistry
from camilladsp_autoswitch.registry.errors import ProfileRegistryError
from camilladsp_autoswitch.validators.camilladsp_validator import (
    CamillaDSPBinaryValidator,
)

from camilladsp_autoswitch.application.services.mapping_service import MediaMappingService
from camilladsp_autoswitch.domain.mapping import MappingError


# =============================================================================
# Status / Mode
# =============================================================================

def cmd_status(_args):
    state = load_state()
    print("CamillaDSP Autoswitch status:\n")
    for field, value in state.__dict__.items():
        print(f"{field:16}: {value}")


def cmd_auto(_args):
    update_state(mode="auto")
    print("Mode set to AUTO")


def cmd_manual(_args):
    update_state(mode="manual")
    print("Mode set to MANUAL")


def cmd_profile(args):
    allowed = ("music", "cinema")
    if args.name not in allowed:
        sys.exit(f"Invalid profile '{args.name}'. Use: {', '.join(allowed)}")

    update_state(profile=args.name)
    print(f"Profile set to {args.name}")


def cmd_variant(args):
    update_state(variant=args.name)
    print(f"Variant set to {args.name}")


# =============================================================================
# Experimental YAML
# =============================================================================

def cmd_experimental_on(args):
    yml = Path(args.file).expanduser().resolve()
    if not yml.exists():
        sys.exit(f"YAML file not found: {yml}")

    update_state(experimental_yml=str(yml))
    print(f"Experimental YAML enabled: {yml}")


def cmd_experimental_off(_args):
    update_state(experimental_yml=None)
    print("Experimental YAML disabled")


# =============================================================================
# Profile registry
# =============================================================================

def cmd_profile_add(args):
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
        for line in str(exc).splitlines():
            print(f"  {line}")
        sys.exit(1)

    if args.variant:
        print(f"Profile '{args.name}.{args.variant}' registered")
    else:
        print(f"Profile '{args.name}' registered")


# =============================================================================
# Mapping
# =============================================================================

def cmd_mapping_init(args):
    service = MediaMappingService()
    try:
        service.init(force=args.force)
        print("mapping.yml created successfully")
    except MappingError as exc:
        print(str(exc))


def cmd_mapping_show(_args):
    service = MediaMappingService()
    try:
        print(service.show())
    except MappingError as exc:
        print(str(exc))


def cmd_mapping_validate(_args):
    service = MediaMappingService()
    try:
        service.validate()
        print("mapping.yml is valid")
    except MappingError as exc:
        print(str(exc))


def cmd_mapping_test(args):
    service = MediaMappingService()
    try:
        result = service.test(media_active=args.state == "on")
        print(result)
    except MappingError as exc:
        print(str(exc))


# =============================================================================
# Argument parser
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdspctl",
        description="Control CLI for CamillaDSP Autoswitch",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # status
    p = sub.add_parser("status", help="Show current runtime state")
    p.set_defaults(func=cmd_status)

    # mode
    p = sub.add_parser("auto", help="Enable automatic mode")
    p.set_defaults(func=cmd_auto)

    p = sub.add_parser("manual", help="Enable manual mode")
    p.set_defaults(func=cmd_manual)

    # profile
    p = sub.add_parser("profile", help="Select base profile")
    p.add_argument("name")
    p.set_defaults(func=cmd_profile)

    # variant
    p = sub.add_parser("variant", help="Select profile variant")
    p.add_argument("name")
    p.set_defaults(func=cmd_variant)

    # experimental
    p = sub.add_parser("experimental", help="Manage experimental YAML")
    exp = p.add_subparsers(dest="exp_cmd", required=True)

    p_on = exp.add_parser("on", help="Enable experimental YAML")
    p_on.add_argument("file")
    p_on.set_defaults(func=cmd_experimental_on)

    p_off = exp.add_parser("off", help="Disable experimental YAML")
    p_off.set_defaults(func=cmd_experimental_off)

    # profile add
    p = sub.add_parser("profile-add", help="Register a CamillaDSP YAML profile")
    p.add_argument("name")
    p.add_argument("file")
    p.add_argument("--variant")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_profile_add)

    # mapping
    p = sub.add_parser("mapping", help="Manage media mapping")
    m = p.add_subparsers(dest="mapping_cmd", required=True)

    p_init = m.add_parser("init", help="Create default mapping.yml")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=cmd_mapping_init)

    p_show = m.add_parser("show", help="Show mapping.yml")
    p_show.set_defaults(func=cmd_mapping_show)

    p_val = m.add_parser("validate", help="Validate mapping.yml")
    p_val.set_defaults(func=cmd_mapping_validate)

    p_test = m.add_parser("test", help="Test mapping resolution")
    p_test.add_argument("state", choices=("on", "off"))
    p_test.set_defaults(func=cmd_mapping_test)

    return parser


# =============================================================================
# Entry point
# =============================================================================

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
        return 0
    except PermissionError as exc:
        print(f"Permission error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
