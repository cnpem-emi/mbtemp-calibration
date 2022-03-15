# MBTemp-calibration
Script para calibração da MBTemp (repositório MBTemp: https://gitlab.cnpem.br/patricia.nallin/mbtemp).

## Funcionamento
O script faz N medidas do canal selecionado em três temperaturas diferentes e calcula os coeficientes da equação Temperatura = (Valor do AD)/k - b através do método dos mínimos quadrados. Os coeficientes são então escritos nas respectivas variáveis da MBTemp.

## Instruções de uso
- ligue a MBTemp à SERIALxxCON através da interface RS-485;
- ligue o instrumento calibrador a um dos canais da MBTemp. O canal 1 (x00) é pré-definido como padrão para calibração;
- inicie o script MBTemp-calib.py usando o python 3 (requer a biblioteca numpy);
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


## Validação
Após a calibração, é possível realizar um procedimento de validação que lê temperaturas em todos os canais e verifica a repetibilidade das leituras. Execute o MBTemp-validation.py (recomendado) ou MBTemp-validation-plotly.py (requer mais bibliotecas).

O procedimento é semelhante ao da calibração:
- defina os parâmetros que serão usados ou continue com os pré-definidos;
- ligue o instrumento calibrador ao canal 1 (x00) e faça as leituras para cada temperatura conforme anteriormente;
- aguarde a mensagem "Start readings for channel [n]?";
- ligue o calibrador no canal indicado;
- repita as leituras para canal.

Ao fim do procedimento, será requisitada uma leitura de alta temperatura, a fim de demonstrar o erro da linearização para altas temperaturas.
- ligue o calibrador no canal 1, ajuste a temperatura e faça as medidas (opcional).

Os dados obtidos serão exportados para a pasta results:
- o arquivo dataset.csv contém todas as leituras com a média e o desvio padrão para cada temperatura e canal;
- as leituras e sua distribuição são plotadas nos arquivos out.html (MBTemp-validation), scatter.html e histogram.html (MBTemp-validation-plotly).
