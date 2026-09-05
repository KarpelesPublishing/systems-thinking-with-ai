"""A subscription business with an onboarding delay and a quality curve.

Both new document kinds in one model: Chapter 16's delay between signing a
customer and that customer being productive for referral, and Chapter 15's
curve for how service quality falls as load rises. The reinforcing loop is
referral; the balancing loop is quality driving churn.
"""

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable

# Quality against load, measured at four operating points during last year.
QUALITY_AGAINST_LOAD = ((0.0, 1.0), (0.8, 0.95), (1.2, 0.72), (2.5, 0.40))


def subscription_growth(referral_rate: float = 0.09, staff: float = 12.0) -> ModelDocument:
    """Referral grows the base; load erodes the quality that referral depends on."""
    return ModelDocument("subscription_growth", "1.0.0", horizon=60, horizon_unit="week",
                         variables=[
        Variable("customers", "stock", "customers", value=250.0,
                 evidence="observed", note="billing system, 2026-08-01"),
        Variable("staff", "parameter", "people", value=staff, evidence="observed",
                 note="rota, 2026-08-01"),
        Variable("per_head", "parameter", "customers/person", value=30.0, evidence="inferred",
                 note="from the last two quarters of support volume"),
        Variable("referral_rate", "parameter", "1/week", value=referral_rate, evidence="assumed"),
        Variable("churn_base", "parameter", "1/week", value=0.02, evidence="inferred",
                 note="from the churn series"),
        Variable("capacity", "auxiliary", "customers", "staff * per_head"),
        Variable("load", "auxiliary", "dimensionless", "customers / capacity"),
        Variable("quality", "lookup", "dimensionless", "load",
                 points=QUALITY_AGAINST_LOAD, evidence="observed",
                 note="four operating points measured over the last year"),
        # Referrals are made by customers who have been onboarded, which takes time.
        Variable("signing", "auxiliary", "customers/week", "customers * referral_rate * quality"),
        Variable("onboarded", "delay", "customers/week", "signing", delay_time=6.0),
        Variable("joining", "flow", "customers/week", "onboarded", target="customers", sign=1),
        Variable("leaving", "flow", "customers/week",
                 "customers * churn_base * (2.0 - quality)", target="customers", sign=-1),
    ])
