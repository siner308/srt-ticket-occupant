# -*- coding: utf-8 -*-

import datetime
import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from shared.logger import get_my_logger
from shared.environments import Env
from shared.chromedriver import setup_chrome

XPATH_PHONE_LOGIN_RADIO_BUTTON = '/html/body/div[1]/div[4]/div/div[2]/form/fieldset/div[1]/div[1]/div[1]/input[3]'
XPATH_ID = '//*[@id="srchDvNm03"]'
XPATH_PW = '//*[@id="hmpgPwdCphd03"]'
XPATH_LOGIN_SUBMIT_BUTTON = '//*[@id="login-form"]/fieldset/div[1]/div[1]/div[4]/div/div[2]/input'

XPATH_FROM_OPTION = '//*[@id="dptRsStnCd"]/option'
XPATH_TO_OPTION = '//*[@id="arvRsStnCd"]/option'
XPATH_TIME_OPTION = '//*[@id="dptTm"]/option'
XPATH_OPTION_CALENDAR = '//*[@id="search-form"]/fieldset/div[3]/div/input[1]'
XPATH_SUBMIT_OPTION_BUTTON = '//*[@id="search-form"]/fieldset/a'


XPATH_START_TIMES = '//*[@id="result-form"]/fieldset/div[6]/table/tbody/tr/td[4]/em'
XPATH_GENERAL_RESV_BUTTONS = '//*[@id="result-form"]/fieldset/div[6]/table/tbody/tr/td[7]/a/span'
XPATH_SPECIAL_RESV_BUTTONS = '//*[@id="result-form"]/fieldset/div[6]/table/tbody/tr/td[6]/a/span'
XPATH_WAIT_RESV_BUTTONS = '//*[@id="result-form"]/fieldset/div[6]/table/tbody/tr/td[8]/a/span'

XPATH_PAYMENT_BUTTON = '//*[@id="list-form"]/fieldset/div[11]/a[1]'

XPATH_RE_SEARCH_BUTTON = '//*[@id="search_top_tag"]/input'

my_logger = get_my_logger('srt')


def reserve(element):
    element.click()
    my_logger.info('click element')


def crawling():
    envs = Env('env.txt')
    # envs = Env('./env')

    id = envs.data['ID']
    password = envs.data['PW']
    resv_date = envs.data['DATE']  # YYYY-MM-DD

    FROM = envs.data['FROM']
    TO = envs.data['TO']

    FIRST_START_TIME = envs.data['FIRST_START_TIME']
    FIRST_END_TIME = envs.data['FIRST_END_TIME']
    resv_first_start_time = time.strptime(FIRST_START_TIME, '%H:%M')
    resv_first_end_time = time.strptime(FIRST_END_TIME, '%H:%M')
    my_logger.info('FIRST  TIME: %s ~ %s' % (FIRST_START_TIME, FIRST_END_TIME))

    login_url = 'https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000'
    booking_url = 'https://etk.srail.kr/main.do'

    driver = setup_chrome()

    # LOGIN
    is_success = False
    is_login_success = False
    while not is_success:
        try:
            driver.get(login_url)
            time.sleep(1)
            element = driver.find_element_by_xpath(XPATH_PHONE_LOGIN_RADIO_BUTTON)
            element.click()

            my_logger.info('input id')
            driver.find_element_by_xpath(XPATH_ID).send_keys(id)
            time.sleep(0.1)

            my_logger.info('input pw')
            element = driver.find_element_by_xpath(XPATH_PW)
            element.send_keys(password)
            time.sleep(0.1)

            my_logger.info('request login')
            element = driver.find_element_by_xpath(XPATH_LOGIN_SUBMIT_BUTTON)
            element.click()
            time.sleep(1)
        except Exception as e:
            my_logger.error(e)

        my_logger.info('move to booking_url')
        driver.get(booking_url)
        time.sleep(1)

        try:
            from_options = driver.find_elements_by_xpath(XPATH_FROM_OPTION)
            for from_option in from_options:
                if from_option.text == FROM:
                    from_option.click()
            to_options = driver.find_elements_by_xpath(XPATH_TO_OPTION)
            for to_option in to_options:
                if to_option.text == TO:
                    to_option.click()

            time_options = driver.find_elements_by_xpath(XPATH_TIME_OPTION)
            for time_option in time_options:
                if int(time_option.text.split('??? ??????')[0]) + 1 >= resv_first_start_time.tm_hour:
                    time_option.click()
                    break

            my_logger.info('click calendar')
            element = driver.find_element_by_xpath(XPATH_OPTION_CALENDAR)
            driver.execute_script("arguments[0].setAttribute('value', %s)" % str(resv_date).replace('-', ''), element)
            time.sleep(2)

            my_logger.info('click submit button')
            button = driver.find_element_by_xpath(XPATH_SUBMIT_OPTION_BUTTON)
            button.click()

            time.sleep(1)
        except Exception as e:
            my_logger.info(e)
            continue

        my_logger.info('trying to first range')

        while True:
            start_times = driver.find_elements_by_xpath(XPATH_START_TIMES)
            special_seats = driver.find_elements_by_xpath(XPATH_SPECIAL_RESV_BUTTONS)
            general_seats = driver.find_elements_by_xpath(XPATH_GENERAL_RESV_BUTTONS)
            wait_resv_buttons = driver.find_elements_by_xpath(XPATH_WAIT_RESV_BUTTONS)

            # ????????? ???????????? ???????????? ????????? ????????? ??????
            for start_time, special_seat, general_seat, wait_resv_button in zip(start_times, special_seats, general_seats, wait_resv_buttons):
                c_time = time.strptime(start_time.text, '%H:%M')
                if resv_first_start_time <= c_time <= resv_first_end_time:
                    if general_seat.text != '??????':
                        my_logger.info('reserve general seat %s' % start_time.text)
                        general_seat.click()
                        time.sleep(0.1)
                        reserve(driver.find_element_by_xpath(XPATH_PAYMENT_BUTTON))
                        is_success = True
                        break
                    if special_seat.text != '??????':
                        my_logger.info('reserve special seat %s' % start_time.text)
                        special_seat.click()
                        time.sleep(0.1)
                        reserve(driver.find_element_by_xpath(XPATH_PAYMENT_BUTTON))
                        is_success = True
                        break
                    if wait_resv_button.text != '??????':
                        my_logger.info('queue wait list %s' % start_time.text)
                        wait_resv_button.click()
                        time.sleep(0.1)
                        is_success = True
                        break

            if is_success:
                my_logger.info('finished')
                return

            my_logger.info('retry...')
            driver.find_element_by_xpath('//*[@id="search_top_tag"]/input').send_keys(Keys.ENTER)
            time.sleep(1)


if __name__ == '__main__':
    crawling()
    my_logger.info('%s completed' % datetime.datetime.now())
    while True:
        time.sleep(1)
