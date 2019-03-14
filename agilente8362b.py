from collections import defaultdict

import visa


class Window:
    WIN_ON = 'ON'
    WIN_OFF = 'OFF'

    def __init__(self, num: int):
        self._state = self.WIN_ON
        self._num = num

    @property
    def num(self):
        return self._num

    @property
    def state(self):
        return self._state

    @property
    def create(self):
        return f'DISPl:WIND{self.num}:STAT {self.state}'


class Measurement:
    S11 = 'S11'
    S12 = 'S12'
    S21 = 'S21'
    S22 = 'S22'

    def __init__(self, chan, name, param):
        self._chan = chan
        self._name = name
        self._param = param

        self._selected = False

        self._xs = list()
        self._ys = list()

    def __str__(self):
        return f'<{self.__class__.__name__}>(chan={self.chan}, name={self.name}, param={self.param})'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def chan(self):
        return self._chan

    @property
    def param(self):
        return self._param

    @property
    def create(self):
        return f'CALC{self.chan}:PAR:DEF:EXT "{self.name}",{self.param}'


class CalbrationSet:
    CAL_SET_ON = 1
    CAL_SET_OFF = 0

    def __init__(self, chan, name):
        self._chan = chan
        self._name = name
        self._state = self.CAL_SET_ON

    @property
    def chan(self):
        return self._chan

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def activate(self):
        return f'SENS{self.chan}:CORR:CSET:ACT "{self.name}",1'


