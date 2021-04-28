import random
import string

names = ["Joette", "Anabelle", "Fred", "Woodrow", "Neoma", "Dorian", "Treasure", "Tami", "Berdie", "Jordi", "Frances",
         "Gerhardt", "Kristina", "Carmelita", "Sim", "Hideo", "Arland", "Wirt", "Robt", "Narcissus", "Steve", "Monique",
         "Kellen", "Jessenia", "Nathalia", "Lissie", "Loriann", "Theresa", "Pranav", "Eppie", "Angelic", "Louvenia",
         "Mathews", "Natalie", "Susan", "Cyril", "Vester", "Rakeem", "Duff", "Garret", "Agnes", "Carol", "Pairlee",
         "Viridiana", "Keith", "Elinore", "Rico", "Demonte", "Imelda", "Jackeline", "Kenneth", "Adalynn", "Blair",
         "Stetson", "Adamaris", "Zaniyah", "Heyward", "Austin", "Elden", "Gregory", "Lemuel", "Aaliyah", "Abby",
         "Hassie", "Sanjuanita", "Takisha", "Orlo", "Geary", "Bettye", "Luciano", "Gretchen", "Chimere", "Melanie",
         "Angele", "Michial", "Emmons", "Edmund", "Renae", "Letha", "Curtiss", "Boris", "Winter", "Nealy", "Renard",
         "Taliyah", "Jaren", "Nilda", "Tiny", "Manila", "Mariann", "Dennis", "Autumn", "Aron", "Drew", "Shea", "Britt",
         "Luvenia", "Doloris", "Bret", "Sammy", "Elmer", "Florencio", "Selah", "Simona", "Tatyana", "Beau", "Alvin",
         "Leslie", "Kimberely", "Sydni", "Mitchel", "Belle", "Brain", "Marlin", "Vallie", "Colon", "Hoyt", "Destinee",
         "Shamar", "Ezzard", "Sheilah", "Leisa", "Tennille", "Brandyn", "Yasmin", "Malaya", "Larry", "Mina", "Myrle",
         "Blaine", "Gusta", "Beryl", "Abdul", "Cleda", "Lailah", "Alexandrea", "Unknown", "Gertrude", "Davon", "Minda",
         "Gabe", "Myles", "Vonda", "Zandra", "Salome", "Minnie", "Merl", "Biddie", "Catina", "Cassidy", "Norman",
         "Emilia", "Fanny", "Nancie", "Domingo", "Christa", "Severt", "Danita", "Jennie", "Anaya", "Michelle",
         "Brittnie", "Althea", "Kimberlee", "Ursula", "Ballard", "Silvester", "Ilda", "Rock", "Tyler", "Hildegarde",
         "Aurelio", "Lovell", "Neha", "Jeramiah", "Kristin", "Kelis", "Adolf", "Elwood", "Almus", "Geo", "Machelle",
         "Arnulfo", "Love", "Lollie", "Bobbye", "Columbus", "Susie", "Reta", "Krysten", "Sunny", "Alzina", "Carolyne",
         "Laurine", "Jayla", "Halbert", "Grayce", "Alvie", "Haylee", "Hosea", "Alvira", "Pallie", "Marylin", "Elise",
         "Lidie", "Vita", "Jakob", "Elmira", "Oliver", "Arra", "Debbra", "Migdalia", "Lucas", "Verle", "Dellar",
         "Madaline", "Iverson", "Lorin", "Easter", "Britta", "Kody", "Colie", "Chaz", "Glover", "Nickolas", "Francisca",
         "Donavan", "Merlene", "Belia", "Laila", "Nikhil", "Burdette", "Mildred", "Malissa", "Del", "Reagan", "Loney",
         "Lambert", "Ellen", "Sydell", "Juanita", "Alphonsus", "Gianna", "William", "Oneal", "Anya", "Luis", "Shad",
         "Armin", "Marvin"]


def create_name() -> str:
    return f"{random.choice(names)} {random.choice(names)}"


def create_netid(name: str) -> str:
    initials = "".join(word[0].lower() for word in name.split())
    numbers = "".join(random.choice(string.digits) for _ in range(3))

    return f"{initials}{numbers}"


def rand_commit(n=10):
    from anubis.utils.data import rand
    return rand(n)
