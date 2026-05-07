import pandas as pd
from langchain_core.documents import Document
import os
import re

class DataConverter:
    def __init__(self, data_file_path: str, metadata_file_path:str, merged_file_path:str):
        self.data_file_path = data_file_path
        self.metadata_file_path = metadata_file_path
        self.merged_file_path = merged_file_path

    def load(self):
        data_df = pd.read_json(self.data_file_path, lines=True)
        metadata_df = pd.read_json(self.metadata_file_path, lines=True)
        print("=== Data ===")
        print(data_df.shape)
        print(data_df.columns)
        data_df.to_csv(os.path.join("data", "Video_Games.csv"), index=False)
        print("\n=== Metadata ===")
        print(metadata_df.shape)
        print(metadata_df.columns)
        metadata_df.to_csv(os.path.join("data", "meta_Video_Games.csv"), index=False)

        merged_df = self.merge_df("asin", data_df, metadata_df[['title' , 'asin']])
        print("\n=== Merged Data ===")
        print(merged_df.shape)
        print(merged_df.columns)
        merged_df.to_csv(os.path.join("data", "merged_Video_Games.csv"), index=False)


    def convert(self, max_docs: int = 5000):
        # self.load()##merge metadata and video game dfs into merged df
        df = pd.read_csv(self.merged_file_path)[['title', 'reviewText']].dropna().head(max_docs)
        docs = [
            Document(
                page_content=re.sub(r'[\x00-\x1f\x7f]', ' ', str(row['reviewText']))[:512],
                metadata={"product_name": str(row['title'])}
            )
            for _, row in df.iterrows()
        ]
        return docs

    def merge_df(self, col:str, df1:pd.DataFrame, df2:pd.DataFrame):
        merged_df = pd.merge(df1, df2, on=col, how='left')
        return merged_df

if __name__ == "__main__":
    converter = DataConverter(
        data_file_path=os.path.join("data", "Video_Games.json"),
        metadata_file_path=os.path.join("data", "meta_Video_Games.json"),
        merged_file_path=os.path.join("data", "merged_Video_Games.csv")
    )
    converter.convert()