#!/bin/bash

# install postgresql via brew
brew update
brew doctor
brew install postgresql

# start postgresql
brew services start postgresql

# stop postgresql
# brew services stop postgresql

# run postgresql
psql postgres

# In PostgreSQL interactive session
CREATE DATABASE dbname
CREATE USER username WITH ENCRYPTED PASSWORD 'password'
GRANT ALL PRIVILEGES ON DATABASE dbname TO username

# Exit PostgreSQL interactive session
\q
