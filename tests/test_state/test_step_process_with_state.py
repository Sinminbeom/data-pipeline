from src.common.process.step_process import StepProcess
from src.common.state.state import abState
from src.common.state.state_container import StateContainer

class TestState1(abState):
    def __init__(self, container: StateContainer) -> None:
        super().__init__(container)

    def on_enter(self):
        print("TestState1 enter")
        pass

    def on_leave(self):
        print("TestState1 leave")
        pass

    def on_proc_once(self):
        print("TestState1 on_proc_once")
        state_component = self.get_state_component()
        # parent_class: TestProcess = state_component.get_parent_class()
        state_component.change_state("t2")
        pass

    def on_proc_every_frame(self):
        print("TestState1 on_proc_every_frame")
        pass


class TestState2(abState):
    def __init__(self, container: StateContainer):
        super().__init__(container)

    def on_enter(self):
        print("TestState2 on_enter")
        pass

    def on_leave(self):
        print("TestState2 on_leave")
        pass

    def on_proc_once(self):
        print("TestState2 on_proc_once")
        pass

    def on_proc_every_frame(self):
        print("TestState2 on_proc_every_frame")
        pass

class TestContainer(StateContainer):
    def __init__(self):
        super().__init__({
            "t1": TestState1(self),
            "t2": TestState2(self)
        })

class TestProcess(StepProcess):
    def __init__(self, iterations: int):
        super().__init__(app_name="app", process_name="proc")
        self._iterations = iterations
        self._tick = 0

    def is_running(self) -> bool:
        # iterations 만큼만 loop
        if self._tick < self._iterations:
            self._tick += 1
            return True
        return False

    def stop(self):
        # StepProcess.action except에서 호출될 수 있으니 no-op
        pass

    def on_init(self):
        pass

    def on_proc_once(self):
        pass

    def on_proc_every_frame(self):
        pass


def test_step_process_runs_state_every_iteration():
    p = TestProcess(iterations=1)
    p.set_state_component(TestContainer(), init_state_key="t1")


    p.action()
