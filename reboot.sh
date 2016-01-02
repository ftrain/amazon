#!/bin/bash
psql <<EOF ford
drop database amazon; 
create database amazon;
EOF

psql <<EOF amazon
CREATE EXTENSION IF NOT EXISTS ltree WITH SCHEMA public;
EOF
