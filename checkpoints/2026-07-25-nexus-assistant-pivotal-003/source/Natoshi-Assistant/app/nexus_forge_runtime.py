#!/usr/bin/env python3
"""Effect-injected runtime bridge for the ordered LOOM Forge review.

The cryptographic/state module prepares work orders but performs no network
I/O. This bridge accepts one caller-owned review function, invokes it in the
only legal order, and feeds the returned untrusted JSON through the Forge
validators. It still cannot write, commit, push, merge, or publish.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from nexus_forge import (
    ForgeMessage,
    LoomSession,
    ReviewSeat,
    build_deepseek_work_order,
    build_second_review_work_order,
    record_deepseek_review,
    record_second_review,
    render_forge_candidate,
    validate_forge_candidate,
)


ReviewCaller = Callable[[ReviewSeat, tuple[ForgeMessage, ...]], str]


@dataclass(frozen=True)
class ForgeRunResult:
    session: LoomSession
    candidate: str
    call_order: tuple[str, str]


def run_ordered_forge_review(
    session: LoomSession,
    *,
    deepseek_seat: ReviewSeat,
    higher_seat: ReviewSeat,
    call_review: ReviewCaller,
) -> ForgeRunResult:
    """Run DeepSeek first and one distinct, higher-ranked external review."""

    session, first_order = build_deepseek_work_order(
        session,
        deepseek_seat,
    )
    first_output = call_review(first_order.seat, first_order.messages)
    session = record_deepseek_review(
        session,
        first_order.seat,
        first_output,
    )

    session, second_order = build_second_review_work_order(
        session,
        higher_seat,
    )
    second_output = call_review(second_order.seat, second_order.messages)
    session = record_second_review(
        session,
        second_order.seat,
        second_output,
    )
    session = validate_forge_candidate(session)
    return ForgeRunResult(
        session=session,
        candidate=render_forge_candidate(session),
        call_order=(first_order.seat.seat_id, second_order.seat.seat_id),
    )

