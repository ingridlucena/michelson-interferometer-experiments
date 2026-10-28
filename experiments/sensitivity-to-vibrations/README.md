# Experimento 01: contagem de franjas com LDR e sensibilidade a vibrações

Contagem automática de franjas em um interferômetro de Michelson usando um módulo LDR e um Arduino, com análise posterior em Python. O objetivo é estudar a sensibilidade do interferômetro a vibrações do ambiente: com o sistema estático, perturbações externas alteram a diferença de caminho entre os braços e aparecem como flutuações na intensidade luminosa captada pelo sensor.

## Procedimento experimental

Foram coletadas duas amostras de 60 s, com os mesmos parâmetros de aquisição e análise:

1. **Amostra 1, vibrações ambientais:** sistema estático, sem perturbação intencional. O sinal registra apenas as influências naturais do laboratório, como vibrações do ambiente, variações de luz e vozes.
2. **Amostra 2, perturbação mecânica:** durante a aquisição, a base do interferômetro foi tocada suavemente, provocando uma mudança maior no padrão de interferência.

## Material e ligações

- Interferômetro de Michelson, calibrado até o padrão de interferência ficar nítido e estável
- Laser de comprimento de onda $\lambda = 532\text{ nm}$ (Laser Verde)
- Placa Arduino (Uno ou Nano) com conversor analógico-digital de 10 bits (valores de 0 a 1023)
- Módulo sensor LDR com saída analógica (AO)
- Máscara com furo pequeno (cerca de 0,5 a 1 mm) na frente do LDR, para que o sensor veja apenas uma fração de uma franja

| Módulo LDR | Arduino |
|---|---|
| VCC | 5V |
| GND | GND |
| AO | A0 |

A saída digital (DO) do módulo não é usada.

## Estrutura da pasta

```text
01-vibracoes-ldr/
├── README.md
├── arduino/contador_franjas/contador_franjas.ino   # código de coleta
├── python/analise_vibracao.py                      # gravação e análise
├── python/requirements.txt                         # dependências
├── figuras/                                        # fluxogramas e tabela
└── data/                                           # arquivos .csv gravados
```

---

## Detalhamento matemático

### 1. Deslocamento e franjas

A passagem de uma franja completa pelo sensor corresponde a um deslocamento de $\lambda/2$ do espelho móvel. Para $N_f$ franjas contadas:

$$x = N_f \cdot \frac{\lambda}{2}$$

### 2. Amostragem e média

O sensor é lido em intervalos fixos $T_s$:

$$f_s = \frac{1}{T_s} = \frac{1}{5\ \text{ms}} = 200\ \text{Hz}$$

Cada amostra $V[n]$ é a média de $N = 4$ leituras do conversor, $a_1, \dots, a_N$:

$$V[n] = \frac{1}{N}\sum_{i=1}^{N} a_i$$

Se o ruído de cada leitura for aproximadamente independente, a média reduz o ruído por um fator $\sqrt{N} = 2$.

### 3. Máximo e mínimo adaptativos

Quando $V[n]$ ultrapassa $V_{\max}$ (ou fica abaixo de $V_{\min}$), esse extremo assume imediatamente o novo valor. Caso contrário, ambos se aproximam do sinal:

$$V_{\max}[n] = V_{\max}[n-1] - \alpha\,\big(V_{\max}[n-1] - V[n]\big)$$

$$V_{\min}[n] = V_{\min}[n-1] + \alpha\,\big(V[n] - V_{\min}[n-1]\big)$$

Isso equivale a um decaimento exponencial com constante de tempo:

$$\tau = \frac{T_s}{\alpha} = \frac{5\ \text{ms}}{0{,}002} = 2{,}5\ \text{s}$$

O sistema "esquece" variações de luminosidade em alguns segundos, sem perder o acompanhamento das franjas.

### 4. Amplitude, ponto médio e histerese

$$A = V_{\max} - V_{\min}, \qquad V_m = \frac{V_{\max} + V_{\min}}{2}$$

As duas linhas de decisão são simétricas em relação a $V_m$:

$$L_{\text{sup}} = V_m + \frac{\beta A}{2}, \qquad L_{\text{inf}} = V_m - \frac{\beta A}{2}$$

