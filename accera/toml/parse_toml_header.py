#!/usr/bin/env python3
####################################################################################################
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# Authors:  Mason Remy
# Requires: Python 3.7+, tomlkit
#
# Utility to parse the TOML metadata from Accera headers
####################################################################################################

import argparse
import os

# Requires tomlkit: pip install tomlkit
import tomlkit


class AcceraModuleData:
    def __init__(self, toml_table):
        self.module_toml = toml_table
        self.name = toml_table["module_name"]
        self.metadata = toml_table["metadata"]
        self.code_table = toml_table["code"]
        variant_metadata_keys = ["_function", "_initialize_function", "_deinitialize_function", "domain"]
        self.is_accera_variant = all(
            key in self.metadata for key in variant_metadata_keys
        )
        if self.is_accera_variant:
            self.function_name = self.metadata["_function"]
            self.initialize_function_name = self.metadata["_initialize_function"]
            self.deinitialize_function_name = self.metadata["_deinitialize_function"]
            self.domain = self.metadata["domain"]
            self.custom_metadata = {
                key: self.metadata[key]
                for key in self.metadata if key not in variant_metadata_keys
            }


class AcceraLibraryData:
    def __init__(self, toml_document):
        self.library_toml = toml_document
        self.name = toml_document["library_name"]
        self.module_names = toml_document["module_names"]
        self.modules_table = toml_document["modules"]
        self.modules = []
        self.modules.extend(
            AcceraModuleData(self.modules_table[module_name])
            for module_name in self.modules_table
        )


def parse_toml_header(filepath):
    path = os.path.abspath(filepath)
    toml_doc = None
    with open(path, "r") as f:
        file_contents = f.read()
        toml_doc = tomlkit.parse(file_contents)
    return AcceraLibraryData(toml_doc)


def print_accera_toml_library_data(accera_library_data):
    print(f"Library Name: {accera_library_data.name}")
    print(f"Module Names: {accera_library_data.module_names}")
    for module in accera_library_data.modules:
        print(f"\tModule: {module.name}")
        print(f"\t\tIs Accera Sample Variant: {module.is_accera_variant}")
        if module.is_accera_variant:
            print(f"\t\tVariant Function: {module.function_name}")
            print(f"\t\tInit Function: {module.initialize_function_name}")
            print(f"\t\tDe-Init Function: {module.deinitialize_function_name}")
            print(f"\t\tDomain: {module.domain}")
            print("\t\tCustom Metadata Parameters:")
            for key in module.custom_metadata:
                print(f"\t\t\t{key} : {module.custom_metadata[key]}")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, type=str, help="Path to file to parse as TOML")
    args = parser.parse_args()

    accera_lib_data = parse_toml_header(args.input)
    print_accera_toml_library_data(accera_lib_data)


if __name__ == "__main__":
    main()
