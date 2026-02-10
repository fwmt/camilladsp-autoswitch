"""
Media Policy Handler.

Responsabilidade:
- Traduzir eventos de atividade de mídia em PolicyDecision
- NÃO contém regras de negócio
- NÃO possui defaults
- NÃO interpreta significado de perfis

Toda a lógica vem do MediaMapping.
"""

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.events import MediaActivityChanged, PolicyDecision
from camilladsp_autoswitch.mapping.media import MediaMapping


class MediaPolicyHandler:
    """
    Boundary entre detecção de eventos e decisão de política.

    Regras:
    - Stateless
    - Determinístico
    - Mapping é a única fonte de verdade
    """

    def __init__(self, bus: EventBus, *, mapping: MediaMapping):
        self._bus = bus
        self._mapping = mapping

        self._bus.subscribe(
            MediaActivityChanged,
            self._on_media_activity_changed,
        )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_media_activity_changed(
        self,
        event: MediaActivityChanged,
    ) -> None:
        """
        Recebe evento de atividade de mídia e emite PolicyDecision.
        """

        selection = self._mapping.select(
            media_active=event.active
        )

        decision = PolicyDecision(
            profile=selection.profile,
            variant=selection.variant,
            reason=(
                "media_active"
                if event.active
                else "media_inactive"
            ),
        )

        self._bus.publish(decision)
