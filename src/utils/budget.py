import datetime
from src.strategies.exceptions import BudgetExceededError

class BudgetGuard:
    BUDGET_CAP = 0.50  # USD per document
    MODEL_PRICING = {
        'gpt-4o': 0.005,  # $/1k tokens
        'gemini-pro-vision': 0.003,
        # Add more models as needed
    }

    def __init__(self, model_name: str, avg_tokens_per_page: int = 1200):
        self.model_name = model_name
        self.price_per_1k = self.MODEL_PRICING.get(model_name, 0.005)
        self.avg_tokens_per_page = avg_tokens_per_page

    def check_budget(self, page_count: int):
        est_tokens = page_count * self.avg_tokens_per_page
        est_cost = (est_tokens / 1000) * self.price_per_1k
        if est_cost > self.BUDGET_CAP:
            raise BudgetExceededError(f"Estimated cost ${est_cost:.2f} exceeds cap ${self.BUDGET_CAP:.2f}")
        return est_cost
