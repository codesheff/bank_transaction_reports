#!/usr/bin/env python3

"""
This module is to 
  Import data from transaction files
  Classify the transaction
  Produce a report output
  Produce a list of unclassified transaction descriptions
"""

import os
import csv
import pandas as pd


unmatched_descriptions = set()
category_lookup = {}


def get_category(row):
    """
    Get the category for a transaction
    """

    # global unmatched_descriptions

    description = row["description"]

    if description in category_lookup:
        category = category_lookup[description]
    else:
        category = "unknown"
        unmatched_descriptions.add(description)

    return category


def read_data_from_csv(file: str):
    """
    Load data from a transaction file
    """

    df = pd.read_csv(file)
    df.columns = ["date", "description", "amount"]
    df.amount = df.amount.replace(r"[^.0-9\-]", "", regex=True).astype(float)

    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")

    df["category"] = df.apply(get_category, axis=1)

    return df


def load_data():
    """
    Find all the transaction files and load them
    """

    first_row = True
    for file in os.listdir("data"):
        # print(file)
        filepath = os.path.join("data", file)
        df_new = read_data_from_csv(file=filepath)
        if first_row:
            df = df_new
            first_row = False
        else:
            df = pd.concat([df, df_new], ignore_index=True)

    return df


def load_category_lookup():
    """
    load the category lookup info from csv
    """

    # global category_lookup
    try:
        with open("category_lookup.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            for row in reader:
                description = row[0]
                category = row[1]

                category_lookup[description] = category
    except FileNotFoundError:
        print(
            """No category_lookup.csv found. 
            Create the file, and populate with 
            description,category
            A list of descriptions will be given at end of this run 

            """
        )


def main() -> None:
    """
    main logic
    """
    load_category_lookup()

    df = load_data()
    output_file = "out.csv"
    df.to_csv(output_file, sep=",", encoding="utf-8")

    print(
        "These are the transaction descriptions that are not found in the category lookup"
    )
    for line in unmatched_descriptions:
        print(line)

    print(len(unmatched_descriptions))


if __name__ == "__main__":
    main()
