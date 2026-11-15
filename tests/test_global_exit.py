"""Verify global exit handling and resource cleanup without a display."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch


class GlobalExitTests(unittest.TestCase):
    def run_game(self, batches):
        pygame = MagicMock(QUIT=256, KEYDOWN=768, KEYUP=769, K_ESCAPE=27)
        pygame.event.get.side_effect = batches
        path = Path(__file__).resolve().parents[1] / "breakout" / "main.py"
        spec = importlib.util.spec_from_file_location("breakout_exit_test", path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"pygame": pygame}):
            spec.loader.exec_module(module)
            module.main()
        pygame.quit.assert_called_once_with()
        return pygame

    def test_escape_exits_before_rendering_or_processing_more_input(self):
        pygame = self.run_game([
            [SimpleNamespace(type=768, key=27), object()],
        ])
        pygame.display.flip.assert_not_called()
        pygame.event.get.assert_called_once_with()

    def test_window_close_uses_same_cleanup(self):
        pygame = self.run_game([[SimpleNamespace(type=256)]])
        pygame.display.flip.assert_not_called()

    def test_other_keys_and_escape_release_do_not_exit(self):
        pygame = self.run_game([
            [SimpleNamespace(type=768, key=32), SimpleNamespace(type=769, key=27)],
            [SimpleNamespace(type=768, key=27)],
        ])
        pygame.display.flip.assert_called_once_with()
        self.assertEqual(pygame.event.get.call_count, 2)
