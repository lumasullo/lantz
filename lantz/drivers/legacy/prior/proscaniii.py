# -*- coding: utf-8 -*-
"""
    lantz.drivers.legacy.prior.proscaniii
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2016 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import comtypes.client as com
from lantz import Driver, Feat, Action


class ProScanIII(Driver):

    def __init__(self, port, *args, **kwargs):

        self.lib = com.GetModule("Prior.dll")
        self.port = port

        self.controller = com.CreateObject(self.lib.Scan())
        self.controller.Connect(self.port)
        self.zobject = com.CreateObject(self.lib.Z())

    @Feat(units='um', limits=(-10000, 10000))
    def zPosition(self):
        '''Gets and sets current position.
        If the value is set to z = 0, the display changes to REL 0 (relative
        display mode). To return to ABS mode use inst.move_absolute(0) and then
        inst.position = 0. Thus, the stage will return to 0 micrometers and the
        display screen will switch to ABS mode.
        '''
        return self.zobject.Position

    @zPosition.setter
    def zPosition(self, value):
        '''Gets and sets current position.
        If the value is set to z = 0, the display changes to REL 0 (relative
        display mode). To return to ABS mode use inst.move_absolute(0) and then
        inst.position = 0. Thus, the stage will return to 0 micrometers and the
        display screen will switch to ABS mode.
        '''
        self.zobject.MoveToAbsolute(value)

    @Action()
    def zMoveRelative(self, value):
        try:
            value.units
            if value.to('um').magnitude > 0:
                return self.zobject.MoveUp(value.to('um').magnitude)

            else:
                return self.zobject.MoveDown(-value.to('um').magnitude)
        except:
                if value > 0:
                    return self.zobject.MoveUp(value)

                else:
                    return self.zobject.MoveDown(-value)

    @Feat()
    def zUmPerRevolution(self):
        return self.zobject.MicronsPerMotorRevolution

    @zUmPerRevolution.setter
    def zUmPerRevolution(self, value):
        self.zobject.MicronsPerMotorRevolution = value

    @Feat(values={'left': 1, 'right': -1})
    def zHostPosition(self):
        return self.zobject.HostDirection

    @zHostPosition.setter
    def zHostPosition(self, value):
        self.zobject.HostDirection = value

    def finalize(self):
        self.controller.DisConnect()


if __name__ == '__main__':

    from lantz import Q_

    um = Q_(1, 'um')

    aa = ProScanIII(12)
#
#    with NanoScanZ(12) as nano:
#        print(nano.position)
#        nano.position = -650 * um
#        print(nano.position)
#        print(nano.hostPosition)
#        nano.hostPosition = 'left'
#        print(nano.hostPosition)
