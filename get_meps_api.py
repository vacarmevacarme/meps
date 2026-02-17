import requests
import pandas as pd
from datetime import date
import logging

###CONST
URL='https://data.europarl.europa.eu/api/v2/meps/'
DATA_FILENAME =f"data/{date.today()}_meps_administrative_data.csv"
LOG_FILENAME = "data/log.log"
DATA_KEY = 'data' #key to extract json response body
ID_LIST=[124936, 968] #list of IDs to request
HEADERS={"Accept": "application/ld+json",
         "user-id":"Project1-prd-1.0.0"
         }


FIELDS="?fields=id"

###LOGGING
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )

#Returns a DataFrame of administriative info for each ID in ID_LIST
def get_meps(id_list):
    #Empty list in which each request will be appended + transformed into DF
    mep_list=[]

    #1. Starting API request for each ID
    for i in range(len(id_list)):
        try: #Exception mgmt
            #1. API request 
            new_url=URL+str(ID_LIST[i])+FIELDS #unique url for each id
            logging.info(f"Starting API request: {new_url}") 
            response = requests.get(new_url,headers=HEADERS)
            response.raise_for_status() #returns explicit http error if any

            #2. Decoding json response
            mep_js=response.json()

            #3. Extracting body
            mep_data=mep_js[DATA_KEY][0] #list of one dict [{}] then one dict
            #4. Selects only this data
            selection = {
                'id': mep_data.get('id'),
                'givenName': mep_data.get('givenName'),
                'familyName': mep_data.get('familyName'),
                'citizenship': mep_data.get('citizenship')[-3:],
                'bday': mep_data.get('bday'),
                'deathDate': mep_data.get('deathDate')
            }
            # Appending data to a list
            logging.info(f"Data found in the API response")
            mep_list.append(selection) #extracting unique dict in this list {}

        #If error, log error and continue to next ID
        except Exception as e:
            logging.error(f"ERROR:{e}\n")
            continue
        
    # 2.Transforming everything to DF ONCE
    df=pd.DataFrame(mep_list)


# Saves in a CSV file
def main():

    df=get_meps(ID_LIST)

    #3. If data found, save as csv file
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