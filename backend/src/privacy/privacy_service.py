"""Privacy service for anonymisation and deanonymisation with retry logic."""

import logging
import re
from typing import Dict, List, Optional, Tuple

from ..common.utils.retry_utils import RetryUtils

# NEED TO REPLACE AND INTEGRATE WITH ML LOGIC but keep same function
class PrivacyService:
    """Service for handling privacy operations like anonymisation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # PII pattern mappings for anonymisation
        self._pii_mappings: Dict[str, str] = {}
        self._anonymization_counter = 0
    
    def transition_anonymise(self, prompt: str, file_content: str = "") -> Tuple[str, str]:
        """
        Transition function for anonymisation step.
        
        Args:
            prompt: User prompt text
            file_content: Markdown content from files
            
        Returns:
            Tuple of (anonymised_prompt, anonymised_file_content)
        """
        combined_text = f"{prompt}\n\n{file_content}" if file_content else prompt
        anonymised_combined = self.anonymise_text_with_retry(combined_text)
        
        if not anonymised_combined:
            self.logger.warning("Anonymisation failed, using original text")
            return prompt, file_content
        
        # Split back into prompt and file content
        if file_content:
            parts = anonymised_combined.split('\n\n', 1)
            if len(parts) == 2:
                return parts[0], parts[1]
            else:
                return anonymised_combined, ""
        else:
            return anonymised_combined, ""
    
    def transition_process(self, anonymised_prompt: str, anonymised_file_content: str = "") -> List[Dict]:
        """
        Transition function for processing step.
        This simulates the privacy service processing and returns the expected list format.
        
        Args:
            anonymised_prompt: Anonymised prompt
            anonymised_file_content: Anonymised file content
            
        Returns:
            List of conversation messages in the expected format
        """
        # Simulate processing - in real implementation this would call the actual ML pipeline
        combined_content = f"{anonymised_prompt}\n\n{anonymised_file_content}" if anonymised_file_content else anonymised_prompt
        
        # Mock response format as specified
        llm_response = [
            {
                "content": anonymised_prompt,
                "role": "human"
            },
            {
                "content": "",
                "role": "ai"
            },
            {
                "content": f"Source: {{'source': 'user_input'}}\nContent: {combined_content}",
                "role": "tool"
            },
            {
                "content": f"Based on your input: {combined_content}\n\n.",
                "role": "ai"
            }
        ]
        
        return llm_response
    
    def transition_deanonymise(self, llm_response: List[Dict]) -> str:
        """
        Transition function for deanonymisation step.
        
        Args:
            llm_response: List of conversation messages from privacy service
            
        Returns:
            Final deanonymised response string
        """
        # Extract content from the last item in the list
        if not llm_response or len(llm_response) == 0:
            self.logger.warning("Empty response list received")
            return "No response generated."
        
        # Get the last item in the list
        last_message = llm_response[-1]
        
        # Extract the content from the last message
        final_ai_content = last_message.get("content", "")
        
        if not final_ai_content:
            self.logger.warning("No content found in last message of response")
            return "No response generated."
        
        # Deanonymise the content
        deanonymised_response = self.deanonymise_text_with_retry(final_ai_content)
        
        if not deanonymised_response:
            self.logger.warning("Deanonymisation failed, using original content")
            return final_ai_content
        
        return deanonymised_response