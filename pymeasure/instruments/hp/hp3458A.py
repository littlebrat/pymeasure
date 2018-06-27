import struct
import enum

from pymeasure.instruments import Instrument
from pymeasure.adapters import VISAAdapter


class HP3458A(Instrument):
    """
    Driver for the HP3458a Digital Voltmeter

    """
    def __init__(self, resourceName, includeSCPI=False, **kwargs):
        adapter = VISAAdapter(resourceName, read_termination='\r')
        super(HP3458A, self).__init__(adapter, 'HP3458A', includeSCPI, **kwargs)
        self.__trigger_type = self.TriggerMode.auto

        self.trigger_arm = self.TriggerMode.hold
        self.mformat = self.FormatMode.dreal
        self.oformat = self.FormatMode.dreal
        self.display = self.ToggableMode.off
        self.azero = self.ToggableMode.off
        self.trigger_arm = self.TriggerMode.syn

    class Mode(enum.Enum):

        """
        Enum of valid measurement modes for HP Multimeter Language
        """
        current_ac = 7
        current_dc = 6
        current_acdc = 8

        voltage_ac = 2
        voltage_dc = 1
        voltage_acdc = 3

        frequency = 9
        period = 10

        fourpt_resistance = 5
        resistance = 4

        direct_sampling_ac = 11
        direct_sampling_dc = 12

        sub_sampling_ac = 13
        sub_sampling_dc = 14

    class ToggableMode(enum.Enum):
        """
        Toggable modes (ON/OFF)
        """
        off = 0
        on = 1

    class TriggerMode(enum.Enum):
        """
        Valid trigger sources for HPML Multimeters.

        """
        # Used with: TARM, TRIG, NRDGS
        # Occurs automatically (whenever required)
        auto = 1

        # Occurs on negative edge transition on the multimeter's external trigger input
        external = 2

        # Occurs when the multimeter's output buffer is empty, reading memory is off or empty,
        # and the controller requests data
        syn = 5

        # Used with: TARM, TRIG
        # Occurs once (upon receipt of TARM SGL or TRIG SGL command, then becomes HOLD)
        single = 3

        # Suspends measurements
        hold = 4

        # Used with: TRIG, NRDGS
        # Occurs when the power line voltage crosses zero volts
        level = 7

        # Occurs when the specified voltage is reached on the specified slope of the input signa
        line = 8

    class FormatMode(enum.Enum):
        """

        """
        #  ASCII-15 bytes per reading (see 1st and 2nd Remarks below)
        ascii = 1

        # Single Integer-16 bits 2's complement (2 bytes per reading)
        sint = 2

        # Double Integer-32 bits 2's complement (4 bytes per reading)
        dint = 3

        # Single Real-(IEEE-754) 32 bits, (4 bytes per reading)
        sreal = 4

        # Double Real-(IEEE-754) 64 bits, (8 bytes per reading)
        dreal = 5

    # The following properties are defined for the default behavior of the
    # multimeter. So, it is recommended to setup a configurable profile
    # instead of using these.

    @property
    def voltage_dc(self):
        return self.measure(self.Mode.voltage_dc)

    @property
    def current_dc(self):
        return self.measure(self.Mode.current_dc)

    @property
    def voltage_ac(self):
        return self.measure(self.Mode.voltage_ac)

    @property
    def current_ac(self):
        return self.measure(self.Mode.current_ac)

    @property
    def resistance(self):
        return self.measure(self.Mode.resistance)

    @property
    def resistance_4w(self):
        return self.measure(self.Mode.fourpt_resistance)

    # From here, there are the configurable properties and
    # actuation methods

    @property
    def line(self):
        return self.ask('LINE?')

    @property
    def trigger_mode(self):
        return self.__trigger_type

    @trigger_mode.setter
    def trigger_mode(self, mode: TriggerMode):
        self.__trigger_type = mode

    @property
    def mode(self):
        return self.Mode(int(self.ask('FUNC?').split(',')[0]))

    @mode.setter
    def mode(self, measurement_mode: Mode):
        self.write('FUNC {}'.format(measurement_mode.value))

    @property
    def nplc(self):
        """Gets the A/D converter's integration time in
        terms of power line cycles. Integration time is the time
        during which the A/D converter measures the input signal.
        """
        return self.ask('NPLC?')

    @nplc.setter
    def nplc(self, nplc_value: float):
        """

        Since the APER and NPLC commands both set the integration time,
        executing either will cancel the integration time previously
        established by the other.

        :param nplc_value:
        :return: None
        """
        self.write('NPLC {}'.format(nplc_value))

    @property
    def aperture(self):
        """Gets the A/D converter integration time in seconds.
        """
        return float(self.ask('APER?'))

    @aperture.setter
    def aperture(self, aperture_value: float):
        """Specifies the A/D converter's integration time and
         overrides any previously specified integration time or resolution.
         Since the APER and NPLC commands both set the integration time,
        executing either will cancel the integration time previously
        established by the other.

        :param aperture_value: The valid range for aperture is 0 - 1 s in increments of 100 ns.
        (Specifying a value <500 ns selects minimum aperture which is 500 ns.)
        :return: None
        """
        self.write('APER {}'.format(aperture_value))

    @property
    def delay(self):
        """The DELAY command allows you to specify a time interval
        that is inserted between the trigger event and the first sample event.

        :return: delay in seconds
        """
        return float(self.ask('DELAY?'))

    @delay.setter
    def delay(self, delay_value: float):
        """Specifies the delay time in seconds. Delay time can range from
        1E-7 (100 ns) to 6000 seconds in 10 ns increments for direct- or
        sub-sampling (DSAC, DSDC, SSAC, or SSDC) or 100 ns increments for
        all other measurement functions.
        Specifying 0 for the delay sets the delay to its minimum possible value.
        
        :param delay_value:
        :return: None
        """
        self.write('DELAY {}'.format(delay_value))

    @property
    def display(self):
        return self.ToggableMode(int(self.ask('DISP?')))

    @display.setter
    def display(self, toggable_mode: ToggableMode):
        self.write('DISP {}'.format(toggable_mode.value))

    @property
    def arange(self):
        return self.ToggableMode(int(self.ask('ARANGE?')))

    @arange.setter
    def arange(self, toggable_mode: ToggableMode):
        self.write('ARRANGE {}'.format(toggable_mode.value))

    @property
    def trigger_arm(self):
        return self.TriggerMode(int(self.ask('TARM?')))

    @trigger_arm.setter
    def trigger_arm(self, trigger_arm_mode: TriggerMode):
        self.write('TARM {}'.format(trigger_arm_mode.value))

    @property
    def oformat(self):
        return self.FormatMode(int(self.ask('OFORMAT?')))

    @oformat.setter
    def oformat(self, oformat_mode: FormatMode):
        self.write('OFORMAT {}'.format(oformat_mode.value))

    @property
    def mformat(self):
        return self.FormatMode(int(self.ask('MFORMAT?')))

    @mformat.setter
    def mformat(self, mformat_mode: FormatMode):
        self.write('MFORMAT {}'.format(mformat_mode.value))

    @property
    def azero(self):
        """The autozero function applies only to DC voltage, DC current,
         and resistance measurements.

        :return: ToggableMode
        """
        return self.ToggableMode(int(self.ask('AZERO?')))

    @azero.setter
    def azero(self, toggable_mode: ToggableMode):
        """When autozero is ON, the multimeter makes a zero measurement
        (measurement with the input disabled) following every reading and
        algebraically subtracts the zero measurement from the reading. This
        approximately doubles the time required per reading.

        :param toggable_mode: on/off
        :return: None
        """
        self.write('AZERO {}'.format(toggable_mode.value))

    @property
    def id(self):
        """ Requests and returns the identification of the instrument. """
        return self.ask('ID?')

    def trigger(self):
        self.write('TRIG {}'.format(self.trigger_mode.value))

    def measure(self, mode=None, read_config=None):
        if mode:
            self.mode = mode

        if read_config is None:
            read_config = FORMAT_CONFIG[self.oformat]

        self.trigger()

        value = self.read(size=read_config[0], encoding=read_config[1])

        return value

    def clear(self):
        """ Clears the instrument status byte
        """
        self.write('CLEAR')

    def reset(self):
        """ Resets the instrument. """
        self.write('RESET')


FORMAT_CONFIG = {
    HP3458A.FormatMode.ascii: (-1, 'utf-8'),
    HP3458A.FormatMode.sint: (2, 'SI/16'),
    HP3458A.FormatMode.dint: (4, 'DI/32'),
    HP3458A.FormatMode.sreal: (4, 'IEEE-754/32'),
    HP3458A.FormatMode.dreal: (8, 'IEEE-754/64'),
}
