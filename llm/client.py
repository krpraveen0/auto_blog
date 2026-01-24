"""
Perplexity AI client wrapper
Uses OpenAI SDK format (Perplexity API is compatible)
"""

import os
import time
from typing import Dict, List, Optional
from openai import OpenAI
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PerplexityClient:
    """Client for Perplexity AI API"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model = config.get('model', 'sonar-pro')
        self.api_timeout = config.get('api_timeout', 60)
        self.max_retries = config.get('max_retries', 3)
        
        # Generation parameters
        gen_params = config.get('generation_params', {})
        self.temperature = gen_params.get('temperature', 0.3)
        self.max_tokens = gen_params.get('max_tokens', 2000)
        self.top_p = gen_params.get('top_p', 0.9)
        
        # Rate limiting
        rate_limit = config.get('rate_limiting', {})
        self.requests_per_minute = rate_limit.get('requests_per_minute', 20)
        self.last_request_time = 0
        
        # Initialize OpenAI client with Perplexity API
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")
        if not api_key.startswith("pplx-"):
            raise ValueError("PERPLEXITY_API_KEY must start with 'pplx-' (check the secret value)")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
        
        logger.info(f"Initialized Perplexity client with model: {self.model}")
    
    def generate(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response using Perplexity API
        
        Args:
            system_prompt: System instruction
            user_prompt: User message
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            Generated text response
        """
        self._enforce_rate_limit()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Generating response (attempt {attempt + 1}/{self.max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                    top_p=self.top_p
                )
                
                content = response.choices[0].message.content
                logger.debug(f"Generated {len(content)} characters")
                
                return content
                
            except Exception as e:
                self._log_api_error(e, attempt)
                
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed after {self.max_retries} attempts: {e}")
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        if self.requests_per_minute <= 0:
            return
        
        min_interval = 60.0 / self.requests_per_minute
        elapsed = time.time() - self.last_request_time
        
        if elapsed < min_interval:
            sleep_time = min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def batch_generate(
        self,
        system_prompt: str,
        user_prompts: List[str]
    ) -> List[str]:
        """
        Generate responses for multiple prompts
        
        Args:
            system_prompt: System instruction (same for all)
            user_prompts: List of user messages
            
        Returns:
            List of generated responses
        """
        responses = []
        
        for i, prompt in enumerate(user_prompts):
            logger.info(f"Generating response {i + 1}/{len(user_prompts)}")
            response = self.generate(system_prompt, prompt)
            responses.append(response)
        
        return responses

    def _log_api_error(self, error: Exception, attempt: int) -> None:
        """Provide clearer context on API failures."""
        err_text = str(error)
        logger.error(f"API error (attempt {attempt + 1}): {err_text}")

        # Detect common auth failures that return HTML 401 pages
        lowered = err_text.lower()
        if "401" in lowered or "authorization required" in lowered or "<html>" in lowered:
            logger.error(
                "Perplexity authentication failed. Verify PERPLEXITY_API_KEY is valid, starts with 'pplx-', "
                "and is correctly configured in GitHub Actions secrets."
            )
        elif "timeout" in lowered:
            logger.error("Perplexity request timed out; consider increasing api_timeout or retries.")
