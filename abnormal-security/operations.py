""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

from requests import request, exceptions as req_exceptions
from connectors.core.connector import get_logger, ConnectorError


logger = get_logger("abnormal-security")


class AbnormalSecurity:
    def __init__(self, config, *args, **kwargs):
        server_url = config.get("server_url")
        if not server_url.startswith('https://') and not server_url.startswith('http://'):
            server_url = "https://"+server_url
        if server_url.endswith("/"):
            server_url = server_url[:-1]
        self.url = server_url
        self.access_token = str(config.get("access_token"))
        self.verify_ssl = config.get("verify_ssl")

    def api_request(self, method, endpoint, params={}, data={}):
        try:
            endpoint = self.url + endpoint
            params = self.build_params(params)
            headers = {"Authorization": f"Bearer {self.access_token}"}
            if params.get("mock-data"):
                headers.update({"mock-data": params.pop("mock-data")})
            logger.debug(f"\n-------------req start-------------\n{method} {endpoint}\nparams: {params}\ndata: {data}\nverify: {self.verify_ssl}\n")
            response = request(method, endpoint, headers=headers, params=params, data=data, verify=self.verify_ssl)
            logger.debug(f"Response status: {response.status_code}\n")
            try:
                from connectors.debug_utils.curl_script import make_curl
                make_curl(method, endpoint, headers=headers, params=params, data=data, verify_ssl=self.verify_ssl)
            except Exception as err:
                logger.error(f"Error in curl utils: {str(err)}")

            if 200 <= response.status_code < 300:
                if response.text != "":
                    return response.json()
                else:
                    return True
            else:
                if response.text != "":
                    err_resp = response.json()
                    error_msg = 'Response [{0}: Details: {1}]'.format(response.status_code, err_resp)
                else:
                    error_msg = 'Response [{0}:{1}]'.format(response.status_code, response.content)
                logger.error(error_msg)
                raise ConnectorError(error_msg)
        except req_exceptions.SSLError:
            logger.error('An SSL error occurred')
            raise ConnectorError('An SSL error occurred')
        except req_exceptions.ConnectionError:
            logger.error('A connection error occurred')
            raise ConnectorError('A connection error occurred')
        except req_exceptions.Timeout:
            logger.error('The request timed out')
            raise ConnectorError('The request timed out')
        except req_exceptions.RequestException:
            logger.error('There was an error while handling the request')
            raise ConnectorError('There was an error while handling the request')
        except Exception as err:
            raise ConnectorError(str(err))

    def build_params(self, params):
        new_params = {}
        for key, value in params.items():
            if value is False or value == 0 or value:
                if key == "mock-data" and isinstance(value, bool):
                    new_params[key] = "True" if value is True else "False"
                else:
                    new_params[key] = value
        return new_params


def check_health_ex(config):
    try:
        params = {"Mock-Data": "True"}
        ob = AbnormalSecurity(config)
        response = ob.api_request("GET", "/threats", params=params)
        return True
    except Exception as err:
        raise ConnectorError(str(err))


def get_threats(config, params):
    ob = AbnormalSecurity(config)
    return ob.api_request("GET", "/threats", params=params)


def get_threat_details(config, params):
    ob = AbnormalSecurity(config)
    threat_id = params.pop("threatId", "")
    return ob.api_request("GET", f"/threats/{threat_id}", params=params)


def get_threat_links(config, params):
    ob = AbnormalSecurity(config)
    threat_id = params.pop("threatId", "")
    return ob.api_request("GET", f"/threats/{threat_id}/links", params=params)


def get_threat_attachments(config, params):
    ob = AbnormalSecurity(config)
    threat_id = params.pop("threatId", "")
    return ob.api_request("GET", f"/threats/{threat_id}/attachments", params=params)


def get_cases(config, params):
    ob = AbnormalSecurity(config)
    return ob.api_request("GET", f"/cases", params=params)


def get_case_details(config, params):
    ob = AbnormalSecurity(config)
    case_id = params.pop("caseId", "")
    return ob.api_request("GET", f"/cases/{case_id}", params=params)


