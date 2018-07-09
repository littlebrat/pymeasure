import enum

from pymeasure.instruments import Instrument


class Keithley2182(Instrument):
    """
    Wrapper class for the keithley 2182 nanovoltmeter.
    Based on the wrapper from InstrumentKit library.

    >>>
    """

    def __init__(self, adapter, **kwargs):
        super(Keithley2182, self).__init__(
            adapter, "Keithley 2182 Nanovoltmeter", **kwargs
        )

    class Mode(enum.Enum):
        voltage = 'VOLTage'
        temperature = 'TEMPerature'

    @property
    def mode(self):
        return self.ask('SENSe:FUNCtion?')

    @mode.setter
    def mode(self, mode_value: Mode):
        self.write('SENSe:FUNCtion {}'.format(mode_value.value))

    @property
    def channel(self):
        return self.ask('SENSE:CHAN?')

    @channel.setter
    def channel(self, channel_value):
        if channel_value in [0, 1, 2]:
            self.write('SENSE:CHAN {}'.format(channel_value))
        else:
            raise ValueError('The channel should be an integer number between 0 and 2')

    class Channel(object):

        def __init__(self, number):
            self.__number = number

        @property
        def mode(self):
            return self.ask('SENSe:FUNCtion?')

        @mode.setter
        def mode(self, mode_value):
            self.write('SENSe:FUNCtion {}'.format(mode_value.value))


        def measure(self):
            pass

        def init(self):
            pass


