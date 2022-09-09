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
    tempo_espera = 120 #segundos
    fname = "database.txt"
    resposta = "(coffee)"

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
                #o teams costuma abrir direto em uma equipe e as vezes a equipe tem mensagem não lida
                #por abrir na equipe o bot não consegue detectar
                #por isso to pedindo pra ler as mensagens uma vez
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
                #clica na equipe pra acessar ela (usando javascript pra não ocorrer erro de não conseguir clicar)
                self.nav.execute_script("arguments[0].click();", canal);
                
                #espera a janela de conversas carregar
                try:
                    self.wait_elem.until(EC.presence_of_element_located((By.XPATH, '//span[@class="ts-created message-datetime"]')))
                except Exception as e:
                    print(e)

                #apesar de detectar que a janela carregou, as mensagens demora um pouco pra carregar, então eu espero 1 segundo
                sleep(1)
                
                #Lê as mensagens da equipe atual
                self.ler_mensagens()

            #se ja não estiver aberto, vai voltar pra aba arquivos
            if not "FileBrowserTabApp" in self.nav.current_url:
                self.abrir_tab_arquivos()

            sleep(1)

    def ler_mensagens(self):

        #procura o body do documento, uso pra enviar as teclas
        self.body = self.nav.find_element(By.TAG_NAME, "body")
        
        #primeiro procura todas as datas das mensagens
        #depois filtra pra datas que só tem a hora (mensagens enviada no dia)
        #depois gera o elemento pai DIV, que encaixa todos os elementos da mensagem
        #fiz em javascript porque era mais facil
        mensagens = self.nav.execute_script('''return Array.from(document.querySelectorAll('[data-tid="messageTimeStamp"]')).filter((e=>{if(8 >= e.textContent.trim().length)return!0})).map((e=>{for(;e&&e.parentNode;)if("item-wrap ts-message-list-item"==(e=e.parentNode).className)return e}));''');
        mensagens = list(filter(None, mensagens))
        #ele lê a mensagem de cima pra baixo, eu inverti pra responder a primeira mensagem
        mensagens.reverse()
        
        for mensagem in mensagens:
        
            #pega o uuid da mensagem (o proprio teams que gera)
            uuid = mensagem.get_attribute('data-scroll-id');

            #verifica se já foi respondida
            if uuid not in self.lista:
                #procura o botão de responder dessa mensagem
                button = self.nav.execute_script('''return arguments[0].querySelector('button[data-tid="replyMessageButtonShort"]')''', mensagem)
                if button:
                    #abre o input pra digitar
                    button.click()
                    #espera o input carregar
                    textbox = None
                    while not textbox:
                        textbox = self.nav.execute_script('''return arguments[0].querySelector('[data-tid*="ckeditor-replyConversation"]')''', mensagem)
                        sleep(0.5)

                    #envia a resposta desejada
                    self.body.send_keys(self.resposta);

                    sleep(0.5)

                    #aperta enter pra enviar a mensagem
                    self.body.send_keys(Keys.ENTER)
                    
                    #adiciona na lista de já respondidos
                    self.lista.append(uuid);
                    self.SalvarLista()
        

    def abrir_tab_arquivos(self):
        #procura a tab arquivos, ja que é uma tab que todas as equipes tem.
        #é necessario mudar para essa tab porque as vezes o canal está recebendo mensagens, mas se ficar na tela da equipe, ele conta como lido
        #inutilizando o bot
        botao = self.nav.execute_script('''return document.querySelector('[id="FileBrowserTabApp"]')''')
        if(botao):
            botao.click()
            return True
        else:
            return False
        

    def read_database(self):
        #vê se o arquivo existe
        if isfile(self.fname):
            #se existir lê o arquivo
            with open(self.fname, "r") as f:
                #divide os id's já respondidos
                conteudo = f.read().split(";")
                #filtra pra não ter None
                conteudo = list(filter(None, conteudo))
                return conteudo
        else:
            #se não existir ele vai criar o arquivo
            open(self.fname, "w+")
            #retorna array vazio, ja que não tem nenhuma mensagem respondida
            return []

        
    def iniciar_navegador(self):
        try:
            #abre o selenium
            self.nav = webdriver.Firefox()
            #cria o objeto que faz o selenium esperar o driver
            self.wait_elem = WebDriverWait(self.nav, self.tempo_espera)
            return True
        except Exception as e:
            print(e)
            #se retornar False não vai prosseguir com o script
            return False
        
    def login(self):
        #acessa a pagina de login
        self.nav.get("https://teams.microsoft.com/_?culture=pt-br&country=BR&lm=deeplink&lmsrc=homePageWeb&cmpid=WebSignIn")
        try:
            #procura o input de email
            input_email = self.wait_elem.until(EC.element_to_be_clickable((By.XPATH, '//input[@type="email"]')))
            #insere as informações
            input_email.send_keys(email)
            input_email.send_keys(Keys.RETURN)

            #procura o input de email
            input_pass = self.wait_elem.until(EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]')))
            #insere as informações
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
            #aperta no Mostrar Mais
            canal.click()
            #verifica se o POPUP aparece
            if self.wait_elem.until(EC.presence_of_element_located((By.XPATH, '''//h4[@class="channel-overflow-teamname ts-section-divider app-font-title2-bold"]'''))):
                #Vê a quantidade de canais que estão ocultos
                ocultos = self.nav.execute_script('''return document.querySelectorAll('button[class="ts-sym icons-star"]')''')
                if len(ocultos) > 0:
                    #sem javascript o selenium não consegue clicar
                    self.nav.execute_script("arguments[0].click();", ocultos[0]);
                    if len(ocultos) > 1:
                        #se tiver mais que um canal, vai repetir o processo na mesma equipe
                        #apertar mostrar mais > ver os canais ocultos > mostrar o primeiro > se tiver mais repetir
                        i = i - 1
            i = i + 1

sla = Sistema()
sla.iniciar()
