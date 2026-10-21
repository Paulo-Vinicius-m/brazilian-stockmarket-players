# A Teia do Poder Corporativo: Análise Topológica de *Interlocking Directorates* no Mercado de Capitais Brasileiro (CVM 2025–2026)

Disciplina de Algoritmos e Estruturas de Dados II (Grafos), Unidade 01, UFRN/DCA.
Notebook principal: [`Projeto1_EDII.ipynb`](Projeto1_EDII.ipynb).

## Integrantes
João Victor do Nascimento Ribeiro de Andrade · Paulo Vinicius de Mendonça Carvalho

## Vídeo
https://youtu.be/... *(substituir pelo link final; até 15 min no total)*

## Problema e pergunta
Companhias abertas parecem autônomas, mas muitas compartilham os mesmos administradores e conselheiros (*interlocking directorates*). Quem ocupa assentos em várias companhias funciona como canal de informação entre elas e pode concentrar poder decisório.

> **Pergunta:** quais executivos atuam como as principais pontes estruturais entre as companhias abertas brasileiras, como essas companhias se conectam por meio deles e qual é o núcleo que concentra o comando?

Uma tabela responde só perguntas locais (quantos cargos uma pessoa tem). O papel de ponte depende de caminhos mínimos e da conectividade global, por isso a pergunta exige grafos. Quem se beneficia: reguladores (CVM, CADE), analistas de risco e governança, e pesquisadores de sociologia econômica.

## Dados (fonte, como obter, limpeza)
- **Fonte:** Portal de Dados Abertos da CVM, Formulário de Referência (FRE), `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/` (`fre_cia_aberta_2025.zip` e `fre_cia_aberta_2026.zip`).
- **Tabela usada:** `fre_cia_aberta_administrador_membro_conselho_fiscal_{ano}.csv` (separador `;`, codificação `latin1`). É a única com as **pessoas físicas** que ocupam Conselho de Administração, Diretoria Estatutária e Conselho Fiscal. As demais tabelas (posição acionária, remuneração etc.) não identificam quem senta nos colegiados.
- **Como obter:** o próprio notebook baixa e extrai os zips na primeira execução (célula 4). O script opcional `download_data.py` baixa todas as tabelas para `data/`, útil para explorar as demais, mas o notebook não depende dele.
- **Limpeza (célula 6):**
  1. Remoção de linhas sem `Nome_Companhia` ou `Nome` (nenhuma removida na execução de referência).
  2. Padronização textual: `strip()` e caixa alta, para que `"João Silva "` e `"JOÃO SILVA"` sejam o mesmo nó.
  3. Deduplicação do par `(companhia, pessoa)`, pois a mesma empresa reenvia versões do FRE e a pessoa pode acumular cargos no mesmo colegiado.
  4. A limpeza vem **antes** de qualquer projeção, porque projeção e contração não comutam (Semana 6): duplicatas inflariam os pesos.
- **Resultado:** 17.452 registros brutos viram **9.023 vínculos únicos** entre **707 companhias** e **6.926 executivos**.

## Modelagem (nó, aresta, peso, direção, o que ficou de fora)
Todas as redes são **não direcionadas**, porque o interesse é a convivência colegiada (canal de informação nos dois sentidos).

| Rede | Nó | Aresta | Peso | Tamanho |
| :--- | :--- | :--- | :--- | :--- |
| **1. Geral** $G_{full}$ | Pessoa ou Empresa | Vínculo registrado na CVM | Nº de mandatos da pessoa na empresa (atributo: órgãos) | 7.633 nós, 9.023 arestas |
| **2. Bipartida** $B$ | Pessoa ($V_P$) / Empresa ($V_C$) | Pessoa ocupa mandato na empresa | Sem peso | 7.633 nós, 9.023 arestas |
| **3. Pessoa–Pessoa** $G_P$ | Pessoa | Atuam juntas em ao menos 1 empresa | Nº de empresas compartilhadas | 6.926 nós, 75.705 arestas |
| **4. Empresa–Empresa** $G_C$ | Empresa | Compartilham ao menos 1 administrador | Nº de administradores em comum | 707 nós, 1.838 arestas |
| **5. Projeção de Newman** $G_N$ | Pessoa | Mesmas arestas de $G_P$ | $w_{ij}=\sum_{c\in N(i)\cap N(j)} \frac{1}{k_c-1}$ | 6.926 nós, 75.705 arestas |

Duas escolhas para a análise: o **backbone** de $B$ (executivos com grau $\ge 2$ e suas companhias: 1.772 nós, 3.288 arestas) torna a visualização legível, e a **projeção de Newman** atenua o "artefato do clique" (uma empresa com $k$ membros gera $\binom{k}{2}$ arestas; o Bradesco, com 117, gera 6.786).