A folga total entre as linhas é $L_{\text{sup}} - L_{\text{inf}} = \beta A$, isto é, 25% da amplitude para $\beta = 0{,}25$.

O programa mantém um estado interno ("baixo" ou "alto"):

- no estado "baixo", se $V[n] > L_{\text{sup}}$: conta uma franja ($N_f \leftarrow N_f + 1$) e passa para "alto";
- no estado "alto", se $V[n] < L_{\text{inf}}$: passa para "baixo".

A contagem só é feita se a amplitude for suficiente para haver franjas distinguíveis do ruído:

$$A > A_{\min} = 40$$

**Condição para a contagem ser confiável.** A folga deve ser maior que a flutuação do ruído, medida do ponto mais alto ao mais baixo ($R_{pp}$):

$$\beta A > R_{pp}$$

Se $\beta A \le R_{pp}$, o ruído atravessa a faixa entre as linhas e gera contagens falsas.

### 5. Frequência de amostragem efetiva e amplitude na análise

Na análise, a frequência de amostragem é calculada pela mediana dos intervalos entre amostras consecutivas, $\Delta t_i$, que é pouco sensível a atrasos isolados:

$$f_s = \frac{1}{\text{mediana}(\Delta t_i)}$$

A amplitude do sinal é calculada pelos percentis 99 e 1 da distribuição das leituras, o que reduz a influência de valores extremos isolados:

$$A = P_{99}(V) - P_{1}(V)$$

### 6. Deslocamento a partir do sinal bruto

A intensidade no sensor varia com o deslocamento $x$ do espelho segundo:

$$I = I_0\,(1 + C\cos\varphi), \qquad \varphi = \frac{4\pi x}{\lambda}$$

em que $I_0$ é a intensidade média e $C$ é o contraste das franjas. O fator $4\pi$ (e não $2\pi$) vem de a luz percorrer duas vezes o braço deslocado. A diferença entre o máximo e o mínimo é $I_{\max} - I_{\min} = 2 I_0 C$, que corresponde à amplitude $A$ medida; logo, $I_0 C = A/2$.

Perto do ponto de maior inclinação da franja, $\varphi = \pi/2 + \delta$ com $\delta$ pequeno, e $\cos\varphi = -\sin\delta \approx -\delta$. Então:

$$\Delta I \approx -I_0 C\,\delta = -\frac{A}{2}\cdot\frac{4\pi\,\Delta x}{\lambda}$$

Isolando $\Delta x$ (em módulo):

$$x = \frac{\lambda\,\Delta I}{2\pi A}$$

em que $\Delta I = V - \bar{V}$ é a variação do sinal em relação à média. A sensibilidade, em deslocamento por unidade do conversor, é $\lambda/(2\pi A)$. Por exemplo, para $\lambda = 532\text{ nm}$ e $A = 58$:

$$\frac{532\ \text{nm}}{2\pi \cdot 58} \approx 1{,}46\ \text{nm por unidade}$$

**Validade.** A aproximação $\sin\delta \approx \delta$ tem erro de cerca de 16% para $\delta = 1\text{ rad}$, o que corresponde a $\Delta x = \lambda/(4\pi) \approx 0{,}08\,\lambda$. Por isso o programa emite um aviso quando o sinal varre mais de 40% da amplitude em torno da média. Nesse caso, a aproximação subestima o deslocamento e a contagem de franjas é o método mais adequado. Além disso, a amplitude $A$ vem dos próprios dados: se o sinal não varreu uma franja inteira, $A$ é subestimada e o deslocamento, superestimado.

### 7. Valor RMS

A amplitude típica do movimento é o desvio padrão do deslocamento ao longo das $M$ amostras:

$$x_{\text{RMS}} = \sqrt{\frac{1}{M}\sum_{i=1}^{M}\left(x_i - \bar{x}\right)^2}$$

Para 60 s de medida, $M = f_s \cdot 60\ \text{s} = 12\,000$.

### 8. Espectro de frequências

Após a subtração da média, o deslocamento $x[n]$ é multiplicado por uma janela de Hann para reduzir o vazamento espectral, e transformado pela FFT:

$$w[n] = 0{,}5\left[1 - \cos\left(\frac{2\pi n}{M-1}\right)\right]$$

