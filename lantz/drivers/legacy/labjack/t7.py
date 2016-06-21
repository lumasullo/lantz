# -*- coding: utf-8 -*-
"""
        :copyright: 2014 by Lantz Authors, see AUTHORS for more details.
        :license: BSD, see LICENSE for more details.
"""


from lantz import Feat, DictFeat
from lantz import Driver

from labjack.ljm import ljm

from lantz import Q_

V = Q_(1, 'V')


class T7(Driver):

    """
    Driver for the Labjack T7 data acquisition device.
    http://labjack.com/support/t7
    For details about the commands, refer to the users guide.
    """

    def __init__(self):
        """
        Opens first found labjack
        """
        self.handle = ljm.openS("ANY", "ANY", "ANY")
        # TODO: handle cases for more than one labjack system.
        self.constants = ljm.constants

    def finalize(self):
        super().finalize()
        ljm.close(self.handle)

    @Feat(read_once=True)
    def idn(self):
        return ('Labjack T7, serial number ' +
                str(int(ljm.eReadName(self.handle, "SERIAL_NUMBER"))))

    @DictFeat(units='volts', keys=list(range(0, 14)))
    def analog_in(self, key):
        """
        AIN#(0:3)
        Returns the voltage of the specified analog input. For
        more information go to
        http://labjack.com/support/datasheets/t7/ain
        """
        return ljm.eReadName(self.handle, "AIN{}".format(key))

    @DictFeat(units='volts', keys=list(range(0, 2)), limits=(0, 5))
    def analog_out(self, key):
        """
        DAC#(0:1)
        Pass a voltage for the specified analog output. For
        more information go to
        http://labjack.com/support/datasheets/t7/dac
        """
        return ljm.eReadName(self.handle, "DAC{}".format(key))

    @analog_out.setter
    def analog_out(self, key, value):
        return ljm.eWriteName(self.handle, "DAC{}".format(key), value)

    @DictFeat(keys=list(range(0, 23)), values={True: 1, False: 0})
    def digital_IO(self, key):
        """
        DIO#(0:23)
        Read or set the state of 1 bit of digital I/O.
        Also configures the direction to input or output. For
        more information go to
        http://labjack.com/support/datasheets/t7/digital-io

        There are four different types of ports, FIO#(0:7), EIO#(0:7),
        CIO#(0:3), MIO#(0:2)

        FIO vs. EIO vs. CIO vs. MIO
        DIO is a generic name used for all digital I/O. The DIO are subdivided
        into different groups called FIO, EIO, CIO, and MIO.

        Sometimes these are referred to as different "ports".
        For example, FIO is an 8-bit port of digital I/O and EIO is a different
        8-bit port of digital I/O.
        The different names (FIO vs. EIO vs. CIO vs. MIO) have little meaning,
        and generally you can call these all DIO0-DIO22 and consider them
        all the same.

        The source impedance of an FIO line is about 550 ohms, whereas the
        source impedance of EIO/CIO/MIO lines is about 180 ohms.
        Source impedance might be important when sourcing or sinking
        substantial currents, such as when controlling relays.
        """
        return ljm.eReadName(self.handle, "DIO{}".format(key))

    @digital_IO.setter
    def digital_IO(self, key, state):
        return ljm.eWriteName(self.handle, "DIO{}".format(key), state)

    def writeName(self, name, value):
        """ Write one value specified by name."""
        return ljm.eWriteName(self.handle, name, value)

    def writeNames(self, names, values):
        """ Write multiple values specified by name."""
        return ljm.eWriteNames(self.handle, len(names), names, values)

    def address(self, name):
        """
        Takes a Modbus register name as input and produces the corresponding
        Modbus address and type. These two values can serve as input to
        functions that have Address and Type as input parameters.

        Name [in]
        A null-terminated c-string register identifier. This register
        identifiers can be a register name or a register alternate name.

        Address [out]
        Output parameter containing the address specified by Name.

        Type [out]
        Output parameter containing the type specified by Name.
        """
        return ljm.nameToAddress(name)

    def addresses(self, names):
        """
        Takes a list of Modbus register names as input and produces two lists
        as output - the corresponding Modbus addresses and types. These two
        lists can serve as input to functions that have Address/aAddresses and
        Type/aTypes as input parameters.

        NumFrames [in]
        The number of names in aNames and the allocated size of aAddresses and
        aTypes.

        aNames [in]
        An array of null-terminated c-string register identifiers. These
        register identifiers can be register names or register alternate names.

        aAddresses [out]
        An output array containing the addresses specified by aNames in the
        same order, must be allocated to the size NumFrames before calling
        LJM_NamesToAddresses.

        aTypes [out]
        An output array containing the types specified by aNames in the same
        order, must be allocated to the size NumFrames before calling
        LJM_NamesToAddresses.
        """
        return ljm.namesToAddresses(len(names), names)

    def streamStart(self, scansPerRead, scanList, scanRate):
        """ Initializes a stream object and begins streaming. This function
        creates a buffer in memory that holds data from the device, so that
        higher data throughput can be achieved.
        ScansPerRead [in]
        The number of scans returned by each call to the LJM_eStreamRead
        function. Increase this parameter to get more data per call of
        LJM_eStreamRead. A typical value would be equal to ScanRate or
        1/2 ScanRate, which results in a read once or twice per second.

        NumAddresses [in]
        The number of addresses in aScanList. The size of the aScanList array.

        aScanList [in]
        An array of addresses to stream.  The scan list is the list of things
        that are to be buffered by LJM, and returned with LJM_eStreamRead. Find
        addresses in the Modbus Map. For example, to stream AIN3 add the
        address 6 to the scan list.

        ScanRate [in/out]
        A pointer that sets the desired number of scans per second. Upon
        successful return of this function, ScanRate will be updated to the
        actual scan rate that the device will use. Keep in mind that data rate
        limits are specified in Samples/Second which is equal to
        NumAddresses * Scans/Second.

        """
        scanRate = ljm.eStreamStart(self.handle, scansPerRead, len(scanList),
                                    scanList, scanRate)
        return scanRate

    def streamRead(self):
        """ Returns data from an initialized and running LJM stream buffer.
        Waits for data to become available, if necessary.
        """
        return ljm.eStreamRead(self.handle)

    def streamStop(self):
        """ Stops LJM from storing any more data from the device. LJM will
        maintain any previously collected data in the buffer to be read. Stops
        the device from collecting data in stream mode.
        """
        return ljm.eStreamStop(self.handle)

if __name__ == '__main__':

    """
    This code tests the driver.
    """

    placa = T7()
    """
    An instance of the labjack T7 is created
    """

    print(placa.idn)
    """
    Serial number is printed
    """

    for i in range(0, 4):
        print(placa.analog_in[i])
    """
    Voltages of analog in ports are read
    """

    for i in range(0, 2):
        placa.analog_out[i] = 1 * V

    """
    Random voltages are set in the analog out ports
    """

    for i in range(0, 2):
        print(placa.analog_out[i])

    """
    Voltages of analog out ports are read
    """

    for i in range(0, 2):
        placa.analog_out[i] = (i+1)*V

    """
    Specific voltages are set in the analog out ports
    """

    for i in range(0, 2):
        print(placa.analog_out[i])

    """
    Voltages of analog out ports are read again
    """

    for i in range(0, 23):
        print(placa.digital_IO[i])

    """
    Voltages of digital in/out ports are read
    """

    placa.finalize()
