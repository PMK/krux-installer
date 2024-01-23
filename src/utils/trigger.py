# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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
trigger.py

Base class to be used accross project
"""
####################
# Standard libraries
####################
import os
import inspect

#######################
# Third party libraries
#######################
from kivy.logger import Logger, LOG_LEVELS


class Trigger:
    """
    Trigger

    Class to be (co)inherited in any class of the project.
    All actions will be logged.
    """

    def __init__(self):
        loglevel = os.environ.get("LOGLEVEL")
        if LOG_LEVELS.get(loglevel):
            Logger.setLevel(LOG_LEVELS[loglevel])
        else:
            if loglevel is None:
                Logger.setLevel(LOG_LEVELS["info"])
            else:
                raise KeyError(f"Not recognized LOGLEVEL: {loglevel}")

    @staticmethod
    def mro_info():
        """
        we can loop through the self's MRO and try to find the method
        that called us.

        :see: https://stackoverflow.com/questions/53153075/get-a-class-name-of-calling-method
        """

        # get the call frame of the calling method
        frame = inspect.currentframe().f_back
        try:
            # find the name of the first variable in the calling
            # function - which is hopefully the "self"
            codeobj = frame.f_code
            try:
                self_name = codeobj.co_varnames[0]
            except IndexError:
                return None

            # try to access the caller's "self"
            try:
                self_obj = frame.f_locals[self_name]
            except KeyError:
                return None

            # check if the calling function is really a method
            self_type = type(self_obj)
            func_name = codeobj.co_name

            # iterate through all classes in the MRO
            for cls in self_type.__mro__:
                # see if this class has a method with the name
                # we're looking for
                try:
                    method = vars(cls)[func_name]
                except KeyError:
                    continue

                # unwrap the method just in case there are any decorators
                try:
                    method = inspect.unwrap(method)
                except ValueError:
                    pass

                # see if this is the method that called us
                if getattr(method, "__code__", None) is codeobj:
                    name = self_type.__name__
                    return name

            # if we didn't find a matching method, return None
            return None

        finally:
            # make sure to clean up the frame at the end to avoid ref cycles
            del frame

    @staticmethod
    def _create_msg(msg):
        """
        Create the logged message with current
        class caller
        """
        return f"{Trigger.mro_info()}: {msg}"

    def info(self, msg):
        """
        Create the info message with the current
        class caller
        """
        Logger.info(self._create_msg(msg))

    def debug(self, msg):
        """
        Create the debug message with the current
        class caller
        """
        Logger.debug(self._create_msg(msg))

    def warning(self, msg):
        """
        Create the warning message with the current
        class caller
        """
        Logger.warning(self._create_msg(msg))

    def error(self, msg):
        """
        Create the error message with the current
        class caller
        """
        Logger.error(self._create_msg(msg))