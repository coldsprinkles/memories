# window.py
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

from gi.repository import Adw
from gi.repository import Gtk, Gdk, Gio
from .lazy_carousel import LazyCarousel

class MemoriesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'MemoriesWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = self.get_application()
        self.settings = app.settings

        window_handle = Gtk.WindowHandle()
        gesture_click = Gtk.GestureClick()
        gesture_click.set_button(3)
        window_handle.add_controller(gesture_click)

        gesture_click.connect("pressed", self.on_right_click_pressed)

        carousel = LazyCarousel(self.settings)
        window_handle.set_child(carousel)

        self.popover_menu = Gtk.PopoverMenu()

        menu_model = Gio.Menu()
        menu_model.append("Preferences", "app.preferences")
        menu_model.append("About", "app.about")

        self.popover_menu.set_menu_model(menu_model)


        self.set_content(window_handle)
        self.set_default_size(370, 370)

    def on_right_click_pressed(self, gesture, n_press, x, y):
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)


        self.popover_menu.set_parent(self)
        self.popover_menu.props.has_arrow = False
        self.popover_menu.props.halign = Gtk.Align.START

        rectangle = Gdk.Rectangle()
        rectangle.x, rectangle.y, rectangle.width, rectangle.height = x, y, 0, 0

        self.popover_menu.props.pointing_to = rectangle
        self.popover_menu.popup()
