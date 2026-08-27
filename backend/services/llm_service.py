"""
LLM Service for fashion style analysis and recommendations
Supports multiple providers: OpenAI, Anthropic, Groq
"""
import os
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def analyze_style(self, prompt: str) -> Dict[str, Any]:
        """Analyze style and return structured response"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        super().__init__(api_key, model, temperature, max_tokens)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai>=1.12.0")

    def analyze_style(self, prompt: str) -> Dict[str, Any]:
        """Analyze style using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional fashion stylist and expert in clothing analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        super().__init__(api_key, model, temperature, max_tokens)
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package is required. Install with: pip install anthropic>=0.18.0")

    def analyze_style(self, prompt: str) -> Dict[str, Any]:
        """Analyze style using Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system="You are a professional fashion stylist and expert in clothing analysis. Always respond with valid JSON.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text
            # Try to parse JSON from response
            # Claude might include extra text, so we extract JSON
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return json.loads(content)

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class GroqProvider(LLMProvider):
    """Groq Llama provider"""

    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        super().__init__(api_key, model, temperature, max_tokens)
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
        except ImportError:
            raise ImportError("groq package is required. Install with: pip install groq>=0.4.0")

    def analyze_style(self, prompt: str) -> Dict[str, Any]:
        """Analyze style using Groq API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional fashion stylist and expert in clothing analysis. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise


