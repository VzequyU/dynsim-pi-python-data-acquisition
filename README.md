# Aquisição de dados do DYNSIM e do PI Server com Python

O projeto reúne a configuração e os programas de aquisição de variáveis atuais
de uma simulação DYNSIM por OPC DA e de eventos históricos do PI Data Archive
pelo AF SDK. A documentação é disponibilizada em português.

## Documentação

- [Guia integrado em PDF](docs/Guia_Aquisicao_DYNSIM_PI_Python_PT.pdf)
- [Guia integrado em Word](docs/Guia_Aquisicao_DYNSIM_PI_Python_PT.docx)

## Fluxo de dados

| Rota | Integração | Consulta | Saída do programa |
| --- | --- | --- | --- |
| DYNSIM | Motor OPCClient e Matrikon OPC DA | Valores atuais de PV e SP | Console com valor, qualidade e horário OPC |
| PI Data Archive | AF SDK e pythonnet | Eventos de um intervalo definido | CSV independente por tag |

As rotas são independentes. A criação de um alias OPC não cadastra um PI Point
nem habilita seu armazenamento histórico.

## Arquivos do projeto

| Arquivo | Função |
| --- | --- |
| `leer_matrikon_opc_da.py` | Cliente de leitura direta OPC DA |
| `Extrator_Dados_PI.ipynb` | Notebook de extração histórica pelo AF SDK |
| `requirements-opc.txt` | Dependências do ambiente OPC |
| `requirements-pi.txt` | Dependências do ambiente PI |
| `docs/` | Guia técnico em PDF e Word |

## Requisitos

O procedimento pressupõe Windows, um caso DYNSIM operacional e Matrikon
configurado. A rota PI requer PI AF Client com `OSIsoft.AFSDK.dll`, acesso à rede
do Data Archive e permissões de leitura. As instalações proprietárias não são
fornecidas por este repositório.

O caso OPC utiliza Python 3.12 de 32 bits. Para PI, adota-se um ambiente Python
3.12 de 64 bits. Os dois ambientes são preparados separadamente. A configuração
dos aliases, do arquivo OCF e do XRef está descrita no guia integrado.

## Implementação da leitura OPC DA

Na pasta do projeto, executam-se os comandos no PowerShell:

```powershell
py -3.12-32 -m venv .venv_opc
.\.venv_opc\Scripts\python.exe -m pip install -r requirements-opc.txt
.\.venv_opc\Scripts\python.exe leer_matrikon_opc_da.py --once
```

A leitura contínua é iniciada com:

```powershell
.\.venv_opc\Scripts\python.exe leer_matrikon_opc_da.py --interval 1
```

`--once` encerra o programa após uma consulta. A execução contínua é encerrada
com Ctrl+C ou com uma exceção. O intervalo é uma espera entre consultas, acrescida
do tempo de comunicação. O programa fornecido lê os valores atuais; não exporta CSV.

O servidor de referência é `Matrikon.OPC.Simulation.1`, em `localhost`. Os Item ID são:

```text
Process.Plant01.Control.FC101.PV
Process.Plant01.Control.FC101.SP
```

Para outras variáveis, ajusta-se `TAGS` e configura-se sua transferência no
simulador. O código não escreve valores nos tags.

## Implementação da extração PI

Executam-se os comandos na mesma pasta do projeto:

```powershell
py -3.12-64 -m venv .venv_pi
.\.venv_pi\Scripts\python.exe -m pip install -r requirements-pi.txt
.\.venv_pi\Scripts\python.exe -m ipykernel install --user --name pi_afsdk `
    --display-name "PI AF SDK 64 bits"
.\.venv_pi\Scripts\python.exe -m jupyter notebook
```

Abre-se `Extrator_Dados_PI.ipynb` e seleciona-se o kernel **PI AF SDK 64 bits**.
Antes da execução, conferem-se `caminho_sdk`, `meu_servidor`, `data_inicio`,
`data_fim` e `tags_para_buscar`. As três células de código são executadas na ordem
apresentada. No VS Code, seleciona-se o mesmo kernel ou o ambiente `.venv_pi`.

O notebook usa o servidor padrão configurado no cliente PI. Os nomes dos pontos
e o período são adaptados à instalação. A pasta efetiva de saída é obtida com
`Path.cwd()` no kernel.

## Resultados e validação

O CSV PI contém `Tag`, `Timestamp` e `Value`, com ponto e vírgula como separador
e vírgula decimal para números formatados pelo programa. Os estados textuais são
mantidos pelo extrator. Uma nova consulta da mesma tag sobrescreve o CSV de mesmo nome.

A evidência original confirma a leitura OPC pontual de FC101.PV e FC101.SP com
qualidade Good. O notebook original contém extrações de 773 e 94 registros para
FC101.PV e LC101.PV, respectivamente. A cópia preparada para este repositório
preserva o código e remove as saídas armazenadas das células.

Os nomes exatos de dois diálogos do OPC Configurator ainda requerem confirmação,
conforme a seção 5 do guia. A execução OPC contínua e a paginação PI acima de
50000 registros não foram validadas pelas evidências fornecidas. O avanço de 1 ms
entre lotes pode excluir eventos na fronteira; a discussão está na seção 12.

Os horários OPC e PI não representam automaticamente o tempo interno da
simulação. O CSV original PI utiliza horário local com resolução textual em segundos.

## Autoria e materiais de origem

- Integração DYNSIM e documentação do caso FC101: Ezequiel Valencia.
- Notebook e tutorial original de extração PI: José Matheus Mendes Trindade,
  Projeto Refino, Universidade de Brasília.

As referências de software e os parâmetros da configuração são apresentados
no guia integrado. Os códigos de origem permanecem identificados e separados
por rota de aquisição.
