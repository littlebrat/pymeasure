import struct

from pymeasure.adapters.visa import VISAAdapter
from pymeasure.instruments import Instrument



class HP3458A(Instrument):
    """
    Represent the HP/Agilent/Keysight 34410A and related multimeters.

    Implemented measurements: voltage_dc, voltage_ac, current_dc, current_ac, resistance, resistance_4w
    """
    # only the most simple functions are implemented
    # voltage_dc = Instrument.measurement("MEAS:VOLT:DC? DEF,DEF", "DC voltage, in Volts")
    #
    # voltage_ac = Instrument.measurement("MEAS:VOLT:AC? DEF,DEF", "AC voltage, in Volts")
    #
    # current_dc = Instrument.measurement("MEAS:CURR:DC? DEF,DEF", "DC current, in Amps")
    #
    # current_ac = Instrument.measurement("MEAS:CURR:AC? DEF,DEF", "AC current, in Amps")
    #
    # resistance = Instrument.measurement("MEAS:RES? DEF,DEF", "Resistance, in Ohms")
    #
    # resistance_4w = Instrument.measurement("MEAS:FRES? DEF,DEF", "Four-wires (remote sensing) resistance, in Ohms")

    def __init__(self, adapter, includeSCPI=False, **kwargs):
        super().__init__(adapter, "HP 3458A Multimeter", includeSCPI,**kwargs)
        self.__bytes_to_read = 8
        adapter.read_termination = '\r'


    @property
    def voltage_dc(self):
        self.write('FUNC 1')
        self.write('TRIG 1')
        return self.read(self.__bytes_to_read)

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
        self.adapter.write(command)

    def read(self, bytes: int=-1, encoding='utf-8'):
        """ Reads from the instrument through the adapter and returns the
        response.
        """

        if bytes == -1:
            msg = self.adapter.read()
        else:
            msg = self.adapter.read_bytes(self.__bytes_to_read)

        if encoding == 'IEEE-754/64':
            return struct.unpack('>d', msg)[0]

        elif encoding == 'utf-8':
            return msg

        else:
            raise ValueError('Encoding {} is not implemented yet.'.format(encoding))

