class ProtocolOwner:
    DELIM = "/"

    @staticmethod
    def build(app_name: str, process_name: str | None = None) -> str:
        if process_name is None:
            return str(app_name)
        return f"{app_name}{ProtocolOwner.DELIM}{process_name}"

    @staticmethod
    def get_app_name(owner: str) -> str:
        return owner.split(ProtocolOwner.DELIM)[0]

    @staticmethod
    def is_owner(owner: str, app_name: str, process_name: str | None = None) -> bool:
        parts = owner.split(ProtocolOwner.DELIM)
        if parts[0] != app_name:
            return False
        if len(parts) > 1 and process_name is not None:
            return parts[1] == process_name
        return True
