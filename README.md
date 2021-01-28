# MESA - MOSLA Error Simulator
##### A flexible DNA Error Detection and Simulation Framework

## Dont want to setup a local instance? 
Try out MESA at [mesa.mosla.de](https://mesa.mosla.de/)

## Tips:
Visit [http://rna.urmc.rochester.edu/RNAstructure.html](http://rna.urmc.rochester.edu/RNAstructure.html) to get the latest version of RNAstructure.tgz !

## Usage:
 
The integrated docker-compose.yml file is all you need to get started!

While you CAN build your own docker image from scratch, a prebuild image is available on DockerHub (mosla/mesadnasim_web) and should be loaded the first time you run `docker-compose up (-d)`
  

Before starting things up you should take a look at the compose-file:
If you plan to use MESA you should change all SECRETS to random and secure strings: 
    
      SECRET_KEY:                             <!!!!!!!!!!!!!!!!!!!!!!!!!!>
      SECRET_VALIDATION_SALT:                 <!!!!!!!!!!!!!!!!!!!!!!!!!!>
      SECRET_PASSWORD_RESET_VALIDATION_KEY:   <!!!!!!!!!!!!!!!!!!!!!!!!!!>
      SECRET_ACCOUNT_DELETION_VALIDATION_KEY: <!!!!!!!!!!!!!!!!!!!!!!!!!!>

Additionally you have to set all mail-settings:
If you do not want to use E-Mail you can set MAIL_ENABLED to 'False', in this case an Administrator has to validate newly registered users - Password reset wont work and changing the E-Mail Address for a user can only be performed by an Administrator
      
      MAIL_ENABLED: 'True'
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
      # CF_HOSTNAME: example.your-server.com

After setting all environment variables you can start MESA by running:

    $ docker-compose up -d ( --build )

if you changed code you can simply run the following command to rebuild all containers and (with -c) reset your database

    $ .\forceRebuildAll.sh (-c)

## Security considerations
Even though the Postgres and Redis-Services are only accessible trough a docker-internal network, changing the default-login  and password (redis and postgres [both user 'postgres' and 'dna_sim' !]) might be required. 

**Please keep this in mind if you plan to deploy this software as a (public) Service!**
