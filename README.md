# Automatização de um interferômetro de Michelson de baixo custo

Este repositório reúne os códigos, a descrição matemática e os experimentos do projeto de automatização de um interferômetro de Michelson de baixo custo, construído na [nome da universidade].

## Sobre o projeto

O projeto parte de um interferômetro de Michelson montado com materiais de baixo custo e funcional para a realização de experimentos no laboratório da universidade. O objetivo é automatizar as medições feitas com o aparelho: em vez de observar e contar as franjas de interferência a olho, um sensor de luz conectado a uma placa Arduino registra o padrão e o número de franjas. Posteriormente foi adcionado um atuador piezoelétrico no espelho móvel do interferômetro, afim de fazer o deslocamento micrométrico de forma controlada.

Na fase de validação do projeto, foram realizados experimentos para verificar o desempenho da automatização e os limites do sistema. Cada experimento está descrito neste repositório, em uma pasta própria que contém os códigos utilizados e um README com a ideia do experimento, a forma como foi conduzido, o funcionamento dos códigos e as fórmulas envolvidas.

## Experimentos

| # | Pasta | Descrição |
|---|---|---|
| 01 | [sensitivity-to-vibrations](experiments/sensitivity-to-vibrations) | Contagem automática de franjas com um sensor LDR e estudo da sensibilidade do interferômetro a vibrações do ambiente |

## Estrutura do repositório

```
michelson-interferometer-experiments/
├── README.md                       # apresentação do projeto (este arquivo)
└── experiments/
    └── sensitivity-to-vibrations/  # experimento 01
        ├── README.md/ #apresentação do experimento 01
        ├── Arduino/
        └── Python/
```

Cada pasta de experimento é independente: contém os códigos de coleta (Arduino) e de análise (Python) — caso seja necessário uma análise mais detalhada — usados naquele experimento e um README com a descrição matemática do que foi feito.


## Autoria

Ingrid Lucena, João Matheus de Moura, Michele Dornelas e Prof. Dr. Fábio Novaes.

Universidade Federal Rural de Pernambuco (UFRPE) — Unidade Acadêmica de Belo Jardim, curso de Engenharia de Controle e Automação.

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).