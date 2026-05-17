import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur de sync : {e}")


# ------------------------------------------------------------
# SAFE EDIT (Option A)
# ------------------------------------------------------------

async def safe_edit(interaction: discord.Interaction, **kwargs):
    try:
        return await interaction.response.edit_message(**kwargs)
    except discord.InteractionResponded:
        return await interaction.edit_original_response(**kwargs)


# ------------------------------------------------------------
# DONNÉES CLANS
# ------------------------------------------------------------

CLAN_DATA = {
    "ventrue": {
        "nom": "Ventrue — Le Sang des Rois",
        "desc": "Les Ventrue sont les seigneurs naturels de la société vampirique.",
        "disciplines": "Dominate, Présence, Robustesse",
        "faiblesse": "Ne peuvent boire qu’un type de sang spécifique.",
        "style": "Politique, noblesse, autorité."
    },
    "toreador": {
        "nom": "Toreador — Les Enfants de la Rose",
        "desc": "Artistes passionnés, sensibles à la beauté.",
        "disciplines": "Célérité, Présence, Auspex",
        "faiblesse": "Fascination paralysante pour la beauté.",
        "style": "Art, séduction, drame."
    },
    "brujah": {
        "nom": "Brujah — Les Rebelles",
        "desc": "Philosophes guerriers animés par la colère.",
        "disciplines": "Puissance, Célérité, Présence",
        "faiblesse": "Frénésie fréquente.",
        "style": "Révolte, passion, combat."
    },
    "malkavian": {
        "nom": "Malkavian — Les Fous Sages",
        "desc": "Visionnaires brisés, prophètes de la folie.",
        "disciplines": "Démence, Auspex, Obfuscation",
        "faiblesse": "Folie irréversible.",
        "style": "Mystère, prophétie, chaos."
    },
    "nosferatu": {
        "nom": "Nosferatu — Les Rats des Ténèbres",
        "desc": "Espions difformes, maîtres des secrets.",
        "disciplines": "Obfuscation, Puissance, Animalisme",
        "faiblesse": "Hideur absolu.",
        "style": "Infiltration, survie, information."
    },
    "tzimisce": {
        "nom": "Tzimisce — Les Seigneurs de la Chair",
        "desc": "Sculpteurs de chair, aristocrates monstrueux.",
        "disciplines": "Vicissitude, Auspex, Dominate",
        "faiblesse": "Dépendance à la terre natale.",
        "style": "Horreur, domination, expérimentation."
    },
    "tremere": {
        "nom": "Tremere — Les Usurpateurs",
        "desc": "Sorcier-sang, érudits impitoyables.",
        "disciplines": "Thaumaturgie, Auspex, Dominate",
        "faiblesse": "Lien de sang pyramidal.",
        "style": "Magie, complots, occultisme."
    },
    "assamite": {
        "nom": "Assamite — Les Juges du Sang",
        "desc": "Assassins mystiques obsédés par la pureté.",
        "disciplines": "Célérité, Obfuscation, Quietus",
        "faiblesse": "Addiction au sang vampirique.",
        "style": "Assassinat, religion, honneur."
    },
    "giovanni": {
        "nom": "Giovanni — Les Nécromanciens",
        "desc": "Banquiers de la mort, maîtres des esprits.",
        "disciplines": "Nécromancie, Puissance, Dominate",
        "faiblesse": "Baiser douloureux.",
        "style": "Famille, mort, commerce."
    },
    "lasombra": {
        "nom": "Lasombra — Les Ombres du Pouvoir",
        "desc": "Théologiens du pouvoir, maîtres des ténèbres.",
        "disciplines": "Obtenebration, Dominate, Puissance",
        "faiblesse": "Pas de reflet.",
        "style": "Ténèbres, autorité, religion."
    },
    "ravnos": {
        "nom": "Ravnos — Les Vagabonds du Mensonge",
        "desc": "Illusionnistes nomades, tricheurs nés.",
        "disciplines": "Chimérie, Animalisme, Fortitude",
        "faiblesse": "Compulsion au vice.",
        "style": "Chaos, illusions, voyage."
    },
    "gangrel": {
        "nom": "Gangrel — Les Bêtes Sauvages",
        "desc": "Nomades proches de la nature.",
        "disciplines": "Animalisme, Fortitude, Protéisme",
        "faiblesse": "Traits bestiaux après frénésie.",
        "style": "Survie, nature, instinct."
    },
}

CLANS = list(CLAN_DATA.keys())

