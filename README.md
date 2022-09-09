# Microsoft Teams - Bot


Esse foi um script que eu fiz na epoca da pandemia do COVID-19. Quando as aulas foram EAD, para ganhar a presença, nós eramos instruidos a responder as mensagens que os professores mandavam.

Esse é um script tem uma funcionalidade bem simples, mas cumpriu os requisitos.

## Processos

1. analisa se tem algum canal oculto e deixa ele visivel se houver (por algum motivo, quando os professores criavam um subcanal, ele aparecia como oculto)
2. analisa se tem alguma equipe ou canal que tem mensagem não lida
3. se houver alguma mensagem NÃO LIDA, ele vai acessar o canal correspondente
4. Vai verificar as mensagens da equipe, ver se ja foi respondida, e caso não for, vai responder a mensagem.


## Usage

### Configurando a autenticação
Você deve abrir o arquivo e mudar o seu email e senha

```python
email = "email@email.com"
senha = "senha"
```

### Baixando o WebDriver
Tambem é necessario baixar o WebDriver que você preferir e colocar na mesma pasta do script

[WebDriver do Firefox](https://github.com/mozilla/geckodriver/releases)  
[WebDriver do Google](https://chromedriver.chromium.org/downloads)  

## Contributing

Pull requests são sempre bem vindos.  

Esse é um codigo que eu fiz quando eu estava no inicio do aprendizado na programação. Tambem não tive mais a oportunidade de testar, então se houver um erro eu agradeceria para que vocês abrissem um "issue"

