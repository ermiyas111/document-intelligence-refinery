class LowConfidenceError(Exception):
    """Raised when extraction confidence is below the threshold."""
    pass

class BudgetExceededError(Exception):
    """Raised when the extraction cost exceeds the allowed budget."""
    pass
