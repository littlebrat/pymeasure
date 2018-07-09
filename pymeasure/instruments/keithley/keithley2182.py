import enum
import time

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

    class Configuration(object):
        def __init__(self, mode, channel):
            self.__mode = mode
            self.__channel = channel

        @property
        def channel(self):
            return self.__channel

        @channel.setter
        def channel(self, channel_value):
            raise NotImplementedError

        @property
        def mode(self):
            return self.__mode

        @mode.setter
        def mode(self, mode_value):
            raise NotImplementedError

        def __repr__(self):
            return 'Configuration({}, {})'.format(self.__mode, self.__channel)

    class Mode(enum.Enum):
        voltage = 'VOLT'
        temperature = 'TEMP'

    class Channel(enum.Enum):
        internal_temp = 0
        dcv_1 = 1
        dcv_2 = 2

    @property
    def configuration(self):
        return self.Configuration(self.mode, self.channel)

    @configuration.setter
    def configuration(self, conf_value: Configuration):
        self.mode = conf_value.mode
        self.channel = conf_value.channel

    @property
    def mode(self):
        return self.Mode(self.ask('SENSe:FUNCtion?')[1:5])

    @mode.setter
    def mode(self, mode_value: Mode):
        self.write('SENSe:FUNCtion {}'.format(mode_value.value))

    @property
    def channel(self):
        return self.Channel(int(self.ask('SENSe:CHAN?')))

    @channel.setter
    def channel(self, channel_value: Channel):
        self.write('SENSe:CHAN {}'.format(channel_value.value))

    def initiate(self):
        """
        Change the state of the triggering system from the "idle" state to the "wait-for-trigger" state.
        Scanning will begin when the specified trigger conditions are satisfied following the receipt of the INITiate
        command. Readings are stored in the instrument's internal reading memory and using this command will clear the
        previous set of readings from memory.
        """
        self.write('INITiate')

    def fetch(self) -> str:
        """
        This command transfers readings stored in non-volatile memory to the instrument's output buffer.
        The readings stored in memory are not erased when you use this method.
        The format of the readings can be changed using FORMat:READing commands.

        :return: Instrument readings in the established format.
        """
        return self.ask('FETCh?')

    def measure(self, config=Configuration, to_wait: float = 0):
        """
        Do a measurement from the current mode or with it given as an optional argument.

        :param config: Mode enum for the measurement
        :param to_wait: Time in seconds to wait for the execution of the measurements.
        :return:
        """
        if config and isinstance(config, self.Configuration):
            self.mode = config

        self.initiate()

        time.sleep(to_wait)

        return float(self.fetch())
