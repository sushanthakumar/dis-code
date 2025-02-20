#!/usr/bin/env bash
# check if reports directory exists, if is there delete it
if [ -d "reports" ]; then
  rm -rf reports
fi

pytest --cov=../pkg/discovery --cov=../pkg/devices \
      --cov-report=html:reports/coverage_report \
      --junitxml=reports/test_report.xml \
      --html=reports/test_report.html