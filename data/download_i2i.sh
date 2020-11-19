#!/bin/bash
database="datafeed"
data_table="item_i2i_prospective_score"
label="psfa"
dt="2020-11-12"

s3_prefix="smartad-dmp/warehouse/${database}/${data_table}/label=${label}/dt=${dt}"
../bin/fetch_table_data.sh "./i2i_prospective_data/${label}/${dt}" ${s3_prefix}