# Roadmap de Formação em Inteligência Artificial

## Objetivo final

Evoluir de **Software Engineer → AI Engineer → AI Architect**, com capacidade de:

- entender os fundamentos matemáticos e estatísticos relevantes;
- construir, treinar, avaliar e depurar modelos de ML/DL;
- entender Transformers e LLMs em nível de engenharia;
- construir aplicações com RAG, tool use e agentes;
- colocar sistemas de IA em produção;
- operar, observar, avaliar e controlar custo/latência;
- projetar arquiteturas de IA escaláveis, seguras e avaliáveis.

## Princípios

- 30% teoria / 70% prática.
- Um projeto evolutivo acompanha o aprendizado.
- Fundamentos antes de abstrações.
- Avaliação é parte do produto, não uma etapa posterior.
- Cada etapa termina com evidência prática de domínio.

---

# Etapa 1 — AI Foundations

**Duração alvo:** 6–8 semanas

### Tópicos

#### Python para IA
- NumPy
- Pandas
- Matplotlib
- typing
- dataclasses
- funções e módulos
- ambientes virtuais
- Jupyter

#### Matemática aplicada
- vetores e matrizes
- produto escalar
- norma e distância
- multiplicação de matrizes
- derivadas
- gradiente
- chain rule
- otimização

#### Estatística e probabilidade
- média, mediana e variância
- distribuições
- probabilidade condicional
- Bayes
- correlação e covariância
- amostragem
- incerteza

### Resultado esperado
Conseguir explicar o ciclo:

`dados → modelo → previsão → loss → gradiente → atualização → repetição`

### Projeto
**Customer Churn Prediction** com pipeline de dados, treinamento, avaliação e API.

---

# Etapa 2 — Machine Learning + Deep Learning

**Duração alvo:** 6–8 semanas

### Machine Learning
- supervised vs. unsupervised learning
- regression
- classification
- clustering
- feature engineering
- train / validation / test
- cross-validation
- baselines
- data leakage
- overfitting / underfitting

### Modelos
- Linear Regression
- Logistic Regression
- Decision Trees
- Random Forest
- Gradient Boosting
- XGBoost

### Avaliação
- confusion matrix
- precision
- recall
- F1
- ROC-AUC
- PR-AUC
- análise de erros

### Deep Learning
- perceptron
- redes neurais
- funções de ativação
- loss functions
- backpropagation
- otimização
- CNN
- RNN/LSTM
- PyTorch

### Projeto
Treinar e servir pelo menos um modelo de Deep Learning com PyTorch.

---

# Etapa 3 — Transformers + LLMs

**Duração alvo:** 6–8 semanas

### Fundamentos
- tokenização
- embeddings
- attention
- self-attention
- positional information
- Transformer
- encoder / decoder
- inference
- sampling
- temperature
- top-k / top-p
- context window
- quantization

### LLM Engineering
- APIs de modelos
- structured outputs
- function calling
- streaming
- retries / fallback
- caching
- custo e latência
- segurança básica

### Ferramentas/ambiente
- Hugging Face
- PyTorch
- modelos via API
- modelos open-source/local quando apropriado

### Projeto
Construir uma aplicação de LLM com saída estruturada, avaliação básica e telemetria.

---

# Etapa 4 — RAG + Agents

**Duração alvo:** 8–12 semanas

### RAG
- chunking
- metadata
- embeddings
- vector search
- cosine similarity
- hybrid search
- reranking
- query transformation
- context construction
- citations
- retrieval evaluation
- hallucination analysis

### Agents
- tool calling
- tool schemas
- agent loops
- planning
- memory
- workflows
- human-in-the-loop
- single-agent vs. multi-agent
- MCP

### Projeto principal
## DevGears AI

Assistente especializado em programação, alimentado por documentação, artigos,
ebooks e conteúdos próprios.

Capacidades progressivas:
- responder perguntas sobre a base documental;
- citar fontes;
- pesquisar documentação;
- analisar código;
- chamar ferramentas;
- gerar exemplos;
- executar workflows controlados.

---

# Etapa 5 — MLOps + LLMOps

**Duração alvo:** 6–10 semanas

### Produção
- Docker
- APIs
- CI/CD
- cloud
- filas e workers quando necessários
- caching
- secrets management

### Observabilidade
- logs
- traces
- métricas
- latência
- throughput
- token usage
- custo
- tool success/failure
- qualidade de retrieval
- qualidade de resposta

### Evaluation
- offline evaluation
- golden datasets
- regression tests para prompts/RAG
- avaliação de retrieval
- avaliação de respostas
- feedback do usuário

### Projeto
Publicar o DevGears AI em ambiente de produção com observabilidade e avaliação.

---

# Etapa 6 — AI Architecture

**Duração alvo:** 8–16 semanas

### Tópicos
- AI system architecture
- distributed systems for AI
- model serving
- inference architecture
- GPU workloads
- scaling
- queueing / async processing
- multi-model architectures
- AI gateways
- security
- prompt injection
- data protection
- governance
- cost architecture
- reliability
- disaster recovery

### Resultado final
Projetar e justificar uma **AI Platform** completa, documentando:
- requisitos;
- arquitetura;
- componentes;
- fluxos;
- trade-offs;
- segurança;
- observabilidade;
- custo;
- estratégia de evolução.

---

# Stack-alvo

| Área | Stack inicial / referência |
|---|---|
| Linguagem | Python |
| ML | scikit-learn |
| Modelos tabulares | XGBoost |
| Deep Learning | PyTorch |
| LLM | APIs + modelos open-source |
| Embeddings | modelos de embedding |
| Vector DB | pgvector / Qdrant |
| Backend IA | FastAPI / ASP.NET |
| Frontend | React / TypeScript |
| Containers | Docker |
| Orquestração | Kubernetes |
| Cloud | Azure + AWS |
| MLOps/experimentos | MLflow e equivalentes |
| Observabilidade | OpenTelemetry + stack adequada |
| Agents | tool calling / MCP / workflows |

---

# Critério de especialização

Não considerar uma área "dominada" apenas porque um curso foi concluído.

Uma etapa é considerada dominada quando consigo:

1. explicar os conceitos sem depender de anotações;
2. implementar uma versão funcional;
3. medir e avaliar o resultado;
4. identificar limitações e falhas;
5. aplicar o conceito em um projeto real;
6. explicar trade-offs de arquitetura e produção quando aplicável.
