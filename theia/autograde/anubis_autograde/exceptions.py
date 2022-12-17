class RejectionException(Exception):
    def __init__(self, msg: str, status_code: int = 406):
        self.msg = msg
        self.status_code = status_code
        super(RejectionException, self).__init__(msg)
