from pathlib import Path

# Paths
HOME_DIR = Path.home()
PARSING_MODEL_DIR = HOME_DIR / ".local/share/bllipparser/GENIA+PubMed"

# Observation constants
CARDIOMEGALY = "Cardiomegaly"
ENLARGED_CARDIOMEDIASTINUM = "Enlarged Cardiomediastinum"
SUPPORT_DEVICES = "Support Devices"
OTHER_FINDING = "Other Finding"
OBSERVATION = "observation"
CATEGORIES = ["Other Finding", "Enlarged Cardiomediastinum", "Cardiomegaly",
              "Lung Lesion", "Airspace Opacity", "Edema", "Consolidation",
              "Pneumonia", "Atelectasis", "Pneumothorax", "Pleural Effusion",
              "Pleural Other", "Fracture", "Support Devices",
              "Emphysema", "Cicatrix", "Hernia", "Calcinosis", "Airspace Disease",
              "Hypoinflation"]

# Numeric constants
POSITIVE = 1
NEGATIVE = 0
UNCERTAIN = -1

# Misc. constants
UNCERTAINTY = "uncertainty"
NEGATION = "negation"
REPORTS = "Reports"
