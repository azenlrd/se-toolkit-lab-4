"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_excludes_interaction_with_different_learner_id():
    # Interaction has item_id==1 but a different learner_id; filter should
    # match by item_id only and return this entry.
    interactions = [_make_log(1, 2, 1), _make_log(2, 1, 2)]
    result = _filter_by_item_id(interactions, 1)

    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].item_id == 1
    assert result[0].learner_id == 2


def test_filter_returns_all_matching_multiple_entries() -> None:
    # Multiple interactions refer to the same item_id; all should be returned
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 5),
        _make_log(3, 3, 5),
        _make_log(4, 4, 6),
    ]
    result = _filter_by_item_id(interactions, 5)
    assert len(result) == 3
    assert [i.id for i in result] == [1, 2, 3]


def test_filter_returns_empty_when_item_id_not_present() -> None:
    # No interaction has item_id 99
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 99)
    assert result == []


def test_filter_handles_zero_and_negative_item_ids() -> None:
    # Ensure exact equality works for zero and negative values
    interactions = [_make_log(1, 1, 0), _make_log(2, 2, -1), _make_log(3, 3, 0)]
    result_zero = _filter_by_item_id(interactions, 0)
    assert len(result_zero) == 2
    assert [i.id for i in result_zero] == [1, 3]

    result_neg = _filter_by_item_id(interactions, -1)
    assert len(result_neg) == 1
    assert result_neg[0].id == 2


def test_filter_preserves_input_order() -> None:
    # The order of returned interactions should preserve the original list order
    interactions = [
        _make_log(10, 1, 7),
        _make_log(11, 2, 8),
        _make_log(12, 3, 7),
        _make_log(13, 4, 7),
    ]
    result = _filter_by_item_id(interactions, 7)
    assert [i.id for i in result] == [10, 12, 13]