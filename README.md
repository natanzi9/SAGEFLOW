# Sageflow - Plataforma Inteligente de Gestão Financeira Familiar

O **Sageflow** é uma aplicação web completa, centralizada e moderna desenvolvida em Python com Flask, SQLAlchemy e Chart.js, seguindo fielmente a especificação e a identidade visual baseada nos tons de **Verde Sage**, **Bege** e **Off White**.

---

## 🎨 Identidade Visual & Design System
O visual da plataforma foi projetado especificamente em torno da paleta minimalista:
- **Verde Sage:** `#5F7D67` (Ações principais, links)
- **Verde Escuro:** `#3F5C45` (Sidebar, cabeçalhos, branding)
- **Bege:** `#F5F1E8` (Cards secundários, preenchimento de inputs)
- **Off White:** `#FAF8F3` (Cor de fundo geral)
- **Cinza Claro:** `#E5E2DA` (Bordas, separadores, tabelas)

---

## 🚀 Como Iniciar o Sistema (Localmente)

Siga os passos abaixo para rodar o servidor web:

### 1. Requisitos
Você precisará ter o Python instalado (instalamos com a versão `3.8.10`). O ambiente virtual já está criado e configurado na pasta do projeto (`venv`).

### 2. Ativar o Ambiente Virtual
Abra um terminal na pasta do projeto (ou no VS Code) e execute:

**No Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**No Windows (Cmd):**
```cmd
.\venv\Scripts\activate.bat
```

### 3. Iniciar o Servidor Flask
Com o ambiente ativado, execute o script de entrada:
```bash
python run.py
```

O console exibirá que o servidor está rodando no endereço:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📂 Estrutura do Sistema Criado

A arquitetura segue uma estrutura organizada em Blueprints para garantir manutenibilidade:

- `app/`
  - `__init__.py`: Inicializa extensões (`SQLAlchemy`, `LoginManager`), carrega configurações e registra as rotas.
  - `models.py`: Modelos de banco de dados (`User`, `Account`, `Card`, `Transaction`, `Budget`, `Goal`, `Investment`, `BillPayable`, `BillReceivable`).
  - `routes/`: Regras de negócio divididas por domínio:
    - `auth.py`: Fluxo de login, registro de conta familiar e redefinição de senha.
    - `dashboard.py`: Painel geral com resumos, atalhos de contas próximas e metas.
    - `accounts.py`: Gerenciamento de contas bancárias (Corrente, Poupança, Carteira Digital).
    - `transactions.py`: Registros de receitas, despesas e transferências.
    - `cards.py`: Controle de cartões, limites e pagamento de faturas.
    - `bills.py`: Contas a pagar e receber recorrentes com vinculação bancária para débito/crédito.
    - `budgets.py`: Orçamentos mensais com alertas automáticos se exceder o limite.
    - `goals.py`: Metas financeiras com aportes diretos das contas.
    - `investments.py`: Resgates e compras de ativos de renda fixa, variável ou cripto.
    - `reports.py`: Processamento de dados agregados dos últimos 6 meses para visualização gráfica.
  - `static/`:
    - `css/style.css`: Estilização premium baseada na paleta Sage, com transições suaves e layout responsivo.
    - `js/main.js`: Lógica cliente-side (toggles de formulário de acordo com tipo de transação).
  - `templates/`: Interfaces HTML5 semânticas com gráficos interativos carregados via **Chart.js** CDN.

---

## 💾 Banco de Dados
Por padrão, o sistema utiliza o **SQLite** (`instance/sageflow.db` ou `sageflow.db` na raiz) que é gerado e configurado automaticamente ao rodar o projeto pela primeira vez (dispensa configuração adicional). 

Para rodar em **MySQL**, basta definir a variável de ambiente:
```bash
set DATABASE_URL=mysql+pymysql://usuario:senha@host:porta/database
```
