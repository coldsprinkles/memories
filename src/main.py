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
                                version='0.1.9',
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

        folders = Adw.PreferencesGroup()
        folders.set_title("Folders")

        # Folder chooser
        add_btn = Gtk.Button(label="Choose Folder", valign=Gtk.Align.CENTER)
        add_btn.connect("clicked", self.select_folder)
        add_row = Adw.ActionRow(title="Picture Folder")
        add_row.add_suffix(add_btn)
        folders.add(add_row)

        # Clear folders button
        clear_btn = Gtk.Button(label="Clear", valign=Gtk.Align.CENTER)
        clear_btn.add_css_class("destructive-action")
        clear_btn.connect("clicked", self.clear_folders)
        clear_row = Adw.ActionRow(title="Clear All Folders")
        clear_row.add_suffix(clear_btn)
        folders.add(clear_row)

        #Folders
        """stored_folders = self.settings.get_strv("image-folders")
        for folder in stored_folders:
            folder_btn = Gtk.Button.new_from_icon_name("edit-delete")
            folder_btn.set_valign(Gtk.Align.CENTER)
            folder_row = Adw.ActionRow(title=str(folder), activatable_widget=folder_btn)
            folder_row.add_suffix(folder_btn)
            folders.add(folder_row)
        """


        # Delay
        delay_spin = Gtk.SpinButton.new_with_range(1, 3600, 1)
        seconds = self.settings.get_int("image-change-delay")
        delay_spin.set_value(seconds)
        delay_spin.set_valign(Gtk.Align.CENTER)
        delay_spin.connect("value-changed", self.set_delay)
        delay_row = Adw.ActionRow(title="Carousel Delay")
        delay_row.add_suffix(delay_spin)
        group.add(delay_row)

        page.add(group)
        page.add(folders)
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

    def set_delay(self, widget):
        self.settings.set_int("image-change-delay", widget.get_value())  # clear GSettings


    def clear_folders(self, btn):
        """Clear all saved image folders."""
        self.settings.set_strv("image-folders", [])  # clear GSettings
        print("All folders cleared!")



    def select_folder(self, btn):
        dialog = Gtk.FileDialog()
        dialog.select_folder(self.props.active_window, None, self.on_folder_selected)

    def on_folder_selected(self, dialog, result):
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

