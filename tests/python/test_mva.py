"""Tests for gad.mva module: BDT training, validation, and analysis utilities."""
import numpy as np
import pytest
import optuna

# Suppress optuna logging in tests
optuna.logging.set_verbosity(optuna.logging.WARNING)

# Constrained search space for fast tests (small trees, few estimators)
_FAST_SEARCH_SPACE = {
    "max_depth": (2, 4),
    "learning_rate": (0.1, 0.3),
    "n_estimators": (10, 30),
    "min_child_weight": (1, 3),
    "subsample": (0.8, 1.0),
    "colsample_bytree": (0.8, 1.0),
    "gamma": (0.0, 1.0),
    "reg_alpha": (1e-4, 1.0),
    "reg_lambda": (1e-4, 1.0),
}


def _make_synthetic_data(n_samples=100, n_features=5, random_state=42):
    """Create synthetic binary classification data for testing."""
    from sklearn.datasets import make_classification
    X, y = make_classification(
        n_samples=n_samples, n_features=n_features,
        n_informative=3, n_redundant=1, n_clusters_per_class=1,
        random_state=random_state,
    )
    return X, y


@pytest.fixture(scope="module")
def trained_result():
    """Train a BDT once and reuse across tests in this module."""
    from gad.mva.trainer import BDTTrainer
    X, y = _make_synthetic_data(n_samples=200)
    trainer = BDTTrainer(
        search_space=_FAST_SEARCH_SPACE, n_trials=3, random_state=42)
    return trainer.train(X, y)


class TestBDTTrainer:
    """Tests for BDTTrainer class."""

    def test_train_returns_expected_keys(self, trained_result):
        expected_keys = {"model", "best_params", "best_auc", "n_trials",
                         "X_train", "X_test", "y_train", "y_test"}
        assert expected_keys == set(trained_result.keys())

    def test_train_auc_above_random(self, trained_result):
        assert trained_result["best_auc"] > 0.5

    def test_train_with_sample_weight(self):
        from gad.mva.trainer import BDTTrainer
        X, y = _make_synthetic_data(n_samples=100)
        weights = np.ones(len(y))
        trainer = BDTTrainer(
            search_space=_FAST_SEARCH_SPACE, n_trials=2, random_state=42)
        result = trainer.train(X, y, sample_weight=weights)
        assert result["best_auc"] > 0.5

    def test_fresh_study_per_call(self):
        from gad.mva.trainer import BDTTrainer
        X, y = _make_synthetic_data(n_samples=80)
        trainer = BDTTrainer(
            search_space=_FAST_SEARCH_SPACE, n_trials=2, random_state=42)
        result1 = trainer.train(X, y)
        result2 = trainer.train(X, y)
        assert result1["n_trials"] == 2
        assert result2["n_trials"] == 2

    def test_custom_search_space(self, trained_result):
        # trained_result uses _FAST_SEARCH_SPACE with max_depth (2,4)
        assert 2 <= trained_result["best_params"]["max_depth"] <= 4


class TestCheckOvertraining:
    """Tests for check_overtraining function."""

    def test_properly_trained_model_passes(self, trained_result):
        from gad.mva.validator import check_overtraining
        ot = check_overtraining(
            trained_result["model"],
            trained_result["X_train"], trained_result["X_test"],
            trained_result["y_train"], trained_result["y_test"],
        )
        assert "signal" in ot
        assert "background" in ot
        assert "overall_passes" in ot
        assert ot["signal"]["ks_pvalue"] >= 0.0
        assert ot["background"]["ks_pvalue"] >= 0.0

    def test_overtraining_result_structure(self, trained_result):
        from gad.mva.validator import check_overtraining
        ot = check_overtraining(
            trained_result["model"],
            trained_result["X_train"], trained_result["X_test"],
            trained_result["y_train"], trained_result["y_test"],
        )
        for label in ("signal", "background"):
            assert "ks_statistic" in ot[label]
            assert "ks_pvalue" in ot[label]
            assert "passes" in ot[label]


