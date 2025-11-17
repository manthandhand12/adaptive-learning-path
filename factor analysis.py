# factor_analysis_survey.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from factor_analyzer import FactorAnalyzer, calculate_bartlett_sphericity, calculate_kmo
from sklearn.impute import SimpleImputer

# 1) Load sheet
fn = "final response( project).xlsx"  # change if needed
df = pd.read_excel(fn, sheet_name=0)

# 2) Select columns relevant to factor analysis
# Adjust names if your sheet uses slightly different column headers.
# Here we pick likely survey columns from the sheet you provided; edit list to match exact headers.
candidate_cols = [
    "Would offline learning content be useful for you?",
    "How much time do you spend on learning apps daily?",
    "Would you like personalized recommendations for lessons?",
    "Do you want your progress to be tracked visually (graphs/charts)?",
    "Would you prefer learning suggestions based on your weak areas?",
    "Do you want your teacher/parent to get progress reports?",
    "Would you use this app if it worked fully offline?",
    "What features would make you use this app daily?",
    "Do you face difficulty in understanding certain subjects?",
    "Which subject do you struggle with the most?",
    "How often do you feel lost during classes?",
    "What are the main reasons for missing classes?",
    "Do you get enough support from teachers?",
    "Do you have access to extra learning material?",
    "Do you face any language barrier in learning?",
    "How comfortable are you with using technology for learning?",
    "Do you prefer learning via Youtube, notes or interactive activities?",
    "Do you like self-paced learning?",
    "Do you learn better alone or in a group?",
    "Do you need practice quizzes for every chapter?",
    "Do you revise for exams?",
    "What motivates you to complete a course?",
    "How often do you use educational apps?",
    "Have you used adaptive learning platforms before?",
    "Do you face network connectivity issues while studying online?"
]

# Keep only columns present in the sheet
cols = [c for c in candidate_cols if c in df.columns]
data = df[cols].copy()

# 3) Quick cleanup and normalization of text responses
def normalize_text(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str):
        s = x.strip().lower()
        # normalize common variants
        s = s.replace("yes, definitely", "yes")
        s = s.replace("maybe, if it has all features", "maybe")
        s = s.replace("i don’t use learning apps", "never")
        s = s.replace("i don’t use learning apps", "never")
        s = s.replace("30–60 minutes", "30-60 minutes")
        return s
    return x

for c in data.columns:
    data[c] = data[c].apply(normalize_text)

# 4) Mapping functions for common response types
# Binary yes/no
binary_map = {"yes": 1, "no": 0, "maybe": np.nan, "maybe ": np.nan}

# Ordinal time map
time_map = {
    "i don’t use learning apps": 0, "never": 0,
    "less than 30 minutes": 1, "<30 minutes": 1,
    "30-60 minutes": 2, "30–60 minutes": 2,
    "more than 2 hours": 3, ">2 hours": 3
}

# Frequency map
freq_map = {
    "never": 0, "once in a while": 1, "a few times a week": 2,
    "daily": 3, "always": 3, "daily": 3, "a few times a week": 2
}

# Comfort map
comfort_map = {
    "not comfortable": 0, "neutral": 1, "somewhat comfortable": 2,
    "very comfortable": 3
}

# Likert for "how often lost" or teacher support
lost_map = {"never": 0, "rarely": 1, "sometimes": 2, "often": 3, "always": 3}

# Strategy: attempt to map each selected column to numeric sensibly
mapped = pd.DataFrame(index=data.index)

for c in data.columns:
    col = data[c].astype(str).str.lower().replace({"nan": np.nan})
    if any(x in c.lower() for x in ["offline", "personalized", "progress", "teacher/parent", "use this app if", "need practice quizzes", "like self-paced", "have used adaptive"]):
        # binary style
        mapped[c] = col.map(lambda v: binary_map.get(v, np.nan) if isinstance(v, str) else np.nan)
    elif "how much time" in c.lower() or "how often do you use educational apps" in c.lower() or "how often" in c.lower():
        mapped[c] = col.map(lambda v: time_map.get(v, freq_map.get(v, np.nan)))
    elif "how comfortable" in c.lower():
        mapped[c] = col.map(lambda v: comfort_map.get(v, np.nan))
    elif "how often do you feel lost" in c.lower():
        mapped[c] = col.map(lambda v: lost_map.get(v, np.nan))
    elif "what features" in c.lower() or "main reasons" in c.lower() or "which subject" in c.lower() or "prefer learning via" in c.lower() or "what motivates" in c.lower():
        # Multi-category text responses: use simple encoding by presence of key tokens
        # Build keyword features for those multi-response columns
        # For now keep as categorical label encoded
        lbl = LabelEncoder()
        tmp = col.fillna("missing")
        try:
            mapped[c] = lbl.fit_transform(tmp)
        except Exception:
            mapped[c] = tmp.replace("missing", np.nan)
    else:
        # fallback: label encode
        lbl = LabelEncoder()
        tmp = col.fillna("missing")
        try:
            mapped[c] = lbl.fit_transform(tmp)
        except Exception:
            mapped[c] = tmp.replace("missing", np.nan)

# 5) Impute missing values (simple median)
imputer = SimpleImputer(strategy="median")
mapped_imputed = pd.DataFrame(imputer.fit_transform(mapped), columns=mapped.columns)

# 6) Check suitability for factor analysis: KMO and Bartlett
kmo_all, kmo_model = calculate_kmo(mapped_imputed)
chi_square_value, p_value = calculate_bartlett_sphericity(mapped_imputed)
print("KMO model value:", kmo_model)
print("Bartlett's test chi-square:", chi_square_value, "p-value:", p_value)

# 7) Determine number of factors visually by eigenvalues (parallel to scree)
fa = FactorAnalyzer(rotation=None)
fa.fit(mapped_imputed)
ev, v = fa.get_eigenvalues()
ev_df = pd.DataFrame({"eigenvalue": ev})
print(ev_df)

# Choose number of factors: take factors with eigenvalue > 1 (common rule)
n_factors = (ev > 1).sum()
if n_factors < 2:
    n_factors = 2
print("Chosen number of factors:", n_factors)

# 8) Run factor analysis with varimax rotation
fa = FactorAnalyzer(n_factors=n_factors, rotation="varimax")
fa.fit(mapped_imputed)

# Factor loadings
loadings = pd.DataFrame(fa.loadings_, index=mapped_imputed.columns, columns=[f"Factor{i+1}" for i in range(n_factors)])
print("\nFactor loadings:\n", loadings.round(3))

# Variance explained
variance = pd.DataFrame({
    "SS_loadings": fa.get_factor_variance()[0],
    "Proportion_var": fa.get_factor_variance()[1],
    "Cumulative_var": fa.get_factor_variance()[2]
}, index=[f"Factor{i+1}" for i in range(n_factors)])
print("\nFactor variance:\n", variance.round(3))

# 9) Compute factor scores for each respondent
scores = pd.DataFrame(fa.transform(mapped_imputed), columns=[f"Factor{i+1}_score" for i in range(n_factors)])
result = pd.concat([df.reset_index(drop=True), scores], axis=1)

# 10) Export results to Excel
out_fn = "factor_analysis_results.xlsx"
result.to_excel(out_fn, index=False)
print("Saved factor scores and original data to:", out_fn)