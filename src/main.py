# main.py
#
# Copyright 2026 riyani
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import MemoriesWindow


class MemoriesApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='com.riyani.memories',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/com/riyani/memories')
        self.create_action('quit', lambda *_: self.quit(), ['<control>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)
        self.settings = Gio.Settings.new("com.riyani.memories")

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = MemoriesWindow(application=self)
        win.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(application_name='memories',
                                application_icon='com.riyani.memories',
                                developer_name='riyani',
                                version='0.1.0',
                                developers=['riyani'],
                                copyright='© 2026 riyani')
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_('translator-credits'))
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        prefs = Adw.PreferencesWindow()
        prefs.set_application(self)

        page = Adw.PreferencesPage()
        page.set_title("Preferences")

        group = Adw.PreferencesGroup()
        group.set_title("Settings")

        # Folder chooser
        folderBtn = Gtk.Button(label="Choose Folder", valign=Gtk.Align.CENTER)
        folderBtn.connect("clicked", self.selectFolder)
        folderRow = Adw.ActionRow(title="Picture Folder")
        folderRow.add_suffix(folderBtn)

        # Clear folders button
        clearBtn = Gtk.Button(label="Clear All Folders", valign=Gtk.Align.CENTER)
        clearBtn.connect("clicked", self.clearFolders)
        clearRow = Adw.ActionRow(title="Clear Folders")
        clearRow.add_suffix(clearBtn)

        # Delay
        delaySpin = Gtk.SpinButton.new_with_range(1, 60, 1)
        delaySpin.set_valign(Gtk.Align.CENTER)
        delaySpin.connect("value-changed", lambda *args: print("todo"))
        delayRow = Adw.ActionRow(title="Carousel Delay")
        delayRow.add_suffix(delaySpin)

        group.add(folderRow)
        group.add(clearRow)
        group.add(delayRow)

        page.add(group)
        prefs.add(page)
        prefs.present()


    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def clearFolders(self, btn):
        """Clear all saved image folders."""
        self.settings.set_strv("image-folders", [])  # clear GSettings
        print("All folders cleared!")

        # If the main window has a carousel, refresh it
        win = self.props.active_window
        if win and hasattr(win, "carousel"):
            win.carousel.load_images_from_settings()  # reload carousel


    def selectFolder(self, btn):
        dialog = Gtk.FileDialog()
        dialog.select_folder(self.props.active_window, None, self.onFolderSelected)

    def onFolderSelected(self, dialog, result):
        folder = dialog.select_folder_finish(result)
        if folder:
            path = folder.get_path()
            folders = self.settings.get_strv("image-folders")
            if path not in folders:
                print("Before:", self.settings.get_strv("image-folders"))
                folders.append(path)
                self.settings.set_strv("image-folders", folders)
                print("After:", self.settings.get_strv("image-folders"))


def main(version):
    """The application's entry point."""
    app = MemoriesApplication()
    return app.run(sys.argv)
