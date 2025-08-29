"""Chat service with dependency injection and state machine transitions."""

import logging
import openai
import os
from typing import Generator

from .dtos.request.chat_request_dto import ChatRequestDto
from .dtos.response.chat_response_dto import ChatResponseDto
from ..common.statemachine.chat.chat_state_machine import ChatStatus
from ..common.statemachine.statemachine import StateMachine


class ChatService:
    
    def __init__(self, privacy_service=None):
        self.privacy_service = privacy_service
        self.logger = logging.getLogger(__name__)
        self.state_machine = StateMachine()
        
        # Create separate validator chains for different data types
        from .validators.chat_validators import PromptValidator, FileValidator
        from ..common.validators import ValidatorChain
        
        self.prompt_validator = ValidatorChain()
        self.prompt_validator.add_validator(PromptValidator())
        
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
            
            # Step 2: Anonymise request (pass whole DTO)
            current_state, anonymised_request = self._transition_to_anonymised(request_dto)
            
            # Step 3: Process with OpenAI
            current_state, llm_response = self._transition_to_processed(anonymised_request)
            
            # Step 4: Deanonymise response
            current_state, final_response = self._transition_to_deanonymised(llm_response)
            
            # Step 5: Success
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
        
        # Validate prompt (allow empty prompt if files are present)
        if not request_dto.files or len(request_dto.files) == 0:
            # No files uploaded, prompt is required
            prompt_error = self.prompt_validator.validate(request_dto.prompt)
            if prompt_error:
                raise ValueError(f"Prompt validation failed: {prompt_error}")
        else:
            # Files are uploaded, prompt can be empty but still validate if provided
            if request_dto.prompt and request_dto.prompt.strip():
                # Only validate non-empty prompts for basic checks (not required check)
                if len(request_dto.prompt) > 10000:
                    raise ValueError("Prompt validation failed: Prompt cannot exceed 10,000 characters")
        
        # Validate files if present
        if request_dto.files:
            for file in request_dto.files:
                file_error = self.file_validator.validate(file)
                if file_error:
                    raise ValueError(f"File validation failed: {file_error}")
        
        self.logger.info("Request validation successful")
        return ChatStatus.VALIDATED
    
    def _transition_to_anonymised(self, request_dto: ChatRequestDto) -> tuple[str, ChatRequestDto]:
        """Transition to ANONYMISED state"""
        self.logger.info("State transition: VALIDATED → ANONYMISED")
        
        anonymised_prompt = request_dto.prompt
        if self.privacy_service:
            try:
                anonymised_prompt = self.privacy_service.anonymise_text_with_retry(request_dto.prompt)
                self.logger.info("Successfully anonymised prompt")
            except Exception as e:
                self.logger.warning(f"Could not anonymise prompt: {e}")
        
        # Create anonymised request DTO
        anonymised_request = ChatRequestDto(prompt=anonymised_prompt, files=request_dto.files)
        
        return ChatStatus.ANONYMISED, anonymised_request
    
    def _transition_to_processed(self, anonymised_request: ChatRequestDto) -> tuple[str, str]:
        """Transition to PROCESSED state with OpenAI logic."""
        self.logger.info("State transition: ANONYMISED → PROCESSED")
        
        try:
            # Prepare file context if files exist
            file_context = ""
            if anonymised_request.files:
                file_descriptions = []
                for file in anonymised_request.files:
                    if file and hasattr(file, 'filename') and file.filename:
                        file_descriptions.append(f"File: {file.filename}")
                file_context = f"\n\nFiles provided: {', '.join(file_descriptions)}"
            
            # System prompt
            system_prompt = """You are a helpful AI assistant. Provide accurate and helpful responses based on the user's prompt. If files are mentioned, acknowledge them in your response."""
            
            # Prepare user message
            user_message = anonymised_request.prompt or ""
            if file_context:
                user_message = f"{user_message}{file_context}".strip()
            
            # If no prompt and files exist, create a default message
            if not user_message.strip() and anonymised_request.files:
                user_message = f"Please analyze the following files: {', '.join([f.filename for f in anonymised_request.files if f.filename])}"
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            llm_response = response.choices[0].message.content
            self.logger.info("OpenAI API call successful")
            
        except Exception as e:
            self.logger.warning(f"OpenAI API failed: {e}, using fallback response")
            # Fallback response
            if anonymised_request.prompt:
                llm_response = f"Response to: {anonymised_request.prompt}"
            else:
                llm_response = "Response to uploaded files"
            
            if anonymised_request.files:
                llm_response += f" (with {len(anonymised_request.files)} files)"
            llm_response += " | This is a fallback response as the call to the llm failed."
        
        return ChatStatus.PROCESSED, llm_response
    
    def _transition_to_deanonymised(self, llm_response: str) -> tuple[str, str]:
        """Transition to DEANONYMISED state."""
        self.logger.info("State transition: PROCESSED → DEANONYMISED")
        
        final_response = llm_response
        if self.privacy_service:
            try:
                final_response = self.privacy_service.deanonymise_text_with_retry(llm_response)
                self.logger.info("Successfully deanonymised response")
            except Exception as e:
                self.logger.warning(f"Could not deanonymise response: {e}")
        
        return ChatStatus.DEANONYMISED, final_response
    
    def _transition_to_success(self) -> str:
        """Transition to SUCCESS state."""
        self.logger.info("State transition: DEANONYMISED → SUCCESS")
        return ChatStatus.SUCCESS
    
    def _transition_to_failure(self) -> str:
        """Transition to FAILURE state."""
        self.logger.error("State transition: * → FAILURE")
        return ChatStatus.FAILURE
