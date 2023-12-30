import undetected_chromedriver as uc
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time

import json

class Tracker():
    def __init__(self) -> None:
        self.URLs = URLs()
        self.Account = Account(self)


        self.driver = uc.Chrome()

    def SetURL(self, url:str):
        self.url = url
        return self

    def GetURL(self) -> str:
        return self.url
    
    def OpenURL(self):
        self.driver.get(self.url)
        return self
    

    def GetPosts(self):
        isSuccesControl = False
        while(len(self.posts)<30 and not isSuccesControl):
            try:
                time.sleep(3)
                self.posts = self.driver.find_elements(By.XPATH, "//div[@data-testid='cellInnerDiv']")
                for post in self.posts:
                    if not self.CheckElement(post):
                        isSuccesControl=False
                        raise Exception("")
                isSuccesControl=True
            
            except:
                time.sleep(3)
                continue

    def GetDatas(self,dataPosts,url):
        for post in self.posts:
            try:
                self.Clear(post) #Debugger
            except:
                raise TypeError()
            try:
                post.find_element(By.CSS_SELECTOR,"div> div > article")
            except:
                continue
            try:
                tweetURL = post.find_element(By.CSS_SELECTOR,"div > div > article > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(1) > div > div > div:nth-child(2) > div div:nth-child(3) > a").get_attribute("href")
            except:
                raise TypeError()
            if tweetURL.split("/")[-1] not in dataPosts[url]:
                dataPosts[url][tweetURL.split("/")[-1]] = {}

            dataPost = dataPosts[url][tweetURL.split("/")[-1]]
            isPin = post.find_elements(By.CSS_SELECTOR,"div > div > article > div > div > div:nth-child(1) > div > div > div")
            if isPin and "Sabitlendi" in isPin[0].text: 
                dataPost["isPin"] = True
            else:
                dataPost["isPin"] = False

            try:

                author = post.find_element(By.CSS_SELECTOR,"div > div > article > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(1) > div > div > div:nth-child(2) > div div:nth-child(1) > a > div > span").text
                
                dataPost["author"] = author
                dataPost["tweetURL"] = tweetURL

                tweetDatetime = post.find_element(By.CSS_SELECTOR,"div > div > article > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(1) > div > div > div:nth-child(2) > div div:nth-child(3) > a > time").get_attribute("datetime")
                dataPost["tweetDatetime"] = tweetDatetime

                tweetContent = post.find_element(By.CSS_SELECTOR,"div > div > article > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div ")
                dataPost["tweetContent"] = tweetContent.text
                dataPost["tweetHTML"] = self.Clear(tweetContent).get_attribute("innerHTML")
            except:
                continue
            

    def VisitCryptoPages(self):
        # Kripto sayfalarını tek tek ziyaret eder.
        dataPosts= self.ReadPost()

        for url in URLs.cryptos:
            oldUrl = self.driver.current_url
            while(oldUrl==self.driver.current_url):
                self.SetURL(url).OpenURL()
                time.sleep(1)
                
            while True:
                self.posts = []
                
                try:
                    self.GetPosts()
                except:
                    continue
                    
                for post in self.posts:
                    if not self.CheckElement(post):
                        continue

                shorturl = url.split("/")[-1]
                if shorturl not in dataPosts:
                    dataPosts[shorturl] = {}

                try:
                    self.GetDatas(dataPosts,shorturl)
                except TypeError as e:
                    continue

                self.WritePost(dataPosts)
                
                break

    def ReadPost(self):
        with open("posts.json","r",encoding="utf-8") as f:
            return json.load(f)

    def WritePost(self,posts):
        posts = self.ReverseSortDict(posts)
        with open("posts.json","w",encoding="utf-8") as f:
            json.dump(posts,f,indent=4,ensure_ascii=False)

    def CheckElement(self,element)->bool:
        try:
            children = element.find_elements(By.XPATH,".//*")
            for child in children:
                self.driver.execute_script("""
                    var child = arguments[0]; 
                    """, child)
        
            self.driver.execute_script("""
                    var child = arguments[0]; 
                    """, element)
            
            return True

        except:
            return False



    def Clear(self,element):
        try:
            children = element.find_elements(By.XPATH,".//*")
            
            # Tüm çocuk elementleri kaldır
            for child in children:
                self.driver.execute_script("""
                    var child = arguments[0]; 
                    child.removeAttribute('class', '');
                    child.removeAttribute('style', '');
                    """, child)
            
            self.driver.execute_script("""
                    var child = arguments[0]; 
                    child.removeAttribute('class', '');
                    child.removeAttribute('style', '');
                    """, element)
            

            return element
        except:
            return False
    

    def ReverseSortDict(self, dict:dict ):
        keys = list(dict.keys())
        keys.sort(reverse=True)

        result = {}
        for key in keys:
            result[key] = dict[key]
            
        return result

class Account:
    """
    Hesap email ve şifre bilgileri içerir.
    """
    driver : uc.Chrome
    email="your mail adress"
    password = "your password"
    username = "your username"
    

    def __init__(self,tracker:Tracker) -> None:
        self.tracker = tracker

    def Login(self):
        while(True):
            try:
                #Yüklenmesini bekle
                WebDriverWait(self.tracker.driver,5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"input")))

                # Email girişi
                usernameInputBox = self.tracker.driver.find_elements(By.CSS_SELECTOR, "input")[0]
                usernameInputBox.click()
                usernameInputBox.send_keys(self.email)
                
                break
            except Exception as e:
                pass
        self.tracker.driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div').click()
        isSucces=True
        while(isSucces):
            try:
                WebDriverWait(self.tracker.driver,5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"input")))
                passwordInputBox = self.tracker.driver.find_elements(By.CSS_SELECTOR, "input")[1]
                passwordInputBox.send_keys(self.password)
                isSucces=False
            except:
                pass
            try:
                self.tracker.driver.find_element(By.XPATH,'//*[@id="modal-header"]/span/span')
                self.VerifyAccount()
            except:
                pass
        self.tracker.driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div').click()
        self.VerifyAccount()

    def VerifyAccount(self):
        try:
            if self.tracker.driver.current_url == "https://twitter.com/home":
                return
            WebDriverWait(self.tracker.driver,2).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')))
            usernameInputBox = self.tracker.driver.find_elements(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')[0]
            usernameInputBox.send_keys(self.username)
            self.tracker.driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div').click()
        except Exception as e:
            pass

class URLs:
    """
    URL linkleri bulundurur.
    """
    login="https://twitter.com/i/flow/login"
    home = "https://twitter.com/home"
    binance = "https://twitter.com/binance"
    bitcoin = "https://twitter.com/bitcoin"
    ethererum="https://twitter.com/ethereum"
    ripple = "https://twitter.com/Ripple"
    solana  = "https://twitter.com/solana"
    cardano = "https://twitter.com/Cardano"
    dogecoin = "https://twitter.com/dogecoin"
    avalanche ="https://twitter.com/avax"
    polkadot = "https://twitter.com/Polkadot"
    cryptos=[
        binance,
        bitcoin,
        ethererum,
        ripple,
        solana,
        cardano,
        dogecoin,
        avalanche,
        polkadot
    ]


if __name__ =="__main__":
    tracker = Tracker().SetURL(URLs.login).OpenURL()
    tracker.Account.Login()
    while True:
        tracker.VisitCryptoPages()