$$X[k] = \sum_{n=0}^{M-1} w[n]\,x[n]\,e^{-2\pi i\,kn/M}$$

A amplitude em cada frequência, normalizada de modo que uma oscilação senoidal de amplitude $a$ apareça com valor $a$ no espectro, e o eixo de frequências são:

$$a[k] = \frac{2\,|X[k]|}{\sum_n w[n]}, \qquad f_k = \frac{k\,f_s}{M}$$

A resolução em frequência e o limite máximo observável (frequência de Nyquist) são:

$$\Delta f = \frac{f_s}{M} \approx 0{,}017\ \text{Hz}, \qquad f_{\text{Nyquist}} = \frac{f_s}{2} = 100\ \text{Hz}$$

A frequência dominante é aquela em que $a[k]$ é máxima, excluindo $k = 0$ (componente contínua).

---

## Parâmetros do código de coleta

Com base no detalhamento matemático apresentado acima, a tabela a seguir mapeia os símbolos com as variáveis utilizadas no código de coleta. A coluna "Símbolo" é a usada nas equações. A tabela em imagem, para uso em slides, está em [`figuras/tabela_ajustes.png`](figuras/tabela_ajustes.png).

| Símbolo | Variável no código | Valor | Significado |
|---|---|---|---|
| $T_s$ | `PERIODO_US` | 5000 µs | Intervalo entre amostras (taxa de 200 Hz) |
| $N$ | `N_OVERSAMPLE` | 4 | Leituras do conversor por amostra (média) |
| $\beta$ | `HIST` | 0,25 | Folga de decisão (histerese), em fração da amplitude |
| $A_{\min}$ | `SPAN_MIN` | 40 | Amplitude mínima para aceitar contagem |
| $\alpha$ | `DECAIMENTO` | 0,002 | Velocidade de adaptação do máximo e do mínimo ($\tau = 2{,}5\text{ s}$) |
| $\lambda$ | (argumento da análise) | 532 nm | Comprimento de onda do laser verde |

---

## Funcionamento do código de coleta (Arduino)

O programa repete continuamente o ciclo abaixo:

1. **Espera o próximo instante**, garantindo amostras em intervalos fixos $T_s$.
2. **Lê o sensor $N$ vezes e faz a média**, reduzindo o ruído eletrônico de cada amostra.
3. **Atualiza `vmax` e `vmin`**, que acompanham o sinal e decaem lentamente em direção a ele.
4. **Calcula `meio`, `span` e a folga**: o ponto médio, a amplitude e as linhas de decisão.
5. **Decide se conta uma franja**, com histerese e trava de ruído.
6. **Envia pela serial** a linha `t_us,leitura,franjas`.


## Funcionamento do código de análise (Python)

- **`gravar`:** abre a porta serial a 115200 baud, aguarda 2 s (o Arduino reinicia ao abrir a porta) e grava no arquivo as linhas válidas durante o tempo pedido.
- **`analisar`:** lê o arquivo e calcula a frequência de amostragem efetiva, a amplitude do sinal, o deslocamento pela contagem de franjas, o deslocamento pelo sinal bruto, o valor RMS e o espectro de frequências.

---

## Limitações

- **O LDR é lento.** Seu tempo de resposta é da ordem de dezenas de milissegundos, de modo que vibrações acima de alguns hertz aparecem atenuadas no espectro, mesmo com amostragem de 200 Hz. Um fotodiodo ou fototransistor seria mais adequado.
- **Um único sensor não dá o sentido do movimento.** 
  - Na contagem macro, toda passagem de franja soma $+1$ ao contador (inversões de sentido continuam somando).
  - No regime micro, flutuações de sentido oposto na mesma encosta da senoide geram o mesmo sinal analógico. Para detectar o sentido seriam necessários dois sensores defasados de um quarto de franja (quadratura dupla).
- **A contagem depende da relação sinal/ruído.** Ela só é confiável se $\beta A > R_{pp}$ (seção 4).
- **A conversão do sinal em deslocamento é uma aproximação linear**, válida para deslocamentos pequenos frente a $\lambda/4$ (seção 6).
- **A deriva lenta** (temperatura, acomodação mecânica) aparece como componente de baixa frequência no espectro e no RMS, e não representa vibração. Um filtro passa-alta antes do cálculo do RMS reduziria esse efeito.