**O que ficou de fora:** acionistas passivos e fundos (não ocupam assento), companhias de capital fechado (não publicam o FRE), hierarquia entre órgãos (direção das arestas), o **setor** das companhias (a tabela usada não traz) e a dimensão temporal (2025 e 2026 foram unificados).

## Conteúdo do curso utilizado
Convenção: `cél. N` é a N-ésima célula de `Projeto1_EDII.ipynb`, contando markdown e código a partir de 1.

| conceito | semana | onde aparece | para que serviu |
| :--- | :---: | :--- | :--- |
| Nós, arestas, atributos; redes não direcionadas e ponderadas; NetworkX | 2 | `Projeto1_EDII.ipynb`, cél. 6 | Construir as 4 modelagens |
| Representação por matrizes (biadjacência $B$, $B B^\top$, $B^\top B$ esparsas) | 2 | cél. 6 | Validar as projeções com `assert` |
| Normalização de nomes e resolução de aliases | 6 | cél. 6 | Evitar nós duplicados antes de projetar |
| Redes bipartidas | 6 | cél. 6, 9 | Modelar a afiliação pessoa–empresa e extrair o backbone |
| Projeção de redes bipartidas e artefato do clique | 6 | cél. 6, 7, 13 | Medir o inchaço dos cliques e escolher a projeção |
| Pesos de projeção (Newman, $1/(k_c-1)$), extensão dos pesos por coocorrência | 6 | cél. 13, 15 | Reduzir o peso de conselhos grandes |
| Força ponderada e grau | 4/5, 6 | cél. 17 | Comparar critérios de importância |
| Hubs, ranking e comparação de centralidades (Spearman) | 4/5 | cél. 17, 19 | Ranquear executivos e comparar grau com betweenness |
| Betweenness ponderada (distância $1/w$) | 4/5, 6 | cél. 17, 19, 23 | Identificar as pontes entre grupos de companhias |
| Componentes conexos e componente gigante (GCC) | 4 | cél. 11 | Medir se o mercado é um bloco ou um arquipélago |
| Caminhos mínimos e diâmetro | 4 | cél. 11, 17 | Distância máxima no GCC e caminhos do betweenness |
| Densidade | 2, 6 | cél. 11 | Esparsidade da bipartida e do GCC |
| BFS (uso indireto) | 3 | cél. 11, 17 (`connected_components`, `diameter`, `betweenness_centrality`) | Percursos por trás dos componentes, do diâmetro e do betweenness |
| Remoção progressiva de nós e fragmentação do GCC | 4, 5 | cél. 21 | Validar que o ranking identifica pontes reais |
| Codificação visual (cor, tamanho, espessura, transparência) com Plotly | 4 | cél. 9, 15, 19, 21, 23 | Visualizar backbone, projeção, ranking e ego-networks |
| Distribuição de graus | 3, 5 | cél. 7, 13 | Mostrar a assimetria de conselhos e de pesos |

## Como executar
Estrutura do repositório:

```text
├── Projeto1_EDII.ipynb    # Notebook principal (análise completa)
├── download_data.py       # Opcional: baixa todas as tabelas do FRE para data/
├── requirements.txt
└── README.md
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook Projeto1_EDII.ipynb      # Run All
```

- Na primeira execução é preciso acesso à internet (a célula 4 baixa os zips da CVM para `fre_cia_aberta_2025/` e `fre_cia_aberta_2026/`).
- `matplotlib` e `seaborn` não estão no `requirements.txt`; a célula 2 instala qualquer pacote ausente.
- Os gráficos da Seção 4 são interativos (Plotly) e aparecem ao executar as células.
- O notebook foi escrito para rodar também no Google Colab (a primeira versão foi executada lá), mas a versão atual com Plotly foi testada apenas localmente.
- **Tempo:** cerca de 3 a 5 min (o diâmetro leva cerca de 1 min e o betweenness amostrado cerca de 1 min). `K_AMOSTRAS = 1500` (célula 17) usa pivôs com semente 42; com `K_AMOSTRAS = None` o betweenness é exato e leva alguns minutos a mais.

## Resultados
Valores da execução de referência (dados da CVM baixados em out/2026; os valores podem variar pouco se a CVM atualizar os arquivos).

**Conectividade (célula 11).** A rede bipartida tem 152 componentes. O GCC reúne 6.029 nós (79,0%) e **512 das 707 companhias (72,4%)**; o segundo maior componente tem só 30 nós. O diâmetro é 24 arestas (até 12 saltos entre companhias, pois cada salto empresa–executivo–empresa usa 2 arestas). A densidade bipartida é 0,0018. O mercado é um continente com ilhas pequenas.

