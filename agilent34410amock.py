class Agilent34410AMock:

    def __init__(self):
        pass

    def write(self, command):
        return 'success'

    def query(self, question):
        answer = '-5'
        return answer

