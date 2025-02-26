"""
Thinking Loop Utility
Implements the continuous thinking loop mechanism.
"""

import asyncio
from typing import Dict, Any, Callable
from loguru import logger

class ThinkingLoop:
    def __init__(self,
                 think_callback: Callable,
                 evaluate_callback: Callable,
                 express_callback: Callable,
                 min_interval: float = 0.1,
                 max_interval: float = 5.0):
        """Initialize the thinking loop."""
        self.think_callback = think_callback
        self.evaluate_callback = evaluate_callback
        self.express_callback = express_callback
        
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.current_interval = min_interval
        
        self.running = False
        self.task = None
        
    async def start(self):
        """Start the continuous thinking loop."""
        if self.running:
            return
            
        self.running = True
        self.task = asyncio.create_task(self._run_loop())
        logger.info("Started continuous thinking loop")
        
    async def stop(self):
        """Stop the continuous thinking loop."""
        if not self.running:
            return
            
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped continuous thinking loop")
        
    async def _run_loop(self):
        """Run the continuous thinking loop."""
        while self.running:
            try:
                # Generate thought
                thought = await self.think_callback()
                
                # Evaluate thought
                evaluation = await self.evaluate_callback(thought)
                
                # Consider expression
                if evaluation.get("should_express", False):
                    await self.express_callback(thought, evaluation)
                    
                # Adjust thinking interval based on evaluation
                self._adjust_interval(evaluation)
                
                # Wait before next iteration
                await asyncio.sleep(self.current_interval)
                
            except Exception as e:
                logger.error(f"Error in thinking loop: {e}")
                # Brief pause on error
                await asyncio.sleep(1.0)
                
    def _adjust_interval(self, evaluation: Dict[str, Any]):
        """Adjust thinking interval based on evaluation results."""
        score = evaluation.get("score", 0.5)
        
        # Increase interval for low-value thoughts
        if score < 0.3:
            self.current_interval = min(
                self.current_interval * 1.5,
                self.max_interval
            )
        # Decrease interval for high-value thoughts
        elif score > 0.7:
            self.current_interval = max(
                self.current_interval * 0.8,
                self.min_interval
            )
        # Maintain interval for moderate-value thoughts
        else:
            self.current_interval = max(
                min(self.current_interval, self.max_interval),
                self.min_interval
            )
