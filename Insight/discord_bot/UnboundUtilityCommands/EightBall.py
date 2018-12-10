from .UnboundCommandBase import *


class EightBall(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.responses = list(self.__response_generator())

    def __response_generator(self):
        fname = '8ball_responses.txt'
        responses = ['Yes', 'No', 'Maybe']
        try:
            with open(fname, 'r') as f:
                for l in f:
                    yield l.strip()
        except FileNotFoundError:
            try:
                with open(fname, 'w') as f:
                    print("Creating default 8ball response file: '{}'. You can add additional by editing the "
                          "file.".format(fname))
                    for r in responses:
                        f.write('{}\n'.format(r))
            except Exception as ex:
                print(ex)
                traceback.print_exc()
            yield from responses
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            yield from responses

    async def get_text(self, message_text: str)->str:
        return str(random.choice(self.responses))


