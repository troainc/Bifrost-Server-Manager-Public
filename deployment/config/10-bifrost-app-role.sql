\getenv app_password BIFROST_APP_PASSWORD
CREATE ROLE bifrost_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD :'app_password';
\unset app_password
