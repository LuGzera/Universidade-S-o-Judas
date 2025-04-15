import math
import random
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "a3_criptografia"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'a3_criptografia'

mysql = MySQL(app)

def sort_prime(num):
    prime_num1 = []
    prime_num2 = [True] * (num + 1)
    for i in range(2, num + 1):
        if prime_num2[i]:
            prime_num1.append(i)
            for j in range(2, int(num / i) + 1):
                prime_num2[i * j] = False
    return prime_num1

def get_random_int(min, max):
    min = math.ceil(min)
    max = math.floor(max)
    return math.floor(random.random() * (max - min + 1)) + min

def mdc(x, y):
    while y:
        t = y
        y = x % y
        x = t
    return x

def modInverse(a, m):
    for x in range(1, m):
        if (a % m) * (x % m) % m == 1:
            return x

primos = sort_prime(300)
p = primos[get_random_int(len(primos)-60, len(primos))]
q = primos[get_random_int(len(primos)-60, len(primos))]

n = p * q
m = (p - 1) * (q - 1)

tempE = 0
temp = get_random_int(1, m)
e = 0
while e == 0:
    tempE = mdc(temp, m)
    if tempE == 1:
        e = temp
    else:
        temp = get_random_int(1, m)

d = modInverse(e, m)

def encrypt_message(message):
    msgCifrada = []
    msgCifradaTemp = []

    strBytes = bytes(message, 'utf-8')
    for byte in strBytes:
        msgCifradaTemp.append(byte)

    for index in range(len(msgCifradaTemp)):
        temp = pow(msgCifradaTemp[index], e)
        temp2 = temp % n
        msgCifrada.append(temp2)

    return msgCifrada

def decrypt_message(encrypted_message):
    decrypted_message = []
    for num in encrypted_message:
        decrypted_message.append(chr(pow(num, d) % n))
    return ''.join(decrypted_message)


@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/voteslist')
def VotesList():
    show_decrypted = request.args.get('decrypted', 'false') == 'true'
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM votes")
    votes = cursor.fetchall()
    cursor.close()

    if show_decrypted:
        votes = [(row[0], decrypt_message(eval(row[1])), row[2], row[3]) for row in votes]

    return render_template('votes.html', votes=votes, show_decrypted=show_decrypted)

@app.route('/insert', methods=['POST'])
def Insert():
    if request.method == 'POST':
        flash("Voto registrado com sucesso!")

        candidato = request.form['candidato']
        username = request.form['username']

        cripto_voto = encrypt_message(candidato)

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO votes (cripto_vote, username) VALUES (%s, %s)", (str(cripto_voto), username))
        mysql.connection.commit()
        return redirect(url_for('Index'))

if __name__ == "__main__":
    app.run(debug=True)
