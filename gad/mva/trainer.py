"""BDT training with optuna Bayesian hyperparameter optimization.

Provides BDTTrainer class that wraps XGBoost with optuna TPE sampler
for automatic hyperparameter search. Designed for HEP signal/background
classification with support for weighted events.
"""
import numpy as np
import xgboost as xgb
import optuna
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score


class BDTTrainer:
    """XGBoost BDT trainer with optuna hyperparameter optimization.

    Parameters
    ----------
    search_space : dict, optional
        Hyperparameter search ranges as {name: (low, high)}.
        Uses DEFAULT_SEARCH_SPACE if not provided.
    n_trials : int
        Number of optuna optimization trials (default 100).
    random_state : int
        Random seed for reproducibility (default 42).
    """

    DEFAULT_SEARCH_SPACE = {
        "max_depth": (3, 10),
        "learning_rate": (0.01, 0.3),
        "n_estimators": (50, 500),
        "min_child_weight": (1, 10),
        "subsample": (0.5, 1.0),
        "colsample_bytree": (0.5, 1.0),
        "gamma": (0.0, 5.0),
        "reg_alpha": (1e-8, 10.0),
        "reg_lambda": (1e-8, 10.0),
    }

    def __init__(self, search_space=None, n_trials=100, random_state=42):
        self.search_space = search_space or self.DEFAULT_SEARCH_SPACE
        self.n_trials = n_trials
        self.random_state = random_state
        self.study = None
        self.best_model = None

    def _objective(self, trial, X_train, y_train, X_val, y_val,
                   sample_weight_train=None):
        """Optuna objective: train XGBoost and return validation AUC."""
        params = {
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "tree_method": "hist",
            "max_depth": trial.suggest_int(
                "max_depth", *self.search_space["max_depth"]),
            "learning_rate": trial.suggest_float(
                "learning_rate", *self.search_space["learning_rate"], log=True),
            "n_estimators": trial.suggest_int(
                "n_estimators", *self.search_space["n_estimators"]),
            "min_child_weight": trial.suggest_int(
                "min_child_weight", *self.search_space["min_child_weight"]),
            "subsample": trial.suggest_float(
                "subsample", *self.search_space["subsample"]),
            "colsample_bytree": trial.suggest_float(
                "colsample_bytree", *self.search_space["colsample_bytree"]),
            "gamma": trial.suggest_float(
                "gamma", *self.search_space["gamma"]),
            "reg_alpha": trial.suggest_float(
                "reg_alpha", *self.search_space["reg_alpha"], log=True),
            "reg_lambda": trial.suggest_float(
                "reg_lambda", *self.search_space["reg_lambda"], log=True),
            "random_state": self.random_state,
        }
        clf = xgb.XGBClassifier(**params)
        clf.fit(X_train, y_train, sample_weight=sample_weight_train,
                eval_set=[(X_val, y_val)], verbose=False)

        y_pred = clf.predict_proba(X_val)[:, 1]
        return roc_auc_score(y_val, y_pred)

    def train(self, X, y, sample_weight=None, test_size=0.2):
        """Run full training pipeline with optuna optimization.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training features.
        y : array-like of shape (n_samples,)
            Binary labels (0 or 1).
        sample_weight : array-like of shape (n_samples,), optional
            Per-event weights passed to XGBClassifier.fit.
        test_size : float
            Fraction held out for validation (default 0.2).

        Returns
        -------
        dict
            Keys: model, best_params, best_auc, n_trials,
            X_train, X_test, y_train, y_test.
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state,
            stratify=y,
        )

        w_train = None
        if sample_weight is not None:
            w_train, _ = train_test_split(
                sample_weight, test_size=test_size,
                random_state=self.random_state, stratify=y,
            )

        # Fresh study per call -- no state leakage between train() calls
        self.study = optuna.create_study(direction="maximize")
        self.study.optimize(
            lambda trial: self._objective(
                trial, X_train, y_train, X_test, y_test, w_train),
            n_trials=self.n_trials,
        )

        # Retrain best model on full training set
        best_params = dict(self.study.best_params)
        best_params.update({
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "tree_method": "hist",
            "random_state": self.random_state,
        })
        self.best_model = xgb.XGBClassifier(**best_params)
        self.best_model.fit(X_train, y_train, sample_weight=w_train)

        return {
            "model": self.best_model,
            "best_params": self.study.best_params,
            "best_auc": self.study.best_value,
            "n_trials": len(self.study.trials),
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }
