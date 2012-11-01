#!/bin/bash

cat data/yelp_academic_dataset.json | grep "\"type\": \"review\"" > data/reviews.json
