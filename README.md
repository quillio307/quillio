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

5. To be continued lol 
