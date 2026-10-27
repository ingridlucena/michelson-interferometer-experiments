#!/usr/bin/env python3
"""
Gravação e análise do sinal do interferômetro (Arduino + LDR).

Uso:
  pip install pyserial numpy matplotlib
  python analise_vibracao.py log COM3 60 medida1.csv     # grava 60 s
  python analise_vibracao.py analisar medida1.csv 532    # análise (lambda em nm)
"""
import sys
import numpy as np


def gravar(porta, duracao, arquivo):
    import serial, time
    ser = serial.Serial(porta, 115200, timeout=1)
    time.sleep(2)  # Aguarda 2s pois o Arduino reinicia ao abrir a porta serial
    ser.reset_input_buffer()
    t0 = time.time()
    n = 0
    with open(arquivo, "w") as f:
        f.write("t_us,leitura,franjas\n")
        while time.time() - t0 < duracao:
            linha = ser.readline().decode(errors="ignore").strip()
            # Valida se a linha recebida contem exatamente os 3 campos CSV esperados
            if linha.count(",") == 2 and linha[0].isdigit():
                f.write(linha + "\n")
                n += 1
    print(f"{n} amostras gravadas em {arquivo}")


def analisar(arquivo, lam_nm):
    import matplotlib.pyplot as plt
    
    lam = lam_nm * 1e-9  # Converte o comprimento de onda de nm para metros
    
    # Carrega os dados gravados (ignorando o cabeçalho)
    d = np.genfromtxt(arquivo, delimiter=",", skip_header=1)
    t = (d[:, 0] - d[0, 0]) * 1e-6  # Converte timestamps de us para segundos
    I = d[:, 1]                      # Leitura analógica do ADC
    N = d[:, 2]                      # Contagem de franjas
    
    # Calcula a taxa de amostragem real fs (em Hz) usando a mediana dos intervalos
    fs = 1.0 / np.median(np.diff(t))

    # Calcula a amplitude (span) usando percentis 1 e 99 para rejeitar ruídos isolados
    Imax, Imin = np.percentile(I, 99), np.percentile(I, 1)
    span = Imax - Imin
    
    print(f"Amostragem: {fs:.1f} Hz | duração: {t[-1]:.1f} s")
    print(f"Amplitude do sinal (p99-p1): {span:.1f} contagens ADC")

    # --- 1) Contagem de Franjas (Regime Macro: dx >= lambda/2) ---
    desloc_franjas = (N - N[0]) * lam / 2
    print(f"Franjas contadas: {int(N[-1] - N[0])} "
          f"(~{desloc_franjas[-1]*1e6:.2f} um de deslocamento total)")

    # --- 2) Aproximação Linear na Quadratura (Regime Micro: dx << lambda/4) ---
    # Fórmula: dx = lambda * dI / (2 * pi * span)
    dI = I - np.mean(I)
    x = lam * dI / (2 * np.pi * span)
    print(f"RMS do deslocamento (aprox. linear): {np.std(x)*1e9:.1f} nm")
    
    # Alerta caso o sinal saia da regiao linear da senoide
    if span > 0 and np.max(np.abs(dI)) > 0.4 * span:
        print("AVISO: o sinal varre quase uma franja inteira; a aproximação "
              "linear subestima o deslocamento. Use só a contagem nesse caso.")

    # --- 3) Análise Espectral no Domínio da Frequência (FFT) ---
    # Aplica janela de Hann no sinal com média removida para mitigar o spectral leakage
    xs = (x - x.mean()) * np.hanning(len(x))
    F = np.fft.rfft(xs)
    f = np.fft.rfftfreq(len(x), 1 / fs)
    
    # Normalização da amplitude real do pico espectral em metros
    amp = 2 * np.abs(F) / np.sum(np.hanning(len(x)))
    
    # Identifica o pico dominante (excluindo o componente DC / k=0)
    k = np.argmax(amp[1:]) + 1
    print(f"Pico dominante: {f[k]:.2f} Hz, amplitude ~{amp[k]*1e9:.1f} nm")

    # --- Plotagem dos Gráficos ---
    fig, ax = plt.subplots(3, 1, figsize=(9, 9))
    
    # Gráfico 1: Sinal analógico bruto
    ax[0].plot(t, I)
    ax[0].set_ylabel("ADC")
    ax[0].set_title("Sinal do LDR")
    
    # Gráfico 2: Deslocamento acumulado por contagem de franjas
    ax[1].plot(t, desloc_franjas * 1e6)
    ax[1].set_ylabel("Desloc. por contagem (um)")
    ax[1].set_xlabel("t (s)")
    
    # Gráfico 3: Espectro de frequências vibracionais
    ax[2].semilogy(f[1:], amp[1:] * 1e9)
    ax[2].set_xlabel("Frequência (Hz)")
    ax[2].set_ylabel("Amplitude (nm)")
    ax[2].set_title("Espectro de vibração (limitado pela resposta do LDR)")
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) >= 5 and sys.argv[1] == "log":
        gravar(sys.argv[2], float(sys.argv[3]), sys.argv[4])
    elif len(sys.argv) >= 4 and sys.argv[1] == "analisar":
        analisar(sys.argv[2], float(sys.argv[3]))
    else:
        print(__doc__)