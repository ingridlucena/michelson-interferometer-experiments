// Contador de franjas - Interferometro de Michelson com modulo LDR
// Ligacao: VCC -> 5V | GND -> GND | AO -> A0
// Saida serial (CSV, 115200 baud): t_us,leitura,franjas

#include <Arduino.h>

const uint8_t  PIN_LDR      = A0;
const uint32_t PERIODO_US   = 5000;   // 200 Hz de amostragem
const uint8_t  N_OVERSAMPLE = 4;      // media de leituras
const int      SPAN_MIN     = 40;     // amplitude minima (max-min) para contar
const float    HIST         = 0.25;   // histerese (25% da amplitude)
const float    DECAIMENTO   = 0.002;  // adaptacao de max/min

float vmax, vmin;
bool estadoAlto = false;
unsigned long franjas = 0;
uint32_t proximo;

float lerLDR() {
  long soma = 0;
  for (uint8_t i = 0; i < N_OVERSAMPLE; i++) soma += analogRead(PIN_LDR);
  return soma / (float)N_OVERSAMPLE;
}

void setup() {
  Serial.begin(115200);
  Serial.println(F("t_us,leitura,franjas"));
  float v = lerLDR();
  vmax = v + 1;
  vmin = v - 1;
  proximo = micros();
}

void loop() {
  if ((int32_t)(micros() - proximo) < 0) return;
  proximo += PERIODO_US;

  float v = lerLDR();

  if (v > vmax) vmax = v; else vmax -= (vmax - v) * DECAIMENTO;
  if (v < vmin) vmin = v; else vmin += (v - vmin) * DECAIMENTO;

  float span = vmax - vmin;
  float meio = 0.5 * (vmax + vmin);

  if (span > SPAN_MIN) {
    float h = HIST * 0.5 * span;
    if (!estadoAlto && v > meio + h) {
      estadoAlto = true;
      franjas++;
    } else if (estadoAlto && v < meio - h) {
      estadoAlto = false;
    }
  }

  Serial.print(micros()); Serial.print(',');
  Serial.print(v, 1);     Serial.print(',');
  Serial.println(franjas);
}