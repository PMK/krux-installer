# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
main_screen.py
"""
import sys
import threading
import traceback
from functools import partial
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.context_instructions import Color
from src.app.screens.base_flash_screen import BaseFlashScreen
from src.utils.flasher import Flasher


class FlashScreen(BaseFlashScreen):
    """Flash screen is where flash occurs"""

    def __init__(self, **kwargs):
        super().__init__(wid="flash_screen", name="FlashScreen", **kwargs)
        self.flasher = Flasher()
        fn = partial(self.update, name=self.name, key="canvas")
        Clock.schedule_once(fn, 0)

    def build_on_data(self):
        """
        Build a streaming IO static method using
        some instance variables for flash procedure
        when KTool.print_callback is called

        (useful for to be used in tests)
        """

        # pylint: disable=unused-argument
        def on_data(*args, **kwargs):
            text = " ".join(str(x) for x in args)
            self.info(text)
            text = FlashScreen.parse_general_output(text)
            text = text.replace("\rProgramming", "Programming")

            if "INFO" in text:
                self.output.append(text)
                if "Rebooting" in text:
                    self.is_done = True
                    # pylint: disable=not-callable
                    self.done()

            elif "Programming BIN" in text:
                self.output[-1] = text

            elif "*" in text:
                self.output.append("*")
                self.output.append("")

            if len(self.output) > 18:
                del self.output[:1]

            self.ids[f"{self.id}_info"].text = "\n".join(self.output)

        setattr(FlashScreen, "on_data", on_data)

    def build_on_process(self):
        """
        Build a streaming IO static method using
        some instance variables for flash procedure

        (useful for to be used in tests)
        """

        def on_process(file_type: str, iteration: int, total: int, suffix: str):
            percent = (iteration / total) * 100

            if sys.platform in ("linux", "win32"):
                sizes = [self.SIZE_M, self.SIZE_MP, self.SIZE_P]
            else:
                sizes = [self.SIZE_MM, self.SIZE_M, self.SIZE_MP]

            please = self.translate("PLEASE DO NOT UNPLUG YOUR DEVICE")
            flashing = self.translate("Flashing")
            at = self.translate("at")

            self.ids[f"{self.id}_progress"].text = "".join(
                [
                    f"[size={sizes[1]}sp][b]{please}[/b][/size]",
                    "\n",
                    f"[size={sizes[0]}sp]{percent:.2f} %[/size]",
                    "\n",
                    f"[size={sizes[2]}sp]",
                    f"{flashing} ",
                    "[color=#efcc00]",
                    "[b]",
                    file_type,
                    "[/b]",
                    "[/color]",
                    f" {at} ",
                    "[color=#efcc00]",
                    "[b]",
                    suffix,
                    "[/b]",
                    "[/color]",
                    "[/size]",
                ]
            )

        setattr(FlashScreen, "on_process", on_process)

    def build_on_done(self):
        """
        Build a streaming IO static method using
        some instance variables when flash procedure is done

        (useful for to be used in tests)
        """

        # pylint: disable=unused-argument
        def on_done(dt):
            del self.output[4:]
            self.ids[f"{self.id}_loader"].source = self.done_img
            self.ids[f"{self.id}_loader"].reload()
            done = self.translate("DONE")
            back = self.translate("Back")
            _quit = self.translate("Quit")

            if sys.platform in ("linux", "win32"):
                size = self.SIZE_M
            else:
                size = self.SIZE_M

            self.ids[f"{self.id}_progress"].text = "".join(
                [
                    f"[size={size}sp][b]{done}![/b][/size]",
                    "\n",
                    "\n",
                    f"[size={size}sp]",
                    "[color=#00FF00]",
                    f"[ref=Back][u]{back}[/u][/ref]",
                    "[/color]",
                    "        ",
                    "[color=#EFCC00]",
                    f"[ref=Quit][u]{_quit}[/u][/ref]",
                    "[/color]",
                ]
            )

        setattr(FlashScreen, "on_done", on_done)

    # pylint: disable=unused-argument
    def on_pre_enter(self, *args):
        self.ids[f"{self.id}_grid"].clear_widgets()
        self.build_on_data()
        self.build_on_process()
        self.build_on_done()

        def on_ref_press(*args):
            if args[1] == "Back":
                self.set_screen(name="MainScreen", direction="right")

            elif args[1] == "Quit":
                App.get_running_app().stop()

            else:
                self.redirect_error(f"Invalid ref: {args[1]}")

        self.make_subgrid(
            wid=f"{self.id}_subgrid", rows=2, root_widget=f"{self.id}_grid"
        )

        self.make_image(
            wid=f"{self.id}_loader",
            source=self.warn_img,
            root_widget=f"{self.id}_subgrid",
        )

        self.make_label(
            wid=f"{self.id}_progress",
            text="",
            root_widget=f"{self.id}_subgrid",
            halign="center",
        )
        self.ids[f"{self.id}_progress"].bind(on_ref_press=on_ref_press)

        self.make_label(
            wid=f"{self.id}_info",
            text="",
            root_widget=f"{self.id}_grid",
            halign="justify",
        )

    # pylint: disable=unused-argument
    def on_enter(self, *args):
        """
        Event fired when the screen is displayed and the entering animation is complete.
        """
        self.done = getattr(FlashScreen, "on_done")
        self.flasher.ktool.__class__.print_callback = getattr(FlashScreen, "on_data")
        on_process = partial(
            self.flasher.flash, callback=getattr(self.__class__, "on_process")
        )
        self.thread = threading.Thread(name=self.name, target=on_process)

        if sys.platform in ("linux", "win32"):
            sizes = [self.SIZE_M, self.SIZE_P]
        else:
            sizes = [self.SIZE_MM, self.SIZE_MP]

        # if anything wrong happen, show it
        def hook(err):
            if not self.is_done:
                trace = traceback.format_exception(
                    err.exc_type, err.exc_value, err.exc_traceback
                )
                msg = "".join(trace)
                self.error(msg)

                back = self.translate("Back")
                _quit = self.translate("Quit")
                self.ids[f"{self.id}_progress"].text = "".join(
                    [
                        f"[size={sizes[0]}]",
                        "[color=#FF0000]Flash failed[/color]",
                        "[/size]",
                        "\n",
                        "\n",
                        f"[size={sizes[0]}]",
                        "[color=#00FF00]",
                        f"[ref=Back][u]{back}[/u][/ref][/color]",
                        "        ",
                        "[color=#EFCC00]",
                        f"[ref=Quit][u]{_quit}[/u][/ref]",
                        "[/color]",
                        "[/size]",
                    ]
                )

                self.ids[f"{self.id}_info"].text = "".join(
                    [f"[size={sizes[1]}]", msg, "[/size]"]
                )

        # hook what happened
        threading.excepthook = hook

        # start thread
        self.thread.start()

    # pylint: disable=unused-argument
    def update(self, *args, **kwargs):
        """Update screen with firmware key. Should be called before `on_enter`"""
        name = kwargs.get("name")
        key = kwargs.get("key")
        value = kwargs.get("value")

        if name in (
            "ConfigKruxInstaller",
            "UnzipStableScreen",
            "DownloadBetaScreen",
            "FlashScreen",
        ):
            self.debug(f"Updating {self.name} from {name}...")
        else:
            raise ValueError(f"Invalid screen name: {name}")

        key = kwargs.get("key")
        value = kwargs.get("value")

        if key == "locale":
            if value is not None:
                self.locale = value
            else:
                self.redirect_error(f"Invalid value for key '{key}': '{value}'")

        elif key == "canvas":
            # prepare background
            with self.canvas.before:
                Color(0, 0, 0, 1)
                Rectangle(size=(Window.width, Window.height))

        elif key == "baudrate":
            if value is not None:
                self.baudrate = value
            else:
                self.redirect_error(f"Invalid value for key '{key}': '{value}'")

        elif key == "firmware":
            if value is not None:
                self.firmware = value
            else:
                self.redirect_error(f"Invalid value for key '{key}': '{value}'")

        elif key == "flasher":
            self.flasher.firmware = self.firmware
            self.flasher.baudrate = self.baudrate

        elif key == "exception":
            self.redirect_error("")
        else:
            self.redirect_error(f'Invalid key: "{key}"')
