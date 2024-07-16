# Grupo 5
   ## Vitória Rodrigues Pinto Borelli Figueiredo
   ## Pedro Augusto Benevides Salviano
   ## Diego Armando Enriquez Martinez
   ## André Silveira Sousa

# Ferramente Simplificada de Vídeo Conferência

Esta versão simplificada do Google Meet permite que vários usuários participem de chamadas baseadas em vídeo, áudio e texto. O sistema é composto por dois componentes principais: o broker e o cliente. O broker lida com a distribuição de mensagens entre os clientes, enquanto o cliente lida com a captura e exibição de vídeo e áudio, bem como o envio e recebimento de mensagens de texto.

## Pré-requisitos

Antes de executar a aplicação, certifique-se de possuir **Python 3.x** e instalar os devidos pacotes através do arquivo "requirements.txt". Para isso, execute o comando:

`pip install -r requirements.txt`

## Uso

1. **Iniciar o Broker:**
   Execute o script `broker.py` no servidor ou na máquina que atuará como o hub central de comunicação.

2. **Iniciar o Cliente:**
   Execute o script `client.py` em cada máquina que deseja participar da chamada. Siga as instruções para configurar o cliente:
   - Usar a câmera do dispositivo para vídeo? (`y`/`N`) 
        Em caso negativo, este exemplo usa um gerador de quadros de vídeo simplista, demonstrando a funcionalidade na ausência de webcam.
   - Informe o endereço IPv4 do servidor do broker (o padrão é `localhost`). Para obter tal informação, basta utilizar o comando `ipconfig` na máquina que atua como broker.
   - Digite o ID da sala para entrar, limitando sua comunicação com aqueles que estão na mesma sala.
   - Ativar a reprodução do microfone? (`y`/`N`) 
        Caso onde seu próprio áudio é reproduzido pelos auto-falantes.
   - Digite seu nome, pelo qual será identificado nas interações durante a chamada.

3. **Interação na Chamada:**
   - Digite mensagens para enviar texto a todos os participantes.
   - Digite `quit` para sair da chamada.

## Notas

- O broker deve estar em execução antes que qualquer cliente possa se conectar.
- Certifique-se de que as configurações do firewall permitam tráfego nas portas especificadas (5552-5557).

