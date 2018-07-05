#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import re
import enum


from pymeasure.instruments import Instrument


class Agilent34970A(Instrument):
    """
    Wrapper for Agilent 34970 Data Acquisition/Switch Unit.

    Implemented measurements: voltage_dc, voltage_ac, current_dc, current_ac, resistance, resistance_4w

    >>> import pymeasure.instruments as insts
    >>> x = insts.agilent.Agilent34970A('GPIB::10')
    >>> channels = [103, 105, 213]
    >>> x.mode = x.Configuration(x.Mode.voltage_dc, channels)
    >>> x.measure()

    """

    def __init__(self, adapter, delay=0.5, **kwargs):
        super(Agilent34970A, self).__init__(
            adapter, "Agilent 34970 Data Acquisition/Switch Unit", **kwargs
        )

    class Mode(enum.Enum):

        """
        Modes available to the DAQ
        """
        current_ac = 'CURRent:AC'
        current_dc = 'CURRent:DC'
        frequency = 'FREQuency'
        fourpt_resistance = 'FRESistance'
        period = 'PERiod'
        resistance = 'RESistance'
        temperature = 'TEMPerature'
        voltage_ac = 'VOLTage:AC'
        voltage_dc = 'VOLTage:DC'

    class ToggableState(enum.Enum):
        on = 'ON'
        off = 'OFF'

    class TimeFormat(enum.Enum):
        relative = 'REL'
        absolute = 'ABS'

    class Configuration(object):
        def __init__(self, mode, channel_list):
            self.__mode = mode
            self.__channel_list = channel_list

        @property
        def channel_list(self):
            return ','.join(str(x) for x in self.__channel_list)

        @property
        def mode(self):
            return self.__mode.value

    @property
    def mode(self):
        raise NotImplementedError

    @mode.setter
    def mode(self, config: Configuration):
        """Sets the mode of the channels in the DAQ.
        Every time that this function is called it will replace the previous channel list.

        :param mode_tuple: a tuple with the Mode enum and a list of channels to be defined
        :return: None
        """
        self.write('CONF:{} (@{})'.format(config.mode, config.channel_list))

    @property
    def read_channel(self):
        return self.ask('FORMat:READing:CHANnel?')

    @read_channel.setter
    def read_channel(self, toggle_value: ToggableState):
        self.write('FORMat:READing:CHANnel {}'.format(toggle_value.value))

    @property
    def read_time(self):
        return self.ask('FORMat:READing:TIME?')

    @read_time.setter
    def read_time(self, toggle_value: ToggableState):
        self.write('FORMat:READing:TIME {}'.format(toggle_value.value))

    @property
    def read_unit(self):
        return self.ask('FORMat:READ:UNIT?')

    @read_unit.setter
    def read_unit(self, toggle_value: ToggableState):
        self.write('FORMat:READ:UNIT {}'.format(toggle_value.value))

    @property
    def read_time_format(self):
        return self.ask('FORMat:READ:TIME:TYPE?')

    @read_time_format.setter
    def read_time_format(self, time_format: TimeFormat):
        self.write('FORMat:READ:TIME:TYPE {}'.format(time_format.value))

    @property
    def channels(self) -> list:
        """

        :return:
        """
        response = self.ask('ROUT:SCAN?')
        regex_find = re.search(r'@(.*)\)', response, re.M)
        return regex_find.group(1).split(',')

    @channels.setter
    def channels(self, channel_list) -> None:
        """

        :param channel_list:
        :return:
        """
        self.write('ROUT:SCAN (@{})'.format(','.join(str(x) for x in channel_list)))

    def check_errors(self) -> dict:
        """
        Return

        :return:
        """
        error_dict = dict()
        for i in range(10):
            result_string = self.ask('SYSTem:ERRor?')
            error_code = int(result_string.split(',')[0])
            error_message = result_string.split('\"')[1]
            if error_code == 0:
                break
            else:
                error_dict[error_code] = error_message
        return error_dict

    def measure(self, config: Configuration=None):
        """ Do a measurement from the current mode or with it given as an optional argument.
        >>> x = Agilent34970A('GPIB::10')
        >>> x.measure(x.Configuration(x.Mode.voltage_dc, [201, 213]))

        :param config:
        :return:
        """
        if config and isinstance(config, self.Configuration):
            self.mode = config

        self.write('INITiate')

        results = self.ask('FETCh?')

        return [float(x) for x in results[:-1].split(',')]
