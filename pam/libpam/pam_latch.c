/*
 * This proof of concept shows how we can integrate Latch with PAM modules in some UNIX systems (like Linux). It can be very handy for some services
 * that are continuously exposed in the Internet, like ssh
 * Copyright (C) 2013 Eleven Paths

 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 */


// standard stuff
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <syslog.h>

// pam stuff
#include <security/pam_modules.h>
#include <security/pam_appl.h>
#include "../latch.h"


/* expected hook */
PAM_EXTERN int pam_sm_setcred( pam_handle_t *pamh, int flags, int argc, const char **argv ) {
	return PAM_SUCCESS;
}

/*
 * Makes getting arguments easier. Accepted arguments are of the form: name=value
 * 
 * @param pName- name of the argument to get
 * @param argc- number of total arguments
 * @param argv- arguments
 * @return Pointer to value or NULL
 */
static const char* getArg(const char* pName, int argc, const char** argv) {
	int len = strlen(pName);
	int i;

	for (i = 0; i < argc; i++) {
		if (strncmp(pName, argv[i], len) == 0 && argv[i][len] == '=') {
			// only give the part url part (after the equals sign)
			return argv[i] + len + 1;
		}
	}
	return 0;
}

/* this function is ripped from pam_unix/support.c, it lets us do IO via PAM */
int converse( pam_handle_t *pamh, int nargs, struct pam_message **message, struct pam_response **response ) {
	int retval ;
	struct pam_conv *conv ;

	retval = pam_get_item( pamh, PAM_CONV, (const void **) &conv ) ; 
	if( retval==PAM_SUCCESS ) {
		retval = conv->conv( nargs, (const struct pam_message **) message, response, conv->appdata_ptr ) ;
	}

	return retval ;
}

static const char* getAccountId(const char* pUser, const char* pAccounts) {

	char * line = NULL;
	char * token = NULL;
	size_t len = 0;
	ssize_t read;
	const char delimiters[]= " \t\n";
	FILE *fp;

	fp = fopen(pAccounts,"r");
	if (fp == NULL) {
        	perror("Failed to open file \"latch accounts\"");
        	return NULL;
    	}

	while((read = getline(&line,&len, fp)) != -1){
		token = strsep(&line,delimiters);
		if(token[strlen(token)-1] == ':'  &&  strncmp(token,pUser,strlen(token)-1) == 0){
			token = strsep(&line,delimiters);
			if(strlen(token) == 64)
				return token;
			else
				return NULL;
		}
	}

	return NULL;
}


/*
 * Get config parameters of the form: parameter = value (from LATCH_CONFIG file)
 * 
 * @return Pointer to value
 * @return '\0' if value is not found ( parameter =  )
 * @return NULL other case
 */
static const char *getConfig(const char* pParameter, const char* pConfig) {

	char * line = NULL;
	char * token = NULL;
	size_t len = 0;
	ssize_t read;
	const char delimiters[]= " \t\n";

	FILE *fp = fopen(pConfig,"r");
	if (fp == NULL) {
        	perror("Failed to open file \"latch.conf\"");
        	return NULL;
    	}

	while((read = getline(&line,&len, fp)) != -1){
		token = strsep(&line,delimiters);
		if(strcmp(pParameter,token) == 0  &&  strcmp("=", strsep(&line,delimiters)) == 0){
			return strsep(&line,delimiters);
		}
	}

	return NULL;
}


void send_syslog_alert(){  

	openlog ("ovpn-server", LOG_PID, LOG_AUTH);
     
	syslog (LOG_ALERT, "Latch-auth-pam warning: Someone tried to access. Latch locked");
     
	closelog ();
}






/* expected hook, this is where custom stuff happens */
PAM_EXTERN int pam_sm_authenticate(pam_handle_t* pamh, int flags, int argc, const char **argv) {
	//int ret = 0;

	const char* pUsername = NULL;				
	const char* pAccountId = NULL;
	const char* pSecretKey = NULL;
	const char* pAppId = NULL;
	const char* pAccounts = NULL;
	const char* pConfig = NULL;
	char *buffer;				
	
	/*
	struct pam_message msg[1],*pmsg[1];
	struct pam_response *resp;

	// setting up conversation call prompting for one-time code 
	pmsg[0] = &msg[0] ;
	msg[0].msg_style = PAM_PROMPT_ECHO_ON ;
	msg[0].msg = "One-time code: " ;
	resp = NULL ;
	*/

	if (pam_get_user(pamh, &pUsername, NULL) != PAM_SUCCESS) {
		return PAM_AUTH_ERR;
	}

	pAccounts = getArg("accounts", argc, argv);
	if (!pAccounts) {
		return PAM_AUTH_ERR;
	}

	pConfig = getArg("config", argc, argv);
	if (!pConfig) {
		return PAM_AUTH_ERR;
	}

	pAccountId = getAccountId(pUsername, pAccounts);
	if (pAccountId == NULL) {
		return PAM_SUCCESS;
	}


	pAppId = getConfig("app_id", pConfig);
	pSecretKey = getConfig("secret_key", pConfig);
	
	if(pAppId == NULL || pSecretKey == NULL){
		perror("Failed to read \"latch.conf\"");
		return PAM_AUTH_ERR;
	}

	if(strcmp(pAppId,"") == 0 || strcmp(pSecretKey,"") == 0){
		perror("Failed to read \"latch.conf\"");
		return PAM_AUTH_ERR;
	}

	init(pAppId, pSecretKey);
	setHost("https://latch.elevenpaths.com");

	buffer = status(pAccountId);
	
	if(buffer == NULL || strcmp(buffer,"") == 0)
		return PAM_SUCCESS;

	if (strstr(buffer, "\"status\":\"off\"") != NULL){
		fprintf (stderr, "AUTH-PAM: latch locked\n");
                send_syslog_alert();
		return PAM_AUTH_ERR;
	}
	
	/*
	if (strstr(buffer, "\"status\":\"on\"") != NULL) {
		
		char *pch;
		if((pch = strstr(buffer, "\"two_factor\"")) != NULL){
			char code[6] ;
			char *input;

			strncpy (code, pch + strlen("\"two_factor\":{\"token\":\""), 6);

			if( (ret = converse(pamh, 1 , pmsg, &resp)) != PAM_SUCCESS ) {
			// if this function fails, make sure that ChallengeResponseAuthentication in sshd_config is set to yes
				return ret ;
			}

			// retrieving user input 
			if( resp ) {
				if( (flags & PAM_DISALLOW_NULL_AUTHTOK) && resp[0].resp == NULL ) {
	    				free( resp );
	    				return PAM_AUTH_ERR;
				}
				input = resp[ 0 ].resp;
				resp[ 0 ].resp = NULL; 		  				  
    			} else {
				return PAM_CONV_ERR;
			}

			// comparing user input with known code 
			if(strncmp(code,input,6) != 0){
				free( input ) ;
				return PAM_AUTH_ERR;
			}
			free( input ) ;
		}
			
	} 
	*/
	//printf("buffer response from  status  call -> %s\n",buffer);

	return PAM_SUCCESS;
}
