from os.path import isfile
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

email = ""
senha = ""

class Sistema:
    wait_elem = None
    tempo_espera = 120
    fname = "database.txt"

    def __init__(self):
        self.lista = self.read_database()
        if self.iniciar_navegador():
            #acessar pagina
            self.nav.get("https://teams.microsoft.com/_?culture=pt-br&country=BR&lm=deeplink&lmsrc=homePageWeb&cmpid=WebSignIn")
            if self.login():
                pass

    def bot(self):
        #abre todos os canais invisiveis
        self.abrir_canal_invisivel();
        
        #procura todas as equipes com apenas Geral
        canais = self.nav.execute_script('''return document.querySelectorAll('[aria-expanded="false"] [class="team"] [class="unread"]')''');
        
        #procura todas as equipes com mais de um subcanal
        canais += self.nav.execute_script('''return document.querySelectorAll('[class="channel-anchor ts-unread-channel"]')''');
        
        for canal in canais:
            #pega o nome da equipe
            equipe = canal.get_attribute("data-tid").split("-")[1];
            #verifica se acessou
            while not equipe in self.nav.title:
                #clica na equipa para acessa-la
                self.nav.execute_script("arguments[0].click();", canal);
                sleep(0.5);
            

    def ler_mensagens(self):
        #primeiro procura todas as datas das mensagens, depois filtra pra datas que só tem a hora (mensagens enviada no dia), depois gera o elemento pai DIV, que engloba toda a mensagem 
        mensagens = self.nav.execute_script('''return Array.from(document.querySelectorAll('[data-tid="messageTimeStamp"]')).filter((e=>{if(5==e.textContent.trim().length)return!0})).map((e=>{for(;e&&e.parentNode;)if("item-wrap ts-message-list-item"==(e=e.parentNode).className)return e}));''');
        for mensagem in mensagens:
            uuid = mensagem.get_attribute('data-scroll-id');
            if uuid not in self.lista:
                self.lista.append(uuid);
                self.SalvarLista();
            else:
                pass
                

    def abrir_canal_invisivel(self):
        i = 0
        #procura todos os botôes "Canal oculto"
        canais = self.nav.find_elements(By.XPATH, '''//a[@class="channel-anchor open-channel-mgr ts-sym expand-collapse-button"]''')
        while i < len(canais):
            canal = canais[i]
            canal.click()
            #verifica se o POPUP aparece
            if self.wait_elem.until(EC.presence_of_element_located((By.XPATH, '''//h4[@class="channel-overflow-teamname ts-section-divider app-font-title2-bold"]'''))):
                ocultos = self.nav.execute_script('''return document.querySelectorAll('button[title="Mostrar este canal na lista de canais"')''')
                if len(ocultos) > 0:
                    #sem javascript o selenium não consegue clicar
                    self.nav.execute_script("arguments[0].click();", ocultos[0]);
                    if len(ocultos) > 1:
                        i = i - 1
            i = i + 1
    
    def login(self):
        try:
            input_email = self.wait_elem.until(EC.element_to_be_clickable((By.XPATH, '//input[@type="email"]')))
            input_email.send_keys(email)
            input_email.send_keys(Keys.RETURN)
            
            input_pass = self.wait_elem.until(EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]')))
            input_pass.send_keys(senha)
            input_pass.send_keys(Keys.RETURN)
            return True
        except Exception as e:
            print(e)
            return False
        
    def iniciar_navegador(self):
        try:
            self.nav = webdriver.Firefox()
            self.wait_elem = WebDriverWait(self.nav, self.tempo_espera)
            return True
        except Exception as e:
            print(e)
            return False

    def read_database(self):
        if isfile(self.fname):
            with open(self.fname, "r") as f:
                conteudo = f.read().split(";")
                conteudo = list(filter(None, conteudo))
                return conteudo
        else:
            open(self.fname, "w+")
            return []

    def SalvarLista(self):
        try:
            with open(self.fname, "w+") as f:
                f.truncate(0)
                for x in self.lista:
                    f.write(x+";")
            return True
        except Exception as e:
            print(e)
            return False

sla = Sistema()