def get_message_details(config, params):
    ob = AbnormalSecurity(config)
    message_id = params.pop("messageId", "")
    return ob.api_request("GET", f"/messages/{message_id}/remediation_history", params=params)


def get_abuse_campaigns(config, params):
    ob = AbnormalSecurity(config)
    return ob.api_request("GET", f"/abusecampaigns", params=params)


def get_abuse_campaign_details(config, params):
    ob = AbnormalSecurity(config)
    campaign_id = params.pop("campaignId", "")
    return ob.api_request("GET", f"/abusecampaigns/{campaign_id}", params=params)


def get_employee_info(config, params):
    ob = AbnormalSecurity(config)
    email_address = params.pop("emailAddress", "")
    return ob.api_request("GET", f"/employee/{email_address}", params=params)


def get_employee_identity_analysis(config, params):
    ob = AbnormalSecurity(config)
    email_address = params.pop("emailAddress", "")
    return ob.api_request("GET", f"/employee/{email_address}/identity", params=params)


def get_employee_login_info(config, params):
    ob = AbnormalSecurity(config)
    email_address = params.pop("emailAddress", "")
    return ob.api_request("GET", f"/employee/{email_address}/logins", params=params)


def get_detection_reports(config, params):
    ob = AbnormalSecurity(config)
    return ob.api_request("GET", f"/detection360/reports", params=params)


def check_case_action_status(config, params):
    ob = AbnormalSecurity(config)
    case_id = params.pop("caseId", "")
    action_id = params.pop("actionId", "")
    return ob.api_request("GET", f"/cases/{case_id}/actions/{action_id}", params=params)


def check_threat_action_status(config, params):
    ob = AbnormalSecurity(config)
    threat_id = params.pop("threatId", "")
    action_id = params.pop("actionId", "")
    return ob.api_request("GET", f"/threats/{threat_id}/actions/{action_id}", params=params)


def download_data_from_threat_log(config, params):
    ob = AbnormalSecurity(config)
    return ob.api_request("GET", f"/threats_export/csv", params=params)


def manage_threat(config, params):
    ob = AbnormalSecurity(config)
    threat_id = params.pop("threatId", "")
    action = params.pop("action", {})
    return ob.api_request("POST", f"/threats/{threat_id}", data=action)


def manage_abnormal_case(config, params):
    ob = AbnormalSecurity(config)
    case_id = params.pop("caseId", "")
    action = params.pop("action", {})
    return ob.api_request("POST", f"/cases/{case_id}", data=action)


def get_case_analysis(config, params):
    ob = AbnormalSecurity(config)
    case_id = params.pop("caseId", "")
    return ob.api_request("GET", f"/cases/{case_id}/analysis", params=params)


def submit_false_positive_report(config, params):
    ob = AbnormalSecurity(config)
    report_data = params.pop("report_data", {})
    return ob.api_request("POST", f"/detection360/reports", data=report_data)


operations = {
    "get_threats": get_threats,
    "get_threat_details": get_threat_details,
    "get_threat_links": get_threat_links,
    "get_threat_attachments": get_threat_attachments,
    "get_cases": get_cases,
    "get_case_details": get_case_details,
    "get_message_details": get_message_details,
    "get_abuse_campaigns": get_abuse_campaigns,
    "get_abuse_campaign_details": get_abuse_campaign_details,
    "get_employee_info": get_employee_info,
    "get_employee_identity_analysis": get_employee_identity_analysis,
    "get_employee_login_info": get_employee_login_info,
    "get_detection_reports": get_detection_reports,
    "check_case_action_status": check_case_action_status,
    "check_threat_action_status": check_threat_action_status,
    "download_data_from_threat_log": download_data_from_threat_log,
    "manage_threat": manage_threat,
    "manage_abnormal_case": manage_abnormal_case,
    "get_case_analysis": get_case_analysis,
    "submit_false_positive_report": submit_false_positive_report
}
