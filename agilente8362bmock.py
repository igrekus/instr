class AgilentE8362BMock:

    def __init__(self):
        pass

    def write(self, command):
        return 'success'

    def query(self, question):
        answer = '42'
        return answer

