"""Verify global exit handling and resource cleanup without a display."""

import importlib.util
from pathlib import Path
import os
import subprocess
import sys
import textwrap
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

    def test_escape_at_each_existing_input_boundary(self):
        # The initial screen is currently the only state. SPACE does not yet
        # transition to another screen, but must not swallow a following ESC.
        for batches in (
            [[SimpleNamespace(type=768, key=32), SimpleNamespace(type=768, key=27)]],
            [[], [SimpleNamespace(type=768, key=27)]],
            [[], [], [SimpleNamespace(type=768, key=27)]],
        ):
            with self.subTest(batches=batches):
                pygame = self.run_game(batches)
                self.assertEqual(pygame.event.get.call_count, len(batches))
                self.assertEqual(pygame.display.flip.call_count, len(batches) - 1)
                self.assertEqual(
                    pygame.time.Clock.return_value.tick.call_count, len(batches) - 1
                )


@unittest.skipUnless(importlib.util.find_spec("pygame"), "requires pygame-ce")
class EscapeProcessTests(unittest.TestCase):
    def test_escape_releases_pygame_and_terminates_process(self):
        # Exercise real SDL events in a separate process: a timeout detects a
        # game loop that stays alive, and assertions verify resource cleanup.
        for frames_before_escape in (0, 1, 3):
            with self.subTest(frames_before_escape=frames_before_escape):
                script = textwrap.dedent("""
                    import sys
                    import pygame
                    from breakout.main import main

                    target = int(sys.argv[1])
                    pygame.init()
                    pygame.display.set_mode((800, 600))
                    pygame.event.clear()
                    pygame.event.post(pygame.event.Event(
                        pygame.KEYDOWN, key=pygame.K_SPACE))
                    frames = 0
                    original_flip = pygame.display.flip

                    def escape():
                        pygame.event.post(pygame.event.Event(
                            pygame.KEYDOWN, key=pygame.K_ESCAPE))

                    def flip():
                        global frames
                        original_flip()
                        frames += 1
                        if frames == target:
                            escape()

                    pygame.display.flip = flip
                    if target == 0:
                        escape()
                    main()
                    assert frames == target, (frames, target)
                    assert not pygame.get_init()
                    assert not pygame.display.get_init()
                    assert not pygame.font.get_init()
                    assert not pygame.mixer.get_init()
                    print("ESC_CLEAN_EXIT")
                """)
                result = subprocess.run(
                    [sys.executable, "-c", script, str(frames_before_escape)],
                    cwd=Path(__file__).resolve().parents[1],
                    env={**os.environ, "SDL_VIDEODRIVER": "dummy",
                         "SDL_AUDIODRIVER": "dummy", "PYGAME_HIDE_SUPPORT_PROMPT": "1"},
                    capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stderr, "")
                self.assertEqual(result.stdout.strip(), "ESC_CLEAN_EXIT")
