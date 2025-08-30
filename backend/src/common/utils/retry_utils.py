"""Utility functions for retry logic and exponential backoff."""

import time
import logging
from typing import Callable, Any, Optional, Union
import asyncio


class RetryUtils:
    """Utility class for retry logic with exponential backoff."""

    @staticmethod
    def exponential_backoff(
        attempt: int, base_delay: float = 1.0, max_delay: float = 60.0
    ) -> float:
        """
        Calculate exponential backoff delay.

        Args:
            attempt: Current attempt number (0-based)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds

        Returns:
            Delay in seconds
        """
        delay = base_delay * (2**attempt)
        return min(delay, max_delay)

    @staticmethod
    def wait_with_backoff(
        attempt: int, base_delay: float = 1.0, max_delay: float = 60.0
    ) -> None:
        """
        Wait with exponential backoff (synchronous).

        Args:
            attempt: Current attempt number (0-based)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
        """
        delay = RetryUtils.exponential_backoff(attempt, base_delay, max_delay)
        logger = logging.getLogger(__name__)
        logger.info(
            f"Waiting {delay:.2f} seconds before retry (attempt {attempt + 1})..."
        )
        time.sleep(delay)

    @staticmethod
    async def async_wait_with_backoff(
        attempt: int, base_delay: float = 1.0, max_delay: float = 60.0
    ) -> None:
        """
        Wait with exponential backoff (asynchronous).

        Args:
            attempt: Current attempt number (0-based)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
        """
        delay = RetryUtils.exponential_backoff(attempt, base_delay, max_delay)
        logger = logging.getLogger(__name__)
        logger.info(
            f"Waiting {delay:.2f} seconds before retry (attempt {attempt + 1})..."
        )
        await asyncio.sleep(delay)

    @staticmethod
    def retry_with_backoff(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exceptions: tuple = (Exception,),
    ) -> Any:
        """
        Retry a function with exponential backoff.

        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            exceptions: Tuple of exceptions to catch and retry on

        Returns:
            Result of the function call

        Raises:
            Last exception if all retries fail
        """
        logger = logging.getLogger(__name__)
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                if attempt == max_retries:
                    logger.error(
                        f"Function failed after {max_retries + 1} attempts: {str(e)}"
                    )
                    raise e

                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                RetryUtils.wait_with_backoff(attempt, base_delay, max_delay)

        # This should never be reached, but just in case
        if last_exception:
            raise last_exception

    @staticmethod
    async def async_retry_with_backoff(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exceptions: tuple = (Exception,),
    ) -> Any:
        """
        Retry an async function with exponential backoff.

        Args:
            func: Async function to retry
            max_retries: Maximum number of retries
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            exceptions: Tuple of exceptions to catch and retry on

        Returns:
            Result of the function call

        Raises:
            Last exception if all retries fail
        """
        logger = logging.getLogger(__name__)
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func()
                else:
                    return func()
            except exceptions as e:
                last_exception = e
                if attempt == max_retries:
                    logger.error(
                        f"Function failed after {max_retries + 1} attempts: {str(e)}"
                    )
                    raise e

                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                await RetryUtils.async_wait_with_backoff(attempt, base_delay, max_delay)

        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
