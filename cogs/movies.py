import subprocess
import requests
from selenium import webdriver
import discord
from discord.ext import commands

import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
import os

is_windows = os.name == 'nt'
# Start virtual display
if not is_windows:
    display = Display(visible=0, size=(1920, 1080))
    display.start()

port = 5000
ip = requests.get('https://api.ipify.org').content.decode('utf8')

class Movies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="movie", aliases=["m"])
    async def movie(self, ctx, movie_id:str):
        master=""
        if hasattr(ctx.bot, 'process'):
            if ctx.bot.process is not None:
                ctx.bot.process.kill()
                ctx.bot.process = None

        url = f"http://www.filmeserialeonline.org/{movie_id}"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        chrome_options.add_argument('--disable-dev-shm-usage')  # Disable /dev/shm usage
        chrome_options.set_capability('goog:chromeOptions', {'args': ['disable-infobars']})  # Disable infobars
        chrome_options.set_capability('goog:chromeOptions', {'args': ['disable-extensions']})  # Disable extensions
        chrome_options.set_capability('goog:chromeOptions', {'args': ['disable-notifications']})  # Disable notifications
        driver = webdriver.Chrome(options=chrome_options)
        #set the window size to 600x600
        driver.set_window_size(1024, 1024)
        #click on 300,200
        driver.execute_script("document.elementFromPoint(300, 200).click();")        
        driver.get(url)
        log_entries = driver.get_log("performance")
        def find_recaptcha(driver):
            return driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha/api2/anchor')]")
        
        try:
            import time
            #wait for the page to load
            driver.implicitly_wait(10)
            #if there's an item with the z-index of 2147483647 click it
            driver.execute_script("document.elementFromPoint(300, 200).click();")
            #check if more windows are opened and make sure it's on the first window
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[0])
            #loop 3 times if recapcha is not found
            for i in range(3):
                try:
                    #find the recaptcha
                    frame = find_recaptcha(driver)
                    #if found click it
                    break
                except Exception as e:
                    driver.execute_script("document.elementFromPoint(300, 200).click();") 
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[0])
                    pass


            driver.switch_to.frame(frame)
            checkbox = driver.find_element(By.XPATH, "//div[@class='recaptcha-checkbox-border']")
            checkbox.click()
            time.sleep(5)

        # Switch back to the main frame
            driver.switch_to.default_content()
        except Exception as e:
            pass

        # Initialize variables to store the last known URL
        last_known_url = None

        # Initialize lists to store request URLs containing 'filemoon'
        filemoon_urls = []

        for entry in log_entries:
            try:
                obj_serialized = entry.get("message")
                obj = json.loads(obj_serialized)
                message = obj.get("message")
                method = message.get("method")
                url = message.get("params", {}).get("documentURL")

                # Update last known URL if available
                if url:
                    last_known_url = url

                if method == 'Network.requestWillBeSentExtraInfo' or method == 'Network.requestWillBeSent':
                    try:
                        request_payload = message['params'].get('request', {})
                        request_url = request_payload.get('url', '')
                        if 'filemoon' in request_url:
                            filemoon_urls.append(request_url)
                        if 'master' in request_url:
                            print(f"MASTER URL:{request_url}")
                    except KeyError:
                        pass

            except Exception as e:
                raise e from None

        if len(filemoon_urls) > 0:
            driver.get(filemoon_urls[0])
            log_entries = driver.get_log("performance")

            for entry in log_entries:
                try:
                    obj_serialized = entry.get("message")
                    obj = json.loads(obj_serialized)
                    message = obj.get("message")
                    method = message.get("method")
                    url = message.get("params", {}).get("documentURL")

                    # Update last known URL if available
                    if url:
                        last_known_url = url

                    if method == 'Network.requestWillBeSentExtraInfo' or method == 'Network.requestWillBeSent':
                        try:
                            request_payload = message['params'].get('request', {})
                            request_url = request_payload.get('url', '')
                            if 'master' in request_url:
                                filemoon_urls.append(request_url)
                        except KeyError:
                            pass

                except Exception as e:
                    raise e from None


            # Print URLs containing 'filemoon'
            print("URLs containing 'master':")
            if len(filemoon_urls) > 1:
                print(filemoon_urls[1])
                master=filemoon_urls[1]
            else:
                master=filemoon_urls[0]
                print(filemoon_urls[0])

        # Close the WebDriver
        driver.quit()

        # Stop virtual display
        if not is_windows:
            display.stop()

        

        if master != "":
            await ctx.send(f'http://{ip}:{port}')
            ctx.bot.process = subprocess.Popen(['python', 'video_streaming/stream.py', str(port), master])
        else:
            await ctx.send("Movie not found!")



async def setup(bot):
    await bot.add_cog(Movies(bot))
