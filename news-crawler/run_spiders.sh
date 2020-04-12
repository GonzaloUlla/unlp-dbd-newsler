#!/bin/bash

APP_FOLDER=/usr/src/app
SPIDERS_FOLDER=${APP_FOLDER}/spiders
JSON_FOLDER=${APP_FOLDER}/data
LOGS_FOLDER=${APP_FOLDER}/logs

DT_NOW=$(date +%Y%m%d_%H%M)

function log() {
  level=$1
  message=$2
  dt_now=$(date '+%F %T')
  script_name=$(basename "$0")
  echo "${level} ${dt_now} [${script_name}] - ${message}"
}

function remove_duplicates() {
  current_json=$1
  last_json=$2
  log INFO "Removing duplicates between current_json: '${current_json}' and last_json: '${last_json}'"
  if [[ -f "${last_json}" && $(diff "${current_json}" "${last_json}") -eq 0 ]]; then
    log DEBUG "Removed: '${current_json}'"
    rm "${current_json}"
  fi
}

function run_spider() {
  spider_name=$1
  json_file="${JSON_FOLDER}"/"${spider_name}"_"${DT_NOW}".json
  last_json=$(ls -t "${JSON_FOLDER}" | grep "${spider_name}" | head -n 1)

  log INFO "Running spider: '${spider_name}'"
  scrapy runspider "${SPIDERS_FOLDER}"/"${spider_name}".py -o "${json_file}" 2>&1 |
    tee -a "${LOGS_FOLDER}"/"${spider_name}".log

  remove_duplicates "${json_file}" "${JSON_FOLDER}"/"${last_json}"
}

function run_all_spiders() {
  log INFO "Running all spiders"
  cd ${SPIDERS_FOLDER} || exit 1
  for spider in *_spider.py; do
    spider_name="$(basename "${spider}" .py)"
    run_spider "${spider_name}"
  done
}

run_all_spiders
