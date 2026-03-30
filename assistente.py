import os
import sys
import requests
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# Tenta pegar a chave do PC. Se não tiver, pede para o usuário digitar.
key_groq = os.environ.get("GROQ_API_KEY")
if not key_groq:
    console.print("[yellow]⚠️ Chave da Groq não encontrada no sistema.[/yellow]")
    key_groq = console.input("[bold cyan]Cole sua API Key da Groq aqui: [/bold cyan]").strip()

key_deepseek = os.environ.get("DEEPSEEK_API_KEY")
if not key_deepseek:
    console.print("[yellow]⚠️ Chave do DeepSeek não encontrada no sistema.[/yellow]")
    key_deepseek = console.input("[bold cyan]Cole sua API Key do DeepSeek aqui: [/bold cyan]").strip()

# Limpa sujeiras das chaves
key_groq = key_groq.replace('\n', '').replace('\r', '').replace(' ', '')
key_deepseek = key_deepseek.replace('\n', '').replace('\r', '').replace(' ', '')

# ==========================================
# 1. PAINEL DE CONFIGURAÇÃO & PERSONALIDADE
# ==========================================
PERSONALIDADE = """Você é um tutor sênior especialista em Análise e Desenvolvimento de Sistemas e Cibersegurança.
Forneça respostas diretas e códigos limpos."""

key_groq_bruta = os.environ.get("GROQ_API_KEY")
if not key_groq_bruta:
    console.print("[red]❌ Erro: Chave GROQ não encontrada.[/red]")
    sys.exit(1)
key_groq = key_groq_bruta.strip().replace('\n', '').replace('\r', '').replace(' ', '')

key_deepseek_bruta = os.environ.get("DEEPSEEK_API_KEY")
if not key_deepseek_bruta:
    console.print("[red]❌ Erro: Chave DEEPSEEK não encontrada.[/red]")
    sys.exit(1)
key_deepseek = key_deepseek_bruta.strip().replace('\n', '').replace('\r', '').replace(' ', '')

CONFIGS_IA = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "headers": {"Content-Type": "application/json", "Authorization": f"Bearer {key_groq}"},
        "color": "green"
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
        "headers": {"Content-Type": "application/json", "Authorization": f"Bearer {key_deepseek}"},
        "color": "cyan"
    }
}

ia_ativa = "groq"
conf_atual = CONFIGS_IA[ia_ativa]

# Interface de Abertura
boas_vindas = f"""[bold]Comandos Especiais:[/bold]
• [yellow]modelo groq[/yellow]    : Muda para Llama 3 (Groq)
• [yellow]modelo deepseek[/yellow]: Muda para DeepSeek
• [yellow]limpar[/yellow]         : Apaga o histórico
• [yellow]sair[/yellow]           : Encerra o programa"""

console.print(Panel(boas_vindas, title=f"🛡️ Assistente ADS/Cyber | IA: {ia_ativa.upper()}", border_style=conf_atual["color"]))

historico = [{"role": "system", "content": PERSONALIDADE}]

# ==========================================
# 2. LOOP DE INTERAÇÃO
# ==========================================
while True:
    try:
        usuario = console.input(f"\n[bold {conf_atual['color']}]({ia_ativa.upper()}) Você:[/bold {conf_atual['color']}] ").strip()

        comando = usuario.lower()
        if not comando: continue
        if comando in ['sair', 'exit', 'quit']:
            console.print("\n[bold red]Encerrando sistema. Até mais![/bold red]")
            break
        elif comando == 'limpar':
            historico = [{"role": "system", "content": PERSONALIDADE}]
            console.print("\n[italic gray][Sistema]: Histórico apagado.[/italic gray]")
            continue
        elif comando.startswith("modelo "):
            nova_ia = comando.split(" ")[1]
            if nova_ia in CONFIGS_IA:
                ia_ativa = nova_ia
                conf_atual = CONFIGS_IA[ia_ativa]
                console.print(f"\n[bold {conf_atual['color']}]🔄 [Sistema]: IA alterada para {ia_ativa.upper()}.[/bold {conf_atual['color']}]")
            else:
                console.print(f"\n[red]⚠️ Modelo '{nova_ia}' não reconhecido.[/red]")
            continue

        historico.append({"role": "user", "content": usuario})
        payload = {"model": conf_atual["model"], "messages": historico}

        # Mostra um status carregando enquanto a IA pensa
        with console.status(f"[bold {conf_atual['color']}]Processando na nuvem...", spinner="dots"):
            resposta = requests.post(conf_atual["url"], headers=conf_atual["headers"], json=payload, timeout=20)

        if resposta.status_code == 200:
            texto_ia = resposta.json()['choices'][0]['message']['content']
            # O Segredo do Design: Renderizar a resposta como Markdown dentro de um Painel
            console.print(Panel(Markdown(texto_ia), title=f"🤖 {ia_ativa.upper()}", border_style=conf_atual["color"]))
            historico.append({"role": "assistant", "content": texto_ia})
        else:
            erro_msg = resposta.json().get('error', {}).get('message', 'Erro desconhecido')
            console.print(f"\n[bold red]⚠️ Falha na API {ia_ativa.upper()} ({resposta.status_code}):[/bold red] {erro_msg}")
            historico.pop()

    except requests.exceptions.RequestException:
        console.print(f"\n[bold red]🔌 Erro de Conexão na IA {ia_ativa.upper()}. Verifique a internet.[/bold red]")
        historico.pop()
        time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Saindo...[/bold red]")
        break
