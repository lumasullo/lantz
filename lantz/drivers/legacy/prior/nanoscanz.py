# -*- coding: utf-8 -*-
"""
    lantz.drivers.legacy.prior.nanoscanz
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2015 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from lantz import Action, Feat
from lantz.drivers.legacy.serial import SerialDriver


class NanoScanZ(SerialDriver):
    """Driver for the NanoScanZ Nano Focusing Piezo Stage from Prior.
    """

    ENCODING = 'ascii'

    RECV_TERMINATION = '\r'
    SEND_TERMINATION = '\r'

    BAUDRATE = 9600
    BYTESIZE = 8
    PARITY = 'none'
    STOPBITS = 1

    #: flow control flags
    RTSCTS = False
    DSRDTR = False
    XONXOFF = False

    @Feat(values={9600, 19200, 38400})
    def baudrate(self):
        """Reports and sets the baud rate.
        NOTE: DO NOT change the baud rate of the Piezo controller when daisy
        chained to ProScan.
        """
        return self.query('BAUD')

    @baudrate.setter
    def baudrate(self, value):
        self.query('BAUD {}'.format(value))

    @Feat(values={True: '4', False: '0'})
    def moving(self):
        """Returns the movement status, 0 stationary, 4 moving
        """
        return self.query('$')

    @Feat(read_once=True)
    def idn(self):
        """Identification of the device
        """
        return self.query('DATE') + ' ' + self.query('SERIAL')

    @Feat(units='micrometer')
    def position(self):
        """Gets and sets current position.
        If the value is set to z = 0, the display changes to REL 0
        (relative display mode). To return to ABS mode use
        inst.move_absolute(0) and then inst.position = 0. Thus, the stage will
        return to 0 micrometers and the display screen will switch to ABS mode.
        """
        return self.query('PZ')

    @position.setter
    def position(self, value):
        self.query('PZ {}'.format(value))

    @Action()
    def goZero(self):
        """Move to zero including any position redefinitions done by the position Feat
        """
        self.query('M')

    @Action(units='micrometer', limits=(100,))
    def moveAbs(self, value):
        """Move to absolute position n, range (0,100).
        This is a "real" absolute position and is independent of any relative
        offset added by the position Feat.
        """
        self.query('V {}'.format(value))

    @Action()
    def moveRel(self, value):
        """
        Move the stage position relative to the current position by an amount
        determined by 'value'.
        If value is given in micrometer, thats the amount the stage is going to
        move, in microns.
        If value is given in steps, the stage will move a distance
        value.magnitude * step. The step is defined by the step Feat
        """
        # Relative movement in microns
        if value.magnitude > 0:
            self.query('U {}'.format(value.magnitude))
        elif value.magnitude < 0:
            self.query('D {}'.format(-value.magnitude))

    @Action()
    def moveRelSteps(self, value):
        # Relative movement in 'steps'
        value = int(value)
        if value > 0:
            for x in range(0, value):
                self.query('U')
        elif value.magnitude < 0:
            for x in range(0, -value):
                self.query('D')

    @Feat(units='micrometer')
    def step(self):
        """Report and set the default step size, in microns
        """
        return self.query('C')

    @step.setter
    def step(self, value):
        self.query('C {}'.format(value))

    @Feat(read_once=True)
    def software_version(self):
        """Software version
        """
        return self.query('VER')


if __name__ == '__main__':
    import argparse
#    import lantz.log

    parser = argparse.ArgumentParser(description='Test Prior NanoScanZ')
    parser.add_argument('-i', '--interactive', action='store_true',
                        default=False, help='Show interactive GUI')
    parser.add_argument('-p', '--port', type=str, default='COM5',
                        help='Serial port to connect to')

    args = parser.parse_args()
#    lantz.log.log_to_screen(lantz.log.DEBUG)
    with NanoScanZ('COM5') as inst:
        if args.interactive:
            from lantz.ui.app import start_test_app
            start_test_app(inst)
        else:
            from lantz import Q_
            # Add your test code here
            print('Non interactive mode')

            um = Q_(1, 'micrometer')

            print(inst.idn)
#            print(inst.position)
#            print(inst.step)
#            inst.step = 1 * um
#            print(inst.step)
