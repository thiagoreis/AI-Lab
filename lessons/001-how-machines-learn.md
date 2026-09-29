# Aula 001 — Como uma máquina aprende?

## Objetivo

Entender o mecanismo mínimo de aprendizado de máquina antes de usar bibliotecas de alto nível.

## Ideia central

Em Machine Learning, fornecemos exemplos e buscamos parâmetros de um modelo que produzam previsões adequadas para os dados.

Forma abstrata:

`y = f(X)`

- `X`: features de entrada.
- `y`: target.
- `f`: modelo.

## Exemplo

Para previsão de preço de uma casa:

- features: área e quantidade de quartos;
- target: preço.

Um modelo linear simples pode ser escrito como:

`y = w*x + b`

- `w`: peso;
- `b`: bias/intercepto.

## Erro e loss

Uma função de perda mede a diferença entre o valor real e a previsão.

Para um exemplo simples:

`Loss = (y_real - y_pred)^2`

O treinamento procura reduzir essa perda.

## Gradient Descent

A ideia é ajustar os parâmetros na direção que reduz a loss.

`w_new = w - learning_rate * dL/dw`

O `learning_rate` controla o tamanho do passo.

## Ciclo de treinamento

`dados → modelo → previsão → loss → gradiente → atualização → repetir`

## Experimento mínimo

```python
x = 2
y_real = 10

w = 0
b = 0

learning_rate = 0.01

for epoch in range(100):
    y_pred = w * x + b
    loss = (y_real - y_pred) ** 2

    dw = -2 * x * (y_real - y_pred)
    db = -2 * (y_real - y_pred)

    w -= learning_rate * dw
    b -= learning_rate * db

    print(
        f"epoch={epoch:03d} "
        f"prediction={y_pred:.4f} "
        f"loss={loss:.4f}"
    )

print("w =", w)
print("b =", b)
```

## Exercícios

1. Compare `learning_rate = 0.1`, `0.01` e `0.001`.
2. Troque o exemplo para `x = 5`, `y_real = 25`.
3. Explique, com suas palavras, por que o `learning_rate` existe.
4. Tente prever o comportamento de um `learning_rate` muito grande antes de testá-lo.

## Critério para avançar

Consigo explicar sem consultar material:

- o que é feature;
- o que é target;
- o que o modelo representa;
- o que a loss mede;
- o que o gradiente informa;
- por que o learning rate influencia o treinamento.
