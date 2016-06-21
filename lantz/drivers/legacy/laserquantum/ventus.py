# -*- coding: utf-8 -*-
"""
    lantz.drivers.legacy.laserquantum.ventus
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from lantz import Action, Feat
from lantz.drivers.legacy.serial import SerialDriver
from lantz import Q_

mW = Q_(1, 'mW')


class Ventus(SerialDriver):
    """Driver for the Laser Quantum Ventus 532 nm 1.5 W laser
    """

    ENCODING = 'ascii'

    RECV_TERMINATION = '\r\n'
    SEND_TERMINATION = '\r'

    BAUDRATE = 19200
    BYTESIZE = 8
    PARITY = 'none'
    STOPBITS = 1

    #: flow control flags
    RTSCTS = False
    DSRDTR = False
    XONXOFF = False

    def initialize(self):
        super().initialize()
        self.power_sp_state = self.power
        self.power_sp = self.power_sp_state

    @Feat(read_once=True)
    def idn(self):
        """Identification of the device
        """
        return 'Ventus 532 nm, 1.5W'

    @Feat()
    def status(self):
        """Returns status of interlock circuitry
        """
        return self.query('STAT?')

    # ENABLE LASER
    @Feat(values={True: 'ENABLED', False: 'DISABLED'})
    def enabled(self):
        """Method for turning on the laser
        """
        return self.query('STATUS?')

    @enabled.setter
    def enabled(self, value):
        if value == 'ENABLED':
            self.query('ON')
        else:
            self.query('OFF')

    # LASER'S CONTROL MODE AND SET POINT

    @Feat(values={'APC': 'POWER', 'ACC': 'CURRENT'})
    def ctl_mode(self):
        """To handle laser diode current (mA) in Active Current Control Mode
        """
        return self.query('CONTROL?')

    @ctl_mode.setter
    def ctl_mode(self, value):
        self.query('CONTROL={}'.format(value))

    @Feat(limits=(0, 100))
    def current_sp(self):
        """# is 0 to 100. This sets the current to the laser diodes as a
        percentage of the current maximum. For example, to set a diode current
        of 85% of maximum, type CURRENT=85, followed by a carriage RETURN
        """
        if self.ctl_mode == 'CURRENT':
            return self.query('CURRENT?')       # CHECK FORMAT
        else:
            return 'Laser not in current mode'

    @current_sp.setter
    def current_sp(self, value):
        self.query('CURRENT={}'.format(value))

#    @Feat(units='mW')
    @Feat()
    def power_sp(self):
        """To handle output power set point (mW) in APC Mode
        """
        return self.power_sp_state

    @power_sp.setter
    def power_sp(self, value):
        self.query('POWER={}'.format(value))
        self.power_sp_state = value * mW

    # LASER'S CURRENT STATUS

    @Feat(units='mW')
    def power(self):
        """To get the laser emission power (mW)
        """
        raw = self.query('POWER?')
        return int(raw.split('mW')[0])

    @Feat(units='degC')
    def laserTemp(self):
        """Returns the temperature of the laser head in degrees Celsius
        """
        raw = self.query('LASTEMP?')
        return float(raw.split('C')[0])

    @Feat(units='degC')
    def psuTemp(self):
        """Returns the temperature of the PSU in degrees Celsius
        """
        raw = self.query('PSUTEMP?')
        return float(raw.split('C')[0])

    @Feat()
    def timers(self):
        """Returns the PSU ‘on’ time, Laser Enabled Time and Laser Operation
        Time
        """
        raw1 = self.query('TIMERS?')
        raw2 = self.query('TIMERS?')
        raw3 = self.query('TIMERS?')
        return raw1, raw2, raw3

    # UNTESTED
    def recalibrate(self, value):
        """Recalibrates the internal laser power meter to the measured power
        in mW
        """
        self.query('ACTP={}'.format(value.magnitude))

    # UNTESTED
    @Action()
    def store(self):
        """Stores the recalibrated ACTP power into long term memory
        """
        self.query('WRITE')


if __name__ == '__main__':
    import argparse
    import lantz.log

    parser = argparse.ArgumentParser(description='Test Kentech HRI')
    parser.add_argument('-i', '--interactive', action='store_true',
                        default=False, help='Show interactive GUI')
    parser.add_argument('-p', '--port', type=str, default='COM10',
                        help='Serial port to connect to')

    args = parser.parse_args()
    lantz.log.log_to_screen(lantz.log.DEBUG)
    with Ventus(args.port) as inst:
        if args.interactive:
            from lantz.ui.qtwidgets import start_test_app
            start_test_app(inst)
        else:
            # Add your test code here
            print('Non interactive mode')
            print(inst.query('POWER?'))
            print(inst.power)
#            print(inst.shg_tuning)
