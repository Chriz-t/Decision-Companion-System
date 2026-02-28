import pandas as pd
import re
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer

class DataPreprocessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None

    # -----------------------------
    # Load Dataset
    # -----------------------------
    def load_data(self):
        self.df = pd.read_csv(self.filepath)
        return self.df

    # -----------------------------
    # Extract numeric from string
    # -----------------------------
    @staticmethod
    def extract_number(value):
        if pd.isna(value):
            return 0
        match = re.search(r"[\d.]+", str(value))
        return float(match.group()) if match else 0
    # -----------------------------
    # Convert Weights to numeric
    # -----------------------------
    @staticmethod
    def encode_weight_type(value):
        mapping = {
            "casual": 2,
            "thinnlight": 1,
            "gaming": 3
        }

        value = str(value).lower().replace(" ", "")
        return mapping.get(value, 2)   # default = Casual
    # -----------------------------
    # Convert SSD/HDD to GB
    # -----------------------------
    @staticmethod
    def convert_storage_to_gb(value):
        if pd.isna(value):
            return 0

        value = str(value).lower()

        number = re.search(r"[\d.]+", value)
        if not number:
            return 0

        number = float(number.group())

        if "tb" in value:
            return number * 1024
        else:
            return number

    # -----------------------------
    # CPU Score Engineering
    # -----------------------------
    @staticmethod
    def compute_cpu_score(row):
        brand = str(row['processor_brand']).lower()
        name = str(row['processor_name']).lower()
        gen = str(row['processor_gnrtn']).lower()

        score = 0

        # -------- BRAND WEIGHT --------
        brand_weight = {
            "intel": 1.0,
            "amd": 1.0,
            "apple": 1.2,
            "snapdragon": 0.8
        }

        score += brand_weight.get(brand, 0.9)

        # -------- TIER WEIGHT --------
        tier_score = 0

        # Intel
        if brand == "intel":
            if "i3" in name:
                tier_score = 3
            elif "i5" in name:
                tier_score = 5
            elif "i7" in name:
                tier_score = 7
            elif "i9" in name:
                tier_score = 9
            elif "pentium" in name or "celeron" in name:
                tier_score = 2
            else:
                tier_score = 4  # default mid

        # AMD
        elif brand == "amd":
            if "ryzen 3" in name:
                tier_score = 3
            elif "ryzen 5" in name:
                tier_score = 5
            elif "ryzen 7" in name:
                tier_score = 7
            elif "ryzen 9" in name:
                tier_score = 9
            elif "athlon" in name:
                tier_score = 2
            elif "apu dual" in name:
                tier_score =2
            else:
                tier_score = 4

        # Apple
        elif brand == "apple":
            if "m1" in name:
                tier_score = 6
            elif "m2" in name:
                tier_score = 8
            elif "m3" in name:
                tier_score = 9
            else:
                tier_score = 6

        else:
            tier_score = 4

        score += tier_score

        # -------- GENERATION SCORE --------
        gen_score = 0

        numbers = re.findall(r'\d+', gen)

        if numbers:
            gen_num = int(numbers[0])

        # Intel style: 10th, 11th, 12th
        if brand == "intel" and gen_num < 50:
            gen_score = gen_num * 0.5

        # AMD Ryzen 3000, 5000 etc
        elif brand == "amd" and gen_num >= 1000:
            gen_score = (gen_num // 1000) * 1.5

        # Apple M1, M2 handled in tier already
        else:
            gen_score = gen_num * 0.3

        score+=gen_score
        return score

    # -----------------------------
    # Clean and Prepare Data
    # -----------------------------
    def preprocess(self):

        if self.df is None:
            self.load_data()

        df = self.df.copy()

        # -------------------------
        # Select only useful columns
        # -------------------------
        df = df[
            [
                "brand",
                "model",
                "processor_brand",
                "processor_name",
                "processor_gnrtn",
                "ram_gb",
                "ssd",
                "hdd",
                "graphic_card_gb",
                "weight",
                "display_size",
                "warranty",
                "star_rating",
                "latest_price",
            ]
        ]

        # -------------------------
        # Clean RAM
        # -------------------------
        df["ram_gb"] = df["ram_gb"].apply(self.extract_number)

        # -------------------------
        # Clean SSD
        # -------------------------
        df["ssd_gb"] = df["ssd"].apply(self.convert_storage_to_gb)
        df["hdd_gb"] = df["hdd"].apply(self.convert_storage_to_gb)
        df["total_storage"] = df["ssd_gb"] + df["hdd_gb"]

        # -------------------------
        # Clean Weight
        # -------------------------
        df["weight_type"] = df["weight"].apply(self.encode_weight_type)

        # -------------------------
        # Clean Display Size
        # -------------------------
        df["display_size"] = df["display_size"].apply(self.extract_number)

        # -------------------------
        # Compute CPU Score
        # -------------------------
        df["cpu_score"] = df.apply(
            lambda row: self.compute_cpu_score(row),
            axis=1,
        )
        # -------------------------
        # Rename for clarity
        # -------------------------
        df = df.rename(
            columns={
                "ram_gb": "ram",
                "graphic_card_gb": "gpu",
                "latest_price": "price",
            }
        )
        columns_to_scale = ["ram","gpu","price", "total_storage","weight_type","cpu_score"]
        scaler = MinMaxScaler()
        # Create scaled versions without touching originals
        for col in columns_to_scale:
            df[col + "_scaled"] = scaler.fit_transform(df[[col]])
        df["price_scaled"]=1-df["price_scaled"]
        return df       