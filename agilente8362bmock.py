from instr.agilente8362b import AgilentE8362B


class AgilentE8362BMock(AgilentE8362B):

    def __init__(self, idn: str, inst=None):
        super().__init__(idn, inst)

        self._measure_num = 0

    def send(self, command):
        print(f'{self._name} send: {command}')
        return 'success'

    def query(self, question):
        answer = '-5'
        if question == 'INITiate1:CONTinuous ON;*OPC?':
            self._measure_num = 0

        if question == 'CALCulate1:DATA? FDATA':
            vals = [-5.5, -5.7, -6.0, -6.4, -6.9, -7.5, -8.0, -8.7, -9.6, -10.5]
            answer = ','.join([str(v - self._measure_num / 2) for v in vals])
            self._measure_num += 1

        print(f'{self._name} query: {question}, answer: {answer}')
        return answer

