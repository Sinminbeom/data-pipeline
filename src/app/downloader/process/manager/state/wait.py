from common.state.state import abState


class WaitState(abState):
    def on_enter(self, owner, machine): pass
    def on_leave(self, owner, machine): pass
    def on_proc_once(self, owner, machine): pass
    def on_proc_every_frame(self, owner, machine): pass
