#!/usr/bin/env python3
"""
Gravação e análise do sinal do interferômetro (Arduino + LDR).

Uso:
  pip install pyserial numpy matplotlib
  python analise_vibracao.py log COM3 60 medida1.csv     # grava 60 s (Linux: /dev/ttyUSB0)
  python analise_vibracao.py analisar medida1.csv 650    # análise (lambda em nm)

Ideia: com o interferômetro parado, vibrações do ambiente movem os espelhos e
fazem a intensidade oscilar. Dois tipos de informação:
  1) Contagem de franjas: mede a deriva/movimentos GRANDES (>= lambda/2).
  2) Sinal bruto: mede vibrações PEQUENAS (< lambda/4) via aproximação linear
     no ponto de quadratura (meio da franja), e dá o espectro de frequências.
"""
import sys
import numpy as np


def gravar(porta, duracao, arquivo):
    import serial, time
    ser = serial.Serial(porta, 115200, timeout=1)
    time.sleep(2)  # Arduino reinicia ao abrir a porta
    ser.reset_input_buffer()
    t0 = time.time()
    n = 0
    with open(arquivo, "w") as f:
        f.write("t_us,leitura,franjas\n")
        while time.time() - t0 < duracao:
            linha = ser.readline().decode(errors="ignore").strip()
            if linha.count(",") == 2 and linha[0].isdigit():
                f.write(linha + "\n")
                n += 1
    print(f"{n} amostras gravadas em {arquivo}")


def analisar(arquivo, lam_nm):
    import matplotlib.pyplot as plt
    lam = lam_nm * 1e-9
    d = np.genfromtxt(arquivo, delimiter=",", skip_header=1)
    t = (d[:, 0] - d[0, 0]) * 1e-6
    I = d[:, 1]
    N = d[:, 2]
    fs = 1.0 / np.median(np.diff(t))

    Imax, Imin = np.percentile(I, 99), np.percentile(I, 1)
    span = Imax - Imin
    print(f"Amostragem: {fs:.1f} Hz | duração: {t[-1]:.1f} s")
    print(f"Amplitude do sinal (p99-p1): {span:.1f} contagens ADC")

    # 1) Contagem de franjas -> deslocamento acumulado (lambda/2 por franja)
    desloc_franjas = (N - N[0]) * lam / 2
    print(f"Franjas contadas: {int(N[-1] - N[0])} "
          f"(~{desloc_franjas[-1]*1e6:.2f} um de deslocamento total)")

    # 2) Sinal bruto -> deslocamento (válido para amplitudes << lambda/4)
    #    I = I0(1 + V cos(phi)), phi = 4*pi*x/lambda. Perto da quadratura:
    #    dx = lambda * dI / (2*pi*(Imax-Imin))
    dI = I - np.mean(I)
    x = lam * dI / (2 * np.pi * span)
    print(f"RMS do deslocamento (aprox. linear): {np.std(x)*1e9:.1f} nm")
    if span > 0 and np.max(np.abs(dI)) > 0.4 * span:
        print("AVISO: o sinal varre quase uma franja inteira; a aproximação "
              "linear subestima o deslocamento. Use só a contagem nesse caso.")

    # Espectro (remove a média, janela de Hann)
    xs = (x - x.mean()) * np.hanning(len(x))
    F = np.fft.rfft(xs)
    f = np.fft.rfftfreq(len(x), 1 / fs)
    amp = 2 * np.abs(F) / np.sum(np.hanning(len(x)))   # amplitude de pico (m)
    k = np.argmax(amp[1:]) + 1
    print(f"Pico dominante: {f[k]:.2f} Hz, amplitude ~{amp[k]*1e9:.1f} nm")

    fig, ax = plt.subplots(3, 1, figsize=(9, 9))
    ax[0].plot(t, I); ax[0].set_ylabel("ADC"); ax[0].set_title("Sinal do LDR")
    ax[1].plot(t, desloc_franjas * 1e6)
    ax[1].set_ylabel("Desloc. por contagem (um)"); ax[1].set_xlabel("t (s)")
    ax[2].semilogy(f[1:], amp[1:] * 1e9)
    ax[2].set_xlabel("Frequência (Hz)"); ax[2].set_ylabel("Amplitude (nm)")
    ax[2].set_title("Espectro de vibração (limitado pela resposta do LDR)")
    plt.tight_layout(); plt.show()


if __name__ == "__main__":
    if len(sys.argv) >= 5 and sys.argv[1] == "log":
        gravar(sys.argv[2], float(sys.argv[3]), sys.argv[4])
    elif len(sys.argv) >= 4 and sys.argv[1] == "analisar":
        analisar(sys.argv[2], float(sys.argv[3]))
    else:
        print(__doc__)
