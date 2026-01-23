class ApplicationException(Exception):
    def __init__(
        self,
        message: str,
        retries: int | None = None,
        causes: list[BaseException | None] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.retries = retries
        self.causes = causes


class AgentLoopError(ApplicationException):
    pass


class ModelImportError(ApplicationException):
    pass
