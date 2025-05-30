from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import ApiUsageTable

# Select the active provider from database (db) session
def select_provider(db : Session):
    # retrieve all the records / providers
    providers = db.query(ApiUsageTable).all()
    # now we will be traversing each provider to get first active provider
    for provider in providers:
        # get the current time
        now = datetime.now()
        # we define a boolean variable to flag if there is a need to update the used_calls
        reset_need = False
        # condition to check for hourly reset type
        if(provider.reset_type == 'H'):
            reset_need = (now - provider.last_reset) > timedelta(hours = 1)
        elif(provider.reset_type == 'M'):
            reset_need = (now - provider.last_reset) > timedelta(days = 30)
        # check if True
        if reset_need:
            provider.used_calls = 0 # reset used_calls to 0
            provider.last_reset = datetime.now() # update the last reset
            # commit the changes
            db.commit()
        # look for active API provider
        if(provider.used_calls < provider.total_calls):
            return provider
    return None

def active_provider_list(db : Session):
    # list to store active providers
    output = []
    # retrieve all the records / providers
    providers = db.query(ApiUsageTable).all()
    # now we will be traversing each provider to get first active provider
    for provider in providers:
        # get the current time
        now = datetime.now()
        # we define a boolean variable to flag if there is a need to update the used_calls
        reset_need = False
        # condition to check for hourly reset type
        if(provider.reset_type == 'H'):
            reset_need = (now - provider.last_reset) > timedelta(hours = 1)
        elif(provider.reset_type == 'M'):
            reset_need = (now - provider.last_reset) > timedelta(days = 30)
        # check if True
        if reset_need:
            provider.used_calls = 0 # reset used_calls to 0
            provider.last_reset = datetime.now() # update the last reset
            # commit the changes
            db.commit()
        # look for active API provider
        if(provider.used_calls < provider.total_calls):
            output.append(provider)
    return output

