import json
import re

# Reconnaît les flèches Mermaid : -->, --->, -.->,  ==>, etc.
# On capture tout ce qui n'est pas un caractère de flèche entre deux noms.
ARROW_PATTERN = re.compile(r"-{1,}>|={1,}>|-\.->")

# Corrige les variantes de flèches qu'un clavier/OS peut introduire par
# autocorrection : espace parasite ("-- >"), ou flèche unicode collée
# (→, ⟶, ⇒, ➔, ➜) à la place de "-->". Tout est ramené à "-->".
_ARROW_NORMALIZE_PATTERN = re.compile(
    r"\s*-{1,}\s*>\s*"  # "-->", "- >", "--  >", etc. (avec espaces parasites)
    r"|\s*[\u2192\u27f6\u21d2\u2794\u279c\u2b95]\s*"  # flèches unicode isolées
)


def normalize_arrows(raw_content: str) -> str:
    """Ramène toutes les variantes de flèches détectées vers la syntaxe
    Mermaid standard '-->', avec un espace de chaque côté. Convertit
    aussi les "\\n" tapés/collés littéralement (backslash + n, PAS un
    vrai retour à la ligne) en un vrai saut de ligne — un copier-coller
    depuis un exemple de code produit souvent ce genre d'artefact."""
    raw_content = raw_content.replace("\\n", "\n")
    return _ARROW_NORMALIZE_PATTERN.sub(" --> ", raw_content).strip()


def _split_line_into_nodes(line: str) -> list[str]:
    """Découpe une ligne comme 'User --> Order --> PaymentService'
    en ['User', 'Order', 'PaymentService']."""
    parts = ARROW_PATTERN.split(line)
    return [p.strip() for p in parts if p.strip()]


def parse_mermaid(raw_content: str) -> dict:
    """
    Parse un texte Mermaid simple (chaînes de type A --> B --> C,
    une ou plusieurs par ligne) et renvoie une structure :
        {"components": [...], "relations": [{"source":..., "target":...}]}

    Les lignes qui ne contiennent pas de flèche reconnue (ex: 'graph TD',
    des commentaires '%% ...', ou des lignes vides) sont ignorées.
    """
    components: list[str] = []
    relations: list[dict] = []

    def add_component(name: str) -> None:
        if name not in components:
            components.append(name)

    for raw_line in raw_content.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("%%"):
            continue
        if line.lower().startswith(("graph ", "flowchart ", "classdiagram", "sequencediagram")):
            continue

        if not ARROW_PATTERN.search(line):
            continue

        nodes = _split_line_into_nodes(line)

        for node in nodes:
            add_component(node)

        for source, target in zip(nodes, nodes[1:]):
            relations.append({"source": source, "target": target})

    return {"components": components, "relations": relations}


def parse_mermaid_to_json_string(raw_content: str) -> str:
    """Comme parse_mermaid, mais renvoie directement une chaîne JSON
    prête à être stockée dans Diagram.parsed_structure (colonne Text)."""
    return json.dumps(parse_mermaid(raw_content), ensure_ascii=False)
