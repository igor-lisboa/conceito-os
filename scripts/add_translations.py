"""Add missing Portuguese entries to the catalog, and report strings still without one.

Usage: python scripts/add_translations.py
Only entries whose msgid is not already in django.po are added, so existing
translations are never overwritten. Run scripts/compile_translations.py afterwards.
"""

import re
import sys
from pathlib import Path

import polib

ROOT = Path(__file__).resolve().parent.parent
PO = ROOT / "locale" / "pt_BR" / "LC_MESSAGES" / "django.po"

NEW = {
    # Navigation
    "Reports": "Relatórios",
    "Sales": "Vendas",
    "Team": "Equipe",
    "Settings": "Configurações",
    "Audit log": "Log de auditoria",
    # Team and invitations
    "Role": "Papel",
    "All clients": "Todos os clientes",
    "None": "Nenhum",
    "Remove access": "Remover acesso",
    "Invite person": "Convidar pessoa",
    "Invitation sent.": "Convite enviado.",
    "Access removed.": "Acesso removido.",
    "Send invitation": "Enviar convite",
    "We will email a link so they can create their own password.": "Enviaremos um link para a pessoa criar a própria senha.",
    "Clients this person can see": "Clientes que esta pessoa pode ver",
    "Owners see every client, so this is only needed for other roles.": "Proprietárias veem todos os clientes; esta lista só é necessária para os demais papéis.",
    "This person is already a member of this organization.": "Esta pessoa já é membro desta organização.",
    "You cannot remove your own access.": "Você não pode remover o próprio acesso.",
    "The last owner of the organization cannot be removed.": "A última proprietária da organização não pode ser removida.",
    "This membership belongs to another organization.": "Este vínculo pertence a outra organização.",
    "You were invited to join a team on Conceito OS.": "Você foi convidado para fazer parte de uma equipe no Conceito OS.",
    "You were invited to %(org)s on Conceito OS": "Você foi convidado para %(org)s no Conceito OS",
    "Organization: %(org)s": "Organização: %(org)s",
    "Create your password with this link. It works once and expires in 24 hours:": "Crie sua senha com este link. Ele funciona uma vez e expira em 24 horas:",
    "Then sign in with your email address on the sign-in page.": "Depois, entre com seu e-mail na página de login.",
    "If you did not expect this invitation, you can ignore this email.": "Se você não esperava este convite, pode ignorar este e-mail.",
    "Too many failed attempts. Try again in 15 minutes.": "Muitas tentativas sem sucesso. Tente de novo em 15 minutos.",
    # Organization settings
    "Organization settings": "Configurações da organização",
    "Organization name": "Nome da organização",
    "Time zone": "Fuso horário",
    "Settings saved.": "Configurações salvas.",
    "Dates on screen follow this time zone. Times are stored in UTC.": "As datas na tela seguem este fuso horário. Os horários são guardados em UTC.",
    "Save": "Salvar",
    # Audit log
    "Action starts with": "Ação começa com",
    "When": "Quando",
    "Who": "Quem",
    "Action": "Ação",
    "Item": "Item",
    "Next page": "Próxima página",
    "No events match this filter.": "Nenhum evento corresponde a este filtro.",
    # Published link
    "Link to the published post": "Link da publicação",
    "Published post": "Publicação",
    # Library
    "Library": "Biblioteca",
    "Add link": "Adicionar link",
    "Add to library": "Adicionar à biblioteca",
    "No links in the library yet.": "Nenhum link na biblioteca ainda.",
    "Paste the link to the file (Drive, Dropbox or similar). The file itself stays there.": "Cole o link do arquivo (Drive, Dropbox ou similar). O arquivo continua no mesmo lugar.",
    "Save link": "Salvar link",
    "Link added to the library.": "Link adicionado à biblioteca.",
    "Kind": "Tipo",
    "Link": "Link",
    "Logo": "Logo",
    "Font": "Fonte",
    "Template": "Modelo",
    "Reference": "Referência",
    "Other": "Outro",
    # CRM
    "Leads": "Leads",
    "Proposals": "Propostas",
    "New lead": "Novo lead",
    "New proposal": "Nova proposta",
    "Lead saved.": "Lead salvo.",
    "Proposal saved.": "Proposta salva.",
    "Stage updated.": "Etapa atualizada.",
    "Status updated.": "Status atualizado.",
    "Unknown stage.": "Etapa desconhecida.",
    "Unknown status.": "Status desconhecido.",
    "Source": "Origem",
    "Contact": "Contato",
    "Next action": "Próxima ação",
    "Next action date": "Data da próxima ação",
    "Notes": "Observações",
    "Name": "Nome",
    "Status": "Status",
    "Lead": "Lead",
    "Amount (BRL)": "Valor (BRL)",
    "Save lead": "Salvar lead",
    "Save proposal": "Salvar proposta",
    "No leads here.": "Nenhum lead aqui.",
    "No proposals yet.": "Nenhuma proposta ainda.",
    "Move": "Mover",
    "Update": "Atualizar",
    "Referral": "Indicação",
    "Website": "Site",
    "Contacted": "Contatado",
    "Meeting": "Reunião",
    "Won": "Ganho",
    "Lost": "Perdido",
    "New": "Novo",
    "Draft": "Rascunho",
    "Sent": "Enviada",
    "Accepted": "Aceita",
    "Rejected": "Recusada",
    # Reports and metrics
    "Monthly report": "Relatório mensal",
    "Network": "Rede",
    "Metric": "Métrica",
    "Value": "Valor",
    "Month": "Mês",
    "Show": "Mostrar",
    "Enter a value": "Informar um valor",
    "Back to report": "Voltar ao relatório",
    "Save value": "Salvar valor",
    "Value saved.": "Valor salvo.",
    "Value updated.": "Valor atualizado.",
    "N/D": "N/D",
    "N/D means no value was entered for this month. No number is estimated.": "N/D significa que nenhum valor foi informado para este mês. Nenhum número é estimado.",
    "Use the format YYYY-MM, for example 2026-10.": "Use o formato AAAA-MM, por exemplo 2026-10.",
    "Format: YYYY-MM": "Formato: AAAA-MM",
    "Reach": "Alcance",
    "Interactions": "Interações",
    "Saves": "Salvamentos",
    "Followers": "Seguidores",
    "Views": "Visualizações",
    "Type the number as it appears in the network's insights. Entering the same month again updates the value.": "Digite o número como aparece nas métricas da rede. Informar o mesmo mês de novo atualiza o valor.",
}


