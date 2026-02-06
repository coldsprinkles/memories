from gi.repository import Adw, Gtk, Gio, GLib

Adw.init()

class LazyCarousel(Adw.NavigationPage):
    __gtype_name__ = 'LazyCarousel'

    def __init__(self, max_index=1000, **kwargs):
        super().__init__(**kwargs)

        # Carousel setup
        self.carousel = Adw.Carousel()
        self.carousel.set_hexpand(True)
        self.carousel.set_vexpand(True)
        self.set_child(self.carousel)

        # Data
        self.max_index = max_index
        self.current_index = 0

        # Create 3 reusable widgets: prev, current, next
        self.widgets = [Adw.StatusPage() for _ in range(3)]
        for w in self.widgets:
            w.set_hexpand(True)
            w.set_vexpand(True)
            self.carousel.append(w)

        # Initialize content
        self.update_widgets(self.current_index)

        # Track middle widget position
        self.current_position = 1

        # Connect signal
        self.carousel.connect("page-changed", self.on_page_changed)

    def update_widgets(self, center_index):
        """Set titles/descriptions of prev/current/next widgets"""
        indices = [center_index - 1, center_index, center_index + 1]
        for w, i in zip(self.widgets, indices):
            if 0 <= i <= self.max_index:
                w.set_title(f"Page {i}")
                w.set_description(f"Description for Page {i}")
            else:
                w.set_title("")
                w.set_description("")

        # Show middle widget without animation
        self.carousel.scroll_to(self.widgets[1], False)
        self.current_position = 1

    def on_page_changed(self, carousel, index):
        active_widget = carousel.get_nth_page(index)

        # Determine swipe direction
        if active_widget == self.widgets[0]:
            direction = -1  # backward
        elif active_widget == self.widgets[2]:
            direction = 1   # forward
        else:
            return  # middle widget, nothing to do

        # Defer rotation to after animation
        GLib.idle_add(self.rotate_widgets, direction)

    def rotate_widgets(self, direction):
        """Rotate and reuse widgets according to swipe direction"""
        if direction == -1:  # backward
            if self.current_index == 0:
                self.update_widgets(self.current_index)
                return False
            self.current_index -= 1
            # Rotate widgets: right widget becomes new left
            self.widgets = [self.widgets[2], self.widgets[0], self.widgets[1]]
            prev_index = self.current_index - 1
            if prev_index >= 0:
                w = self.widgets[0]
                w.set_title(f"Page {prev_index}")
                w.set_description(f"Description for Page {prev_index}")
                self.carousel.reorder(w, 0)

        elif direction == 1:  # forward
            if self.current_index == self.max_index:
                self.update_widgets(self.current_index)
                return False
            self.current_index += 1
            # Rotate widgets: left widget becomes new right
            self.widgets = [self.widgets[1], self.widgets[2], self.widgets[0]]
            next_index = self.current_index + 1
            if next_index <= self.max_index:
                w = self.widgets[2]
                w.set_title(f"Page {next_index}")
                w.set_description(f"Description for Page {next_index}")
                self.carousel.reorder(w, 2)

        # Scroll to middle widget after rotation
        self.carousel.scroll_to(self.widgets[1], False)
        self.current_position = 1
        return False  # remove idle handler


# GTK Application Example
class ExampleWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(400, 300)
        self.set_title("Infinite Lazy Carousel")

        page = LazyCarousel(max_index=1000)
        self.set_child(page)


class ExampleApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.lazycarousel")

    def do_activate(self):
        win = ExampleWindow(application=self)
        win.present()


if __name__ == "__main__":
    app = ExampleApp()
    app.run() LETS MAKE THIS MORE OOP SO IT WORKS WITH ANY ITERABLE LIST THAT CAN MAKEWIDGETS