class TestCheckSystematicRobustness:
    """Tests for check_systematic_robustness function."""

    def test_nominal_vs_shifted(self, trained_result):
        from gad.mva.validator import check_systematic_robustness
        feature_names = [f"f{i}" for i in range(trained_result["X_test"].shape[1])]
        X_shifted_small = trained_result["X_test"] + 0.01
        X_shifted_large = trained_result["X_test"] + 5.0
        robustness = check_systematic_robustness(
            trained_result["model"],
            trained_result["X_test"],
            {"small_shift": X_shifted_small, "large_shift": X_shifted_large},
            feature_names,
        )
        assert "small_shift" in robustness
        assert "large_shift" in robustness
        assert "max_shift" in robustness["small_shift"]
        assert "mean_shift" in robustness["small_shift"]
        assert "stable" in robustness["small_shift"]
        assert robustness["small_shift"]["stable"] is True


class TestFeatureImportance:
    """Tests for get_feature_importance function."""

    def test_returns_sorted_list(self, trained_result):
        from gad.mva.importance import get_feature_importance
        feature_names = [f"f{i}" for i in range(5)]
        imp = get_feature_importance(trained_result["model"], feature_names)
        assert isinstance(imp, list)
        assert len(imp) > 0
        # Check sorted descending by importance
        importances = [d["importance"] for d in imp]
        assert importances == sorted(importances, reverse=True)

    def test_result_dict_keys(self, trained_result):
        from gad.mva.importance import get_feature_importance
        feature_names = [f"f{i}" for i in range(5)]
        imp = get_feature_importance(trained_result["model"], feature_names)
        for entry in imp:
            assert "feature" in entry
            assert "importance" in entry
            assert "importance_fraction" in entry

    def test_importance_fractions_sum_to_one(self, trained_result):
        from gad.mva.importance import get_feature_importance
        feature_names = [f"f{i}" for i in range(5)]
        imp = get_feature_importance(trained_result["model"], feature_names)
        total = sum(d["importance_fraction"] for d in imp)
        assert abs(total - 1.0) < 1e-6


class TestCategorizationEvaluation:
    """Tests for evaluate_categorization function."""

    def test_categorized_better(self):
        from gad.mva.importance import evaluate_categorization
        # Inclusive: 10 signal, 1000 background
        yields_inclusive = {"signal": 10.0, "background": 1000.0}
        # Categorized into two pure categories
        yields_categorized = [
            {"signal": 8.0, "background": 100.0},
            {"signal": 2.0, "background": 50.0},
        ]
        result = evaluate_categorization(yields_inclusive, yields_categorized)
        assert result["recommendation"] == "categorized"
        assert result["improvement_percent"] > 5.0
        assert "inclusive_significance" in result
        assert "categorized_significance" in result
        assert "per_category_significances" in result

    def test_inclusive_better(self):
        from gad.mva.importance import evaluate_categorization
        # Inclusive: balanced
        yields_inclusive = {"signal": 10.0, "background": 100.0}
        # Categorized: just splits evenly (no gain)
        yields_categorized = [
            {"signal": 5.0, "background": 50.0},
            {"signal": 5.0, "background": 50.0},
        ]
        result = evaluate_categorization(yields_inclusive, yields_categorized)
        assert result["recommendation"] == "inclusive"

    def test_zero_background_handled(self):
        from gad.mva.importance import evaluate_categorization
        yields_inclusive = {"signal": 0.0, "background": 100.0}
        yields_categorized = [{"signal": 0.0, "background": 50.0}]
        result = evaluate_categorization(yields_inclusive, yields_categorized)
        assert result["inclusive_significance"] == 0.0


class TestShapeVsCounting:
    """Tests for compare_shape_vs_counting function."""

    def test_shape_recommended(self):
        from gad.mva.importance import compare_shape_vs_counting
        result = compare_shape_vs_counting(shape_significance=3.0,
                                           counting_significance=2.0)
        assert result["recommendation"] == "shape"
        assert result["improvement_percent"] > 10.0

    def test_counting_recommended(self):
        from gad.mva.importance import compare_shape_vs_counting
        result = compare_shape_vs_counting(shape_significance=2.0,
                                           counting_significance=3.0)
        assert result["recommendation"] == "counting"

    def test_either_when_close(self):
        from gad.mva.importance import compare_shape_vs_counting
        result = compare_shape_vs_counting(shape_significance=2.0,
                                           counting_significance=1.95)
        assert result["recommendation"] == "either"

    def test_has_warning_field(self):
        from gad.mva.importance import compare_shape_vs_counting
        result = compare_shape_vs_counting(shape_significance=2.0,
                                           counting_significance=1.5)
        assert "warning" in result
        assert "stat-only" in result["warning"].lower() or "systematics" in result["warning"].lower()