QUESTIONS = [
    "1. Vous préférez jouer un personnage qui\nA) dirige\nB) charme\nC) se bat\nD) observe",
    "2. Votre priorité narrative est…\nA) le pouvoir\nB) l’art\nC) la révolte\nD) la folie",
    "3. Vous aimez les mécaniques centrées sur…\nA) le contrôle\nB) la séduction\nC) la force\nD) l’esprit",
    "4. En campagne, vous préférez…\nA) gérer\nB) organiser\nC) combattre\nD) prophétiser",
    "5. Votre faiblesse acceptable…\nA) autorité\nB) beauté\nC) passion\nD) mystère",
    "6. Vos thèmes favoris…\nA) hiérarchie\nB) art\nC) liberté\nD) destin",
    "7. Intrigues préférées…\nA) politique\nB) scandales\nC) duels\nD) énigmes",
    "8. Combat…\nA) stratégique\nB) théâtral\nC) frontal\nD) imprévisible",
    "9. Vous aimez posséder…\nA) influence\nB) réputation\nC) force\nD) savoir occulte",
    "10. Pouvoirs préférés…\nA) contrôle\nB) émotions\nC) puissance\nD) altération",
    "11. Habitat idéal…\nA) manoir\nB) salon d’art\nC) route\nD) frontière du réel",
    "12. Antagoniste préféré…\nA) politicien\nB) rival social\nC) guerrier\nD) manipulateur",
    "13. Votre plaisir de jeu…\nA) négociation\nB) esthétique\nC) combat\nD) mystère"
]

MAPPING = {
    "A": ["ventrue", "lasombra", "tremere"],
    "B": ["toreador", "malkavian", "ravnos"],
    "C": ["brujah", "gangrel", "assamite"],
    "D": ["nosferatu", "tzimisce", "giovanni", "tremere"]
}

# ------------------------------------------------------------
# NATURE / ATTITUDE
# ------------------------------------------------------------

NATURE_DATA = {
    "architecte": "Bâtisseur, organisateur, visionnaire.",
    "penseur": "Analytique, calme, logique.",
    "visionnaire": "Idéaliste, prophétique.",
    "bonvivant": "Épicurien, joyeux.",
    "enfant": "Spontané, naïf.",
    "defenseur": "Protecteur, loyal.",
    "meneur": "Charismatique, inspirant.",
    "bourreau": "Autoritaire, impitoyable.",
    "rebelle": "Provocateur, libre.",
    "survivant": "Pragmatique, endurant.",
    "fanatique": "Obsédé par une cause.",
    "juge": "Rigide, impartial."
}

NATURE_MAPPING = {
    "A": ["architecte", "penseur", "visionnaire"],
    "B": ["bonvivant", "enfant"],
    "C": ["defenseur", "meneur", "bourreau"],
    "D": ["rebelle", "survivant", "fanatique"]
}

NATURE_QUESTIONS = [
    "1. Face à un problème…\nA) analyser\nB) ressentir\nC) convaincre\nD) agir",
    "2. Motivation…\nA) construire\nB) profiter\nC) protéger\nD) renverser",
    "3. Contradiction…\nA) argumenter\nB) désamorcer\nC) imposer\nD) ignorer",
    "4. Pouvoir…\nA) organiser\nB) ignorer\nC) dominer\nD) défier",
    "5. Défaut…\nA) obsession\nB) frivolité\nC) cruauté\nD) impulsivité",
    "6. Qualité…\nA) vision\nB) joie\nC) force\nD) liberté",
    "7. Dilemme…\nA) justice\nB) émotion\nC) protection\nD) intérêt",
    "8. Rapport aux autres…\nA) guider\nB) divertir\nC) rassurer\nD) surprendre",
    "9. Ennemi…\nA) désordre\nB) ennui\nC) faiblesse\nD) autorité",
    "10. Idéal…\nA) ordre\nB) joie\nC) force\nD) liberté",
    "11. Souffrance…\nA) résoudre\nB) consoler\nC) éliminer\nD) ignorer",
    "12. Relation à soi…\nA) analyser\nB) accepter\nC) endurcir\nD) changer",
    "13. Vous êtes…\nA) réflexion\nB) plaisir\nC) force\nD) rébellion"
]

# ------------------------------------------------------------
# QUIZ CLAN
# ------------------------------------------------------------

CLAN_SESSIONS = {}


