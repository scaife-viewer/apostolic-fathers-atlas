#!/bin/bash

isort -rc apostolic_fathers_atlas
black apostolic_fathers_atlas
flake8 apostolic_fathers_atlas
