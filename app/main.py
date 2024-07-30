import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from .database import get_db_connection, init_db
import asyncio

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Le User va te donner un theme et tu va devoir le deconstruire en minimum une dizaine de chapitres a aborder pour enseigner le theme. Ne donne que le sommaire et il doit etre grand et complet. le sommaire est une liste de chapitre numéroté avec un descriptif de ce qu'il contient (exemple : 1. NOM_DU_CHAPITRE_1, etc ..).le sommaire est en Markdown"},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def generate_chapter(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "L'utilisateur te fournira le titre d'un chapitre et quelques points clés sous forme de puces. Ta mission est de développer un contenu complet en Markdown basé sur ces éléments. Concentre-toi sur la fourniture d'explications claires, d'exemples pertinents et de conseils pratiques. Assure-toi que le contenu est accessible pour un public pro mais également enrichissant pour les niveaux intermédiaires. Ton écriture doit être professionnelle, captivante, et rigoureusement informative. N'oublie pas d'inclure une légère introduction et une légère conclusion pour chaque chapitre, ainsi que des sous-titres pour chaque point clé. Le but est de lister et d'explorer les fonctionnalités et de fournir une compréhension solide du sujet, en évitant toute complexité inutile ou jargon excessif. Pense à ajouter de courte explication vulgariser pour résumer chaques chapitres pour renforcer la compréhension."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

async def generate_async(prompt):
    loop = asyncio.get_event_loop()
    completion = await loop.run_in_executor(None, lambda: client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Le User va te donner un theme et tu va devoir le deconstruire en minimum une dizaine de chapitres a aborder pour enseigner le theme. Ne donne que le sommaire et il doit etre grand et complet. le sommaire est une liste de chapitre numéroté avec un descriptif de ce qu'il contient (exemple : 1. NOM_DU_CHAPITRE_1, etc ..).le sommaire est en Markdown"},
            {"role": "user", "content": prompt}
        ]
    ))
    return completion.choices[0].message.content

async def generate_chapter_async(prompt):
    loop = asyncio.get_event_loop()
    completion = await loop.run_in_executor(None, lambda: client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "L'utilisateur te fournira le titre d'un chapitre et quelques points clés sous forme de puces. Ta mission est de développer un contenu complet en Markdown basé sur ces éléments. Concentre-toi sur la fourniture d'explications claires, d'exemples pertinents et de conseils pratiques. Assure-toi que le contenu est accessible pour un public pro mais également enrichissant pour les niveaux intermédiaires. Ton écriture doit être professionnelle, captivante, et rigoureusement informative. N'oublie pas d'inclure une légère introduction et une légère conclusion pour chaque chapitre, ainsi que des sous-titres pour chaque point clé. Le but est de lister et d'explorer les fonctionnalités et de fournir une compréhension solide du sujet, en évitant toute complexité inutile ou jargon excessif. Pense à ajouter de courte explication vulgariser pour résumer chaques chapitres pour renforcer la compréhension."},
            {"role": "user", "content": prompt}
        ]
    ))
    return completion.choices[0].message.content

def main(theme):
    init_db()
    
    # Générer le sommaire
    print("Génération du sommaire...")
    sommaire = generate(theme)
    print("Sommaire généré.")
    
    # Diviser le sommaire en chapitres
    chapitres = re.split(r'\n(\d+\. [^\n]+)', sommaire)[1:]
    chapitres_et_descriptions = [f"{chapitres[i]}{chapitres[i+1]}" for i in range(0, len(chapitres), 2)]
    
    cours_complet = ""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Générer le contenu pour chaque chapitre
    total_chapitres = len(chapitres_et_descriptions)
    for i, chapitre in enumerate(chapitres_et_descriptions, 1):
        #print(f"Génération du chapitre {i}/{len(chapitres_et_descriptions)} : {chapitre.split('.')[0]}")
        print(f"Génération du chapitre {i}/{total_chapitres} : {chapitre.split('.')[1].strip()}")
        contenu_chapitre = generate_chapter(chapitre)
        cours_complet += contenu_chapitre + "\n\n"
        print(f"Progression : {i}/{total_chapitres} chapitres générés ({i/total_chapitres*100:.2f}%)")
    
    # Créer un nom de fichier unique basé sur le thème et la date
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{theme.replace(' ', '_')}_{timestamp}.md"
    filepath = os.path.join("cours_files", filename)
    
    # Assurer que le dossier existe
    os.makedirs("cours_files", exist_ok=True)
    
    # Sauvegarder le cours complet dans un fichier Markdown
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(cours_complet)
    
    # Sauvegarder la référence dans la base de données
    cur.execute("INSERT INTO cours (theme, sommaire, fichier_path) VALUES (?, ?, ?)",
                (theme, sommaire, filepath))
    conn.commit()
    
    conn.close()
    
    print(f"Cours complet généré et sauvegardé dans le fichier : {filepath}")
    print("Référence sauvegardée dans la base de données.")
    return filepath

async def main_async(theme):
    init_db()
    
    # Générer le sommaire
    print("Génération du sommaire...")
    sommaire = await generate_async(theme)
    print("Sommaire généré.")
    
    # Diviser le sommaire en chapitres
    chapitres = re.split(r'\n(\d+\. [^\n]+)', sommaire)[1:]
    chapitres_et_descriptions = [f"{chapitres[i]}{chapitres[i+1]}" for i in range(0, len(chapitres), 2)]
    
    cours_complet = ""
    
    # Générer le contenu pour chaque chapitre
    total_chapitres = len(chapitres_et_descriptions)
    for i, chapitre in enumerate(chapitres_et_descriptions, 1):
        print(f"Génération du chapitre {i}/{total_chapitres} : {chapitre.split('.')[1].strip()}")
        contenu_chapitre = await generate_chapter_async(chapitre)
        cours_complet += contenu_chapitre + "\n\n"
        print(f"Progression : {i}/{total_chapitres} chapitres générés ({i/total_chapitres*100:.2f}%)")
    
    # Créer un nom de fichier unique basé sur le thème et la date
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{theme.replace(' ', '_')}_{timestamp}.md"
    filepath = os.path.join("cours_files", filename)
    
    # Assurer que le dossier existe
    os.makedirs("cours_files", exist_ok=True)
    
    # Sauvegarder le cours complet dans un fichier Markdown
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(cours_complet)
    
    # Sauvegarder la référence dans la base de données
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE cours SET sommaire = ?, fichier_path = ? WHERE theme = ?",
                (sommaire, filepath, theme))
    conn.commit()
    conn.close()
    
    print(f"Cours complet généré et sauvegardé dans le fichier : {filepath}")
    print("Référence sauvegardée dans la base de données.")
    return filepath

if __name__ == "__main__":
    theme = input("Thème du cours : ")
    fichier_cours = asyncio.run(main_async(theme))
    print(f"Le cours a été sauvegardé dans : {fichier_cours}")