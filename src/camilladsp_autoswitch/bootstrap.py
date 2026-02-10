"""
Application bootstrap.

Responsibilities:
- Wire the event-driven pipeline
- Load infrastructure dependencies
- Inject domain objects into handlers

Rules:
- No domain logic here
- Fail fast in production
- Be test-friendly via dependency injection
"""

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.event_store import EventStore
from camilladsp_autoswitch.event_store_subscriber import EventStoreSubscriber
from camilladsp_autoswitch.media_activity_detector import MediaActivityDetector
from camilladsp_autoswitch.media_policy_handler import MediaPolicyHandler
from camilladsp_autoswitch.intent_handler import IntentHandler
from camilladsp_autoswitch.intent_executor_handler import IntentExecutorHandler
from camilladsp_autoswitch.autoswitch import apply_yaml, resolve_yaml_path
from camilladsp_autoswitch.validator import validate

from camilladsp_autoswitch.mapping.media import MediaMapping, ProfileSelection
from camilladsp_autoswitch.mapping.loader import load_media_mapping


def _fallback_mapping() -> MediaMapping:
    """
    In-memory fallback mapping.

    Used ONLY when:
    - running tests
    - mapping.yml is not present

    Production installations MUST provide a mapping file.
    """
    return MediaMapping(
        on=ProfileSelection(profile="cinema", variant=None),
        off=ProfileSelection(profile="music", variant=None),
    )


def bootstrap(
    *,
    resolve_yaml=resolve_yaml_path,
    validate_fn=validate,
    apply_fn=apply_yaml,
    enable_event_store: bool = True,
    replay_on_start: bool = True,
    media_processes=None,
    mapping: MediaMapping | None = None,
) -> EventBus:
    """
    Build and wire the full autoswitch event-driven pipeline.
    """

    # -----------------------------
    # Core
    # -----------------------------
    bus = EventBus()

    # -----------------------------
    # Event store (optional)
    # -----------------------------
    if enable_event_store:
        store = EventStore()
        EventStoreSubscriber(bus, store)
        bus.event_store = store  # test-friendly hook

    # -----------------------------
    # Media mapping (REQUIRED)
    # -----------------------------
    if mapping is None:
        try:
            mapping = load_media_mapping(allow_fallback=True)
        except Exception:
            # Test / development fallback
            mapping = _fallback_mapping()

    # -----------------------------
    # Handlers (pure reactions)
    # -----------------------------
    MediaPolicyHandler(bus, mapping=mapping)
    IntentHandler(bus)
    IntentExecutorHandler(
        bus,
        resolve_yaml=resolve_yaml,
        validate=validate_fn,
        apply=apply_fn,
    )

    # -----------------------------
    # Event source (event-driven)
    # -----------------------------
    MediaActivityDetector(
        bus,
        media_processes=media_processes,
    )

    # -----------------------------
    # Replay (after wiring!)
    # -----------------------------
    if replay_on_start and enable_event_store:
        bus.event_store.replay(bus)

    return bus