NEW_PHASE1_FINAL = {
    "Install an authenticator app on your phone (Google Authenticator, Microsoft Authenticator or similar).": "Instale um aplicativo autenticador no seu celular (Google Authenticator, Microsoft Authenticator ou similar).",
    "Add an account with this key, or open the link below on the phone:": "Adicione uma conta com esta chave, ou abra o link abaixo no celular:",
    "Type the 6-digit code the app shows now:": "Digite o cÃ³digo de 6 dÃ­gitos que o aplicativo mostra agora:",
    "Add comment": "Adicionar comentÃ¡rio",
    "Agenda": "Agenda",
    "Alerts": "Avisos",
    "Board": "Quadro",
    "Calendar": "CalendÃ¡rio",
    "Comments": "ComentÃ¡rios",
    "Confirm": "Confirmar",
    "Copy": "CÃ³pia",
    "copy": "cÃ³pia",
    "Due": "Vence",
    "Duplicate as a new draft": "Duplicar como novo rascunho",
    "Empty": "Vazio",
    "Enter your code": "Digite seu cÃ³digo",
    "Files": "Arquivos",
    "For questions about your content, write to": "Para dÃºvidas sobre o seu conteÃºdo, escreva para",
    "Main": "Principal",
    "Mark as done": "Marcar como concluÃ­da",
    "Months": "Meses",
    "Move a piece with its buttons on the piece page. Each change is recorded.": "Mova uma peÃ§a pelos botÃµes da prÃ³pria pÃ¡gina da peÃ§a. Cada mudanÃ§a fica registrada.",
    "New task": "Nova tarefa",
    "Next": "PrÃ³ximo",
    "No brands available for you yet.": "Nenhuma marca disponÃ­vel para vocÃª ainda.",
    "No comments yet.": "Nenhum comentÃ¡rio ainda.",
    "No files shared with you yet.": "Nenhum arquivo compartilhado com vocÃª ainda.",
    "No tasks yet.": "Nenhuma tarefa ainda.",
    "Nothing scheduled this month.": "Nada agendado neste mÃªs.",
    "Nothing scheduled yet.": "Nada agendado ainda.",
    "Open in my authenticator app": "Abrir no meu aplicativo autenticador",
    "Previous": "Anterior",
    "Production board": "Quadro de produÃ§Ã£o",
    "Reopen": "Reabrir",
    "Results": "Resultados",
    "Save task": "Salvar tarefa",
    "Scheduled content, month view": "ConteÃºdo agendado, visÃ£o do mÃªs",
    "Security": "SeguranÃ§a",
    "Send comment": "Enviar comentÃ¡rio",
    "Show everyone's tasks": "Mostrar as tarefas de todos",
    "Show my tasks": "Mostrar minhas tarefas",
    "Skip to content": "Pular para o conteÃºdo",
    "Tasks": "Tarefas",
    "Turn on": "Ativar",
    "Two-step sign-in": "VerificaÃ§Ã£o em duas etapas",
    "Two-step sign-in is on. You will be asked for a code from your app after your password.": "A verificaÃ§Ã£o em duas etapas estÃ¡ ativa. Depois da senha, vocÃª vai precisar de um cÃ³digo do seu aplicativo.",
    "Write a comment (mention someone with @email)": "Escreva um comentÃ¡rio (mencione alguÃ©m com @e-mail)",
    "Write a comment for the team": "Escreva um comentÃ¡rio para a equipe",
    "Task": "Tarefa",
    "Due date": "Data limite",
    "Code from your app": "CÃ³digo do seu aplicativo",
    "Mon": "Seg", "Tue": "Ter", "Wed": "Qua", "Thu": "Qui", "Fri": "Sex", "Sat": "SÃ¡b", "Sun": "Dom",
    "Write a comment of up to 2000 characters.": "Escreva um comentÃ¡rio de atÃ© 2000 caracteres.",
    "Comment added.": "ComentÃ¡rio adicionado.",
    "Comment sent.": "ComentÃ¡rio enviado.",
    "Copy created as a draft.": "CÃ³pia criada como rascunho.",
    "Task added.": "Tarefa adicionada.",
    "Two-step sign-in is on for your account.": "A verificaÃ§Ã£o em duas etapas estÃ¡ ativa na sua conta.",
    "That code is not right. Check the time on your phone and try again.": "Este cÃ³digo nÃ£o estÃ¡ certo. Confira a hora do seu celular e tente de novo.",
    "That code is not right.": "Este cÃ³digo nÃ£o estÃ¡ certo.",
}
NEW.update(NEW_PHASE1_FINAL)
NEW.update({
    "1. Install an authenticator app on your phone (Google Authenticator, Microsoft Authenticator or similar).": "1. Instale um aplicativo autenticador no seu celular (Google Authenticator, Microsoft Authenticator ou similar).",
    "2. Add an account with this key, or open the link below on the phone:": "2. Adicione uma conta com esta chave, ou abra o link abaixo no celular:",
    "3. Type the 6-digit code the app shows now:": "3. Digite o código de 6 dígitos que o aplicativo mostra agora:",
})


def existing_msgids(catalog):
    return {entry.msgid for entry in catalog}


def add_missing(catalog):
    have = existing_msgids(catalog)
    added = 0
    for msgid, msgstr in NEW.items():
        if msgid not in have:
            catalog.append(polib.POEntry(msgid=msgid, msgstr=msgstr))
            added += 1
    return added


def strings_in_templates():
    found = set()
    for path in (ROOT / "templates").rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        found.update(re.findall(r'\{%\s*trans\s+"([^"]+)"', text))
        found.update(re.findall(r"\{%\s*trans\s+'([^']+)'", text))
    return found


def main():
    catalog = polib.pofile(str(PO))
    added = add_missing(catalog)
    if added:
        # Save only when something changed, so the .mo file is not left older than the .po.
        catalog.save(str(PO))
    print(f"added {added} entries")

    have = existing_msgids(catalog)
    missing = sorted(s for s in strings_in_templates() if s not in have)
    if missing:
        print("template strings without a catalog entry:")
        for msgid in missing:
            print("  ", msgid)
        return 1
    print("every template string has a catalog entry")
    return 0


if __name__ == "__main__":
    sys.exit(main())