class ClanButtons(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await record_clan_answer(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await record_clan_answer(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await record_clan_answer(interaction, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
    async def d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await record_clan_answer(interaction, "D")


@bot.tree.command(name="clanquiz", description="Quiz pour choisir un clan Dark Ages")
async def clanquiz(interaction: discord.Interaction):
    user_id = interaction.user.id
    CLAN_SESSIONS[user_id] = {
        "index": -1,
        "scores": {c: 0 for c in CLANS}
    }

    embed = discord.Embed(
        title="Quiz Clan — Dark Ages",
        description="Réponds aux questions A/B/C/D.",
        color=discord.Color.red()
    )

    await interaction.response.send_message(
        embed=embed,
        view=ClanButtons(user_id),
        ephemeral=True
    )


async def record_clan_answer(interaction: discord.Interaction, answer: str):
    user_id = interaction.user.id
    session = CLAN_SESSIONS[user_id]

    if session["index"] == -1:
        session["index"] = 0
        await send_clan_question(interaction)
        return

    for clan in MAPPING[answer]:
        session["scores"][clan] += 1

    session["index"] += 1

    if session["index"] >= len(QUESTIONS):
        await finalize_clan_quiz(interaction)
    else:
        await send_clan_question(interaction)


async def send_clan_question(interaction: discord.Interaction):
    user_id = interaction.user.id
    session = CLAN_SESSIONS[user_id]
    q = QUESTIONS[session["index"]]

    embed = discord.Embed(
        title=f"Question {session['index']+1}/{len(QUESTIONS)}",
        description=q,
        color=discord.Color.red()
    )

    await safe_edit(interaction, embed=embed, view=ClanButtons(user_id))


async def finalize_clan_quiz(interaction: discord.Interaction):
    user_id = interaction.user.id
    session = CLAN_SESSIONS[user_id]

    scores = session["scores"]
    best = max(scores.values())
    best_clans = [c for c, s in scores.items() if s == best]

    embed = discord.Embed(
        title="Résultat du Quiz Clan",
        color=discord.Color.dark_red()
    )

    for c in best_clans:
        embed.add_field(
            name=CLAN_DATA[c]["nom"],
            value=CLAN_DATA[c]["desc"],
            inline=False
        )

    await safe_edit(interaction, embed=embed, view=None)
    del CLAN_SESSIONS[user_id]


# ------------------------------------------------------------
# QUIZ NATURE / ATTITUDE
# ------------------------------------------------------------

NATURE_SESSIONS = {}


class NatureButtons(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await record_nature_answer(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await record_nature_answer(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await record_nature_answer(interaction, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
    async def d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await record_nature_answer(interaction, "D")


@bot.tree.command(name="naturequiz", description="Quiz pour déterminer Nature et Attitude")
async def naturequiz(interaction: discord.Interaction):
    user_id = interaction.user.id

    NATURE_SESSIONS[user_id] = {
        "index": -1,
        "scores": {k: 0 for k in NATURE_DATA.keys()}
    }

    embed = discord.Embed(
        title="Quiz Nature & Attitude",
        description="Réponds aux questions A/B/C/D.",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed,
        view=NatureButtons(user_id),
        ephemeral=True
    )


async def record_nature_answer(interaction: discord.Interaction, answer: str):
    user_id = interaction.user.id
    session = NATURE_SESSIONS[user_id]

    if session["index"] == -1:
        session["index"] = 0
        await send_nature_question(interaction)
        return

    for archetype in NATURE_MAPPING[answer]:
        session["scores"][archetype] += 1

    session["index"] += 1

    if session["index"] >= len(NATURE_QUESTIONS):
        await finalize_nature_quiz(interaction)
    else:
        await send_nature_question(interaction)


async def send_nature_question(interaction: discord.Interaction):
    user_id = interaction.user.id
    session = NATURE_SESSIONS[user_id]
    q = NATURE_QUESTIONS[session["index"]]

    embed = discord.Embed(
        title=f"Question {session['index']+1}/{len(NATURE_QUESTIONS)}",
        description=q,
        color=discord.Color.blue()
    )

    await safe_edit(interaction, embed=embed, view=NatureButtons(user_id))


async def finalize_nature_quiz(interaction: discord.Interaction):
    user_id = interaction.user.id
    session = NATURE_SESSIONS[user_id]

    scores = session["scores"]
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    nature = sorted_scores[0][0]
    attitude = sorted_scores[1][0]

    embed = discord.Embed(
        title="Résultat Nature & Attitude",
        color=discord.Color.dark_blue()
    )

    embed.add_field(
        name="Nature",
        value=f"**{nature.capitalize()}** — {NATURE_DATA[nature]}",
        inline=False
    )

    embed.add_field(
        name="Attitude",
        value=f"**{attitude.capitalize()}** — {NATURE_DATA[attitude]}",
        inline=False
    )

    await safe_edit(interaction, embed=embed, view=None)
    del NATURE_SESSIONS[user_id]


# ------------------------------------------------------------
# FUSION : /createcharacter
# ------------------------------------------------------------

CREATE = {}


@bot.tree.command(name="createcharacter", description="Crée un personnage complet (Clan + Nature + Attitude)")
async def createcharacter(interaction: discord.Interaction):
    user_id = interaction.user.id

    CREATE[user_id] = {
        "phase": "clan",
        "clan_index": -1,
        "nature_index": -1,
        "clan_scores": {c: 0 for c in CLANS},
        "nature_scores": {k: 0 for k in NATURE_DATA.keys()}
    }

    embed = discord.Embed(
        title="Création de personnage — Étape 1 : Clan",
        description="Réponds aux questions A/B/C/D.",
        color=discord.Color.red()
    )

    await interaction.response.send_message(
        embed=embed,
        view=CreateButtons(user_id),
        ephemeral=True
    )


class CreateButtons(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_create(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_create(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_create(interaction, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
    async def d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_create(interaction, "D")


async def handle_create(interaction: discord.Interaction, answer: str):
    user_id = interaction.user.id
    session = CREATE[user_id]

    # Phase 1 : Clan
    if session["phase"] == "clan":
        if session["clan_index"] == -1:
            session["clan_index"] = 0
            await send_create_clan(interaction)
            return

        for clan in MAPPING[answer]:
            session["clan_scores"][clan] += 1

        session["clan_index"] += 1

        if session["clan_index"] >= len(QUESTIONS):
            session["phase"] = "nature"
            await start_nature(interaction)
        else:
            await send_create_clan(interaction)
        return

    # Phase 2 : Nature
    if session["phase"] == "nature":
        if session["nature_index"] == -1:
            session["nature_index"] = 0
            await send_create_nature(interaction)
            return

        for archetype in NATURE_MAPPING[answer]:
            session["nature_scores"][archetype] += 1

        session["nature_index"] += 1

        if session["nature_index"] >= len(NATURE_QUESTIONS):
            await finalize_character(interaction)
        else:
            await send_create_nature(interaction)


async def send_create_clan(interaction: discord.Interaction):
    user_id = interaction.user.id
    session = CREATE[user_id]
    q = QUESTIONS[session["clan_index"]]

    embed = discord.Embed(
        title=f"Étape 1 — Clan ({session['clan_index']+1}/{len(QUESTIONS)})",
        description=q,
        color=discord.Color.red()
    )

    await safe_edit(interaction, embed=embed, view=CreateButtons(user_id))


async def start_nature(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Étape 2 — Nature & Attitude",
        description="Réponds aux questions A/B/C/D.",
        color=discord.Color.blue()
    )

    await safe_edit(interaction, embed=embed, view=CreateButtons(interaction.user.id))


async def send_create_nature(interaction: discord.Interaction):
    user_id = interaction.user.id
    session = CREATE[user_id]
    q = NATURE_QUESTIONS[session["nature_index"]]

    embed = discord.Embed(
        title=f"Étape 2 — Nature ({session['nature_index']+1}/{len(NATURE_QUESTIONS)})",
        description=q,
        color=discord.Color.blue()
    )

    await safe_edit(interaction, embed=embed, view=CreateButtons(user_id))


async def finalize_character(interaction: discord.Interaction):
    user_id = interaction.user.id
    session = CREATE[user_id]

    clan_scores = session["clan_scores"]
    best_clan = max(clan_scores, key=clan_scores.get)

    nature_scores = session["nature_scores"]
    sorted_natures = sorted(nature_scores.items(), key=lambda x: x[1], reverse=True)

    nature = sorted_natures[0][0]
    attitude = sorted_natures[1][0]

    embed = discord.Embed(
        title="🎭 Personnage Dark Ages généré",
        color=discord.Color.dark_purple()
    )

    embed.add_field(
        name="Clan",
        value=f"**{CLAN_DATA[best_clan]['nom']}**\n{CLAN_DATA[best_clan]['desc']}",
        inline=False
    )

    embed.add_field(
        name="Nature",
        value=f"**{nature.capitalize()}** — {NATURE_DATA[nature]}",
        inline=False
    )

    embed.add_field(
        name="Attitude",
        value=f"**{attitude.capitalize()}** — {NATURE_DATA[attitude]}",
        inline=False
    )

    embed.add_field(
        name="Résumé RP",
        value=(
            f"Tu es un **{CLAN_DATA[best_clan]['nom']}**, animé par une **Nature {nature.capitalize()}** "
            f"et une **Attitude {attitude.capitalize()}**.\n"
            f"Ton essence profonde ({nature}) guide tes choix, "
            f"tandis que ton masque social ({attitude}) façonne ton rapport au monde."
        ),
        inline=False
    )

    await safe_edit(interaction, embed=embed, view=None)
    del CREATE[user_id]


# ------------------------------------------------------------
# LANCEMENT DU BOT
# ------------------------------------------------------------

import os
bot.run(os.getenv("DISCORD_TOKEN"))
