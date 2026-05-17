"""Regression test for https://github.com/AsInsideOut/miunlocktool/issues/8

`migate.get_service(auth_cookies, params=None)` expects `params` as a dict —
it mutates it on the first line of the function with `params["_json"] = True`.
Passing the SID *string* directly causes:

    TypeError: 'str' object does not support item assignment

This test guards against that regression by mocking the full call chain
and asserting that `migate.get_service` is invoked with a dict containing
"sid", not the bare service-id string.
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

# Stub out `migate` before importing `miunlock`, so the test does not require
# the real migate library to be installed.
sys.modules["migate"] = mock.MagicMock()
sys.modules["migate.config"] = mock.MagicMock(console=mock.MagicMock())

# Make the parent "Version 6.2" directory importable so `import miunlock` works.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import miunlock  # noqa: E402


class TestRegressionIssue8(unittest.TestCase):
    def test_main_passes_dict_to_get_service(self):
        with mock.patch.object(miunlock, "config_s", return_value={"path": "/usr/bin/fastboot"}), \
             mock.patch.object(miunlock, "get_domain", return_value="https://test.example"), \
             mock.patch.object(miunlock, "unlock_device", return_value={"success": "ok"}):

            miunlock.migate.reset_mock()
            miunlock.migate.get_passtoken.return_value = {"deviceId": "x", "userId": "1"}
            miunlock.migate.get_service.return_value = {
                "cookies": {},
                "servicedata": {"ssecurity": ""},
            }

            miunlock.main()

            self.assertTrue(
                miunlock.migate.get_service.called,
                "migate.get_service was never called — main() returned early?",
            )
            args, _ = miunlock.migate.get_service.call_args
            self.assertEqual(len(args), 2, "get_service should receive 2 positional args")
            self.assertIsInstance(
                args[1], dict,
                f"params must be a dict (migate mutates it with params['_json']=True); "
                f"got {type(args[1]).__name__}",
            )
            self.assertEqual(args[1].get("sid"), "unlockApi")


if __name__ == "__main__":
    unittest.main()
