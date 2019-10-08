# MESA - MOSLA Error Simulator
##### A flexible DNA Error Detection and Simulation Framework

## Usage:
 
The integrated docker-compose.yml file is all you need to get started!

Before starting things up you should take a look at the compose-file:
If you plan to use MESA you should change all SECRETS to random and secure strings: 
    
      SECRET_KEY:                             <!!!!!!!!!!!!!!!!!!!!!!!!!!>
      SECRET_VALIDATION_SALT:                 <!!!!!!!!!!!!!!!!!!!!!!!!!!>
      SECRET_EMAIL_VALIDATION_KEY:            <!!!!!!!!!!!!!!!!!!!!!!!!!!>
      SECRET_ACCOUNT_DELETION_VALIDATION_KEY: <!!!!!!!!!!!!!!!!!!!!!!!!!!>
Additionally you have to set all mail-settings:

      MAIL_SERVER: <smtp.your-server.com>
      MAIL_PORT: <465>
      MAIL_SENDER_ALIAS: <mosla.dnasim@your-server.com>
      MAIL_PASSWORD: <password>
      MAIL_USERNAME: <mosla.dnasim@your-server.com>
      MAIL_USE_TLS: False
      MAIL_USE_SSL: True

To receive all exceptions and errors via mail you MAY set:  

      EXCEPTION_EMAIL: <error-logging@your-server.com>

To use Lets-Encrypt with Cloudflare-DNA you can set: 

      # CF_Account_ID: XxXxXxXxXxXxXxXxXxXxXxXxXxXxXx
      # CF_Token: XxXxXxXxXxXxXxXxXxXxXxXxXxXxXx

After setting all environment variables you can start MESA by running:

    $ docker-compose up -d ( --build )

if you changed code you can simply run the following command to rebuild all containers and (with -c) reset your database

    $ .\forceRebuildAll.sh (-c)
