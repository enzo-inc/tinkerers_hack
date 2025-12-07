"""Screenshot analysis using OpenAI's vision model with structured outputs."""

import logging
from openai import OpenAI

from .config import MODEL_NAME, get_openai_client
from .logging_config import log_openai_request, log_openai_response
from .models import StateUpdate

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an AI assistant analyzing screenshots from the video game Elden Ring to track game state.

Your task is to examine each screenshot and determine if it contains information about:
1. **Player Location**: Look for area names displayed in the top-left corner when entering new areas, grace site names, or recognizable landmarks. Location names in Elden Ring include regions like "Limgrave", "Liurnia of the Lakes", "Caelid", "Altus Plateau", "Mountaintops of the Giants", and specific locations like "Stormveil Castle", "Raya Lucaria Academy", "Roundtable Hold", etc.

2. **Inventory/Equipment**: Look for inventory screens, equipment menus, or item pickup notifications. When you see an inventory screen, list the visible items.

Guidelines:
- Return "noop" if the screenshot shows normal gameplay without location indicators or inventory screens
- Only report location changes when you see clear location text or unmistakable landmarks
- Only report inventory when an actual inventory/equipment menu is open
- Be conservative - if you're not sure, return "noop"
- Include brief reasoning for your decision

Common UI elements in Elden Ring:
- Location names appear briefly in the bottom-center or top-left when entering new areas
- Grace sites show their names when resting
- Inventory/Equipment screens have a dark background with item icons and descriptions
- Item pickups show a small notification at the bottom of the screen"""


class ScreenshotAnalyzer:
    """Analyzes game screenshots using GPT vision model."""
    
    def __init__(self, client: OpenAI | None = None):
        """Initialize analyzer with OpenAI client.
        
        Args:
            client: OpenAI client instance. If None, creates one from config.
        """
        self.client = client or get_openai_client()
        self.model = MODEL_NAME
    
    def analyze(self, image_base64: str) -> StateUpdate:
        """Analyze a screenshot and return state update.
        
        Args:
            image_base64: Base64-encoded PNG image
            
        Returns:
            StateUpdate with detected changes or noop
        """
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this Elden Ring screenshot and determine if there's any game state to update."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        # Log the request
        log_openai_request(logger, self.model, messages, StateUpdate)
        
        logger.debug(f"Sending request to OpenAI model: {self.model}")
        
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=StateUpdate,
        )
        
        parsed_result = response.choices[0].message.parsed
        
        # Log the response
        log_openai_response(logger, response, parsed_result)
        
        return parsed_result
