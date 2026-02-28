from data_preprocessing import DataPreprocessor


preprocessor=DataPreprocessor("data/laptops.csv")
data=preprocessor.preprocess()
print(data)