from app.service.presidio_service import presidio_anonymize


class AnonymizeEncryptor:
    def __init__(self, presidio_engine, encryption_engine):
        self.presidio_engine = presidio_engine
        self.encryption_engine = encryption_engine

    def anonymize_and_encrypt(self, text):
        """
        Anonymizes the input text using Presidio and then encrypts the anonymized text.
        Returns the encrypted text.
        """
        anonymized_text = presidio_anonymize(text, self.presidio_engine)
        encrypted_text = self.encryption_engine.encrypt(anonymized_text)
        return encrypted_text
