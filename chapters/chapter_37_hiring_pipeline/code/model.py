"""A hiring pipeline as a model document: heads, vacancies, and capability as separate stocks.

Time is in months and every level is in thousands, the units the BLS JOLTS release uses. Three
stocks carry the argument. `headcount` is people on payroll. `vacancies` is open requisitions,
drained by hiring after a fill delay. `experience` is a coflow on headcount (Chapter 17): a new
hire adds a fraction of a full contributor, the fraction rises toward one over a ramp, and a
leaver takes the average away. `effective_capability` reads that coflow, so heads and capability
are different numbers and a hiring surge lowers the second while it raises the first.

Two loops matter. A target gap opens vacancies and hires close the gap (balancing). Understaffing
raises workload, workload raises quits, and quits reopen the gap (reinforcing). The `clock` stock
is a counter that lets the target grow with time; the critic flags it as a stock with no outflow,
and that is what it is.

Nothing here is fitted. Chapter 37's calibrate module fits three of these parameters against the
record and marks them inferred.
"""

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable

JOLTS = "BLS JOLTS and CES, seasonally adjusted, January 2015, data/bls_jolts/jolts_monthly.csv"

# Values read from the committed record for January 2015 and the 2015 to 2019 mean. They are
# observed in the sense that a person can open the CSV and find them; the CSV vintage is fixed
# by the manifest checksum.
HEADCOUNT_2015_01 = 140568.0
VACANCIES_2015_01 = 5344.0
FILL_TIME_2015_2019 = 1.152          # mean of openings / hires, months
LAYOFF_RATE_2015_2019 = 0.01472      # mean of (separations - quits) / employment, per month

# Assumed values, with the reason each is where it is.
INITIAL_CAPABILITY = 0.4             # a new hire counts as this fraction of a seasoned one
NORMAL_CAPABILITY_SHARE = 0.9        # the share at which workload reads as one
RAMP_TIME = 6.0                      # months for a hire to reach a seasoned contribution
GAP_CLOSING_TIME = 3.0               # months over which a target gap is turned into vacancies
QUIT_SENSITIVITY = 2.0               # quit rate rises this many times the excess workload
BASE_QUIT_RATE = 0.02                # per month, before the fit moves it
TARGET_GROWTH = 0.0012               # per month, before the fit moves it


def document(target_step: float = 0.0) -> ModelDocument:
    """The hiring pipeline with unfitted parameters. `target_step` raises the target at month 0."""
    variables = [
        Variable("headcount", "stock", "thousand persons", value=HEADCOUNT_2015_01,
                 evidence="observed", note=f"CES total nonfarm employment, {JOLTS}"),
        Variable("vacancies", "stock", "thousand openings", value=VACANCIES_2015_01,
                 evidence="observed", note=f"JOLTS job openings level, {JOLTS}"),
        Variable("experience", "stock", "thousand effective persons",
                 value=NORMAL_CAPABILITY_SHARE * HEADCOUNT_2015_01, evidence="assumed",
                 note="headcount times the normal capability share; no observed counterpart"),
        Variable("clock", "stock", "months", value=0.0, evidence="observed",
                 note="months since January 2015; a counter, so it has no outflow by design"),
        Variable("tick", "flow", "months/month", equation="1", target="clock", sign=1),
        # parameters
        Variable("target_base", "parameter", "thousand persons", value=HEADCOUNT_2015_01,
                 evidence="observed", note=f"the target starts at the January 2015 level, {JOLTS}"),
        Variable("target_step", "parameter", "fraction", value=target_step, evidence="assumed",
                 note="a policy scenario: how far above the record the target is set at month 0"),
        Variable("target_growth", "parameter", "1/month", value=TARGET_GROWTH,
                 evidence="assumed", note="fitted by calibrate.py"),
        Variable("fill_time", "parameter", "months", value=FILL_TIME_2015_2019,
                 evidence="observed",
                 note=f"mean openings divided by hires, 2015 to 2019, {JOLTS}"),
        Variable("gap_closing_time", "parameter", "months", value=GAP_CLOSING_TIME,
                 evidence="assumed", note="how quickly a target gap becomes open requisitions"),
        Variable("base_quit_rate", "parameter", "1/month", value=BASE_QUIT_RATE,
                 evidence="assumed", note="fitted by calibrate.py"),
        Variable("quit_sensitivity", "parameter", "dimensionless", value=QUIT_SENSITIVITY,
                 evidence="assumed", note="quit rate multiplier per unit of excess workload"),
        Variable("layoff_rate", "parameter", "1/month", value=LAYOFF_RATE_2015_2019,
                 evidence="observed",
                 note=f"mean of layoffs, discharges and other separations over employment, "
                      f"{JOLTS}"),
        Variable("initial_capability", "parameter", "dimensionless", value=INITIAL_CAPABILITY,
                 evidence="assumed", note="a new hire's contribution as a share of a seasoned one"),
        Variable("ramp_time", "parameter", "months", value=RAMP_TIME, evidence="assumed",
                 note="fitted by calibrate.py; the record barely constrains it"),
        Variable("normal_capability_share", "parameter", "dimensionless",
                 value=NORMAL_CAPABILITY_SHARE, evidence="assumed",
                 note="experience over headcount at which workload reads as one"),
        # auxiliaries
        Variable("target_headcount", "auxiliary", "thousand persons",
                 equation="target_base * (1 + target_step) * exp(target_growth * clock)"),
        Variable("effective_capability", "auxiliary", "thousand effective persons",
                 equation="experience", note="the exported artifact: capability, not heads"),
        Variable("workload", "auxiliary", "dimensionless",
                 equation="target_headcount * normal_capability_share"
                          " / max(effective_capability, 1)"),
        Variable("quit_rate", "auxiliary", "1/month",
                 equation="base_quit_rate * (1 + quit_sensitivity * max(0, workload - 1))"),
        # flows on headcount
        Variable("hires", "flow", "thousand persons/month", equation="vacancies / fill_time",
                 target="headcount", sign=1),
        Variable("quits", "flow", "thousand persons/month", equation="headcount * quit_rate",
                 target="headcount", sign=-1),
        Variable("layoffs", "flow", "thousand persons/month", equation="headcount * layoff_rate",
                 target="headcount", sign=-1),
        # flows on vacancies
        Variable("vacancies_opened", "flow", "thousand openings/month",
                 equation="max(0, (target_headcount - headcount) / gap_closing_time"
                          " + quits + layoffs)",
                 target="vacancies", sign=1),
        Variable("vacancies_filled", "flow", "thousand openings/month", equation="hires",
                 target="vacancies", sign=-1),
        # flows on the experience coflow
        Variable("experience_hired", "flow", "thousand effective persons/month",
                 equation="hires * initial_capability", target="experience", sign=1),
        Variable("learning", "flow", "thousand effective persons/month",
                 equation="max(0, headcount - experience) / ramp_time", target="experience",
                 sign=1),
        Variable("experience_lost", "flow", "thousand effective persons/month",
                 equation="(quits + layoffs) * experience / max(headcount, 1)",
                 target="experience", sign=-1),
    ]
    return ModelDocument(name="hiring_pipeline", version="1.0.0", variables=variables,
                         horizon=120, horizon_unit="month", time_step=1.0)


def effective_capability(result) -> list[float]:
    """The exported artifact: the capability path of a run, in thousand effective persons."""
    return list(result.series["effective_capability"])


def capability_share(result) -> list[float]:
    """Effective capability over headcount, the number no payroll report carries."""
    return [c / max(h, 1e-9) for c, h in
            zip(result.series["effective_capability"], result.series["headcount"])]
