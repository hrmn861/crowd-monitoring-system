"""
Unit Tests for Alert State Machine and Hysteresis Logic
"""

import pytest

class AlertStateMachine:
    def __init__(self, threshold: int, persistence_s: int, cooldown_s: int):
        self.threshold = threshold
        self.persistence_s = persistence_s
        self.cooldown_s = cooldown_s
        self.state = "idle" # idle, pending, active, cooldown
        self.pending_duration = 0
        self.cooldown_remaining = 0

    def step(self, current_count: int, dt_s: int) -> str:
        if self.state == "cooldown":
            self.cooldown_remaining -= dt_s
            if self.cooldown_remaining <= 0:
                self.state = "idle"
                self.cooldown_remaining = 0
            return self.state

        if current_count >= self.threshold:
            if self.state == "idle":
                self.state = "pending"
                self.pending_duration = dt_s
            elif self.state == "pending":
                self.pending_duration += dt_s
                if self.pending_duration >= self.persistence_s:
                    self.state = "active"
        else:
            if self.state == "pending":
                # Condition ceased before persistence satisfied -> revert to idle
                self.state = "idle"
                self.pending_duration = 0
            elif self.state == "active":
                # Resolves -> enter cooldown
                self.state = "cooldown"
                self.cooldown_remaining = self.cooldown_s

        return self.state

def test_alert_requires_persistence():
    asm = AlertStateMachine(threshold=50, persistence_s=60, cooldown_s=300)
    
    # 1. Transient spike below persistence
    assert asm.step(current_count=55, dt_s=10) == "pending"
    assert asm.step(current_count=55, dt_s=20) == "pending"
    # Drops below threshold -> clears without triggering alert
    assert asm.step(current_count=40, dt_s=10) == "idle"

def test_alert_triggers_when_persisted():
    asm = AlertStateMachine(threshold=50, persistence_s=60, cooldown_s=300)
    asm.step(current_count=55, dt_s=30)
    assert asm.step(current_count=55, dt_s=30) == "active"
    
    # Clears -> enters cooldown
    assert asm.step(current_count=42, dt_s=1) == "cooldown"
    # While in cooldown, spikes do not fire
    assert asm.step(current_count=60, dt_s=100) == "cooldown"
