import datetime
import json
import os
import random
import shutil
import ssl
import time
import traceback
from pathlib import Path
from typing import Generator

import cloudscraper
import pyperclip
import pytest
import requests
import ua_generator
from capmonster_python import RecaptchaV2Task, RecaptchaV3Task

from playwright.sync_api import sync_playwright, Playwright, BrowserContext, expect

from logger import logger

csrf = ""
class RequestSession:

    def __init__(self, proxy, address, capmonster):

        self.address, self.capmonster = address, capmonster

        self.session = self._make_scraper

        self.UA = ua_generator.generate(device="desktop").text
        self.session.proxies = proxy
        self.session.headers.update({"user-agent": self.UA,
                                     "content-type": "application/x-www-form-urlencoded",
                                     "X-Csrftoken": f"{csrf}",
                                     "cookie": f"csrftoken={csrf};"})

        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def RequestArbitrumTokens(self):

        self.sitekeyArb = "6LfuM6giAAAAAOSzQAA57VwKBSEOgcRstYXUGqTa"

        payload = {"address":self.address,
                   "network":"arbitrum_goerli",
                   "token_v3":self.token_v3}

        with self.session.post("https://faucet.triangleplatform.com/api/request", json=payload) as response:

            try:
                if response.json()['message'] == 'Please complete the reCAPTCHA and try again.':
                    payload = {"address": self.address,
                               "network": "arbitrum_goerli",
                               "token_v3": self.token_v3,
                               "token_v2": self.token_v2}

                    with self.session.post("https://faucet.triangleplatform.com/api/request", json=payload) as response:
                        return response.json()

            except:
                pass

            return response.json()


    @property
    def token_v3(self)->str:

        capmonster = RecaptchaV3Task(self.capmonster)
        task_id = capmonster.create_task("https://faucet.triangleplatform.com/", self.sitekeyArb)
        result = capmonster.join_task_result(task_id)
        return result.get("gRecaptchaResponse")

    @property
    def token_v2(self)->str:

        capmonster = RecaptchaV2Task(self.capmonster)
        task_id = capmonster.create_task("https://faucet.triangleplatform.com/", self.sitekeyArb)
        result = capmonster.join_task_result(task_id)
        return result.get("gRecaptchaResponse")

    @property
    def _make_scraper(self):

        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers(
            "ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:"
            "ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:"
            "ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:"
            "ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:"
            "ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:"
            "AECDH-AES128-SHA:AECDH-AES256-SHA"
        )
        ssl_context.set_ecdh_curve("prime256v1")
        ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
        ssl_context.check_hostname = False

        return cloudscraper.create_scraper(
            debug=False,
            ssl_context=ssl_context
        )


