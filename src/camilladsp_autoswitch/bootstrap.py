from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.event_store import EventStore
from camilladsp_autoswitch.event_store_subscriber import EventStoreSubscriber
from camilladsp_autoswitch.media_activity_detector import MediaActivityDetector
from camilladsp_autoswitch.media_policy_handler import MediaPolicyHandler
from camilladsp_autoswitch.intent_handler import IntentHandler
from camilladsp_autoswitch.intent_executor_handler import IntentExecutorHandler
from camilladsp_autoswitch.autoswitch import apply_yaml, resolve_yaml_path
from camilladsp_autoswitch.validator import validate


def bootstrap(
    *,
    resolve_yaml=resolve_yaml_path,
    validate_fn=validate,
    apply_fn=apply_yaml,
    enable_event_store: bool = True,
    replay_on_start: bool = True,
    media_processes=None,
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
    # Handlers (pure reactions)
    # -----------------------------
    MediaPolicyHandler(bus)
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
