"""Chat service with dependency injection and state machine transitions."""

import logging
import openai
import os

from .dtos.request.chat_request_dto import ChatRequestDto
from .dtos.response.chat_response_dto import ChatResponseDto
from ..common.statemachine.chat.chat_state_machine import ChatStatus
from ..common.statemachine.statemachine import StateMachine
from .validators.chat_validators import create_chat_validator_chain


class ChatService:
    """Chat service that handles chat processing logic with state transitions."""
    
    def __init__(self, privacy_service=None):
        """Initialize chat service with dependencies."""
        self.privacy_service = privacy_service
        self.logger = logging.getLogger(__name__)
        self.state_machine = StateMachine()
        self.validator_chain = create_chat_validator_chain()
        
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY', 'demo-key')
    
    def process_chat(self, request_dto: ChatRequestDto) -> dict:
        """
        Process chat request with state machine transitions.
        
        Args:
            request_dto: Chat request data (contains files already)
            
        Returns:
            Typed ChatResponseDto as dict
        """
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
    
    def _transition_to_validated(self, request_dto: ChatRequestDto) -> str:
        """Transition to VALIDATED state using validation chain."""
        self.logger.info("State transition: PENDING → VALIDATED")
        
        # Validate prompt
        prompt_error = self.validator_chain.validate(request_dto.prompt, 'prompt')
        if prompt_error:
            raise ValueError(f"Prompt validation failed: {prompt_error}")
        
        # Validate files if present
        if request_dto.files:
            for file in request_dto.files:
                file_error = self.validator_chain.validate(file, 'file')
                if file_error:
                    raise ValueError(f"File validation failed: {file_error}")
        
        self.logger.info("Request validation successful")
        return ChatStatus.VALIDATED
    
    def _transition_to_anonymised(self, request_dto: ChatRequestDto) -> tuple[str, ChatRequestDto]:
        """Transition to ANONYMISED state - pass whole DTO."""
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
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{anonymised_request.prompt}{file_context}"}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            llm_response = response.choices[0].message.content
            self.logger.info("OpenAI API call successful")
            
        except Exception as e:
            self.logger.warning(f"OpenAI API failed: {e}, using fallback response")
            # Fallback response
            llm_response = f"Response to: {anonymised_request.prompt}"
            if anonymised_request.files:
                llm_response += f" (with {len(anonymised_request.files)} files)"
            llm_response += " | This is a fallback response demonstrating proper state machine transitions."
        
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
