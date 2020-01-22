class AgilentN9030AMock:

    def __init__(self):
        pass

    def write(self, command):
        return 'success'

    def query(self, question):
        answer = '-2'
        return answer

