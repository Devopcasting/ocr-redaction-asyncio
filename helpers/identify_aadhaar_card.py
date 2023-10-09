import re

class IdentifyAadhaarCard:
    def __init__(self, clean_text: list) -> None:
        self.clean_text = clean_text
        # Search keyword for Aadhaar card
        self.aadhaar_card_identifiers = ["government", "government of india", "male", "female", "help@uidal.gov.in", 
                                         "www.uidal.gov.in", "UNIQUE IDENTIFICATION AUTHORITY OF INDIA"]
        self.aadhaar_card_identifiers_front = ["government", "government of india", "male", "female"]
        self.aadhaar_card_identifiers_back = ["help@uidal.gov.in", "www.uidal.gov.in", "unique identification authority of india"]
    
    # func: check for valid aadhaar card
    def check_aadhaar_card(self):
        for i in self.clean_text:
            for k in i.split():
                if k.lower() in self.aadhaar_card_identifiers:
                    return True
        return False
    
    # func: check for aadhaar card front or back side
    def check_aadhaar_front(self):
        for i in self.clean_text:
            for k in i.split():
                if k.lower() in self.aadhaar_card_identifiers_front:
                    return True
        return False