class JackToken:
    def __init__(self, token, token_type):
        self.token = token
        self.type = token_type
    
    def get_token(self):
        return self.token
    
    def get_token_type(self):
        return self.type
    
    def set_token_type(self, token_type):
        self.type = token_type