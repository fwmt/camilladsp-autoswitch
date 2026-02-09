class PollingMediaActivitySource:
    def __init__(self, detector):
        self._detector = detector

    def start(self) -> None:
        # mantém loop apenas aqui
        while True:
            self._detector.poll()
