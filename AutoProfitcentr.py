import customtkinter
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from skimage.metrics import structural_similarity as ssim
from skimage.color import rgb2gray
import base64
import time
import re
import io
from PIL import Image
import requests
import datetime
import threading

class Pro():
    def build_browser(self):
        chrome_options = Options()
        if headless_var.get() == "on" and auto == True:
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
    def sosanh_img(self, capt_base64, captcha_file):
        found = False
        image1 = Image.open(io.BytesIO(base64.b64decode(capt_base64)))
        image1 = image1.resize((78,78))
        image1 = rgb2gray(image1)
        f = open(".\\image\\" + captcha_file)
        lines = f.readlines()
        for img in lines:
            image2 = Image.open(io.BytesIO(base64.b64decode(img[:-1])))
            image2 = image2.resize((78,78))
            image2 = rgb2gray(image2)
            ssim_score = ssim(image1, image2, data_range=1.0)
            if ssim_score > 0.5:
                found = True
                break
            else: 
                found = False
        return found
        
    def giaiCaptcha(self, captcha_file):
        cap_element = self.driver.find_elements(By.CLASS_NAME, "out-capcha-lab")
        for i in range(6):
            cap_base64 = cap_element[i].get_attribute("style")[45:-3]
            if (self.sosanh_img(cap_base64, captcha_file) == True):
                cap_element[i].click()
    def getCaptcha(self):
        captcha = self.driver.find_element(By.CLASS_NAME, "out-capcha-title")
        captcha_titles = captcha.text.split()
        if len(captcha_titles) == 4:
            captcha_file = captcha_titles[-1] + ".txt"
        elif len(captcha_titles) == 5:
            captcha_file = captcha_titles[-2] + " " + captcha_titles[-1] + ".txt"
        return captcha_file
    def currentTime(self):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S, %m/%d/%Y")
        return formatted_time

    def login(self, user, pwd):
        self.driver.get("https://profitcentr.com/login")
        username = self.driver.find_element(By.NAME, "username")
        password = self.driver.find_element(By.NAME, "password")
        username.send_keys(user)
        password.send_keys(pwd)
        # captcha_reload = driver.find_element(By.CLASS_NAME, "out-reload")
        chuaGiai = True
        while chuaGiai:
            try:
                captcha_file = self.getCaptcha()
                self.giaiCaptcha(captcha_file)
                chuaGiai = False
            except:
                self.driver.execute_script("re_load_capcha();")
                time.sleep(3)
        login_btn = self.driver.find_element(By.CLASS_NAME, "btn_big_green")
        login_btn.click()
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        t = 0
        time.sleep(2)
        while self.driver.current_url == "https://profitcentr.com/login":
            time.sleep(1)
            t += 1
            if t >= 10:
                self.login(user, pwd)
    def getCookie(self):
        cookies = self.driver.get_cookies()
        cookies = [cookie for cookie in cookies if cookie["domain"].endswith("profitcentr.com")]
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
        return cookies_dict
    def getBalance(self):
        headers = {
            'authority': 'profitcentr.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
            'cache-control': 'max-age=0',
            'referer': 'https://profitcentr.com/login',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        cookie = self.getCookie()
        response = requests.get('https://profitcentr.com/members', cookies=cookie, headers=headers)
        html = response.text
        pattern = r'<span id="new-money-ballans">([\d.]+)</span>'
        match = re.search(pattern, html)
        if match:
            balance = match.group(1)
        else:
            balance = "0.0"
        return str(balance)
    def jumpJob(self):
        if self.driver.current_url != "https://profitcentr.com":
            self.driver.get("https://profitcentr.com/")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        mnu_title1 = self.driver.find_element(By.ID, "mnu_title1")
        if self.driver.find_element(By.ID, "mnu_tblock1").get_attribute("style") == "display: none;":
            mnu_title1.click()
        jump = self.driver.find_elements(By.CLASS_NAME, "ajax-site.user_menuline")[1]
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(jump))
        jump.click()
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "menu-earnings")))
        jumps = self.driver.find_elements(By.XPATH, "//*[contains(@id, 'start-jump-')]")
        cookie = self.getCookie()
        currentUrl = self.driver.current_url
        headers = {
            'authority': 'profitcentr.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://profitcentr.com',
            'referer': currentUrl,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        count = 0
        for jump in jumps:
            onclick = jump.find_element(By.TAG_NAME, "a").get_attribute("onclick")
            data = str(onclick).split("'")
            id = data[5]
            t = int(data[7])
            hash = data[9]
            data1 = {
                'id': id,
                'hash': hash,
                'func': 'go-jump',
            }
            data2 = {
                'id': id,
                'hash': hash,
                'func': 'good-jump',
            }
            count += 1
            response1 = requests.post('https://profitcentr.com/ajax/earnings/ajax-jump.php', cookies=cookie, headers=headers, data=data1)
            time.sleep(t)
            response2 = requests.post('https://profitcentr.com/ajax/earnings/ajax-jump.php', cookies=cookie, headers=headers, data=data2)
            match = re.search(r">(\d+\.\d+)<\\/", response2.text)
            try:
                value = match.group(1)
                updateLogs("[JUMP]  "+ self.currentTime() + "   |   +" + value + " RUB")
                updateBalance()
            except:
                updateLogs("[JUMP]  "+ self.currentTime() + "   |   ERROR" )
    def youTube(self):
        if self.driver.current_url != "https://profitcentr.com":
            self.driver.get("https://profitcentr.com/")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        mnu_title1 = self.driver.find_element(By.ID, "mnu_title1")
        if self.driver.find_element(By.ID, "mnu_tblock1").get_attribute("style") == "display: none;":
            mnu_title1.click()
        time.sleep(3)
        yt = self.driver.find_elements(By.CLASS_NAME, "ajax-site.user_menuline")[5]
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(yt))
        yt.click()
        try:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "out-capcha-lab")))
        except:
            pass
        if len(self.driver.find_elements(By.CLASS_NAME, "out-capcha-lab")) > 0:
            chuaGiai = True
            while chuaGiai:
                try:
                    captcha_file = self.getCaptcha()
                    self.giaiCaptcha(captcha_file)
                    time.sleep(2)
                    chuaGiai = False
                except:
                    self.driver.execute_script("re_load_capcha();")
                    time.sleep(5)
            yt_captcha_submit = self.driver.find_element(By.CLASS_NAME, "btn.green")
            yt_captcha_submit.click()
            time.sleep(5)
        if len(self.driver.find_elements(By.CLASS_NAME, "out-capcha-lab")) > 0:
            self.youTube()
        tries = 0
        while True:
            try:
                tries += 1
                time.sleep(3)
                self.driver.find_element(By.ID, "load-pages").click()
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                if tries >= 10:
                    break
            except:
                break
        elements = self.driver.find_elements(By.XPATH, "//*[contains(@id, 'start-ads-')]")
        for i in range(len(elements)):
            break_for_loop = False
            current_window = self.driver.current_window_handle
            if len(self.driver.window_handles) >= 2:
                for window in self.driver.window_handles:
                    if window != current_window:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                self.driver.switch_to.window(current_window)
                self.youTube()
            try:
                elements[i].find_element(By.TAG_NAME, "span").click()
                time.sleep(3)
            except:
                try:
                    elements[i].find_element(By.TAG_NAME, "span").click()
                    time.sleep(3)
                except:
                    pass
            
            noYTButton = True
            tries = 0
            while noYTButton:
                try:
                    tries += 1
                    elements2 = self.driver.find_elements(By.CLASS_NAME, "youtube-button")
                    onclick_value = elements2[-1].find_element(By.TAG_NAME, "span").get_attribute("onclick")
                    noYTButton = False
                except:
                    if tries >= 5:
                        break_for_loop = True
                        break
                    time.sleep(1)
            if break_for_loop == True:
                continue
            onclick_parts = str(onclick_value).split("&")
            id_value = ""
            id_status_value = ""
            id_video_value = ""
            data_hash_value = ""
            for part in onclick_parts:
                if part.startswith("id="):
                    id_value = part.split("=")[1]
                elif part.startswith("id_status="):
                    id_status_value = part.split("=")[1]
                elif part.startswith("id_video="):
                    id_video_value = part.split("=")[1]
                elif part.startswith("hash="):
                    data_hash_value = part.split("=")[1][:-3]
            headers = {
                'authority': 'profitcentr.com',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://strawberry-drum-xdhc.squarespace.com',
                'referer': 'https://strawberry-drum-xdhc.squarespace.com/',
                'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            }

            data = {
                'func': 'ads-status',
                'hash': data_hash_value,
                'ids': id_status_value,
                'id': id_value,
                'video': id_video_value,
            }
            response = requests.post('https://profitcentr.com/ajax/earnings/ajax-youtube-in.php', headers=headers, data=data)
            match = re.search(r'<b>(.*?)</b>', response.text)
            try:
                value = match.group(1)
            except:
                continue
            updateLogs("[YOUTUBE]   "+ self.currentTime() + "   |   +" + value + " RUB")
            updateBalance()


# chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument(f'user-agent={ua}')

def updateLogs(log):
    logs.configure(state='normal')
    logs.insert('end', log + "\n")
    logs.see('end')
    logs.configure(state='disabled')
def showPassword():
    if showPsw_var.get() == "on":
        password.configure(show="")
    else:
        password.configure(show="*")
def toggle_button():
    global is_running, auto
    auto = True
    if is_running:
        is_running = False
        start_button.configure(text="Start", fg_color = "green", hover_color = "#005900")
        pro.driver.quit()
    else:
        save_config()
        user = username.get().split()[0]
        pwd = password.get().split()[0]
        if user == "" or pwd == "":
            updateLogs("Chưa điền user hoặc password!")
        else:
            is_running = True
            start_button.configure(text="Stop", fg_color = "#e50000", hover_color = "#b20000")
            while True:
                pro.build_browser()
                pro.login(user, pwd)
                updateBalance()
                pro.jumpJob()
                for i in range(5):
                    pro.youTube()
                updateLogs(pro.currentTime() + " | Het job, nghi 30p!")
                pro.driver.quit()
                time.sleep(1800)
def toggle_button_manual():
    global is_running, auto
    auto = False
    if is_running:
        is_running = False
        manual_button.configure(text="Manual", fg_color = "#1f6aa5", hover_color = "#154a73")
        try:
            pro.driver.quit()
        except:
            pass
    else:
        is_running = True
        if autoLogin_var.get() == "on":
            manual_button.configure(text="Close", fg_color = "#e50000", hover_color = "#b20000")
            user = username.get().split()[0]
            pwd = password.get().split()[0]
            if user == "" or pwd == "":
                updateLogs("Chưa điền user hoặc password!")
            else:
                pro.build_browser()
                pro.login(user, pwd)
                updateBalance()
        else:
            is_running = True
            manual_button.configure(text="Close", fg_color = "#e50000", hover_color = "#b20000")
            pro.build_browser()
            pro.driver.get("https://profitcentr.com")
            while True:
                if pro.driver.window_handles:
                    time.sleep(60)
def updateBalance():
    newbalance = pro.getBalance()
    balance.configure(text = newbalance)
def save_config():
    user = username.get()  # Retrieve the username value
    pwd = password.get()  # Retrieve the password value
    with open("config.txt", "w") as file:
        file.write(user + "\n")
        file.write(pwd)
def load_config():
    try:
        with open("config.txt", "r") as file:
            lines = file.readlines()
            user = lines[0].strip()
            pwd = lines[1].strip()
            username.insert(0, user)
            password.insert(0, pwd)
    except:
        pass

is_running = False
auto = False
pro = Pro()
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("635x370")
app.iconbitmap(".\\favicon\\favicon.ico")
app.title("Auto Profitcentr by 2Trung")

username_label = customtkinter.CTkLabel(app, text="Username", fg_color="transparent")
username_label.grid(row=0, column=0, padx=(20, 20), pady=(10, 0))
password_label = customtkinter.CTkLabel(app, text="Password", fg_color="transparent")
password_label.grid(row=0, column=1, padx=(20, 20), pady=(10, 0))
balance_label = customtkinter.CTkLabel(app, text="Balance", fg_color="transparent")
balance_label.grid(row=0, column=2, padx=(20, 20), pady=(10, 0))
manual_button = customtkinter.CTkButton(master=app, text="Manual", command=lambda: threading.Thread(target=toggle_button_manual).start())
manual_button.grid(row=0, column=3, padx=(20, 20), pady=(20, 0))

username = customtkinter.CTkEntry(app)
username.grid(row=1, column=0, padx=(20, 20), pady=(0, 20))
password = customtkinter.CTkEntry(app, show="*")
password.grid(row=1, column=1, padx=(20, 20), pady=(0, 20))
balance = customtkinter.CTkLabel(app, text="0", text_color="green", font=("Arial", 20, "bold"))
balance.grid(row=1, column=2, padx=(0, 0), pady=(0, 20))
start_button = customtkinter.CTkButton(master=app, command=lambda: threading.Thread(target=toggle_button).start())
start_button.configure(text="Start", fg_color = "green", hover_color = "#005900")
start_button.grid(row=1, column=3, padx=(20, 20), pady=(0, 0))

headless_var = customtkinter.StringVar(value="off")
headless = customtkinter.CTkCheckBox(app, text="Run headless",
                                     variable=headless_var, onvalue="on", offvalue="off")
headless.grid(row=2, column=0, padx=(0, 0), pady=(0, 0))

showPsw_var = customtkinter.StringVar(value="off")
showPsw = customtkinter.CTkCheckBox(app, text="Show password", command=showPassword,
                                     variable=showPsw_var, onvalue="on", offvalue="off")
showPsw.grid(row=2, column=1, padx=(0, 0), pady=(0, 0))
autoLogin_var = customtkinter.StringVar(value="off")
autoLogin = customtkinter.CTkCheckBox(app, text="Auto login (Manual mode)",
                                     variable=autoLogin_var, onvalue="on", offvalue="off")
autoLogin.grid(row=2, column=2,columnspan=2, padx=(0, 0))

log_label = customtkinter.CTkLabel(app, text="Logs", fg_color="transparent")
log_label.grid(row=3, columnspan=4, padx=(20, 20), pady=(10, 0))
logs = customtkinter.CTkTextbox(app)
logs.configure(state="disabled")
logs.grid(row=4, column=0, columnspan=4, padx=(20, 20), pady=(0, 0), sticky="nsew")

load_config()
app.mainloop()


