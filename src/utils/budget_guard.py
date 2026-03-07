from src.strategies.exceptions import BudgetExceededError
from src.utils.config import RefinerySettings

class BudgetGuard:
    def __init__(self):
        self.budget_cap = RefinerySettings.get().rules.budgetary_guardrails.max_cost_per_doc_usd
        self.model_pricing = RefinerySettings.get().rules.budgetary_guardrails.model_pricing
        self.current_spend = 0.0

    def check_and_update(self, model_name: str, tokens: int):
        price_per_1k = self.model_pricing.get(model_name, 0.005)
        cost = (tokens / 1000) * price_per_1k
        if self.current_spend + cost > self.budget_cap:
            raise BudgetExceededError(f"Budget cap exceeded: {self.current_spend + cost:.2f} > {self.budget_cap:.2f}")
        self.current_spend += cost
        return cost
