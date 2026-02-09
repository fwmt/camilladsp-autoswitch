class LoggingSubscriber:
    """
    Logs every published event with semantic clarity.
    """

    def __init__(self, bus, logger):
        self._logger = logger
        bus.subscribe(object, self._log)

    def _log(self, event):
        self._logger.info(
            f"Event {event.__class__.__name__} published"
        )
