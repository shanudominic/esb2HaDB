#!/usr/bin/env python3

import os
import requests
from random import randint
from time import sleep
from bs4 import BeautifulSoup   # pip install beautifulsoup4
import re as re
import json

from .logger import getLogger

log = getLogger(os.path.basename(__file__))

def download_data(meter_mprn, esb_user_name, esb_password, download_file):
    ###### START OF SCRIPT ###### 
    print("################################################################################")

    log.debug("##### REQUEST 1 -- GET [https://myaccount.esbnetworks.ie/] ######")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
    })    

    try:
        request_1_response = session.get('https://myaccount.esbnetworks.ie/', allow_redirects=True, timeout= (10,5))     # timeout -- 10sec for connect and 5sec for response
    except requests.exceptions.Timeout:
        log.error("[FAILED] The request timed out, server is not responding. Try again later.")
        session.close()
        raise SystemExit(0)
    except requests.exceptions.RequestException as e:
        log.error("An error occurred:", e)
        session.close()
        raise SystemExit(0)

    result = re.findall(r"(?<=var SETTINGS = )\S*;", str(request_1_response.content))
    settings = json.loads(result[0][:-1])
    tester_soup = BeautifulSoup(request_1_response.content, 'html.parser')
    page_title = tester_soup.find("title")
    request_1_response_cookies = session.cookies.get_dict()
    x_csrf_token = settings['csrf']
    transId = settings['transId']

    log.debug("[!] Request #1 Page Title : %s ", page_title.text)
    log.debug("[!] Request #1 Status Code : %s", request_1_response.status_code)
    log.debug("[!] Request #1 Response Headers : %s", request_1_response.headers)
    log.debug("[!] Request #1 Cookies Captured : %s", request_1_response_cookies)
    log.debug("x_csrf_token : %s", x_csrf_token)
    log.debug("transId : %s", transId)

    x_ms_cpim_sso = request_1_response_cookies.get('x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0')
    x_ms_cpim_csrf = request_1_response_cookies.get('x-ms-cpim-csrf')
    x_ms_cpim_trans = request_1_response_cookies.get('x-ms-cpim-trans')

    log.debug("##### creating x_ms_cpim cookies ######")
    log.debug("x_ms_cpim_sso : %s", request_1_response_cookies.get('x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0'))
    log.debug("x_ms_cpim_csrf : %s", request_1_response_cookies.get('x-ms-cpim-csrf'))
    log.debug("x_ms_cpim_trans : %s", request_1_response_cookies.get('x-ms-cpim-trans'))
    log.debug("##### REQUEST 2 -- POST [SelfAsserted] ######")

    sleeping_delay= randint(10,20)
    log.debug('random sleep for %s seconds...', sleeping_delay)
    sleep(sleeping_delay)

    request_2_response = session.post(
        'https://login.esbnetworks.ie/esbntwkscustportalprdb2c01.onmicrosoft.com/B2C_1A_signup_signin/SelfAsserted?tx=' + transId + '&p=B2C_1A_signup_signin', 
        data={
        'signInName': esb_user_name, 
        'password': esb_password, 
        'request_type': 'RESPONSE'
        },
        headers={
        'x-csrf-token': x_csrf_token,
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://login.esbnetworks.ie',
        'Dnt': '1',
        'Sec-Gpc': '1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0',
        'Te': 'trailers',
        },
        cookies={
            'x-ms-cpim-csrf':request_1_response_cookies.get('x-ms-cpim-csrf'),
        #    'x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0':request_1_response_cookies.get('x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0'),
            'x-ms-cpim-trans':request_1_response_cookies.get('x-ms-cpim-trans'),
        },
        allow_redirects=False)

    request_2_response_cookies = session.cookies.get_dict()

    log.debug("[!] Request #2 Status Code : %s", request_2_response.status_code)
    log.debug("[!] Request #2 Response Headers : %s", request_2_response.headers)
    log.debug("[!] Request #2 Cookies Captured : %s", request_2_response_cookies)
    log.debug("[!] Request #2 text : %s ", request_2_response.text)
    log.debug("##### REQUEST 3 -- GET [API CombinedSigninAndSignup] ######")

    request_3_response = session.get(
        'https://login.esbnetworks.ie/esbntwkscustportalprdb2c01.onmicrosoft.com/B2C_1A_signup_signin/api/CombinedSigninAndSignup/confirmed',
        params={
        'rememberMe': False,
        'csrf_token': x_csrf_token,
        'tx': transId,
        'p': 'B2C_1A_signup_signin',
        },
        headers={
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Dnt": "1",
        "Sec-Gpc": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0, i",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Te": "trailers",
        },
        cookies={
            "x-ms-cpim-csrf":request_2_response_cookies.get("x-ms-cpim-csrf"),
        #    "x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0": request_2_response_cookies.get("x-ms-cpim-sso:esbntwkscustportalprdb2c01.onmicrosoft.com_0"),
            'x-ms-cpim-trans':request_2_response_cookies.get("x-ms-cpim-trans"),
        },
    )

    tester_soup = BeautifulSoup(request_3_response.content, 'html.parser')
    page_title = tester_soup.find("title")
    request_3_response_cookies = session.cookies.get_dict()

    log.debug("[!] Page Title : %s", page_title.text)      # will print "Loading..." if failed
    log.debug("[!] Request #3 Status Code : %s", request_3_response.status_code)
    log.debug("[!] Request #3 Response Headers : %s", request_3_response.headers)
    log.debug("[!] Request #3 Cookies Captured : %s", request_3_response_cookies)
    log.debug("[!] Request #3 Content : %s", request_3_response.content)
    log.debug("##### TEST IF SUCCESS ######")

    request_3_response_head_test = request_3_response.text[0:21]
    if (request_3_response_head_test == "<!DOCTYPE html PUBLIC"):
        page_title = tester_soup.find("title")
        log.debug("[PASS] SUCCESS -- ALL OK [PASS]")
        log.debug("[!] Page Title : %s", page_title.text)
    else: 
        session.close()
        try:
            tester_soup_msg = tester_soup.find('h1')
            tester_soup_msg = tester_soup_msg.text
            log.warning("[FAILED] Page response : %s", tester_soup_msg)
        except: tester_soup_msg = ""
        try:
            no_js_msg = tester_soup.find('div', id='no_js')
            no_js_msg = no_js_msg.text
            log.warning("[FAILED] Page response : %s", no_js_msg)
        except: no_js_msg = ""
        try:
            no_cookie_msg = tester_soup.find('div', id='no_cookie')
            no_cookie_msg = no_cookie_msg.text
            log.warning("[FAILED] Page response : %s", no_cookie_msg)
        except: no_cookie_msg = ""
        log.error("[Script Message] Unable to reach login page -- too many retries (max=2 in 24h) or prior sessions was not closed properly. Please try again after midnight.")
        raise SystemExit(0)
        
    log.debug("##### REQUEST - SOUP - state & client_info & code ######")
    soup = BeautifulSoup(request_3_response.content, 'html.parser')
    try:
        form = soup.find('form', {'id': 'auto'})
        login_url_ = form['action']
        state_ = form.find('input', {'name': 'state'})['value']
        client_info_ = form.find('input', {'name': 'client_info'})['value']
        code_ = form.find('input', {'name': 'code'})['value']

        log.debug("login url : %s" ,login_url_)
        log.debug("state_ : %s", state_)
        log.debug("client_info_ : %s", client_info_)
        log.debug("code_ : %s", code_)
    except:
        log.error("[FAILED] Unable to get full set of required cookies from [request_3_response.content] -- too many retries (captcha?) or prior sessions was not closed properly. Please wait 6 hours for server to timeout and try again.")
        session.close()
        raise SystemExit(0)

    log.debug("##### REQUEST 4 -- POST [signin-oidc] ######")
    sleeping_delay= randint(2,5)
    log.debug('random sleep for %s seconds ....',sleeping_delay)
    sleep(sleeping_delay)

    request_4_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://login.esbnetworks.ie",
        "Dnt": "1",
        "Sec-Gpc": "1",
        "Referer": "https://login.esbnetworks.ie/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=0, i",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Te": "trailers",
    }

    request_4_response = session.post(
            login_url_,
            allow_redirects=False,
            data={
            'state': state_,
            'client_info': client_info_,
            'code': code_,
            },
            headers=request_4_headers,
        )

    request_4_response_cookies = session.cookies.get_dict()

    log.debug("[!] Request #4 Status Code : %s", request_4_response.status_code)  # expect 302
    log.debug("[!] Request #4 Response Headers : %s", request_4_response.headers)
    log.debug("[!] Request #4 Cookies Captured : %s", request_4_response_cookies)
    log.debug("[!] Request #4 Content : %s", request_4_response.content)
    log.debug("##### REQUEST 5 -- GET [https://myaccount.esbnetworks.ie] ######")

    request_5_url = "https://myaccount.esbnetworks.ie"
    request_5_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://login.esbnetworks.ie/",
        "Dnt": "1",
        "Sec-Gpc": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=0, i",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Te": "trailers",
    }
    request_5_cookies = {
        "ARRAffinity":request_4_response_cookies.get("ARRAffinity"),
        "ARRAffinitySameSite":request_4_response_cookies.get("ARRAffinitySameSite"),
    }

    request_5_response = session.get(request_5_url,headers=request_5_headers,cookies=request_5_cookies)
    request_5_response_cookies = session.cookies.get_dict()

    log.debug("[!] Request #5 Status Code : %s", request_5_response.status_code)
    log.debug("[!] Request #5 Response Headers : %s", request_5_response.headers)
    log.debug("[!] Request #5 Cookies Captured : %s", request_5_response_cookies)
    log.debug("[!] Request #5 Content : %s", request_5_response.content)
    log.debug("##### Welcome page block #####")
        
    user_welcome_soup = BeautifulSoup(request_5_response.text,'html.parser')
    welcome_page_title_ = user_welcome_soup.find('title')
    log.debug("[!] Page Title : %s", welcome_page_title_.text)                   # it should print "Customer Portal"
    welcome_page_title_ = user_welcome_soup.find('h1', class_='esb-title-h1')
    log.debug("[!] Confirmed User Login : %s", welcome_page_title_.text)    # It should print "Welcome, Name Surname"
    asp_net_core_cookie = request_5_response_cookies.get(".AspNetCore.Cookies")

    log.debug("##### REQUEST 6 -- GET [Api/HistoricConsumption] ######")
    sleeping_delay= randint(3,8)
    log.debug('random sleep for %s seconds ....',sleeping_delay)
    sleep(sleeping_delay)
    request_6_url = "https://myaccount.esbnetworks.ie/Api/HistoricConsumption"
    request_6_cookies = {
        "ARRAffinity":request_4_response_cookies.get("ARRAffinity"),
        "ARRAffinitySameSite":request_4_response_cookies.get("ARRAffinitySameSite"),
        ".AspNetCore.Cookies":asp_net_core_cookie,
    }
    request_6_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Dnt": "1",
        "Sec-Gpc": "1",
        "Referer": "https://myaccount.esbnetworks.ie/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
        "Te": "trailers",
    }

    request_6_response = session.get(request_6_url, headers=request_6_headers,cookies=request_6_cookies)
    request_6_response_cookies = session.cookies.get_dict()

    log.debug("[!] Request #6 Status Code : %s", request_5_response.status_code)
    log.debug("[!] Request #6 Response Headers :%s", request_5_response.headers)
    log.debug("[!] Request #6 Cookies Captured : %s", request_6_response_cookies)
    log.debug("##### My Energy Consumption - Customer Portal #####")

    consumption_soup = BeautifulSoup(request_6_response.text,'html.parser')
    consumption_page_title_ = consumption_soup.find('title')
    welcome_page_title_ = consumption_soup.find('h1', class_='esb-title-h1')

    log.debug("[!] Page Title : %s", consumption_page_title_.text)    # it should print "My Energy Consumption - Customer Portal"
    log.debug("[!] 'esb-title-h1' : %s", welcome_page_title_.text)    # It should print "My Energy Consumption"
    log.debug("##### REQUEST 7 -- GET [file download token] ######")
    
    sleeping_delay= randint(2,5)
    log.debug('random sleep for %s seconds ....',sleeping_delay)
    sleep(sleeping_delay)

    request_7_url = "https://myaccount.esbnetworks.ie/af/t"
    request_7_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Returnurl": "https://myaccount.esbnetworks.ie/Api/HistoricConsumption",
        "Dnt": "1",
        "Sec-Gpc": "1",
        "Referer": "https://myaccount.esbnetworks.ie/Api/HistoricConsumption",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "Te": "trailers",
    }
    request_7_cookies = {
        "ARRAffinity":request_4_response_cookies.get("ARRAffinity"),
        "ARRAffinitySameSite":request_4_response_cookies.get("ARRAffinitySameSite"),
    }
    request_7_response = session.get(request_7_url,headers=request_7_headers,cookies=request_7_cookies)
    request_7_response_cookies = session.cookies.get_dict()
    file_download_token = json.loads(request_7_response.text)["token"]

    log.debug("[!] Request #7 Status Code : %s", request_7_response.status_code)
    log.debug("[!] Request #7 Response Headers : %s", request_7_response.headers)
    log.debug("[!] Request #7 Cookies Captured : %s", request_7_response_cookies)
    log.debug("[!] Request #7 Content : %s", request_7_response.content)
    log.debug("File download token : %s ",file_download_token)
    log.debug("##### REQUEST 8 -- GET [/DataHub/DownloadHdfPeriodic] ######")

    request_8_url = "https://myaccount.esbnetworks.ie/DataHub/DownloadHdfPeriodic"
    request_8_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://myaccount.esbnetworks.ie/Api/HistoricConsumption",
        "Content-Type": "application/json",
        "X-Returnurl": "https://myaccount.esbnetworks.ie/Api/HistoricConsumption",
        "X-Xsrf-Token": file_download_token,
        "Origin": "https://myaccount.esbnetworks.ie",
        "Dnt": "1",
        "Sec-Gpc": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        "Cache-Control": "max-age=0",
        "Te": "trailers",
    }
    payload_data = {
        "mprn": meter_mprn,
        "searchType": "intervalkwh"  ### <<<< !!! THIS IS WHERE YOU SELECT WHICH FILE YOU WANT !!!
    }
    request_8_response = session.post(request_8_url, headers=request_8_headers, json=payload_data)
    
    log.debug("[!] Request #8 Status Code : %s", request_8_response.status_code)
    log.debug("[!] Request #8 Response Headers : %s", request_8_response.headers)
    log.debug("[END] HTTP Requests completed. Closing session.")

    session.close()

    log.debug("#### Getting file attributes ####")
    file_size_ = request_8_response.headers.get("Content-Length")
    file_name_ = request_8_response.headers.get("Content-Disposition")
    file_name_ = file_name_.split(";")
    file_name_ = file_name_[1].split("=")
    file_name_ = file_name_[1]

    log.debug("[!] File size, bytes : %s",file_size_)
    log.debug("[!] Disposition : %s",file_name_)     # it should print [attachment; filename=HDF_kW_mprn_date.csv; filename*=UTF-8''HDF_kW_mprn_date.csv]
    log.debug("[!] File Name : %s",file_name_)
    log.debug("##### Checking/converting received CSV file/object #####")

    if (isinstance(request_8_response.content, bytes)):
        log.debug("[!] Object class is 'bytes', decoding to 'utf-8' and continuing...")
        csv_file = request_8_response.content.decode("utf-8")
    elif(isinstance(request_8_response.content, str)):
        log.debug("[!] Object class is 'string', continuing...")
        csv_file = request_8_response.content
    else:
        log.error("[FAIL] received object is neither 'bytes' nor 'string, stopping here, please check/validate [request_8_response.content]")
        raise SystemExit(0)

    log.info("##### Saving CSV file to disk: %s ######", download_file)
    with open(download_file,"w") as f:
        f.write(csv_file)    # it should save the content of the request_8_response.content object to disk
    log.info("Done.")
    
    print("################################################################################")
