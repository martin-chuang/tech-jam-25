"""Chat service with dependency injection and state machine transitions."""

import logging
import openai
import os
from typing import Generator, List, Dict

from .dtos.request.chat_request_dto import ChatRequestDto
from .dtos.response.chat_response_dto import ChatResponseDto
from ..common.statemachine.chat.chat_state_machine import ChatStatus
from ..common.statemachine.statemachine import StateMachine
from ..common.utils.file_converter import FileConverter


class ChatService:
    
    def __init__(self, privacy_service=None):
        self.privacy_service = privacy_service
        self.logger = logging.getLogger(__name__)
        self.state_machine = StateMachine()
        self.file_converter = FileConverter()
        
        # Create separate validator chains for different data types
        from .validators.chat_validators import PromptValidator, FileValidator
        from ..common.validators import ValidatorChain
        
        # Prompt validator with optional validation (allow empty prompts when files are present)
        self.prompt_validator = ValidatorChain()
        self.prompt_validator.add_validator(PromptValidator(required=False)) 
        
        self.file_validator = ValidatorChain()
        self.file_validator.add_validator(FileValidator())
        
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY', 'demo-key')
    
    def process_chat(self, request_dto: ChatRequestDto) -> dict:
        try:
            # Initialize state
            current_state = ChatStatus.PENDING
            self.logger.info(f"Starting chat processing - State: {current_state}")
            
            # Step 1: Validate request using validation chain
            current_state = self._transition_to_validated(request_dto)
            
            # Step 2: Convert files to markdown and combine with prompt
            current_state, markdown_content = self._transition_to_file_processed(request_dto)
            
            # Step 3: Anonymise request (pass prompt and file content)
            current_state, anonymised_prompt, anonymised_content = self._transition_to_anonymised(request_dto.prompt, markdown_content)
            
            # Step 4: Process with privacy service
            current_state, llm_response = self._transition_to_processed(anonymised_prompt, anonymised_content)
            
            # Step 5: Deanonymise response
            current_state, final_response = self._transition_to_deanonymised(llm_response)
            
            # Step 6: Success
            current_state = self._transition_to_success()
            
            self.logger.info(f"Chat processing completed - Final state: {current_state}")
            
            # Return just the deanonymised response string
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error processing chat: {str(e)}")
            self._transition_to_failure()
            
            # Return error message as string
            return "Something went wrong."
    
    def process_chat_streaming(self, request_dto: ChatRequestDto) -> Generator[str, None, None]:
        """
        Process chat request with streaming thoughts via SSE.
        This method uses the stream_thoughts module to yield state transitions.
        """
        from ..common.SSE.stream_thoughts import process_chat_with_thoughts
        return process_chat_with_thoughts(self, request_dto)
    
    def _transition_to_validated(self, request_dto: ChatRequestDto) -> str:
        """Transition to VALIDATED state using validation chain."""
        self.logger.info("State transition: PENDING → VALIDATED")
        
        # Validate prompt (now optional)
        if request_dto.prompt:
            prompt_error = self.prompt_validator.validate(request_dto.prompt)
            if prompt_error:
                raise ValueError(f"Prompt validation failed: {prompt_error}")
        
        # Validate files if present
        if request_dto.files:
            for file in request_dto.files:
                file_error = self.file_validator.validate(file)
                if file_error:
                    raise ValueError(f"File validation failed: {file_error}")
        
        # Ensure we have either prompt or files
        if not request_dto.prompt and not request_dto.files:
            raise ValueError("Either prompt or files must be provided")
        
        self.logger.info("Request validation successful")
        return ChatStatus.VALIDATED
    
    def _transition_to_file_processed(self, request_dto: ChatRequestDto) -> tuple[str, str]:
        """Transition to convert files to markdown."""
        self.logger.info("State transition: VALIDATED → FILE_PROCESSED")
        
        markdown_content = ""
        if request_dto.files:
            for file in request_dto.files:
                if file:
                    file_markdown = self.file_converter.convert_to_markdown(file)
                    if file_markdown:
                        markdown_content += file_markdown + "\n\n"
        
        self.logger.info(f"Files processed to markdown: {len(markdown_content)} characters")
        return "FILE_PROCESSED", markdown_content
    
    def _transition_to_anonymised(self, prompt: str, file_content: str) -> tuple[str, str, str]:
        """Transition to ANONYMISED state using privacy service transition."""
        self.logger.info("State transition: FILE_PROCESSED → ANONYMISED")
        
        if self.privacy_service:
            try:
                anonymised_prompt, anonymised_content = self.privacy_service.transition_anonymise(prompt or "", file_content)
                self.logger.info("Successfully anonymised content")
                return ChatStatus.ANONYMISED, anonymised_prompt, anonymised_content
            except Exception as e:
                self.logger.warning(f"Could not anonymise content: {e}")
        
        # Fallback to original content
        return ChatStatus.ANONYMISED, prompt or "", file_content
    
    def _transition_to_processed(self, anonymised_prompt: str, anonymised_content: str) -> tuple[str, List[Dict]]:
        """Transition to PROCESSED state using privacy service transition."""
        self.logger.info("State transition: ANONYMISED → PROCESSED")
        
        if self.privacy_service:
            try:
                llm_response = self.privacy_service.transition_process(anonymised_prompt, anonymised_content)
                self.logger.info("Privacy service processing successful")
                return ChatStatus.PROCESSED, llm_response
            except Exception as e:
                self.logger.warning(f"Privacy service processing failed: {e}")
        
        # Fallback response in expected format
        fallback_response = [
            {
                "content": anonymised_prompt,
                "role": "human"
            },
            {
                "content": "",
                "role": "ai"
            },
            {
                "content": f"Source: {{'source': 'user_input'}}\nContent: {anonymised_prompt} {anonymised_content}",
                "role": "tool"
            },
            {
                "content": f"Response to: {anonymised_prompt} {anonymised_content} | This is a fallback response.",
                "role": "ai"
            }
        ]
        
        return ChatStatus.PROCESSED, fallback_response
    
    def _transition_to_deanonymised(self, llm_response: List[Dict]) -> tuple[str, str]:
        """Transition to DEANONYMISED state using privacy service transition."""
        self.logger.info("State transition: PROCESSED → DEANONYMISED")
        
        if self.privacy_service:
            try:
                final_response = self.privacy_service.transition_deanonymise(llm_response)
                self.logger.info("Successfully deanonymised response")
                return ChatStatus.DEANONYMISED, final_response
            except Exception as e:
                self.logger.warning(f"Could not deanonymise response: {e}")
        
        # Fallback - extract content from last item manually
        if not llm_response or len(llm_response) == 0:
            final_response = "No response generated."
        else:
            # Get the last item in the list and extract its content
            last_message = llm_response[-1]
            final_response = last_message.get("content", "No response generated.")
        
        return ChatStatus.DEANONYMISED, final_response
    
    def _transition_to_success(self) -> str:
        """Transition to SUCCESS state."""
        self.logger.info("State transition: DEANONYMISED → SUCCESS")
        return ChatStatus.SUCCESS
    
    def _transition_to_failure(self) -> str:
        """Transition to FAILURE state."""
        self.logger.error("State transition: * → FAILURE")
        return ChatStatus.FAILURE