class LLMService:
    """Main LLM service with provider factory and retry logic"""

    def __init__(self, provider: str, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 1000):
        self.provider_name = provider.lower()
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.provider = self._create_provider()

    def _create_provider(self) -> LLMProvider:
        """Factory method to create appropriate provider"""
        if self.provider_name == "openai":
            return OpenAIProvider(self.api_key, self.model, self.temperature, self.max_tokens)
        elif self.provider_name == "anthropic":
            return AnthropicProvider(self.api_key, self.model, self.temperature, self.max_tokens)
        elif self.provider_name == "groq":
            return GroqProvider(self.api_key, self.model, self.temperature, self.max_tokens)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider_name}. Supported: openai, anthropic, groq")

    def _build_prompt(
        self,
        detection_data: Optional[Dict[str, Any]] = None,
        color_data: Optional[Dict[str, Any]] = None,
        pattern_data: Optional[Dict[str, Any]] = None,
        pose_data: Optional[Dict[str, Any]] = None,
        fit_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build comprehensive prompt from all analysis data"""
        
        prompt_parts = [
            "You are a professional fashion stylist analyzing an outfit. Based on the following analysis data, provide fashion insights.",
            ""
        ]

        # Add detected items
        if detection_data and detection_data.get("detections"):
            prompt_parts.append("DETECTED ITEMS:")
            for detection in detection_data["detections"]:
                class_name = detection.get("class_name", "unknown")
                confidence = detection.get("confidence", 0) * 100
                prompt_parts.append(f"- {class_name.capitalize()} (confidence: {confidence:.1f}%)")
            prompt_parts.append("")

        # Add color and pattern information
        if color_data and color_data.get("items"):
            prompt_parts.append("COLORS & PATTERNS:")
            for item in color_data["items"]:
                class_name = item.get("class_name", "unknown")
                prompt_parts.append(f"- {class_name.capitalize()}:")
                
                # Colors
                if item.get("colors"):
                    color_strs = [
                        f"{c.get('name', 'unknown')} ({c.get('hex', '#000000')}, {c.get('percentage', 0):.1f}%)"
                        for c in item["colors"]
                    ]
                    prompt_parts.append(f"  Colors: {', '.join(color_strs)}")
                
                # Pattern
                if item.get("pattern"):
                    pattern_type = item["pattern"].get("type", "solid")
                    pattern_conf = item["pattern"].get("confidence", 0) * 100
                    prompt_parts.append(f"  Pattern: {pattern_type} ({pattern_conf:.0f}% confidence)")
            prompt_parts.append("")

        # Add pose and body measurements
        if pose_data and pose_data.get("measurements"):
            prompt_parts.append("BODY MEASUREMENTS:")
            measurements = pose_data["measurements"]
            for key, value in measurements.items():
                if value:
                    formatted_key = key.replace("_", " ").title()
                    if isinstance(value, float):
                        prompt_parts.append(f"- {formatted_key}: {value:.1f}px")
                    else:
                        prompt_parts.append(f"- {formatted_key}: {value}")
            prompt_parts.append("")

        # Add fit analysis
        if fit_data and fit_data.get("items"):
            prompt_parts.append("FIT ANALYSIS:")
            for item in fit_data["items"]:
                class_name = item.get("class_name", "unknown")
                fit_type = item.get("fit_type", "unknown")
                fit_ratio = item.get("fit_ratio", 0)
                size_estimate = item.get("size_estimate", "N/A")
                prompt_parts.append(f"- {class_name.capitalize()}: {fit_type} fit (ratio: {fit_ratio:.2f}), Estimated size: {size_estimate}")
            prompt_parts.append("")

        # Add instructions for response format
        prompt_parts.extend([
            "Based on this comprehensive analysis, provide:",
            "1. Overall style classification (e.g., streetwear, casual, formal, business casual, sporty, vintage)",
            "2. Confidence score (0-1)",
            "3. Detailed style description",
            "4. Three outfit combination suggestions that work with these items",
            "5. E-commerce search keywords (optimized for Amazon/Flipkart)",
            "6. Fashion advice and styling tips",
            "",
            "Return your response as JSON ONLY with this exact structure:",
            "{",
            '  "style": {',
            '    "type": "casual",',
            '    "confidence": 0.89,',
            '    "description": "Detailed description of the style..."',
            "  },",
            '  "suggestions": [',
            "    {",
            '      "title": "Outfit title",',
            '      "description": "How to style it",',
            '      "items": ["item1", "item2", "item3"]',
            "    }",
            "  ],",
            '  "keywords": ["keyword1", "keyword2", "keyword3", ...],',
            '  "advice": "Fashion advice and styling tips..."',
            "}"
        ])

        return "\n".join(prompt_parts)

    def analyze_style(
        self,
        detection_data: Optional[Dict[str, Any]] = None,
        color_data: Optional[Dict[str, Any]] = None,
        pattern_data: Optional[Dict[str, Any]] = None,
        pose_data: Optional[Dict[str, Any]] = None,
        fit_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze style with retry logic
        
        Args:
            detection_data: YOLO detection results
            color_data: Color and pattern extraction results
            pattern_data: (deprecated, included in color_data)
            pose_data: MediaPipe pose detection results
            fit_data: Fit analysis results
            max_retries: Maximum number of retry attempts
            
        Returns:
            Structured style analysis response
        """
        prompt = self._build_prompt(detection_data, color_data, pattern_data, pose_data, fit_data)
        
        logger.info(f"Analyzing style with {self.provider_name} ({self.model})")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        for attempt in range(max_retries):
            try:
                result = self.provider.analyze_style(prompt)
                
                # Validate response structure
                if not self._validate_response(result):
                    logger.warning(f"Invalid response structure on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        # Return a fallback response
                        return self._get_fallback_response()
                
                logger.info("Style analysis successful")
                return result

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

        return self._get_fallback_response()

    def _validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate LLM response structure"""
        if not isinstance(response, dict):
            return False
        
        # Check required fields
        if "style" not in response or not isinstance(response["style"], dict):
            return False
        
        style = response["style"]
        if "type" not in style or "confidence" not in style or "description" not in style:
            return False
        
        if "suggestions" not in response or not isinstance(response["suggestions"], list):
            return False
        
        if "keywords" not in response or not isinstance(response["keywords"], list):
            return False
        
        if "advice" not in response or not isinstance(response["advice"], str):
            return False
        
        return True

    def _get_fallback_response(self) -> Dict[str, Any]:
        """Return a fallback response when LLM fails"""
        return {
            "style": {
                "type": "casual",
                "confidence": 0.5,
                "description": "Unable to perform detailed style analysis. Please try again."
            },
            "suggestions": [
                {
                    "title": "Classic Combination",
                    "description": "Keep it simple with neutral colors and comfortable fit",
                    "items": ["Similar item in neutral color", "Comfortable bottoms", "Versatile footwear"]
                },
                {
                    "title": "Layered Look",
                    "description": "Add dimension with complementary layers",
                    "items": ["Light jacket or cardigan", "Matching accessories", "Statement piece"]
                },
                {
                    "title": "Dressed Up",
                    "description": "Elevate the look for more formal occasions",
                    "items": ["Formal blazer", "Dressy shoes", "Minimal accessories"]
                }
            ],
            "keywords": [
                "casual wear",
                "comfortable clothing",
                "everyday outfit",
                "versatile style"
            ],
            "advice": "Focus on fit, comfort, and personal style. Experiment with different combinations to find what works best for you."
        }


def create_llm_service(config) -> Optional[LLMService]:
    """
    Factory function to create LLM service from config
    
    Args:
        config: Flask config object with LLM settings
        
    Returns:
        LLMService instance or None if not configured
    """
    # Flask config can be accessed like a dict
    provider = config.get("LLM_PROVIDER") or getattr(config, "LLM_PROVIDER", None)
    
    if not provider:
        logger.warning("LLM_PROVIDER not configured")
        return None
    
    # Get API key based on provider
    api_key = None
    if provider.lower() == "openai":
        api_key = config.get("OPENAI_API_KEY") or getattr(config, "OPENAI_API_KEY", None)
    elif provider.lower() == "anthropic":
        api_key = config.get("ANTHROPIC_API_KEY") or getattr(config, "ANTHROPIC_API_KEY", None)
    elif provider.lower() == "groq":
        api_key = config.get("GROQ_API_KEY") or getattr(config, "GROQ_API_KEY", None)
    
    if not api_key:
        logger.warning(f"API key not configured for provider: {provider}")
        return None
    
    model = config.get("LLM_MODEL") or getattr(config, "LLM_MODEL", "gpt-4")
    temperature = config.get("LLM_TEMPERATURE") or getattr(config, "LLM_TEMPERATURE", 0.7)
    max_tokens = config.get("LLM_MAX_TOKENS") or getattr(config, "LLM_MAX_TOKENS", 1000)
    
    try:
        return LLMService(
            provider=provider,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
    except Exception as e:
        logger.error(f"Failed to create LLM service: {e}")
        return None
