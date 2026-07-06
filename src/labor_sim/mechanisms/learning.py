"""
LearningMechanism：在崗者學習 g + 失業者再訓練 retrain_rate + ability_ceiling 飽和邏輯。
掛鉤：post_step——需要當步配對完的 emp_mask 才能決定誰用 g、誰用 retrain_rate。
實際成長邏輯委派給 Human.grow()（避免邏輯散落兩處）。
"""

from __future__ import annotations


class LearningMechanism:
    def pre_match(self, world, t: int) -> None:
        pass  # no-op：學習不影響本步任務生成/配對

    def post_step(self, world, t: int) -> None:
        world.human.grow(world.last_emp_mask)
