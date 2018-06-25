import struct
import enum

from pymeasure.instruments import Instrument


class HP3458A(Instrument):
    """
    Driver for the HP3458a Digital Voltmeter

    """
    def __init__(self, adapter, includeSCPI=False, **kwargs):
        super().__init__(adapter, "HP 3458A Multimeter", includeSCPI, **kwargs)
        adapter.read_termination = '\r'
        self.trigger_arm = self.TriggerMode.hold
        self.mformat = self.FormatMode.sreal
        self.oformat = self.FormatMode.sreal
        self.display = self.ToggableMode.off
        self.azero = self.ToggableMode.off
        self.tarm_mode = self.TriggerMode.syn

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

    @property
    def voltage_dc(self):
        self.write('FUNC 1')
        self.write('TRIG 1')
        return self.read(self.__bytes_to_read)

    @property
    def mode(self):
        return self.query('FUNC?')

    @mode.setter
    def mode(self, measurement_mode: Mode):
        self.write('FUNC {}'.format(measurement_mode.value))

    @property
    def display(self):
        return self.query('DISP?')

    @display.setter
    def display(self, toggable_mode: ToggableMode):
        self.write('DISP {}'.format(toggable_mode.value))

    @property
    def trigger_arm(self):
        return self.query('TARM?')

    @trigger_arm.setter
    def trigger_arm(self, trigger_arm_mode: TriggerMode):
        self.write('TARM {}'.format(trigger_arm_mode.value))

    @property
    def oformat(self):
        return self.query('OFORMAT?')

    @oformat.setter
    def oformat(self, oformat_mode: FormatMode):
        self.write('OFORMAT {}'.format(oformat_mode.value))

    @property
    def mformat(self):
        return self.query('MFORMAT?')

    @mformat.setter
    def mformat(self, mformat_mode: FormatMode):
        self.write('MFORMAT {}'.format(mformat_mode.value))

    @property
    def azero(self):
        return self.query('AZERO?')

    @azero.setter
    def azero(self, toggable_mode: ToggableMode):
        self.write('AZERO {}'.format(toggable_mode.value))

    @property
    def id(self):
        """ Requests and returns the identification of the instrument. """
        return self.adapter.query('ID?')

    def clear(self):
        """ Clears the instrument status byte
        """
        self.adapter.write('CLEAR')

    def reset(self):
        """ Resets the instrument. """
        self.adapter.write('RESET')

    def query(self, command):
        """ Writes the command to the instrument through the adapter
        and returns the read response.

        :param command: command string to be sent to the instrument
        """
        return self.adapter.query(command)

    def write(self, command):
        """ Writes the command to the instrument through the adapter.

        :param command: command string to be sent to the instrument
        """
        return self.adapter.write(command)

    def read(self, bytes: int=-1, encoding='utf-8'):
        """ Reads from the instrument through the adapter and returns the
        response.
        """

        if bytes == -1:
            msg = self.adapter.read()
        else:
            msg = self.adapter.read_bytes(bytes)


        if encoding == 'SI/16':
            return struct.unpack('>h', msg)[0]

        elif encoding == 'DI/32':
            return struct.unpack('>l', msg)[0]

        elif encoding == 'IEEE-754/32':
            return struct.unpack('>f', msg)[0]

        elif encoding == 'IEEE-754/64':
            return struct.unpack('>d', msg)[0]

        elif encoding == 'utf-8':
            return msg

        else:
            raise ValueError('Encoding {} is not implemented yet.'.format(encoding))

FORMAT_CONFIG = {
    HP3458A.FormatMode.ascii: (-1, 'utf-8'),  #TODO DOES NOT WORK
    HP3458A.FormatMode.sint: (2, 'SI/16'),
    HP3458A.FormatMode.dint: (4, 'DI/32'),
    HP3458A.FormatMode.sreal: (4, 'IEEE-754/32'),
    HP3458A.FormatMode.dreal: (8, 'IEEE-754/64'),
}