# quillio

This repository is used for storing documents necessary for project planning and CS307 grading submission, and will hold the code base. 


## Development

To run the application locally, you can run the command:
`heroku local`

For database connections, you will have to set the environment variable locally to the connection string found in the heroku dashboard.
`export MONGODB_URI=some://connectionstring.that.is.awesome850938509238590`

## Third Party Integrations and APIs

In order to implement some features with Quillio, we used the following third party products, services, and APIs: 

* Google Speech to Text API
* SendGrid Mailing Services
* ...





## Information on SendGrid
The following link contains instructions on installation: https://devcenter.heroku.com/articles/sendgrid
Installation steps were taken as follows: 
1. Run the following: 
```bash
	pipenv install sendgrid
	heroku addons:create sendgrid:starter
``` 

2. Check the installation and addon was successful by visiting the remote heroku page for the application, and run the following to get config settings: 
```bash
	heroku config:get SENDGRID_USERNAME
	heroku config:get SENDGRID_PASSWORD
```

3. Add an API Key (more secure than just using the username and password). Run the following: 
```bash
	heroku config:set SENDGRID_API_KEY=<api_key_here>	
```
4. Make sure all heroku integration is successful so far by running: 
```bash
	heroku config
```
All set config variables should be displayed with the correct value. 

### Information on Email Testing Protocol
Since our emailing service is run through a third party server, all tests were completed through Postman. Links sent in emails with private tokens and secure email addresses were run through postman to affirm that the appropriate responses came through with each post request. Other manual tests were ran that stress tested input, such as invalid email addresses, in order to affirm that our code was robust enough to handle production level input. We also used the SendGrid API dashboard to monitor email usage statistics (sent, received, viewed, etc). 


## Missing Config.py File
In order to keep sensitive data private and secure, such as API keys, security salts, and database urls, the config.py file is not included in this repository. Any future contributers to this project (outside of the members of the project that have access to code locally) will have to be given access to the config file contents in order to develop and test with our software. 

## Unit Tests
All unit tests and integration tests for Quillio can be found in the quillio-test repository listed under the [quillio organization](https://github.com/quillio307). Unit tests were written using the Mocha JS Framework. 