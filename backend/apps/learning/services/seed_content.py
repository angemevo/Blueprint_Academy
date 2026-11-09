"""Contenu PROPOSE du premier module : « Prise en main de l'editeur ».

PROPOSITION A VALIDER PAR ANGE : tout est non publie. Rien n'est affirme
comme exact dans Unreal sans etre marque « A VERIFIER DANS UNREAL » ; chaque
exercice doit etre rejoue dans un vrai projet UE5 avant publication.

Donnees pures (aucune logique) : `seed.py` les ecrit en base.
"""

BEGIN = "K2Node_Event:ReceiveBeginPlay"
PRINT = "K2Node_CallFunction:PrintString"
DELAY = "K2Node_CallFunction:Delay"

MODULE_SLUG = "prise-en-main-editeur"
TODO = "A VERIFIER DANS UNREAL"


def _n(id_, type_, x, y):
    return {"id": id_, "type": type_, "position": {"x": x, "y": y}}


def _e(a, b, from_pin="then", to_pin="execute"):
    return {"from": a, "to": b, "from_pin": from_pin, "to_pin": to_pin}


def _sel(type_):
    return {"type": type_}


def _wire(a, b):
    return {"from": _sel(a), "to": _sel(b), "from_pin": "then", "to_pin": "execute"}


_PALETTE = [{"type": BEGIN}, {"type": PRINT}, {"type": DELAY}]


def _callout(variant, title, text):
    return {"type": "callout", "variant": variant, "title": title, "text": text}


LESSONS = [
    {
        "slug": "lire-un-blueprint",
        "title": "Lire un Blueprint : evenements, nodes et fils",
        "summary": "Un evenement declenche une chaine de nodes reliee par des fils d'execution.",
        "estimated_minutes": 8,
        "skills": ["editor-basics"],
        "content": {
            "version": 1,
            "blocks": [
                {"type": "heading", "text": "Un graphe se lit de gauche a droite", "level": 2},
                _callout(
                    "info",
                    "C'est quoi ?",
                    "Un Blueprint est un graphe de nodes. Un node est une action ou un "
                    "evenement ; les fils blancs d'execution disent dans quel ordre ils "
                    "s'executent.",
                ),
                _callout(
                    "why",
                    "Pourquoi ?",
                    "Parce que le jeu doit reagir a quelque chose (le debut de la partie, "
                    "un contact) : l'evenement est le point de depart de toute chaine.",
                ),
                _callout(
                    "when",
                    "Quand ?",
                    "Event BeginPlay s'execute au demarrage de l'Actor dans le niveau : "
                    "c'est le bon endroit pour une initialisation.",
                ),
                {
                    "type": "list",
                    "style": "numbered",
                    "items": [
                        "Reperer l'evenement (rouge dans l'editeur : " + TODO + ").",
                        "Suivre le fil d'execution vers la droite.",
                        "Lire chaque node dans l'ordre ou le fil le traverse.",
                    ],
                },
                {
                    "type": "graph",
                    "graph": {
                        "nodes": [_n("b", BEGIN, 0, 0), _n("p", PRINT, 300, 0)],
                        "edges": [_e("b", "p")],
                    },
                    "caption": "Event BeginPlay puis Print String. Noms de pins : " + TODO + ".",
                },
                _callout(
                    "pitfall",
                    "Erreur du debutant",
                    "Poser un node sans le relier : il n'est jamais execute. Un node non "
                    "relie par un fil d'execution ne fait rien.",
                ),
                _callout(
                    "real_game",
                    "Dans un vrai jeu",
                    "Un Actor de checkpoint utilise un evenement pour reagir quand le "
                    "joueur arrive, puis enchaine ses actions.",
                ),
                {
                    "type": "self_check",
                    "question": "Que se passe-t-il si Print String n'est pas relie a l'evenement ?",
                    "answer": "Rien : il n'est jamais execute.",
                },
            ],
        },
    },
    {
        "slug": "compiler-et-lire-les-erreurs",
        "title": "Compiler et lire les erreurs",
        "summary": "Compiler verifie le Blueprint ; l'ordre des fils decide de ce qui se passe.",
        "estimated_minutes": 8,
        "skills": ["compile-and-debug"],
        "content": {
            "version": 1,
            "blocks": [
                {"type": "heading", "text": "Compiler, puis deboguer", "level": 2},
                _callout(
                    "info",
                    "C'est quoi ?",
                    "Compiler transforme le graphe en quelque chose que le jeu peut "
                    "executer et signale les erreurs. Le bouton Compile est dans la barre "
                    "d'outils de l'editeur (" + TODO + ").",
                ),
                _callout(
                    "why",
                    "Pourquoi ?",
                    "Un Blueprint non compile garde l'ancien comportement : on compile a "
                    "chaque modification pour tester la nouvelle version.",
                ),
                _callout(
                    "when",
                    "Quand ?",
                    "Apres chaque changement du graphe, avant de lancer le jeu.",
                ),
                {
                    "type": "list",
                    "style": "bullet",
                    "items": [
                        "Une erreur (rouge) empeche de compiler ; lire son message en premier.",
                        "Un symptome sans erreur (message qui n'apparait pas, qui arrive en "
                        "retard) vient souvent d'un fil manquant ou d'un Delay en trop.",
                        "Delay retarde la suite de la chaine : " + TODO + " (comportement exact).",
                    ],
                },
                _callout(
                    "pitfall",
                    "Erreur du debutant",
                    "Tester sans compiler, puis chercher un bug dans un graphe qui n'a "
                    "jamais ete pris en compte.",
                ),
                _callout(
                    "real_game",
                    "Dans un vrai jeu",
                    "Une porte qui s'ouvre avec 5 secondes de retard : le symptome mene a un "
                    "Delay oublie dans la chaine.",
                ),
                {
                    "type": "self_check",
                    "question": "Un message devrait s'afficher au demarrage mais n'apparait pas. Premier reflexe ?",
                    "answer": "Verifier que le fil d'execution relie bien l'evenement au Print String, puis compiler.",
                },
            ],
        },
    },
]


