"""
Async LLM wrapper for parallel processing
Enables 3-6x faster learning guide generation through concurrent API calls
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class AsyncLLMService:
    """Async wrapper for LLM API calls"""

    def __init__(self, api_key: str, model: str, provider: str = "openai"):
        """
        Initialize async LLM service

        Args:
            api_key: API key for the provider
            model: Model name (e.g., 'gpt-4', 'claude-3-sonnet')
            provider: Provider name ('openai', 'anthropic', 'ollama', 'google')
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider.lower()
        self.session = None

        # Provider-specific configurations
        self.api_configs = {
            "openai": {
                "base_url": "https://api.openai.com/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com/v1/messages",
                "headers": {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
            },
            "ollama": {
                "base_url": "http://localhost:11434/api/generate",
                "headers": {"Content-Type": "application/json"}
            }
        }

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _format_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Format request based on provider"""
        if self.provider == "openai":
            return {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000)
            }
        elif self.provider == "anthropic":
            # Claude uses different format
            system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
            user_messages = [m for m in messages if m["role"] != "system"]

            return {
                "model": self.model,
                "system": system_msg,
                "messages": user_messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000)
            }
        elif self.provider == "ollama":
            # Ollama local format
            prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
            return {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }

    def _extract_response(self, response_data: Dict[str, Any]) -> str:
        """Extract text from provider-specific response"""
        try:
            if self.provider == "openai":
                return response_data["choices"][0]["message"]["content"]
            elif self.provider == "anthropic":
                return response_data["content"][0]["text"]
            elif self.provider == "ollama":
                return response_data["response"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract response: {e}")
            return ""

    async def call(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        retry_count: int = 3
    ) -> Optional[str]:
        """
        Make async LLM API call with retry logic

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            retry_count: Number of retries on failure

        Returns:
            LLM response text or None on failure
        """
        if not self.session:
            raise RuntimeError("AsyncLLMService must be used as async context manager")

        config = self.api_configs.get(self.provider)
        if not config:
            logger.error(f"Unsupported provider: {self.provider}")
            return None

        request_data = self._format_request(
            messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Retry logic with exponential backoff
        for attempt in range(retry_count):
            try:
                logger.debug(f"LLM API call (attempt {attempt + 1}/{retry_count})")

                async with self.session.post(
                    config["base_url"],
                    headers=config["headers"],
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = self._extract_response(data)
                        logger.info(f"LLM call successful ({len(result)} chars)")
                        return result
                    elif response.status == 429:  # Rate limit
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Rate limit hit, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")

            except asyncio.TimeoutError:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                await asyncio.sleep(2 ** attempt)

            except aiohttp.ClientError as e:
                logger.error(f"Client error: {e}")
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.exception(f"Unexpected error: {e}")
                return None

        logger.error(f"All retry attempts failed for LLM call")
        return None

    async def batch_call(
        self,
        request_list: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[Optional[str]]:
        """
        Make multiple LLM calls concurrently with rate limiting

        Args:
            request_list: List of dicts with 'messages', 'temperature', etc.
            max_concurrent: Maximum concurrent requests

        Returns:
            List of responses (None for failed requests)
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def bounded_call(request: Dict[str, Any]) -> Optional[str]:
            async with semaphore:
                return await self.call(**request)

        logger.info(f"Starting batch of {len(request_list)} LLM calls")
        start_time = asyncio.get_event_loop().time()

        results = await asyncio.gather(
            *[bounded_call(req) for req in request_list],
            return_exceptions=True
        )

        elapsed = asyncio.get_event_loop().time() - start_time
        logger.info(f"Batch completed in {elapsed:.2f}s ({len(request_list)/elapsed:.2f} req/s)")

        # Convert exceptions to None
        return [r if not isinstance(r, Exception) else None for r in results]


# Convenience functions for common use cases
async def generate_enhancements_parallel(
    api_key: str,
    model: str,
    provider: str,
    content: str,
    agent_prompt: str
) -> Dict[str, Optional[str]]:
    """
    Generate all 10 learning enhancements in parallel

    Args:
        api_key: LLM API key
        model: Model name
        provider: Provider name
        content: Note content to enhance
        agent_prompt: System prompt for agent

    Returns:
        Dict with enhancement names as keys, results as values
    """
    async with AsyncLLMService(api_key, model, provider) as llm:
        # Define all enhancement requests
        requests = [
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Generate a TL;DR summary (3-5 bullet points) for:\n{content}"}
                ],
                "temperature": 0.3
            },
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Extract 5-10 key concept tags from:\n{content}"}
                ],
                "temperature": 0.3
            },
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Create a Mermaid diagram for:\n{content}"}
                ],
                "temperature": 0.5
            },
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Generate 5-7 review questions for:\n{content}"}
                ],
                "temperature": 0.6
            },
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Create 8-10 flashcards for:\n{content}"}
                ],
                "temperature": 0.5
            },
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Identify 3-5 related concepts to explore:\n{content}"}
                ],
                "temperature": 0.6
            },
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Suggest 3-5 learning resources for:\n{content}"}
                ],
                "temperature": 0.5
            },
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Provide learning insights and mental models for:\n{content}"}
                ],
                "temperature": 0.7
            },
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Add clarifying comments for:\n{content}"}
                ],
                "temperature": 0.5
            },
            {
                "messages": [
                    {"role": "system", "content": agent_prompt},
                    {"role": "user", "content": f"Generate a learning path (next steps) for:\n{content}"}
                ],
                "temperature": 0.6
            }
        ]

        # Execute all requests in parallel
        results = await llm.batch_call(requests, max_concurrent=5)

        # Map results to enhancement names
        enhancement_names = [
            "tldr", "tags", "diagram", "quiz", "flashcards",
            "related_concepts", "resources", "insights", "comments", "learning_path"
        ]

        return dict(zip(enhancement_names, results))


# Example usage
if __name__ == "__main__":
    async def test_async_llm():
        """Test the async LLM service"""
        # This is just an example - replace with actual API key
        test_content = """
        Neural networks consist of layers: input, hidden, and output.
        Each connection has a weight that gets adjusted during training.
        Backpropagation is the algorithm used to update these weights.
        """

        results = await generate_enhancements_parallel(
            api_key="your-api-key",
            model="gpt-4",
            provider="openai",
            content=test_content,
            agent_prompt="You are a learning mentor AI."
        )

        print("Generated enhancements:")
        for name, result in results.items():
            print(f"\n{name.upper()}:")
            print(result[:200] if result else "Failed")

    # Run the test
    asyncio.run(test_async_llm())
