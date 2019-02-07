import visa


class Pna20(object):

    model = 'PNA20'

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
        print(f'{self._name} send {command} ->', self._inst.write(command))

    def query(self, question):
        print(f'{self._name} ask {question}')
        # if question in [':CALCulate:fn:TRACe:FREQuency?', ':CALCulate:fn:TRACe:NOISe?']:
        if question in ['CALC:FN:TRAC:FREQ?', 'CALC:FN:TRAC:NOIS?']:
            answer = self._inst.query_binary_values(question)
        else:
            answer = self._inst.query(question)
        print(f'> {answer}')
        return answer

    def ping(self):
        return self._inst.query('*IDN?')

    def reset(self):
        return self.send(f'*RST')

    # :CALCULATE subsystem
    def calc_freq(self):
        return self.query('CALC:FREQ?')

    def calc_pow(self):
        return self.query('CALC:POW?')

    def calc_prel_averages(self, mode: str):
        return self.query(f'CALC:{mode}:PREL:AVER?')

    def calc_prel_corrections(self, mode='fn'):
        return self.query(f'CALC:{mode}:PREL:CORR?')

    def calc_wait_average(self, param='ALL'):
        return self.send(f'CALCulate:WAIT:AVERage {param}')

    def calc_trace_freq(self, mode):
        # return self.query(f':CALCulate:{mode}:TRACe:FREQuency?')
        return self.query(f'CALC:{mode}:TRAC:FREQ?')

    def calc_trace_noise(self, mode: str):
        # return self.query(f':CALCulate:{mode}:TRACe:NOISe?')
        return self.query(f'CALC:{mode}:TRAC:NOIS?')

    # :MEASURE subsystem
    def measure_supply_current(self, supply=1):
        return self.query(f'MEAS:SUPP{supply}:CURR?')

    # :SENSE subsystem
    def sense_adc_rosc_source(self, source: str):
        return self.send(f'SENS:ADC:ROSC:SOUR {source}')

    def sense_averages(self, mode: str, averages: int):
        return self.send(f'SENS:{mode}:AVER {averages}')

    def sense_corrections(self, mode: str, corrections: int):
        return self.send(f'SENS:{mode}:CORR {corrections}')

    def sense_mode(self, mode: str):
        return self.send(f'SENS:MODE {mode}')

    def sense_freq_det(self, mode: str, value: str):
        return self.send(f'SENS:{mode}:freq:det {value}')

    def sense_freq_exec(self):
        return self.send('SENS:FREQ:EXEC')

    def sense_freq_start(self, mode: str, freq: int):
        return self.send(f'SENS:{mode}:FREQuency:STARt {freq}')

    def sense_freq_stop(self, mode: str, freq: int):
        return self.send(f'SENS:{mode}:FREQuency:STOP {freq}')

    def sense_ppd(self, mode: str, value: int):
        return self.send(f'SENS:{mode}:PPD {value}')

    def sense_references_tune_max(self, mode: str, source: int, value: float):
        return self.send(f'SENSe:{mode}:REFerences:TUNE:MAX {source},{value}')

    def sense_reset(self, mode: str):
        self.send(f'SENS:{mode}:RES')

    def sense_smo_aperture(self, mode: str, aperture: int):
        self.send(f'SENS:{mode}:SMO:APER {aperture}')

    def sense_smo_status(self, mode: str, status: str):
        self.send(f'SENS:{mode}:SMO:STAT {status}')

    def sense_spur_omis(self, mode: str, omission: str):
        self.send(f'SENS:{mode}:SPUR:OMIS {omission}')

    def sense_spur_threshold(self, mode: str, threshold: int):
        self.send(f'SENS:{mode}:SPUR:THR {threshold}')

    # SOURCE subsystem
    def source_tune_dut_status(self, status: str):
        return self.send(f'SOURCE:TUNE:DUT:STAT {status}')

    def source_tune_dut_voltage(self, volt: float):
        return self.send(f'SOURCE:TUNE:DUT:VOLT {volt}')

    def source_supply_status(self, supply: int, status: str):
        return self.send(f'SOURCE:SUPPLY{supply}:STAT {status}')

    def source_supply_voltage(self, supply: int, volt: float):
        return self.send(f'SOURCE:SUPPLY{supply}:volt {volt}')

    # :STATUS subsystem
    def status_questionable_condition(self):
        return self.query('STAT:QUES:POW:COND?')

    # :SYSTEM subsystem
    def system_error_all(self):
        return self.query('SYSTEM:ERROR:ALL?')

    # :TRIGGER subsystem
    def trigger_init(self):
        return self.send(f'INIT')

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


