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
        self.create_action("preferences", self.on_preferences_action, ["<Ctrl>comma"])
        self.settings = Gio.Settings(schema_id="com.riyani.memories")

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
        about.present(self.props.active_window)

    def on_preferences_action(self, action, param):
        prefs = Adw.PreferencesWindow()

        prefs.set_application(self)

        page = Adw.PreferencesPage()
        page.set_title("Preferences")
        page.set_icon_name("preferences-system-symbolic")

        group = Adw.PreferencesGroup()
        group.set_title("Settings")
        #group.set_description("some settings")

        folderChooserButton = Gtk.Button(label="Choose Folder")
        folderChooserButton.set_valign(Gtk.Align.CENTER)
        folderChooserButton.connect("clicked", self.selectFolder)

        folderRow = Adw.ActionRow()
        folderRow.set_title("Picture Folder")
        folderRow.set_activatable_widget(folderChooserButton)
        folderRow.add_suffix(folderChooserButton)

        delaySpin = Gtk.SpinButton.new_with_range(1, 2000, 1)
        delaySpin.set_valign(Gtk.Align.CENTER)
        self.settings.bind("delay", delaySpin, "value", Gio.SettingsBindFlags.DEFAULT)

        delayRow = Adw.ActionRow(title="Carousel Delay (seconds)")
        delayRow.set_activatable_widget(delaySpin)
        delayRow.add_suffix(delaySpin)

        aboutButton = Gtk.Button(label="About")
        aboutButton.connect("clicked", self.on_about_action)
        aboutButton.set_valign(Gtk.Align.CENTER)
        aboutRow = Adw.ActionRow(title="About me")
        aboutRow.set_activatable_widget(aboutButton)
        aboutRow.add_suffix(aboutButton)

        group.add(delayRow)
        group.add(folderRow)
        group.add(aboutRow)
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

    def selectFolder(self, btn):
        file_dialog = Gtk.FileDialog()
        file_dialog.select_folder(self.props.active_window, None, self.onSingleSelected)

    def onSingleSelected(self, file_dialog, result):
        folder = file_dialog.select_folder_finish(result)
        selectedFolder = self.getFolder(folder)
        self.settings.set_string("picture-folder", selectedFolder)
        print(f"Selected Folder: {selectedFolder}")

    def getFolder(self, folder):
        return folder.get_path()


def main(version):
    """The application's entry point."""
    app = MemoriesApplication()
    return app.run(sys.argv)