class PWModel:

    def __init__(self, number, twoCaptcha, private=None, proxy=None):
        self.playwright = sync_playwright().start()

        self.number, self.twoCaptcha = number, twoCaptcha
        self.privateKey,self.proxy = private, proxy

        EX_path = 'MetaMask'
        EX_path_2 = '2Captcha'
        user_data_dir = f"{os.getcwd()}\\dataDir"


        self.context = self.playwright.chromium.launch_persistent_context(user_data_dir,
                                                                          user_agent=random_user_agent(),
                                                                     proxy={
            "server": f"{proxy.split(':')[0]}:{proxy.split(':')[1]}",
            "username": f"{proxy.split(':')[2]}",
            "password": f"{proxy.split(':')[3]}",
        } if proxy != None else None,headless=False, devtools=False, args=[f'--load-extension={os.getcwd()}\\{EX_path},{os.getcwd()}\\{EX_path_2}',
                                               f'--disable-extensions-except={os.getcwd()}\\{EX_path},{os.getcwd()}\\{EX_path_2}'
                                               ])

        self.page = self.context.new_page()

        self.page.set_default_timeout(60000)




    def MMActivation(self):
        # Открытие страницы Twitter
        self.page.goto('https://google.com')
        self.page.wait_for_timeout(5000)

        # print(self.context.pages)

        self.MMPage = self.context.pages[-1]
        self.MMPage.bring_to_front()
        self.MMPage.reload()
        self.MMPage.wait_for_selector('input[id="onboarding__terms-checkbox"]').click()
        self.MMPage.wait_for_selector('button[data-testid="onboarding-create-wallet"]').click()
        self.MMPage.wait_for_selector('button[data-testid="metametrics-i-agree"]').click()
        self.MMPage.wait_for_selector('input[data-testid="create-password-new"]').fill('Passwordsdjeruf039fnreo')
        self.MMPage.wait_for_selector('input[data-testid="create-password-confirm"]').fill('Passwordsdjeruf039fnreo')
        self.MMPage.wait_for_selector('input[data-testid="create-password-terms"]').click()
        self.MMPage.wait_for_selector('button[data-testid="create-password-wallet"]').click()
        self.MMPage.wait_for_selector('button[data-testid="secure-wallet-later"]').click()
        self.MMPage.wait_for_selector('input[data-testid="skip-srp-backup-popover-checkbox"]').click()
        self.MMPage.wait_for_selector('button[data-testid="skip-srp-backup"]').click()
        self.MMPage.wait_for_selector('button[data-testid="onboarding-complete-done"]').click()
        self.MMPage.wait_for_selector('button[data-testid="pin-extension-next"]').click()
        self.MMPage.wait_for_timeout(1000)
        self.MMPage.wait_for_selector('button[data-testid="pin-extension-done"]').click()
        self.MMPage.wait_for_timeout(4000)
        self.MMPage.wait_for_selector('button[data-testid="popover-close"]').click()
        # self.MMPage.wait_for_timeout(1000)
        # self.MMPage.wait_for_selector('button[data-testid="popover-close"]').click()

        if self.privateKey == None:
            self.MMPage.wait_for_selector(
                'xpath=//*[@id="app-content"]/div/div[3]/div/div/div/div[1]/div/div/div/button').click()
            self.MMPage.wait_for_timeout(3000)
            self.address = pyperclip.paste()

            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div/div/div[1]/span/button/span').click()
            self.MMPage.wait_for_selector('xpath=//*[@id="popover-content"]/div[2]/button[2]').click()

            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/span/div[1]/div/div/div/button[3]').click()
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/span/div[1]/div/div/div/div[5]/div/input').fill('Passwordsdjeruf039fnreo')
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/span/div[1]/div/div/div/div[7]/button[2]').click()

            holdButton = self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/span/div[1]/div/div/div/div[3]/button/span')
            holdButton.hover()
            self.MMPage.mouse.down()
            self.MMPage.wait_for_timeout(3000)
            self.MMPage.mouse.up()

            self.privateKey = '0x'+self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/span/div[1]/div/div/div/div[5]/div').text_content()
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/span/div[1]/div/div/div/div[7]/button').click()


        else:

            self.MMPage.wait_for_timeout(1000)
            self.MMPage.wait_for_selector('button[data-testid="account-menu-icon"]').click()
            self.MMPage.wait_for_selector('div.account-menu > button.account-menu__item.account-menu__item--clickable')
            self.MMPage.query_selector_all('div.account-menu > button.account-menu__item.account-menu__item--clickable')[1].click()
            self.MMPage.wait_for_selector('input[id="private-key-box"]').fill(self.privateKey)
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/button[2]').click()
            self.MMPage.wait_for_selector('button[data-testid="eth-overview-send"]')

            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div/div/div[1]/div/div/div/button').click()
            self.address = pyperclip.paste()

        # self.page.wait_for_timeout(1000000)



    def Task(self):

        self.page.bring_to_front()
        self.page.goto('https://pacific-info.manta.network/')

        self.AddAndSwitchNetwork('xpath=//*[@id="__next"]/div/div[2]/main/div/div[1]/div[1]/div[2]/div/div/div[2]/button[1]')

        self.page.wait_for_selector('xpath=//*[@id="__next"]/div/div[2]/main/div/div[1]/div[1]/div[2]/div/div/div[2]/button[2]').click()
        self.page.wait_for_timeout(1000)
        self.page.wait_for_selector('xpath=//*[@id="address"]').fill(self.address)

        self.page.wait_for_selector('div.captcha-solver').click()

        f = 0
        while f < 200:
            try:
                res = self.page.query_selector('div.captcha-solver-info').text_content()
                if res == "ERROR_ZERO_BALANCE":
                    logger.error("Пополните капчу")
                    return "Error"
                elif res == "Капча решена!":
                    logger.success(f"{self.number} | Капча успешно решена")
                    break
                else:

                    continue
            except:
                pass

            f += 1

        if f >= 200:
            logger.error("Слишком долгое ожидание решения")
            return "Error"

        self.page.wait_for_selector('form > button.w-full.faucet-button').click()
        self.page.wait_for_selector('form > button.w-full.faucet-button', state='hidden')

        self.page.wait_for_timeout(2000)

        self.page.wait_for_selector(
            'xpath=//*[@id="__next"]/div/div[2]/main/div/div[1]/div[1]/div[2]/div/div/div[2]/button[3]').click()
        self.page.wait_for_timeout(1000)
        self.page.wait_for_selector('xpath=//*[@id="address"]').fill(self.address)

        self.page.wait_for_selector('div.captcha-solver').click()

        f = 0
        while f < 200:
            try:
                res = self.page.query_selector('div.captcha-solver-info').text_content()
                if res == "ERROR_ZERO_BALANCE":
                    logger.error("Пополните капчу")
                    return "Error"
                elif res == "Капча решена!":
                    logger.success(f"{self.number} | Капча успешно решена")
                    break
                else:

                    continue
            except:
                pass

            f += 1

        if f >= 200:
            logger.error("Слишком долгое ожидание решения")
            return "Error"

        self.page.wait_for_selector('form > button.w-full.faucet-button').click()
        self.page.wait_for_selector('form > button.w-full.faucet-button', state='hidden')

        self.page.wait_for_timeout(2000)

        self.ConnectWallet('xpath=//*[@id="__next"]/div[1]/header/div/div/nav/a')

        self.page.wait_for_selector('xpath=//*[@id="__next"]/div[1]/div/div/div[2]/div[1]/div[1]/div')




        c = 0
        while float(self.page.wait_for_selector('xpath=//*[@id="__next"]/div[1]/div/div/div[2]/div[1]/div[1]/div').get_attribute('title')) == 0 and c < 100:
            self.page.wait_for_timeout(1000)
            c+=1

        if c >= 100:
            raise Exception("Не удалось дождаться прогрузки баланса")

        percentage = float(self.page.wait_for_selector('xpath=//*[@id="__next"]/div[1]/div/div/div[2]/div[1]/div[1]/div').get_attribute('title'))*(random.randint(10,35)/100)
        self.page.wait_for_selector('xpath=//*[@id="__next"]/div[1]/div/div/div[2]/div[1]/div[2]/input').fill(str(percentage))

        self.ConfirmTransaction('xpath=//*[@id="__next"]/div[1]/div/div/div[2]/button')

        self.page.wait_for_selector('xpath=//*[@id="headlessui-dialog-panel-:r1:"]', state='hidden', timeout=200000)
        self.page.wait_for_selector('xpath=//*[@id="headlessui-dialog-panel-:r4:"]/div[2]/button').click()

        self.page.wait_for_timeout(random.randint(5000,25000))

        self.page.wait_for_selector('xpath=//*[@id="__next"]/div[1]/div/div/div[1]/span[2]').click()
        self.page.wait_for_timeout(3000)

        self.SwitchNetwork('xpath=//*[@id="__next"]/div[1]/div/div/div[2]/button')

        c = 0
        while float(self.page.wait_for_selector(
                'xpath=//*[@id="__next"]/div[1]/div/div/div[2]/div[1]/div[1]/div').get_attribute(
                'title')) == 0 and c < 100:
            self.page.wait_for_timeout(1000)
            c += 1

        if c >= 100:
            raise Exception("Не удалось дождаться прогрузки баланса")

        percentage = float(self.page.wait_for_selector(
            'xpath=//*[@id="__next"]/div[1]/div/div/div[2]/div[1]/div[1]/div').get_attribute('title')) * (
                                 random.randint(10, 35) / 100)
        self.page.wait_for_selector('xpath=//*[@id="__next"]/div[1]/div/div/div[2]/div[1]/div[2]/input').fill(
            str(percentage))

        self.ConfirmTransaction('xpath=//*[@id="__next"]/div[1]/div/div/div[2]/button')


        self.page.wait_for_timeout(100000000)

    def TwoCaptchaActivation(self):
        self.CaptchaPage = self.context.new_page()

        self.CaptchaPage.wait_for_timeout(3000)
        self.CaptchaPage.bring_to_front()
        self.CaptchaPage.goto('chrome-extension://ifibfemgeogfhoebkmokieepdoobkbpo/options/options.html')
        self.CaptchaPage.wait_for_selector('[name="apiKey"]').fill(self.twoCaptcha)
        self.CaptchaPage.wait_for_timeout(1000)
        self.CaptchaPage.wait_for_selector('button[data-lang="login"]').click()
        self.CaptchaPage.wait_for_timeout(3000)

        logger.success(f"{self.number} | Плагин 2Captcha успешно активирован")
    def SwitchNetwork(self, element):

        pages = len(self.context.pages)
        self.page.wait_for_selector(element).click()

        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
            _ += 1

        if _ >= 60:
            raise Exception("Превышено время ожидания открытия страницы Метамаск")

        else:

            self.MMConfirmer = self.context.pages[-1]
            self.MMConfirmer.wait_for_selector('button.btn-primary.button').click()
            self.MMConfirmer.wait_for_timeout(3000)

    def ConfirmTransaction(self, element):

        pages = len(self.context.pages)
        self.page.wait_for_selector(element).click()

        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
            _ += 1

        if _ >= 60:
            raise Exception("Превышено время ожидания открытия страницы Метамаск")

        else:

            self.MMConfirmer = self.context.pages[-1]
            self.MMConfirmer.wait_for_selector('button[data-testid="page-container-footer-next"]').click()
            self.MMConfirmer.wait_for_timeout(3000)


    def ConnectWallet(self, element):

        pages = len(self.context.pages)
        self.page.wait_for_selector(element).click()

        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
            _ += 1

        if _ >= 60:
            raise Exception("Превышено время ожидания открытия страницы Метамаск")

        else:

            self.MMConfirmer = self.context.pages[-1]
            self.MMConfirmer.wait_for_selector('button[data-testid="page-container-footer-next"]').click()
            self.MMConfirmer.wait_for_timeout(3000)
            self.MMConfirmer.wait_for_selector('button[data-testid="page-container-footer-next"]').click()
            self.MMConfirmer.wait_for_timeout(3000)
            try:
                self.MMConfirmer.wait_for_selector('button.btn-primary.button', timeout=5000).click()
            except:
                pass


    def AddAndSwitchNetwork(self, element):

        pages = len(self.context.pages)
        self.page.wait_for_selector(element).click()

        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
            _+=1

        if _ >= 60:
            raise Exception("Превышено время ожидания открытия страницы Метамаск")

        else:

            self.MMConfirmer = self.context.pages[-1]
            self.MMConfirmer.wait_for_selector('button.btn-primary.button').click()
            self.MMConfirmer.wait_for_timeout(3000)
            self.MMConfirmer.wait_for_selector('button.btn-primary.button').click()


    def TurnOnChain(self, network):

        if network == 'BSC':

            self.MMPage.wait_for_selector('div.network-display').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-secondary"]').click()
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div[4]/div[2]/button').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary"]').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary home__new-network-added__switch-to-button"]').click()
            self.MMPage.wait_for_timeout(5000)

        if network == 'POLYGON':
            self.MMPage.wait_for_selector('div.network-display').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-secondary"]').click()
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div[10]/div[2]/button').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary"]').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary home__new-network-added__switch-to-button"]').click()
            self.MMPage.wait_for_timeout(5000)

        if network == 'ZK':
            self.MMPage.wait_for_selector('div.network-display').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-secondary"]').click()
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[3]/a/h6').click()

            self.MMPage.wait_for_selector('input.form-field__input')
            inputs = self.MMPage.query_selector_all('input.form-field__input')
            inputs[0].fill('zkSync Era Mainnet')
            inputs[1].fill('https://mainnet.era.zksync.io')
            inputs[2].fill('324')
            inputs[3].fill('ETH')
            inputs[4].fill('https://explorer.zksync.io/')

            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary"]').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary home__new-network-added__switch-to-button"]').click()
            self.MMPage.wait_for_timeout(5000)

    def close(self):

        self.playwright.stop()

if __name__ == '__main__':

    try:
        shutil.rmtree("dataDir")
    except:
        pass

    start_time = time.time()
    try:

        Model = PWModel(number='1',
                        twoCaptcha='')

        Model.TwoCaptchaActivation()
        Model.MMActivation()

        Model.Task()


        Model.close()

        print('Готово')


    except:
        traceback.print_exc()


    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Время выполнения скрипта: {execution_time} секунд")
    Model.page.wait_for_timeout(10000000)

