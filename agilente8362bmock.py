from instr.agilente8362b import AgilentE8362B


class AgilentE8362BMock(AgilentE8362B):

    def __init__(self, idn: str, inst=None):
        super().__init__(idn, inst)

        self._measure_num = 0

    def send(self, command):
        print(f'{self._name} send: {command}')
        return 'success'

    def query(self, question):
        # 51 data points:
        answer = '-5'
        if question == 'INITiate1:CONTinuous ON;*OPC?':
            self._measure_num = 0

        if question == 'CALCulate1:DATA? FDATA':
            vals = [-6.35922600000E+001, -7.54481400000E+001, -7.35482500000E+001, -8.14576800000E+001, -8.03099400000E+001, -8.30356500000E+001, -8.11258500000E+001, -9.07190200000E+001, -8.31870700000E+001, -8.20321000000E+001, -9.37882100000E+001, -8.10723300000E+001, -8.00839900000E+001, -7.67275500000E+001, -7.49358000000E+001, -8.10655400000E+001, -9.38921500000E+001, -8.53814600000E+001, -8.95478200000E+001, -7.70012600000E+001, -9.67159200000E+001, -8.83523900000E+001, -9.14728800000E+001, -9.03211200000E+001, -7.56316300000E+001, -8.44623800000E+001, -8.35657000000E+001, -7.65543500000E+001, -8.66997800000E+001, -8.44859200000E+001, -8.86205700000E+001, -8.76242500000E+001, -8.10742600000E+001, -8.81784000000E+001, -8.65285800000E+001, -8.87762400000E+001, -9.69573400000E+001, -8.96282400000E+001, -8.35469900000E+001, -8.45129500000E+001, -8.66145200000E+001, -1.05780700000E+002, -8.88681300000E+001, -1.02219600000E+002, -9.38262800000E+001, -8.69898800000E+001, -8.82864800000E+001, -9.27375400000E+001, -8.67494400000E+001, -8.46078600000E+001, -8.83278700000E+001]
            answer = ','.join([str(v - self._measure_num / 4) for v in vals])
            self._measure_num += 1
        print(f'{self._name} query: {question}, answer: {answer}')
        return answer

