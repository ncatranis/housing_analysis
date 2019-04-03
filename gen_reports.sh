#!/usr/bin/env bash
jupyter nbconvert single_home_analysis.ipynb --to=pdf --TemplateExporter.exclude_input=True
