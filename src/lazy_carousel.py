import os
from gi.repository import Adw, Gtk, GLib

class LazyCarousel(Adw.NavigationPage):
    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.image_files = []
        self.max_index = 0
        self.current_index = 0

        self.carousel = Adw.Carousel()
        self.carousel.set_allow_mouse_drag(False)
        self.carousel.set_hexpand(True)
        self.carousel.set_vexpand(True)
        self.set_child(self.carousel)

        self.widgets = [Gtk.Picture.new_for_filename("") for _ in range(3)]
        for w in self.widgets:
            w.set_hexpand(True)
            w.set_vexpand(True)
            w.set_content_fit(Gtk.ContentFit.COVER)
            self.carousel.append(w)

        self.carousel.connect("page-changed", self.on_page_changed)

        self.settings.connect("changed::image-folders", lambda *_: self.load_images_from_settings())
        self.settings.connect("changed::image-change-delay", lambda *_: self.start_timer())

        self.load_images_from_settings()
        self.timer = None
        self.start_timer()

    def start_timer(self):
        seconds = self.settings.get_int("image-change-delay")
        if self.timer:
            GLib.source_remove(self.timer)
        self.timer = GLib.timeout_add(seconds*1000, self.change_page)

    def change_page(self):
        self.carousel.scroll_to(self.carousel.get_nth_page(2), True)
        return True

    def load_images_from_settings(self):
        folders = self.settings.get_strv("image-folders")
        files = []
        for folder in folders:
            if os.path.isdir(folder):
                for root, dirs, files_in_dir in os.walk(folder):
                    for f in files_in_dir:
                        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                            files.append(os.path.join(root, f))
        self.image_files = files
        self.max_index = len(self.image_files) - 1
        self.current_index = 0
        self.refresh_widgets()

    def refresh_widgets(self):
        indices = [
            max(0, self.current_index - 1),
            self.current_index,
            min(self.max_index, self.current_index + 1)
        ]
        for widget, idx in zip(self.widgets, indices):
            if 0 <= idx <= self.max_index:
                # self.image_files already has full paths
                widget.set_filename(self.image_files[idx])
            else:
                widget.set_filename(None)


        if self.max_index >= 0:
            self.carousel.scroll_to(self.widgets[1], False)

    def on_page_changed(self, carousel, index):
        active = carousel.get_nth_page(index)
        direction = 0

        if active == self.widgets[0]:
            direction = -1
        elif active == self.widgets[2]:
            direction = 1

        if direction != 0:
            GLib.idle_add(self.handle_swipe, direction)

    def handle_swipe(self, direction):
        self.start_timer()

        new_index = self.current_index + direction
        if 0 <= new_index <= self.max_index:
            self.current_index = new_index
            self.refresh_widgets()
        return False

