# Biblioteca Escolar — Sistema de Gerenciamento

Sistema web completo para gerenciamento de biblioteca escolar com acervo, empréstimos, reservas e usuários. Desenvolvido com **Python (Flask) + SQLite + HTML/CSS/JS**.

## Funcionalidades

### Acervo
- Catálogo de livros com busca por título ou autor
- CRUD completo (cadastrar, editar, excluir livros)
- Status visual: Disponível, Emprestado, Reservado
- Categorização por gênero

### Empréstimos
- Empréstimo e devolução de livros com 1 clique
- Controle de prazos (14 dias)
- Listagem de empréstimos ativos por usuário
- Histórico completo de empréstimos

### Reservas
- Reservar livros disponíveis
- Cancelamento de reservas pelo usuário ou admin
- Lista de reservas ativas

### Usuários
- CRUD completo de usuários
- Controle de matrícula única
- Bloqueio de exclusão se houver empréstimo ativo
- Visualização de livros em posse do usuário

### Dashboard
- Estatísticas em tempo real (total livros, disponíveis, emprestados, etc.)
- Cards com acesso rápido a todos os módulos
- Alertas de empréstimos atrasados

### Painel de Configurações
- **Minha Conta**: editar perfil, alterar senha, ver meus empréstimos/reservas
- **Admin**: estatísticas do sistema, todos os empréstimos, reset do banco de dados

### Interface
- Navegação por menu superior em todas as páginas
- Design responsivo (desktop e mobile)
- Modais para formulários CRUD
- Login rápido com botões de teste

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3 + Flask |
| Banco | SQLite (local) / `/tmp` (Vercel) |
| Frontend | HTML5 + CSS3 + JavaScript (Vanilla) |
| Ícones | Font Awesome 6 |
| Deploy | Vercel (Python Serverless + Static) |

## Endpoints da API

### Autenticação
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/login` | Login do usuário |

### Livros
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/livros` | Listar todos |
| GET | `/api/livros/<id>` | Detalhes do livro |
| GET | `/api/livros/buscar?q=` | Buscar por título/autor |
| POST | `/api/livros` | Cadastrar |
| PUT | `/api/livros/<id>` | Editar |
| DELETE | `/api/livros/<id>` | Excluir |

### Empréstimos
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/emprestimos` | Listar todos |
| GET | `/api/emprestimos/ativos` | Empréstimos ativos |
| POST | `/api/emprestar` | Emprestar livro |
| POST | `/api/devolver` | Devolver livro |

### Reservas
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/reservas` | Listar reservas |
| POST | `/api/reservar` | Reservar livro |
| POST | `/api/cancelar-reserva` | Cancelar reserva |

### Usuários
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/usuarios` | Listar todos |
| POST | `/api/usuarios` | Cadastrar |
| PUT | `/api/usuarios/<id>` | Editar |
| DELETE | `/api/usuarios/<id>` | Excluir |
| PUT | `/api/usuarios/<id>/senha` | Alterar senha |
| GET | `/api/usuarios/<id>/emprestimos` | Empréstimos do usuário |

### Categorias
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/categorias` | Listar todas |
| POST | `/api/categorias` | Cadastrar |
| PUT | `/api/categorias/<id>` | Editar |
| DELETE | `/api/categorias/<id>` | Excluir |

### Sistema
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/dashboard` | Estatísticas gerais |
| GET | `/api/atrasados` | Empréstimos atrasados |
| POST | `/api/resetar` | Resetar banco de dados (admin) |

## Como executar localmente

```bash
# Instalar dependências
pip install flask flask-cors

# Iniciar servidor
python biblioteca.py

# Acessar
http://localhost:5000
```

O banco SQLite (`biblioteca.db`) é criado automaticamente na primeira execução com dados de exemplo.

## Deploy na Vercel

1. Conecte o repositório no [vercel.com/import](https://vercel.com/import)
2. A Vercel detecta o `vercel.json` automaticamente
3. O deploy usa `/tmp/biblioteca.db` (o sistema de arquivos do Vercel é read-only)

> **Nota:** SQLite em `/tmp` é efêmero — dados podem ser perdidos em redeploys. Para dados permanentes, migrar para Vercel Postgres.

## Usuários de teste

| Matrícula | Senha | Nome | Tipo |
|-----------|-------|------|------|
| `admin` | `admin123` | Administrador | Admin |
| `larissa` | `1235` | Larissa | Usuário |
| `2024001` | `senha123` | João Silva | Usuário |
| `2024002` | `senha123` | Maria Oliveira | Usuário |
| `2024003` | `senha123` | Pedro Santos | Usuário |
