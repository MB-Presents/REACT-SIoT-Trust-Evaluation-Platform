class TransactionContext:
    def __init__(self):
        self.creation_time = None
        self.trustor_location = None
        self.trustee_location = None
        self._trustor  = None
        self._trustee = None