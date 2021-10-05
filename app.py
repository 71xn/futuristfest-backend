import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Database stuff
try:
    conn = psycopg2.connect(
        host="ec2-54-170-163-224.eu-west-1.compute.amazonaws.com",
        database="de4fdaf8osb01c",
        user="epsxuyzwewbnlj",
        password="bfd54096dbb405f667865b7c0cc632161c41e4b1773cbd656057dcc537f7788f")
except (Exception, psycopg2.DatabaseError) as error:
    print(error)


def sqltest():
    cur = conn.cursor()

    # execute a statement
    print('PostgreSQL database version:')
    cur.execute('SELECT version()')

    # display the PostgreSQL database server version
    db_version = cur.fetchone()
    print(db_version)

    # close the communication with the PostgreSQL
    cur.close()
    return "Database status: UP, Database Version: " + str(db_version)


@app.route("/")
@cross_origin()
def helloWorld():
    sqltest()
    return "Hello, cross-origin-world!"


@app.route('/getmsg/', methods=['GET'])
@cross_origin()
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)

    # For debugging
    print(f"got name {name}")

    response = {"message": f"Hello {name}"}

    # Return the response in json format
    return jsonify(response)


@app.route('/healthcheck/', methods=['GET'])
@cross_origin()
def health():
    dbhealth = sqltest();
    response = {"health-status": f"{dbhealth}"}
    return jsonify(response)
