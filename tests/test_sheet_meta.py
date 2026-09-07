"""Contract tests for the data-freshness label (core/sheet_meta.py).

The label's whole job is to tell the truth about how old the sheet is. The
subtle part is WHICH session counts as current, and it can be wrong in two
directions:

  too eager  -- the exchange closes at 15:30 but the vendor publishes EOD later,
                so grading against the last CLOSED session shows "behind" every
                weekday afternoon during entirely normal operation;
  too lazy   -- the original rule keyed off a nominal 06:00 run and so could
                never expect a session captured the same evening, which read
                "current" while the sheet sat a full session behind.

Both are pinned below, along with the boundary itself, which must stay identical
in all three places that use it (this module, sheet_state.py, Prism.gs).
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (str(ROOT), str(ROOT / "core")):
    if p not in sys.path:
        sys.path.insert(0, p)

from core import sheet_meta as sm  # noqa: E402

IST = sm.IST


def _at(y, m, d, hh=10, mm=0):
    return datetime(y, m, d, hh, mm, tzinfo=IST)


# ---------------------------------------------------------------- title parsing
@pytest.mark.parametrize("header,expected", [
    ('attachment; filename="PRISM 2026-08-28 Fri.xlsx"', "PRISM 2026-08-28 Fri"),
    ("attachment; filename*=UTF-8''PRISM%202026-08-28%20Fri.xlsx", "PRISM 2026-08-28 Fri"),
    # filename* wins when both are present -- it is the encoding-aware form
    ('attachment; filename="fallback.xlsx"; filename*=UTF-8\'\'PRISM%202026-08-28%20Fri.xlsx',
     "PRISM 2026-08-28 Fri"),
    ('attachment; filename="Prism.xlsx"', "Prism"),
    ("", None),
    ("attachment", None),
])
def test_title_parsed_from_content_disposition(header, expected):
    assert sm._parse_title(header) == expected


@pytest.mark.parametrize("title,expected", [
    ("PRISM 2026-08-28 Fri", date(2026, 8, 28)),
    ("PRISM 2026-01-01 Thu", date(2026, 1, 1)),
    ("anything 2026-12-31 whatever", date(2026, 12, 31)),
    ("Prism", None),
    ("PRISM 28-08-2026", None),      # not ISO -> refuse rather than guess
    ("PRISM 2026-13-45 Fri", None),  # syntactically ISO, not a real date
    (None, None),
    ("", None),
])
def test_data_date_parsed_from_title(title, expected):
    assert sm.parse_data_date(title) == expected


# ------------------------------------------------------------- session boundary
def test_expected_session_is_yesterdays_before_todays_is_published():
    # Tue 10:00 -- Monday's session was published last evening, Tuesday's is not
    # out yet.
    assert sm.expected_session(_at(2026, 9, 1, 10)) == date(2026, 8, 31)


def test_afternoon_does_not_make_the_sheet_look_stale():
    """The first regression this boundary prevents: false amber.

    At 16:00 Tuesday, Tuesday's session HAS closed on the exchange -- but the
    vendor has not published EOD, so there is nothing to fetch. Grading against
    the last CLOSED session would show 'behind' every single weekday afternoon.
    """
    morning = sm.expected_session(_at(2026, 9, 1, 10))
    afternoon = sm.expected_session(_at(2026, 9, 1, 16))
    assert morning == afternoon == date(2026, 8, 31)


def test_evening_expects_todays_session():
    """The second regression, and the reason this rule was rewritten: false green.

    The old rule keyed off a nominal 06:00 run, so it could NEVER expect a
    session captured the same evening -- the card read "current" at 19:40 on
    2026-09-07 while the sheet still held 2026-09-04. Being permanently one
    session behind was invisible, which is worse than being behind.
    """
    assert sm.expected_session(_at(2026, 9, 7, 19, 40)) == date(2026, 9, 7)


def test_the_publication_boundary_is_inclusive_and_minute_precise():
    assert sm.expected_session(_at(2026, 9, 7, 18, 59)) == date(2026, 9, 4)
    assert sm.expected_session(_at(2026, 9, 7, 19, 0)) == date(2026, 9, 7)


def test_after_midnight_keeps_the_evenings_session():
    """01:00 Tuesday is still Monday's data -- an hour-only rule that reset at
    midnight would drop back to Friday and re-fetch for nothing."""
    assert sm.expected_session(_at(2026, 9, 8, 1, 0)) == date(2026, 9, 7)


def test_friday_evening_expects_friday():
    assert sm.expected_session(_at(2026, 9, 4, 20, 0)) == date(2026, 9, 4)


def test_saturday_never_expects_a_session_that_does_not_exist():
    """The weekday guard is load-bearing: Saturday and Sunday are past 19:00 too,
    so a time-only rule would expect a Saturday close and grade forever amber."""
    assert sm.expected_session(_at(2026, 9, 5, 20, 0)) == date(2026, 9, 4)
    assert sm.expected_session(_at(2026, 9, 6, 23, 0)) == date(2026, 9, 4)


def test_the_publication_boundary_is_one_constant_in_all_three_places():
    """core/sheet_meta.py grades the sheet, stockscans_sync/sheet_state.py decides
    whether to fetch, and Prism.gs writes the name they both read. If these drift
    the gate loops forever (expecting a name the ingest will never write) or the
    card paints a perfectly current sheet amber."""
    import re

    hh, mm = sm._DATA_READY

    # stockscans_sync/ is gitignored (the private ingest scaffold). On a code-only checkout the
    # two files are absent: SKIP, never error — a test the public repo cannot run is a red suite
    # for everyone but this machine. Locally the pin stays fully live.
    if not (ROOT / "stockscans_sync" / "sheet_state.py").exists() or not (ROOT / "stockscans_sync" / "Prism.gs").exists():
        pytest.skip("stockscans_sync/ (gitignored) not present on this checkout")

    state = (ROOT / "stockscans_sync" / "sheet_state.py").read_text(encoding="utf-8")
    m = re.search(r"^_DATA_READY\s*=\s*\((\d+),\s*(\d+)\)", state, re.M)
    assert m, "sheet_state.py no longer declares _DATA_READY as a literal pair"
    assert (int(m.group(1)), int(m.group(2))) == (hh, mm)

    gs = (ROOT / "stockscans_sync" / "Prism.gs").read_text(encoding="utf-8")
    m = re.search(r"^var DATA_READY_IST\s*=\s*'(\d{2}):(\d{2})'", gs, re.M)
    assert m, "Prism.gs no longer declares DATA_READY_IST as a literal 'HH:mm'"
    assert (int(m.group(1)), int(m.group(2))) == (hh, mm)


@pytest.mark.parametrize("when,expected", [
    (_at(2026, 8, 29, 10), date(2026, 8, 28)),   # Sat -> Friday
    (_at(2026, 8, 30, 10), date(2026, 8, 28)),   # Sun -> Friday
    (_at(2026, 8, 31, 10), date(2026, 8, 28)),   # Mon -> Friday (weekend skipped)
])
def test_weekends_resolve_back_to_friday(when, expected):
    assert sm.expected_session(when) == expected


@pytest.mark.parametrize("start,end,n", [
    (date(2026, 8, 28), date(2026, 8, 28), 0),
    (date(2026, 8, 28), date(2026, 8, 31), 1),   # Fri -> Mon is ONE session, not 3 days
    (date(2026, 8, 28), date(2026, 9, 1), 2),
    (date(2026, 8, 31), date(2026, 8, 28), 0),   # never negative
])
def test_sessions_counted_not_calendar_days(start, end, n):
    assert sm.sessions_between(start, end) == n


# --------------------------------------------------------------------- grading
def test_current_data_reads_green():
    f = sm.describe(None, "sheet", now=_at(2026, 9, 1, 10), title="PRISM 2026-08-31 Mon")
    assert (f.status, f.tone, f.day) == ("current", "green", "Mon")
    assert f.label == "Mon, 31 Aug 2026"
    assert f.is_known


def test_one_session_behind_reads_amber():
    f = sm.describe(None, "sheet", now=_at(2026, 9, 1, 10), title="PRISM 2026-08-28 Fri")
    assert (f.status, f.tone, f.sessions_behind) == ("1 session behind", "gold", 1)


def test_several_sessions_behind_reads_red():
    f = sm.describe(None, "sheet", now=_at(2026, 9, 4, 10), title="PRISM 2026-08-28 Fri")
    assert f.tone == "red" and f.sessions_behind >= 2
    assert "sessions behind" in f.status


def test_monday_morning_on_friday_data_is_current_not_three_days_old():
    """Calendar arithmetic would call this 3 days stale and paint it red on every
    Monday. It is the freshest data that exists."""
    f = sm.describe(None, "sheet", now=_at(2026, 8, 31, 8), title="PRISM 2026-08-28 Fri")
    assert (f.status, f.tone) == ("current", "green")


# ------------------------------------------------------------------- fail-soft
def test_unnamed_sheet_shows_its_real_name_rather_than_a_fake_date():
    f = sm.describe(None, "sheet", now=_at(2026, 9, 1), title="Prism")
    assert f.data_date is None and f.is_known is False
    assert f.label == "Prism" and f.tone == "muted"


def test_missing_title_never_raises():
    f = sm.describe(None, "sheet", now=_at(2026, 9, 1), title=None)
    assert f.data_date is None and f.tone == "muted"


def test_fetch_returns_none_instead_of_raising(monkeypatch):
    """A network failure must cost a label, never a render."""
    import requests

    def boom(*a, **k):
        raise requests.ConnectionError("no network")

    monkeypatch.setattr(requests, "get", boom)
    assert sm.fetch_sheet_title("someid") is None


def test_empty_sheet_id_makes_no_request(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("must not call out with an empty id")

    import requests
    monkeypatch.setattr(requests, "get", boom)
    assert sm.fetch_sheet_title("") is None


def test_http_error_yields_none(monkeypatch):
    import requests

    class Resp:
        status_code = 404
        headers: dict = {}

        def close(self):
            pass

    monkeypatch.setattr(requests, "get", lambda *a, **k: Resp())
    assert sm.fetch_sheet_title("someid") is None
