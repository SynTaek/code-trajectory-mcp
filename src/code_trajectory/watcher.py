# SPDX-License-Identifier: MIT
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer
from .recorder import Recorder

logger = logging.getLogger(__name__)


class DebouncedEventHandler(FileSystemEventHandler):
    """Handles file system events with debouncing to prevent excessive snapshots.

    Attributes:
        recorder: The Recorder instance to use for snapshots.
        debounce_interval: Time in seconds to wait before processing a change.
        timers: Dictionary of active timers for each file.
    """
    def __init__(self, recorder: Recorder, debounce_interval: float = 2.0):
        self.recorder = recorder
        self.debounce_interval = debounce_interval
        self.timers = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        # Ignore .git directory.
        if ".git" in filepath:
            return

        # Check if ignored by git.
        try:
            if self.recorder.repo.ignored(filepath):
                logger.debug(f"Ignoring {filepath} (git ignored)")
                return
        except Exception as e:
            logger.warning(f"Failed to check ignore status for {filepath}: {e}")

        if filepath in self.timers:
            self.timers[filepath].cancel()

        timer = Timer(self.debounce_interval, self._snapshot, [filepath])
        self.timers[filepath] = timer
        timer.start()

    def _snapshot(self, filepath):
        try:
            self.recorder.create_snapshot(filepath)
            if filepath in self.timers:
                del self.timers[filepath]
        except Exception as e:
            logger.error(f"Error snapshotting {filepath}: {e}")


class Watcher:
    """Monitors the project directory for file changes.

    Attributes:
        path: The root directory to watch.
        recorder: The Recorder instance to handle snapshots.
        observer: The watchdog Observer instance.
        handler: The event handler for file changes.
    """
    def __init__(self, path: str, recorder: Recorder):
        self.path = path
        self.recorder = recorder
        self.observer = Observer()
        self.handler = DebouncedEventHandler(recorder)

    def start(self):
        self.observer.schedule(self.handler, self.path, recursive=True)
        self.observer.start()
        logger.info(f"Started watching {self.path}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped watcher")
