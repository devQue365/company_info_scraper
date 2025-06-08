from sqlalchemy import desc, case
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import *

# Get the active providers from database (db) session
def get_providers(db : Session):
    provider_list = []
    def analyze(provider_type, provider_list, db: Session):
    # --- for different providers ---
        for provider in provider_type:
            # get the current time
            now = datetime.now()
            # we define a boolean variable to flag if there is a need to update the used_calls
            reset_need = False
            # condition to check for hourly reset type
            if(provider.reset_type == 'H'):
                reset_need = (now - provider.last_reset) > timedelta(hours = 1)
            elif(provider.reset_type == 'M'):
                reset_need = (now - provider.last_reset) > timedelta(days = 30)
            elif(provider.reset_type == 'D'):
                reset_need = (now - provider.last_reset) > timedelta(days = 1)
            # check if True
            if reset_need:
                provider.used_calls = 0 # reset used_calls to 0
                provider.last_reset = datetime.now() # update the last reset
                # commit the changes
                db.commit()
            # look for active API provider
            if(provider.used_calls < provider.total_calls):
                provider_list.append(provider)
                break
    try:
        custom_order = case(
            (SAL.type == 'E', 1),
            (SAL.type == 'L', 2)
        )
        # retrieve all the records / providers for each and every API usage table
        tweet_providers = db.query(TWT).filter(TWT.used_calls < TWT.total_calls).all()
        map_providers = db.query(MAP).filter(MAP.used_calls < MAP.total_calls).all()
        overview_providers = db.query(OVR).filter(OVR.used_calls < OVR.total_calls).all()
        sal_providers = db.query(SAL).filter(SAL.used_calls < SAL.total_calls).order_by(custom_order, desc(SAL.total_calls)).all()

        # Analyze each provider type
        analyze(tweet_providers, provider_list, db)
        analyze(map_providers, provider_list, db)
        analyze(overview_providers, provider_list, db)
        analyze(sal_providers, provider_list, db)
    except Exception as e:
        print(f"Error while fetching providers: {e}")
        return []
    # return the list of active providers
    return provider_list

# def active_provider_list(db : Session):
#     # list to store active providers
#     output = []
#     # retrieve all the records / providers
#     providers = db.query(ApiUsageTable).all()
#     # now we will be traversing each provider to get first active provider
#     for provider in providers:
#         # get the current time
#         now = datetime.now()
#         # we define a boolean variable to flag if there is a need to update the used_calls
#         reset_need = False
#         # condition to check for hourly reset type
#         if(provider.reset_type == 'H'):
#             reset_need = (now - provider.last_reset) > timedelta(hours = 1)
#         elif(provider.reset_type == 'M'):
#             reset_need = (now - provider.last_reset) > timedelta(days = 30)
#         # check if True
#         if reset_need:
#             provider.used_calls = 0 # reset used_calls to 0
#             provider.last_reset = datetime.now() # update the last reset
#             # commit the changes
#             db.commit()
#         # look for active API provider
#         if(provider.used_calls < provider.total_calls):
#             output.append(provider)
#     return output


