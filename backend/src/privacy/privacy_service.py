"""Privacy service for anonymisation and deanonymisation with retry logic."""

import logging
import re
from typing import Dict, List, Optional

from ..common.utils.retry_utils import RetryUtils

# NEED TO REPLACE AND INTEGRATE WITH ML LOGIC
class PrivacyService:
    """Service for handling privacy operations like anonymisation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # PII pattern mappings for anonymisation
        self._pii_mappings: Dict[str, str] = {}
        self._anonymization_counter = 0
    
    def anonymise_text_with_retry(self, text: str) -> Optional[str]:
        """Anonymise text with retry logic."""
        return RetryUtils.retry_with_backoff(
            func=lambda: self.anonymise_text(text),
            max_retries=3,
            base_delay=1.0
        )
    
    def deanonymise_text_with_retry(self, text: str) -> Optional[str]:
        """Deanonymise text with retry logic."""
        return RetryUtils.retry_with_backoff(
            func=lambda: self.deanonymise_text(text),
            max_retries=3,
            base_delay=1.0
        )
        
        for attempt in range(self.max_retries):
            try:
                return self.deanonymise_text(text)
            except Exception as e:
                self.logger.warning(
                    f"Deanonymisation attempt {attempt + 1} failed: {str(e)}"
                )
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_base * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
        
        return None
    
    def anonymise_text(self, text: str) -> str:
        """Anonymise PII in text."""
        if not text:
            return text
        
        anonymised_text = text
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        anonymised_text = self._replace_with_placeholder(
            anonymised_text, email_pattern, 'EMAIL'
        )
        
        # Phone pattern (simple US format)
        phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b'
        anonymised_text = self._replace_with_placeholder(
            anonymised_text, phone_pattern, 'PHONE'
        )
        
        # SSN pattern
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        anonymised_text = self._replace_with_placeholder(
            anonymised_text, ssn_pattern, 'SSN'
        )
        
        # Credit card pattern (basic)
        cc_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        anonymised_text = self._replace_with_placeholder(
            anonymised_text, cc_pattern, 'CREDIT_CARD'
        )
        
        # Name pattern (very basic - proper nouns)
        name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        anonymised_text = self._replace_with_placeholder(
            anonymised_text, name_pattern, 'NAME'
        )
        
        self.logger.debug(f"Anonymised text: {len(self._pii_mappings)} PII items replaced")
        return anonymised_text
    
    def deanonymise_text(self, text: str) -> str:
        """Deanonymise text by replacing placeholders with original values."""
        if not text or not self._pii_mappings:
            return text
        
        deanonymised_text = text
        
        # Replace placeholders with original values
        for placeholder, original in self._pii_mappings.items():
            deanonymised_text = deanonymised_text.replace(placeholder, original)
        
        self.logger.debug(f"Deanonymised text: {len(self._pii_mappings)} PII items restored")
        return deanonymised_text
    
    def _replace_with_placeholder(self, text: str, pattern: str, pii_type: str) -> str:
        """Replace PII matches with placeholders and store mapping."""
        matches = re.finditer(pattern, text)
        result = text
        
        for match in matches:
            original_value = match.group()
            placeholder = f"[{pii_type}_{self._anonymization_counter}]"
            self._pii_mappings[placeholder] = original_value
            result = result.replace(original_value, placeholder, 1)
            self._anonymization_counter += 1
        
        return result
    
    def clear_mappings(self) -> None:
        """Clear PII mappings (useful for new sessions)."""
        self._pii_mappings.clear()
        self._anonymization_counter = 0
    
    def get_mapping_count(self) -> int:
        """Get the number of PII mappings."""
        return len(self._pii_mappings)
