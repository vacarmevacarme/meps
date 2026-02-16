import requests
import pandas as pd
from datetime import date
import logging

###CONST
URL='https://europeanparliament.com/api/meps/'
DATA_FILENAME =f"data/{date.today()}_meps_administrative_data.csv"
LOG_FILENAME = "data/log.log"
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
    #Empty list in which each ID will be appended then to DF once
    mep_list=[] 

    #Starting API request for each ID
    for i in range(len(ID_LIST)):
        try: #Exception mgmt
            #1. API request 
            new_url=URL+str(ID_LIST[i])+FIELDS #unique url for each id
            logging.info(f"Starting API request: {new_url}") 
            response = requests.get(new_url)
            response.raise_for_status() #returns explicit http error if any

            #2. Decoding json response
            mep_js=response.json()

            #3. Extracting body. If not found with this key, returns empty list
            mep_data=mep_js.get(DATA_KEY,[]) #list of one dict [{}]
            # Appending data to a list (one dict per ID)
            logging.info(f"Data found in the API response for key={DATA_KEY}")
            mep_list.append(mep_data[0]) #extracting unique dict in this list {}

        #If error, log error and continue to next ID
        except Exception as e:
            logging.error(f"ERROR:{e}\n")
            continue
        
    # 5.Transforming everything to DF ONCE
    df=pd.DataFrame(mep_list)

    return df


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