def _ex(slug, lesson, type_, title, skill, content, solution, hints, order):
    return {
        "slug": slug,
        "lesson": lesson,
        "type": type_,
        "title": title,
        "skills": [skill],
        "content": content,
        "solution": solution,
        "hints": hints,
        "order": order,
    }


_L1, _L2 = "lire-un-blueprint", "compiler-et-lire-les-erreurs"

EXERCISES = [
    # --- Skill editor-basics -------------------------------------------------
    _ex(
        "relier-beginplay-print", _L1, "H", "Relier BeginPlay a Print String", "editor-basics",
        {
            "prompt": "Ajoute un Print String et relie-le a Event BeginPlay.",
            "palette": _PALETTE,
            "partial_graph": {"nodes": [_n("b", BEGIN, 0, 0)], "edges": []},
            "locked_node_ids": ["b"],
        },
        {
            "required_nodes": [{"type": PRINT, "feedback": "Il manque un Print String."}],
            "required_edges": [{**_wire(BEGIN, PRINT), "feedback": "Relie le fil d'execution de BeginPlay a Print String."}],
            "explanation": "Le fil blanc part de BeginPlay et entre dans Print String.",
        },
        ["Cherche un node dans la palette.", "Tire un fil depuis la sortie d'execution de l'evenement."],
        1,
    ),
    _ex(
        "completer-delay-print", _L1, "H", "Afficher un message apres un delai", "editor-basics",
        {
            "prompt": "Le message doit s'afficher apres le Delay. Ajoute-le.",
            "palette": _PALETTE,
            "partial_graph": {
                "nodes": [_n("b", BEGIN, 0, 0), _n("d", DELAY, 300, 0)],
                "edges": [_e("b", "d")],
            },
            "locked_node_ids": ["b", "d"],
        },
        {
            "required_nodes": [{"type": PRINT}],
            "required_edges": [{**_wire(DELAY, PRINT), "feedback": "Print String doit suivre le Delay."}],
        },
        ["Le Print String vient apres le Delay, pas avant."],
        2,
    ),
    _ex(
        "construire-delay-print", _L1, "E", "Construire une chaine complete", "editor-basics",
        {
            "prompt": "Construis : BeginPlay, puis Delay, puis Print String.",
            "palette": _PALETTE,
        },
        {
            "required_nodes": [_sel(BEGIN), _sel(DELAY), _sel(PRINT)],
            "required_edges": [_wire(BEGIN, DELAY), _wire(DELAY, PRINT)],
        },
        ["Place d'abord les trois nodes, puis relie-les dans l'ordre."],
        3,
    ),
    # --- Skill compile-and-debug ---------------------------------------------
    _ex(
        "message-jamais-affiche", _L2, "F", "Le message n'apparait jamais", "compile-and-debug",
        {
            "prompt": "Au demarrage, rien ne s'affiche. Corrige le graphe.",
            "symptom": "Le jeu demarre, aucun message n'apparait.",
            "palette": _PALETTE,
            "broken_graph": {
                "nodes": [_n("b", BEGIN, 0, 0), _n("p", PRINT, 300, 0)],
                "edges": [],
            },
            "locked_node_ids": ["b"],
        },
        {
            "required_edges": [{**_wire(BEGIN, PRINT), "feedback": "Le Print String n'est relie a rien."}],
        },
        ["Regarde les fils d'execution : le Print String est-il relie ?"],
        1,
    ),
    _ex(
        "delay-en-trop", _L2, "F", "Le message arrive en retard", "compile-and-debug",
        {
            "prompt": "Le message doit s'afficher tout de suite. Corrige le graphe.",
            "symptom": "Le message apparait plusieurs secondes apres le demarrage.",
            "palette": _PALETTE,
            "broken_graph": {
                "nodes": [_n("b", BEGIN, 0, 0), _n("d", DELAY, 300, 0), _n("p", PRINT, 600, 0)],
                "edges": [_e("b", "d"), _e("d", "p")],
            },
            "locked_node_ids": ["b"],
        },
        {
            "required_edges": [_wire(BEGIN, PRINT)],
            "forbidden_nodes": [{**_sel(DELAY), "feedback": "Un Delay retarde le message."}],
        },
        ["Quel node introduit l'attente ?"],
        2,
    ),
    _ex(
        "deux-messages", _L2, "G", "Deux messages dans l'ordre", "compile-and-debug",
        {
            "prompt": "Affiche deux messages : un tout de suite, un autre apres un Delay.",
            "palette": _PALETTE,
            "success_criteria": ["Deux Print String", "Un Delay entre les deux"],
        },
        {
            "required_nodes": [{**_sel(PRINT), "min_count": 2}, _sel(DELAY), _sel(BEGIN)],
            "required_edges": [_wire(BEGIN, PRINT), _wire(PRINT, DELAY), _wire(DELAY, PRINT)],
        },
        ["BeginPlay, Print String, Delay, Print String : une seule chaine."],
        3,
    ),
]
