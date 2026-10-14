import json, os, sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        info = dict(getattr(item, "_info", {}))
        info.update(nodeid=item.nodeid, status="PASS" if rep.passed else "FAIL")
        RESULTS.append(info)


def pytest_sessionfinish(session):
    out = os.environ.get("RESULTS_FILE", "results.json")
    with open(out, "w") as fh:
        json.dump(RESULTS, fh, indent=1)


@pytest.fixture
def log(request):
    def _log(tid, module, technique, inp, expected, actual):
        request.node._info = dict(id=tid, module=module, technique=technique,
                                  input=inp, expected=str(expected), actual=str(actual))
    return _log
