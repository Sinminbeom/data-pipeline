import pytest
from enum import Enum
from typing import Dict

from src.common.state.state import abState
from src.common.state.state_container import StateContainer
from src.common.state.state_machine import StateMachine


# ============================================================
# Test Domain
# ============================================================

class PlayerState(Enum):
    IDLE = "IDLE"
    RUN = "RUN"


class Player:
    def __init__(self) -> None:
        self.input_x = 0.0
        self.speed = 0.0
        self.log: list[str] = []


# ============================================================
# Container Helper
# ============================================================

class PlayerStateContainer(StateContainer[Player, PlayerState]):
    def __init__(self, idle_state: abState[Player, PlayerState], run_state: abState[Player, PlayerState]) -> None:
        states: Dict[PlayerState, abState[Player, PlayerState]] = {
            PlayerState.IDLE: idle_state,
            PlayerState.RUN: run_state,
        }
        super().__init__(states)


# ============================================================
# 1) Transition in on_proc_once()
#    IDLE.once에서 RUN으로 즉시 전이
# ============================================================

class IdleState_ChangeToRun_InOnce(abState[Player, PlayerState]):
    def on_enter(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.enter")
        owner.speed = 0.0

    def on_leave(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.leave")

    def on_proc_once(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.once")
        machine.change(PlayerState.RUN)

    def on_proc_every_frame(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.tick")


class RunState_Basic(abState[Player, PlayerState]):
    def on_enter(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("RUN.enter")
        owner.speed = 5.0

    def on_leave(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("RUN.leave")

    def on_proc_once(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("RUN.once")

    def on_proc_every_frame(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("RUN.tick")


def test_change_in_on_proc_once_skips_old_tick_and_runs_new_once_and_tick_same_update():
    """
    Policy(B) expectation:
      - IDLE.once 중 전이 발생 -> IDLE.tick은 나오면 안 됨
      - 같은 update에서 RUN.once + RUN.tick이 실행되어야 함
    """
    player = Player()
    container = PlayerStateContainer(
        idle_state=IdleState_ChangeToRun_InOnce(),
        run_state=RunState_Basic(),
    )
    machine = StateMachine(player, container, PlayerState.IDLE)

    machine.update()

    assert player.log == [
        "IDLE.enter",
        "IDLE.once",
        "IDLE.leave",
        "RUN.enter",
        "RUN.once",
        "RUN.tick",
    ]
    assert player.speed == 5.0


# ============================================================
# 2) Transition in on_proc_every_frame()
#    IDLE.tick에서 RUN으로 전이
# ============================================================

class IdleState_ChangeToRun_InTick(abState[Player, PlayerState]):
    def on_enter(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.enter")
        owner.speed = 0.0

    def on_leave(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.leave")

    def on_proc_once(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.once")

    def on_proc_every_frame(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.tick")
        machine.change(PlayerState.RUN)


def test_change_in_on_proc_every_frame_applies_after_tick_and_new_state_runs_next_update():
    """
    tick 도중 전이는 '그 tick 자체'는 이미 실행되었으므로 IDLE.tick은 남는다.
    그리고 현재 update() 구현은 tick에서 change가 일어나도 새 상태 tick을 같은 프레임에 더 실행하지 않는다.
    => 다음 update에서 RUN.once + RUN.tick.
    """
    player = Player()
    container = PlayerStateContainer(
        idle_state=IdleState_ChangeToRun_InTick(),
        run_state=RunState_Basic(),
    )
    machine = StateMachine(player, container, PlayerState.IDLE)

    machine.update()  # IDLE.once + IDLE.tick(여기서 change) + IDLE.leave + RUN.enter
    machine.update()  # RUN.once + RUN.tick

    assert player.log == [
        "IDLE.enter",
        "IDLE.once",
        "IDLE.tick",
        "IDLE.leave",
        "RUN.enter",
        "RUN.once",
        "RUN.tick",
    ]
    assert player.speed == 5.0


# ============================================================
# 3) Transition in on_enter()
#    IDLE.enter에서 즉시 RUN으로 전이
# ============================================================

class IdleState_ChangeToRun_InEnter(abState[Player, PlayerState]):
    def on_enter(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.enter")
        owner.speed = 0.0
        machine.change(PlayerState.RUN)

    def on_leave(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.leave")

    def on_proc_once(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.once")

    def on_proc_every_frame(self, owner: Player, machine: StateMachine[Player, PlayerState]) -> None:
        owner.log.append("IDLE.tick")


def test_change_in_on_enter_happens_before_first_update_runs_in_run_immediately():
    """
    __init__에서 initial change(IDLE) -> IDLE.enter 내부에서 즉시 change(RUN) 발생.
    따라서 첫 update는 RUN 상태에서 시작:
      - RUN.once + RUN.tick
    """
    player = Player()
    container = PlayerStateContainer(
        idle_state=IdleState_ChangeToRun_InEnter(),
        run_state=RunState_Basic(),
    )
    machine = StateMachine(player, container, PlayerState.IDLE)

    machine.update()

    assert player.log == [
        "IDLE.enter",
        "IDLE.leave",
        "RUN.enter",
        "RUN.once",
        "RUN.tick",
    ]
    assert player.speed == 5.0
