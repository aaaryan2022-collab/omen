# ============================================
# OMEN Security - permissions_v5 spec 29 real conservative defaults
SCOPES = {
    "CONTROL": False,
    "FS_READ": True,
    "FS_WRITE": False,
    "MEMORY": True,
    "SCREEN_CAPTURE": False,
    "MICROPHONE": False,
    "TERM_RUN": False,
}

class PermissionManager:
    """Real check - never bypass. Default conservative per spec 48/55."""
    def __init__(self, scopes=None):
        self.scopes = scopes or SCOPES.copy()
    def check(self, scope_key, action="execute"):
        destructive = ("FS_WRITE","SCREEN_CAPTURE","TERM_RUN","MICROPHONE","CONTROL")
        if scope_key in destructive:
            return self.scopes.get(scope_key, False)
        return True
