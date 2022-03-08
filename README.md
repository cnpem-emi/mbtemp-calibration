# MBTemp-remote
Script para calibração da MBTemp

## Funcionamento
O script faz N medidas do canal selecionado em três temperaturas diferentes e calcula os coeficientes da equação Temperatura = (Valor do AD)/k - b através do método dos mínimos quadrados. Os coeficientes são então escritos nas respectivas variáveis da MBTemp.

## Instruções de uso
- ligue a MBTemp à SERIALxxCON através da interface RS-485;
- ligue o hardware calibrador a um dos canais da MBTemp. O canal 1 (x00) é pré-definido como padrão para calibração;
- inicie o script usando o python 3, a biblioteca numpy é necessária;
- o script mostra os parâmetros pré-definidos para calibração, você pode iniciar o procedimento com estes parâmetros ou alterá-los, informando-os no seguinte formato:
  - endereço da MBTemp em hexadecimal;
  - canal usado para calibração em hexadecimal (x00 - x07);
  - temperaturas T1, T2 e T3 com a mesma precisão do calibrador (use . como separador).
  - número N inteiro de leituras para cada temperatura;
- após a escolha dos parâmetros, para cada temperatura:
  - aguarde a mensagem "Start readings for [T] °C?";
  - ajuste o calibrador para a temperatura indicada antes de continuar.
- após as leituras, os coeficientes k e b serão calculados e automaticamente gravados na MBTemp;
- concluída a calibração, podem ser feitas leituras de temperatura em seguida.