**Só 17,2% dos executivos (1.191 de 6.926) ocupam 2 ou mais companhias** e sustentam toda a conectividade entre elas.

**Projeção de Newman (células 13 e 15).** Na projeção simples, os 10% maiores conselhos geram 47,9% das arestas. Na de Newman, respondem por 23,9% do peso total. A soma dos pesos (4.510,5) bate com $\sum_{c:k_c\ge2} k_c/2$. Também verificamos que a força de Newman de um executivo é igual ao seu número de companhias: o ganho da projeção está nas distâncias (betweenness), não na força.

**Quem conecta o mercado (células 17 a 23).**
- O betweenness ponderado correlaciona 0,90 (Spearman) com o número de cargos e só 0,45 com a força na projeção simples, que é dominada por conselhos grandes. Os cinco maiores são Maria Elvira Lopes Gimenez (13 companhias), Murici dos Santos (9), Carla Alessandra Trematore (8), Paulo Roberto Franceschi (8) e Marcelo Curti (9).
- **9 dos 10 maiores conectores atuam no Conselho Fiscal**, em geral contadores, economistas e advogados. Isso sugere um perfil de conselheiro fiscal profissional que costura companhias de setores distintos (observação descritiva, não causal).
- Entre quem atua em até 3 companhias, as maiores pontes são Roberto Pedote (2 companhias), Raquel Wille Sarquis (3) e Antonio Kandir (3), todas acima do percentil 97% de betweenness.
- **Robustez (célula 21).** Removendo 150 executivos, a fração de companhias no GCC cai de 72,4% para **56,9% (por betweenness)**, 60,5% (por nº de cargos) e 69,3% (aleatório, média de 10 sorteios). O betweenness encontra pontes mais efetivas que o grau, mas a diferença é modesta.
- Os 3 maiores conectores tocam 30 companhias e dividem o comando com 136 outros multi-conselheiros (ego-network, célula 23).

**Mandatos cruzados mais intensos (célula 6).** Os pares com mais administradores em comum são do mesmo grupo: as três empresas CEMIG (31), Gerdau e Metalúrgica Gerdau (19) e Argo Energia e Argo Transmissão (17). O papel estrutural de um executivo não implica irregularidade; é uma propriedade da rede.

## Limitações e próximos passos
- **Núcleo do comando não calculado.** A pergunta cita o "núcleo", mas não aplicamos k-core/k-shell. Próximo passo: `core_number` em $G_C$ e em $G_N$ (em $G_P$ o núcleo seria inflado pelo clique do Bradesco), comparando grau e pertencimento ao núcleo.
- **Pontes entre setores não demonstradas.** O CSV não traz setor. Seria preciso juntar o cadastro de companhias da CVM (`CAD/DADOS/cad_cia_aberta.csv`) para medir pontes entre setores de fato.
- **Identidade por nome.** O nó da pessoa é o nome em caixa alta. Homônimos viram um só nó e grafias diferentes viram dois. `Data_Nascimento` poderia desambiguar.
- **Grupos econômicos.** Interlocks dentro do mesmo grupo (CEMIG, Gerdau) dominam os maiores pesos e inflam a coesão aparente. Não separamos interlocks de grupo de interlocks genuínos.
- **Betweenness aproximado.** O cálculo usa 1.500 pivôs (semente fixa). O top 10 teve o mesmo conjunto de executivos em execuções com versões ligeiramente diferentes dos dados, mas a ordem e os valores finos podem mudar; `K_AMOSTRAS = None` dá o valor exato.
- **Betweenness e grau andam juntos** (Spearman 0,90), então o ranking de pontes é próximo ao ranking por cargos. O que sustenta o papel de ponte é a validação por remoção, cujo efeito é modesto (57% contra 61%).
- **Recorte temporal.** 2025 e 2026 estão unificados. Comparar os dois anos mediria a rotatividade dos conectores.
- **Conteúdo não explorado:** triângulos e agrupamento (separar triângulos formados por três pessoas diferentes dos formados por uma só), BFS e DFS implementados à mão, exportação para o Gephi, `nxviz`.
- **Ética.** Os dados são públicos, mas descrevem pessoas reais. Os resultados descrevem posição na rede, não conduta.

## Referências
- CVM. *Dados Abertos: Formulário de Referência (FRE)*. https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/ e dicionário em `.../FRE/META/`.
- CVM. Resolução CVM nº 80/2022 (registro de emissores e Formulário de Referência).
- Material da disciplina (Semanas 1 a 6), Prof. Dr. Ivanovitch Medeiros Dantas da Silva, UFRN/DCA, github.com/ivanovitchm/datastructure.
