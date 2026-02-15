import requests
import pandas as pd
import duckdb as ddb
from datetime import date
import logging
from  pathlib import Path

###CONST
URL='https://europeanparliament.com/api'
BASE_DIR = BASE_DIR = Path(__file__).resolve().parent #always launch from parent folder
DATA_DIR = BASE_DIR / "data"
DATA_FILENAME=DATA_DIR / f"{date.today()}_meps_administrative_data.csv.csv"
LOG_FILENAME=DATA_DIR / "log.log"
DATA_KEY = 'data'


###LOGGING
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_meps():
    #Exceptions mgmt
    try:
        #1. Starting API request
        logging.info(f"Starting API request: {URL}")  
        response = requests.get(URL, timeout=10)
        logging.info(f"response.status_code: {response.status_code}")

        #2. Decoding json response
        characters_js=response.json() #dict

        #3. Fetching data list. If not found, returns empty list
        characters_list=characters_js.get(DATA_KEY,[])

        #If empty list, log and return empty DF
        if not characters_list:
            logging.warning(f"No data found in the API response for key={DATA_KEY}")
            return pd.DataFrame()
        
        #4. If data found, list to DF
        logging.warning(f"Data found in the API response for key={DATA_KEY}")
        characters_df=pd.DataFrame(characters_list)

        #5. Filtering with duckdb
        df=ddb.query("""
                    SELECT 
                        id,
                        givenName,
                        familyName,
                        citizenship.iso3 as citizenship,
                        bday,
                        deathDate
                    FROM characters_df
                     """).to_df()

        return df
    
    #If error raised, log error and return empty DF
    except Exception as e:
        logging.error(e)
        return pd.DataFrame()


def main():
    df=get_meps()

    #If data found, save as csv file
    if not df.empty:
        df.to_csv(DATA_FILENAME,index=False)
        logging.info(
            f"CSV file '{DATA_FILENAME}' created successfuly with {len(df)} lines"
            )
        
    #If no data found, logging error and no csv file
    else:
        logging.warning("Empty data. No CSV created.")


if __name__=='__main__':
    main()