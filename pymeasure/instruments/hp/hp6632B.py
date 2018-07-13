import time
import enum

from pymeasure.instruments import Instrument

class HP6632B(Instrument):
    """
    This instrument combines two instruments in one unit: a DC source, which produces DC output with
    programmable voltage and current amplitude; and a current meter, with the capability to measure
    very low-level currents.

    >>> d = HP6632B('GPIB0::7')
    >>> d.voltage = 20
    >>> d.output = True
    """
    def __init__(self, adapter, **kwargs):
        super(HP6632B, self).__init__(
            adapter, "HP 6632b System DC Power Supply", **kwargs
        )

    class ToggableMode(enum.Enum):
        on = 'ON'
        off = 'OFF'

    @property
    def voltage(self):
        return self.ask('MEAS:VOLT?')

    @voltage.setter
    def voltage(self, voltage_value: float):
        self.write('VOLTage {}'.format(voltage_value))

    @property
    def overvoltage(self):
        return self.ask('VOLTage:PROTection?')

    @overvoltage.setter
    def overvoltage(self, volt_value: float):
        self.write('VOLTage:PROTection {}'.format(volt_value))

    @property
    def voltage_triggered(self):
        return self.ask('VOLTage:TRIGgered?')

    @voltage_triggered.setter
    def voltage_triggered(self, volt_trigger_value: float):
        self.write('VOLTage:TRIGgered {}'.format(volt_trigger_value))

    @property
    def current_triggered(self):
        return self.ask('CURRent:TRIGgered?')

    @current_triggered.setter
    def current_triggered(self, volt_trigger_value: float):
        self.write('CURRent:TRIGgered {}'.format(volt_trigger_value))

    @property
    def current(self):
        return self.ask('MEAS:CURR?')

    @current.setter
    def current(self, current_value: float):
        self.write('CURRent {}'.format(current_value))

    @property
    def overcurrent(self):
        return self.ask('CURRent:PROTection:STATe?')

    @overcurrent.setter
    def overcurrent(self, toggle: ToggableMode):
        self.write('CURRent:PROTection:STATe {}'.format(toggle.value))

    @property
    def output(self):
        return self.ask('OUTPut?')

    @output.setter
    def output(self, toggle: ToggableMode):
        self.write('OUTPut {}'.format(toggle.value))

    def abort(self):
        self.write('ABORt')
