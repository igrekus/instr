from instr.agilente8362b import AgilentE8362B


class AgilentE8362BMock(AgilentE8362B):

    def __init__(self, idn: str, inst=None):
        super().__init__(idn, inst)

    def send(self, command):
        print(f'{self._name} send: {command}')
        return 'success'

    def query(self, question):
        answer = '-5'
        print(f'{self._name} query: {question}, answer: {answer}')
        return answer

