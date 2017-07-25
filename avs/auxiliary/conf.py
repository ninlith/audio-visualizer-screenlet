# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Okko Hartikainen <okko.hartikainen@gmail.com>
#
# This file is part of audio-visualizer-screenlet, which is licensed under the
# GNU General Public License 3.0 or later. See COPYING.

"""Configuration-related classes and functions."""

# pylint: disable=import-error
from pathlib import Path
import argparse
import logging
import logging.config
import os
from six.moves import configparser
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from auxiliary import utils

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def parse_command_line_args():
    """Define and parse command-line options."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--debug",
        help="enable DEBUG logging level",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.INFO,
    )
    args = parser.parse_args()
    return args


def setup_logging(loglevel):
    """Set up logging configuration."""
    logging_config = dict(
        version=1,
        disable_existing_loggers=False,
        formatters={
            'f': {
                'format':
                    "%(asctime)s %(levelname)s %(name)s - %(message)s",
                'datefmt': "%F %T"}},
        handlers={
            'h': {
                'class': "logging.StreamHandler",
                'formatter': "f",
                'level': loglevel}},
        root={
            'handlers': ["h"],
            'level': loglevel},
        )
    logging.config.dictConfig(logging_config)


class Configs(object):
    """Handle config files."""

    def __init__(self, title):
        # Configuration path.
        if 'LOCALAPPDATA' in os.environ:
            self.app_config_path = Path(os.environ['LOCALAPPDATA']) / title
        elif 'XDG_CONFIG_HOME' in os.environ:
            self.app_config_path = Path(os.environ['XDG_CONFIG_HOME']) / title
        else:
            self.app_config_path = Path(os.environ['HOME']) / ".config" / title
        logger.info("Config path: {}".format(self.app_config_path))

        # Load and merge options from default_settings.ini and settings.ini.
        self.settings = MyConfigParser()
        script_path = Path(__file__).parent
        defaults_file = script_path / "default_settings.ini"
        try:
            self.settings.read_file(defaults_file.open())
        except AttributeError:
            self.settings.readfp(defaults_file.open())  # deprecated
        self.settings_file = self.app_config_path / "settings.ini"
        self.settings.read(str(self.settings_file))

        # Create settings.ini if missing.
        if not self.settings_file.is_file():
            self.settings_file.parent.mkdir(parents=True,exist_ok=True)
            with self.settings_file.open('w') as configfile:
                self.settings.write(configfile)

        # Load state.ini.
        self.state_file = self.app_config_path / "state.ini"
        self.state = MyConfigParser()
        self.state.read(str(self.state_file))

        # Set up watchdog to monitor file system events.
        path = self.app_config_path
        event_handler = MyWatchdogHandler(patterns=[str(self.settings_file)])
        observer = Observer()
        observer.schedule(event_handler, str(path), recursive=False)
        observer.start()

    def load_state_value(self, section, option):
        """Load value from state."""
        try:
            logger.debug("Loading state [{}] {}".format(section, option))
            return self.state.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise ValueError("State not saved or invalid.")

    def save_state_value(self, section, option, value):
        """Save value to state."""
        logger.debug("Saving state [{}] {}: {}".format(section, option, value))
        if not self.state.has_section(section):
            logger.debug("Adding section [{}] to state".format(section))
            self.state.add_section(section)
        self.state.set(section, option, value)
        with self.state_file.open('w') as configfile:
            self.state.write(configfile)


class MyConfigParser(configparser.ConfigParser):
    """ConfigParser with added convenience methods."""
    # pylint: disable=too-many-ancestors, no-member

    def getmultifloat(self, section, option):
        """Return comma-separated values as a list of floats."""
        value = self.get(section, option)
        return [float(x) for x in value.replace(" ", "").split(",")]

    def getmultistr(self, section, option):
        """Return comma-separated values as a list of strings."""
        value = self.get(section, option)
        return [str(x) for x in value.replace(" ", "").split(",")]


class MyWatchdogHandler(PatternMatchingEventHandler):
    """
    Trigger program restart if given patterns match with file paths associated
    with occurring events.
    """
    ignore_directories = True

    def on_any_event(self, event):
        logger.info("Restarting...")
        utils.restart_program()
