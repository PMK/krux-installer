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
wiper.py
"""
import io
import sys
import typing
from contextlib import redirect_stdout
from threading import Thread
from .base_flasher import BaseFlasher


class Wiper(BaseFlasher):
    """Class to wipe some specific board"""
    
    def __init__(self):
        super().__init__()
        
    def wipe(self, callback: typing.Callable = print):
        """Erase all data in device"""
        try:
            self.ktool.print_callback = callback
            self.configure_device()
            sys.argv = []
            sys.argv.extend([
                "-B",
                self.board,
                "-b",
                "1500000",
                "-E"
            ])
            
            self.ktool.process()
            sys.exit(0)
                
        except Exception as exc:
            raise RuntimeError(str(exc)) from exc