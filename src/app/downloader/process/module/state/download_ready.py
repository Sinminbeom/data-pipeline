from python_library.state import abState


class DownloadReadyState(abState):
    """PlayableList 성공 후 다음 명령(InrPlayReq)을 기다리는 상태.

    Phase 1: 진입만 수행. 후속 명령 라우팅은 module.handle_play_request에서.
    """

    def on_enter(self): pass
    def on_leave(self): pass
    def on_proc_once(self): pass
    def on_proc_every_frame(self): pass
