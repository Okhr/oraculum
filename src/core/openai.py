import os
from dotenv import load_dotenv
import dotenv
from openai import OpenAI

if __name__ == '__main__':
    load_dotenv()

    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": """
            You will be given one or multiple chunks of text followed by a named entity belonging to one of the following classes : Location (LOC), Person (PER), Miscelaneous (MISC), Organization (ORG), None of the others (NONE)
            You will ouput one of {LOC, PER, MISC, ORG}, only one and nothing else
            
            # CHUNKS
            Elle ouvrit grands ses yeux bleu foncé, que les gouttes de pluie faisaient cligner sans cesse. Geralt se pencha et trancha le lien qui enserrait la main droite du prisonnier.\n\n— Regarde, Jaskier, dit-il en saisissant le captif par le poignet et en soulevant sa main libre. Tu vois cette cicatrice sur sa main ? C’est Ciri qui la lui a faite. Sur l’île de Thanedd, voici un mois. C’est un Nilfgaardien. Il était venu sur Thanedd dans l’intention de kidnapper Ciri. Elle lui a fait cette entaille alors qu’elle luttait pour ne pas se faire enlever.\n\n— Ça ne lui a pas servi à grand-chose, finalement, marmonna Milva. Quand même, m’est avis qu’il y a là quelque chose qui ne tient pas debout. Si celui-là a enlevé ta Ciri de l’île pour le compte de Nilfgaard, par quel miracle s’est-il retrouvé dans ce cercueil ? Et pourquoi le havekar voulait-il justement le livrer aux Nilfgaardiens ? Enlève-lui son bâillon, sorceleur.            

            # NAMED ENTITY
            Nilfgaardien
            """}
        ],
        n=1,
        temperature=1.0,
        top_p=1.0
    )
    print(response)
