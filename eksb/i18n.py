"""Translations. Two languages, one dict, no framework.

Adding a language: add a key to STRINGS with the same keys as "en" and list
it in LANGUAGES. Missing keys fall back to English rather than crashing.
"""
from __future__ import annotations

LANGUAGES = {"en": "English", "pt-BR": "Português (Brasil)"}

STRINGS: dict[str, dict[str, str]] = {

"en": {
    # -- framing ------------------------------------------------------
    "product.name": "Emergent Knowledge Second Brain",
    "tagline": "Your knowledge should outlive the chat - and the model.",
    "pitch": (
        "Your AI history should become reusable knowledge, not disposable\n"
        "context.\n\n"
        "EKSB keeps your decisions, sources and project history in plain\n"
        "Markdown that belongs to you — not to one chat, one model or one\n"
        "provider. An AI assistant can then look up the part it needs,\n"
        "instead of you re-explaining the project every time."
    ),
    "first.journey": (
        "Try the demo  ->  add a project  ->  connect an AI assistant\n"
        "->  work normally. EKSB becomes the memory your assistant reads from."
    ),
    "first.addproject": "Add a project folder now?",
    "first.connect.hint": (
        "EKSB is most useful when an AI assistant can read it. That is\n"
        "optional, needs no API key, and can wait."
    ),
    "first.connect.now": "Show me how to connect one?",
    "arg.path": "<folder>",

    # -- first run ----------------------------------------------------
    "lang.choose": "Choose a language / Escolha um idioma:",
    "lang.saved": "Language set to {lang}.",
    "first.title": "Welcome to EKSB.",
    "first.what": "What would you like to do?",
    "first.try": "Try the demo",
    "first.create": "Create my workspace",
    "first.open": "Open an existing workspace",
    "first.learn": "Learn more",
    "ready": "You're ready.",
    "ready.next": "Three things to try next:",
    "arg.word": "<word>",

    # -- main menu ----------------------------------------------------
    "menu.title": "What would you like to do?",
    "menu.continue": "Where things stand",
    "menu.continue.demo": "Look around the demo",
    "menu.search": "Search my history",
    "menu.search.demo": "Search the demo",
    "menu.project": "Projects",
    "menu.connect": "Connect an AI assistant",
    "menu.add": "Add something",
    "menu.attention": "What needs my attention?",
    "menu.provenance": "Check where something came from",
    "menu.health": "Check my workspace",
    "menu.about": "About this installation",

    # -- where things stand ------------------------------------------
    "stat.title": "Where things stand",
    "stat.projects": "Projects",
    "stat.items": "Knowledge",
    "stat.ai": "AI assistants",
    "stat.noai": "none connected — optional, see \"Connect an AI assistant\"",
    "stat.recent": "Most recently touched",
    "stat.pending": "Waiting on you ({n})",
    "stat.seeall": "\"What needs my attention?\" has the full list.",

    # -- projects and ingestion --------------------------------------
    "proj.title": "Projects",
    "proj.what": "Projects",
    "proj.list": "List my projects",
    "proj.add": "Add a project folder",
    "proj.none": "No projects yet.",
    "proj.hint": "Add one with:  eksb ingest <folder>",
    "proj.counts": "{indexed} file(s) indexed · {integrated} note(s) written from them",
    "proj.levels": ("registered = EKSB knows where it is · indexed = its text is "
                    "searchable · integrated = knowledge written from it"),
    "level.registered": "registered",
    "level.indexed": "indexed",
    "level.integrated": "integrated",
    "ing.path": "Path to the project folder",
    "ing.name": "What should this project be called?",
    "ing.done": "Indexed {project}",
    "ing.added": "newly indexed",
    "ing.updated": "changed since last time (earlier versions kept)",
    "ing.unchanged": "already up to date",
    "ing.skipped": "skipped",
    "ing.truncated": "Stopped at {n} files. Raise it with --max-files.",
    "ing.indexed_not_understood": (
        "Indexed, not understood. The text is now searchable and citable —\n"
        "turning it into decisions and concepts is the next step, and it takes\n"
        "judgment: yours, or a connected assistant's."
    ),
    "ing.next": "Try:  eksb search <word>   ·   eksb connect",
    "ing.nodir": "There is no folder at {path}.",
    "ing.inside": "{path} is inside your workspace. Point at the project itself.",
    "skip.ignored": "ignored (build, cache, dependencies)",
    "skip.not-text": "not text",
    "skip.too-big": "too large",
    "skip.unreadable": "unreadable",
    "skip.over-limit": "over the file limit",

    # -- connecting an assistant --------------------------------------
    "conn.title": "Connect an AI assistant",
    "conn.what": (
        "EKSB can act as memory for an AI assistant that speaks MCP. The\n"
        "assistant then searches your history and adds to it, instead of you\n"
        "pasting context into every conversation.\n\n"
        "Nothing runs until the assistant starts it, and no API key is needed\n"
        "by EKSB itself."
    ),
    "conn.detected": "Clients found on this machine:",
    "conn.wired": "already configured",
    "conn.notwired": "not configured yet",
    "conn.nodetect": "No MCP client detected. The configuration below works for any.",
    "conn.howto": "Add this to your client's MCP configuration:",
    "conn.where": "Claude Code:  claude mcp add-json eksb '<the object above>'",
    "conn.restart": "Other clients: paste it into their MCP config file, then restart.",
    "conn.docs": "Full instructions: docs/integrations/mcp.md",
    "mcp.serving": "EKSB MCP server on {path} — speaking JSON-RPC on stdin/stdout.",
    "menu.settings": "Settings",
    "menu.learn": "Learn more",
    "menu.exit": "Exit",
    "menu.choose": "Choose a number",
    "menu.invalid": "That isn't one of the options.",
    "menu.back": "Back",
    "bye": "Bye.",

    # -- workspace ----------------------------------------------------
    "ws.current": "Workspace",
    "ws.none": "I couldn't find an EKSB workspace here.",
    "ws.none.hint": "Create one with:  eksb init <folder>",
    "ws.where": "Where should the workspace live?",
    "ws.name": "What should it be called?",
    "ws.created": "Workspace created at {path}",
    "ws.stored": "Your notes are plain Markdown files in that folder. Nothing else stores them.",
    "ws.exists": "There is already an EKSB workspace at {path}.",
    "ws.notempty": "{path} already has files in it. Pick an empty folder.",
    "ws.opened": "Now using the workspace at {path}",
    "ws.notfound": "There is no EKSB workspace at {path}.",
    "ws.path": "Path to the workspace",
    "ws.createhere": "There is no workspace at {path} yet. Create one there?",
    "ws.nowactive": "That is now your active workspace.",

    # -- demo ---------------------------------------------------------
    "demo.installing": "Setting up the demo workspace...",
    "demo.ready": "Demo ready at {path}",
    "demo.what": (
        "It holds one fictional engineering conversation and the knowledge\n"
        "pulled out of it: a position, a decision, a rejected alternative, a\n"
        "claim from outside, an unendorsed suggestion, and an open question."
    ),
    "demo.try": "Try:",
    "demo.label": "DEMO",
    "demo.readonly": ("This is the demo workspace. Create or open your own "
                      "workspace before adding real projects or knowledge."),
    "demo.readonly.hint": "eksb init {path}",
    "demo.offer": "Create your own workspace now?",

    # -- search -------------------------------------------------------
    "search.prompt": "Search for",
    "search.none": "Nothing matched \"{q}\".",
    "search.count": "{n} match(es) for \"{q}\":",
    "search.pick": "Enter a number to open one, or press Enter to go back",

    # -- adding -------------------------------------------------------
    "add.what": "What do you want to add?",
    "add.note": "Something I want to remember, in my own words",
    "add.source": "Keep a conversation or document I already have",
    "add.type": "What kind of thing is it?",
    "add.title": "Give it a short name",
    "add.created": "Created {path}",
    "add.edit": "Open that file in any editor and write. It is plain Markdown.",
    "type.concept": "An idea I will refer back to",
    "type.principle": "A rule I intend to act on",
    "type.question": "A question I want to keep open",
    "type.decision": "A decision, with what I turned down",
    "type.project": "A project with a state that changes",
    "save.path": "Path to the file",
    "save.kind": "Where did it come from?",
    "save.kind.chatgpt": "A ChatGPT conversation",
    "save.kind.claude": "A Claude conversation",
    "save.kind.web": "A web page",
    "save.kind.paper": "A paper or article",
    "save.kind.personal_note": "My own notes",
    "save.saved": "Kept as {path}",
    "save.kept": "Kept word for word, with a fingerprint — if it is ever edited, "
                 "`eksb validate` will say so.",
    "save.nofile": "There is no file at {path}.",
    "save.nottext": "{path} is not a text file. EKSB keeps text and Markdown.",

    # -- note / provenance --------------------------------------------
    "note.notfound": "I couldn't find \"{q}\" in this workspace.",
    "prov.title": "Where \"{title}\" came from",
    "prov.sources": "Came from",
    "prov.nosources": "No source recorded for this note.",
    "prov.missing": "Source recorded but not present in this workspace: {ids}",
    "prov.claims": "What it says, and who said it",
    "prov.out": "Points at",
    "prov.in": "Pointed at by",
    "prov.this": "this note",
    "prov.origin": "originally: {kind}, {date}",

    # -- attention ----------------------------------------------------
    "att.title": "Things that need your attention",
    "att.clean": "Nothing needs your attention right now.",
    "att.open": "Open questions",
    "att.unendorsed": "Suggested by an assistant, not confirmed by you",
    "att.unverified": "Claims from outside, not yet verified",
    "att.superseded": "Positions you changed",
    "att.review": "Marked for review",
    "att.queue": "Waiting in the review queue",
    "att.errors": "Problems in the files",
    "att.warnings": "Worth a look",

    # -- doctor -------------------------------------------------------
    "doc.title": "EKSB Doctor",
    "doc.python": "Python",
    "doc.eksb": "EKSB",
    "doc.workspace": "Workspace",
    "doc.schema": "Schema",
    "doc.items": "Knowledge items",
    "doc.relations": "Connections",
    "doc.broken": "Broken references",
    "doc.config": "Configuration",
    "doc.optional": "Optional, not required:",
    "doc.obsidian": "Obsidian",
    "doc.mcp": "AI assistants (MCP)",
    "doc.project": "Project",
    "doc.available": "client found, not configured",
    "doc.detected": "detected",
    "doc.notdetected": "not detected",
    "doc.ok": "OK",
    "doc.problem": "PROBLEM",
    "doc.none": "none set",
    "doc.ready": "EKSB is ready.",
    "doc.notready": "EKSB found problems. See above.",

    # -- about --------------------------------------------------------
    "about.title": "About this installation",
    "about.data": "Where your data is",
    "about.data.ws": "Your knowledge (Markdown files you can read and edit):",
    "about.data.cfg": "EKSB's own settings (language, last workspace):",
    "about.running": "What is running",
    "about.nodaemon": (
        "Nothing runs in the background. EKSB is a command you run; when it\n"
        "finishes, no EKSB process remains on your machine."
    ),
    "about.network": "Network",
    "about.nonetwork": (
        "EKSB makes no network connections. Nothing is uploaded, no AI model\n"
        "is called, and there is no telemetry."
    ),
    "about.integrations": "Optional integrations",
    "about.obsidian.on": "Obsidian is installed. EKSB does not use it or need it — your workspace is plain Markdown, so Obsidian can open it if you want.",
    "about.obsidian.off": "Obsidian is not installed. EKSB does not need it.",
    "about.agents": ("AI assistants (MCP): available, off until you configure a client. The server runs only while that client is running, started by it, over its own input and output — no port, no daemon."),
    "about.stop": "To remove EKSB: uninstall the package and delete the two folders above.",

    # -- settings -----------------------------------------------------
    "set.title": "Settings",
    "set.lang": "Language",
    "set.ws": "Default workspace",
    "set.file": "Settings file",
    "set.changelang": "Change language",
    "set.changews": "Change default workspace",

    # -- learn --------------------------------------------------------
    "learn.title": "Learn more",
    "learn.what": "What EKSB does",
    "learn.data": "How your data is stored",
    "learn.concepts": "The ideas behind it",
    "learn.docs": "Full documentation",
    "learn.docs.body": "The full documentation lives in the docs/ folder of the\nproject repository:\n\n  https://github.com/ViniciusOliveiraOV/EmergentKnowledgeSB",
    "learn.concepts.body": (
        "EKSB tracks, for every claim, who said it:\n\n"
        "  you said it            — your own position\n"
        "  an assistant said it   — a suggestion, never silently promoted\n"
        "  a source said it       — recorded, truth not assumed\n"
        "  it follows from        — reasoning over what is already there\n"
        "  still open             — an unresolved question\n\n"
        "The point is that a model's guess never quietly becomes something\n"
        "you believe you always thought. Only you can make that change.\n\n"
        "When you change your mind, the old position is kept and marked,\n"
        "not overwritten — so you can still see what you used to think."
    ),

    # -- errors -------------------------------------------------------
    "err.generic": "Something went wrong: {msg}",
    "err.debug": "Run again with --debug for technical details.",
    "err.interrupted": "Stopped.",
    "press.enter": "Press Enter to continue",
    "yes": "y",
    "no": "n",
    "yn": "[y/N]",
},

"pt-BR": {
    "product.name": "Emergent Knowledge Second Brain",
    "tagline": "Seu conhecimento deve sobreviver à conversa - e ao modelo.",
    "pitch": (
        "Seu histórico com IA deveria virar conhecimento reutilizável, não\n"
        "contexto descartável.\n\n"
        "O EKSB guarda suas decisões, fontes e a história dos seus projetos em\n"
        "Markdown comum, que pertence a você — não a uma conversa, um modelo\n"
        "ou um fornecedor. Assim um assistente de IA consulta só a parte de que\n"
        "precisa, em vez de você reexplicar o projeto toda vez."
    ),
    "first.journey": (
        "Testar a demonstração  ->  adicionar um projeto  ->  conectar um\n"
        "assistente de IA  ->  trabalhar normalmente. O EKSB vira a memória\n"
        "que o seu assistente consulta."
    ),
    "first.addproject": "Adicionar uma pasta de projeto agora?",
    "first.connect.hint": (
        "O EKSB rende mais quando um assistente de IA consegue lê-lo. Isso é\n"
        "opcional, não exige chave de API, e pode ficar para depois."
    ),
    "first.connect.now": "Quer ver como conectar um?",
    "arg.path": "<pasta>",

    "lang.choose": "Choose a language / Escolha um idioma:",
    "lang.saved": "Idioma definido: {lang}.",
    "first.title": "Bem-vindo ao EKSB.",
    "first.what": "O que você quer fazer?",
    "first.try": "Experimentar a demonstração",
    "first.create": "Criar meu workspace",
    "first.open": "Abrir um workspace existente",
    "first.learn": "Saiba mais",
    "ready": "Pronto. Seu EKSB está preparado.",
    "ready.next": "Três coisas para experimentar:",
    "arg.word": "<palavra>",

    "menu.title": "O que você quer fazer?",
    "menu.continue": "Como as coisas estão",
    "menu.continue.demo": "Explorar a demonstração",
    "menu.search": "Buscar no meu histórico",
    "menu.search.demo": "Buscar na demonstração",
    "menu.project": "Projetos",
    "menu.connect": "Conectar um assistente de IA",
    "menu.add": "Adicionar algo",
    "menu.attention": "O que precisa da minha atenção?",
    "menu.provenance": "Ver de onde veio uma informação",
    "menu.health": "Verificar meu workspace",
    "menu.about": "Sobre esta instalação",

    "stat.title": "Como as coisas estão",
    "stat.projects": "Projetos",
    "stat.items": "Conhecimento",
    "stat.ai": "Assistentes de IA",
    "stat.noai": "nenhum conectado — opcional, veja \"Conectar um assistente de IA\"",
    "stat.recent": "Mexido mais recentemente",
    "stat.pending": "Esperando por você ({n})",
    "stat.seeall": "\"O que precisa da minha atenção?\" tem a lista completa.",

    "proj.title": "Projetos",
    "proj.what": "Projetos",
    "proj.list": "Listar meus projetos",
    "proj.add": "Adicionar uma pasta de projeto",
    "proj.none": "Nenhum projeto ainda.",
    "proj.hint": "Adicione um com:  eksb ingest <pasta>",
    "proj.counts": "{indexed} arquivo(s) indexado(s) · {integrated} nota(s) escrita(s) a partir deles",
    "proj.levels": ("registrado = o EKSB sabe onde fica · indexado = o texto é "
                    "pesquisável · integrado = há conhecimento escrito a partir dele"),
    "level.registered": "registrado",
    "level.indexed": "indexado",
    "level.integrated": "integrado",
    "ing.path": "Caminho da pasta do projeto",
    "ing.name": "Como este projeto deve se chamar?",
    "ing.done": "Indexado: {project}",
    "ing.added": "indexado(s) agora",
    "ing.updated": "mudou desde a última vez (versões anteriores mantidas)",
    "ing.unchanged": "já estava em dia",
    "ing.skipped": "ignorado(s)",
    "ing.truncated": "Parei em {n} arquivos. Aumente com --max-files.",
    "ing.indexed_not_understood": (
        "Indexado, não compreendido. O texto agora é pesquisável e citável —\n"
        "transformá-lo em decisões e conceitos é o passo seguinte, e exige\n"
        "julgamento: o seu, ou o de um assistente conectado."
    ),
    "ing.next": "Experimente:  eksb search <palavra>   ·   eksb connect",
    "ing.nodir": "Não existe nenhuma pasta em {path}.",
    "ing.inside": "{path} está dentro do seu workspace. Aponte para o projeto em si.",
    "skip.ignored": "ignorados (build, cache, dependências)",
    "skip.not-text": "não são texto",
    "skip.too-big": "grandes demais",
    "skip.unreadable": "ilegíveis",
    "skip.over-limit": "acima do limite de arquivos",

    "conn.title": "Conectar um assistente de IA",
    "conn.what": (
        "O EKSB pode servir de memória para um assistente de IA que fale MCP.\n"
        "O assistente passa a consultar o seu histórico e a acrescentar a ele,\n"
        "em vez de você colar contexto em toda conversa.\n\n"
        "Nada roda até o assistente iniciar, e o próprio EKSB não precisa de\n"
        "chave de API."
    ),
    "conn.detected": "Clientes encontrados nesta máquina:",
    "conn.wired": "já configurado",
    "conn.notwired": "ainda não configurado",
    "conn.nodetect": "Nenhum cliente MCP detectado. A configuração abaixo serve para qualquer um.",
    "conn.howto": "Adicione isto à configuração MCP do seu cliente:",
    "conn.where": "Claude Code:  claude mcp add-json eksb '<o objeto acima>'",
    "conn.restart": "Outros clientes: cole no arquivo de configuração MCP e reinicie.",
    "conn.docs": "Instruções completas: docs/integrations/mcp.md",
    "mcp.serving": "Servidor MCP do EKSB em {path} — falando JSON-RPC pela entrada/saída padrão.",
    "menu.settings": "Configurações",
    "menu.learn": "Saiba mais",
    "menu.exit": "Sair",
    "menu.choose": "Escolha um número",
    "menu.invalid": "Essa não é uma das opções.",
    "menu.back": "Voltar",
    "bye": "Até logo.",

    "ws.current": "Workspace",
    "ws.none": "Não encontrei um workspace EKSB neste diretório.",
    "ws.none.hint": "Crie um com:  eksb init <pasta>",
    "ws.where": "Onde o workspace deve ficar?",
    "ws.name": "Como ele deve se chamar?",
    "ws.created": "Workspace criado em {path}",
    "ws.stored": "Suas notas são arquivos Markdown comuns nessa pasta. Nada mais as armazena.",
    "ws.exists": "Já existe um workspace EKSB em {path}.",
    "ws.notempty": "{path} já tem arquivos dentro. Escolha uma pasta vazia.",
    "ws.opened": "Usando agora o workspace em {path}",
    "ws.notfound": "Não existe um workspace EKSB em {path}.",
    "ws.path": "Caminho do workspace",
    "ws.createhere": "Ainda não existe um workspace em {path}. Criar um lá?",
    "ws.nowactive": "Este agora é o seu workspace ativo.",

    "demo.installing": "Preparando o workspace de demonstração...",
    "demo.ready": "Demonstração pronta em {path}",
    "demo.what": (
        "Ela contém uma conversa técnica fictícia e o conhecimento extraído\n"
        "dela: uma posição, uma decisão, uma alternativa rejeitada, uma\n"
        "afirmação externa, uma sugestão não endossada e uma pergunta aberta."
    ),
    "demo.try": "Experimente:",
    "demo.label": "DEMONSTRAÇÃO",
    "demo.readonly": ("Este é o workspace de demonstração. Crie ou abra seu "
                      "próprio workspace antes de adicionar projetos ou "
                      "conhecimento reais."),
    "demo.readonly.hint": "eksb init {path}",
    "demo.offer": "Quer criar seu próprio workspace agora?",

    "search.prompt": "Buscar por",
    "search.none": "Nada corresponde a \"{q}\".",
    "search.count": "{n} resultado(s) para \"{q}\":",
    "search.pick": "Digite um número para abrir, ou Enter para voltar",

    "add.what": "O que você quer adicionar?",
    "add.note": "Algo que eu quero lembrar, com minhas palavras",
    "add.source": "Guardar uma conversa ou documento que eu já tenho",
    "add.type": "Que tipo de coisa é?",
    "add.title": "Dê um nome curto",
    "add.created": "Criado em {path}",
    "add.edit": "Abra esse arquivo em qualquer editor e escreva. É Markdown comum.",
    "type.concept": "Uma ideia à qual eu vou voltar",
    "type.principle": "Uma regra que eu pretendo seguir",
    "type.question": "Uma pergunta que quero manter em aberto",
    "type.decision": "Uma decisão, com o que eu recusei",
    "type.project": "Um projeto com um estado que muda",
    "save.path": "Caminho do arquivo",
    "save.kind": "De onde veio?",
    "save.kind.chatgpt": "Uma conversa do ChatGPT",
    "save.kind.claude": "Uma conversa do Claude",
    "save.kind.web": "Uma página da web",
    "save.kind.paper": "Um artigo ou paper",
    "save.kind.personal_note": "Minhas próprias anotações",
    "save.saved": "Guardado como {path}",
    "save.kept": "Guardado palavra por palavra, com uma impressão digital — se for "
                 "editado algum dia, o `eksb validate` avisa.",
    "save.nofile": "Não existe nenhum arquivo em {path}.",
    "save.nottext": "{path} não é um arquivo de texto. O EKSB guarda texto e Markdown.",

    "note.notfound": "Não encontrei \"{q}\" neste workspace.",
    "prov.title": "De onde veio \"{title}\"",
    "prov.sources": "Veio de",
    "prov.nosources": "Nenhuma fonte registrada para esta nota.",
    "prov.missing": "Fonte registrada mas ausente deste workspace: {ids}",
    "prov.claims": "O que diz, e quem disse",
    "prov.out": "Aponta para",
    "prov.in": "Apontado por",
    "prov.this": "esta nota",
    "prov.origin": "originalmente: {kind}, {date}",

    "att.title": "Coisas que precisam da sua atenção",
    "att.clean": "Nada precisa da sua atenção agora.",
    "att.open": "Perguntas em aberto",
    "att.unendorsed": "Sugerido por um assistente, não confirmado por você",
    "att.unverified": "Afirmações externas ainda não verificadas",
    "att.superseded": "Posições que você mudou",
    "att.review": "Marcado para revisão",
    "att.queue": "Aguardando na fila de revisão",
    "att.errors": "Problemas nos arquivos",
    "att.warnings": "Vale uma olhada",

    "doc.title": "Diagnóstico do EKSB",
    "doc.python": "Python",
    "doc.eksb": "EKSB",
    "doc.workspace": "Workspace",
    "doc.schema": "Esquema",
    "doc.items": "Itens de conhecimento",
    "doc.relations": "Conexões",
    "doc.broken": "Referências quebradas",
    "doc.config": "Configuração",
    "doc.optional": "Opcional, não obrigatório:",
    "doc.obsidian": "Obsidian",
    "doc.mcp": "Assistentes de IA (MCP)",
    "doc.project": "Projeto",
    "doc.available": "cliente encontrado, não configurado",
    "doc.detected": "detectado",
    "doc.notdetected": "não detectado",
    "doc.ok": "OK",
    "doc.problem": "PROBLEMA",
    "doc.none": "não definido",
    "doc.ready": "O EKSB está pronto.",
    "doc.notready": "O EKSB encontrou problemas. Veja acima.",

    "about.title": "Sobre esta instalação",
    "about.data": "Onde ficam seus dados",
    "about.data.ws": "Seu conhecimento (arquivos Markdown que você pode ler e editar):",
    "about.data.cfg": "Configurações do próprio EKSB (idioma, último workspace):",
    "about.running": "O que está rodando",
    "about.nodaemon": (
        "Nada roda em segundo plano. O EKSB é um comando que você executa;\n"
        "quando ele termina, nenhum processo do EKSB fica na sua máquina."
    ),
    "about.network": "Rede",
    "about.nonetwork": (
        "O EKSB não faz nenhuma conexão de rede. Nada é enviado, nenhum\n"
        "modelo de IA é chamado, e não há telemetria."
    ),
    "about.integrations": "Integrações opcionais",
    "about.obsidian.on": "O Obsidian está instalado. O EKSB não o usa nem precisa dele — seu workspace é Markdown comum, então o Obsidian pode abri-lo se você quiser.",
    "about.obsidian.off": "O Obsidian não está instalado. O EKSB não precisa dele.",
    "about.agents": ("Assistentes de IA (MCP): disponível, desligado até você configurar um cliente. O servidor só roda enquanto esse cliente roda, iniciado por ele, pela entrada e saída dele — sem porta, sem daemon."),
    "about.stop": "Para remover o EKSB: desinstale o pacote e apague as duas pastas acima.",

    "set.title": "Configurações",
    "set.lang": "Idioma",
    "set.ws": "Workspace padrão",
    "set.file": "Arquivo de configuração",
    "set.changelang": "Mudar idioma",
    "set.changews": "Mudar o workspace padrão",

    "learn.title": "Saiba mais",
    "learn.what": "O que o EKSB faz",
    "learn.data": "Como seus dados são guardados",
    "learn.concepts": "As ideias por trás disso",
    "learn.docs": "Documentação completa",
    "learn.docs.body": "A documentação completa fica na pasta docs/ do\nrepositório do projeto:\n\n  https://github.com/ViniciusOliveiraOV/EmergentKnowledgeSB",
    "learn.concepts.body": (
        "O EKSB registra, para cada afirmação, quem a disse:\n\n"
        "  você disse             — sua própria posição\n"
        "  um assistente disse    — uma sugestão, nunca promovida em silêncio\n"
        "  uma fonte disse        — registrado, sem assumir que é verdade\n"
        "  decorre de             — raciocínio sobre o que já existe\n"
        "  ainda em aberto        — uma pergunta não resolvida\n\n"
        "O objetivo é que o palpite de um modelo nunca vire, sem você notar,\n"
        "algo que você acredita ter sempre pensado. Só você faz essa mudança.\n\n"
        "Quando você muda de ideia, a posição antiga é mantida e marcada, não\n"
        "sobrescrita — para você ainda enxergar o que pensava antes."
    ),

    "err.generic": "Algo deu errado: {msg}",
    "err.debug": "Rode de novo com --debug para ver os detalhes técnicos.",
    "err.interrupted": "Interrompido.",
    "press.enter": "Pressione Enter para continuar",
    "yes": "s",
    "no": "n",
    "yn": "[s/N]",
},
}

_lang = "en"


def set_lang(lang: str | None) -> str:
    global _lang
    _lang = lang if lang in STRINGS else "en"
    return _lang


def get_lang() -> str:
    return _lang


def t(key: str, **kw) -> str:
    s = STRINGS.get(_lang, {}).get(key) or STRINGS["en"].get(key) or key
    return s.format(**kw) if kw else s
