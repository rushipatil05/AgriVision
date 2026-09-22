from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


def get_logistic_regression_model(random_state: int = 42) -> LogisticRegression:
    """
    Returns configured Logistic Regression baseline model.
    """
    return LogisticRegression(
        max_iter=1500,
        solver="lbfgs",
        random_state=random_state
    )


def get_random_forest_model(random_state: int = 42) -> RandomForestClassifier:
    """
    Returns configured Random Forest baseline model.
    """
    return RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=random_state,
        n_jobs=-1
    )
