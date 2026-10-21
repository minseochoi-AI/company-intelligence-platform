"""The native campaign executor collects proofs; ordinary pytest checks locally.

No local fallback writes receipts or claims to be executor-bound evidence.
"""

from copy import deepcopy
import pytest


class LocalChecks:
    def invoke(self, case_id, function, *args, checks=None, observe=None, **kwargs):
        before = {
            "args": deepcopy(args),
            "kwargs": deepcopy(kwargs),
            "state": deepcopy(observe()) if observe else None,
        }
        result, error = None, None
        try:
            result = function(*args, **kwargs)
        except Exception as caught:
            error = caught
        after = {
            "args": args,
            "kwargs": kwargs,
            "state": observe() if observe else None,
        }
        for name, predicate in (checks or {}).items():
            assert predicate(before, after, result, error) is True, (case_id, name)
        if error is not None and "exception" not in (checks or {}):
            raise error
        return result


class SelectedProof:
    def __init__(self, request):
        self.request = request
        self.local = LocalChecks()

    def invoke(self, case_id, function, *args, **kwargs):
        session = getattr(self.request.config, "_dcw_proof", None)
        if session is not None and any(
            case["case_id"] == case_id for case in session.requirement["cases"]
        ):
            native = self.request.getfixturevalue("dcw_proof")
            return native.invoke(case_id, function, *args, **kwargs)
        return self.local.invoke(case_id, function, *args, **kwargs)


@pytest.fixture
def proof(request):
    return SelectedProof(request)
