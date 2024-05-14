import json
import subprocess
import requests
from selenium import webdriver
import discord
from discord.ext import commands



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
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        log_entries = driver.get_log("performance")

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

        

        if master != "":
            await ctx.send(f'http://{ip}:{port}')
            ctx.bot.process = subprocess.Popen(['python', 'video_streaming/stream.py', str(port), master])
        else:
            await ctx.send("Movie not found!")



async def setup(bot):
    await bot.add_cog(Movies(bot))
