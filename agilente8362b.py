import visa


class AgilentE8362B:

    model = 'E8362B'

    def __init__(self, idn: str, inst):
        self._idn = idn
        _, name, _, _ = idn.split(',')
        self._name = name.strip()
        self._inst = inst

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

    def mkr_read_measurement(self, chan=1, parameter=''):
        return self.query(f'CALC{chan}:PAR:SEL "{parameter}";CALC{chan}:DATA? FDATA')

    def mkr_read_freqs(self, chan=1, parameter=''):
        return self.query(f'CALC{chan}:PAR:SEL "{parameter}";SENS{chan}:X?')

    def mkr_init(self):
        self.send('SYST:PRES')
        self.query('*OPC?')
        self.send('CALC:PAR:DEL:ALL')

        self.send('DISP:WIND2 ON')

        self.send('CALC1:PAR:DEF "CH1_S21",S21')
        self.send('CALC2:PAR:DEF "CH2_S21",S21')
        self.send('CALC1:PAR:DEF "CH1_S11",S11')
        self.send('CALC1:PAR:DEF "CH1_S22",S22')

        self.send('SENS1:CORR:CSET:ACT "-20dBm_1.1-1.4G",1')
        self.send('SENS2:CORR:CSET:ACT "-20dBm_1.1-1.4G",1')

        self.send('DISP:WIND1:TRAC1:FEED "CH1_S21"')
        self.send('DISP:WIND2:TRAC1:FEED "CH2_S21"')
        self.send('DISP:WIND1:TRAC2:FEED "CH1_S11"')
        self.send('DISP:WIND1:TRAC3:FEED "CH1_S22"')

        self.send('SENS1:SWE:MODE CONT')
        self.send('SENS2:SWE:MODE CONT')

        self.send('CALC1:FORM MLOG')
        self.send('DISP:WIND1:TRAC1:Y:SCAL:AUTO')
        self.send('CALC2:FORM UPH')
        self.send('DISP:WIND2:TRAC1:Y:SCAL:AUTO')

        self.send(f'FORM:DATA ASCII')

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


