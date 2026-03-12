# gad.mva - Multivariate Analysis module
# BDT training with optuna optimization, overtraining validation,
# feature importance, categorization and shape-vs-counting evaluation.

from gad.mva.trainer import BDTTrainer
from gad.mva.validator import check_overtraining, check_systematic_robustness
from gad.mva.importance import (
    get_feature_importance,
    evaluate_categorization,
    compare_shape_vs_counting,
)

__all__ = [
    "BDTTrainer",
    "check_overtraining",
    "check_systematic_robustness",
    "get_feature_importance",
    "evaluate_categorization",
    "compare_shape_vs_counting",
]
