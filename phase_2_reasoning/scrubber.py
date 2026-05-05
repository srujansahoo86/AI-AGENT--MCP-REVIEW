import re

class PIIScrubber:
    """A lightweight PII scrubber using regular expressions."""
    
    def __init__(self):
        # Regular expressions for common PII
        self.email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        # Matches basic phone numbers like (123) 456-7890, 123-456-7890, +1 123 456 7890
        self.phone_pattern = re.compile(r'(\+?\d{1,2}\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}')
        # Basic 16-digit credit card pattern
        self.cc_pattern = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
        
    def scrub(self, text: str) -> str:
        """
        Takes raw text and replaces potential PII with placeholders.
        """
        if not text:
            return text
            
        text = self.email_pattern.sub('[EMAIL]', text)
        text = self.cc_pattern.sub('[CREDIT_CARD]', text)
        text = self.phone_pattern.sub('[PHONE]', text)
        
        return text

if __name__ == "__main__":
    scrubber = PIIScrubber()
    test_str = "Contact me at john.doe@email.com or call +1 555-019-8372. My card is 1234 5678 9101 1121."
    print("Original:", test_str)
    print("Scrubbed:", scrubber.scrub(test_str))
