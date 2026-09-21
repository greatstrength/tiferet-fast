"""FastAPI Core Assets

General-purpose service-id and flag constants used by FastAPI session
blueprint handlers when resolving OpenAPI events from DI.
"""

# *** constants

# ** constant: get_route_evt_service_id
GET_ROUTE_EVT_SERVICE_ID = 'get_route_evt'

# ** constant: get_status_code_evt_service_id
GET_STATUS_CODE_EVT_SERVICE_ID = 'get_status_code_evt'

# ** constant: get_routers_evt_service_id
GET_ROUTERS_EVT_SERVICE_ID = 'get_routers_evt'

# ** constant: app_flag
APP_FLAG = 'app'
