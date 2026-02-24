from functools import lru_cache
import os

import toml


@lru_cache
def load_queries():
    base_path = "app/queries"
    all_queries = {}

    for filename in os.listdir(base_path):
        if filename.endswith(".toml"):
            module_name = filename.replace("_queries.toml", "")

            file_path = os.path.join(base_path, filename)
            data = toml.load(file_path)

            # If TOML has [club] inside club_queries.toml → flatten it
            if module_name in data:
                all_queries[module_name] = data[module_name]
            else:
                all_queries[module_name] = data

    return all_queries
