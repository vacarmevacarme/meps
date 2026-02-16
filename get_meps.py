import requests
import pandas as pd
from datetime import date
import logging

###CONST
URL='https://europeanparliament.com/api/meps/'
DATA_DIR='data/'
DATA_FILENAME =DATA_DIR/f"{date.today()}_meps_administrative_data.csv"
LOG_FILENAME = DATA_DIR/"log.log"
DATA_KEY = 'data' #key to extract json response body
ID_LIST=[124936, 968] #list of IDs to request
FIELDS="?fields=id,givenName,familyName,citizenship.iso3,bday,deathDate"

###LOGGING
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_meps():

    concat_df=pd.DataFrame() #Empty DF in which each ID will be appended

    #1. Starting API request for each ID
    try: #Exception mgmt
        for i in len(ID_LIST):
            #New url to request
            new_url=URL+str(ID_LIST[i])+FIELDS
            #API request 
            logging.info(f"Starting API request: {new_url}") 
            response = requests.get(new_url)
            response.raise_for_status() #returns explicit http error

            #Decoding json response
            meps_js=response.json()

            #Extracting body. If not found with this key, returns empty list
            meps_list=meps_js.get(DATA_KEY,[])
            #If body not found, log and request next ID in the ID_LIST
            if not meps_list:
                logging.warning(f"No data found in the \
                                API response for key={DATA_KEY}")
                continue
            
            #3. Concatenate data in one DF
            logging.info(f"Data found in the API response for key={DATA_KEY}")
            meps_body=pd.DataFrame(meps_list) #list to DF
            concat_df=pd.concat([concat_df,meps_body])

        return concat_df
    
    #If error raised, log error, ID for which it occured and return DF as it is
    except Exception as e:
        logging.error(f"ERROR:{e}\nAT ID {ID_LIST[i]}")
        return concat_df


def main():

    df=get_meps()

    #6. If data found, save as csv file
    if not df.empty:
        df.to_csv(DATA_FILENAME,index=False)
        logging.info(
            f"CSV file '{DATA_FILENAME}' created successfuly \
                                        with {len(df)} lines"
            )
        
    #If no data found, logging error and no csv file
    else:
        logging.warning("Empty data. No CSV created.")


if __name__=='__main__':
    main()