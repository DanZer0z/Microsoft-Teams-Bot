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
        #lê todas as mensagens já respondidas
        self.lista = self.read_database()
    
        #abre o selenium
        if self.iniciar_navegador():
            
            #faz login no teams
            if self.login():
                
                #espera a janela de loading
                self.wait_elem.until(EC.element_to_be_clickable((By.XPATH, '//channel-list')))

                sleep(1)
                #o teams costuma abrir direto em uma equipe, as vezes a equipe tem mensagem
                #por abrir na equipe o bot não consegue detectar
                #por isso to pedindo pra ler as mensagens
                self.ler_mensagens()

                #depois de ler as mensagens vai pra tab arquivos
                self.abrir_tab_arquivos()
                

    def iniciar(self):
        
        while True:
            #abre todos os canais invisiveis
            self.abrir_canal_invisivel();
            
            #procura todas as equipes NÃO LIDAS com apenas o subgrupo GERAL
            canais = self.nav.execute_script('''return document.querySelectorAll('[aria-expanded="false"] [class="team"] [class="unread"]')''');
            
            #procura todas as equipes com subcanal NÃO LIDO
            canais += self.nav.execute_script('''return document.querySelectorAll('[class^="channel-anchor ts-unread-channel"]')''');
            
            for canal in canais:
                #clica na equipe pra acessar ela (usando javascript pra não ocorrer erro)
                self.nav.execute_script("arguments[0].click();", canal);

                #espera a janela carregar
                try:
                    self.wait_elem.until(EC.presence_of_element_located((By.XPATH, '//span[@class="ts-created message-datetime"]')))
                except Exception as e:
                    print(e)

                sleep(1)
                
                #Lê as mensagens da equipe atual
                self.ler_mensagens()

            #se ja não estiver aberto, vai voltar pra lá
            if not "FileBrowserTabApp" in self.nav.current_url:
                self.abrir_tab_arquivos()

    def ler_mensagens(self):
        #primeiro procura todas as datas das mensagens, depois filtra pra datas que só tem a hora (mensagens enviada no dia), depois gera o elemento pai DIV, que engloba toda a mensagem 
        mensagens = self.nav.execute_script('''return Array.from(document.querySelectorAll('[data-tid="messageTimeStamp"]')).filter((e=>{if(8 >= e.textContent.trim().length)return!0})).map((e=>{for(;e&&e.parentNode;)if("item-wrap ts-message-list-item"==(e=e.parentNode).className)return e}));''');
        mensagens = list(filter(None, mensagens))
        mensagens.reverse()
        self.body = self.nav.find_element(By.TAG_NAME, "body")

        for mensagem in mensagens:

            self.body.send_keys(Keys.END)
            
            try:
                #pega o uuid da mensagem (o proprio teams que gera)
                uuid = mensagem.get_attribute('data-scroll-id');
            except:
                self.ler_mensagens();
                break

            #verifica se já foi respondida
            if uuid not in self.lista:
                button = mensagem.find_element(By.XPATH, '//button[@data-tid="replyMessageButtonShort"]')
                if button:
                    button.click()
                    sleep(0.5)
                    self.body.send_keys("ola");
                    sleep(0.5)
                    self.body.send_keys(Keys.ENTER)
            
                    #adiciona na lista de já respondidos
                    self.lista.append(uuid);
                    self.SalvarLista()

                    

    def abrir_tab_arquivos(self):
        #procura a tab arquivos, ja que é uma tab que todas as equipes tem.
        #é necessario mudar para essa tab porque as vezes o canal está recebendo mensagens, e se ficar na tela ele não conta como não lido
        #inutilizando o bot
        botao = self.nav.execute_script('''return document.querySelector('[id="FileBrowserTabApp"]')''')
        if(botao):
            botao.click()
            return True
        else:
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

        
    def iniciar_navegador(self):
        try:
            self.nav = webdriver.Firefox()
            self.wait_elem = WebDriverWait(self.nav, self.tempo_espera)
            return True
        except Exception as e:
            print(e)
            return False
        
    def login(self):
        self.nav.get("https://teams.microsoft.com/_?culture=pt-br&country=BR&lm=deeplink&lmsrc=homePageWeb&cmpid=WebSignIn")
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

    def abrir_canal_invisivel(self):
        i = 0
        #procura todos os botões "Canal oculto"
        canais = self.nav.find_elements(By.XPATH, '''//a[@class="channel-anchor open-channel-mgr ts-sym expand-collapse-button"]''')
        while i < len(canais):
            canal = canais[i]
            canal.click()
            #verifica se o POPUP aparece
            if self.wait_elem.until(EC.presence_of_element_located((By.XPATH, '''//h4[@class="channel-overflow-teamname ts-section-divider app-font-title2-bold"]'''))):
                ocultos = self.nav.execute_script('''return document.querySelectorAll('button[class="ts-sym icons-star"]')''')
                if len(ocultos) > 0:
                    #sem javascript o selenium não consegue clicar
                    self.nav.execute_script("arguments[0].click();", ocultos[0]);
                    if len(ocultos) > 1:
                        i = i - 1
            i = i + 1

sla = Sistema()
sla.iniciar()