class AgilentE8362B:

    model = 'E8362B'

    def __init__(self, idn: str, inst):
        self._idn = idn
        _, name, _, _ = idn.split(',')
        self._name = name.strip()
        self._inst = inst

        self._measurements = defaultdict(list)
        self._windows = list()
        self._calibrations = defaultdict(list)

    def __str__(self):
        return f'{self._name}'

    def __repr__(self):
        return f'{self.__class__}(idn={self._idn})'

    def send(self, command):
        ret = self._inst.write(command)
        print(f'{self._name} send {command}:', ret)
        return ret

    def query(self, question):
        print(f'{self._name} ask {question}')
        answer = self._inst.query(question)
        print(f'>>> {answer}')
        return answer

    def close(self):
        self._inst.close()

    def ping(self):
        return self._inst.query('*IDN?')

    def reset(self):
        return self.send(f'SYSTem:FPRESet')

    def wait(self):
        return self.send(f'*WAI')

    def format(self, format='ASCII'):
        return self.send(f'FORMat {format}')

    def calib_import_device_state(self, name=''):
        return self.send(f'MMEMory:LOAD:CSARchive "{name}"')

    def display_create_window(self, window=1):
        return self.send(f'DISPlay:WINDow{window}:STATe ON')

    def display_create_trace(self, window=1, trace=1, meas_name=''):
        return self.send(f"DISPlay:WINDow{window}:TRACe{trace}:FEED '{meas_name}'")

    def display_delete_trace(self, window=1, trace=1):
        return self.send(f'DISPlay:WINDow{window}:TRACe{trace}:DELete')

    def trigger_source(self, source):
        """
        EXTernal - external (rear panel) source.
        IMMediate - internal source sends continuous trigger signals
        MANual - sends one trigger signal when manually triggered from the front panel or INIT:IMM is sent.
        :param source:
        :return:
        """
        return self.send(f'TRIGger:SEQuence:SOURce {source}')

    def trigger_point_mode(self, chan=1, mode='OFF'):
        """
        ON (or 1) - Channel measures one data point per trigger.
        OFF (or 0) - All measurements in the channel made per trigger

        :param mode:
        :return:
        """
        return self.send(f'SENSe{chan}:SWEep:TRIGger:POINt {mode}')

    def trigger_initiate(self, chan=1):
        return self.send(f'INITiate{chan}:IMMediate')

    def trigger_scope(self, scope='CURRENT'):
        return self.send(f'TRIGger:SEQuence:SCOPe {scope}')

    def source_power(self, chan=1, port=1, value=0):
        return self.send(f'SOURce{chan}:POWer{port} {value}dbm')

    def sense_fom_sweep_type(self, chan=1, range=1, type='linear'):
        return self.send(f'SENSe{chan}:FOM:RANGe{range}:SWEep:TYPE {type}')

    def sense_sweep_points(self, chan=1, points=51):
        return self.send(f'SENSe{chan}:SWEep:POINts {points}')

    def sense_freq_start(self, chan=1, value=1, unit='MHz'):
        return self.send(f'SENSe{chan}:FREQuency:STARt {value}{unit}')

    def sense_freq_stop(self, chan=1, value=1, unit='GHz'):
        return self.send(f'SENSe{chan}:FREQuency:STOP {value}{unit}')

    def calc_create_measurement(self, chan=1, meas_name='', meas_type='S21'):
        if not meas_name:
            meas_name = f'meas_{meas_type}'
        return self.send(f"CALCulate{chan}:PARameter:DEFine:EXTended '{meas_name}',{meas_type}"), meas_name

    def calc_parameter_select(self, chan=1, name=''):
        return self.send(f"CALCulate{chan}:PARameter:SELect '{name}'")

    def calc_formatted_data(self, chan=1):
        """
        FDATA Formatted measurement data to or from Data Access Map location
        Display (access point 2).
        Corrected data is returned when correction is ON.
        Uncorrected data is returned when correction is OFF.
        Returns TWO numbers per data point for Polar and Smith Chart format.
        Returns one number per data point for all other formats.
        Format of the read data is same as the displayed format.
        :return
        """
        return self.query(f'CALCulate{chan}:DATA? FDATA')

    def ref_create_window(self, win: Window):
        self._windows.append(win)
        return self.send(win.create)

    def ref_clear_meas(self):
        self._measurements.clear()
        return self.send('CALC:PAR:DEL:ALL')

    def ref_create_meas(self, meas: Measurement):
        self._measurements[meas.chan].append(meas)
        return self.send(meas.create)

    def ref_load_cal_set(self, calset: CalbrationSet):
        self._calibrations[calset.chan].append(calset)
        return self.send(calset.activate)

    # TODO implement
    # CALCulate<cnum>:PARameter[:DEFine]:EXTended <Mname>,<param>
    # Note: This command replaces CALC:PAR:DEF as it allows the creating of measurements using
    # external multiport testsets.
    # (Write-only) Creates a measurement but does NOT display it.
    # There is no limit to the number of measurements that can be created. However, there is a limit to the
    # number of measurements that can be displayed. See Traces, Channels, and Windows on the PNA.
    # Use DISP:WIND:STATe to create a window if it doesn't already exist.
    # Use DISP:WIND<wnum>:TRAC<tnum>:FEED <Mname> to display the measurement.
    # You must select the measurement (CALC<cnum>:PAR:SEL <mname>) before making additional
    # settings.
    # See Critical Note
    # Parameters
    # <cnum> Channel number of the new measurement. If unspecified, value is set to 1.
    # <Mname> (String) Name of the measurement. Any non-empty, unique string, enclosed in
    # quotes.
    # <param> (String ) Measurement Parameter to create. Case sensitive.
    # For S-parameters:
    # Any S-parameter available in the PNA
    # 2333Single-digit port numbers CAN be separated by "_" (underscore). For
    # example: "S21" or "S2_1"
    # Double-digit port numbers MUST be separated by underscore. For
    # example: "S10_1"
    # For ratioed measurements:
    # Any two PNA physical receivers separated by forward slash '/' followed by
    # comma and source port.
    # For example: "A/R1, 3"
    # Learn more about ratioed measurements
    # See a block diagram showing the receivers in YOUR PNA.
    # For non-ratioed measurements:
    # Any PNA physical receiver followed by comma and source port.
    # For example: "A, 4"
    # Learn more about unratioed measurements.
    # See the block diagram showing the receivers in YOUR PNA.
    # With PNA Rev 6.2, Ratioed and Unratioed measurements can also use logical
    # receiver notation to refer to receivers. This notation makes it easy to refer to
    # receivers with an external test set connected to the PNA. You do not need to
    # know which physical receiver is used for each test port. Learn more.
    # For ADC measurements:
    # Any ADC receiver in the PNA followed by a comma, then the source port.
    # For example: "AI1,2" indicates the Analog Input1 with source port of 2.
    # Learn more about ADC receiver measurements.
    # For Balanced Measurements:
    # First create an S-parameter measurement, then change the measurement
    # using CALC:FSIM:BAL "define" commands. See an example.
    # Examples CALC4:PAR:EXT 'ch4_S33', 'S33' 'Defines an S33 measurement
    # calculate2:parameter:define:extended 'ch1_a', 'b9, 1' 'logical
    # 2334receiver notation for unratioed meas of test port 9 receiver with
    # source port 1.
    # calculate2:parameter:define:extended 'ch1_a', 'b9/a10,1' 'logical
    # receiver notation for ratioed meas of test port 9 receiver divided
    # by the reference receiver for port 10 using source port 1
    # Query Syntax Not Applicable; see Calc:Par:Cat?
    # Default Not Applicable

    # CALCulate<cnum>:PARameter[:DEFine] <Mname>,<param>[,port]   Superseded
    # Note: This command is replaced with CALC:PAR:DEFine:EXTended. This command will continue
    # to work for up to 4 port parameters.
    # 2331(Write-only)  Creates a measurement but does NOT display it.
    # There is no limit to the number of measurements that can be created. However, there is a limit to the
    # number of measurements that can be displayed. See Traces, Channels, and Windows on the PNA.
    # Use DISP:WIND:STATe to create a window if it doesn't already exist.
    # Use DISP:WIND<wnum>:TRAC<tnum>:FEED <Mname> to display the measurement.
    # For FCA Measurements see CALC:CUST:DEF
    # You must select the measurement (CALC<cnum>:PAR:SEL <mname>) before making additional
    # settings.
    # See Critical Note
    # Parameters
    # <cnum> Channel number of the new measurement. If unspecified, value is set to 1.
    # <Mname> Name of the measurement. Any non-empty, unique string, enclosed in quotes.
    # <param> For S-parameters:
    # Any S-parameter available in the PNA
    # For ratioed measurements:
    # Any two receivers that are available in the PNA. (See the block diagram
    # showing the receivers in YOUR PNA.)
    # For example: AR1 (this means A/R1)
    # For non-ratioed measurements:
    # Any receiver that is available in the PNA. (See the block diagram showing
    # the receivers in YOUR PNA.)
    # For example: A
    # For Balanced Measurements:
    # First create an S-parameter measurement, then change the measurement
    # using CALC:FSIM:BAL commands. See an example.
    # For Applications see CALC:CUST:DEF.
    # [port] Optional argument;
    # 2332For multi-port reflection S-parameter measurements:  specifies the PNA port
    # which will provide the load for the calibration. This argument is ignored if a
    # transmission S-parameter is specified.
    # For all non S-parameter measurements: specifies the source port for the
    # measurement.
    # Examples CALC4:PAR 'ch4_S33',S33,2 'Defines an S33 measurement with a load
    # on port2 of the analyzer.
    # calculate2:parameter:define 'ch1_a', a, 1 'unratioed meas
    # calculate2:parameter:define 'ch1_a', ar1,1 'ratioed meas
    # Query Syntax Not Applicable; see Calc:Par:Cat?
    # Default Not Applicable

    # TODO implement
    # CALCulate<cnum>:PARameter:CATalog:EXTended?
    # (Read-only) Returns the names and parameters of existing measurements for the specified channel.
    #  This command lists receiver parameters with "_" such that R1,1 is reported as R1_1. This makes the
    # returned string a true "comma-delimited" list all the time.

    # TODO implement
    # CALCulate<cnum>:PARameter:DELete[:NAME] <Mname>
    #  (Write-only) Deletes the specified measurement.
    # See Critical Note
    # Parameters
    # <cnum> Channel number of the measurement. There must be a selected measurement
    # on that channel. If unspecified, <cnum> is set to 1.
    # <Mname> String - Name of the measurement
    # Examples CALC:PAR:DEL 'TEST'
    # calculate2:parameter:delete 'test'
    # Query Syntax Not Applicable
    # Default Not Applicable
    # ---
    # CALCulate:PARameter:DELete:ALL
    #  (Write-only) Deletes all measurements on the PNA.
    # See Critical Note
    # Parameters
    # Examples CALC:PAR:DEL:ALL
    # Query Syntax Not Applicable
    # Default Not Applicable

    @property
    def name(self):
        return self._name

    @property
    def operation_complete(self):
        # TODO check query return value
        ans = self.query('*OPC?')
        return bool(ans)

    @classmethod
    def from_instance(cls, idn, inst):
        return cls(idn=idn, inst=inst)

    @classmethod
    def from_address_string(cls, address: str):
        rm = visa.ResourceManager()
        try:
            inst = rm.open_resource(address)
            idn = inst.query('*IDN?')
            return cls(idn, inst=inst)
        except visa.VisaIOError as ex:
            raise RuntimeError(f'VISA error: {address}: {ex}')

    @classmethod
    def try_find(cls):
        rm = visa.ResourceManager()
        for res in rm.list_resources():
            print(f'trying {res}')
            try:
                inst = rm.open_resource(res)
                idn = inst.query('*IDN?')
                if cls.model in idn:
                    return cls(idn=idn, inst=inst), res
            except visa.VisaIOError as ex:
                print(f'VISA error: {ex}')
        else:
            return None

