import numpy as np
import pandas as pd
import cvxpy as cp


def optimize_portfolio(returns: pd.DataFrame, target_return: float,
                       min_weight: float = None, max_weight: float = None,
                       use_bounds: bool = False):
    mu = returns.mean().values
    Sigma = returns.cov().values
    n = len(mu)

    x = cp.Variable(n)
    risk = cp.quad_form(x, Sigma)

    constraints = [cp.sum(x) == 1, x >= 0, mu @ x >= target_return]

    if use_bounds and min_weight is not None and max_weight is not None:
        constraints.append(x >= min_weight)
        constraints.append(x <= max_weight)

    problem = cp.Problem(cp.Minimize(risk), constraints)
    try:
        problem.solve()
        if x.value is None:
            return None
        weights = pd.Series(x.value, index=returns.columns)
        expected_return = mu @ x.value
        risk_value = np.sqrt(x.value @ Sigma @ x.value)
        return weights, expected_return, risk_value
    except:
        return None
